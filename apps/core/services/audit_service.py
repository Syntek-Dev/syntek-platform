"""Audit logging service for security event tracking.

This module provides centralised audit logging for all security-relevant
events including authentication, authorisation, and data access.

SECURITY NOTE:
- All events logged with encrypted IP addresses
- Timestamps in UTC with timezone awareness
- Immutable logs (no updates, only inserts)
- Organisation-scoped for multi-tenancy

Example:
    >>> AuditService.log_login(user, ip_address, device_fingerprint)
    >>> AuditService.log_login_failed(email, ip_address)
"""

from apps.core.models import AuditLog, Organisation, User
from apps.core.utils.encryption import IPEncryption


class AuditService:
    """Service for security audit logging.

    Handles creation and retrieval of audit logs for security events.
    All logs include encrypted IP addresses and device fingerprints.

    Security Features:
    - Immutable logs (no updates after creation)
    - IP address encryption before storage
    - Organisation-scoped access
    - Device fingerprinting for session tracking

    Attributes:
        None - All methods are static
    """

    @staticmethod
    def log_event(
        action: str,
        user: User | None = None,
        organisation: Organisation | None = None,
        ip_address: str = "",
        user_agent: str = "",
        device_fingerprint: str = "",
        metadata: dict | None = None,
    ) -> AuditLog:
        """Log a security event.

        Args:
            action: Event action type (from AuditLog.ActionType)
            user: User who performed the action (None for failed login)
            organisation: Organisation context
            ip_address: IP address (will be encrypted)
            user_agent: Browser user agent string
            device_fingerprint: Device identifier
            metadata: Additional JSON metadata

        Returns:
            Created AuditLog instance
        """
        # Encrypt IP address if provided
        encrypted_ip = None
        if ip_address:
            encrypted_ip = IPEncryption.encrypt_ip(ip_address)

        # Create audit log
        log = AuditLog.objects.create(
            action=action,
            user=user,
            organisation=organisation or (user.organisation if user else None),
            ip_address=encrypted_ip,
            user_agent=user_agent,
            device_fingerprint=device_fingerprint,
            metadata=metadata or {},
        )

        return log

    @staticmethod
    def log_login(
        user: User,
        ip_address: str,
        device_fingerprint: str = "",
        user_agent: str = "",
    ) -> AuditLog:
        """Log successful login event.

        Args:
            user: User who logged in
            ip_address: IP address (will be encrypted)
            device_fingerprint: Device identifier
            user_agent: Browser user agent string

        Returns:
            Created AuditLog instance
        """
        return AuditService.log_event(
            action=AuditLog.ActionType.LOGIN,
            user=user,
            ip_address=ip_address,
            device_fingerprint=device_fingerprint,
            user_agent=user_agent,
        )

    @staticmethod
    def log_login_failed(
        email: str,
        ip_address: str,
        device_fingerprint: str = "",
        user_agent: str = "",
        organisation: Organisation | None = None,
    ) -> AuditLog:
        """Log failed login attempt.

        Args:
            email: Email address used in failed login
            ip_address: IP address (will be encrypted)
            device_fingerprint: Device identifier
            user_agent: Browser user agent string
            organisation: Organisation context if known

        Returns:
            Created AuditLog instance
        """
        return AuditService.log_event(
            action=AuditLog.ActionType.LOGIN_FAILED,
            user=None,
            organisation=organisation,
            ip_address=ip_address,
            device_fingerprint=device_fingerprint,
            user_agent=user_agent,
            metadata={"email": email},
        )

    @staticmethod
    def log_logout(user: User, ip_address: str = "") -> AuditLog:
        """Log logout event.

        Args:
            user: User who logged out
            ip_address: IP address (will be encrypted)

        Returns:
            Created AuditLog instance
        """
        return AuditService.log_event(
            action=AuditLog.ActionType.LOGOUT,
            user=user,
            ip_address=ip_address,
        )

    @staticmethod
    def log_password_change(user: User, ip_address: str = "") -> AuditLog:
        """Log password change event.

        Args:
            user: User who changed password
            ip_address: IP address (will be encrypted)

        Returns:
            Created AuditLog instance
        """
        return AuditService.log_event(
            action=AuditLog.ActionType.PASSWORD_CHANGE,
            user=user,
            ip_address=ip_address,
        )

    @staticmethod
    def get_user_logs(user: User, limit: int = 100) -> list:
        """Get recent audit logs for a user.

        Args:
            user: User to get logs for
            limit: Maximum number of logs to return

        Returns:
            List of AuditLog instances
        """
        return list(AuditLog.objects.filter(user=user).order_by("-created_at")[:limit])

    @staticmethod
    def get_organisation_logs(organisation: Organisation, limit: int = 100) -> list:
        """Get recent audit logs for an organisation.

        Args:
            organisation: Organisation to get logs for
            limit: Maximum number of logs to return

        Returns:
            List of AuditLog instances
        """
        return list(
            AuditLog.objects.filter(organisation=organisation).order_by("-created_at")[:limit]
        )
