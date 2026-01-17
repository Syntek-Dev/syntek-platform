"""Management command for cleaning up old audit logs.

This command archives or deletes audit logs older than the configured
retention period. Typically run as a daily cron job.

GDPR COMPLIANCE:
- Default retention: 90 days for security logs
- Configurable via AUDIT_LOG_RETENTION_DAYS setting
- Supports archiving to external storage before deletion

Usage:
    python manage.py cleanup_audit_logs
    python manage.py cleanup_audit_logs --dry-run
    python manage.py cleanup_audit_logs --retention-days=180
"""

from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    """Management command for audit log cleanup (H7).

    Archives and deletes audit logs older than the retention period.
    Supports dry-run mode for testing and custom retention periods.

    Features:
    - Configurable retention period
    - Dry-run mode for testing
    - Progress reporting
    - Archiving support (can be extended)

    Example:
        ./manage.py cleanup_audit_logs
        ./manage.py cleanup_audit_logs --dry-run --retention-days=60
    """

    help = "Clean up old audit logs based on retention policy"

    def add_arguments(self, parser):
        """Add command arguments.

        Args:
            parser: ArgumentParser instance.
        """
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Preview what would be deleted without actually deleting",
        )
        parser.add_argument(
            "--retention-days",
            type=int,
            default=None,
            help="Number of days to retain logs (overrides AUDIT_LOG_RETENTION_DAYS setting)",
        )
        parser.add_argument(
            "--archive",
            action="store_true",
            help="Archive logs to file before deletion (not yet implemented)",
        )

    def handle(self, *args, **options):
        """Execute the cleanup command.

        Args:
            *args: Positional arguments.
            **options: Command options from add_arguments.
        """
        from apps.core.models import AuditLog

        dry_run = options.get("dry_run", False)
        archive = options.get("archive", False)

        # Get retention period
        retention_days = options.get("retention_days")
        if retention_days is None:
            retention_days = getattr(settings, "AUDIT_LOG_RETENTION_DAYS", 90)

        self.stdout.write(f"Audit log retention period: {retention_days} days")

        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=retention_days)
        self.stdout.write(f"Cutoff date: {cutoff_date.strftime('%Y-%m-%d %H:%M:%S %Z')}")

        # Find logs to delete
        old_logs = AuditLog.objects.filter(created_at__lt=cutoff_date)
        count = old_logs.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"No audit logs older than {retention_days} days found. No action needed."
                )
            )
            return

        self.stdout.write(f"Found {count} audit logs older than {retention_days} days")

        # Dry run mode
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))
            self.stdout.write(f"Would delete {count} audit log entries")

            # Show sample of what would be deleted
            sample = old_logs.order_by("created_at")[:5]
            self.stdout.write("\nSample of logs that would be deleted:")
            for log in sample:
                self.stdout.write(
                    f"  - {log.created_at.strftime('%Y-%m-%d')} "
                    f"| {log.action} "
                    f"| {log.user.email if log.user else 'N/A'}"
                )

            if count > 5:
                self.stdout.write(f"  ... and {count - 5} more")

            return

        # Archive logs if requested
        if archive:
            self.stdout.write("Archiving logs...")
            archived_count = self._archive_logs(old_logs, cutoff_date)
            self.stdout.write(self.style.SUCCESS(f"Archived {archived_count} logs to file"))

        # Delete old logs
        self.stdout.write("Deleting old audit logs...")
        deleted_count, _ = old_logs.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully deleted {deleted_count} audit logs older than {retention_days} days"
            )
        )

        # Show statistics
        remaining_count = AuditLog.objects.count()
        self.stdout.write(f"\nRemaining audit logs: {remaining_count}")

    def _archive_logs(self, queryset, cutoff_date) -> int:
        """Archive logs to file before deletion.

        This is a placeholder implementation. In production, you might:
        - Export to S3/cloud storage
        - Write to compressed CSV
        - Send to log aggregation service (Splunk, ELK, etc.)

        Args:
            queryset: QuerySet of logs to archive.
            cutoff_date: Cutoff date for the archive.

        Returns:
            Number of logs archived.
        """
        import csv
        from pathlib import Path

        from apps.core.utils.encryption import IPEncryption

        # Create archive directory
        archive_dir = Path(settings.BASE_DIR) / "archives" / "audit_logs"
        archive_dir.mkdir(parents=True, exist_ok=True)

        # Create archive filename with date
        archive_file = archive_dir / f"audit_logs_{cutoff_date.strftime('%Y%m%d')}.csv"

        # Write to CSV
        with archive_file.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "ID",
                    "Action",
                    "User Email",
                    "Organisation",
                    "IP Address",
                    "User Agent",
                    "Device Fingerprint",
                    "Metadata",
                    "Created At",
                ]
            )

            count = 0
            for log in queryset.iterator(chunk_size=1000):
                # Decrypt IP for archive (admin access only)
                ip_address = ""
                if log.ip_address:
                    try:
                        ip_address = IPEncryption.decrypt_ip(log.ip_address)
                    except Exception:
                        ip_address = "[Encrypted]"

                writer.writerow(
                    [
                        str(log.id),
                        log.action,
                        log.user.email if log.user else "N/A",
                        log.organisation.name if log.organisation else "N/A",
                        ip_address,
                        log.user_agent,
                        log.device_fingerprint,
                        str(log.metadata),
                        log.created_at.isoformat(),
                    ]
                )
                count += 1

        self.stdout.write(f"Archive created: {archive_file}")
        return count
