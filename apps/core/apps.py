"""Core application configuration."""

import logging
import sys

from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from cryptography.fernet import Fernet, InvalidToken

logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    """Configuration for core application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"

    def ready(self):
        """Perform app initialisation on startup.

        Validates encryption keys and other critical configuration.
        Ensures all required security keys are present and valid before
        the application starts accepting requests.
        """
        # Only validate in production/staging (not during migrations or tests)
        if "migrate" in sys.argv or "makemigrations" in sys.argv or "test" in sys.argv:
            return

        # Validate all encryption and signing keys
        self._validate_token_signing_key()
        self._validate_totp_encryption_key()
        self._validate_ip_encryption_key()

        logger.info("✅ All security keys validated successfully")

        # Warm cache on startup if enabled
        if getattr(settings, "WARM_CACHE_ON_STARTUP", False):
            self._warm_cache_on_startup()

    def _validate_token_signing_key(self):
        """Validate token signing key on startup.

        The TOKEN_SIGNING_KEY is used for HMAC-SHA256 signing of authentication tokens.
        This validation ensures the key is present and has sufficient entropy.

        Raises:
            ImproperlyConfigured: If TOKEN_SIGNING_KEY is invalid or missing
        """
        import hashlib
        import hmac

        # Check if TOKEN_SIGNING_KEY is set
        if not hasattr(settings, "TOKEN_SIGNING_KEY"):
            raise ImproperlyConfigured(
                "TOKEN_SIGNING_KEY is not set in settings. "
                "Please set TOKEN_SIGNING_KEY environment variable. "
                'Generate with: python -c "import secrets; print(secrets.token_hex(32))"'
            )

        signing_key = settings.TOKEN_SIGNING_KEY

        # Ensure key is not empty
        if not signing_key or not signing_key.strip():
            raise ImproperlyConfigured(
                "TOKEN_SIGNING_KEY cannot be empty. "
                'Generate with: python -c "import secrets; print(secrets.token_hex(32))"'
            )

        # Ensure key is a string
        if not isinstance(signing_key, str):
            raise ImproperlyConfigured(
                f"TOKEN_SIGNING_KEY must be a string, got {type(signing_key).__name__}"
            )

        # Validate minimum key length (at least 32 characters for security)
        if len(signing_key) < 32:
            raise ImproperlyConfigured(
                f"TOKEN_SIGNING_KEY is too short ({len(signing_key)} characters). "
                "Minimum length is 32 characters for security. "
                'Generate with: python -c "import secrets; print(secrets.token_hex(32))"'
            )

        # Test HMAC signing to ensure key works
        try:
            test_message = b"test_token_validation"
            key_bytes = signing_key.encode()
            signature = hmac.new(key_bytes, test_message, hashlib.sha256).hexdigest()

            # Verify the signature can be recreated (deterministic)
            verification = hmac.new(key_bytes, test_message, hashlib.sha256).hexdigest()
            if signature != verification:
                raise ImproperlyConfigured(
                    "TOKEN_SIGNING_KEY validation failed: HMAC signing is not deterministic"
                )

            logger.info("✅ Token signing key validated successfully")

        except Exception as e:
            raise ImproperlyConfigured(
                f"TOKEN_SIGNING_KEY validation failed: {e}. "
                'Generate a new key with: python -c "import secrets; print(secrets.token_hex(32))"'
            ) from e

    def _validate_totp_encryption_key(self):
        """Validate TOTP encryption key on startup.

        The TOTP_ENCRYPTION_KEY is used for Fernet encryption of TOTP secrets.
        This validation ensures the key is present and properly formatted.

        Raises:
            ImproperlyConfigured: If TOTP_ENCRYPTION_KEY is invalid or missing
        """
        # Check if TOTP_ENCRYPTION_KEY is set
        if not hasattr(settings, "TOTP_ENCRYPTION_KEY"):
            raise ImproperlyConfigured(
                "TOTP_ENCRYPTION_KEY is not set in settings. "
                "Please set TOTP_ENCRYPTION_KEY environment variable. "
                "Generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            )

        totp_key = settings.TOTP_ENCRYPTION_KEY

        # Ensure key is not empty
        if not totp_key:
            raise ImproperlyConfigured(
                "TOTP_ENCRYPTION_KEY cannot be empty. "
                "Generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            )

        # Convert to bytes if string
        if isinstance(totp_key, str):
            totp_key = totp_key.encode()

        # Validate key format
        try:
            # Attempt to create Fernet instance to validate key format
            fernet = Fernet(totp_key)

            # Test encrypt/decrypt to ensure key is valid
            test_secret = b"test_totp_secret_ABCDEFGH12345678"
            encrypted = fernet.encrypt(test_secret)
            decrypted = fernet.decrypt(encrypted)

            if decrypted != test_secret:
                raise ImproperlyConfigured(
                    "TOTP_ENCRYPTION_KEY validation failed: Encrypt/decrypt test did not match"
                )

            logger.info("✅ TOTP encryption key validated successfully")

        except (ValueError, InvalidToken, TypeError) as e:
            raise ImproperlyConfigured(
                f"TOTP_ENCRYPTION_KEY is invalid: {e}. "
                f"The key must be a valid Fernet key (32 url-safe base64-encoded bytes). "
                f"Generate with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            ) from e

    def _validate_ip_encryption_key(self):
        """Validate IP encryption key on startup (SV4).

        Raises:
            ImproperlyConfigured: If IP_ENCRYPTION_KEY is invalid or missing
        """
        # Check if IP_ENCRYPTION_KEY is set
        if not hasattr(settings, "IP_ENCRYPTION_KEY"):
            raise ImproperlyConfigured(
                "IP_ENCRYPTION_KEY is not set in settings. "
                "Please set IP_ENCRYPTION_KEY environment variable."
            )

        ip_key = settings.IP_ENCRYPTION_KEY

        # Convert to bytes if string
        if isinstance(ip_key, str):
            ip_key = ip_key.encode()

        # Validate key format
        try:
            # Attempt to create Fernet instance to validate key format
            fernet = Fernet(ip_key)

            # Test encrypt/decrypt to ensure key is valid
            test_data = b"test_ip_192.168.1.1"
            encrypted = fernet.encrypt(test_data)
            decrypted = fernet.decrypt(encrypted)

            if decrypted != test_data:
                raise ImproperlyConfigured(
                    "IP_ENCRYPTION_KEY validation failed: Encrypt/decrypt test did not match."
                )

            logger.info("✅ IP encryption key validated successfully")

        except (ValueError, InvalidToken, TypeError) as e:
            raise ImproperlyConfigured(
                f"IP_ENCRYPTION_KEY is invalid: {e}. "
                f"The key must be a valid Fernet key (32 url-safe base64-encoded bytes). "
                f"Generate a new key with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            ) from e

    def _warm_cache_on_startup(self):
        """Warm cache with frequently accessed data on application startup.

        This method is called during app initialization if WARM_CACHE_ON_STARTUP
        setting is True. It pre-loads commonly accessed data into the cache to
        improve initial request performance.

        Note:
            Only warms a limited number of users (50 by default) to avoid
            slowing down startup. Full cache warming should use the management
            command: python manage.py warm_cache
        """
        from django.contrib.auth import get_user_model
        from django.core.cache import cache

        User = get_user_model()

        try:
            logger.info("🔥 Warming cache on startup...")

            # Warm organisations (all active)
            from apps.core.models import Organisation

            organisations = Organisation.objects.filter(is_active=True)
            for org in organisations:
                cache_key = f"org:{org.id}"
                cache_data = {
                    "id": str(org.id),
                    "name": org.name,
                    "slug": org.slug,
                    "is_active": org.is_active,
                }
                cache.set(cache_key, cache_data, timeout=3600)

            logger.info(f"✅ Warmed {organisations.count()} organisations")

            # Warm users (limited to 50 most recently active)
            users = (
                User.objects.filter(is_active=True)
                .select_related("organisation")
                .order_by("-last_login")[:50]
            )

            for user in users:
                # Cache user data
                cache_key = f"user:{user.id}"
                cache_data = {
                    "id": str(user.id),
                    "email": user.email,
                    "organisation_id": str(user.organisation_id) if user.organisation_id else None,
                    "is_active": user.is_active,
                    "email_verified": user.email_verified,
                    "two_factor_enabled": user.two_factor_enabled,
                }
                cache.set(cache_key, cache_data, timeout=3600)

                # Cache user permissions
                cache_key = f"user_perms:{user.id}"
                permissions = list(user.get_all_permissions())
                cache.set(cache_key, permissions, timeout=3600)

            logger.info(f"✅ Warmed {users.count()} users with permissions")
            logger.info("✅ Cache warming complete")

        except Exception as e:
            # Log error but don't crash startup
            logger.warning(f"⚠️  Cache warming failed: {e}")
            logger.warning("Application will start without warmed cache")
