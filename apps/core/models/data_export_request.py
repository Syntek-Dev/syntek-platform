"""DataExportRequest model for GDPR Article 15 compliance.

This module implements the Right of Access (Article 15) by tracking
user data export requests. Users can request their personal data in
machine-readable formats (JSON or CSV).
"""

import uuid

from django.db import models
from django.utils import timezone


class DataExportRequest(models.Model):
    """Track user data export requests (GDPR Article 15).

    Records requests for personal data exports under the Right of Access.
    Each request generates a file containing all user personal data in
    JSON or CSV format, available for 24 hours after generation.

    Attributes:
        id: UUID primary key
        user: Foreign key to User who requested the export
        status: Current status of the export request
        format: Export file format (JSON or CSV)
        file_path: Encrypted storage path of generated export file
        download_url: Signed URL for secure file download
        expires_at: Timestamp when download URL expires (24 hours from completion)
        created_at: Timestamp when request was created
        completed_at: Timestamp when export was completed
        metadata: Additional information about the export (file size, record counts)
    """

    class StatusChoices(models.TextChoices):
        """Export request status choices."""

        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        EXPIRED = "expired", "Expired"

    class FormatChoices(models.TextChoices):
        """Export file format choices."""

        JSON = "json", "JSON"
        CSV = "csv", "CSV"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
        related_name="data_export_requests",
        help_text="User who requested the data export",
    )

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        help_text="Current status of the export request",
    )

    format = models.CharField(
        max_length=10,
        choices=FormatChoices.choices,
        default=FormatChoices.JSON,
        help_text="Export file format (JSON or CSV)",
    )

    file_path = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="Storage path of generated export file",
    )

    download_url = models.CharField(
        max_length=1000,
        blank=True,
        default="",
        help_text="Signed URL for secure file download",
    )

    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when download URL expires (24 hours from completion)",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when request was created",
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp when export was completed",
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional export metadata (file size, record counts, etc.)",
    )

    class Meta:
        db_table = "data_export_requests"
        verbose_name = "Data Export Request"
        verbose_name_plural = "Data Export Requests"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self) -> str:
        """Return export request description."""
        return f"Data export for {self.user.email} ({self.status})"

    def is_expired(self) -> bool:
        """Check if the export download has expired.

        Returns:
            True if expires_at is in the past, False otherwise.
        """
        if self.expires_at is None:
            return False
        return timezone.now() > self.expires_at

    def mark_as_expired(self) -> None:
        """Mark the export as expired and update status."""
        self.status = self.StatusChoices.EXPIRED
        self.save(update_fields=["status"])
