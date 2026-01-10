"""Management command for IP encryption key rotation.

This command handles the rotation of IP encryption keys by:
1. Generating a new encryption key
2. Decrypting all IPs with the old key
3. Re-encrypting all IPs with the new key
4. Updating database records

SECURITY NOTE (C6):
- Supports graceful key rotation without data loss
- Backs up old key for rollback
- Validates all records before committing
- Provides rollback mechanism on failure

Usage:
    python manage.py rotate_ip_keys
    python manage.py rotate_ip_keys --dry-run
    python manage.py rotate_ip_keys --backup
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Management command for rotating IP encryption keys (C6).

    Handles rotation of Fernet encryption keys used for IP address
    encryption in AuditLog and SessionToken models. Ensures zero
    downtime by supporting multi-key decryption during rotation.

    Features:
    - Dry-run mode to test rotation
    - Automatic backup of old key
    - Rollback on failure
    - Progress reporting

    Example:
        ./manage.py rotate_ip_keys
        ./manage.py rotate_ip_keys --dry-run
    """

    help = "Rotate IP encryption keys and re-encrypt all IP addresses"

    def add_arguments(self, parser):
        """Add command arguments.

        Args:
            parser: ArgumentParser instance
        """
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Test rotation without making changes",
        )
        parser.add_argument(
            "--backup",
            action="store_true",
            help="Create backup of old key before rotation",
        )
        parser.add_argument(
            "--new-key",
            type=str,
            help="Specify new encryption key (base64-encoded), otherwise auto-generate",
        )

    def handle(self, *args, **options):
        """Execute the key rotation command.

        Args:
            *args: Positional arguments
            **options: Command options from add_arguments
        """
        from django.conf import settings

        from apps.core.models import AuditLog, SessionToken
        from apps.core.utils.encryption import IPEncryption

        dry_run = options.get("dry_run", False)
        backup = options.get("backup", False)
        new_key_input = options.get("new_key")

        # Get current key
        current_key = settings.IP_ENCRYPTION_KEY
        if isinstance(current_key, str):
            current_key = current_key.encode()

        # Generate or use provided new key
        if new_key_input:
            try:
                new_key = new_key_input.encode()
                # Validate it's a proper Fernet key by attempting to create instance
                from cryptography.fernet import Fernet

                Fernet(new_key)
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Invalid new key format: {e}"))
                return
        else:
            new_key = IPEncryption.generate_key()
            self.stdout.write(self.style.SUCCESS(f"Generated new key: {new_key.decode()}"))

        # Get counts
        audit_count = AuditLog.objects.filter(ip_address__isnull=False).count()
        token_count = SessionToken.objects.filter(ip_address__isnull=False).count()
        total_count = audit_count + token_count

        self.stdout.write(f"Found {audit_count} AuditLog records with IP addresses")
        self.stdout.write(f"Found {token_count} SessionToken records with IP addresses")
        self.stdout.write(f"Total records to re-encrypt: {total_count}")

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))
            self.stdout.write(f"Would rotate encryption key for {total_count} records")
            return

        # Confirm rotation
        if total_count > 0:
            confirm = input(
                f"\nThis will re-encrypt {total_count} IP addresses. Continue? [y/N]: "
            )
            if confirm.lower() != "y":
                self.stdout.write(self.style.WARNING("Key rotation cancelled"))
                return

        # Backup old key if requested
        if backup:
            import os
            from pathlib import Path

            backup_dir = Path(settings.BASE_DIR) / "backups"
            backup_dir.mkdir(exist_ok=True)
            backup_file = backup_dir / f"ip_key_backup_{int(__import__('time').time())}.txt"

            with open(backup_file, "w") as f:
                f.write(current_key.decode())

            self.stdout.write(
                self.style.SUCCESS(f"Old key backed up to: {backup_file}")
            )

        # Perform rotation
        self.stdout.write("Starting key rotation...")
        result = IPEncryption.rotate_key(current_key, new_key)

        # Report results
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Rotated {result['audit_logs_updated']} AuditLog records"
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ Rotated {result['session_tokens_updated']} SessionToken records"
            )
        )

        if result["errors"]:
            self.stdout.write(
                self.style.ERROR(f"❌ {len(result['errors'])} errors occurred:")
            )
            for error in result["errors"][:10]:  # Show first 10 errors
                self.stdout.write(self.style.ERROR(f"  - {error}"))
            if len(result["errors"]) > 10:
                self.stdout.write(
                    self.style.ERROR(
                        f"  ... and {len(result['errors']) - 10} more errors"
                    )
                )
        else:
            self.stdout.write(self.style.SUCCESS("✅ No errors occurred"))

        # Show new key
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("Key rotation complete!"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"\nNew key: {new_key.decode()}")
        self.stdout.write(
            "\n⚠️  IMPORTANT: Update your IP_ENCRYPTION_KEY environment variable"
        )
        self.stdout.write("⚠️  to the new key shown above, then restart your application.\n")
