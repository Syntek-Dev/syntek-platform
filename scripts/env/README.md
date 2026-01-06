# Environment Scripts

Helper scripts for running commands in environment-specific Docker containers.

## Table of Contents

- [Environment Scripts](#environment-scripts)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Available Scripts](#available-scripts)
    - [dev.sh](#devsh)
    - [test.sh](#testsh)
    - [staging.sh](#stagingsh)
    - [production.sh](#productionsh)
  - [Command Reference](#command-reference)
    - [Development](#development)
    - [Testing](#testing)
    - [Staging/Production](#stagingproduction)
  - [Related Documentation](#related-documentation)

---

## Overview

These scripts provide convenient shortcuts for running Django management commands, tests, and
other operations inside Docker containers for each environment (dev, test, staging, production).

**Key:** All commands run inside Docker, matching the production environment exactly.

---

## Available Scripts

### dev.sh

Development environment helper.

**Usage:**
```bash
./scripts/env/dev.sh [command] [options]
```

**Common Commands:**
- `start` - Start development environment
- `stop` - Stop development environment
- `migrate` - Run Django migrations
- `makemigrations` - Create Django migrations
- `createsuperuser` - Create admin user
- `shell` - Django interactive shell
- `runserver` - Run development server
- `manage` [command] - Run any Django manage.py command
- `logs` [service] - View Docker logs
- `format` - Auto-format code
- `test` - Run tests

### test.sh

Test environment helper for running tests and quality checks.

**Usage:**
```bash
./scripts/env/test.sh [command] [options]
```

**Common Commands:**
- `run` - Run all tests
- `fast` - Fast tests (no coverage)
- `coverage` - Run with coverage report
- `lint` - Run linting checks
- `format` - Auto-format code
- `typecheck` - Type checking
- `unit` - Unit tests only
- `integration` - Integration tests only
- `app` [name] - Tests for specific app

### staging.sh

Staging environment helper.

**Usage:**
```bash
./scripts/env/staging.sh [command] [options]
```

**Common Commands:**
- `deploy` - Deploy to staging
- `migrate` - Run migrations
- `backup` - Create database backup
- `health` - Health checks
- `test` - Smoke tests
- `logs` - View logs

### production.sh

Production environment helper (use with caution).

**Usage:**
```bash
./scripts/env/production.sh [command] [options]
```

**Common Commands:**
- `deploy` - Deploy to production (requires confirmation)
- `backup` - Create backup
- `health` - Health checks
- `scale` [count] - Scale web services
- `maintenance-on` - Enable maintenance mode
- `maintenance-off` - Disable maintenance mode

---

## Command Reference

### Development

| Task | Command |
|------|---------|
| Start dev environment | `./scripts/env/dev.sh start` |
| Stop dev environment | `./scripts/env/dev.sh stop` |
| Run migrations | `./scripts/env/dev.sh migrate` |
| Create migrations | `./scripts/env/dev.sh makemigrations` |
| Create superuser | `./scripts/env/dev.sh createsuperuser` |
| Django shell | `./scripts/env/dev.sh shell` |
| Format code | `./scripts/env/dev.sh format` |
| View logs | `./scripts/env/dev.sh logs` |

### Testing

| Task | Command |
|------|---------|
| Run all tests | `./scripts/env/test.sh run` |
| Run with coverage | `./scripts/env/test.sh coverage` |
| Run linting | `./scripts/env/test.sh lint` |
| Type checking | `./scripts/env/test.sh typecheck` |
| Fast tests | `./scripts/env/test.sh fast` |

### Staging/Production

| Task | Command |
|------|---------|
| Deploy | `./scripts/env/staging.sh deploy` |
| Database backup | `./scripts/env/staging.sh backup` |
| Health check | `./scripts/env/staging.sh health` |
| View logs | `./scripts/env/staging.sh logs` |

---

## Related Documentation

- [Scripts Overview](../README.md) - Scripts directory overview
- [Setup Guide](../../docs/DEVELOPER-SETUP.md) - Development setup
- [CLAUDE.md](../../.claude/CLAUDE.md) - Project configuration

---

**Last Updated:** 2026-01-03
