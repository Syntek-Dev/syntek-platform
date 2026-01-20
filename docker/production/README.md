# Production Docker Configuration

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

Docker setup for production deployment environment.

## Table of Contents

- [Production Docker Configuration](#production-docker-configuration)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Services](#services)
    - [Gunicorn Application Server](#gunicorn-application-server)
    - [PostgreSQL (Managed)](#postgresql-managed)
    - [Redis Cluster (Managed)](#redis-cluster-managed)
    - [Nginx Load Balancer](#nginx-load-balancer)
    - [Monitoring](#monitoring)
  - [Deployment](#deployment)
  - [Security](#security)

---

## Overview

Production environment configuration with maximum reliability, security, and performance.

---

## Directory Tree

```
docker/production/
├── README.md                  # This file - Production Docker setup
└── docker-compose.yml         # Docker Compose configuration for production
```

---

## Services

### Gunicorn Application Server

- Multiple worker processes (auto-scaled)
- Connection pooling
- Graceful reload without downtime

### PostgreSQL (Managed)

- AWS RDS or DigitalOcean managed database
- Automated daily backups
- Point-in-time recovery
- Read replicas for scaling

### Redis Cluster (Managed)

- High availability cluster
- Automatic failover
- Multi-AZ deployment
- Automatic backups

### Nginx Load Balancer

- TLS/SSL termination
- Request routing
- Static file caching
- Compression

### Monitoring

- Health checks
- Log aggregation
- Performance monitoring
- Alert notifications

---

## Deployment

**WARNING:** Production deployments require careful review and approval.

```bash
# Deploy to production (requires confirmation)
./scripts/env/production.sh deploy

# Create backup before deployment
./scripts/env/production.sh backup

# Health checks
./scripts/env/production.sh health

# Maintenance mode
./scripts/env/production.sh maintenance-on
./scripts/env/production.sh maintenance-off
```

---

## Security

1. **HTTPS Only:** All traffic encrypted with TLS 1.2+
2. **Database Encryption:** Encrypted at rest and in transit
3. **Secrets Management:** Environment variables securely stored
4. **Rate Limiting:** Protect against abuse
5. **WAF Rules:** Web application firewall configured
6. **Audit Logging:** All access logged and monitored

---

**Last Updated:** 2026-01-03
