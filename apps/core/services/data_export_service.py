"""Data export service for GDPR Article 15 compliance.

This module implements the Right of Access (Article 15) by providing
functionality to export all user personal data in machine-readable
formats (JSON or CSV).

GDPR Requirements:
- Users can request a copy of all their personal data
- Data must be provided in a commonly used, machine-readable format
- Export must be available within 30 days (we aim for <24 hours)
- Download link expires after 24 hours for security

Example:
    >>> request = DataExportService.request_export(user, format="json")
    >>> # Async task processes the export
    >>> status = DataExportService.get_export_status(request.id)
    >>> url = DataExportService.get_download_url(request.id)
"""

import csv
import json
import os
import uuid
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.utils import timezone

from apps.core.models import (
    AccountDeletionRequest,
    AuditLog,
    BackupCode,
    ConsentRecord,
    DataExportRequest,
    PasswordHistory,
    SessionToken,
    TOTPDevice,
    User,
    UserProfile,
)
from apps.core.services.audit_service import AuditService
from apps.core.utils.encryption import IPEncryption


class DataExportService:
    """Service for exporting user personal data (GDPR Article 15).

    Handles creation, processing, and delivery of user data exports.
    Exports include all personal data within the US-001 scope:
    - User profile information
    - Organisation membership
    - Authentication history (audit logs)
    - Active sessions
    - 2FA device information (not secrets)
    - Password change history (timestamps only)
    - Consent records

    Security Features:
    - Exports stored in secure location with UUID filenames
    - Download URLs expire after 24 hours
    - All export requests are audit logged
    - Rate limiting prevents abuse (max 1 export per 24 hours)

    Attributes:
        EXPORT_DIR: Directory for storing export files
        DOWNLOAD_EXPIRY_HOURS: Hours until download URL expires
    """

    EXPORT_DIR = getattr(settings, "GDPR_EXPORT_DIR", "/tmp/gdpr_exports")
    DOWNLOAD_EXPIRY_HOURS = 24
    RATE_LIMIT_HOURS = 24  # One export per 24 hours

    @staticmethod
    def request_export(
        user: User,
        export_format: str = "json",
        ip_address: str = "",
        user_agent: str = "",
    ) -> DataExportRequest:
        """Create a new data export request.

        Creates a pending export request that will be processed asynchronously.
        Rate limited to one export per 24 hours per user.

        Args:
            user: User requesting the export.
            export_format: Export format ("json" or "csv").
            ip_address: IP address of the request (for audit logging).
            user_agent: User agent string (for audit logging).

        Returns:
            DataExportRequest instance.

        Raises:
            ValueError: If format is invalid or rate limit exceeded.
        """
        # Validate format
        if export_format not in ["json", "csv"]:
            raise ValueError("Export format must be 'json' or 'csv'")

        # Check rate limit
        recent_export = DataExportRequest.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(hours=DataExportService.RATE_LIMIT_HOURS),
        ).first()

        if recent_export:
            raise ValueError(
                f"Export rate limit exceeded. Please wait {DataExportService.RATE_LIMIT_HOURS} "
                "hours between export requests."
            )

        # Create export request
        export_request = DataExportRequest.objects.create(
            user=user,
            format=export_format,
            status=DataExportRequest.StatusChoices.PENDING,
        )

        # Audit log the request
        AuditService.log_event(
            action="data_export_requested",
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={
                "export_id": str(export_request.id),
                "format": export_format,
            },
        )

        return export_request

    @staticmethod
    def process_export(request_id: uuid.UUID) -> DataExportRequest:
        """Process a data export request.

        Generates the export file containing all user personal data.
        This method should be called from a Celery task.

        Args:
            request_id: UUID of the DataExportRequest.

        Returns:
            Updated DataExportRequest instance.

        Raises:
            DataExportRequest.DoesNotExist: If request not found.
            ValueError: If request is not in pending status.
        """
        export_request = DataExportRequest.objects.select_related("user").get(id=request_id)

        if export_request.status != DataExportRequest.StatusChoices.PENDING:
            raise ValueError(f"Export request is not pending (status: {export_request.status})")

        # Update status to processing
        export_request.status = DataExportRequest.StatusChoices.PROCESSING
        export_request.save(update_fields=["status"])

        try:
            # Collect all user data
            user_data = DataExportService._collect_user_data(export_request.user)

            # Generate export file
            if export_request.format == "json":
                file_path, file_size = DataExportService._generate_json_export(
                    user_data, export_request.id
                )
            else:
                file_path, file_size = DataExportService._generate_csv_export(
                    user_data, export_request.id
                )

            # Update request with file info
            export_request.file_path = file_path
            export_request.download_url = DataExportService._generate_download_url(
                export_request.id
            )
            export_request.expires_at = timezone.now() + timedelta(
                hours=DataExportService.DOWNLOAD_EXPIRY_HOURS
            )
            export_request.completed_at = timezone.now()
            export_request.status = DataExportRequest.StatusChoices.COMPLETED
            export_request.metadata = {
                "file_size": file_size,
                "record_counts": DataExportService._get_record_counts(user_data),
            }
            export_request.save()

            # Audit log completion
            AuditService.log_event(
                action="data_export_completed",
                user=export_request.user,
                metadata={
                    "export_id": str(export_request.id),
                    "format": export_request.format,
                    "file_size": file_size,
                },
            )

        except Exception as e:
            # Mark as failed
            export_request.status = DataExportRequest.StatusChoices.FAILED
            export_request.metadata = {"error": str(e)}
            export_request.save(update_fields=["status", "metadata"])

            # Audit log failure
            AuditService.log_event(
                action="data_export_failed",
                user=export_request.user,
                metadata={
                    "export_id": str(export_request.id),
                    "error": str(e),
                },
            )
            raise

        return export_request

    @staticmethod
    def get_export_status(request_id: uuid.UUID, user: User) -> DataExportRequest | None:
        """Get the status of a data export request.

        Args:
            request_id: UUID of the DataExportRequest.
            user: User requesting the status (for authorisation).

        Returns:
            DataExportRequest if found and belongs to user, None otherwise.
        """
        try:
            return DataExportRequest.objects.get(id=request_id, user=user)
        except DataExportRequest.DoesNotExist:
            return None

    @staticmethod
    def get_user_exports(user: User, limit: int = 10) -> list[DataExportRequest]:
        """Get recent export requests for a user.

        Args:
            user: User to get exports for.
            limit: Maximum number of exports to return.

        Returns:
            List of DataExportRequest instances.
        """
        return list(DataExportRequest.objects.filter(user=user).order_by("-created_at")[:limit])

    @staticmethod
    def get_download_url(request_id: uuid.UUID, user: User) -> str | None:
        """Get the download URL for a completed export.

        Args:
            request_id: UUID of the DataExportRequest.
            user: User requesting the URL (for authorisation).

        Returns:
            Download URL if export is completed and not expired, None otherwise.
        """
        try:
            export_request = DataExportRequest.objects.get(
                id=request_id,
                user=user,
                status=DataExportRequest.StatusChoices.COMPLETED,
            )

            if export_request.is_expired():
                export_request.mark_as_expired()
                return None

            return export_request.download_url

        except DataExportRequest.DoesNotExist:
            return None

    @staticmethod
    def cleanup_expired_exports() -> int:
        """Remove expired export files and update statuses.

        Should be called by a scheduled Celery task daily.

        Returns:
            Number of exports cleaned up.
        """
        now = timezone.now()
        expired_exports = DataExportRequest.objects.filter(
            status=DataExportRequest.StatusChoices.COMPLETED,
            expires_at__lt=now,
        )

        count = 0
        for export in expired_exports:
            # Delete file if exists
            if export.file_path and os.path.exists(export.file_path):
                try:
                    os.remove(export.file_path)
                except OSError:
                    pass  # File may already be deleted

            export.mark_as_expired()
            count += 1

        return count

    @staticmethod
    def _collect_user_data(user: User) -> dict[str, Any]:
        """Collect all personal data for a user.

        Gathers data from all models containing user personal information
        within the US-001 (User Authentication) scope.

        Args:
            user: User to collect data for.

        Returns:
            Dictionary containing all user personal data.
        """
        data = {
            "export_metadata": {
                "export_date": timezone.now().isoformat(),
                "gdpr_article": "Article 15 (Right of Access) & Article 20 (Data Portability)",
                "data_controller": getattr(settings, "DATA_CONTROLLER_NAME", "Syntek CMS Platform"),
                "format_version": "1.0.0",
            },
            "user_profile": DataExportService._get_user_profile_data(user),
            "organisation": DataExportService._get_organisation_data(user),
            "email_verification": DataExportService._get_email_verification_data(user),
            "two_factor_authentication": DataExportService._get_2fa_data(user),
            "active_sessions": DataExportService._get_session_data(user),
            "authentication_history": DataExportService._get_audit_log_data(user),
            "password_history": DataExportService._get_password_history_data(user),
            "consent_records": DataExportService._get_consent_data(user),
            "deletion_requests": DataExportService._get_deletion_request_data(user),
            "processing_restriction": DataExportService._get_processing_restriction_data(user),
        }

        return data

    @staticmethod
    def _get_user_profile_data(user: User) -> dict[str, Any]:
        """Get user profile data."""
        profile_data = {
            "id": str(user.id),
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }

        # Include extended profile if exists
        try:
            profile = UserProfile.objects.get(user=user)
            profile_data["extended_profile"] = {
                "phone": profile.phone,
                "timezone": profile.timezone,
                "language": profile.language,
                "bio": profile.bio,
            }
        except UserProfile.DoesNotExist:
            profile_data["extended_profile"] = None

        return profile_data

    @staticmethod
    def _get_organisation_data(user: User) -> dict[str, Any] | None:
        """Get organisation membership data."""
        if not user.organisation:
            return None

        return {
            "id": str(user.organisation.id),
            "name": user.organisation.name,
            "slug": user.organisation.slug,
            "role": "Member",  # TODO: Get actual role when RBAC is implemented
            "joined_at": user.created_at.isoformat() if user.created_at else None,
        }

    @staticmethod
    def _get_email_verification_data(user: User) -> dict[str, Any]:
        """Get email verification status data."""
        return {
            "email_verified": user.email_verified,
            "email_verified_at": (
                user.email_verified_at.isoformat() if user.email_verified_at else None
            ),
        }

    @staticmethod
    def _get_2fa_data(user: User) -> dict[str, Any]:
        """Get 2FA status data (excluding secrets)."""
        devices = TOTPDevice.objects.filter(user=user, is_confirmed=True)

        return {
            "two_factor_enabled": user.two_factor_enabled,
            "device_count": devices.count(),
            "devices": [
                {
                    "name": device.device_name,
                    "created_at": device.created_at.isoformat(),
                    "last_used_at": device.last_used_at.isoformat()
                    if device.last_used_at
                    else None,
                }
                for device in devices
            ],
            "backup_codes_remaining": BackupCode.objects.filter(user=user, is_used=False).count(),
        }

    @staticmethod
    def _get_session_data(user: User) -> list[dict[str, Any]]:
        """Get active session data."""
        sessions = SessionToken.objects.filter(user=user, is_revoked=False)

        return [
            {
                "device_fingerprint": session.device_fingerprint,
                "user_agent": session.user_agent,
                "created_at": session.created_at.isoformat(),
                "last_activity_at": session.last_activity_at.isoformat(),
                "expires_at": session.expires_at.isoformat(),
            }
            for session in sessions
        ]

    @staticmethod
    def _get_audit_log_data(user: User, limit: int = 1000) -> list[dict[str, Any]]:
        """Get authentication history from audit logs."""
        logs = AuditLog.objects.filter(user=user).order_by("-created_at")[:limit]

        return [
            {
                "action": log.action,
                "timestamp": log.created_at.isoformat(),
                "ip_address": (IPEncryption.decrypt_ip(log.ip_address) if log.ip_address else None),
                "user_agent": log.user_agent,
                "device_fingerprint": log.device_fingerprint,
            }
            for log in logs
        ]

    @staticmethod
    def _get_password_history_data(user: User) -> list[dict[str, Any]]:
        """Get password change history (timestamps only, not hashes)."""
        history = PasswordHistory.objects.filter(user=user).order_by("-created_at")

        return [
            {
                "changed_at": record.created_at.isoformat(),
            }
            for record in history
        ]

    @staticmethod
    def _get_consent_data(user: User) -> list[dict[str, Any]]:
        """Get consent records."""
        consents = ConsentRecord.objects.filter(user=user).order_by("-granted_at")

        return [
            {
                "consent_type": consent.consent_type,
                "granted": consent.granted,
                "version": consent.version,
                "granted_at": consent.granted_at.isoformat(),
                "withdrawn_at": (
                    consent.withdrawn_at.isoformat() if consent.withdrawn_at else None
                ),
            }
            for consent in consents
        ]

    @staticmethod
    def _get_deletion_request_data(user: User) -> list[dict[str, Any]]:
        """Get account deletion request history."""
        requests = AccountDeletionRequest.objects.filter(user=user).order_by("-created_at")

        return [
            {
                "status": request.status,
                "reason": request.reason,
                "created_at": request.created_at.isoformat(),
                "confirmed_at": (
                    request.confirmed_at.isoformat() if request.confirmed_at else None
                ),
                "completed_at": (
                    request.completed_at.isoformat() if request.completed_at else None
                ),
            }
            for request in requests
        ]

    @staticmethod
    def _get_processing_restriction_data(user: User) -> dict[str, Any]:
        """Get processing restriction status."""
        return {
            "processing_restricted": user.processing_restricted,
            "restriction_reason": user.restriction_reason,
            "restricted_at": (user.restricted_at.isoformat() if user.restricted_at else None),
        }

    @staticmethod
    def _generate_json_export(data: dict[str, Any], request_id: uuid.UUID) -> tuple[str, int]:
        """Generate JSON export file.

        Args:
            data: User data dictionary.
            request_id: Export request ID for filename.

        Returns:
            Tuple of (file_path, file_size).
        """
        # Ensure export directory exists
        os.makedirs(DataExportService.EXPORT_DIR, exist_ok=True)

        file_path = os.path.join(DataExportService.EXPORT_DIR, f"{request_id}.json")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        file_size = os.path.getsize(file_path)
        return file_path, file_size

    @staticmethod
    def _generate_csv_export(data: dict[str, Any], request_id: uuid.UUID) -> tuple[str, int]:
        """Generate CSV export file.

        Flattens the data structure into CSV format with multiple sections.

        Args:
            data: User data dictionary.
            request_id: Export request ID for filename.

        Returns:
            Tuple of (file_path, file_size).
        """
        # Ensure export directory exists
        os.makedirs(DataExportService.EXPORT_DIR, exist_ok=True)

        file_path = os.path.join(DataExportService.EXPORT_DIR, f"{request_id}.csv")

        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)

            # Write each section
            for section_name, section_data in data.items():
                writer.writerow([f"=== {section_name.upper()} ==="])

                if isinstance(section_data, dict):
                    for key, value in section_data.items():
                        if isinstance(value, (dict, list)):
                            writer.writerow([key, json.dumps(value)])
                        else:
                            writer.writerow([key, value])

                elif isinstance(section_data, list):
                    if section_data and isinstance(section_data[0], dict):
                        # Write headers
                        headers = list(section_data[0].keys())
                        writer.writerow(headers)
                        # Write rows
                        for item in section_data:
                            writer.writerow([item.get(h, "") for h in headers])
                    else:
                        for item in section_data:
                            writer.writerow([item])

                writer.writerow([])  # Empty row between sections

        file_size = os.path.getsize(file_path)
        return file_path, file_size

    @staticmethod
    def _generate_download_url(request_id: uuid.UUID) -> str:
        """Generate a secure download URL for the export.

        In production, this would generate a signed URL.
        For now, returns a simple URL pattern.

        Args:
            request_id: Export request ID.

        Returns:
            Download URL string.
        """
        base_url = getattr(settings, "SITE_URL", "http://localhost:8000")
        return f"{base_url}/api/gdpr/exports/{request_id}/download/"

    @staticmethod
    def _get_record_counts(data: dict[str, Any]) -> dict[str, int]:
        """Get record counts for each data section.

        Args:
            data: User data dictionary.

        Returns:
            Dictionary of section names to record counts.
        """
        counts = {}
        for section_name, section_data in data.items():
            if isinstance(section_data, list):
                counts[section_name] = len(section_data)
            elif isinstance(section_data, dict):
                counts[section_name] = 1
            else:
                counts[section_name] = 0
        return counts
