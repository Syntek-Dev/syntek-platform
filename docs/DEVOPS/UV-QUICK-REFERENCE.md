# UV Quick Reference Card

**Last Updated**: 06/01/2026

---

## Installation

```bash
# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Via pip (alternative)
pip install uv
```

---

## Common Commands

| Task                    | uv Command                   | npm Equivalent              |
| ----------------------- | ---------------------------- | --------------------------- |
| Generate lock file      | `uv lock`                    | `npm install`               |
| Install from lock file  | `uv sync`                    | `npm ci`                    |
| Install dependencies    | `uv pip install -e .`        | `npm install`               |
| Install with dev extras | `uv pip install -e ".[dev]"` | `npm install --include=dev` |
| Add new package         | `uv add <package>`           | `npm install <package>`     |
| Remove package          | `uv remove <package>`        | `npm uninstall <package>`   |
| Update all dependencies | `uv lock --upgrade`          | `npm update`                |
| List installed packages | `uv pip list`                | `npm list`                  |
| Show package info       | `uv pip show <package>`      | `npm info <package>`        |

---

## Workflow

### First Time Setup

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Generate lock file
uv lock

# 3. Install dependencies
uv sync --extra dev
```

### Daily Development

```bash
# Install dependencies (if uv.lock exists)
uv sync --extra dev

# Or use pip-like workflow
uv pip install -e ".[dev]"
```

### Adding Dependencies

```bash
# Method 1: Edit pyproject.toml manually, then:
uv lock          # Update lock file
uv sync          # Install new dependencies

# Method 2: Use uv add (auto-updates pyproject.toml)
uv add django-debug-toolbar
```

### Updating Dependencies

```bash
# Update all to latest compatible versions
uv lock --upgrade

# Install updated versions
uv sync
```

---

## Docker Usage

All Dockerfiles now use `uv`. No changes needed to your workflow:

```bash
# Development
docker compose -f docker/dev/docker-compose.yml up -d

# Testing
docker compose -f docker/test/docker-compose.yml run --rm web pytest

# Staging/Production
docker compose -f docker/production/docker-compose.yml build
```

---

## Lock File (uv.lock)

### What is it?

Like `package-lock.json` in npm, `uv.lock` pins exact versions of all dependencies (including
transitive dependencies) for reproducible builds.

### Should I commit it?

**YES!** Commit `uv.lock` to Git so everyone gets the same versions.

### When to regenerate?

- After editing `pyproject.toml`
- When adding/removing dependencies
- When updating dependencies (`uv lock --upgrade`)
- After resolving merge conflicts in `uv.lock`

---

## Troubleshooting

### uv command not found

```bash
# Check PATH
echo $PATH

# Add to PATH (in ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.cargo/bin:$PATH"

# Reload shell
source ~/.bashrc  # or source ~/.zshrc
```

### Lock file conflicts after git pull

```bash
# Option 1: Use theirs and regenerate
git checkout --theirs uv.lock
uv lock

# Option 2: Use ours and regenerate
git checkout --ours uv.lock
uv lock
```

### Dependency resolution fails

```bash
# View detailed error
uv lock --verbose

# Try upgrading all
uv lock --upgrade

# Fall back to pip temporarily
pip install -e ".[dev]"
```

---

## Why uv?

- **10-100x faster** than pip
- **Lock files** for reproducible builds (like npm)
- **Better caching** in Docker (faster builds)
- **Modern workflow** (install vs lock separation)
- **Drop-in replacement** (works with existing pyproject.toml)

---

## Resources

- **Documentation**: <https://github.com/astral-sh/uv>
- **Migration Guide**: [UV-MIGRATION-GUIDE.md](./UV-MIGRATION-GUIDE.md)
- **Project CLAUDE.md**: [.claude/CLAUDE.md](../../.claude/CLAUDE.md)
