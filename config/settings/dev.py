"""Development environment Django settings for backend_template project.

This module contains settings specific to the development environment.
It extends base.py with development-specific configurations.
"""

import socket  # noqa: E402

from .base import *  # noqa: F403, F401

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
