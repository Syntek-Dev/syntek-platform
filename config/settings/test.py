"""Test environment Django settings for backend_template project.

This module contains settings specific to the test environment.
It extends base.py with test-specific configurations.
"""

from .base import *  # noqa: F403, F401

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)  # noqa: F405

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])  # noqa: F405

# Fast password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Use in-memory cache for tests
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Email backend for tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"


# Disable migrations for faster tests
class DisableMigrations:
    """Disable migrations during tests for faster execution."""

    def __contains__(self, item):
        """Check if item is in migrations."""
        return True

    def __getitem__(self, item):
        """Return None to disable migrations."""
        return None


MIGRATION_MODULES = DisableMigrations()

# Logging configuration (minimal for tests)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}
