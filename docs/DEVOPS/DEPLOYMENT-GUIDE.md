# Deployment Guide

**Last Updated**: 17/01/2026
**Version**: 1.0.0
**Audience**: DevOps Engineers, System Administrators

---

## Table of Contents

- [Deployment Guide](#deployment-guide)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Prerequisites](#prerequisites)
  - [Environment Configuration](#environment-configuration)
    - [Required Environment Variables](#required-environment-variables)
    - [Security Keys](#security-keys)
  - [Redis Configuration](#redis-configuration)
    - [Development Setup](#development-setup)
    - [Production Setup](#production-setup)
    - [Redis Configuration Options](#redis-configuration-options)
    - [Health Checks](#health-checks)
  - [Celery Configuration](#celery-configuration)
    - [Worker Setup](#worker-setup)
    - [Beat Scheduler](#beat-scheduler)
    - [Monitoring Celery](#monitoring-celery)
    - [Production Considerations](#production-considerations)
  - [Sentry Configuration](#sentry-configuration)
    - [Initial Setup](#initial-setup)
    - [Django Integration](#django-integration)
    - [Environment-Specific Configuration](#environment-specific-configuration)
    - [Custom Error Handling](#custom-error-handling)
    - [Performance Monitoring](#performance-monitoring)
  - [Docker Deployment](#docker-deployment)
    - [Development](#development)
    - [Production](#production)
  - [Database Setup](#database-setup)
    - [PostgreSQL Configuration](#postgresql-configuration)
    - [Running Migrations](#running-migrations)
    - [Database Backups](#database-backups)
  - [Email Configuration](#email-configuration)
  - [Health Checks](#health-checks-1)
  - [Monitoring and Alerting](#monitoring-and-alerting)
  - [Deployment Checklist](#deployment-checklist)
  - [Rollback Procedures](#rollback-procedures)
  - [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers the deployment of the authentication system including all required services:

- **Django Application** - Core authentication service
- **PostgreSQL** - Primary database
- **Redis** - Caching, rate limiting, and Celery broker
- **Celery** - Async task processing (emails)
- **Sentry** - Error tracking and performance monitoring

---

## Prerequisites

- Docker and Docker Compose
- Python 3.12+
- PostgreSQL 15+
- Redis 7+
- Domain with SSL certificate (production)
- Sentry account (production)
- SMTP server or email service provider

---

## Environment Configuration

### Required Environment Variables

Create environment files based on the examples provided:

```bash
# Copy the appropriate example file
cp .env.dev.example .env.dev
cp .env.staging.example .env.staging
cp .env.production.example .env.production
```

### Security Keys

Generate secure keys for production:

```bash
# Generate Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate token signing key (32 bytes, base64)
python -c "import secrets, base64; print(base64.urlsafe_b64encode(secrets.token_bytes(32)).decode())"

# Generate Fernet key for encryption
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

**Required keys for authentication:**

```bash
# .env.production
SECRET_KEY=your-django-secret-key
TOKEN_SIGNING_KEY=your-token-signing-key
TOTP_ENCRYPTION_KEY=your-fernet-key
IP_ENCRYPTION_KEY=your-fernet-key
```

---

## Redis Configuration

### Development Setup

Redis is included in the development Docker Compose file:

```bash
# Start all services including Redis
./scripts/env/dev.sh start

# Redis will be available at redis://localhost:6379
```

### Production Setup

**Option 1: Managed Redis (Recommended)**

Use AWS ElastiCache, DigitalOcean Managed Redis, or similar:

```bash
# .env.production
REDIS_URL=rediss://user:password@your-redis-host:6379/0
CELERY_BROKER_URL=rediss://user:password@your-redis-host:6379/1
CELERY_RESULT_BACKEND=rediss://user:password@your-redis-host:6379/1
```

**Option 2: Self-hosted Redis**

```yaml
# docker-compose.production.yml
services:
  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ['CMD', 'redis-cli', '-a', '${REDIS_PASSWORD}', 'ping']
      interval: 10s
      timeout: 5s
      retries: 5
```

### Redis Configuration Options

```python
# config/settings/production.py

# Cache configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "PASSWORD": env("REDIS_PASSWORD", default=None),
            "SSL": env.bool("REDIS_SSL", default=True),
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
            },
        },
        "KEY_PREFIX": "auth",
        "TIMEOUT": 300,  # 5 minutes default
    }
}

# Session storage in Redis
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"
```

### Health Checks

```bash
# Check Redis connection
./scripts/env/production.sh shell -c "
from django.core.cache import cache
cache.set('health_check', 'ok', 10)
result = cache.get('health_check')
print(f'Redis health: {result}')
"
```

---

## Celery Configuration

### Worker Setup

**Development:**

```bash
# Start Celery worker (included in docker-compose)
./scripts/env/dev.sh start

# Or manually
celery -A config worker -l INFO
```

**Production:**

```yaml
# docker-compose.production.yml
services:
  celery_worker:
    build: .
    command: celery -A config worker -l WARNING --concurrency=4
    environment:
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
      - CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}
    depends_on:
      - redis
      - web
    restart: unless-stopped
    healthcheck:
      test: ['CMD', 'celery', '-A', 'config', 'inspect', 'ping']
      interval: 30s
      timeout: 10s
      retries: 3
```

### Beat Scheduler

For scheduled tasks (e.g., token cleanup):

```yaml
# docker-compose.production.yml
services:
  celery_beat:
    build: .
    command: celery -A config beat -l WARNING --scheduler django_celery_beat.schedulers:DatabaseScheduler
    environment:
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
    depends_on:
      - redis
      - web
    restart: unless-stopped
```

### Monitoring Celery

**Using Flower (optional):**

```yaml
services:
  flower:
    build: .
    command: celery -A config flower --port=5555
    ports:
      - '5555:5555'
    environment:
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
    depends_on:
      - redis
```

**Using Django Admin:**

Tasks and their status are visible in Django admin under "Celery Results".

### Production Considerations

```python
# config/settings/production.py

# Celery Configuration
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")

# Serialization
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

# Timezone
CELERY_TIMEZONE = "Europe/London"
CELERY_ENABLE_UTC = True

# Task execution
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60  # 30 minutes
CELERY_TASK_SOFT_TIME_LIMIT = 25 * 60  # 25 minutes
CELERY_RESULT_EXPIRES = 60 * 60 * 24  # 24 hours

# Worker configuration
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_WORKER_CONCURRENCY = env.int("CELERY_WORKER_CONCURRENCY", default=4)
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1000

# Retry configuration
CELERY_TASK_ACKS_LATE = True
CELERY_TASK_REJECT_ON_WORKER_LOST = True

# Email task specific
CELERY_TASK_ROUTES = {
    "apps.core.tasks.email_tasks.*": {"queue": "emails"},
}
```

**Running multiple queues:**

```bash
# Start worker for email queue with higher priority
celery -A config worker -Q emails -l WARNING --concurrency=2

# Start general worker
celery -A config worker -Q default -l WARNING --concurrency=4
```

---

## Sentry Configuration

### Initial Setup

1. Create a Sentry account at https://sentry.io
2. Create a new Django project
3. Copy the DSN from project settings

### Django Integration

```bash
# Install Sentry SDK (already in requirements)
pip install sentry-sdk[django]
```

```python
# config/settings/production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

# Only initialize in production/staging
if not DEBUG:
    sentry_sdk.init(
        dsn=env("SENTRY_DSN"),
        integrations=[
            DjangoIntegration(
                transaction_style="url",
                middleware_spans=True,
            ),
            CeleryIntegration(
                monitor_beat_tasks=True,
                propagate_traces=True,
            ),
            RedisIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
            ),
        ],

        # Environment tag
        environment=env("ENVIRONMENT", default="production"),

        # Release tracking
        release=env("VERSION", default="0.8.0"),

        # Performance monitoring
        traces_sample_rate=0.1,  # 10% of transactions
        profiles_sample_rate=0.1,  # 10% of sampled transactions

        # Error sampling
        sample_rate=1.0,  # 100% of errors

        # PII handling
        send_default_pii=False,

        # Before send hook for data scrubbing
        before_send=scrub_sensitive_data,

        # Ignore common errors
        ignore_errors=[
            KeyboardInterrupt,
            SystemExit,
        ],
    )


def scrub_sensitive_data(event, hint):
    """Remove sensitive data before sending to Sentry."""
    # Scrub password fields
    if "request" in event and "data" in event["request"]:
        data = event["request"]["data"]
        if isinstance(data, dict):
            for key in ["password", "token", "secret", "api_key"]:
                if key in data:
                    data[key] = "[REDACTED]"

    # Scrub headers
    if "request" in event and "headers" in event["request"]:
        headers = event["request"]["headers"]
        if "Authorization" in headers:
            headers["Authorization"] = "[REDACTED]"

    return event
```

### Environment-Specific Configuration

```bash
# .env.staging
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/staging-project
ENVIRONMENT=staging

# .env.production
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/production-project
ENVIRONMENT=production
```

### Custom Error Handling

```python
# apps/core/utils/sentry.py
import sentry_sdk


def capture_auth_error(error, user=None, extra=None):
    """Capture authentication-related errors with context."""
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("category", "authentication")

        if user:
            scope.set_user({
                "id": str(user.id),
                "email": user.email,
            })

        if extra:
            for key, value in extra.items():
                scope.set_extra(key, value)

        sentry_sdk.capture_exception(error)


def capture_security_event(event_type, user=None, details=None):
    """Capture security events as Sentry issues."""
    with sentry_sdk.push_scope() as scope:
        scope.set_tag("category", "security")
        scope.set_tag("event_type", event_type)
        scope.set_level("warning")

        if user:
            scope.set_user({"id": str(user.id)})

        if details:
            scope.set_context("security_event", details)

        sentry_sdk.capture_message(f"Security Event: {event_type}")
```

### Performance Monitoring

```python
# Custom transaction for auth flows
from sentry_sdk import start_transaction

def login_with_monitoring(email, password):
    with start_transaction(op="auth", name="user.login") as transaction:
        transaction.set_tag("auth_method", "password")

        # Validate credentials
        with transaction.start_child(op="validate", description="Validate credentials"):
            user = validate_credentials(email, password)

        # Create session
        with transaction.start_child(op="session", description="Create session"):
            session = create_session(user)

        return session
```

---

## Docker Deployment

### Development

```bash
# Start all services
./scripts/env/dev.sh start

# View logs
./scripts/env/dev.sh logs

# Stop services
./scripts/env/dev.sh stop
```

### Production

```bash
# Build production image
docker build -t auth-service:latest -f docker/production/Dockerfile .

# Push to registry
docker tag auth-service:latest your-registry/auth-service:latest
docker push your-registry/auth-service:latest

# Deploy with Docker Compose
docker-compose -f docker/production/docker-compose.yml up -d

# Or use provided script
./scripts/env/production.sh deploy
```

**Production docker-compose.yml:**

```yaml
version: '3.8'

services:
  web:
    image: your-registry/auth-service:latest
    environment:
      - DJANGO_SETTINGS_MODULE=config.settings.production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SENTRY_DSN=${SENTRY_DSN}
    ports:
      - '8000:8000'
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ['CMD', 'curl', '-f', 'http://localhost:8000/health/']
      interval: 30s
      timeout: 10s
      retries: 3

  celery_worker:
    image: your-registry/auth-service:latest
    command: celery -A config worker -l WARNING
    environment:
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
    depends_on:
      - redis
    restart: unless-stopped

  celery_beat:
    image: your-registry/auth-service:latest
    command: celery -A config beat -l WARNING
    environment:
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

---

## Database Setup

### PostgreSQL Configuration

```bash
# .env.production
DATABASE_URL=postgres://user:password@host:5432/dbname?sslmode=require
```

**Recommended PostgreSQL settings:**

```sql
-- Connection pooling (via PgBouncer recommended)
max_connections = 100

-- Performance
shared_buffers = 256MB
effective_cache_size = 768MB
work_mem = 16MB
maintenance_work_mem = 128MB

-- Write performance
wal_buffers = 16MB
checkpoint_completion_target = 0.9
```

### Running Migrations

```bash
# Development
./scripts/env/dev.sh migrate

# Production (with backup)
./scripts/env/production.sh backup
./scripts/env/production.sh migrate
```

### Database Backups

```bash
# Create backup
./scripts/env/production.sh backup

# Restore backup
./scripts/env/production.sh restore backup_2026-01-17.sql
```

---

## Email Configuration

**SMTP Configuration:**

```bash
# .env.production
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=true
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourplatform.com
```

**Using SendGrid:**

```python
# config/settings/production.py
EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
SENDGRID_API_KEY = env("SENDGRID_API_KEY")
```

---

## Health Checks

The application provides health check endpoints:

```bash
# Basic health check
curl http://localhost:8000/health/

# Detailed health check (includes Redis, DB)
curl http://localhost:8000/health/detailed/
```

**Response format:**

```json
{
  "status": "healthy",
  "version": "0.8.0",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "celery": "ok"
  }
}
```

---

## Monitoring and Alerting

### Recommended Alerts

| Metric             | Threshold  | Severity |
| ------------------ | ---------- | -------- |
| Error rate         | > 1%       | Critical |
| Response time P95  | > 2s       | Warning  |
| Failed login rate  | > 100/hour | Warning  |
| Account lockouts   | > 10/hour  | Warning  |
| Celery queue depth | > 1000     | Warning  |
| Redis memory usage | > 80%      | Warning  |

### Sentry Alerts

Configure alerts in Sentry dashboard for:

- New issues
- Issue frequency spikes
- Unhandled exceptions
- Performance degradation

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing (`./scripts/env/test.sh run`)
- [ ] Environment variables configured
- [ ] Database migrations tested
- [ ] Backup created
- [ ] Redis connection verified
- [ ] Celery workers healthy
- [ ] Sentry DSN configured
- [ ] SSL certificates valid
- [ ] CORS origins configured
- [ ] Rate limiting thresholds set

### Deployment

- [ ] Deploy new version
- [ ] Run migrations
- [ ] Verify health checks
- [ ] Test authentication flow
- [ ] Test email delivery
- [ ] Verify Sentry is receiving events

### Post-Deployment

- [ ] Monitor error rates in Sentry
- [ ] Check Celery task processing
- [ ] Review audit logs
- [ ] Confirm all services healthy
- [ ] Update deployment documentation

---

## Rollback Procedures

### Quick Rollback

```bash
# Rollback to previous version
docker-compose -f docker/production/docker-compose.yml down
docker tag your-registry/auth-service:previous your-registry/auth-service:latest
docker-compose -f docker/production/docker-compose.yml up -d
```

### Database Rollback

```bash
# Rollback last migration
./scripts/env/production.sh shell -c "python manage.py migrate apps.core 0008"

# Restore from backup
./scripts/env/production.sh restore backup_2026-01-17.sql
```

---

## Troubleshooting

### Common Issues

**Redis Connection Failed:**

```bash
# Check Redis is running
docker-compose ps redis

# Test connection
redis-cli -h localhost -p 6379 ping
```

**Celery Tasks Not Processing:**

```bash
# Check worker status
celery -A config inspect active

# Check queue depth
celery -A config inspect reserved
```

**Sentry Not Receiving Events:**

```bash
# Test Sentry connection
./scripts/env/production.sh shell -c "
import sentry_sdk
sentry_sdk.capture_message('Test message from deployment')
print('Check Sentry dashboard for test message')
"
```

**Email Not Sending:**

```bash
# Test email configuration
./scripts/env/production.sh shell -c "
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'noreply@example.com', ['test@example.com'])
print('Check inbox for test email')
"
```

---

**Document Version:** 1.0.0
**Last Updated:** 17/01/2026
