"""Development environment Django settings for backend_template project.

This module contains settings specific to the development environment.
It extends base.py with development-specific configurations.
"""

import socket

from .base import *  # noqa: F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=True)  # noqa: F405

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1", "*"])  # noqa: F405

# Development-specific installed apps
INSTALLED_APPS += [  # noqa: F405
    "django_extensions",
    "debug_toolbar",
]

# Development-specific middleware
MIDDLEWARE += [  # noqa: F405
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

# Debug Toolbar configuration
INTERNAL_IPS = [
    "127.0.0.1",
    "localhost",
]

# Docker support: add container gateway IP for debug toolbar
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS += [ip[: ip.rfind(".")] + ".1" for ip in ips]

# IP allowlist for admin access - development allows localhost only
# In development, admin access is restricted to localhost and Docker network
ADMIN_ALLOWED_IPS = env.list(  # noqa: F405
    "ADMIN_ALLOWED_IPS",
    default=[
        "127.0.0.1",  # localhost IPv4
        "::1",  # localhost IPv6
        "172.16.0.0/12",  # Docker networks
        "10.0.0.0/8",  # Private network range
        "192.168.0.0/16",  # Private network range
    ],
)

# Email backend for development (Mailpit)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST", default="mailpit")  # noqa: F405
EMAIL_PORT = env.int("EMAIL_PORT", default=1025)  # noqa: F405
EMAIL_USE_TLS = False
EMAIL_USE_SSL = False

# GraphQL security - enable introspection in development
GRAPHQL_ENABLE_INTROSPECTION = True

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
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
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False,
        },
        "security.audit": {
            "handlers": ["security_console"],
            "level": "DEBUG",  # More verbose in development
            "propagate": False,
        },
    },
}

# =============================================================================
# Sentry (Optional in Development)
# =============================================================================
# Enable Sentry in development for testing the integration
# Set SENTRY_DSN in .env.dev to enable

SENTRY_DSN = env("SENTRY_DSN", default="")  # noqa: F405
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    from sentry_sdk.integrations.redis import RedisIntegration

    sentry_logging = LoggingIntegration(
        level=env.int("SENTRY_LOG_LEVEL", default=10),  # noqa: F405  # DEBUG=10 in dev
        event_level=env.int("SENTRY_EVENT_LEVEL", default=40),  # noqa: F405  # ERROR=40
    )

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            sentry_logging,
            RedisIntegration(),
        ],
        environment=env("SENTRY_ENVIRONMENT", default="development"),  # noqa: F405
        release=env("SENTRY_RELEASE", default=None),  # noqa: F405
        send_default_pii=env.bool("SENTRY_SEND_PII", default=True),  # noqa: F405
        _experiments={
            "enable_logs": env.bool("SENTRY_ENABLE_LOGS", default=True),  # noqa: F405
        },
        traces_sample_rate=env.float("SENTRY_TRACES_SAMPLE_RATE", default=1.0),  # noqa: F405
        profile_session_sample_rate=env.float(  # noqa: F405
            "SENTRY_PROFILE_SESSION_SAMPLE_RATE", default=1.0
        ),
        profile_lifecycle=env("SENTRY_PROFILE_LIFECYCLE", default="trace"),  # noqa: F405
        enable_db_query_source=True,
        db_query_source_threshold_ms=100,
        debug=True,  # Enable debug mode in development
    )
