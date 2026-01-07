# Docker Configuration

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

Docker Compose configurations for each environment (dev, test, staging, production).

## Table of Contents

- [Docker Configuration](#docker-configuration)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [Environment-Specific Setup](#environment-specific-setup)
    - [Development (dev/)](#development-dev)
    - [Test (test/)](#test-test)
    - [Staging (staging/)](#staging-staging)
    - [Production (production/)](#production-production)
  - [Common Commands](#common-commands)
    - [Development](#development)
    - [Testing](#testing)
    - [Manual Docker Commands](#manual-docker-commands)
  - [Troubleshooting](#troubleshooting)
    - [Container won't start](#container-wont-start)
    - [Port already in use](#port-already-in-use)
    - [Database connection error](#database-connection-error)
    - [Out of disk space](#out-of-disk-space)
  - [Related Documentation](#related-documentation)

---

## Overview

Docker configurations for managing containerized development, testing, staging, and production
environments. Each environment has isolated containers to prevent interference.

**Principle:** Match production environment as closely as possible in dev and staging.

---

## Directory Structure

```
docker/
├── README.md
├── dev/                    # Development environment
│   ├── Dockerfile
│   └── docker-compose.yml
├── test/                   # Test environment
│   ├── Dockerfile
│   └── docker-compose.yml
├── staging/                # Staging environment
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── entrypoint.sh
└── production/             # Production environment
    ├── Dockerfile
    ├── docker-compose.yml
    └── entrypoint.sh
```

---

## Environment-Specific Setup

### Development (dev/)

**Purpose:** Local development with hot reloading, debug tools, and convenience features.

**Services:**

- Django development server
- PostgreSQL database
- Redis cache
- Mailpit (email simulation)

**Features:**

- Volume mounts for code changes
- Debug mode enabled
- Fast reload on file changes
- Logs to console

**Start:**

```bash
./scripts/env/dev.sh start
```

**Access:**

- Web: <http://localhost:8000>
- Admin: <http://localhost:8000/admin>
- Mailpit: <http://localhost:8025>

### Test (test/)

**Purpose:** CI/CD testing with consistent, reproducible environment.

**Services:**

- Django test runner
- PostgreSQL (test database)
- Redis cache
- Mailpit

**Features:**

- Fast, isolated test runs
- Clean database per run
- Coverage reporting
- Parallel test execution

**Start:**

```bash
./scripts/env/test.sh run
```

### Staging (staging/)

**Purpose:** Pre-production testing with production-like configuration.

**Services:**

- Gunicorn application server
- PostgreSQL (external RDS/DO)
- Redis (managed)
- Nginx reverse proxy

**Features:**

- Production-like security
- Database migrations
- Static file serving
- Health checks

**Deploy:**

```bash
./scripts/env/staging.sh deploy
```

### Production (production/)

**Purpose:** Live production deployment with maximum security and reliability.

**Services:**

- Gunicorn (multiple workers)
- PostgreSQL (managed RDS/DO)
- Redis (managed, clustered)
- Nginx load balancer

**Features:**

- HTTPS/SSL enforcement
- Health monitoring
- Automatic restarts
- Log aggregation
- Security hardening

**Deploy:**

```bash
./scripts/env/production.sh deploy
```

---

## Common Commands

### Development

```bash
# Start environment
./scripts/env/dev.sh start

# Run migrations
./scripts/env/dev.sh migrate

# Create superuser
./scripts/env/dev.sh createsuperuser

# Access shell
./scripts/env/dev.sh shell

# View logs
./scripts/env/dev.sh logs

# Stop environment
./scripts/env/dev.sh stop
```

### Testing

```bash
# Run all tests
./scripts/env/test.sh run

# Run with coverage
./scripts/env/test.sh coverage

# Run linting
./scripts/env/test.sh lint

# Type checking
./scripts/env/test.sh typecheck
```

### Manual Docker Commands

```bash
# Build image
docker compose -f docker/dev/docker-compose.yml build

# Start services
docker compose -f docker/dev/docker-compose.yml up -d

# Stop services
docker compose -f docker/dev/docker-compose.yml down

# View logs
docker compose -f docker/dev/docker-compose.yml logs -f

# Run command in container
docker compose -f docker/dev/docker-compose.yml exec web python manage.py migrate

# Remove volumes (WARNING: deletes data)
docker compose -f docker/dev/docker-compose.yml down -v
```

---

## Troubleshooting

### Container won't start

```bash
# Check logs
docker compose -f docker/dev/docker-compose.yml logs web

# Rebuild without cache
docker compose -f docker/dev/docker-compose.yml build --no-cache

# Remove and restart
docker compose -f docker/dev/docker-compose.yml down -v
docker compose -f docker/dev/docker-compose.yml up -d
```

### Port already in use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
# Change "8000:8000" to "8001:8000"
```

### Database connection error

```bash
# Check database is running
docker compose -f docker/dev/docker-compose.yml ps

# Check database logs
docker compose -f docker/dev/docker-compose.yml logs db

# Reset database
docker compose -f docker/dev/docker-compose.yml down -v
docker compose -f docker/dev/docker-compose.yml up -d
```

### Out of disk space

```bash
# Clean up Docker
docker system prune -a

# Remove volumes (WARNING: deletes data)
docker volume prune

# Check disk usage
docker system df
```

---

## Related Documentation

- [Development Setup](../docs/DEVELOPER-SETUP.md) - Complete setup guide
- [Scripts](../scripts/README.md) - Helper scripts documentation
- [DEVOPS CI/CD](../docs/DEVOPS/CICD-GITHUB-ACTIONS.MD) - CI/CD documentation

---

**Last Updated:** 2026-01-03
