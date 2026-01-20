# Test Commands

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Overview

This document provides quick reference commands for running tests, linting, type checking, and
quality assurance in the test environment using Docker Compose.

**Key Commands:**

- Run test suites (all, specific files, patterns)
- Generate coverage reports
- Run linting and type checks
- Execute quality assurance checks

---

## Run All Tests

```bash
docker compose -f docker/test/docker-compose.yml run --rm web pytest
```

## Run Tests with Coverage

```bash
docker compose -f docker/test/docker-compose.yml run --rm web pytest --cov=apps --cov-report=html
```

## Run Specific Test File

```bash
docker compose -f docker/test/docker-compose.yml run --rm web pytest apps/myapp/tests/test_models.py
```

## Run Tests with Verbose Output

```bash
docker compose -f docker/test/docker-compose.yml run --rm web pytest -v
```

## Run Tests Matching Pattern

```bash
docker compose -f docker/test/docker-compose.yml run --rm web pytest -k "test_user"
```

## Run Linting

```bash
docker compose -f docker/test/docker-compose.yml run --rm web flake8 apps/
docker compose -f docker/test/docker-compose.yml run --rm web black --check apps/
```

## Run Type Checking

```bash
docker compose -f docker/test/docker-compose.yml run --rm web mypy apps/
```
