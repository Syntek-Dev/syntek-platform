"""AuditLog model skeleton.

This is a minimal skeleton for TDD. Tests will fail until fully implemented.
Minimum fields added to allow migrations to run.
"""

import uuid
from typing import ClassVar

from django.db import models


class AuditLog(models.Model):
    """Audit log for tracking security-relevant user actions.

    Records authentication events, permission changes, and other
    security-relevant activities with encrypted IP addresses and
    device fingerprinting (H8).

    Attributes:
        id: UUID primary key
        user: Foreign key to User (nullable for failed login attempts)
        organisation: Foreign key to Organisation (nullable)
        action: Type of action performed (see ActionType choices)
        ip_address: Encrypted IP address (BinaryField for Fernet encryption)
        user_agent: Browser user agent string
        device_fingerprint: Device identifier hash (H8)
        metadata: Additional JSON metadata for the action
        created_at: Timestamp when action occurred
    """

    class ActionType(models.TextChoices):
        """Choices for audit log action types."""

        LOGIN: ClassVar[str] = "LOGIN", "Login"  # type: ignore[assignment]
        LOGOUT: ClassVar[str] = "LOGOUT", "Logout"  # type: ignore[assignment]
        LOGIN_FAILED: ClassVar[str] = "LOGIN_FAILED", "Login Failed"  # type: ignore[assignment]
        PASSWORD_CHANGE: ClassVar[str] = "PASSWORD_CHANGE", "Password Change"  # type: ignore[assignment]
        PASSWORD_RESET: ClassVar[str] = "PASSWORD_RESET", "Password Reset"  # type: ignore[assignment]
        EMAIL_VERIFIED: ClassVar[str] = "EMAIL_VERIFIED", "Email Verified"  # type: ignore[assignment]
        TWO_FACTOR_ENABLED: ClassVar[str] = "TWO_FACTOR_ENABLED", "Two Factor Enabled"  # type: ignore[assignment]
        TWO_FACTOR_DISABLED: ClassVar[str] = "TWO_FACTOR_DISABLED", "Two Factor Disabled"  # type: ignore[assignment]
        ACCOUNT_LOCKED: ClassVar[str] = "ACCOUNT_LOCKED", "Account Locked"  # type: ignore[assignment]
        ACCOUNT_UNLOCKED: ClassVar[str] = "ACCOUNT_UNLOCKED", "Account Unlocked"  # type: ignore[assignment]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    organisation = models.ForeignKey(
        "core.Organisation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=50, choices=ActionType.choices)
    ip_address = models.BinaryField(null=True, blank=True)
    user_agent = models.TextField(blank=True, default="")
    device_fingerprint = models.CharField(max_length=64, blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["organisation", "-created_at"]),
            models.Index(fields=["action", "-created_at"]),
            models.Index(fields=["created_at"]),
            # H1: Composite index for filtering user actions
            models.Index(fields=["user", "action"]),
        ]

    def __str__(self) -> str:
        """Return audit log description."""
        user_email = self.user.email if self.user else "Unknown"
        return f"{self.action} by {user_email} at {self.created_at}"
