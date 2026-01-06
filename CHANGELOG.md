# Changelog

**Last Updated**: 06/01/2026
**Version**: 0.3.1
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
- [0.3.1 - 06/01/2026](#031---06012026)
- [0.3.0 - 06/01/2026](#030---06012026)
- [0.2.0 - 03/01/2026](#020---03012026)
- [0.1.0 - 03/01/2026](#010---03012026)

---

## [Unreleased]

### Added

- Nothing yet

---

## [0.3.1] - 06/01/2026

### Added

- Python package lock file (`uv.lock`) for reproducible builds across all environments

### Fixed

- Markdown table alignment in `.claude/CLAUDE.md` (test naming conventions and coverage tables)
- Extra blank lines in all user story documentation files (`docs/STORIES/*.md`)
- Blank line consistency in CI workflow review documentation
- Missing trailing newline in `config/clickup-sprint-mapping.json`

### Changed

- Added clarifying comment in `.gitignore` about `uv.lock` requirement

---

## [0.3.0] - 06/01/2026

### Added

**Platform Architecture**
- Comprehensive CMS platform architecture documentation (16-phase development plan)
- Multi-repository architecture specification (backend, UI library, web, mobile)
- Design token system architecture
- Content branching workflow design (git-like for content)
- 9 site template specifications

**Sprint and User Story Management**
- Sprint documentation structure in `docs/SPRINTS/`
- User story documentation structure in `docs/STORIES/`
- Sprint-to-ClickUp mapping configuration
- Story-to-ClickUp mapping configuration
- Integration status tracking documentation

**ClickUp Integration Enhancements**
- Enhanced ClickUp API client with retry logic and error handling
- Automated sprint synchronisation script
- Enhanced user story synchronisation script
- Custom field mapping (story points, sprint, priority)
- Branch name to task ID linking automation
- Commit message to task comment synchronisation
- Bidirectional status updates

**Git Workflow Plugin**
- Comprehensive Git workflow management plugin for Claude
- Automated branch creation following `us###/description` pattern
- Multi-environment branch strategy management (testing → dev → staging → main)
- Pre-commit version management integration
- Pull request template generation
- Semantic versioning analysis
- Changelog automation
- Commit message validation and formatting
- GitHub CLI integration for PR operations

**Claude Plugins**
- `git-tool.py` for Git workflow automation
- `version-tool.py` for version detection
- `project-tool.py` for project information queries

**Environment Configuration**
- ClickUp workspace, space, folder, and list ID variables in all `.env.*.example` files
- Environment variable-based ClickUp configuration (removes hardcoded IDs)

### Changed

**CI/CD and Workflows**
- Enhanced dependency review workflow with improved security scanning
- Updated CodeQL configuration for better code analysis
- Updated CODEOWNERS for new documentation structure
- Enhanced pull request template with ClickUp integration

**Configuration and Tooling**
- Updated `pyproject.toml` with new tool configurations
- Updated `package.json` scripts and dependencies (version 0.3.0)
- Updated `.python-version` to Python 3.11
- Updated `.pylintrc` linting rules
- Updated `.hadolint.yaml` Docker linting configuration
- Updated `.pre-commit-config.yaml` for new file structure
- Updated `Makefile` with ClickUp synchronisation targets

**Docker Configuration**
- Enhanced development service definitions and volume mappings
- Updated test database configuration
- Improved staging deployment readiness checks
- Enhanced production security and performance settings

**Automation Scripts**
- Enhanced `dev.sh` with new development commands
- Improved `test.sh` with better test coverage reporting
- Enhanced `staging.sh` with deployment validation
- Improved `production.sh` with safety checks and confirmations
- Updated `.husky/post-merge` for dependency synchronisation

**Documentation**
- Standardised all markdown file extensions to lowercase `.md` (SETUP-GUIDE.md format)
- Updated all documentation with platform architecture references
- Enhanced documentation across all modules (60+ files)
- Improved cross-referencing between related documents
- Updated version headers and last modified dates throughout

**Code Quality**
- Cleaned up Django configuration imports and deprecated patterns
- Improved password validator documentation
- Enhanced settings module organisation
- Removed dead code and unused variables

### Deprecated

None - All changes are additive.

### Removed

- Deprecated URL configuration patterns in `config/urls.py`
- Unused import statements from Django settings

### Fixed

None - No bug fixes in this release.

### Security

- Environment variable-based ClickUp configuration prevents ID exposure in git
- Enhanced pre-commit hooks for new file structure
- Improved CodeQL analysis configuration for better security scanning

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
