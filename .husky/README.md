# Git Hooks (Husky)

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

Automated Git hooks for code quality, testing, and commit validation.

## Table of Contents

- [Git Hooks (Husky)](#git-hooks-husky)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Hooks](#hooks)
    - [pre-commit](#pre-commit)
    - [pre-push](#pre-push)
    - [commit-msg](#commit-msg)
    - [post-merge](#post-merge)
  - [Setup](#setup)
    - [Manual Installation](#manual-installation)
    - [Verify Installation](#verify-installation)
  - [Bypassing Hooks](#bypassing-hooks)
    - [Skip pre-commit hook](#skip-pre-commit-hook)
    - [Skip pre-push hook](#skip-pre-push-hook)
    - [Skip commit-msg hook](#skip-commit-msg-hook)
  - [Troubleshooting](#troubleshooting)
    - [Hooks not running](#hooks-not-running)
    - [Docker not running error](#docker-not-running-error)
    - [Permission denied](#permission-denied)
    - [Tests fail in hook but pass locally](#tests-fail-in-hook-but-pass-locally)
  - [Related Documentation](#related-documentation)

---

## Overview

Husky automatically manages Git hooks to enforce code quality standards before commits and pushes. This ensures that:

- Code quality checks pass before pushing
- Tests pass before committing
- Commit messages follow the project format
- Dependencies are updated after merging

All hooks run inside Docker containers to maintain consistency with the CI environment.

---

## Hooks

### pre-commit

**When:** Runs before `git commit`

**What it does:**

- Runs linting checks (Black, isort, flake8)
- Validates Python syntax
- Checks for security issues (Bandit)

**If it fails:**

- Commit is blocked
- Fix the issues shown
- Run `./scripts/env/test.sh format` to auto-fix most issues
- Try committing again

### pre-push

**When:** Runs before `git push`

**What it does:**

- Runs full test suite (pytest)
- Verifies all tests pass
- Checks code coverage

**If it fails:**

- Push is blocked
- Fix failing tests locally
- Run `./scripts/env/test.sh run` to test locally
- Try pushing again

### commit-msg

**When:** Runs after commit message is entered

**What it does:**

- Validates commit message format
- Enforces project commit message style

**Expected format:**

```
type(scope): Description

Longer explanation if needed.

Fixes #123
```

**Valid types:**

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `refactor:` - Code refactoring
- `test:` - Test additions/updates
- `ci:` - CI/CD changes

**If it fails:**

- Edit commit message: `git commit --amend`
- Follow the format guidelines
- Save and close the editor

### post-merge

**When:** Runs after successfully merging branches

**What it does:**

- Checks if dependencies changed
- Notifies if migrations need running
- Alerts about environment changes

**If it notifies:**

- Read the message carefully
- Run migrations if needed: `./scripts/env/dev.sh migrate`
- Install dependencies if needed: `pip install -e ".[dev]"`

---

## Setup

Hooks are installed automatically by the project setup process.

### Manual Installation

If hooks are not installed:

```bash
# Install husky
npm install

# Install git hooks
npx husky install
```

### Verify Installation

```bash
# Check hooks are installed
ls -la .husky/

# Should show:
# pre-commit
# pre-push
# commit-msg
# post-merge
```

---

## Bypassing Hooks

**Only use as a last resort!**

### Skip pre-commit hook

```bash
git commit --no-verify
```

### Skip pre-push hook

```bash
git push --no-verify
```

### Skip commit-msg hook

```bash
git commit --no-verify -m "message"
```

**Warning:** Bypassing hooks means code quality checks won't run. Only do this if you have a
very good reason and plan to fix issues immediately.

---

## Troubleshooting

### Hooks not running

**Problem:** Pre-commit hook doesn't run

**Solution:**

```bash
# Reinstall hooks
npx husky install

# Verify installation
ls -la .husky/pre-commit
```

### Docker not running error

**Problem:** Hook fails with "Docker not running" or "Cannot connect to Docker daemon"

**Solution:**

1. Start Docker (Docker Desktop on macOS/Windows, `systemctl start docker` on Linux)
2. Retry the git operation

### Permission denied

**Problem:** "Permission denied" when running hooks

**Solution:**

```bash
# Make hooks executable
chmod +x .husky/pre-commit
chmod +x .husky/pre-push
chmod +x .husky/commit-msg
chmod +x .husky/post-merge
```

### Tests fail in hook but pass locally

**Problem:** Tests fail in pre-push hook but pass when running locally

**Possible causes:**

- Different Docker image versions
- Environment variables not set
- Uncommitted changes

**Solution:**

```bash
# Clear Docker cache and rebuild
docker compose -f docker/test/docker-compose.yml down -v
docker compose -f docker/test/docker-compose.yml build --no-cache

# Try push again
git push
```

---

## Related Documentation

- [Setup Guide](../docs/DEVELOPER-SETUP.md) - Development environment setup
- [Scripts](../scripts/README.md) - Available helper scripts
- [DEVOPS/CICD](../docs/DEVOPS/CICD-GITHUB-ACTIONS.MD) - CI/CD documentation

---

**Last Updated:** 2026-01-03
