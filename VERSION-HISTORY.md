# Version History

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [Unreleased](#unreleased)
- [0.2.0 - 03/01/2026](#020---03012026)
- [0.1.0 - 03/01/2026](#010---03012026)

---

## [Unreleased]

### Technical Changes
- Nothing yet

---

## [0.2.0] - 03/01/2026

### Summary
Version management system initialisation. Added comprehensive versioning documentation, automated markdown header management, and established semantic versioning workflow for the project.

### Breaking Changes
None - Documentation and tooling improvements only.

### Database Migrations
None - No database changes.

### API Changes
None - No API changes.

### Files Changed

#### Version Management
| File | Changes |
|------|---------|
| `VERSION` | Created version file containing 0.2.0 |
| `VERSION-HISTORY.md` | Technical change log for developers with detailed file changes |
| `CHANGELOG.md` | Developer-focused summary following Keep a Changelog format |
| `RELEASES.md` | User-facing release notes with feature highlights |
| `package.json` | Updated version to 0.2.0 |

#### Markdown Documentation Headers
All markdown files (60+ files) updated with metadata headers:
- `README.md` - Project root documentation
- `.claude/CLAUDE.md` - Claude AI configuration
- `.claude/SYNTEK-GUIDE.md` - Syntek Dev Suite guide
- `.claude/commands/*.md` - Environment command references (4 files)
- `.github/README.md` - GitHub workflows documentation
- `.github/PULL_REQUEST_TEMPLATE.md` - PR template
- `.github/workflows/README.md` - CI/CD workflow documentation
- `.husky/README.md` - Git hooks documentation
- `.vscode/README.md` - VS Code configuration
- `.prettierrc.md` - Prettier configuration
- `api/README.md` - GraphQL API documentation
- `apps/README.md` - Django apps structure
- `config/README.md` - Configuration documentation
- `config/middleware/README.md` - Middleware documentation
- `config/settings/README.md` - Settings documentation
- `config/validators/README.md` - Validators documentation
- `docker/README.md` - Docker overview (+ 4 environment-specific files)
- `docs/README.md` - Documentation index
- `docs/DEVELOPER-SETUP.md` - Developer setup guide
- `docs/DOTFILES.md` - Configuration files reference
- `docs/VERSIONS.md` - Version management guide
- `docs/DEVOPS/README.md` - DevOps documentation
- `docs/DEVOPS/CICD-GITHUB-ACTIONS.MD` - GitHub Actions guide
- `docs/GDPR/*.md` - GDPR compliance documentation (2 files)
- `docs/LOGGING/*.md` - Logging documentation (2 files)
- `docs/METRICS/README.md` - Metrics documentation
- `docs/PM-INTEGRATION/*.MD` - ClickUp integration documentation (6 files)
- `docs/PRETTIER/*.md` - Prettier documentation (3 files)
- `docs/REVIEWS/*.md` - Code review documentation (2 files)
- `docs/SECURITY/*.md` - Security documentation (4 files)
- `docs/SYNTAX/*.md` - Linting documentation (2 files)
- `scripts/README.md` - Scripts overview
- `scripts/clickup/README.md` - ClickUp scripts
- `scripts/env/README.md` - Environment scripts
- `static/README.md` - Static assets
- `templates/README.md` - Django templates
- `tests/README.md` - Test documentation
- `media/README.md` - Media files

### Dependencies Updated
None - No dependency changes.

### Configuration Changes
| File | Key | Change |
|------|-----|--------|
| `package.json` | `version` | Updated from 0.1.0 to 0.2.0 |

### Performance Notes
None - Documentation changes only.

### Security Notes
None - No security changes.

### Documentation Standards
Implemented metadata header standard for all markdown files:
- **Last Updated**: Date in DD/MM/YYYY format (British format)
- **Version**: Semantic version matching project version
- **Maintained By**: Team/individual responsible
- **Language**: British English (en_GB)
- **Timezone**: Europe/London

### Version Management Workflow
Established semantic versioning workflow:
- VERSION file for build systems
- VERSION-HISTORY.md for technical details
- CHANGELOG.md for developer summary
- RELEASES.md for user-facing notes
- Automated markdown header updates
- British English and DD/MM/YYYY date formats

---

## [0.1.0] - 03/01/2026

### Summary
Initial release of the Django/Wagtail backend template with comprehensive multi-environment Docker setup, CI/CD pipelines, and developer tooling. This release establishes the foundational architecture for building scalable backend applications with Django, Wagtail CMS, PostgreSQL, and GraphQL.

### Breaking Changes
None - Initial release.

### Database Migrations
None - Initial setup with no migrations yet.

### API Changes
| Endpoint | Method | Change |
|----------|--------|--------|
| `/api/graphql` | POST | GraphQL endpoint initialised with security middleware |
| `/admin/` | GET | Wagtail admin interface available |

### Files Changed

#### Core Django Configuration
| File | Changes |
|------|---------|
| `config/settings/base.py` | Base Django settings with security headers, middleware, GraphQL, Wagtail integration |
| `config/settings/dev.py` | Development settings with debug toolbar, Mailpit, local database |
| `config/settings/test.py` | Test settings with in-memory database, coverage reporting |
| `config/settings/staging.py` | Staging settings with managed services, logging, security |
| `config/settings/production.py` | Production settings with strict security, performance optimisation |
| `config/urls.py` | URL routing with GraphQL, Wagtail, admin interfaces |
| `config/wsgi.py` | WSGI application configuration |
| `config/asgi.py` | ASGI application configuration for async support |
| `manage.py` | Django management command entry point |

#### API and Security
| File | Changes |
|------|---------|
| `api/schema.py` | GraphQL schema definition with sample queries |
| `api/security.py` | JWT authentication, rate limiting, query complexity analysis |
| `api/urls.py` | GraphQL endpoint routing |
| `config/middleware/security.py` | Security headers, CSP, HSTS middleware |
| `config/middleware/ratelimit.py` | Rate limiting middleware with Redis/Valkey backend |
| `config/middleware/audit.py` | Audit logging middleware for tracking requests |
| `config/validators/password.py` | Custom password validators with NCSC recommendations |

#### Docker Configuration
| File | Changes |
|------|---------|
| `docker/dev/Dockerfile` | Development container with hot reload, debugging tools |
| `docker/dev/docker-compose.yml` | Dev environment with PostgreSQL, Redis, Mailpit |
| `docker/test/Dockerfile` | Test container optimised for CI/CD |
| `docker/test/docker-compose.yml` | Test environment with isolated database |
| `docker/staging/Dockerfile` | Staging container with production-like setup |
| `docker/staging/docker-compose.yml` | Staging environment configuration |
| `docker/staging/entrypoint.sh` | Staging entrypoint with migrations, health checks |
| `docker/production/Dockerfile` | Production container with multi-stage build, security |
| `docker/production/docker-compose.yml` | Production environment configuration |
| `docker/production/entrypoint.sh` | Production entrypoint with comprehensive checks |
| `.dockerignore` | Docker build optimisation |
| `.hadolint.yaml` | Docker linting configuration |

#### CI/CD Pipelines
| File | Changes |
|------|---------|
| `.github/workflows/ci.yml` | Continuous integration pipeline with tests, linting, security scanning |
| `.github/workflows/pr-validation.yml` | Pull request validation with automated checks |
| `.github/workflows/deploy-staging.yml` | Automated staging deployment pipeline |
| `.github/workflows/deploy-production.yml` | Production deployment with approval gates |
| `.github/workflows/codeql.yml` | CodeQL security analysis |
| `.github/workflows/dependency-review.yml` | Dependency vulnerability scanning |
| `.github/workflows/clickup-sync.yml` | ClickUp task synchronisation |
| `.github/workflows/clickup-branch-sync.yml` | Branch-to-task linking automation |
| `.github/PULL_REQUEST_TEMPLATE.md` | PR template with checklist |
| `.github/CODEOWNERS` | Code ownership definitions |
| `.github/dependabot.yml` | Automated dependency updates |

#### Pre-commit Hooks
| File | Changes |
|------|---------|
| `.pre-commit-config.yaml` | Pre-commit hook configuration with 15+ checks |
| `.husky/pre-commit` | Git pre-commit hook runner |
| `.husky/commit-msg` | Commit message validation (Conventional Commits) |
| `.husky/pre-push` | Pre-push validation |
| `.husky/post-merge` | Post-merge dependency check |

#### Environment Configuration
| File | Changes |
|------|---------|
| `.env.example` | General environment template |
| `.env.dev.example` | Development environment variables |
| `.env.test.example` | Test environment variables |
| `.env.staging.example` | Staging environment variables |
| `.env.production.example` | Production environment variables |
| `.env.chrome.example` | Headless Chrome configuration for testing |
| `.envrc` | direnv configuration for automatic environment loading |

#### Python Quality Tools
| File | Changes |
|------|---------|
| `pyproject.toml` | Python project configuration with Black, isort, pytest, mypy, Ruff |
| `setup.cfg` | Additional Python tool configuration |
| `.pylintrc` | Pylint linting rules |
| `.flake8` | Flake8 linting configuration |
| `.bandit` | Bandit security scanning rules |
| `.coveragerc` | Coverage.py configuration with 80% threshold |
| `.python-version` | Python version specification (3.12.1) |

#### JavaScript and Markdown Formatting
| File | Changes |
|------|---------|
| `package.json` | Node.js dependencies for Prettier |
| `.prettierrc` | Prettier formatting configuration |
| `.prettierrc.md` | Markdown-specific Prettier rules |
| `.prettierignore` | Files to exclude from formatting |
| `.markdownlint.json` | Markdown linting rules |
| `.commitlintrc.json` | Commit message linting (Conventional Commits) |
| `.cspell.json` | Spell checking configuration |

#### Shell and Tool Configuration
| File | Changes |
|------|---------|
| `.shellcheckrc` | Shell script linting rules |
| `.yamllint.yml` | YAML linting configuration |
| `.tool-versions` | asdf tool version management |
| `.graphqlconfig` | GraphQL IDE configuration |

#### Git Configuration
| File | Changes |
|------|---------|
| `.gitignore` | Comprehensive ignore rules for Python, Node.js, Docker, IDEs |
| `.gitattributes` | Git attributes for line endings, diff handling |
| `.editorconfig` | Cross-editor coding style configuration |

#### Automation Scripts
| File | Changes |
|------|---------|
| `Makefile` | Common development tasks (test, lint, format, docker) |
| `scripts/env/dev.sh` | Development environment management script |
| `scripts/env/test.sh` | Test environment runner with coverage |
| `scripts/env/staging.sh` | Staging deployment script |
| `scripts/env/production.sh` | Production deployment script with safeguards |
| `scripts/setup-ci.sh` | CI/CD setup automation |
| `scripts/run-ci-locally.sh` | Local CI pipeline runner |
| `scripts/setup-prettier.sh` | Prettier setup automation |
| `scripts/clickup/clickup_client.py` | ClickUp API client |
| `scripts/clickup/sync_stories.py` | User story synchronisation |
| `scripts/clickup/pull_tasks.py` | Task pulling from ClickUp |

#### IDE Configuration
| File | Changes |
|------|---------|
| `.vscode/extensions.json` | Recommended VS Code extensions |
| `.claude/CLAUDE.md` | Claude AI project instructions |
| `.claude/SYNTEK-GUIDE.md` | Syntek Dev Suite usage guide |
| `.claude/commands/dev.md` | Development command reference |
| `.claude/commands/test.md` | Testing command reference |
| `.claude/commands/staging.md` | Staging command reference |
| `.claude/commands/production.md` | Production command reference |

#### Documentation
| File | Changes |
|------|---------|
| `README.md` | Project overview and quick start guide |
| `docs/README.md` | Documentation index |
| `docs/DEVELOPER-SETUP.md` | Comprehensive developer setup guide |
| `docs/VERSIONS.md` | Version management guide |
| `docs/DOTFILES.md` | Configuration file documentation |
| `docs/DEVOPS/README.md` | DevOps practices and deployment |
| `docs/DEVOPS/CICD-GITHUB-ACTIONS.MD` | GitHub Actions CI/CD guide |
| `docs/PM-INTEGRATION/README.MD` | ClickUp integration documentation |
| `docs/PM-INTEGRATION/SETUP-GUIDE.MD` | ClickUp setup instructions |
| `docs/PM-INTEGRATION/CLICKUP-INTEGRATION-SUMMARY.MD` | Integration summary |
| `docs/PM-INTEGRATION/QUICK-REFERENCE.MD` | Quick reference guide |
| `docs/PM-INTEGRATION/GITHUB-SECRETS.MD` | GitHub secrets configuration |
| `docs/PM-INTEGRATION/TROUBLESHOOTING.MD` | Troubleshooting guide |
| `docs/GDPR/README.md` | GDPR compliance overview |
| `docs/GDPR/COMPLIANCE-ASSESSMENT-2026-01-03.md` | GDPR assessment report |
| `docs/LOGGING/README.md` | Logging strategy |
| `docs/LOGGING/IMPLEMENTATION-PLAN-2026-01-03.md` | Logging implementation plan |
| `docs/SECURITY/README.md` | Security overview |
| `docs/SECURITY/SECURITY.md` | Security implementation guide |
| `docs/SECURITY/SECURITY-IMPLEMENTATION-SUMMARY.md` | Security summary |
| `docs/SECURITY/SECURITY-QUICK-REFERENCE.md` | Security quick reference |
| `docs/PRETTIER/README.md` | Prettier formatting overview |
| `docs/PRETTIER/PRETTIER-SETUP.md` | Prettier setup guide |
| `docs/PRETTIER/PRETTIER-IMPLEMENTATION-SUMMARY.md` | Prettier implementation summary |
| `docs/SYNTAX/README.md` | Linting and syntax overview |
| `docs/SYNTAX/LINTING-REPORT-2026-01-03.md` | Linting report |
| `docs/REVIEWS/README.md` | Code review guidelines |
| `docs/REVIEWS/CODE-REVIEW-2026-01-03.md` | Code review report |
| `docs/METRICS/README.md` | Self-learning metrics |
| `docs/METRICS/config.json` | Metrics configuration |
| `tests/README.md` | Test structure and guidelines |
| `api/README.md` | GraphQL API documentation |
| `apps/README.md` | Django apps structure guide |
| `config/README.md` | Configuration documentation |
| `config/settings/README.md` | Settings module documentation |
| `config/middleware/README.md` | Middleware documentation |
| `config/validators/README.md` | Validator documentation |
| `docker/README.md` | Docker setup documentation |
| `docker/dev/README.md` | Development Docker guide |
| `docker/test/README.md` | Test Docker guide |
| `docker/staging/README.md` | Staging Docker guide |
| `docker/production/README.md` | Production Docker guide |
| `scripts/README.md` | Scripts documentation |
| `scripts/env/README.md` | Environment scripts guide |
| `scripts/clickup/README.md` | ClickUp scripts documentation |
| `static/README.md` | Static assets documentation |
| `templates/README.md` | Django templates documentation |

### Dependencies Updated
| Package | Version | Notes |
|---------|---------|-------|
| `Django` | 5.0.x | Latest stable Django framework |
| `wagtail` | 6.x | Wagtail CMS |
| `strawberry-graphql` | Latest | GraphQL library |
| `psycopg[binary]` | 3.x | PostgreSQL adapter |
| `redis` | Latest | Redis client |
| `gunicorn` | Latest | WSGI HTTP server |
| `whitenoise` | Latest | Static file serving |
| `pytest` | Latest | Testing framework |
| `pytest-django` | Latest | Django pytest plugin |
| `pytest-cov` | Latest | Coverage plugin |
| `black` | Latest | Code formatter |
| `ruff` | Latest | Linter |
| `mypy` | Latest | Type checker |
| `prettier` | ^3.4.2 | JavaScript/Markdown formatter |

### Configuration Changes
| File | Key | Change |
|------|-----|--------|
| `config/settings/base.py` | `ALLOWED_HOSTS` | Configured per environment |
| `config/settings/base.py` | `DATABASES` | PostgreSQL with environment variables |
| `config/settings/base.py` | `CACHES` | Redis/Valkey caching backend |
| `config/settings/base.py` | `MIDDLEWARE` | Security, rate limiting, audit logging |
| `config/settings/base.py` | `INSTALLED_APPS` | Django, Wagtail, GraphQL, custom apps |
| `.env.*.example` | All | Environment-specific configuration templates |

### Performance Notes
- Multi-stage Docker builds reduce image size by ~60%
- Redis caching for session and application data
- PostgreSQL connection pooling configured
- Static file compression with WhiteNoise
- GraphQL query complexity limiting to prevent abuse

### Security Notes
- JWT authentication for API access
- Rate limiting on all endpoints (100 requests/hour default)
- Content Security Policy headers
- HSTS enabled in production
- Secrets management via environment variables
- Bandit security scanning in CI
- CodeQL analysis enabled
- Dependency vulnerability scanning
- Pre-commit hooks prevent committing secrets
- Password validation following NCSC guidelines

### Infrastructure
- **Containers**: Docker Compose for all environments
- **Database**: PostgreSQL 16 (containerised in dev/test, managed in staging/prod)
- **Cache**: Redis or Valkey
- **Email**: Mailpit for dev/test, SMTP for staging/prod
- **CI/CD**: GitHub Actions with automated deployment
- **Project Management**: ClickUp integration with automatic task sync

### Development Workflow
- Branch naming: `us{number}/feature-name` linked to ClickUp tasks
- Commit format: Conventional Commits with automated validation
- Pre-commit hooks: 15+ checks including formatting, linting, security
- Automated testing with 80% coverage requirement
- Pull request template with comprehensive checklist
- Code review automation with CODEOWNERS

### Testing
- Pytest framework with Django plugin
- Unit, integration, and GraphQL tests
- Coverage reporting with 80% minimum threshold
- Isolated test database per environment
- Headless Chrome for browser testing
- Local CI pipeline runner for pre-push validation

### Documentation
- Comprehensive README files in all major directories
- Developer setup guide with step-by-step instructions
- API documentation with example queries
- Security implementation guide
- GDPR compliance assessment
- Deployment guides for all environments
- Troubleshooting documentation
