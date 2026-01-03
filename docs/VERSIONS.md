# Versions and Dependencies

## Table of Contents

- [Versions and Dependencies](#versions-and-dependencies)
  - [Table of Contents](#table-of-contents)
  - [Core Framework Versions](#core-framework-versions)
  - [System Requirements](#system-requirements)
    - [Installing Specific Versions](#installing-specific-versions)
  - [Development Tools](#development-tools)
    - [Code Quality Tools](#code-quality-tools)
    - [Testing Tools](#testing-tools)
    - [Pre-commit Hooks](#pre-commit-hooks)
    - [Editor and IDE Tools](#editor-and-ide-tools)
  - [Docker Base Images](#docker-base-images)
    - [Development Docker Image](#development-docker-image)
    - [Testing Docker Image](#testing-docker-image)
    - [Staging Docker Image](#staging-docker-image)
    - [Production Docker Image](#production-docker-image)
  - [Version Management](#version-management)
    - [Configuration Files](#configuration-files)
    - [Version Consistency](#version-consistency)
  - [Updating Versions](#updating-versions)
    - [Updating Python Version](#updating-python-version)
    - [Updating Django or Wagtail](#updating-django-or-wagtail)
    - [Updating System Tools](#updating-system-tools)
  - [Version Pinning Strategy](#version-pinning-strategy)
  - [Last Updated](#last-updated)

---

## Core Framework Versions

These are the primary framework versions used in this project, as specified in `pyproject.toml`:

| Framework | Version | Notes |
|-----------|---------|-------|
| Django | 5.2 | Web framework |
| Wagtail CMS | 7 | Content management system |
| Python | 3.14 | Programming language |
| PostgreSQL | 18.1 | Database |

## System Requirements

All development machines and deployment environments must meet these minimum requirements:

| Tool | Version | Purpose | Configuration File |
|------|---------|---------|-------------------|
| Python | 3.14 | Runtime and development | `.python-version` |
| PostgreSQL | 18.1 | Database | `.tool-versions` |
| Node.js | 24.12.0 | Frontend tooling (Prettier, build tools) | `.tool-versions` |
| Docker | Latest | Containerization (optional but recommended) | N/A |
| Docker Compose | Latest | Multi-container orchestration | N/A |
| Git | Latest | Version control | N/A |

### Installing Specific Versions

**Using asdf version manager (recommended):**
```bash
# Install asdf
git clone https://github.com/asdf-vm/asdf.git ~/.asdf

# Install required versions from .tool-versions
asdf install

# Verify installations
asdf current
```

**Using individual version managers:**

```bash
# Python (using pyenv)
pyenv install 3.14
pyenv local 3.14

# Node.js (using nvm)
nvm install 24.12.0
nvm use 24.12.0

# PostgreSQL (via system package manager)
# macOS: brew install postgresql@18
# Ubuntu: sudo apt-get install postgresql-18
# Windows: Download from https://www.postgresql.org/download/windows/
```

---

## Development Tools

The following tools are configured in the project but versions are managed through pip:

### Code Quality Tools

| Tool | Purpose | Configuration |
|------|---------|---------------|
| Black | Code formatting | `pyproject.toml` - line length: 100 |
| isort | Import sorting | `pyproject.toml` - Black compatible |
| Ruff | Fast Python linting | `pyproject.toml` - replaces flake8 |
| mypy | Static type checking | `pyproject.toml` - Django support |
| pylint | Additional linting | `.pylintrc` - Django plugins |
| flake8 | Legacy linting | `.flake8` - kept for compatibility |
| bandit | Security scanning | `.bandit` - finds security issues |

### Testing Tools

| Tool | Purpose | Configuration |
|------|---------|---------------|
| pytest | Test runner | `pyproject.toml` - pytest settings |
| coverage | Coverage reporting | `.coveragerc` - coverage settings |
| pytest-django | Django integration | `pyproject.toml` - DJANGO_SETTINGS_MODULE |
| pytest-cov | Coverage plugin | `pyproject.toml` - auto-enabled |

### Pre-commit Hooks

Versions are managed in `.pre-commit-config.yaml`:

```yaml
- black          # Code formatter
- isort          # Import sorter
- flake8         # Linter
- mypy           # Type checker
- bandit         # Security
- django-upgrade # Django upgrades
- markdownlint   # Markdown linting
- yamllint       # YAML linting
- hadolint       # Dockerfile linting
```

**Installation:**
```bash
pip install pre-commit
pre-commit install
```

### Editor and IDE Tools

| Tool | Version | Configuration |
|------|---------|---------------|
| Prettier | Latest | `.prettierrc` |
| EditorConfig | Via plugin | `.editorconfig` |
| Pylance | Latest | VS Code extension |

---

## Docker Base Images

Each environment uses specific Docker base images for consistency:

### Development Docker Image

```dockerfile
FROM python:3.14-slim

# System packages
- build-essential (latest)
- libpq-dev (latest)
```

**Location:** `docker/dev/Dockerfile`

### Testing Docker Image

```dockerfile
FROM python:3.14-slim

# Same base as dev with test dependencies
```

**Location:** `docker/test/Dockerfile`

### Staging Docker Image

```dockerfile
FROM python:3.14-slim

# Production-optimized dependencies
```

**Location:** `docker/staging/Dockerfile`

### Production Docker Image

```dockerfile
FROM python:3.14-slim

# Minimal, production-ready image
```

**Location:** `docker/production/Dockerfile`

All images use `python:3.14-slim` as the base for consistency across environments.

---

## Version Management

### Configuration Files

**`.python-version`** - Python version specification for pyenv
```
python 3.14
```

**`.tool-versions`** - asdf version manager configuration
```
python 3.14
nodejs 24.12.0
postgres 18.1
```

**`pyproject.toml`** - Modern Python project configuration
```toml
requires-python = ">=3.14"

[project]
classifiers = [
    "Framework :: Django :: 5.2",
    "Framework :: Wagtail :: 7",
    "Programming Language :: Python :: 3.14",
]

[tool.mypy]
python_version = "3.14"

[tool.ruff]
target-version = "py314"

[tool.black]
target-version = ['py314']
```

**`setup.cfg`** - Legacy configuration for backward compatibility
```ini
python_requires = >=3.14
```

### Version Consistency

The following versions are pinned across multiple configuration files to ensure consistency:

| Setting | Files | Current Value |
|---------|-------|---------------|
| Python version | `.python-version`, `pyproject.toml`, `setup.cfg`, Docker | 3.14 |
| Node.js version | `.tool-versions` | 24.12.0 |
| PostgreSQL version | `.tool-versions`, Docker | 18.1 |
| Django version | `pyproject.toml` classifiers | 5.2 |
| Wagtail version | `pyproject.toml` classifiers | 7 |

---

## Updating Versions

### Updating Python Version

1. **Update configuration files:**
   ```bash
   # .python-version
   echo "python 3.15" > .python-version

   # .tool-versions
   sed -i 's/python 3.14/python 3.15/' .tool-versions
   ```

2. **Update pyproject.toml:**
   ```toml
   requires-python = ">=3.15"

   [tool.black]
   target-version = ['py315']

   [tool.ruff]
   target-version = "py315"

   [tool.mypy]
   python_version = "3.15"
   ```

3. **Update Dockerfiles:**
   ```dockerfile
   FROM python:3.15-slim
   ```

4. **Update CLAUDE.md and documentation:**
   - Update the Prerequisites section
   - Update version tables
   - Update example commands if needed

5. **Test the update:**
   ```bash
   # Rebuild Docker containers with new Python version
   make docker-build

   # Start containers and verify version
   make docker-up
   docker compose -f docker/dev/docker-compose.yml exec web python --version
   ```

### Updating Django or Wagtail

1. **Update pyproject.toml:**
   ```toml
   classifiers = [
       "Framework :: Django :: 6.0",  # Updated
       "Framework :: Wagtail :: 8",   # Updated
   ]
   ```

2. **Update CLAUDE.md** if architecture changes

3. **Update documentation** to reflect new features/breaking changes

4. **Run tests inside Docker:**
   ```bash
   make test
   ```

5. **Review breaking changes** in official release notes

### Updating System Tools

For Node.js, PostgreSQL, or other system tools:

1. **Update .tool-versions:**
   ```
   nodejs 25.0.0  # Updated
   postgres 19.0  # Updated
   ```

2. **Update .tool-versions documentation** in `DOTFILES.md`

3. **Update Docker base images** if system dependencies change

4. **Rebuild Docker containers with new versions:**
   ```bash
   # Rebuild to use updated base images
   make docker-build
   make docker-up

   # Verify versions inside Docker
   docker compose -f docker/dev/docker-compose.yml exec web python --version
   docker compose -f docker/dev/docker-compose.yml exec web node --version
   ```

---

## Version Pinning Strategy

This project uses:

- **Pinned major versions** for frameworks (Django 5.2, Wagtail 7) to prevent breaking changes
- **Flexible minor/patch versions** in requirements files (managed by pip during installation)
- **Specific versions in .tool-versions** for reproducible development environments
- **Python version pinning** to match team capabilities and library support

This approach balances stability with flexibility for bug fixes and security updates.

---

## Last Updated

**Date:** 2026-01-03
**By:** Documentation Update
**Changes:** Created comprehensive version documentation with all current versions
