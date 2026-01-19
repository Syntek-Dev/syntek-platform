"""Management command for warming application cache on startup.

This command pre-loads frequently accessed data into the cache to improve
initial request performance after deployment or cache invalidation.

Warmed Data:
- User permissions (for active users)
- Organisation data (all organisations)
- TOTP device status (for 2FA users)
- Session token counts (for active users)

Usage:
    python manage.py warm_cache
    python manage.py warm_cache --limit 100
    python manage.py warm_cache --verbose
"""

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    """Management command for warming application cache.

    Pre-loads frequently accessed data into Redis/Valkey cache to prevent
    slow initial requests after deployment or cache flush.

    Features:
    - Warm user permissions
    - Warm organisation data
    - Warm 2FA device status
    - Progress reporting
    - Configurable user limit

    Example:
        ./manage.py warm_cache
        ./manage.py warm_cache --limit 50 --verbose
    """

    help = "Warm application cache with frequently accessed data"

    def add_arguments(self, parser):
        """Add command arguments.

        Args:
            parser: ArgumentParser instance
        """
        parser.add_argument(
            "--limit",
            type=int,
            default=0,
            help="Limit number of users to warm (0 = all, default: 0)",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Show verbose progress output",
        )
        parser.add_argument(
            "--ttl",
            type=int,
            default=3600,
            help="Cache TTL in seconds (default: 3600 = 1 hour)",
        )

    def handle(self, *args, **options):
        """Execute the cache warming command.

        Args:
            *args: Positional arguments
            **options: Command options from add_arguments
        """
        limit = options.get("limit", 0)
        verbose = options.get("verbose", False)
        ttl = options.get("ttl", 3600)

        self.stdout.write(self.style.SUCCESS("🔥 Starting cache warming..."))

        # Warm organisation data
        self._warm_organisations(ttl, verbose)

        # Warm user data
        self._warm_users(limit, ttl, verbose)

        # Warm permission data
        self._warm_permissions(limit, ttl, verbose)

        # Warm 2FA device status
        self._warm_totp_devices(limit, ttl, verbose)

        self.stdout.write("\n" + self.style.SUCCESS("✅ Cache warming complete!"))

    def _warm_organisations(self, ttl: int, verbose: bool) -> None:
        """Warm organisation data cache.

        Args:
            ttl: Cache TTL in seconds
            verbose: Whether to show progress
        """
        from apps.core.models import Organisation

        organisations = Organisation.objects.filter(is_active=True)
        count = organisations.count()

        self.stdout.write(f"\n📦 Warming {count} organisations...")

        for org in organisations:
            cache_key = f"org:{org.id}"
            cache_data = {
                "id": str(org.id),
                "name": org.name,
                "slug": org.slug,
                "is_active": org.is_active,
            }
            cache.set(cache_key, cache_data, timeout=ttl)

            if verbose:
                self.stdout.write(f"  ✓ Cached organisation: {org.name}")

        self.stdout.write(self.style.SUCCESS(f"  ✅ Warmed {count} organisations"))

    def _warm_users(self, limit: int, ttl: int, verbose: bool) -> None:
        """Warm user data cache.

        Args:
            limit: Maximum users to warm (0 = all)
            ttl: Cache TTL in seconds
            verbose: Whether to show progress
        """
        users = User.objects.filter(is_active=True).select_related("organisation")

        if limit > 0:
            users = users[:limit]

        count = users.count()
        self.stdout.write(f"\n👤 Warming {count} active users...")

        for user in users:
            cache_key = f"user:{user.id}"
            cache_data = {
                "id": str(user.id),
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "organisation_id": str(user.organisation_id) if user.organisation_id else None,
                "is_active": user.is_active,
                "email_verified": user.email_verified,
                "two_factor_enabled": user.two_factor_enabled,
            }
            cache.set(cache_key, cache_data, timeout=ttl)

            if verbose:
                self.stdout.write(f"  ✓ Cached user: {user.email}")

        self.stdout.write(self.style.SUCCESS(f"  ✅ Warmed {count} users"))

    def _warm_permissions(self, limit: int, ttl: int, verbose: bool) -> None:
        """Warm user permissions cache.

        Args:
            limit: Maximum users to warm (0 = all)
            ttl: Cache TTL in seconds
            verbose: Whether to show progress
        """
        users = User.objects.filter(is_active=True).prefetch_related(
            "groups",
            "user_permissions",
        )

        if limit > 0:
            users = users[:limit]

        count = users.count()
        self.stdout.write(f"\n🔒 Warming permissions for {count} users...")

        for user in users:
            # Cache user permissions
            cache_key = f"user_perms:{user.id}"
            permissions = list(user.get_all_permissions())
            cache.set(cache_key, permissions, timeout=ttl)

            # Cache user groups
            cache_key = f"user_groups:{user.id}"
            groups = list(user.groups.values_list("name", flat=True))
            cache.set(cache_key, groups, timeout=ttl)

            if verbose:
                self.stdout.write(
                    f"  ✓ Cached permissions for {user.email}: "
                    f"{len(permissions)} perms, {len(groups)} groups"
                )

        self.stdout.write(self.style.SUCCESS(f"  ✅ Warmed permissions for {count} users"))

    def _warm_totp_devices(self, limit: int, ttl: int, verbose: bool) -> None:
        """Warm 2FA device status cache.

        Args:
            limit: Maximum users to warm (0 = all)
            ttl: Cache TTL in seconds
            verbose: Whether to show progress
        """
        from apps.core.models import TOTPDevice

        users_with_2fa = User.objects.filter(
            is_active=True,
            two_factor_enabled=True,
        ).select_related("organisation")

        if limit > 0:
            users_with_2fa = users_with_2fa[:limit]

        count = users_with_2fa.count()
        self.stdout.write(f"\n🔐 Warming 2FA device status for {count} users...")

        for user in users_with_2fa:
            # Get confirmed TOTP devices for user
            devices = TOTPDevice.objects.filter(
                user=user,
                is_confirmed=True,
            ).values("id", "name", "last_used_at")

            cache_key = f"totp_devices:{user.id}"
            cache.set(cache_key, list(devices), timeout=ttl)

            if verbose:
                self.stdout.write(
                    f"  ✓ Cached 2FA devices for {user.email}: {len(devices)} devices"
                )

        self.stdout.write(self.style.SUCCESS(f"  ✅ Warmed 2FA status for {count} users"))
