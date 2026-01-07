# Scripts Directory

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

Helper scripts for CI/CD setup and local development.

## Table of Contents

- [Scripts Directory](#scripts-directory)
  - [Table of Contents](#table-of-contents)
  - [Available Scripts](#available-scripts)
    - [`setup-ci.sh`](#setup-cish)
    - [`run-ci-locally.sh`](#run-ci-locallysh)
  - [Docker-First Approach](#docker-first-approach)
  - [Git Hooks Integration](#git-hooks-integration)
  - [Troubleshooting](#troubleshooting)
    - [Docker not running](#docker-not-running)
    - [Permission denied](#permission-denied)
    - [Container build fails](#container-build-fails)
  - [Examples](#examples)
    - [Before Committing](#before-committing)
    - [Before Creating PR](#before-creating-pr)
    - [Check Migrations](#check-migrations)
    - [Security Audit](#security-audit)
  - [Additional Resources](#additional-resources)

## Available Scripts

### `setup-ci.sh`

**Purpose:** Initial CI/CD setup and validation

**What it does:**

- Checks Docker and Docker Compose availability
- Builds test container
- Installs Git hooks
- Validates GitHub Actions workflows
- Validates Docker configurations
- Tests code quality tools in Docker

**Usage:**

```bash
./scripts/setup-ci.sh
```

**When to run:**

- Initial project setup
- After cloning the repository
- After updating workflow files
- To verify CI/CD configuration

### `run-ci-locally.sh`

**Purpose:** Run CI checks locally before pushing

**What it does:**

- Runs the same checks as GitHub Actions
- All checks run inside Docker containers
- Provides quick feedback before pushing

**Usage:**

```bash
# Run all checks
./scripts/run-ci-locally.sh all

# Run specific check
./scripts/run-ci-locally.sh lint
./scripts/run-ci-locally.sh test
./scripts/run-ci-locally.sh security
./scripts/run-ci-locally.sh migrate

# Auto-format code
./scripts/run-ci-locally.sh format
```

**Available checks:**

| Check      | Description                       |
| ---------- | --------------------------------- |
| `all`      | Run all checks (default)          |
| `lint`     | Black, isort, flake8, mypy        |
| `format`   | Auto-format with Black and isort  |
| `test`     | pytest with coverage              |
| `security` | Bandit and Django security checks |
| `migrate`  | Django migration validation       |

## Docker-First Approach

All scripts use Docker for consistency:

**Benefits:**

- Matches CI/CD environment exactly
- No local Python dependencies needed
- Consistent across all developer machines
- Same tools and versions as production

**Requirements:**

- Docker installed and running
- Docker Compose available

## Git Hooks Integration

After running `setup-ci.sh`, Git hooks are automatically installed:

**Pre-commit:** Runs linting and formatting checks
**Pre-push:** Runs test suite
**Commit-msg:** Validates commit message format
**Post-merge:** Notifies about dependency/migration changes

## Troubleshooting

### Docker not running

```bash
# Start Docker
# macOS: Open Docker Desktop
# Linux: sudo systemctl start docker
```

### Permission denied

```bash
chmod +x scripts/*.sh
```

### Container build fails

```bash
# Clean Docker cache
docker compose -f docker/test/docker-compose.yml down -v
docker system prune -f

# Rebuild
docker compose -f docker/test/docker-compose.yml build --no-cache
```

## Examples

### Before Committing

```bash
# Format code automatically
./scripts/run-ci-locally.sh format

# Run quick linting check
./scripts/run-ci-locally.sh lint
```

### Before Creating PR

```bash
# Run full CI suite
./scripts/run-ci-locally.sh all
```

### Check Migrations

```bash
# Validate migrations
./scripts/run-ci-locally.sh migrate
```

### Security Audit

```bash
# Run security scans
./scripts/run-ci-locally.sh security
```

## Additional Resources

- [Full CI/CD Documentation](../docs/DEVOPS/CICD-GITHUB-ACTIONS.MD)
- [Quick Reference](../docs/DEVOPS/QUICK-REFERENCE.MD)
- [Workflow README](../.github/workflows/README.md)
