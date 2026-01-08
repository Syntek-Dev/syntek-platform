"""AuditLog model skeleton.

This is a minimal skeleton for TDD. Tests will fail until fully implemented.
Minimum fields added to allow migrations to run.
"""

import uuid

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

        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        LOGIN_FAILED = "LOGIN_FAILED", "Login Failed"
        PASSWORD_CHANGE = "PASSWORD_CHANGE", "Password Change"
        PASSWORD_RESET = "PASSWORD_RESET", "Password Reset"
        EMAIL_VERIFIED = "EMAIL_VERIFIED", "Email Verified"
        TWO_FACTOR_ENABLED = "TWO_FACTOR_ENABLED", "Two Factor Enabled"
        TWO_FACTOR_DISABLED = "TWO_FACTOR_DISABLED", "Two Factor Disabled"
        ACCOUNT_LOCKED = "ACCOUNT_LOCKED", "Account Locked"
        ACCOUNT_UNLOCKED = "ACCOUNT_UNLOCKED", "Account Unlocked"

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
