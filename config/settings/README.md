# Django Settings

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

Environment-specific Django settings for dev, test, staging, and production.

## Table of Contents

- [Django Settings](#django-settings)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Settings Files](#settings-files)
    - [base.py](#basepy)
    - [dev.py](#devpy)
    - [test.py](#testpy)
    - [staging.py](#stagingpy)
    - [production.py](#productionpy)
  - [Settings Inheritance](#settings-inheritance)
    - [How It Works](#how-it-works)
    - [Pattern](#pattern)
  - [Environment-Specific Configuration](#environment-specific-configuration)
    - [Database Configuration](#database-configuration)
    - [Email Configuration](#email-configuration)
    - [Security Headers](#security-headers)
  - [Adding New Settings](#adding-new-settings)
    - [Step 1: Add to base.py](#step-1-add-to-basepy)
    - [Step 2: Override in Environment (if needed)](#step-2-override-in-environment-if-needed)
    - [Step 3: Document in .env files](#step-3-document-in-env-files)
    - [Step 4: Update Environment Variables](#step-4-update-environment-variables)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains Django settings organized by environment. Each environment extends the base settings with environment-specific overrides.

**Pattern:** Single settings module per environment extending shared base configuration.

---

## Settings Files

### base.py

Shared settings across all environments.

**Contains:**

- Base Django configuration
- Installed apps
- Middleware
- Logging configuration
- Database connection basics
- Cache configuration
- Static/Media files
- Security defaults
- Email configuration

**Key Variables:**

```python
DEBUG = False  # Default, overridden in dev
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = []  # Overridden per environment
INSTALLED_APPS = [...]  # All apps
MIDDLEWARE = [...]  # All middleware
```

### dev.py

Development environment settings.

**Overrides:**

```python
DEBUG = True
ALLOWED_HOSTS = ["*"]
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
# or Mailpit backend
```

**Additions:**

- Django Debug Toolbar
- Enhanced logging
- Relaxed security headers

**Usage:**

```bash
./scripts/env/dev.sh start
export DJANGO_SETTINGS_MODULE=config.settings.dev
```

### test.py

Test environment settings.

**Overrides:**

```python
DEBUG = False
DATABASES["default"]["NAME"] = ":memory:"  # Or test-specific
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
```

**Features:**

- Fast SQLite or in-memory database
- Email-to-memory backend
- Simplified logging
- Reduced security checks

**Usage:**

```bash
./scripts/env/test.sh run
export DJANGO_SETTINGS_MODULE=config.settings.test
```

### staging.py

Staging environment settings.

**Overrides:**

```python
DEBUG = False
ALLOWED_HOSTS = ["staging.example.com"]
DATABASES["default"]["HOST"] = "staging-db.amazonaws.com"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
```

**Features:**

- Production-like configuration
- Real database (AWS RDS or DigitalOcean)
- SMTP email
- Full security headers
- Monitoring enabled

**Usage:**

```bash
./scripts/env/staging.sh deploy
export DJANGO_SETTINGS_MODULE=config.settings.staging
```

### production.py

Production environment settings.

**Overrides:**

```python
DEBUG = False
ALLOWED_HOSTS = ["example.com", "www.example.com"]
DATABASES["default"]["HOST"] = "prod-db.amazonaws.com"
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
```

**Features:**

- Strictest security settings
- Production database
- SMTP email with TLS
- HTTPS enforced
- Security headers
- Advanced monitoring and logging

**Usage:**

```bash
./scripts/env/production.sh deploy
export DJANGO_SETTINGS_MODULE=config.settings.production
```

---

## Settings Inheritance

### How It Works

```
base.py
  ↓
  ├─→ dev.py (extends base.py with DEBUG=True, etc.)
  ├─→ test.py (extends base.py with test database, etc.)
  ├─→ staging.py (extends base.py with staging DB, email, etc.)
  └─→ production.py (extends base.py with production DB, security, etc.)
```

### Pattern

```python
# In dev.py
from .base import *  # Import everything from base

# Override specific settings
DEBUG = True
ALLOWED_HOSTS = ["*"]

# Add environment-specific settings
INSTALLED_APPS += ["debug_toolbar"]
MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]
```

---

## Environment-Specific Configuration

### Database Configuration

**Development:**

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "backend_template_dev",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": "5432",
    }
}
```

**Production:**

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT", default=5432),
    }
}
```

### Email Configuration

**Development (Console):**

```python
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

**Production (SMTP):**

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env.int("EMAIL_PORT", default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
```

### Security Headers

**Development (Relaxed):**

```python
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = ["localhost:8000", "127.0.0.1:8000"]
```

**Production (Strict):**

```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_SECURITY_POLICY = {...}
```

---

## Adding New Settings

### Step 1: Add to base.py

Add the setting to `base.py` with sensible defaults:

```python
# In config/settings/base.py
CUSTOM_SETTING = env("CUSTOM_SETTING", default="default_value")
```

### Step 2: Override in Environment (if needed)

Override in specific environment if different:

```python
# In config/settings/production.py
from .base import *

CUSTOM_SETTING = "production_value"
```

### Step 3: Document in .env files

Add to example environment files:

```bash
# In .env.example
CUSTOM_SETTING=value
```

### Step 4: Update Environment Variables

Set in Docker environment or CI/CD:

```bash
# Docker environment variable
export CUSTOM_SETTING=value

# Or in .env file
echo "CUSTOM_SETTING=value" >> .env
```

---

## Related Documentation

- [Configuration Overview](../README.md) - Config directory overview
- [Environment Variables](../../docs/DOTFILES.md) - Environment variable documentation
- [Security Settings](../../docs/SECURITY/SECURITY.md) - Security configuration
- [Setup Guide](../../docs/DEVELOPER-SETUP.md) - Development setup

---

**Last Updated:** 2026-01-03
