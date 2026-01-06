# CI/CD PIPELINE - GITHUB ACTIONS

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

> **Platform:** GitHub Actions
> **Container Runtime:** Docker Compose
> **Last Updated:** 2026-01-03

## Table of Contents

- [CI/CD PIPELINE - GITHUB ACTIONS](#cicd-pipeline---github-actions)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Architecture](#architecture)
  - [Workflows](#workflows)
    - [1. CI Pipeline (`ci.yml`)](#1-ci-pipeline-ciyml)
      - [Lint and Format Check](#lint-and-format-check)
      - [Type Checking](#type-checking)
      - [Security Scanning](#security-scanning)
      - [Test Suite](#test-suite)
      - [Dockerfile Linting](#dockerfile-linting)
      - [Configuration Validation](#configuration-validation)
    - [2. PR Validation (`pr-validation.yml`)](#2-pr-validation-pr-validationyml)
      - [PR Title Validation](#pr-title-validation)
      - [Branch Name Validation](#branch-name-validation)
      - [PR Size Check](#pr-size-check)
      - [Migration Validation](#migration-validation)
      - [Secret Detection](#secret-detection)
      - [Dependency Review](#dependency-review)
      - [Commit Message Linting](#commit-message-linting)
    - [3. Staging Deployment (`deploy-staging.yml`)](#3-staging-deployment-deploy-stagingyml)
      - [Build and Push Docker Image](#build-and-push-docker-image)
      - [Deploy to Staging](#deploy-to-staging)
    - [4. Production Deployment (`deploy-production.yml`)](#4-production-deployment-deploy-productionyml)
      - [Pre-Deployment Checks](#pre-deployment-checks)
      - [Build and Push Production Image](#build-and-push-production-image)
      - [Security Scan](#security-scan)
      - [Manual Approval](#manual-approval)
      - [Deploy to Production](#deploy-to-production)
      - [Rollback on Failure](#rollback-on-failure)
    - [5. Dependency Review (`dependency-review.yml`)](#5-dependency-review-dependency-reviewyml)
      - [Dependency Review (PR only)](#dependency-review-pr-only)
      - [Check Outdated Dependencies (scheduled)](#check-outdated-dependencies-scheduled)
      - [License Compliance Scan](#license-compliance-scan)
      - [Docker Base Image Scan](#docker-base-image-scan)
    - [6. Security Scanning (`codeql.yml`)](#6-security-scanning-codeqlyml)
      - [CodeQL Analysis](#codeql-analysis)
      - [Semgrep Security Scan](#semgrep-security-scan)
      - [Bandit Security Analysis](#bandit-security-analysis)
      - [Secret Scanning](#secret-scanning)
      - [Django Security Checks](#django-security-checks)
  - [Git Hooks](#git-hooks)
    - [Pre-Commit Hook (`.husky/pre-commit`)](#pre-commit-hook-huskypre-commit)
    - [Pre-Push Hook (`.husky/pre-push`)](#pre-push-hook-huskypre-push)
    - [Commit Message Hook (`.husky/commit-msg`)](#commit-message-hook-huskycommit-msg)
    - [Post-Merge Hook (`.husky/post-merge`)](#post-merge-hook-huskypost-merge)
  - [Required GitHub Secrets](#required-github-secrets)
    - [Repository Secrets](#repository-secrets)
    - [GitHub Environments](#github-environments)
      - [Staging Environment](#staging-environment)
      - [Production Environment](#production-environment)
      - [Production Approval Environment](#production-approval-environment)
  - [Environment Variables](#environment-variables)
    - [Staging Environment](#staging-environment-1)
    - [Production Environment](#production-environment-1)
  - [Deployment Checklist](#deployment-checklist)
    - [Initial Setup](#initial-setup)
    - [Before Each Deployment](#before-each-deployment)
    - [After Deployment](#after-deployment)
  - [Troubleshooting](#troubleshooting)
    - [CI Failures](#ci-failures)
    - [Deployment Failures](#deployment-failures)
    - [Rollback Procedure](#rollback-procedure)
  - [Performance Optimisation](#performance-optimisation)
    - [Docker Build Caching](#docker-build-caching)
    - [Parallel Job Execution](#parallel-job-execution)
    - [Test Optimisation](#test-optimisation)
  - [Security Best Practices](#security-best-practices)
  - [Monitoring and Alerts](#monitoring-and-alerts)
    - [GitHub Actions Notifications](#github-actions-notifications)
    - [Recommended Monitoring](#recommended-monitoring)
  - [ClickUp Integration](#clickup-integration)
  - [Additional Resources](#additional-resources)
  - [Changelog](#changelog)

## Overview

This document describes the CI/CD pipeline implementation for the Django + PostgreSQL + GraphQL backend template. All CI/CD checks run inside Docker containers to ensure complete parity with the local development environment.

## Architecture

The CI/CD pipeline follows a three-tier environment strategy:

| Environment | Branch    | Deployment      | Purpose                       |
| ----------- | --------- | --------------- | ----------------------------- |
| Development | `dev`     | Manual          | Local development and testing |
| Staging     | `staging` | Auto-deploy     | Pre-production testing and QA |
| Production  | `main`    | Manual approval | Live production environment   |

## Workflows

### 1. CI Pipeline (`ci.yml`)

**Triggers:**

- Push to `main`, `staging`, `dev`, `testing` branches
- Pull requests to `main`, `staging`, `dev` branches

**Jobs:**

#### Lint and Format Check

Runs code quality checks inside Docker:

- Black formatting verification
- isort import sorting verification
- flake8 linting
- pylint static analysis

```bash
docker compose -f docker/test/docker-compose.yml run --rm web black --check .
docker compose -f docker/test/docker-compose.yml run --rm web isort --check-only .
docker compose -f docker/test/docker-compose.yml run --rm web flake8 .
```

#### Type Checking

Runs mypy type checking:

```bash
docker compose -f docker/test/docker-compose.yml run --rm web mypy .
```

#### Security Scanning

Runs Bandit security analysis:

```bash
docker compose -f docker/test/docker-compose.yml run --rm web bandit -r apps/ api/ config/
```

#### Test Suite

Runs pytest with coverage reporting:

```bash
docker compose -f docker/test/docker-compose.yml up -d db redis mailpit
docker compose -f docker/test/docker-compose.yml run --rm web pytest --cov
```

**Artifacts:**

- Coverage reports (XML and HTML)
- Bandit security reports
- Retention: 7 days

#### Dockerfile Linting

Validates all Dockerfiles using hadolint:

- `docker/dev/Dockerfile`
- `docker/test/Dockerfile`
- `docker/staging/Dockerfile`
- `docker/production/Dockerfile`

#### Configuration Validation

Validates YAML and JSON configuration files.

### 2. PR Validation (`pr-validation.yml`)

**Triggers:**

- Pull request opened, synchronised, reopened, or edited

**Jobs:**

#### PR Title Validation

Ensures PR titles follow Conventional Commits format:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions or modifications
- `build`: Build system changes
- `ci`: CI/CD changes
- `chore`: Other changes

#### Branch Name Validation

Enforces branch naming conventions:

- `us###/description` - User story branches (e.g., `us123/add-authentication`)
- `feature/description` - Feature branches
- `bugfix/description` - Bug fix branches
- `hotfix/description` - Hotfix branches
- `release/version` - Release branches
- `docs/description` - Documentation branches
- `refactor/description` - Refactoring branches
- `test/description` - Test branches

#### PR Size Check

Warns if PR exceeds 1000 changed lines (does not fail).

#### Migration Validation

Checks for:

- Missing Django migrations
- Migration file validity
- Migration conflicts

```bash
docker compose -f docker/test/docker-compose.yml run --rm web \
  python manage.py makemigrations --check --dry-run --no-input
```

#### Secret Detection

Uses TruffleHog to detect committed secrets.

#### Dependency Review

Reviews dependency changes for vulnerabilities (main branch only).

#### Commit Message Linting

Validates commit messages using commitlint.

### 3. Staging Deployment (`deploy-staging.yml`)

**Triggers:**

- Push to `staging` branch
- Manual workflow dispatch

**Environment:** `staging`

**Jobs:**

#### Build and Push Docker Image

- Builds production-ready Docker image
- Pushes to container registry
- Tags: `staging-latest`, `staging-{sha}`
- Uses layer caching for faster builds

#### Deploy to Staging

- Connects via SSH to staging server
- Creates database backup
- Pulls latest Docker image
- Runs database migrations
- Collects static files
- Restarts application containers
- Performs health checks

**Required Secrets:**

- `CONTAINER_REGISTRY` - Container registry URL
- `REGISTRY_USERNAME` - Registry username
- `REGISTRY_PASSWORD` - Registry password
- `STAGING_HOST` - Staging server hostname
- `STAGING_USER` - SSH username
- `STAGING_SSH_PRIVATE_KEY` - SSH private key
- `STAGING_URL` - Staging environment URL
- `SLACK_WEBHOOK_URL` - Slack notification webhook (optional)

**Deployment Steps:**

```bash
# On staging server
cd /opt/backend-template
docker pull [IMAGE]
docker compose -f docker/staging/docker-compose.yml down
docker compose -f docker/staging/docker-compose.yml run --rm web python manage.py migrate
docker compose -f docker/staging/docker-compose.yml run --rm web python manage.py collectstatic
docker compose -f docker/staging/docker-compose.yml up -d
```

### 4. Production Deployment (`deploy-production.yml`)

**Triggers:**

- Push to `main` branch
- Manual workflow dispatch

**Environment:** `production` (requires manual approval)

**Jobs:**

#### Pre-Deployment Checks

Runs critical tests before deployment (can be skipped with `skip-tests` input).

#### Build and Push Production Image

- Builds production Docker image
- Extracts version from git tags
- Pushes to container registry
- Tags: `production-latest`, `prod-{sha}`, semantic version
- Generates SBOM (Software Bill of Materials)

#### Security Scan

- Scans production image with Trivy
- Uploads results to GitHub Security
- Fails on critical vulnerabilities

#### Manual Approval

Requires manual approval via GitHub Environments before deploying to production.

**Timeout:** 24 hours for approval

#### Deploy to Production

- Creates automatic database backup
- Performs rolling deployment (zero-downtime)
- Scales up new containers before removing old ones
- Runs health checks
- Sends Slack notifications

**Production Deployment Steps:**

```bash
# On production server
cd /opt/backend-template

# Backup database
docker compose -f docker/production/docker-compose.yml exec -T db \
  pg_dump -U backend_template backend_template > backup.sql

# Rolling update
docker compose -f docker/production/docker-compose.yml up -d --scale web=2
sleep 30
docker compose -f docker/production/docker-compose.yml up -d --scale web=1 --remove-orphans
```

#### Rollback on Failure

Automatic rollback trigger if deployment fails.

### 5. Dependency Review (`dependency-review.yml`)

**Triggers:**

- Pull requests to `main` or `staging`
- Weekly schedule (Monday 9:00 AM UTC)
- Manual workflow dispatch

**Jobs:**

#### Dependency Review (PR only)

Reviews dependency changes for:

- Security vulnerabilities
- License compliance
- Severity thresholds

**Allowed Licenses:**

- MIT
- Apache-2.0
- BSD-2-Clause, BSD-3-Clause
- ISC
- PostgreSQL
- Python-2.0

**Denied Licenses:**

- GPL-3.0
- AGPL-3.0

#### Check Outdated Dependencies (scheduled)

- Audits dependencies for vulnerabilities using `pip-audit`
- Checks for outdated packages
- Creates GitHub issues for review

#### License Compliance Scan

- Generates license reports using `pip-licenses`
- Checks for incompatible licenses
- Uploads license reports as artifacts

#### Docker Base Image Scan

Scans `python:3.14-slim` base image for vulnerabilities using Trivy.

### 6. Security Scanning (`codeql.yml`)

**Triggers:**

- Push to `main`, `staging`, `dev` branches
- Pull requests to `main`, `staging`
- Weekly schedule (Monday 3:00 AM UTC)
- Manual workflow dispatch

**Jobs:**

#### CodeQL Analysis

- Static code analysis for Python
- Uses `security-extended` and `security-and-quality` queries
- Uploads results to GitHub Security tab

#### Semgrep Security Scan

- Runs Semgrep security rules
- Rule sets: `security-audit`, `django`, `python`, `docker`
- Generates SARIF output

#### Bandit Security Analysis

Runs Bandit inside Docker container for Python security issues.

#### Secret Scanning

Uses TruffleHog to detect committed secrets.

#### Django Security Checks

Runs Django's built-in security checks:

```bash
python manage.py check --deploy --fail-level WARNING
```

## Git Hooks

### Pre-Commit Hook (`.husky/pre-commit`)

Runs before each commit:

- Black formatting check
- isort import sorting check
- flake8 linting

**Docker-based execution:**

```bash
docker compose -f docker/test/docker-compose.yml run --rm web black --check .
docker compose -f docker/test/docker-compose.yml run --rm web isort --check-only .
docker compose -f docker/test/docker-compose.yml run --rm web flake8 .
```

**Fallback:** If Docker is not running, uses local `pre-commit` hooks.

### Pre-Push Hook (`.husky/pre-push`)

Runs before each push:

- Full test suite execution
- Database migrations check

**Docker-based execution:**

```bash
docker compose -f docker/test/docker-compose.yml up -d db redis mailpit
docker compose -f docker/test/docker-compose.yml run --rm web pytest -x --maxfail=3
docker compose -f docker/test/docker-compose.yml down -v
```

### Commit Message Hook (`.husky/commit-msg`)

Validates commit message format:

- Enforces Conventional Commits format
- Checks message length (max 100 characters for subject)

**Valid commit message format:**

```
type(scope?): subject

body (optional)

footer (optional)
```

### Post-Merge Hook (`.husky/post-merge`)

Runs after `git merge` or `git pull`:

- Detects changes to requirements files
- Detects changes to migration files
- Provides helpful reminders to rebuild containers or run migrations

## Required GitHub Secrets

### Repository Secrets

| Secret Name                    | Description                      | Used In           |
| ------------------------------ | -------------------------------- | ----------------- |
| `CONTAINER_REGISTRY`           | Container registry URL           | Deploy workflows  |
| `REGISTRY_USERNAME`            | Container registry username      | Deploy workflows  |
| `REGISTRY_PASSWORD`            | Container registry password      | Deploy workflows  |
| `STAGING_HOST`                 | Staging server hostname          | Staging deploy    |
| `STAGING_USER`                 | Staging SSH username             | Staging deploy    |
| `STAGING_SSH_PRIVATE_KEY`      | Staging SSH private key          | Staging deploy    |
| `STAGING_URL`                  | Staging environment URL          | Staging deploy    |
| `PRODUCTION_HOST`              | Production server hostname       | Production deploy |
| `PRODUCTION_USER`              | Production SSH username          | Production deploy |
| `PRODUCTION_SSH_PRIVATE_KEY`   | Production SSH private key       | Production deploy |
| `PRODUCTION_URL`               | Production environment URL       | Production deploy |
| `SLACK_WEBHOOK_URL` (optional) | Slack webhook for notifications  | Deploy workflows  |
| `CLICKUP_API_KEY` (optional)   | ClickUp API key for project sync | ClickUp sync      |

### GitHub Environments

#### Staging Environment

- Auto-deployment enabled
- No manual approval required
- Environment URL: Set to staging URL

#### Production Environment

- Manual approval required
- Reviewers: Add production deployment approvers
- Environment URL: Set to production URL

#### Production Approval Environment

- Dedicated approval gate before production deployment
- Timeout: 24 hours

## Environment Variables

### Staging Environment

```bash
DJANGO_SETTINGS_MODULE=config.settings.staging
DATABASE_URL=postgres://user:pass@host:5432/db_staging
REDIS_URL=redis://host:6379/0
SECRET_KEY=[generate secure key]
ALLOWED_HOSTS=staging.example.com
DEBUG=False
```

### Production Environment

```bash
DJANGO_SETTINGS_MODULE=config.settings.production
DATABASE_URL=postgres://user:pass@host:5432/db_production
REDIS_URL=redis://host:6379/0
SECRET_KEY=[generate secure key]
ALLOWED_HOSTS=example.com
DEBUG=False
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

## Deployment Checklist

### Initial Setup

- [ ] Set up GitHub Environments (staging, production, production-approval)
- [ ] Configure repository secrets
- [ ] Set up container registry (Docker Hub, ECR, GHCR)
- [ ] Configure SSH access to servers
- [ ] Set up database backups
- [ ] Configure Slack webhooks (optional)
- [ ] Install husky hooks: `npx husky install`
- [ ] Install pre-commit: `pip install pre-commit && pre-commit install`

### Before Each Deployment

- [ ] All CI checks pass
- [ ] PR approved and merged
- [ ] Database migrations reviewed
- [ ] Breaking changes documented
- [ ] Rollback plan prepared

### After Deployment

- [ ] Health checks pass
- [ ] Smoke tests executed
- [ ] Monitoring dashboards reviewed
- [ ] Error tracking checked (Sentry)
- [ ] Database backup verified

## Troubleshooting

### CI Failures

**Black formatting failed:**

```bash
docker compose -f docker/test/docker-compose.yml run --rm web black .
```

**isort failed:**

```bash
docker compose -f docker/test/docker-compose.yml run --rm web isort .
```

**Tests failed:**

```bash
docker compose -f docker/test/docker-compose.yml up -d
docker compose -f docker/test/docker-compose.yml run --rm web pytest -vv
```

### Deployment Failures

**SSH connection failed:**

- Verify SSH key is correct
- Check server firewall rules
- Confirm SSH key has correct permissions (600)

**Database migration failed:**

- Review migration files
- Check database connectivity
- Verify database user permissions
- Restore from backup if needed

**Container health check failed:**

- Review application logs
- Check environment variables
- Verify database connectivity
- Check Redis connectivity

### Rollback Procedure

**Manual rollback:**

```bash
# SSH into server
ssh user@host

# Navigate to application directory
cd /opt/backend-template

# Pull previous image tag
docker pull [REGISTRY]/backend-template:[PREVIOUS_TAG]

# Update docker-compose to use previous tag
export IMAGE_TAG=[PREVIOUS_TAG]

# Restart containers
docker compose -f docker/production/docker-compose.yml up -d

# Restore database if needed
docker compose -f docker/production/docker-compose.yml exec -T db \
  psql -U backend_template backend_template < /opt/backups/backup.sql
```

## Performance Optimisation

### Docker Build Caching

Workflows use GitHub Actions cache for Docker layers:

```yaml
cache-from: type=gha
cache-to: type=gha,mode=max
```

### Parallel Job Execution

CI jobs run in parallel where possible:

- Linting and type checking run concurrently
- Security scans run independently
- Deployment jobs run sequentially for safety

### Test Optimisation

- Use `-x --maxfail=3` for fail-fast testing
- Mark slow tests with `@pytest.mark.slow`
- Use `pytest-xdist` for parallel test execution (future enhancement)

## Security Best Practices

- [ ] Secrets stored in GitHub Secrets, not code
- [ ] SSH keys have appropriate permissions (600)
- [ ] Production requires manual approval
- [ ] All Docker images use specific versions (not `latest`)
- [ ] Security scans run on every PR
- [ ] Dependency vulnerabilities reviewed weekly
- [ ] Database backups created before deployments
- [ ] SBOM generated for production images
- [ ] Container images scanned with Trivy
- [ ] CodeQL analysis runs weekly

## Monitoring and Alerts

### GitHub Actions Notifications

Configure GitHub Actions notifications in repository settings:

- Email notifications for workflow failures
- Slack integration for deployment status
- Status checks required for PR merges

### Recommended Monitoring

- **Application Performance Monitoring (APM):** New Relic, DataDog, or similar
- **Error Tracking:** Sentry
- **Log Aggregation:** ELK Stack, Loki, or CloudWatch
- **Uptime Monitoring:** UptimeRobot, Pingdom, or StatusCake
- **Database Monitoring:** pgAdmin, CloudWatch RDS metrics

## ClickUp Integration

The `clickup-sync.yml` workflow syncs GitHub activity with ClickUp tasks:

**Branch naming pattern:** `us###/description`

**Status mapping:**

- PR opened → `in review`
- Merged to dev → `in progress`
- Merged to staging → `accepted`
- Merged to main → `Closed`

**Configuration:**

- Task mapping file: `config/clickup-story-mapping.json`
- Required secret: `CLICKUP_API_KEY`

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

## Changelog

| Date       | Change                                    | Author        |
| ---------- | ----------------------------------------- | ------------- |
| 2026-01-03 | Initial CI/CD pipeline implementation     | Claude Opus 4 |
| 2026-01-03 | Added Docker-based testing and deployment | Claude Opus 4 |
| 2026-01-03 | Configured security scanning workflows    | Claude Opus 4 |
| 2026-01-03 | Set up Git hooks with Docker support      | Claude Opus 4 |
