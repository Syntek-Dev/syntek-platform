# Django Project Configuration

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

Django project-wide configuration, settings, middleware, and validators.

## Table of Contents

- [Django Project Configuration](#django-project-configuration)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [Core Files](#core-files)
    - [asgi.py](#asgipy)
    - [wsgi.py](#wsgipy)
    - [urls.py](#urlspy)
  - [Configuration Management](#configuration-management)
    - [Settings Hierarchy](#settings-hierarchy)
    - [Selecting Settings Module](#selecting-settings-module)
    - [Settings by Environment](#settings-by-environment)
    - [Adding Environment Variables](#adding-environment-variables)
    - [Environment File Structure](#environment-file-structure)
  - [Subdirectories](#subdirectories)
    - [settings/](#settings)
    - [middleware/](#middleware)
    - [validators/](#validators)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains the Django project configuration including settings for different
environments, middleware implementations, validators, and URL routing.

**Key Concept:** Environment-specific settings extend the base configuration to handle dev, test,
staging, and production requirements.

---

## Directory Structure

```
config/
├── README.md               # This file
├── __init__.py
├── asgi.py                 # ASGI configuration for async workers
├── wsgi.py                 # WSGI configuration for production servers
├── urls.py                 # Root URL router
├── settings/               # Environment-specific settings
│   ├── __init__.py
│   ├── base.py            # Shared settings across all environments
│   ├── dev.py             # Development environment settings
│   ├── test.py            # Test environment settings
│   ├── staging.py         # Staging environment settings
│   └── production.py      # Production environment settings
├── middleware/             # Custom middleware classes
│   ├── __init__.py
│   ├── audit.py           # Audit logging middleware
│   ├── security.py        # Security headers middleware
│   └── ratelimit.py       # Rate limiting middleware
├── validators/             # Custom form and field validators
│   ├── __init__.py
│   └── password.py        # Password validation rules
└── clickup-config.json    # ClickUp integration configuration
```

---

## Core Files

### asgi.py

ASGI application configuration for async Python web servers (Daphne, Hypercorn).

**Usage:**

```bash
# Run with async server
daphne -b 0.0.0.0 -p 8000 config.asgi:application
```

### wsgi.py

WSGI application configuration for traditional web servers (Gunicorn, uWSGI).

**Usage:**

```bash
# Run with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

**Production:** This is the entry point for production deployments.

### urls.py

Root URL router for the entire Django project. Includes:

- Admin interface
- GraphQL API
- Health check endpoints
- Debug toolbar (dev only)

**Usage:**

```python
# Add app URLs
urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql/", GraphQLView.as_view(schema=schema)),
]
```

---

## Configuration Management

### Settings Hierarchy

The settings follow an inheritance pattern:

```
base.py (shared configuration)
  ↑
  ├─ dev.py (extends base)
  ├─ test.py (extends base)
  ├─ staging.py (extends base)
  └─ production.py (extends base)
```

### Selecting Settings Module

The active settings module is controlled by the `DJANGO_SETTINGS_MODULE` environment variable:

```bash
# Development
export DJANGO_SETTINGS_MODULE=config.settings.dev

# Testing
export DJANGO_SETTINGS_MODULE=config.settings.test

# Staging
export DJANGO_SETTINGS_MODULE=config.settings.staging

# Production
export DJANGO_SETTINGS_MODULE=config.settings.production
```

**Docker:** Environment scripts automatically set this variable.

```bash
./scripts/env/dev.sh migrate      # Uses config.settings.dev
./scripts/env/test.sh run         # Uses config.settings.test
./scripts/env/staging.sh deploy   # Uses config.settings.staging
```

### Settings by Environment

| Setting              | Dev       | Test    | Staging  | Production |
| -------------------- | --------- | ------- | -------- | ---------- |
| DEBUG                | True      | False   | False    | False      |
| ALLOWED_HOSTS        | \*        | \*      | [domain] | [domain]   |
| Database             | Local     | Local   | RDS/DO   | RDS/DO     |
| Email                | Mailpit   | Mailpit | SMTP     | SMTP       |
| Logging              | Console   | File    | Syslog   | Syslog     |
| CSRF_TRUSTED_ORIGINS | localhost | -       | [domain] | [domain]   |

### Adding Environment Variables

Use `environ.Env()` in settings:

```python
# In config/settings/base.py
import environ

env = environ.Env()
env.read_env(".env")

# Read variable with default
DEBUG = env("DEBUG", default=False)

# Read required variable
SECRET_KEY = env("SECRET_KEY")

# Read with type conversion
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])
DATABASES_PORT = env.int("DB_PORT", default=5432)
```

### Environment File Structure

```bash
# .env (for development)
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:pass@localhost:5432/dbname
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## Subdirectories

### settings/

For detailed information on environment-specific settings, see [settings/README.md](settings/README.md).

### middleware/

For custom middleware implementations, see [middleware/README.md](middleware/README.md).

### validators/

For custom form validators, see [validators/README.md](validators/README.md).

---

## Related Documentation

- [Settings Documentation](./settings/README.md) - Environment-specific settings
- [Middleware Documentation](./middleware/README.md) - Custom middleware
- [Validators Documentation](./validators/README.md) - Form validators
- [Setup Guide](../docs/DEVELOPER-SETUP.md) - Development setup
- [Security Documentation](../docs/SECURITY/SECURITY.md) - Security configuration
- [CLAUDE.md](../.claude/CLAUDE.md) - Project conventions

---

**Last Updated:** 2026-01-03
