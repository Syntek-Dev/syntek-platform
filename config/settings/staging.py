"""Staging environment Django settings for backend_template project.

This module contains settings specific to the staging environment.
It extends base.py with staging-specific configurations.
"""

from .base import *  # noqa: F403, F401

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

# Sentry configuration (optional)
if env("SENTRY_DSN", default=None):  # noqa: F405
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration

    sentry_sdk.init(
        dsn=env("SENTRY_DSN"),  # noqa: F405
        integrations=[DjangoIntegration()],
        environment="staging",
        traces_sample_rate=0.1,
        send_default_pii=False,
    )
