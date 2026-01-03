# backend_template

A reusable backend template using Django, Wagtail, PostgreSQL and GraphQL with environment-specific
setups for dev, staging, production, and test.

**Important:** All development happens inside Docker containers. You do not need to install Python,
PostgreSQL, or any other dependencies locally. Simply use the environment scripts in `scripts/env/`
to run everything inside Docker.

## Table of Contents

- [backend_template](#backend_template)
  - [Table of Contents](#table-of-contents)
  - [Stack](#stack)
  - [Features](#features)
  - [Project Structure](#project-structure)
  - [Quick Start](#quick-start)
    - [Prerequisites](#prerequisites)
    - [Development](#development)
    - [Testing](#testing)
  - [Documentation](#documentation)
    - [Getting Started](#getting-started)
    - [Code Quality \& Reviews](#code-quality--reviews)
    - [Architecture \& Operations](#architecture--operations)
    - [Compliance \& Legal](#compliance--legal)
    - [Code Formatting](#code-formatting)
    - [Project Directory Documentation](#project-directory-documentation)
  - [Contributing](#contributing)
    - [Development Workflow](#development-workflow)
    - [Code Standards](#code-standards)
  - [License](#license)

## Stack

| Component   | Version          |
| ----------- | ---------------- |
| Python      | 3.14             |
| Django      | 5.2              |
| Wagtail CMS | 7                |
| PostgreSQL  | 18.1             |
| Node.js     | 24.12.0          |
| GraphQL     | (via Strawberry) |

## Features

- Separate Docker containers for each environment (dev, staging, prod, test)
- Staging and Production use managed PostgreSQL (AWS RDS or DigitalOcean)
- Redis or Valkey for caching
- Mailpit for email simulation in dev/test environments
- GraphQL API with security extensions
- Wagtail CMS integration
- Comprehensive security features
- GDPR compliance tools
- Structured logging system
- GraphQL query protection (depth, complexity, introspection control)
- Rate limiting and audit logging

## Project Structure

```
backend_template/
├── .claude/                 # Claude Code configuration
├── .github/                 # GitHub configuration (workflows, templates, CodeQL)
├── .husky/                  # Git hooks
├── .vscode/                 # VS Code workspace settings
├── api/                     # GraphQL API
├── apps/                    # Django applications
├── config/                  # Django project configuration
│   ├── middleware/          # Custom middleware
│   ├── settings/            # Environment-specific settings
│   └── validators/          # Custom validators
├── docker/                  # Docker configuration per environment
│   ├── dev/                 # Development containers
│   ├── test/                # Test containers
│   ├── staging/             # Staging containers
│   └── production/          # Production containers
├── docs/                    # Project documentation
├── media/                   # User-uploaded media files
├── scripts/                 # Helper scripts and utilities
│   ├── env/                 # Environment-specific run scripts
│   └── clickup/             # ClickUp project management integration
├── static/                  # Static files (CSS, JS, images)
├── templates/               # Django HTML templates
├── tests/                   # Test suite
├── manage.py                # Django management script
├── pyproject.toml           # Python project configuration
├── Makefile                 # Quick commands reference
└── README.md                # This file
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git configured with valid credentials

### Development

```bash
# Start the development environment
./scripts/env/dev.sh start

# Run migrations
./scripts/env/dev.sh migrate

# Create a superuser
./scripts/env/dev.sh createsuperuser

# View available URLs and services
./scripts/env/dev.sh urls

# Access the application
# Web: http://localhost:8000
# Admin: http://localhost:8000/admin
# Mailpit: http://localhost:8025
```

### Testing

```bash
# Run full test suite
./scripts/env/test.sh run

# Run with coverage
./scripts/env/test.sh coverage

# Run linting checks
./scripts/env/test.sh lint
```

For more detailed setup instructions, see [docs/DEVELOPER-SETUP.md](docs/DEVELOPER-SETUP.md).

## Documentation

The documentation is organized by topic in the `docs/` folder. Here's a quick index:

### Getting Started

- [Developer Setup Guide](docs/DEVELOPER-SETUP.md) - Complete setup instructions
- [Configuration Files](docs/DOTFILES.md) - Understanding project configuration files
- [Versions and Dependencies](docs/VERSIONS.md) - Complete version information

### Code Quality & Reviews

- [Code Review Reports](docs/REVIEWS/) - Security and quality code reviews
- [Linting & Syntax](docs/SYNTAX/) - Code quality checks and analysis
- [Security Documentation](docs/SECURITY/) - Comprehensive security guide

### Architecture & Operations

- [DevOps & CI/CD](docs/DEVOPS/) - Deployment and pipeline documentation
- [Logging System](docs/LOGGING/) - Structured logging implementation
- [Database Documentation](docs/DATABASE/) - Schema and migrations

### Compliance & Legal

- [GDPR Compliance](docs/GDPR/) - Data protection documentation
- [Project Management Integration](docs/PM-INTEGRATION/) - ClickUp and GitHub integration

### Code Formatting

- [Prettier Setup](docs/PRETTIER/) - Code formatting configuration

### Project Directory Documentation

- [.claude/](.claude/README.md) - Claude Code configuration
- [.github/](.github/README.md) - GitHub workflows and configuration
- [.husky/](.husky/README.md) - Git hooks setup
- [.vscode/](.vscode/README.md) - VS Code configuration
- [api/](api/README.md) - GraphQL API structure
- [apps/](apps/README.md) - Django applications
- [config/](config/README.md) - Project configuration
- [docker/](docker/README.md) - Docker setup per environment
- [scripts/](scripts/README.md) - Helper scripts and utilities
- [templates/](templates/README.md) - Django templates
- [static/](static/README.md) - Static files (CSS, JS, images)
- [tests/](tests/README.md) - Test suite organization

## Contributing

This project follows a structured development workflow. Refer to
[docs/GUIDES/CONTRIBUTING.md](docs/GUIDES/CONTRIBUTING.md) for detailed
contribution guidelines.

### Development Workflow

1. Create a feature branch: `git checkout -b us{number}/feature-name`
2. Make your changes and commit: `git commit -m "Clear commit message"`
3. Run tests locally: `./scripts/env/test.sh run`
4. Push to remote: `git push origin us{number}/feature-name`
5. Create a Pull Request on GitHub

### Code Standards

This project enforces:

- **Python Style:** Black, isort, flake8, mypy
- **Django Standards:** As defined in CLAUDE.md
- **Docstring Format:** Google-style docstrings
- **Type Hints:** Required on all function signatures
- **Security:** Bandit and Django security checks

Run `./scripts/env/test.sh lint` to check code quality locally.

## License

[License information to be added]
