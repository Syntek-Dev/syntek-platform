# Development Commands

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Overview

This document provides quick reference commands for starting, managing, and interacting with the
development environment using Docker Compose and Django management scripts.

**Key Commands:**
- Start/stop containers
- Run migrations and create superusers
- Access Django shell and logs
- Health checks and database backups

---

## Start Development Environment

```bash
docker compose -f docker/dev/docker-compose.yml up -d
```

## Stop Development Environment

```bash
docker compose -f docker/dev/docker-compose.yml down
```

## View Logs

```bash
docker compose -f docker/dev/docker-compose.yml logs -f
```

## Django Shell

```bash
docker compose -f docker/dev/docker-compose.yml exec web python manage.py shell
```

## Run Migrations

```bash
docker compose -f docker/dev/docker-compose.yml exec web python manage.py migrate
```

## Create Superuser

```bash
docker compose -f docker/dev/docker-compose.yml exec web python manage.py createsuperuser
```

## Access Points

- **Web Application:** <http://localhost:8000>
- **Admin Panel:** <http://localhost:8000/admin>
- **GraphQL Playground:** <http://localhost:8000/graphql>
- **Mailpit:** <http://localhost:8025>
