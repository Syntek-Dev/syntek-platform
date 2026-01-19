"""AccountDeletionRequest model for GDPR Article 17 compliance.

This module implements the Right to Erasure (Article 17) by tracking
account deletion requests. Users can request permanent deletion of their
accounts with a confirmation workflow to prevent accidental deletions.
"""

import hashlib
import hmac
import secrets
import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class AccountDeletionRequest(models.Model):
    """Track account deletion requests (GDPR Article 17).

    Records user requests for account deletion under the Right to Erasure.
    Implements a confirmation workflow with hashed tokens to prevent
    accidental deletions. Tracks what data is retained for legal compliance.

    Attributes:
        id: UUID primary key
        user: Foreign key to User requesting account deletion
        status: Current status of the deletion request
        confirmation_token: Hashed confirmation token (HMAC-SHA256)
        reason: Optional user-provided reason for deletion
        data_retained: JSON list of data retained for legal compliance
        created_at: Timestamp when deletion was requested
        confirmed_at: Timestamp when deletion was confirmed by user
        completed_at: Timestamp when deletion was completed
        processed_by: Foreign key to User who processed the deletion (for admin-initiated)
    """

    class StatusChoices(models.TextChoices):
        """Account deletion status choices."""

        PENDING = "pending", "Pending Confirmation"
        CONFIRMED = "confirmed", "Confirmed"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="deletion_requests",
        help_text="User who requested account deletion",
    )

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        help_text="Current status of the deletion request",
    )

    confirmation_token = models.CharField(
        max_length=128,
        blank=True,
        default="",
        help_text="Hashed confirmation token (HMAC-SHA256)",
    )

    reason = models.TextField(
        blank=True,
        default="",
        help_text="Optional user-provided reason for deletion",
    )

    data_retained = models.JSONField(
        default=list,
        blank=True,
        help_text="JSON list of data retained for legal compliance (7 years)",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when deletion was requested",
    )

    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when deletion was confirmed by user",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when deletion was completed",
    )

    processed_by = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_deletions",
        help_text="User who processed the deletion (for admin-initiated deletions)",
    )

    class Meta:
        db_table = "account_deletion_requests"
        verbose_name = "Account Deletion Request"
        verbose_name_plural = "Account Deletion Requests"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["confirmation_token"]),
        ]

    def __str__(self) -> str:
        """Return deletion request description."""
        user_email = self.user.email if self.user else "Deleted User"
        return f"Deletion request for {user_email} ({self.status})"

    @staticmethod
    def generate_confirmation_token() -> tuple[str, str]:
        """Generate a confirmation token and its hash.

        Creates a cryptographically secure token and its HMAC-SHA256 hash
        for storage. The plain token is sent to the user, while the hash
        is stored in the database.

        Returns:
            Tuple of (plain_token, hashed_token)
        """
        plain_token = secrets.token_urlsafe(32)
        hashed_token = AccountDeletionRequest.hash_token(plain_token)
        return plain_token, hashed_token

    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a confirmation token using HMAC-SHA256.

        Args:
            token: Plain text confirmation token

        Returns:
            HMAC-SHA256 hash of the token
        """
        key = settings.SECRET_KEY.encode()
        return hmac.new(key, token.encode(), hashlib.sha256).hexdigest()

    def verify_token(self, plain_token: str) -> bool:
        """Verify a confirmation token against the stored hash.

        Uses constant-time comparison to prevent timing attacks.

        Args:
            plain_token: Plain text token to verify

        Returns:
            True if token matches the stored hash, False otherwise
        """
        expected_hash = AccountDeletionRequest.hash_token(plain_token)
        return hmac.compare_digest(self.confirmation_token, expected_hash)

    def is_expired(self, expiry_hours: int = 24) -> bool:
        """Check if the deletion request has expired.

        Deletion requests expire after 24 hours to prevent stale requests.

        Args:
            expiry_hours: Number of hours before expiry (default: 24)

        Returns:
            True if request is older than expiry_hours, False otherwise
        """
        if self.status != self.StatusChoices.PENDING:
            return False

        expiry_time = self.created_at + timezone.timedelta(hours=expiry_hours)
        return timezone.now() > expiry_time
