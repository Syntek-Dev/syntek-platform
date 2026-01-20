"""Account deletion service for GDPR Article 17 compliance.

This module implements the Right to Erasure (Article 17) by providing
functionality for users to request and confirm permanent deletion of
their accounts.

GDPR Requirements:
- Users can request deletion of their personal data
- Confirmation workflow prevents accidental deletions
- Some data may be retained for legal compliance (anonymised)
- Audit logs are anonymised, not deleted (7 year retention)

Deletion Workflow:
1. User requests deletion -> Confirmation email sent
2. User clicks confirmation link with token
3. User enters password to confirm
4. Account and related data deleted/anonymised
5. Confirmation email sent

Example:
    >>> request = AccountDeletionService.request_deletion(user, "No longer needed")
    >>> # User receives email with confirmation token
    >>> AccountDeletionService.confirm_deletion(token, password)
"""

import hashlib
import os

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.core.models import (
    AccountDeletionRequest,
    AuditLog,
    BackupCode,
    ConsentRecord,
    DataExportRequest,
    EmailVerificationToken,
    PasswordHistory,
    PasswordResetToken,
    SessionToken,
    TOTPDevice,
    User,
    UserProfile,
)
from apps.core.services.audit_service import AuditService
from apps.core.services.email_service import EmailService


