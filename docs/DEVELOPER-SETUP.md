# Developer Setup Guide

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

This guide helps new developers get started with the Django/PostgreSQL/GraphQL backend project.

All development happens inside Docker containers. No local Python virtual environment is needed.

## Table of Contents

- [Developer Setup Guide](#developer-setup-guide)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Quick Start](#quick-start)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Build Docker Containers](#2-build-docker-containers)
    - [3. Start Docker Containers](#3-start-docker-containers)
    - [4. Set Up Environment Variables](#4-set-up-environment-variables)
    - [5. Run Migrations](#5-run-migrations)
    - [6. Create Superuser](#6-create-superuser)
    - [7. Access the Application](#7-access-the-application)
  - [Development Workflow](#development-workflow)
    - [Code Quality Checks](#code-quality-checks)
    - [Running Tests](#running-tests)
    - [Database Migrations](#database-migrations)
    - [Django Shell](#django-shell)
    - [GraphQL Schema](#graphql-schema)
  - [Editor Setup](#editor-setup)
    - [VS Code](#vs-code)
    - [PyCharm](#pycharm)
    - [Other Editors](#other-editors)
  - [Git Workflow](#git-workflow)
    - [Branch Naming](#branch-naming)
    - [Commit Messages](#commit-messages)
    - [Pre-commit Hooks](#pre-commit-hooks)
    - [Pull Requests](#pull-requests)
  - [Docker Development](#docker-development)
    - [Using Docker Compose](#using-docker-compose)
    - [Environment-Specific Containers](#environment-specific-containers)
  - [Common Tasks](#common-tasks)
    - [Adding a New Django App](#adding-a-new-django-app)
    - [Adding GraphQL Queries/Mutations](#adding-graphql-queriesmutations)
  - [Troubleshooting](#troubleshooting)
    - [Database Connection Issues](#database-connection-issues)
    - [Migration Conflicts](#migration-conflicts)
    - [Import Errors](#import-errors)
    - [Pre-commit Hook Failures](#pre-commit-hook-failures)
    - [Port Already in Use](#port-already-in-use)
  - [Environment Variables Reference](#environment-variables-reference)
  - [Additional Resources](#additional-resources)
  - [Getting Help](#getting-help)
  - [Next Steps](#next-steps)

## Prerequisites

- **Docker** (required for all development)
- **Docker Compose** (required for multi-container orchestration)
- Git
- Node.js 24.12.0 (optional, for running frontend tooling outside Docker)

Note: Python, PostgreSQL, and all project dependencies are installed inside Docker containers.
You do not need to install them locally.

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd backend_template
```

### 2. Build Docker Containers

```bash
# Build the Docker images for development
make docker-build

# Or manually:
docker compose -f docker/dev/docker-compose.yml build
```

### 3. Start Docker Containers

```bash
# Start all development containers
make docker-up

# Or manually:
docker compose -f docker/dev/docker-compose.yml up -d
```

The containers include:

- **web**: Django application running on port 8000
- **db**: PostgreSQL 18.1 database
- **redis**: Redis cache (if configured)
- **mailpit**: Email simulator on port 8025

### 4. Set Up Environment Variables

```bash
# Copy the example environment file
cp .env.example .env.dev

# Edit .env.dev with your local settings
nano .env.dev  # or use your preferred editor
```

**Important environment variables to set:**

- `SECRET_KEY`: Generate using
  `docker compose -f docker/dev/docker-compose.yml exec web python -c
"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- `DATABASE_URL`: PostgreSQL connection string (predefined in docker-compose)
- `DEBUG`: Set to `True` for development

### 5. Run Migrations

```bash
# Run migrations inside the Docker container
make migrate

# Or manually:
docker compose -f docker/dev/docker-compose.yml exec web python manage.py migrate
```

### 6. Create Superuser

```bash
# Create admin user inside the Docker container
make superuser

# Or manually:
docker compose -f docker/dev/docker-compose.yml exec web python manage.py createsuperuser
```

### 7. Access the Application

Visit:

- **Django Admin**: <http://localhost:8000/admin/>
- **GraphQL Playground**: <http://localhost:8000/graphql>
- **Mailpit (Email Simulator)**: <http://localhost:8025>

All services are automatically started when you run `make docker-up`.

## Development Workflow

### Code Quality Checks

Before committing, ensure your code passes all checks:

```bash
# Format code
make format

# Run linters
make lint

# Run all pre-commit checks
make check
```

### Running Tests

All tests run inside Docker containers. Use the Makefile commands which abstract the Docker complexity:

```bash
# Run all tests with coverage (inside Docker)
make test

# Run specific test types (inside Docker)
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-fast          # Without coverage (faster)

# Run specific test file (inside Docker)
make test-file FILE=tests/test_models.py

# Run tests matching pattern (inside Docker)
make test-pattern PATTERN="test_user"
```

**Note:** All pytest commands run inside the Docker test container. Do not attempt to run pytest
locally - the container provides the correct Python environment, dependencies, and database setup.

### Database Migrations

All migration commands run inside the Docker container:

```bash
# Create new migration (inside Docker)
make makemigrations

# Or with custom name (inside Docker):
make makemigrations NAME=add_user_profile

# Apply migrations (inside Docker)
make migrate

# Check migration status (inside Docker)
make showmigrations

# Rollback migration (inside Docker)
make migrate APP=app_name VERSION=migration_name
```

**Note:** Do not run `python manage.py` commands locally. Always use the Makefile commands which
execute inside the Docker container with the correct database and dependencies.

### Django Shell

```bash
# Open enhanced Django shell inside Docker (with shell_plus)
make shell

# All Django shell sessions run inside the Docker container
# Do not attempt to run 'python manage.py shell' locally
```

### GraphQL Schema

```bash
# Generate GraphQL schema file (inside Docker)
make graphql-schema
```

**Note:** The `make graphql-schema` command runs inside the Docker container with the correct Django environment.

## Editor Setup

### VS Code

The project includes VS Code configuration in `.vscode/`:

1. **Install recommended extensions** (VS Code will prompt you):
   - Python
   - Pylance
   - Django
   - GraphQL
   - Docker
   - GitLens
   - Prettier

2. **Extensions will auto-configure** formatting and linting

3. **Debug configurations** are available in the Debug panel:
   - Django: Run Server
   - Django: Run Tests
   - Django: Shell
   - Django: Migrate

### PyCharm

1. **Set Python interpreter**: Settings → Project → Python Interpreter → Add → Docker Compose
   - Select the development Docker service
   - PyCharm will auto-detect the Python interpreter from the Docker container
2. **Enable Django support**: Settings → Languages & Frameworks → Django
3. **Set Django settings**: `config.settings.dev`
4. **Configure Run/Debug Configuration**:
   - Create a Django Server configuration that uses Docker Compose
   - Set Docker Compose service to `web` from `docker/dev/docker-compose.yml`
5. **Mark directories**:
   - Mark `apps/` as Sources Root
   - Mark `tests/` as Test Sources Root

**Note:** Do not use a local virtual environment. PyCharm will use the Python interpreter inside the Docker container.

### Other Editors

The `.editorconfig` file will configure most editors automatically. Install the EditorConfig plugin for your editor.

## Git Workflow

### Branch Naming

Follow these conventions:

- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Urgent production fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation updates

### Commit Messages

Follow Conventional Commits:

- `feat: add user authentication`
- `fix: resolve database connection issue`
- `docs: update API documentation`
- `test: add tests for user model`
- `refactor: simplify query logic`
- `chore: update dependencies`

### Pre-commit Hooks

Pre-commit hooks run automatically before each commit:

- Code formatting (Black, isort)
- Linting (flake8, pylint)
- Type checking (mypy)
- Security checks (bandit)
- YAML/JSON validation

If hooks fail, fix the issues and commit again.

**Bypass hooks** (not recommended):

```bash
git commit --no-verify
```

### Pull Requests

1. **Create a feature branch**:

   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make changes and commit**:

   ```bash
   git add .
   git commit -m "feat: add my new feature"
   ```

3. **Push to remote**:

   ```bash
   git push origin feature/my-new-feature
   ```

4. **Create PR** on GitHub/GitLab using the PR template

5. **Address review comments** and push updates

6. **Merge** when approved

## Docker Development

### Using Docker Compose

```bash
# Build images
make docker-build

# Start all services
make docker-up

# Stop services
make docker-down

# View logs
make docker-logs

# Open shell in container
make docker-shell

# Run commands in container
docker-compose exec web python manage.py migrate
docker-compose exec web pytest
```

### Environment-Specific Containers

```bash
# Development
docker-compose -f docker-compose.yml up

# With overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

## Common Tasks

### Adding a New Django App

All Django management commands run inside the Docker container:

```bash
# Create new app (inside Docker)
make startapp NAME=my_app

# Add to INSTALLED_APPS in config/settings/base.py
INSTALLED_APPS = [
    ...
    'apps.my_app',
]

# Create migrations (inside Docker)
make makemigrations APP=my_app
make migrate
```

**Note:** Always use the Makefile commands. Do not run `python manage.py` commands locally.

### Adding GraphQL Queries/Mutations

1. **Create schema in app**:

   ```python
   # apps/my_app/schema.py
   import graphene

   class Query(graphene.ObjectType):
       hello = graphene.String()

       def resolve_hello(self, info):
           return "Hello, World!"
   ```

2. **Register in main schema**:

   ```python
   # config/schema.py
   from apps.my_app.schema import Query as MyAppQuery

   class Query(MyAppQuery, graphene.ObjectType):
       pass
   ```

3. **Generate schema**:
   ```bash
   make graphql-schema
   ```

## Troubleshooting

### Database Connection Issues

```bash
# Check PostgreSQL container is running
make docker-logs

# Reset database (WARNING: destroys data)
make db-reset
```

**Note:** PostgreSQL runs inside Docker. Do not attempt to use `pg_isready` locally - it won't
work since PostgreSQL is not installed on your machine.

### Migration Conflicts

All migration commands run inside Docker:

```bash
# List migrations (inside Docker)
make showmigrations

# Merge conflicting migrations (inside Docker)
make makemigrations

# Fake a migration if needed (inside Docker)
make migrate
```

**Note:** Do not run `python manage.py` commands locally. Always use the Makefile commands.

### Import Errors

If you get import errors:

```bash
# Verify Docker containers are running
make docker-up

# Check logs for errors
make docker-logs

# Restart containers
make docker-restart
```

**Important:** Do not attempt to activate a virtual environment with `source .venv/bin/activate`.
This project uses Docker containers, not local virtual environments. All Python code runs inside
the Docker container.

### Pre-commit Hook Failures

```bash
# Update hooks
pre-commit autoupdate

# Run specific hook
pre-commit run black --all-files

# Clear cache and retry
pre-commit clean
pre-commit install --install-hooks
```

### Port Already in Use

```bash
# Stop the current Docker containers
make docker-down

# Start fresh containers
make docker-up
```

**Note:** The Django development server runs inside Docker on port 8000. If you get a "port
already in use" error, stop the containers with `make docker-down` and restart them with
`make docker-up`. Do not attempt to run `python manage.py runserver` locally.

## Environment Variables Reference

| Variable               | Description         | Example                                          |
| ---------------------- | ------------------- | ------------------------------------------------ |
| `DEBUG`                | Enable debug mode   | `True` or `False`                                |
| `SECRET_KEY`           | Django secret key   | Random 50-character string                       |
| `ALLOWED_HOSTS`        | Allowed hostnames   | `localhost,127.0.0.1`                            |
| `DATABASE_URL`         | Database connection | `postgres://user:pass@host:5432/db`              |
| `REDIS_URL`            | Redis connection    | `redis://redis:6379/0`                           |
| `CORS_ALLOWED_ORIGINS` | CORS whitelist      | `http://localhost:3000`                          |
| `EMAIL_BACKEND`        | Email backend       | `django.core.mail.backends.console.EmailBackend` |
| `LOG_LEVEL`            | Logging level       | `INFO`, `DEBUG`, `WARNING`                       |

## Additional Resources

- **Django Documentation**: <https://docs.djangoproject.com/>
- **GraphQL Documentation**: <https://graphql.org/>
- **Project-specific docs**: See `/docs` directory

## Getting Help

- Check the `/docs` directory for detailed documentation
- Review the `DOTFILES.md` for configuration details
- Ask in the team chat or open an issue
- Consult with the backend team lead

## Next Steps

1. Read the project README
2. Review the architecture documentation in `/docs/PLANS`
3. Look at existing code in `/apps`
4. Pick a ticket from the backlog and start developing!

Happy coding!
