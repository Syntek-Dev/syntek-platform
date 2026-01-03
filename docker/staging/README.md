# Staging Docker Configuration

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

Docker setup for staging environment (pre-production).

## Table of Contents

- [Staging Docker Configuration](#staging-docker-configuration)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Services](#services)
    - [Gunicorn Application Server](#gunicorn-application-server)
    - [PostgreSQL (External)](#postgresql-external)
    - [Redis (Managed)](#redis-managed)
    - [Nginx Reverse Proxy](#nginx-reverse-proxy)
  - [Deployment](#deployment)

---

## Overview

Staging environment configuration matching production setup for final testing before release.

---

## Services

### Gunicorn Application Server

- Production WSGI server
- Multiple worker processes
- Graceful reload

### PostgreSQL (External)

- AWS RDS or DigitalOcean managed database
- Configured via environment variables
- Automatic backups

### Redis (Managed)

- Managed cache service
- Clustering enabled
- Automatic failover

### Nginx Reverse Proxy

- SSL/TLS termination
- Load balancing
- Static file serving

---

## Deployment

```bash
# Deploy to staging
./scripts/env/staging.sh deploy

# Run migrations
./scripts/env/staging.sh migrate

# Health check
./scripts/env/staging.sh health

# View logs
./scripts/env/staging.sh logs
```

---

**Last Updated:** 2026-01-03
