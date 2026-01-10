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
        """
        # Only validate in production/staging (not during migrations or tests)
        if "migrate" in sys.argv or "makemigrations" in sys.argv or "test" in sys.argv:
            return

        self._validate_ip_encryption_key()

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
                    "IP_ENCRYPTION_KEY validation failed: "
                    "Encrypt/decrypt test did not match."
                )

            logger.info("✅ IP encryption key validated successfully")

        except (ValueError, InvalidToken, TypeError) as e:
            raise ImproperlyConfigured(
                f"IP_ENCRYPTION_KEY is invalid: {e}. "
                f"The key must be a valid Fernet key (32 url-safe base64-encoded bytes). "
                f"Generate a new key with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
            ) from e
