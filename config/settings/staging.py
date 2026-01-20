"""Staging environment Django settings for backend_template project.

This module contains settings specific to the staging environment.
It extends base.py with staging-specific configurations.
"""

from .base import *  # noqa: F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)  # noqa: F405

# ALLOWED_HOSTS must be explicitly set in staging - no wildcards for security
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")  # noqa: F405

# Security settings (mirror production for accurate testing)
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Session security (mirror production)
SESSION_COOKIE_SAMESITE = "Strict"
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# CSRF security
CSRF_COOKIE_SAMESITE = "Strict"

# IP allowlist for admin access - staging should use restricted IPs
# REQUIRED: Set ADMIN_ALLOWED_IPS environment variable with trusted IPs
# Example: ADMIN_ALLOWED_IPS="10.0.0.1,192.168.1.0/24,203.0.113.5"
ADMIN_ALLOWED_IPS = env.list("ADMIN_ALLOWED_IPS", default=[])  # noqa: F405

# GraphQL security - optionally enable introspection for staging
GRAPHQL_ENABLE_INTROSPECTION = env.bool("GRAPHQL_ENABLE_INTROSPECTION", default=True)  # noqa: F405

# Email backend for staging
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="smtp.sendgrid.net")  # noqa: F405
EMAIL_PORT = env.int("EMAIL_PORT", default=587)  # noqa: F405
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")  # noqa: F405
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")  # noqa: F405
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@example.com")  # noqa: F405

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "security_console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
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
# Staging mirrors production settings for accurate testing
# See: https://docs.sentry.io/platforms/python/integrations/django/

SENTRY_DSN = env("SENTRY_DSN", default="")  # noqa: F405
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
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
        environment=env("SENTRY_ENVIRONMENT", default="staging"),  # noqa: F405
        # Release version for tracking deployments
        release=env("SENTRY_RELEASE", default=None),  # noqa: F405
        # Add request headers, IP addresses, and user info to events
        send_default_pii=env.bool("SENTRY_SEND_PII", default=True),  # noqa: F405
        # Enable sending logs to Sentry
        _experiments={
            "enable_logs": env.bool("SENTRY_ENABLE_LOGS", default=True),  # noqa: F405
        },
        # Performance Monitoring: capture 100% in staging for thorough testing
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=1.0),  # noqa: F405
        # Profiling: sample rate for profile sessions
        profile_session_sample_rate=env.float(  # noqa: F405
            "SENTRY_PROFILE_SESSION_SAMPLE_RATE", default=1.0
        ),
        # Profile lifecycle: "trace" runs profiler during active transactions
        profile_lifecycle=env("SENTRY_PROFILE_LIFECYCLE", default="trace"),  # noqa: F405
        # Enable tracing for database queries
        enable_db_query_source=True,
        db_query_source_threshold_ms=100,
    )
