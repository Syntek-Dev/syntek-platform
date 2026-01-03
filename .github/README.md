# GitHub Configuration

GitHub-specific configuration for CI/CD workflows, code quality, security scanning, and pull request management.

## Table of Contents

- [GitHub Configuration](#github-configuration)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [Workflows](#workflows)
    - [Available Workflows](#available-workflows)
    - [Running Workflows Locally](#running-workflows-locally)
    - [Workflow Environment](#workflow-environment)
  - [Security](#security)
    - [CodeQL Analysis](#codeql-analysis)
    - [Dependabot](#dependabot)
  - [Pull Requests](#pull-requests)
    - [Pull Request Template](#pull-request-template)
    - [Review Requirements](#review-requirements)
  - [Code Owners](#code-owners)
    - [Using Code Owners](#using-code-owners)
    - [Adding Code Owners](#adding-code-owners)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains all GitHub-specific configuration:

- **Workflows:** GitHub Actions CI/CD pipeline definitions
- **Dependabot:** Automated dependency updates
- **CodeQL:** Code quality and security scanning
- **Templates:** Pull request and issue templates
- **Configuration:** Code owner assignments and branch protection rules

All workflows run inside Docker containers to ensure consistency with the development environment.

---

## Directory Structure

```
.github/
├── workflows/           # GitHub Actions CI/CD pipelines
├── codeql/             # CodeQL analysis configuration
├── CODEOWNERS          # Code owner assignments
├── dependabot.yml      # Dependency update automation
├── PULL_REQUEST_TEMPLATE.md  # PR template
└── README.md           # This file
```

---

## Workflows

GitHub Actions workflows are defined in `.github/workflows/`. They run the full CI/CD pipeline for every push and pull request.

### Available Workflows

| Workflow                | Trigger     | Purpose                            |
| ----------------------- | ----------- | ---------------------------------- |
| `tests.yml`             | Push, PR    | Run pytest, coverage checks        |
| `lint.yml`              | Push, PR    | Black, isort, flake8, mypy, bandit |
| `security.yml`          | Push, PR    | Django security, OWASP checks      |
| `migrations.yml`        | Push, PR    | Validate Django migrations         |
| `deploy-staging.yml`    | Main branch | Deploy to staging environment      |
| `deploy-production.yml` | Tag release | Deploy to production               |

### Running Workflows Locally

Test workflows locally before pushing:

```bash
# Run all CI checks in Docker
./scripts/run-ci-locally.sh all

# Run specific checks
./scripts/run-ci-locally.sh lint
./scripts/run-ci-locally.sh test
./scripts/run-ci-locally.sh security
```

### Workflow Environment

All workflows run in Docker containers:

- **Test Container:** `docker/test/docker-compose.yml`
- **Python:** 3.14 (matches project specification)
- **Database:** PostgreSQL in test mode
- **Cache:** Redis in test mode

This ensures workflow environment matches developer machines exactly.

---

## Security

### CodeQL Analysis

CodeQL scans the codebase for security vulnerabilities and code quality issues.

**Configuration:** `.github/codeql/codeql-config.yml`

**Runs on:**

- Every push to main
- Pull requests
- Weekly schedule

**View Results:**

- GitHub Security tab: `Settings > Code security and analysis > Code scanning alerts`

### Dependabot

Automated dependency update checks are configured in `dependabot.yml`.

**Monitors:**

- Python requirements files
- Node.js package.json
- GitHub Actions versions

**Security Updates:** Created immediately as high-priority PRs
**Regular Updates:** Grouped and scheduled

---

## Pull Requests

### Pull Request Template

All new pull requests use the template defined in `PULL_REQUEST_TEMPLATE.md`.

The template includes sections for:

- **Description:** What changes were made and why
- **Testing:** How to test the changes
- **Screenshots:** Visual changes (if applicable)
- **Checklist:** Verification items before merge

### Review Requirements

Pull requests require:

1. **CI Pipeline Pass:** All workflows must pass
2. **Code Review:** At least one approval from code owners
3. **No Conflicts:** Must be up to date with main branch
4. **Branch Protection:** Rules enforce these requirements

---

## Code Owners

Code ownership is defined in `CODEOWNERS`. This file automatically assigns reviewers based on file patterns.

### Using Code Owners

When you create a PR:

1. Code owners are automatically requested as reviewers
2. At least one code owner must approve before merge
3. If a code owner doesn't respond, PR may be blocked

### Adding Code Owners

To assign responsibility for a section:

```
# Format: path  @github-username
apps/users/  @developer-name
config/  @admin-name
```

---

## Related Documentation

- [Workflows README](workflows/README.md) - Detailed workflow documentation
- [DEVOPS/CICD-GITHUB-ACTIONS.MD](../docs/DEVOPS/CICD-GITHUB-ACTIONS.MD) - Complete CI/CD guide
- [Setup Guide](../docs/DEVELOPER-SETUP.md) - Developer environment setup
- [PM Integration](../docs/PM-INTEGRATION/) - ClickUp GitHub integration

---

**Last Updated:** 2026-01-03
