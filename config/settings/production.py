"""Production environment Django settings for backend_template project.

This module contains settings specific to the production environment.
It extends base.py with production-specific configurations.
"""

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from .base import *  # noqa: F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")  # noqa: F405

# Security settings
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Additional session security for production
SESSION_COOKIE_SAMESITE = "Strict"  # Stricter than base setting
SESSION_COOKIE_AGE = 3600  # 1 hour for production (shorter than base setting)
SESSION_SAVE_EVERY_REQUEST = True  # Extend session on activity
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# CSRF security for production
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_SAMESITE = "Strict"  # Stricter than base setting

# IP allowlist for admin access - production MUST have restricted IPs
# REQUIRED: Set ADMIN_ALLOWED_IPS environment variable with trusted IPs
# Example: ADMIN_ALLOWED_IPS="10.0.0.1,192.168.1.0/24,203.0.113.5"
# WARNING: If not set, admin access will NOT be IP-restricted
ADMIN_ALLOWED_IPS = env.list("ADMIN_ALLOWED_IPS", default=[])  # noqa: F405

# GraphQL security - disable introspection in production
GRAPHQL_ENABLE_INTROSPECTION = False

# Email backend for production
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")  # noqa: F405
EMAIL_PORT = env.int("EMAIL_PORT", default=587)  # noqa: F405
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER")  # noqa: F405
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")  # noqa: F405
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")  # noqa: F405
SERVER_EMAIL = env("SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)  # noqa: F405

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "security_console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "level": "INFO",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
        "security.audit": {
            "handlers": ["security_console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# =============================================================================
# Sentry Error Tracking, Logging, Profiling, and Metrics
# =============================================================================
# Requires: SENTRY_DSN environment variable
# See: https://docs.sentry.io/platforms/python/integrations/django/

SENTRY_DSN = env("SENTRY_DSN", default="")  # noqa: F405
if SENTRY_DSN:
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    # Configure which log levels are captured
    sentry_logging = LoggingIntegration(
        level=env.int("SENTRY_LOG_LEVEL", default=20),  # noqa: F405  # INFO=20
        event_level=env.int("SENTRY_EVENT_LEVEL", default=40),  # noqa: F405  # ERROR=40
    )

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            sentry_logging,
            RedisIntegration(),
        ],
        # Environment identifier in Sentry dashboard
        environment=env("SENTRY_ENVIRONMENT", default="production"),  # noqa: F405
        # Release version for tracking deployments
        release=env("SENTRY_RELEASE", default=None),  # noqa: F405
        # Add request headers, IP addresses, and user info to events
        # See: https://docs.sentry.io/platforms/python/data-management/data-collected/
        send_default_pii=env.bool("SENTRY_SEND_PII", default=True),  # noqa: F405
        # Enable sending logs to Sentry
        _experiments={
            "enable_logs": env.bool("SENTRY_ENABLE_LOGS", default=True),  # noqa: F405
        },
        # Performance Monitoring: capture transactions for tracing
        # 1.0 = 100% of transactions, 0.1 = 10%
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=1.0),  # noqa: F405
        # Profiling: sample rate for profile sessions
        # 1.0 = 100% of sessions profiled
        profile_session_sample_rate=env.float(  # noqa: F405
            "SENTRY_PROFILE_SESSION_SAMPLE_RATE", default=1.0
        ),
        # Profile lifecycle: "trace" runs profiler during active transactions
        profile_lifecycle=env("SENTRY_PROFILE_LIFECYCLE", default="trace"),  # noqa: F405
        # Enable tracing for database queries
        enable_db_query_source=True,
        # Set threshold for slow DB query warnings (ms)
        db_query_source_threshold_ms=100,
    )

# CSP (Content Security Policy) headers
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'",)
