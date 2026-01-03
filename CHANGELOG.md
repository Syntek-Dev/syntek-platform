# Changelog

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Table of Contents

- [Unreleased](#unreleased)
- [0.2.0 - 03/01/2026](#020---03012026)
- [0.1.0 - 03/01/2026](#010---03012026)

---

## [Unreleased]

### Added
- Nothing yet

---

## [0.2.0] - 03/01/2026

### Added

**Version Management System**
- VERSION file containing semantic version number (0.2.0)
- VERSION-HISTORY.md for technical change logs with detailed file changes
- CHANGELOG.md following Keep a Changelog format for developer summaries
- RELEASES.md for user-facing release notes and feature highlights

**Documentation Standards**
- Metadata headers added to all 60+ markdown files in the project
- Headers include: Last Updated, Version, Maintained By, Language, Timezone
- British English (en_GB) language specification
- Europe/London timezone specification
- DD/MM/YYYY date format standardisation

**Workflow Improvements**
- Established semantic versioning workflow (MAJOR.MINOR.PATCH)
- Documentation update automation for version bumps
- Consistent version tracking across all project files

### Changed
- Updated package.json version from 0.1.0 to 0.2.0
- All markdown files now include standardised metadata headers

### Deprecated
None - Documentation improvements only.

### Removed
None - No files removed.

### Fixed
None - No bug fixes.

### Security
None - No security changes.

---

## [0.1.0] - 03/01/2026

### Added

**Core Framework**
- Django 5.0.x project structure with environment-specific settings (dev, test, staging, production)
- Wagtail CMS integration with admin interface
- GraphQL API with Strawberry GraphQL
- PostgreSQL database configuration for all environments
- Redis/Valkey caching backend

**Docker Infrastructure**
- Multi-environment Docker setup with isolated containers
- Development containers with hot reload and debugging tools
- Test containers optimised for CI/CD
- Staging containers with production-like configuration
- Production containers with multi-stage builds and security hardening
- Docker Compose configurations for all environments

**CI/CD Pipelines**
- GitHub Actions CI pipeline with automated testing, linting, and security scanning
- Pull request validation workflow
- Automated staging deployment pipeline
- Production deployment workflow with approval gates
- CodeQL security analysis
- Dependency vulnerability scanning with Dependabot
- ClickUp task synchronisation automation

**Security**
- JWT authentication for API endpoints
- Rate limiting middleware with Redis backend
- Security headers middleware (CSP, HSTS, X-Frame-Options)
- Audit logging middleware for request tracking
- Custom password validators following NCSC guidelines
- GraphQL query complexity analysis
- Bandit security scanning in pre-commit hooks
- Secret detection in pre-commit hooks

**Developer Tooling**
- Pre-commit hooks with 15+ automated checks
- Husky git hooks for commit message validation
- Conventional Commits enforcement
- Black code formatting
- Ruff linting
- Mypy type checking
- Pylint, Flake8, and isort configuration
- Prettier for JavaScript and Markdown formatting
- ShellCheck for shell script validation
- Hadolint for Dockerfile linting
- CSpell for spell checking

**Automation Scripts**
- Environment management scripts (dev.sh, test.sh, staging.sh, production.sh)
- Makefile with common development tasks
- CI setup automation script
- Local CI pipeline runner
- Prettier setup script
- ClickUp integration scripts for task management

**Testing**
- Pytest framework with Django plugin
- Coverage reporting with 80% minimum threshold
- Isolated test database configuration
- Headless Chrome setup for browser testing
- Test structure documentation

**Project Management**
- ClickUp integration with automatic task synchronisation
- Branch naming convention linked to user stories (us{number}/feature-name)
- Pull request template with comprehensive checklist
- CODEOWNERS configuration for code review automation

**Documentation**
- Comprehensive README files in all major directories
- Developer setup guide with step-by-step instructions
- Docker setup documentation for all environments
- CI/CD pipeline documentation
- ClickUp integration guide with setup and troubleshooting
- Security implementation guide
- GDPR compliance assessment
- Logging implementation plan
- Code review guidelines and reports
- Prettier formatting guide
- Syntax and linting documentation
- Version management guide

**IDE Configuration**
- VS Code recommended extensions list
- Claude AI project instructions and command reference
- EditorConfig for cross-editor consistency
- GraphQL IDE configuration

**Environment Configuration**
- Environment variable templates for all environments (.env.*.example)
- direnv configuration for automatic environment loading
- Environment-specific Docker Compose files
- Separated development, test, staging, and production settings

### Changed
None - Initial release.

### Deprecated
None - Initial release.

### Removed
None - Initial release.

### Fixed
None - Initial release.

### Security
- Implemented JWT authentication for API access
- Added rate limiting to prevent abuse (100 requests/hour default)
- Configured security headers (CSP, HSTS, X-Frame-Options)
- Enabled CodeQL security analysis in CI
- Added Bandit security scanning in pre-commit hooks
- Configured Dependabot for automated vulnerability patching
- Implemented secret detection in pre-commit hooks
- Added password validation following NCSC guidelines
