# GitHub Actions Workflows

This directory contains automated CI/CD workflows for the Django + Wagtail backend template.

## Table of Contents

- [GitHub Actions Workflows](#github-actions-workflows)
  - [Table of Contents](#table-of-contents)
  - [Workflow Files](#workflow-files)
  - [Quick Start](#quick-start)
    - [Running Workflows Locally](#running-workflows-locally)
    - [Manual Workflow Triggers](#manual-workflow-triggers)
  - [Workflow Details](#workflow-details)
    - [CI Pipeline (`ci.yml`)](#ci-pipeline-ciyml)
    - [PR Validation (`pr-validation.yml`)](#pr-validation-pr-validationyml)
    - [Deployment Workflows](#deployment-workflows)
    - [Security Workflows](#security-workflows)
  - [Required Secrets](#required-secrets)
    - [Deployment Secrets](#deployment-secrets)
    - [Optional Secrets](#optional-secrets)
  - [GitHub Environments](#github-environments)
    - [`staging`](#staging)
    - [`production`](#production)
    - [`production-approval`](#production-approval)
  - [Workflow Badges](#workflow-badges)
  - [Troubleshooting](#troubleshooting)
    - [Workflow Fails to Start](#workflow-fails-to-start)
    - [Docker Build Failures](#docker-build-failures)
    - [Deployment Failures](#deployment-failures)
    - [Security Scan Failures](#security-scan-failures)
  - [Performance Optimisation](#performance-optimisation)
    - [Workflow Caching](#workflow-caching)
    - [Parallel Execution](#parallel-execution)
    - [Timeout Settings](#timeout-settings)
  - [Documentation](#documentation)
  - [Support](#support)

## Workflow Files

| Workflow | Purpose | Triggers |
|----------|---------|----------|
| `ci.yml` | Main CI pipeline with linting, type checking, and testing | Push to main/staging/dev, PRs |
| `pr-validation.yml` | PR title, branch naming, and commit validation | PRs opened/synchronised |
| `deploy-staging.yml` | Deploy to staging environment | Push to staging branch |
| `deploy-production.yml` | Deploy to production with approval | Push to main branch |
| `dependency-review.yml` | Dependency vulnerability and license scanning | PRs, weekly schedule |
| `codeql.yml` | Security analysis with CodeQL, Semgrep, Bandit | Push to main/staging/dev, weekly |
| `clickup-sync.yml` | Sync GitHub activity with ClickUp tasks | Push, PRs |
| `clickup-branch-sync.yml` | Branch-specific ClickUp integration | Branch events |

## Quick Start

### Running Workflows Locally

You can test workflows locally using [act](https://github.com/nektos/act):

```bash
# Install act
brew install act  # macOS
# or
curl https://raw.githubusercontent.com/nektos/act/master/install.sh | sudo bash  # Linux

# Run CI workflow
act push -j lint-and-format

# Run tests
act push -j test
```

### Manual Workflow Triggers

```bash
# Trigger staging deployment
gh workflow run deploy-staging.yml

# Trigger production deployment
gh workflow run deploy-production.yml

# Trigger dependency review
gh workflow run dependency-review.yml
```

## Workflow Details

### CI Pipeline (`ci.yml`)

Comprehensive quality checks running in Docker containers:

**Jobs:**
- Lint and format checking (Black, isort, flake8)
- Type checking (mypy)
- Security scanning (Bandit)
- Test suite with coverage
- Dockerfile linting (hadolint)
- Configuration validation

**All checks run inside Docker containers for environment parity.**

### PR Validation (`pr-validation.yml`)

Ensures PRs meet project standards:

**Checks:**
- PR title format (Conventional Commits)
- Branch naming conventions
- PR size warnings
- Django migration validation
- Secret detection
- Dependency review
- Commit message linting

### Deployment Workflows

**Staging (`deploy-staging.yml`):**
- Auto-deploys on merge to `staging` branch
- Builds and pushes Docker image
- Deploys via SSH
- Runs health checks
- Sends Slack notifications

**Production (`deploy-production.yml`):**
- Requires manual approval
- Pre-deployment security scans
- Database backup before deployment
- Zero-downtime rolling deployment
- Post-deployment smoke tests
- Automatic rollback on failure

### Security Workflows

**CodeQL (`codeql.yml`):**
- Static code analysis
- Semgrep security scanning
- Bandit Python security checks
- Django security validation
- Secret detection with TruffleHog

**Dependency Review (`dependency-review.yml`):**
- Vulnerability scanning with pip-audit
- License compliance checking
- Outdated dependency detection
- Base image scanning with Trivy
- Weekly automated checks

## Required Secrets

Configure these in repository settings → Secrets and variables → Actions:

### Deployment Secrets

| Secret | Description |
|--------|-------------|
| `CONTAINER_REGISTRY` | Container registry URL (e.g., ghcr.io) |
| `REGISTRY_USERNAME` | Registry username |
| `REGISTRY_PASSWORD` | Registry password or token |
| `STAGING_HOST` | Staging server hostname |
| `STAGING_USER` | SSH username for staging |
| `STAGING_SSH_PRIVATE_KEY` | SSH private key for staging |
| `STAGING_URL` | Staging environment URL |
| `PRODUCTION_HOST` | Production server hostname |
| `PRODUCTION_USER` | SSH username for production |
| `PRODUCTION_SSH_PRIVATE_KEY` | SSH private key for production |
| `PRODUCTION_URL` | Production environment URL |

### Optional Secrets

| Secret | Description |
|--------|-------------|
| `SLACK_WEBHOOK_URL` | Slack webhook for deployment notifications |
| `CLICKUP_API_KEY` | ClickUp API key for task synchronisation |

## GitHub Environments

Set up the following environments in repository settings:

### `staging`
- Protection rules: None (auto-deploy)
- Secrets: Staging-specific secrets
- URL: Set to staging environment URL

### `production`
- Protection rules: Required reviewers (1+)
- Secrets: Production-specific secrets
- URL: Set to production environment URL

### `production-approval`
- Protection rules: Required reviewers (1+)
- Purpose: Manual approval gate before production deployment
- Timeout: 24 hours

## Workflow Badges

Add these badges to README.md:

```markdown
![CI Pipeline](https://github.com/[owner]/[repo]/workflows/CI%20Pipeline/badge.svg)
![Security Scan](https://github.com/[owner]/[repo]/workflows/CodeQL%20Security%20Analysis/badge.svg)
![Deploy Staging](https://github.com/[owner]/[repo]/workflows/Deploy%20to%20Staging/badge.svg)
![Deploy Production](https://github.com/[owner]/[repo]/workflows/Deploy%20to%20Production/badge.svg)
```

## Troubleshooting

### Workflow Fails to Start

- Check workflow syntax with `yamllint .github/workflows/*.yml`
- Verify required secrets are configured
- Check GitHub Actions permissions in repository settings

### Docker Build Failures

- Check Dockerfile syntax
- Verify base image availability
- Review build logs for specific errors
- Clear GitHub Actions cache if needed

### Deployment Failures

- Verify SSH connectivity: `ssh user@host`
- Check server disk space
- Review application logs on server
- Verify database connectivity

### Security Scan Failures

- Review security findings in GitHub Security tab
- Update dependencies to resolve vulnerabilities
- Add exceptions for false positives in workflow configuration

## Performance Optimisation

### Workflow Caching

All workflows use GitHub Actions cache for:
- Docker layers (`cache-from: type=gha`)
- Python dependencies (pip cache)
- Build artifacts

### Parallel Execution

Jobs run in parallel where possible:
- Linting, type checking, and security scans run concurrently
- Independent validation checks run in parallel
- Only deployment jobs run sequentially for safety

### Timeout Settings

Each job has appropriate timeouts:
- Linting: 10 minutes
- Tests: 20 minutes
- Deployments: 20 minutes
- Approval: 24 hours

## Documentation

For complete documentation, see:
- [Full CI/CD Documentation](../../docs/DEVOPS/CICD-GITHUB-ACTIONS.MD)
- [Quick Reference Guide](../../docs/DEVOPS/QUICK-REFERENCE.MD)

## Support

For issues or questions:
1. Check workflow logs in GitHub Actions tab
2. Review documentation in `docs/DEVOPS/`
3. Contact DevOps team
4. Create issue with `ci/cd` label
