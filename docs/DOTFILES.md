# Dotfiles Documentation

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

This document explains all configuration files (dotfiles) in this Django/Wagtail/PostgreSQL/GraphQL project.

## Table of Contents

- [Dotfiles Documentation](#dotfiles-documentation)
  - [Table of Contents](#table-of-contents)
  - [Python Configuration](#python-configuration)
    - [`.python-version`](#python-version)
    - [`pyproject.toml`](#pyprojecttoml)
    - [`setup.cfg`](#setupcfg)
    - [`.flake8`](#flake8)
    - [`.pylintrc`](#pylintrc)
    - [`.bandit`](#bandit)
  - [Code Quality](#code-quality)
    - [`.pre-commit-config.yaml`](#pre-commit-configyaml)
    - [`.editorconfig`](#editorconfig)
    - [`.prettierrc`](#prettierrc)
  - [Testing](#testing)
    - [`.coveragerc`](#coveragerc)
    - [`pytest.ini` (in pyproject.toml)](#pytestini-in-pyprojecttoml)
  - [Editor Configuration](#editor-configuration)
    - [`.vscode/settings.json`](#vscodesettingsjson)
    - [`.vscode/extensions.json`](#vscodeextensionsjson)
    - [`.vscode/launch.json`](#vscodelaunchjson)
  - [Git Configuration](#git-configuration)
    - [`.gitignore`](#gitignore)
    - [`.gitattributes`](#gitattributes)
    - [`.github/CODEOWNERS`](#githubcodeowners)
    - [`.github/PULL_REQUEST_TEMPLATE.md`](#githubpull_request_templatemd)
    - [`.github/dependabot.yml`](#githubdependabotyml)
  - [Docker Configuration](#docker-configuration)
    - [`.dockerignore`](#dockerignore)
    - [`.hadolint.yaml`](#hadolintyaml)
  - [GraphQL Configuration](#graphql-configuration)
    - [`.graphqlconfig`](#graphqlconfig)
  - [Environment Management](#environment-management)
    - [`.envrc`](#envrc)
    - [`.tool-versions`](#tool-versions)
    - [`.env.example`](#envexample)
    - [`.env.chrome`](#envchrome)
  - [Linting Configuration](#linting-configuration)
    - [`.yamllint.yml`](#yamllintyml)
    - [`.markdownlint.json`](#markdownlintjson)
    - [`.shellcheckrc`](#shellcheckrc)
  - [Build Configuration](#build-configuration)
    - [`Makefile`](#makefile)
  - [Configuration File Hierarchy](#configuration-file-hierarchy)
  - [Quick Start](#quick-start)
  - [Customization](#customization)
    - [Adding New Linters](#adding-new-linters)
    - [Changing Code Style](#changing-code-style)
    - [Adding VS Code Extensions](#adding-vs-code-extensions)
  - [Troubleshooting](#troubleshooting)
    - [Pre-commit hooks fail](#pre-commit-hooks-fail)
    - [Linting conflicts](#linting-conflicts)
    - [Type checking errors](#type-checking-errors)
  - [References](#references)

---

## Python Configuration

### `.python-version`
Specifies the Python version for this project (3.14). Used by pyenv and other version managers.

### `pyproject.toml`
Modern Python project configuration file containing:
- **Project metadata**: name, version, description, dependencies
- **Black**: Python code formatter settings (line length: 100)
- **isort**: Import sorting configuration
- **mypy**: Static type checking configuration
- **pytest**: Test runner configuration with coverage settings
- **coverage**: Code coverage reporting settings
- **bandit**: Security linting configuration
- **pylint**: Python linting with Django support
- **ruff**: Fast Python linter (alternative to flake8)

### `setup.cfg`
Legacy Python configuration file for backward compatibility. Contains:
- Package metadata
- pytest configuration
- flake8 settings
- mypy settings
- coverage configuration

### `.flake8`
Flake8 linter configuration:
- Max line length: 100 characters
- Max complexity: 10
- Excludes: migrations, venv, build directories
- Ignores: E203, E501, W503 (conflicts with Black)
- Django-specific import ordering

### `.pylintrc`
Pylint configuration with Django support:
- Django settings module integration
- Disabled rules for Django patterns
- Custom settings for Django models

### `.bandit`
Security linter configuration:
- Excludes test directories
- Skips specific security checks that are false positives

---

## Code Quality

### `.pre-commit-config.yaml`
Pre-commit hooks that run before each commit:
- **General checks**: trailing whitespace, YAML/JSON validation
- **Black**: Auto-format Python code
- **isort**: Sort imports
- **flake8**: Linting with Django plugins
- **mypy**: Type checking
- **bandit**: Security checks
- **django-upgrade**: Upgrade Django code to latest patterns
- **markdownlint**: Markdown linting
- **yamllint**: YAML linting
- **hadolint**: Dockerfile linting

**Installation:**

Pre-commit hooks are automatically installed inside the Docker container. You do not need to install them locally. They run automatically before each commit inside the container.

```bash
# Pre-commit hooks run automatically when committing
git commit -m "your message"
```

**Note:** Do not attempt to install pre-commit locally with `pip install pre-commit`. The Docker container handles all pre-commit hook execution.

### `.editorconfig`
Cross-editor configuration:
- UTF-8 encoding
- LF line endings
- 4 spaces for Python
- 2 spaces for JSON/YAML/HTML/CSS
- Tabs for Makefiles
- Trim trailing whitespace
- Insert final newline

### `.prettierrc`
Code formatter for JavaScript/CSS/HTML in Django templates:
- No semicolons
- Single quotes
- 2-space indentation
- 100 character line width
- LF line endings
- Special handling for HTML templates

---

## Testing

### `.coveragerc`
Coverage.py configuration:
- Source: current directory
- Omits: migrations, tests, venv, static files
- Branch coverage enabled
- HTML and XML report generation

### `pytest.ini` (in pyproject.toml)
Pytest configuration:
- Django settings: `config.settings.test`
- Test discovery patterns
- Coverage integration
- Custom markers: slow, integration, unit, graphql, wagtail
- Verbose output

**Run tests:**
```bash
pytest
pytest --cov --cov-report=html  # With coverage
pytest -m "not slow"             # Skip slow tests
pytest -m integration            # Only integration tests
```

---

## Editor Configuration

### `.vscode/settings.json`
VS Code workspace settings:
- Python interpreter: Points to the Docker container (not a local venv)
- Linters: flake8, pylint, mypy, bandit
- Formatter: Black
- Django language server configuration
- Auto-format on save
- 100 character ruler
- File associations for Django templates

**Note:** All linting and formatting happens inside the Docker container via Makefile commands and pre-commit hooks. Do not configure VS Code to use a local virtual environment.

### `.vscode/extensions.json`
Recommended VS Code extensions:
- Python and Pylance
- Django and Jinja templates
- GraphQL
- Docker
- GitLens
- Prettier and EditorConfig
- Testing adapters

### `.vscode/launch.json`
Debug configurations:
- Run Django server
- Run tests
- Django shell
- Database migrations
- Debug specific tests

---

## Git Configuration

### `.gitignore`
Specifies files to exclude from version control:
- Python: `__pycache__`, `*.pyc`, `*.pyo`
- Django: `*.log`, `db.sqlite3`, `media/`, `staticfiles/`
- Virtual environments: `venv/`, `.venv/`
- IDE: `.idea/`, `.vscode/` (except specific config files)
- Environment files: `.env.*` (except `.env.*.example`)
- Testing: `.coverage`, `.pytest_cache/`, `htmlcov/`
- OS files: `.DS_Store`, `Thumbs.db`

### `.gitattributes`
Git attributes for consistent line endings and file handling:
- LF line endings for all text files
- Binary file detection for images, fonts
- Linguist overrides for GitHub language statistics

### `.github/CODEOWNERS`
Defines code ownership for PR reviews:
- Backend team owns all code by default
- Backend leads own settings and migrations
- DevOps owns Docker and CI/CD
- GraphQL schema requires both backend and frontend review

### `.github/PULL_REQUEST_TEMPLATE.md`
PR template with checklist for:
- Change description
- Testing verification
- Migration handling
- GraphQL schema changes
- Code quality checks

### `.github/dependabot.yml`
Automated dependency updates:
- Python packages (weekly)
- Docker images (weekly)
- GitHub Actions (weekly)

---

## Docker Configuration

### `.dockerignore`
Files to exclude from Docker builds:
- Git files
- Python cache
- Virtual environments
- Development files
- Documentation
- Test results

### `.hadolint.yaml`
Dockerfile linting configuration:
- Ignored rules for flexibility
- Trusted registries
- Warning threshold
- JSON output format

---

## GraphQL Configuration

### `.graphqlconfig`
GraphQL configuration for schema management:
- Schema path: `schema.graphql`
- Development endpoint: `http://localhost:8000/graphql`
- Staging and production endpoints
- Introspection settings
- File includes and excludes

**Generate schema:**
```bash
python manage.py graphql_schema --out schema.graphql
```

---

## Environment Management

### `.envrc`
direnv configuration file (optional):
- Historically used for local virtual environment activation
- **Not required** for this project since development happens in Docker containers

**Note:** This file is kept for teams that use direnv locally for other tools. However, you do not need direnv to develop on this project. The Docker container provides the complete Python environment and dependencies. Simply use the Makefile commands to run tasks inside Docker.

### `.tool-versions`
asdf version manager configuration:
- Python 3.14
- Node.js 24.12.0
- PostgreSQL 18.1

### `.env.example`
Template for environment variables:
- Django settings (DEBUG, SECRET_KEY, ALLOWED_HOSTS)
- Database configuration
- GraphQL settings
- Wagtail configuration
- CORS settings
- Email configuration
- Redis and Celery (optional)
- Security settings

### `.env.chrome`
Browser configuration for testing:
- Chrome binary paths for Selenium, Playwright, Puppeteer
- WebDriver settings
- Headless mode configuration

---

## Linting Configuration

### `.yamllint.yml`
YAML linting rules:
- 120 character line length
- 2-space indentation
- Truthy values allowed: true, false, yes, no
- Excludes: venv, node_modules, static files

### `.markdownlint.json`
Markdown linting configuration:
- 120 character line length (warnings only)
- Disabled rules for flexible documentation
- Tables and code blocks exempt from line length

### `.shellcheckrc`
Shell script linting configuration:
- Disabled rules for common patterns
- Warning severity threshold
- Source path settings

---

## Build Configuration

### `Makefile`
Common development commands:

**Installation:**
```bash
make install        # Install all dependencies
make install-dev    # Install dev dependencies + pre-commit
```

**Development:**
```bash
make dev            # Run development server
make migrate        # Run migrations
make makemigrations # Create new migrations
make shell          # Django shell with shell_plus
make superuser      # Create superuser
```

**Testing:**
```bash
make test           # Run all tests with coverage
make test-fast      # Run tests without coverage
make test-unit      # Run only unit tests
make test-integration # Run only integration tests
```

**Code Quality:**
```bash
make lint           # Run all linters
make format         # Format code with black and isort
make check          # Run pre-commit on all files
```

**Docker:**
```bash
make docker-build   # Build Docker images
make docker-up      # Start containers
make docker-down    # Stop containers
make docker-shell   # Open shell in container
```

**Database:**
```bash
make db-reset       # Reset database (WARNING: destroys data)
make db-backup      # Backup to backup.json
make db-restore     # Restore from backup.json
```

**GraphQL:**
```bash
make graphql-schema # Generate GraphQL schema file
```

**Cleanup:**
```bash
make clean          # Remove temporary files
make clean-all      # Remove venv and all temp files
```

---

## Configuration File Hierarchy

```
backend_template/
├── .editorconfig                 # Editor settings (all editors)
├── .python-version               # Python version (pyenv)
├── pyproject.toml                # Modern Python config (Black, isort, mypy, pytest)
├── setup.cfg                     # Legacy Python config (backward compatibility)
├── .flake8                       # Flake8 linter
├── .pylintrc                     # Pylint with Django support
├── .bandit                       # Security linting
├── .coveragerc                   # Coverage reporting
├── .pre-commit-config.yaml       # Pre-commit hooks
├── .prettierrc                   # JS/CSS/HTML formatter
├── .markdownlint.json            # Markdown linter
├── .yamllint.yml                 # YAML linter
├── .hadolint.yaml                # Dockerfile linter
├── .shellcheckrc                 # Shell script linter
├── .gitignore                    # Git ignore rules
├── .gitattributes                # Git file attributes
├── .dockerignore                 # Docker build exclusions
├── .graphqlconfig                # GraphQL schema config
├── .envrc                        # direnv environment loader
├── .tool-versions                # asdf version manager
├── .env.example                  # Environment variable template
├── .env.chrome                   # Browser paths for testing
├── Makefile                      # Build automation
├── .github/
│   ├── dependabot.yml            # Dependency updates
│   ├── CODEOWNERS                # Code ownership
│   └── PULL_REQUEST_TEMPLATE.md  # PR template
└── .vscode/
    ├── settings.json             # VS Code settings
    ├── extensions.json           # Recommended extensions
    └── launch.json               # Debug configurations
```

---

## Quick Start

**Important:** This project uses Docker containers for development. Do not create a local Python virtual environment.

1. **Build Docker containers:**
   ```bash
   make docker-build
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env.dev
   # Edit .env.dev with your settings if needed
   ```

3. **Start Docker containers:**
   ```bash
   make docker-up
   ```

4. **Run migrations (inside Docker):**
   ```bash
   make migrate
   ```

5. **Start development:**
   ```bash
   make dev
   ```

All Python dependencies, linting, formatting, and pre-commit hooks run automatically inside the Docker container. You do not need to install anything locally except Docker and Docker Compose.

---

## Customization

### Adding New Linters

Add to `.pre-commit-config.yaml`:
```yaml
- repo: https://github.com/user/repo
  rev: v1.0.0
  hooks:
    - id: hook-name
```

### Changing Code Style

Edit `pyproject.toml`:
```toml
[tool.black]
line-length = 120  # Change from 100 to 120
```

### Adding VS Code Extensions

Edit `.vscode/extensions.json`:
```json
{
  "recommendations": [
    "publisher.extension-name"
  ]
}
```

---

## Troubleshooting

### Pre-commit hooks fail

Pre-commit hooks run automatically inside the Docker container. If they fail:

```bash
# Restart Docker containers
make docker-restart

# Rebuild containers if issues persist
make docker-build
make docker-up
```

**Note:** Do not attempt to run `pre-commit autoupdate`, `pre-commit install`, or other pre-commit commands locally. These are handled inside the Docker container automatically.

### Linting conflicts

If linting fails inside Docker:

```bash
# Run linting inside Docker
make lint

# Auto-fix formatting issues
make format
```

These commands run inside the Docker container with the correct configurations from `.flake8` and `pyproject.toml`.

### Type checking errors

If you get type checking errors:

```bash
# Run type checking inside Docker
docker compose -f docker/dev/docker-compose.yml exec web mypy apps/
```

Do not attempt to install type stubs locally with `pip install`. The Docker container has all necessary type stubs installed.

---

## References

- [EditorConfig](https://editorconfig.org/)
- [Black](https://black.readthedocs.io/)
- [isort](https://pycqa.github.io/isort/)
- [flake8](https://flake8.pycqa.org/)
- [mypy](http://mypy-lang.org/)
- [pytest](https://docs.pytest.org/)
- [pre-commit](https://pre-commit.com/)
- [Prettier](https://prettier.io/)
- [Django](https://docs.djangoproject.com/)
- [Wagtail](https://docs.wagtail.org/)
- [GraphQL](https://graphql.org/)
