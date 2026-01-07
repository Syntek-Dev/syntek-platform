# Test Docker Configuration

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

Docker setup for test environment and CI/CD pipeline.

## Table of Contents

- [Test Docker Configuration](#test-docker-configuration)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Services](#services)
    - [Test Runner](#test-runner)
    - [PostgreSQL Test Database](#postgresql-test-database)
    - [Redis Cache](#redis-cache)
    - [Mailpit](#mailpit)
  - [Running Tests](#running-tests)

---

## Overview

Test environment Docker configuration for automated testing, code quality checks, and continuous integration.

---

## Services

### Test Runner

- Pytest test framework
- Code coverage reporting
- Parallel test execution

### PostgreSQL Test Database

- Fresh database per test run
- Automatic cleanup
- Isolated from other environments

### Redis Cache

- Test-specific instance
- Used for testing cache functionality

### Mailpit

- Email testing
- Verification of email sends

---

## Running Tests

```bash
# Run all tests
./scripts/env/test.sh run

# Run with coverage
./scripts/env/test.sh coverage

# Run linting
./scripts/env/test.sh lint

# Fast tests (no coverage)
./scripts/env/test.sh fast
```

---

**Last Updated:** 2026-01-03