class AccountDeletionService:
    """Service for account deletion (GDPR Article 17).

    Handles the complete account deletion workflow including request
    creation, confirmation, and execution. Implements proper data
    retention for legal compliance.

    Deletion Strategy:
    - Immediate deletion: User profile, sessions, tokens, 2FA devices
    - Anonymisation: Audit logs (user reference removed, structure preserved)
    - Retention: Anonymised audit logs for 7 years (legal compliance)

    Security Features:
    - Confirmation token with 24-hour expiry
    - Password verification required for confirmation
    - All deletion events are audit logged
    - Email notifications at each step

    Attributes:
        CONFIRMATION_EXPIRY_HOURS: Hours until confirmation token expires
    """

    CONFIRMATION_EXPIRY_HOURS = 24

    @staticmethod
    def request_deletion(
        user: User,
        reason: str = "",
        ip_address: str = "",
        user_agent: str = "",
    ) -> AccountDeletionRequest:
        """Request account deletion.

        Creates a pending deletion request and sends a confirmation email.
        The user must confirm within 24 hours.

        Args:
            user: User requesting deletion.
            reason: Optional reason for deletion.
            ip_address: IP address of the request (for audit logging).
            user_agent: User agent string (for audit logging).

        Returns:
            AccountDeletionRequest instance.

        Raises:
            ValueError: If user already has a pending deletion request.
        """
        # Check for existing pending request
        existing_request = AccountDeletionRequest.objects.filter(
            user=user,
            status=AccountDeletionRequest.StatusChoices.PENDING,
        ).first()

        if existing_request and not existing_request.is_expired():
            raise ValueError(
                "You already have a pending deletion request. "
                "Please check your email or wait for it to expire."
            )

        # Cancel any expired pending requests
        AccountDeletionRequest.objects.filter(
            user=user,
            status=AccountDeletionRequest.StatusChoices.PENDING,
        ).update(status=AccountDeletionRequest.StatusChoices.CANCELLED)

        # Generate confirmation token
        plain_token, hashed_token = AccountDeletionRequest.generate_confirmation_token()

        # Create deletion request
        deletion_request = AccountDeletionRequest.objects.create(
            user=user,
            reason=reason,
            confirmation_token=hashed_token,
            status=AccountDeletionRequest.StatusChoices.PENDING,
        )

        # Update user's deletion_requested_at
        user.deletion_requested_at = timezone.now()
        user.save(update_fields=["deletion_requested_at"])

        # Send confirmation email
        AccountDeletionService._send_confirmation_email(user, plain_token)

        # Audit log the request
        AuditService.log_event(
            action="account_deletion_requested",
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={
                "request_id": str(deletion_request.id),
                "reason_provided": bool(reason),
            },
        )

        return deletion_request

    @staticmethod
    def confirm_deletion(
        token: str,
        password: str,
        ip_address: str = "",
        user_agent: str = "",
    ) -> AccountDeletionRequest:
        """Confirm and execute account deletion.

        Verifies the confirmation token and password, then processes
        the deletion. This operation is irreversible.

        Args:
            token: Plain text confirmation token from email.
            password: User's current password for verification.
            ip_address: IP address of the request (for audit logging).
            user_agent: User agent string (for audit logging).

        Returns:
            Updated AccountDeletionRequest instance.

        Raises:
            ValueError: If token is invalid, expired, or password is wrong.
        """
        # Find the deletion request by token hash
        token_hash = AccountDeletionRequest.hash_token(token)

        try:
            deletion_request = AccountDeletionRequest.objects.select_related("user").get(
                confirmation_token=token_hash,
                status=AccountDeletionRequest.StatusChoices.PENDING,
            )
        except AccountDeletionRequest.DoesNotExist:
            raise ValueError("Invalid or expired confirmation token.")

        # Check if expired
        if deletion_request.is_expired(AccountDeletionService.CONFIRMATION_EXPIRY_HOURS):
            deletion_request.status = AccountDeletionRequest.StatusChoices.CANCELLED
            deletion_request.save(update_fields=["status"])
            raise ValueError("Confirmation token has expired. Please request deletion again.")

        user = deletion_request.user

        # Verify password
        if not user.check_password(password):
            # Audit log failed attempt
            AuditService.log_event(
                action="account_deletion_failed",
                user=user,
                ip_address=ip_address,
                user_agent=user_agent,
                metadata={
                    "request_id": str(deletion_request.id),
                    "reason": "invalid_password",
                },
            )
            raise ValueError("Invalid password.")

        # Update request status to confirmed
        deletion_request.confirmed_at = timezone.now()
        deletion_request.status = AccountDeletionRequest.StatusChoices.CONFIRMED
        deletion_request.save(update_fields=["confirmed_at", "status"])

        # Audit log confirmation
        AuditService.log_event(
            action="account_deletion_confirmed",
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"request_id": str(deletion_request.id)},
        )

        # Process the deletion
        return AccountDeletionService.process_deletion(deletion_request.id)

    @staticmethod
    def process_deletion(request_id) -> AccountDeletionRequest:
        """Process the account deletion.

        Executes the actual deletion of user data. Should be called
        after confirmation or from a Celery task.

        Args:
            request_id: UUID of the AccountDeletionRequest.

        Returns:
            Updated AccountDeletionRequest instance.

        Raises:
            AccountDeletionRequest.DoesNotExist: If request not found.
            ValueError: If request is not confirmed.
        """
        deletion_request = AccountDeletionRequest.objects.select_related("user").get(id=request_id)

        if deletion_request.status not in [
            AccountDeletionRequest.StatusChoices.CONFIRMED,
            AccountDeletionRequest.StatusChoices.PENDING,  # Allow direct processing for admin
        ]:
            raise ValueError(
                f"Deletion request is not confirmed (status: {deletion_request.status})"
            )

        # Update status to processing
        deletion_request.status = AccountDeletionRequest.StatusChoices.PROCESSING
        deletion_request.save(update_fields=["status"])

        user = deletion_request.user
        user_email = user.email  # Save for notification
        user_id = user.id

        try:
            with transaction.atomic():
                # Record what data will be retained
                data_retained = AccountDeletionService._get_data_retention_summary(user)
                deletion_request.data_retained = data_retained

                # 1. Anonymise audit logs (retain structure, remove PII)
                AccountDeletionService._anonymise_audit_logs(user)

                # 2. Delete user-related data
                AccountDeletionService._delete_user_data(user)

                # 3. Delete the user account
                user.delete()

                # 4. Update deletion request
                deletion_request.user = None  # User is now deleted
                deletion_request.completed_at = timezone.now()
                deletion_request.status = AccountDeletionRequest.StatusChoices.COMPLETED
                deletion_request.save()

            # Send deletion confirmation email
            AccountDeletionService._send_deletion_complete_email(user_email)

            # Create a final audit log entry (without user reference)
            AuditLog.objects.create(
                action="account_deletion_completed",
                user=None,
                organisation=None,
                metadata={
                    "request_id": str(deletion_request.id),
                    "user_id": str(user_id),
                    "email_hash": AccountDeletionService._hash_email(user_email),
                },
            )

        except Exception as e:
            # Mark as failed but don't re-raise in production
            deletion_request.status = AccountDeletionRequest.StatusChoices.PENDING
            deletion_request.metadata = {"error": str(e)}
            deletion_request.save(update_fields=["status", "metadata"])
            raise

        return deletion_request

    @staticmethod
    def cancel_deletion(
        request_id,
        user: User,
        ip_address: str = "",
        user_agent: str = "",
    ) -> AccountDeletionRequest:
        """Cancel a pending deletion request.

        Args:
            request_id: UUID of the AccountDeletionRequest.
            user: User cancelling the request (for authorisation).
            ip_address: IP address of the request (for audit logging).
            user_agent: User agent string (for audit logging).

        Returns:
            Updated AccountDeletionRequest instance.

        Raises:
            AccountDeletionRequest.DoesNotExist: If request not found.
            ValueError: If request is not pending or doesn't belong to user.
        """
        try:
            deletion_request = AccountDeletionRequest.objects.get(
                id=request_id,
                user=user,
                status=AccountDeletionRequest.StatusChoices.PENDING,
            )
        except AccountDeletionRequest.DoesNotExist:
            raise ValueError("No pending deletion request found.")

        deletion_request.status = AccountDeletionRequest.StatusChoices.CANCELLED
        deletion_request.save(update_fields=["status"])

        # Clear deletion_requested_at on user
        user.deletion_requested_at = None
        user.save(update_fields=["deletion_requested_at"])

        # Audit log cancellation
        AuditService.log_event(
            action="account_deletion_cancelled",
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata={"request_id": str(deletion_request.id)},
        )

        return deletion_request

    @staticmethod
    def get_user_deletion_requests(user: User) -> list[AccountDeletionRequest]:
        """Get all deletion requests for a user.

        Args:
            user: User to get requests for.

        Returns:
            List of AccountDeletionRequest instances.
        """
        return list(AccountDeletionRequest.objects.filter(user=user).order_by("-created_at"))

    @staticmethod
    def _anonymise_audit_logs(user: User) -> int:
        """Anonymise audit logs for a user.

        Removes user reference and PII from metadata while preserving
        the log structure for legal compliance.

        Args:
            user: User whose logs should be anonymised.

        Returns:
            Number of logs anonymised.
        """
        logs = AuditLog.objects.filter(user=user)
        count = logs.count()

        for log in logs:
            # Remove user reference
            log.user = None

            # Anonymise metadata (remove email, names, etc.)
            if log.metadata:
                anonymised_metadata = {}
                for key, value in log.metadata.items():
                    if key not in ["email", "user_email", "first_name", "last_name", "name"]:
                        anonymised_metadata[key] = value
                anonymised_metadata["anonymised"] = True
                anonymised_metadata["anonymised_at"] = timezone.now().isoformat()
                log.metadata = anonymised_metadata

            log.save(update_fields=["user", "metadata"])

        return count

    @staticmethod
    def _delete_user_data(user: User) -> dict[str, int]:
        """Delete all user-related data.

        Removes data from related models that should not be retained.

        Args:
            user: User whose data should be deleted.

        Returns:
            Dictionary of model names to deletion counts.
        """
        counts = {}

        # Delete session tokens
        counts["session_tokens"] = SessionToken.objects.filter(user=user).delete()[0]

        # Delete TOTP devices
        counts["totp_devices"] = TOTPDevice.objects.filter(user=user).delete()[0]

        # Delete backup codes
        counts["backup_codes"] = BackupCode.objects.filter(user=user).delete()[0]

        # Delete password reset tokens
        counts["password_reset_tokens"] = PasswordResetToken.objects.filter(user=user).delete()[0]

        # Delete email verification tokens
        counts["email_verification_tokens"] = EmailVerificationToken.objects.filter(
            user=user
        ).delete()[0]

        # Delete password history
        counts["password_history"] = PasswordHistory.objects.filter(user=user).delete()[0]

        # Delete consent records
        counts["consent_records"] = ConsentRecord.objects.filter(user=user).delete()[0]

        # Delete data export requests (and their files)
        exports = DataExportRequest.objects.filter(user=user)
        for export in exports:
            if export.file_path:
                try:
                    os.remove(export.file_path)
                except OSError:
                    pass
        counts["data_export_requests"] = exports.delete()[0]

        # Delete user profile
        counts["user_profile"] = UserProfile.objects.filter(user=user).delete()[0]

        return counts

    @staticmethod
    def _get_data_retention_summary(user: User) -> list[str]:
        """Get summary of data that will be retained after deletion.

        Args:
            user: User being deleted.

        Returns:
            List of data retention notices.
        """
        audit_log_count = AuditLog.objects.filter(user=user).count()

        retained = []

        if audit_log_count > 0:
            retained.append(
                f"Anonymised audit logs ({audit_log_count} entries) - "
                "retained for 7 years for legal compliance"
            )

        retained.append("Account deletion request record - retained for compliance tracking")

        return retained

    @staticmethod
    def _send_confirmation_email(user: User, token: str) -> None:
        """Send deletion confirmation email.

        Args:
            user: User to send email to.
            token: Plain text confirmation token.
        """
        base_url = getattr(settings, "SITE_URL", "http://localhost:8000")
        confirmation_url = f"{base_url}/account/delete/confirm?token={token}"

        EmailService.send_email(
            to_email=user.email,
            subject="Confirm Account Deletion Request",
            template_name="account_deletion_confirmation",
            context={
                "user": user,
                "confirmation_url": confirmation_url,
                "expiry_hours": AccountDeletionService.CONFIRMATION_EXPIRY_HOURS,
            },
        )

    @staticmethod
    def _send_deletion_complete_email(email: str) -> None:
        """Send deletion complete notification email.

        Args:
            email: Email address to send to.
        """
        EmailService.send_email(
            to_email=email,
            subject="Account Deletion Complete",
            template_name="account_deletion_complete",
            context={
                "email": email,
            },
        )

    @staticmethod
    def _hash_email(email: str) -> str:
        """Hash email for anonymised logging.

        Args:
            email: Email to hash.

        Returns:
            SHA256 hash of the email (first 16 characters).
        """
        return hashlib.sha256(email.lower().encode()).hexdigest()[:16]
