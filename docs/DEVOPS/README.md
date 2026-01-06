# DevOps Documentation

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

Documentation for CI/CD pipelines, deployment, and infrastructure.

## Table of Contents

- [DevOps Documentation](#devops-documentation)
  - [Table of Contents](#table-of-contents)
  - [Quick Links](#quick-links)
  - [Overview](#overview)
  - [Quick Start](#quick-start)
    - [Initial Setup](#initial-setup)
    - [Local Development](#local-development)
    - [Git Workflow](#git-workflow)
  - [Architecture](#architecture)
    - [Three-Tier Environment Strategy](#three-tier-environment-strategy)
    - [CI/CD Pipeline](#cicd-pipeline)
  - [GitHub Actions Workflows](#github-actions-workflows)
  - [Git Hooks](#git-hooks)
  - [Required Configuration](#required-configuration)
    - [GitHub Secrets](#github-secrets)
    - [GitHub Environments](#github-environments)
  - [Key Features](#key-features)
    - [Docker-Based CI](#docker-based-ci)
    - [Zero-Downtime Deployments](#zero-downtime-deployments)
    - [Comprehensive Security](#comprehensive-security)
    - [Quality Gates](#quality-gates)
  - [Monitoring](#monitoring)
  - [Documentation Structure](#documentation-structure)
  - [Common Commands](#common-commands)
    - [Local Development](#local-development-1)
    - [CI/CD Operations](#cicd-operations)
    - [Debugging](#debugging)
  - [Troubleshooting](#troubleshooting)
  - [Support](#support)
  - [Additional Resources](#additional-resources)

## Quick Links

| Document                                           | Purpose                               |
| -------------------------------------------------- | ------------------------------------- |
| [CICD-GITHUB-ACTIONS.MD](./CICD-GITHUB-ACTIONS.MD) | Complete CI/CD pipeline documentation |
| [QUICK-REFERENCE.MD](./QUICK-REFERENCE.MD)         | Quick commands and troubleshooting    |

## Overview

This project uses a Docker-first approach for CI/CD:

**All CI/CD checks run inside Docker containers** to ensure:

- Complete parity with local development
- Consistent environments across dev/CI/staging/production
- No dependency on local Python installation
- Reproducible builds and tests

## Quick Start

### Initial Setup

```bash
# Run setup script
./scripts/setup-ci.sh

# This will:
# - Validate Docker configuration
# - Install Git hooks
# - Validate CI/CD workflows
# - Test code quality tools
```

### Local Development

```bash
# Run all CI checks locally
./scripts/run-ci-locally.sh all

# Auto-format code
./scripts/run-ci-locally.sh format

# Run tests
./scripts/run-ci-locally.sh test
```

### Git Workflow

```bash
# Create feature branch
git checkout -b us123/add-feature

# Make changes
# Hooks automatically run on commit and push

# Create PR to staging
gh pr create --base staging --title "feat: Add feature"

# After approval, merge to staging (auto-deploys)

# Create PR to main for production
gh pr create --base main --title "feat: Add feature"

# After approval and manual deployment approval, merge to main
```

## Architecture

### Three-Tier Environment Strategy

```
Development (dev) → Staging (staging) → Production (main)
     ↓                    ↓                    ↓
Local testing      Auto-deployment    Manual approval
```

### CI/CD Pipeline

```
Push/PR
  ↓
Lint & Format (Black, isort, flake8)
  ↓
Type Check (mypy)
  ↓
Security Scan (Bandit, CodeQL, Semgrep)
  ↓
Tests (pytest with coverage)
  ↓
Dockerfile Validation (hadolint)
  ↓
Migration Check
  ↓
PR Validation
  ↓
Deploy to Staging (auto) or Production (manual)
```

## GitHub Actions Workflows

| Workflow          | Trigger           | Purpose                           |
| ----------------- | ----------------- | --------------------------------- |
| CI Pipeline       | Push/PR           | Linting, testing, security        |
| PR Validation     | PR events         | Title, branch, commits validation |
| Deploy Staging    | Push to `staging` | Auto-deploy to staging            |
| Deploy Production | Push to `main`    | Manual approval, deploy to prod   |
| Dependency Review | PR/weekly         | Vulnerability scanning            |
| CodeQL            | Push/PR/weekly    | Security analysis                 |

## Git Hooks

All hooks run checks inside Docker containers:

**Pre-commit:**

- Black formatting
- isort import sorting
- flake8 linting

**Pre-push:**

- Full test suite

**Commit-msg:**

- Conventional Commits validation

**Post-merge:**

- Dependency change notifications

## Required Configuration

### GitHub Secrets

**Deployment:**

- Container registry credentials
- SSH keys for staging/production
- Environment URLs

**Optional:**

- Slack webhook
- ClickUp API key

### GitHub Environments

**staging:**

- Auto-deployment enabled
- No approval required

**production:**

- Manual approval required
- Protected environment

**production-approval:**

- Approval gate before production

## Key Features

### Docker-Based CI

All checks run in Docker:

```bash
docker compose -f docker/test/docker-compose.yml run --rm web pytest
```

No local Python installation needed.

### Zero-Downtime Deployments

Production uses rolling deployments:

- Scale up new containers
- Health check
- Remove old containers
- Automatic rollback on failure

### Comprehensive Security

- CodeQL static analysis
- Semgrep security rules
- Bandit Python security
- TruffleHog secret detection
- Trivy container scanning
- Django security checks
- Weekly dependency audits

### Quality Gates

PRs must pass:

- All CI checks
- Security scans
- Migration validation
- Commit message format
- Branch naming convention

## Monitoring

Recommended tools:

- **APM:** New Relic, DataDog
- **Errors:** Sentry
- **Logs:** ELK Stack, Loki
- **Uptime:** UptimeRobot
- **Database:** pgAdmin, CloudWatch

## Documentation Structure

```
docs/DEVOPS/
├── README.md                    # This file
├── CICD-GITHUB-ACTIONS.MD       # Complete CI/CD guide
└── QUICK-REFERENCE.MD           # Quick commands

.github/workflows/
├── README.md                    # Workflow overview
├── ci.yml                       # Main CI pipeline
├── pr-validation.yml            # PR checks
├── deploy-staging.yml           # Staging deployment
├── deploy-production.yml        # Production deployment
├── dependency-review.yml        # Dependency scanning
└── codeql.yml                   # Security analysis

scripts/
├── README.md                    # Script documentation
├── setup-ci.sh                  # Initial setup
└── run-ci-locally.sh            # Local CI runner
```

## Common Commands

### Local Development

```bash
# Start dev environment
docker compose -f docker/dev/docker-compose.yml up -d

# Run tests
./scripts/run-ci-locally.sh test

# Format code
./scripts/run-ci-locally.sh format

# Check migrations
./scripts/run-ci-locally.sh migrate
```

### CI/CD Operations

```bash
# View workflow status
gh run list

# Trigger staging deployment
gh workflow run deploy-staging.yml

# Trigger production deployment
gh workflow run deploy-production.yml
```

### Debugging

```bash
# View CI logs
gh run view [RUN_ID] --log

# SSH to staging
ssh user@staging-host

# View application logs
docker compose -f docker/staging/docker-compose.yml logs -f web
```

## Troubleshooting

See [QUICK-REFERENCE.MD](./QUICK-REFERENCE.MD) for detailed troubleshooting.

Common issues:

- **CI fails:** Run `./scripts/run-ci-locally.sh all` to reproduce locally
- **Deployment fails:** Check SSH keys and server connectivity
- **Tests fail:** Review logs with `docker compose logs`

## Support

1. Check documentation in this directory
2. Review workflow logs in GitHub Actions
3. Run local CI checks to debug
4. Contact DevOps team
5. Create GitHub issue with `ci/cd` label

## Additional Resources

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Django Deployment](https://docs.djangoproject.com/en/stable/howto/deployment/)
- [Conventional Commits](https://www.conventionalcommits.org/)
