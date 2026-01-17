"""Test environment Django settings for backend_template project.

This module contains settings specific to the test environment.
It extends base.py with test-specific configurations.
"""

from .base import *  # noqa: F403

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


# Note: Migrations are enabled for tests to ensure database schema is created.
# If tests become slow, consider using pytest-django's --reuse-db flag instead
# of disabling migrations entirely.

# Increase rate limits for tests to avoid test interference
RATELIMIT_GRAPHQL_MUTATION_REQUESTS_PER_MINUTE = 10000
RATELIMIT_GRAPHQL_QUERY_REQUESTS_PER_MINUTE = 10000
RATELIMIT_AUTH_REQUESTS_PER_MINUTE = 10000
RATELIMIT_API_REQUESTS_PER_MINUTE = 10000
RATELIMIT_DEFAULT_REQUESTS_PER_MINUTE = 10000

# Remove rate limiting middleware for tests (keep IP allowlist for security tests)
MIDDLEWARE = [
    m
    for m in MIDDLEWARE  # noqa: F405
    if m
    not in [
        "config.middleware.ratelimit.RateLimitMiddleware",
    ]
]

# IP allowlist for admin access - test environment allows localhost only
# Tests run locally, so restrict to localhost addresses
ADMIN_ALLOWED_IPS = [
    "127.0.0.1",  # localhost IPv4
    "::1",  # localhost IPv6
    "172.16.0.0/12",  # Docker networks (for CI/CD containers)
    "10.0.0.0/8",  # Private network range
    "192.168.0.0/16",  # Private network range
]

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
