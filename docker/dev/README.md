# Development Docker Configuration

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

Docker setup for local development environment.

## Table of Contents

- [Development Docker Configuration](#development-docker-configuration)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Services](#services)
    - [Django Development Server](#django-development-server)
    - [PostgreSQL Database](#postgresql-database)
    - [Redis Cache](#redis-cache)
    - [Mailpit](#mailpit)
  - [Quick Start](#quick-start)
  - [Access URLs](#access-urls)

---

## Overview

Development Docker configuration with hot-reloading, debug tools, and convenient features for local development.

---

## Services

### Django Development Server

- Port: 8000
- Auto-reload on code changes
- Debug toolbar included
- Interactive debugger

### PostgreSQL Database

- Port: 5432
- Database: backend_template_dev
- User: postgres
- Password: postgres

### Redis Cache

- Port: 6379
- Volatile memory (clears on restart)
- Used for caching and session storage

### Mailpit

- Port: 8025
- Email simulation for development
- Web UI for viewing sent emails

---

## Quick Start

```bash
# Start environment
./scripts/env/dev.sh start

# Run migrations
./scripts/env/dev.sh migrate

# Create superuser
./scripts/env/dev.sh createsuperuser

# View logs
./scripts/env/dev.sh logs

# Stop environment
./scripts/env/dev.sh stop
```

---

## Access URLs

| Service  | URL                             |
| -------- | ------------------------------- |
| Web App  | <http://localhost:8000>         |
| Admin    | <http://localhost:8000/admin>   |
| GraphQL  | <http://localhost:8000/graphql> |
| Mailpit  | <http://localhost:8025>         |
| Database | localhost:5432                  |
| Redis    | localhost:6379                  |

---

**Last Updated:** 2026-01-03
