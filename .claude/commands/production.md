# Production Commands

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Overview

This document provides critical commands for production deployments, migrations, monitoring, and
rollback procedures. All production operations require confirmation and extreme caution.

**Key Commands:**
- Deploy to production (requires confirmation)
- Run database migrations with backups
- Monitor health and logs
- Manage maintenance mode
- Execute rollbacks

---

## Table of Contents

- [Production Commands](#production-commands)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Deploy to Production](#deploy-to-production)
  - [Run Migrations on Production](#run-migrations-on-production)
  - [View Production Logs](#view-production-logs)
  - [Production Environment Variables](#production-environment-variables)
  - [Health Check](#health-check)
  - [Rollback](#rollback)

---

## Deploy to Production

```bash
# Build and push production image
docker build -f docker/production/Dockerfile -t backend-template:latest .
docker push registry.example.com/backend-template:latest

# Deploy (update as per your CI/CD)
./scripts/deploy-production.sh
```

## Run Migrations on Production

```bash
# Use CI/CD pipeline for production migrations
# Manual migrations should be avoided in production
docker compose -f docker/production/docker-compose.yml exec web python manage.py migrate --plan
docker compose -f docker/production/docker-compose.yml exec web python manage.py migrate
```

## View Production Logs

```bash
# Use your logging service (CloudWatch, Datadog, etc.)
# Or access container logs
docker compose -f docker/production/docker-compose.yml logs -f web
```

## Production Environment Variables

Required in production:

- `DJANGO_SETTINGS_MODULE=config.settings.production`
- `DATABASE_URL` - PostgreSQL connection string (AWS RDS or DO)
- `REDIS_URL` - Redis/Valkey connection string
- `SECRET_KEY` - Strong secret key
- `ALLOWED_HOSTS` - Production domain(s)
- `EMAIL_*` - Production SMTP configuration
- `SENTRY_DSN` - Error tracking
- `AWS_*` or `DO_*` - Cloud provider credentials

## Health Check

```bash
curl -I https://example.com/health/
```

## Rollback

```bash
# Deploy previous image version
docker pull registry.example.com/backend-template:previous-tag
./scripts/deploy-production.sh previous-tag
```
