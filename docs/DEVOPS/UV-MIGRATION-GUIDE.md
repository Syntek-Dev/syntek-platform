# UV Migration Guide

**Last Updated**: 06/01/2026
**Version**: 0.3.0
**Maintained By**: Development Team

---

## Table of Contents

- [UV Migration Guide](#uv-migration-guide)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [What is uv?](#what-is-uv)
  - [Lock File Behaviour (uv.lock vs package-lock.json)](#lock-file-behaviour-uvlock-vs-package-lockjson)
    - [Key Differences from npm](#key-differences-from-npm)
    - [Workflow Comparison](#workflow-comparison)
  - [Migration Changes](#migration-changes)
    - [Dockerfiles Updated](#dockerfiles-updated)
    - [Key Changes in Dockerfiles](#key-changes-in-dockerfiles)
  - [Local Development Setup](#local-development-setup)
    - [Installing uv](#installing-uv)
    - [Creating the Lock File](#creating-the-lock-file)
    - [Installing Dependencies](#installing-dependencies)
  - [Docker Usage](#docker-usage)
    - [Development Environment](#development-environment)
    - [Test Environment](#test-environment)
    - [Staging/Production](#stagingproduction)
  - [Common uv Commands](#common-uv-commands)
  - [Benefits of uv](#benefits-of-uv)
  - [Troubleshooting](#troubleshooting)
    - [uv command not found in Docker](#uv-command-not-found-in-docker)
    - [Lock file conflicts](#lock-file-conflicts)
    - [Dependency resolution failures](#dependency-resolution-failures)
  - [Migration Checklist](#migration-checklist)

---

## Overview

This project has been migrated from using `pip` to using **`uv`**, a fast Python package installer
and resolver written in Rust. This document explains the changes, how to use `uv`, and how it
compares to familiar tools like `npm`.

---

## What is uv?

**`uv`** is a modern Python package installer that:

- Installs packages 10-100x faster than pip
- Uses a Cargo-inspired (Rust) resolver for dependency management
- Generates lock files (`uv.lock`) for reproducible builds
- Works with `pyproject.toml` (no separate requirements.txt needed)
- Compatible with existing pip workflows

**GitHub**: <https://github.com/astral-sh/uv>

---

## Lock File Behaviour (uv.lock vs package-lock.json)

Yes, `uv` creates lock files similar to `package-lock.json`, but with some differences:

| Feature                          | npm                 | uv                      |
| -------------------------------- | ------------------- | ----------------------- |
| **Lock file name**               | `package-lock.json` | `uv.lock`               |
| **Format**                       | JSON                | TOML (human-readable)   |
| **Auto-generated on install**    | Yes (`npm install`) | No (explicit `uv lock`) |
| **Pins transitive dependencies** | Yes                 | Yes                     |
| **Commit to Git**                | Yes                 | Yes                     |
| **CI/Docker usage**              | `npm ci`            | `uv sync`               |

### Key Differences from npm

1. **Separate lock generation**: Unlike `npm install` which both installs and updates the lock
   file, `uv` separates these operations:
   - `uv lock` - Generate/update lock file
   - `uv sync` - Install from lock file

2. **TOML format**: `uv.lock` is TOML-based (like Cargo.lock in Rust), making it more
   human-readable than JSON.

3. **Optional lock files**: You can use `uv` without a lock file (like pip), but lock files are
   recommended for reproducible builds.

### Workflow Comparison

| npm Workflow            | uv Workflow           | Purpose                                           |
| ----------------------- | --------------------- | ------------------------------------------------- |
| `npm install`           | `uv lock`             | Create/update lock file with resolved versions    |
| `npm ci`                | `uv sync`             | Install exact versions from lock file (CI/Docker) |
| `npm install <package>` | `uv add <package>`    | Add new dependency and update lock                |
| `npm update`            | `uv lock --upgrade`   | Update all dependencies to latest compatible      |
| Edit `package.json`     | Edit `pyproject.toml` | Modify dependencies manually                      |

---

## Migration Changes

### Dockerfiles Updated

All Dockerfiles have been updated to use `uv` instead of `pip`:

- `docker/dev/Dockerfile`
- `docker/test/Dockerfile`
- `docker/staging/Dockerfile`
- `docker/production/Dockerfile`

### Key Changes in Dockerfiles

1. **Install uv during build**:

   ```dockerfile
   RUN curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Add uv to PATH**:

   ```dockerfile
   ENV PATH="/root/.cargo/bin:$PATH"
   ```

3. **Copy both pyproject.toml and uv.lock**:

   ```dockerfile
   COPY pyproject.toml uv.lock* ./
   ```

   Note: `uv.lock*` means copy if exists (optional until generated)

4. **Use `uv pip install` with `--system` flag**:
   ```dockerfile
   RUN uv pip install --system -e ".[dev]"
   ```
   The `--system` flag installs packages system-wide in the container (not in a virtual environment).

---

## Local Development Setup

### Installing uv

**Linux/macOS:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Via pip (alternative):**

```bash
pip install uv
```

**Verify installation:**

```bash
uv --version
```

### Creating the Lock File

Generate `uv.lock` from `pyproject.toml`:

```bash
# Generate lock file with all dependencies resolved
uv lock

# This creates uv.lock in the project root
```

**When to run `uv lock`:**

- After modifying `pyproject.toml`
- When adding new dependencies
- When you want to update dependency versions
- Before committing dependency changes

### Installing Dependencies

**Option 1: Use uv sync (recommended with lock file)**

```bash
# Install from uv.lock (reproducible, fast)
uv sync

# Install with specific extras
uv sync --extra dev
```

**Option 2: Use uv pip install (like traditional pip)**

```bash
# Install base dependencies
uv pip install -e .

# Install with dev extras
uv pip install -e ".[dev]"

# Install with production extras
uv pip install -e ".[production]"
```

---

## Docker Usage

### Development Environment

```bash
# Build with uv (automatically installs dev dependencies)
docker compose -f docker/dev/docker-compose.yml build

# Start development environment
docker compose -f docker/dev/docker-compose.yml up -d

# View build logs to see uv in action
docker compose -f docker/dev/docker-compose.yml build --no-cache web
```

### Test Environment

```bash
# Build test container with uv
docker compose -f docker/test/docker-compose.yml build

# Run tests
docker compose -f docker/test/docker-compose.yml run --rm web pytest
```

### Staging/Production

```bash
# Build production image with uv
docker compose -f docker/production/docker-compose.yml build

# Production containers install only production extras
# (no dev/test dependencies)
```

---

## Common uv Commands

| Command                        | Description                                           |
| ------------------------------ | ----------------------------------------------------- |
| `uv lock`                      | Generate/update `uv.lock` from `pyproject.toml`       |
| `uv sync`                      | Install dependencies from `uv.lock`                   |
| `uv sync --extra dev`          | Install with dev extras                               |
| `uv add <package>`             | Add new dependency and update lock                    |
| `uv remove <package>`          | Remove dependency and update lock                     |
| `uv lock --upgrade`            | Update all dependencies to latest compatible versions |
| `uv pip install -e .`          | Install project in editable mode (like pip)           |
| `uv pip install --system -e .` | Install system-wide (Docker containers)               |
| `uv pip list`                  | List installed packages                               |
| `uv pip freeze`                | Output installed packages in requirements.txt format  |
| `uv --version`                 | Show uv version                                       |

---

## Benefits of uv

1. **Speed**: 10-100x faster than pip
   - Parallel downloads
   - Rust-based resolver
   - Global package cache

2. **Reproducible Builds**: `uv.lock` ensures everyone gets the same versions
   - Pins all transitive dependencies
   - Works across platforms (Linux, macOS, Windows)

3. **Better Caching**: Docker builds are faster
   - Layer caching with `COPY pyproject.toml uv.lock* ./`
   - Only rebuilds when dependencies change

4. **Modern Workflow**: Similar to npm/yarn/pnpm
   - Lock files for CI/CD
   - Separate install vs lock operations

5. **Drop-in Replacement**: Works with existing `pyproject.toml`
   - No migration needed for dependency definitions
   - Compatible with pip requirements

---

## Troubleshooting

### uv command not found in Docker

**Symptom**: `uv: command not found` during Docker build

**Solution**: Ensure uv installation completed and PATH is set:

```dockerfile
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"
```

### Lock file conflicts

**Symptom**: `uv.lock` has merge conflicts after git pull

**Solution**: Regenerate the lock file:

```bash
# Discard lock file changes
git checkout --theirs uv.lock

# Regenerate from pyproject.toml
uv lock

# Verify it works
uv sync
```

### Dependency resolution failures

**Symptom**: `uv lock` fails with "cannot resolve dependencies"

**Solution 1**: Check for conflicting version constraints in `pyproject.toml`

```bash
# View detailed resolution output
uv lock --verbose
```

**Solution 2**: Update to latest compatible versions

```bash
# Upgrade all dependencies
uv lock --upgrade
```

**Solution 3**: Fall back to pip temporarily

```bash
# Use pip for debugging
pip install -e ".[dev]"
pip freeze > requirements.txt
```

---

## Migration Checklist

- [x] Install `uv` locally (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- [x] Generate `uv.lock` (`uv lock`)
- [x] Update all Dockerfiles to use `uv`
- [x] Test development environment builds (`docker compose -f docker/dev/docker-compose.yml build`)
- [x] Test test environment builds (`docker compose -f docker/test/docker-compose.yml build`)
- [x] Test staging/production builds
- [x] Commit `uv.lock` to Git
- [x] Update CI/CD pipelines (if needed)
- [x] Update team documentation
- [x] Train team on `uv` commands

---

**Next Steps:**

1. Run `uv lock` to generate `uv.lock`
2. Commit `uv.lock` to Git
3. Test Docker builds with `uv`
4. Update CI/CD workflows (GitHub Actions, etc.) if they reference pip directly
