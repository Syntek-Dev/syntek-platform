# backend_template

**Last Updated**: 06/01/2026
**Version**: 0.3.2
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

A comprehensive Django CMS platform backend providing content management, design tokens,
multi-tenancy, SaaS integrations, and enterprise-grade security. Part of the Syntek CMS Platform
architecture supporting web and mobile applications.

**Platform Architecture:** This backend is one component of a multi-repository CMS platform.
See [docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md](docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md) for the
complete architectural plan including all 16 development phases.

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

| Component  | Version          |
| ---------- | ---------------- |
| Python     | 3.14             |
| Django     | 5.2              |
| PostgreSQL | 18.1             |
| Node.js    | 24.12.0          |
| GraphQL    | (via Strawberry) |

## Features

### Core Platform Features

- **Multi-Repository Architecture:** Integrates with ui_design, frontend_web, frontend_mobile
- **Multi-Tenancy:** Organisation-based isolation with encrypted data
- **Design Token System:** Database-driven theming for consistent branding across platforms
- **Content Management:** Pure Django CMS with block-based content and JSON structure
- **Content Branching:** Git-like workflow (feature → testing → dev → staging → production)
- **9 Site Templates:** E-commerce, Blog, Corporate, Church, Charity, SaaS, Sole Trader,
  Estate Agent, Single Page
- **GraphQL API:** Strawberry-based with query protection, depth limiting, complexity analysis
- **AI Integration:** Anthropic Claude for content assistance, SEO, code help (planned)
- **SaaS Integrations:** Email, Cloud documents, Password manager (planned)

### Infrastructure & Security

- Separate Docker containers for each environment (dev, staging, prod, test)
- Staging and Production use managed PostgreSQL (AWS RDS or DigitalOcean)
- Redis or Valkey for caching and session storage
- Mailpit for email simulation in dev/test environments
- 2FA authentication with TOTP
- Comprehensive audit logging with encrypted IP addresses
- Environment variable encryption and management
- GDPR compliance tools
- Structured logging system with Sentry integration
- Rate limiting and security middleware

**See:** [docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md](docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md) for
complete platform architecture and phased development plan.

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

### Platform Architecture

- **[CMS Platform Plan](docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md)** - **START HERE** -
  Comprehensive architectural plan for the entire CMS platform including all 16 development phases,
  database schema, GraphQL API contracts, security architecture, and multi-repository structure

### Getting Started

- [Developer Setup Guide](docs/DEVELOPER-SETUP.md) - Complete setup instructions
- [Configuration Files](docs/DOTFILES.md) - Understanding project configuration files
- [Versions and Dependencies](docs/VERSIONS.md) - Complete version information

### Code Quality & Reviews

- [Code Review Reports](docs/REVIEWS/) - Security and quality code reviews
- [Linting & Syntax](docs/SYNTAX/) - Code quality checks and analysis
- [Security Documentation](docs/SECURITY/) - Comprehensive security guide

### Architecture & Operations

- [Platform Architecture](docs/ARCHITECTURE/) - **CMS platform design and phases**
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
