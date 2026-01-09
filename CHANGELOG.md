# Changelog

**Last Updated**: 09/01/2026
**Version**: 0.6.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

## Overview

This changelog documents all notable changes to the backend template project in reverse chronological order. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). For user-facing release notes, see [RELEASES.md](RELEASES.md). For detailed technical changes, see [VERSION-HISTORY.md](VERSION-HISTORY.md).

---

## Table of Contents

- [Changelog](#changelog)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [\[Unreleased\]](#unreleased)
    - [Added](#added)
  - [\[0.6.0\] - 08/01/2026](#060---08012026)
    - [Added](#added-1)
    - [Changed](#changed)
    - [Security](#security)
  - [\[0.5.0\] - 08/01/2026](#050---08012026)
    - [Added](#added-2)
    - [Changed](#changed-1)
    - [Fixed](#fixed)
    - [Security](#security-1)
  - [\[0.4.1\] - 08/01/2026](#041---08012026)
    - [Added](#added-3)
    - [Changed](#changed-2)
    - [Fixed](#fixed-1)
    - [Security](#security-2)
  - [\[0.4.0\] - 07/01/2026](#040---07012026)
    - [Added](#added-4)
    - [Changed](#changed-3)
    - [Fixed](#fixed-2)
    - [Security](#security-3)
  - [\[0.3.3\] - 07/01/2026](#033---07012026)
    - [Added](#added-5)
    - [Changed](#changed-4)
    - [Removed](#removed)
    - [Fixed](#fixed-3)
  - [\[0.3.2\] - 06/01/2026](#032---06012026)
    - [Added](#added-6)
    - [Fixed](#fixed-4)
    - [Changed](#changed-5)
  - [\[0.3.1\] - 06/01/2026](#031---06012026)
    - [Added](#added-7)
    - [Fixed](#fixed-5)
    - [Changed](#changed-6)
  - [\[0.3.0\] - 06/01/2026](#030---06012026)
    - [Added](#added-8)
    - [Changed](#changed-7)
    - [Deprecated](#deprecated)
    - [Removed](#removed-1)
    - [Fixed](#fixed-6)
    - [Security](#security-4)
  - [\[0.2.0\] - 03/01/2026](#020---03012026)
    - [Added](#added-9)
    - [Changed](#changed-8)
    - [Deprecated](#deprecated-1)
    - [Removed](#removed-2)
    - [Fixed](#fixed-7)
    - [Security](#security-5)
  - [\[0.1.0\] - 03/01/2026](#010---03012026)
    - [Added](#added-10)
    - [Changed](#changed-9)
    - [Deprecated](#deprecated-2)
    - [Removed](#removed-3)
    - [Fixed](#fixed-8)
    - [Security](#security-6)


---

## [Unreleased]

### Added

- Nothing yet

---

## [0.6.0] - 09/01/2026

### Added

- **GraphQL API Implementation (US-001 Phase 3):**
  - Complete GraphQL schema with Strawberry GraphQL
  - Full implementation of authentication mutations: `register`, `login`, `logout`, `requestPasswordReset`, `resetPassword`, `verifyEmail`
  - User queries: `me`, `user`, `users`, `auditLogs` with organisation boundary enforcement
  - Authentication types: `AuthPayload`, `UserType`, `AuditLogType`, input types for all mutations
  - CSRF protection middleware for mutations (C4 requirement)
  - GraphQL security extensions: query depth limiting, complexity analysis, introspection control
  - Permission system for organisation-based access control
  - **DataLoaders for N+1 query prevention (H2 requirement):**
    - `UserLoader` for batch user loading
    - `OrganisationLoader` for batch organisation loading
    - `AuditLogLoader` for batch audit log loading
  - **Standardised error handling (H4 requirement):**
    - Custom error types: `AuthenticationError`, `ValidationError`, `PermissionError`
    - Error code enumeration with unique codes for all error scenarios
    - Consistent error messages for user enumeration prevention (M7)
  - **Authentication middleware:**
    - JWT token validation
    - User authentication context
    - Organisation boundary enforcement
- **Comprehensive Test Suite:**
  - Unit tests for auth mutations, user queries, permissions, CSRF middleware, DataLoaders
  - Integration tests for complete GraphQL authentication flow
  - End-to-end tests for user registration workflow
  - Enhanced test factories with proper field mappings
  - Test markers: `security` and `performance` for targeted test execution
- **Code Quality Improvements:**
  - Added Flake8 linting to development scripts
  - Enhanced pytest configuration with new test markers
  - Improved code documentation across all modules

### Changed

- **GraphQL mutations and queries:** Upgraded from stubs to full implementations
- **Test factories:** Updated to match current model schema
- **Documentation:** Updated across all domains (Auth, Backend, Debug, GDPR, Logging, QA, Reviews, Security)
- **Settings:** Enhanced security configurations for production, staging, and test environments
- Development scripts now include Flake8 in lint checks

### Security

- **C4 (CSRF Protection):** CSRF middleware enforces CSRF token validation for all mutations
- **C5 (Email Verification):** Email verification enforcement implemented in login mutation
- **M7 (User Enumeration Prevention):** Standardised error messages prevent user enumeration attacks
- **H2 (N+1 Query Prevention):** DataLoaders implemented for efficient batch loading
- **H4 (Error Standardisation):** Consistent error codes and messages across API
- **H10 (IP Encryption):** IP addresses encrypted in audit logs with decryption on query

---

## [0.5.0] - 08/01/2026

### Added

- Encryption utilities for sensitive data (token hashing with HMAC-SHA256)
- Authentication services for user registration, login, and password reset
- Token service for managing authentication tokens
- Email service for sending verification and notification emails
- Password reset service with secure token generation
- Audit service for comprehensive activity logging
- Enhanced security features with token hashing and IP encryption
- Comprehensive documentation for US-001 Phase 2 completion

### Changed

- Updated models for enhanced security features
- Improved test coverage for authentication and security functionality
- Enhanced development and documentation scripts
- Updated settings and validation for US-001 implementation
- Updated dependencies to support authentication features

### Fixed

- None - This is a feature addition release

### Security

- Enhanced token security with HMAC-SHA256 hashing for all authentication tokens
- Added encryption utilities for protecting sensitive data
- Improved IP address encryption in audit logs

---

## [0.4.1] - 08/01/2026

### Added

- Database indexes for AuditLog model (user_id, action, timestamp) for improved query performance
- Database indexes for SessionToken model (token, expires_at) for faster authentication checks
- `is_expired()` helper method to SessionToken model for cleaner expiry validation

### Changed

- Consolidated 13 fragmented documentation files into organised review structure
- Reorganised US-001 documentation into clear directory hierarchy
- Updated version headers across all US-001 documentation files
- Clarified configuration comments in environment variable examples

### Fixed

- None - This is a performance and organisation release

### Security

- Database indexes improve performance without exposing additional data
- Helper methods maintain consistent security checks across token validation

---

## [0.4.0] - 07/01/2026

### Added

- Complete core app implementation for user authentication (US-001 Phase 1)
- User model with email-based authentication, 2FA support, and organisation relationships
- Organisation model for multi-tenancy with encrypted data fields
- Email verification token system with HMAC-SHA256 hashing
- Password reset token system with expiration and validation
- Two-factor authentication (2FA) token system with backup codes
- Audit log model for comprehensive activity tracking
- Failed login attempt tracking for security monitoring
- User session management with device and location tracking
- Admin interfaces for all core models with organisation filtering
- Authentication services (registration, login, password reset, 2FA)
- Utility functions for token generation, email sending, IP encryption
- 10+ custom password validators following NCSC guidelines
- IP allowlist middleware for enhanced security
- Comprehensive test framework with pytest, BDD (pytest-bdd), and factories
- 29 test files covering unit, integration, BDD, E2E, and GraphQL tests
- Factory Boy factories for test data generation
- BDD feature files and step definitions for authentication workflows

### Changed

- Updated Django settings for core app integration
- Enhanced middleware configuration with audit logging and IP allowlist
- Updated pyproject.toml with core app dependencies (django-otp, qrcode, cryptography)
- Enhanced environment scripts (test.sh, staging.sh, production.sh) with test commands
- Updated environment variable examples with security and testing configuration
- Updated Docker configurations for test and production environments
- Enhanced .gitignore and .dockerignore for test artifacts

### Fixed

- None - Initial core app implementation

### Security

- Implemented 10+ password validators (length, complexity, common passwords, personal info, reuse, breach check)
- Added HMAC-SHA256 token hashing for all authentication tokens
- Implemented IP allowlist middleware for restricted access
- Added audit logging for all authentication actions
- Encrypted sensitive fields (IP addresses) in database
- Implemented rate limiting for authentication endpoints
- Added account lockout after failed login attempts

---

## [0.3.3] - 07/01/2026

### Added

- Comprehensive US-001 User Authentication implementation plan (203KB)
- Architecture review documentation for US-001 (65KB)
- Security analysis and hardening documentation for US-001 (43KB)
- New documentation directories: PLANS, ARCHITECTURE/US-001, SECURITY/US-001, CODE-REVIEW, BACKEND, DATABASE, GDPR/US-001, QA, REVIEWS/US-001, TESTS
- Implementation details for 6 Critical, 15 High, and 12 Medium priority security issues
- Coverage for all 27 edge cases in authentication workflow
- Token hashing consistency fixes (HMAC-SHA256)
- 7 implementation phases with integrated security fixes
- Comprehensive API specifications for authentication endpoints

### Changed

- Updated markdown linting configuration to exclude `.venv` directory
- Enhanced markdownlint.json for better documentation validation
- Updated docs/README.md with new documentation structure references
- Updated US-004 Organisation Setup story details

### Removed

- Consolidated docs/REVIEWS/CODE-REVIEW-2026-01-03.md into US-001 structure
- Removed docs/REVIEWS/REVIEW-HUSKY-HOOKS-UPDATE-2026-01-06.MD (reorganised)

### Fixed

- Package.json markdown linting now excludes virtual environment directory
- Markdownlint configuration updated for new project structure

---

## [0.3.2] - 06/01/2026

### Added

- Prettier validation to pre-commit hook (JavaScript, TypeScript, JSON, YAML formatting)
- Markdownlint validation to pre-commit hook (markdown formatting)
- uv.lock tracking to post-merge hook (dependency change notifications)
- Migration reminder to post-merge hook
- Comprehensive review document for hook changes (`docs/REVIEWS/REVIEW-HUSKY-HOOKS-UPDATE-2026-01-06.MD`)

### Fixed

- Replaced flake8 with ruff in `.husky/pre-commit` hook (consistency with CI)
- Replaced flake8 with ruff in `.husky/pre-push` hook (consistency with CI)
- Replaced flake8 with ruff in `.pre-commit-config.yaml` (consistency with CI)
- F841 unused variable errors in 13 plugin files (`.claude/plugins/*.py`)
- F841 unused variable errors in 6 ClickUp script files (`scripts/clickup/*.py`)
- F841 unused variable errors in 4 API/middleware files
- E741 ambiguous variable name in `git-tool.py` (renamed `l` to `line`)
- B007 unused loop variable in `project-tool.py` (prefixed with underscore)

### Changed

- Optimised pre-commit hook to check only staged files (performance improvement)
- Enhanced pre-push hook with better validation checks
- Updated `.claude/CLAUDE.md` to include `.claude/plugins/` directory in project structure

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
