# Version History

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [Version History](#version-history)
  - [Table of Contents](#table-of-contents)
  - [\[Unreleased\]](#unreleased)
    - [Technical Changes](#technical-changes)
  - [\[0.3.3\] - 07/01/2026](#033---07012026)
    - [Summary](#summary)
    - [Breaking Changes](#breaking-changes)
    - [Database Migrations](#database-migrations)
    - [API Changes](#api-changes)
    - [Files Changed](#files-changed)
      - [Documentation (New)](#documentation-new)
      - [Documentation (Updated)](#documentation-updated)
      - [Documentation (Removed)](#documentation-removed)
      - [Configuration](#configuration)
    - [Key Documentation Additions](#key-documentation-additions)
    - [Technical Details](#technical-details)
    - [Migration Notes](#migration-notes)
    - [Testing Notes](#testing-notes)
    - [Deployment Notes](#deployment-notes)
  - [\[0.3.2\] - 06/01/2026](#032---06012026)
    - [Summary](#summary-1)
    - [Breaking Changes](#breaking-changes-1)
    - [Database Migrations](#database-migrations-1)
    - [API Changes](#api-changes-1)
    - [Files Changed](#files-changed-1)
      - [Git Hooks (Husky)](#git-hooks-husky)
      - [Ruff Linting Fixes (Plugin Files)](#ruff-linting-fixes-plugin-files)
      - [Ruff Linting Fixes (ClickUp Scripts)](#ruff-linting-fixes-clickup-scripts)
      - [Ruff Linting Fixes (API and Middleware)](#ruff-linting-fixes-api-and-middleware)
      - [Documentation](#documentation)
    - [Dependencies](#dependencies)
    - [Developer Notes](#developer-notes)
    - [Migration Instructions](#migration-instructions)
  - [\[0.3.1\] - 06/01/2026](#031---06012026)
    - [Summary](#summary-2)
    - [Breaking Changes](#breaking-changes-2)
    - [Database Migrations](#database-migrations-2)
    - [API Changes](#api-changes-2)
    - [Files Changed](#files-changed-2)
      - [Documentation Formatting (Markdown Lint Fixes)](#documentation-formatting-markdown-lint-fixes)
      - [Build and Configuration](#build-and-configuration)
    - [Dependencies](#dependencies-1)
    - [Developer Notes](#developer-notes-1)
    - [Migration Instructions](#migration-instructions-1)
  - [\[0.3.0\] - 06/01/2026](#030---06012026)
    - [Summary](#summary-3)
    - [Breaking Changes](#breaking-changes-3)
    - [Database Migrations](#database-migrations-3)
    - [API Changes](#api-changes-3)
    - [Files Changed](#files-changed-3)
      - [Platform Architecture Documentation](#platform-architecture-documentation)
      - [Sprint and User Story Management](#sprint-and-user-story-management)
      - [ClickUp Integration Enhancement](#clickup-integration-enhancement)
      - [Git Workflow Plugin](#git-workflow-plugin)
      - [Environment Configuration](#environment-configuration)
      - [CI/CD and Workflows](#cicd-and-workflows)
      - [Configuration and Tooling](#configuration-and-tooling)
      - [Docker Configuration](#docker-configuration)
      - [Automation Scripts](#automation-scripts)
      - [Comprehensive Documentation Updates](#comprehensive-documentation-updates)
      - [Code Refactoring](#code-refactoring)
    - [Dependencies Updated](#dependencies-updated)
    - [Configuration Changes](#configuration-changes)
    - [Performance Notes](#performance-notes)
    - [Security Notes](#security-notes)
    - [Documentation Standards](#documentation-standards)
    - [Platform Architecture](#platform-architecture)
    - [Git Workflow Plugin Features](#git-workflow-plugin-features)
    - [ClickUp Integration Enhancements](#clickup-integration-enhancements)
  - [\[0.2.0\] - 03/01/2026](#020---03012026)
    - [Summary](#summary-4)
    - [Breaking Changes](#breaking-changes-4)
    - [Database Migrations](#database-migrations-4)
    - [API Changes](#api-changes-4)
    - [Files Changed](#files-changed-4)
      - [Version Management](#version-management)
      - [Markdown Documentation Headers](#markdown-documentation-headers)
    - [Dependencies Updated](#dependencies-updated-1)
    - [Configuration Changes](#configuration-changes-1)
    - [Performance Notes](#performance-notes-1)
    - [Security Notes](#security-notes-1)
    - [Documentation Standards](#documentation-standards-1)
    - [Version Management Workflow](#version-management-workflow)
  - [\[0.1.0\] - 03/01/2026](#010---03012026)
    - [Summary](#summary-5)
    - [Breaking Changes](#breaking-changes-5)
    - [Database Migrations](#database-migrations-5)
    - [API Changes](#api-changes-5)
    - [Files Changed](#files-changed-5)
      - [Core Django Configuration](#core-django-configuration)
      - [API and Security](#api-and-security)
      - [Docker Configuration](#docker-configuration-1)
      - [CI/CD Pipelines](#cicd-pipelines)
      - [Pre-commit Hooks](#pre-commit-hooks)
      - [Environment Configuration](#environment-configuration-1)
      - [Python Quality Tools](#python-quality-tools)
      - [JavaScript and Markdown Formatting](#javascript-and-markdown-formatting)
      - [Shell and Tool Configuration](#shell-and-tool-configuration)
      - [Git Configuration](#git-configuration)
      - [Automation Scripts](#automation-scripts-1)
      - [IDE Configuration](#ide-configuration)
      - [Documentation](#documentation-1)
    - [Dependencies Updated](#dependencies-updated-2)
    - [Configuration Changes](#configuration-changes-2)
    - [Performance Notes](#performance-notes-2)
    - [Security Notes](#security-notes-2)
    - [Infrastructure](#infrastructure)
    - [Development Workflow](#development-workflow)
    - [Testing](#testing)
    - [Documentation](#documentation-2)

---

## [Unreleased]

### Technical Changes

- Nothing yet

---

## [0.3.3] - 07/01/2026

### Summary

Documentation expansion for US-001 User Authentication including comprehensive implementation plan,
architecture review, security analysis, and supporting documentation across multiple categories.
This release also includes tooling improvements for markdown linting configuration and cleanup of
outdated review files.

### Breaking Changes

None - Documentation and configuration updates only.

### Database Migrations

None - No database changes.

### API Changes

None - No API changes.

### Files Changed

#### Documentation (New)

| Directory               | File                           | Purpose                         | Size  |
| ----------------------- | ------------------------------ | ------------------------------- | ----- |
| `docs/PLANS/`           | US-001-USER-AUTHENTICATION.md  | Complete authentication plan    | 203KB |
| `docs/ARCHITECTURE/US-` | ARCHITECTURE-REVIEW.md         | Technical architecture analysis | 65KB  |
| `docs/SECURITY/US-001/` | US-001-SECURITY.md             | Security review and hardening   | 43KB  |
| `docs/CODE-REVIEW/`     | Various code review files      | Code quality assessments        | -     |
| `docs/BACKEND/`         | Backend implementation details | Server-side architecture        | -     |
| `docs/DATABASE/`        | Database schema documentation  | Data model specifications       | -     |
| `docs/GDPR/US-001/`     | GDPR compliance documentation  | Data protection requirements    | -     |
| `docs/QA/`              | Quality assurance tests        | Testing strategies              | -     |
| `docs/REVIEWS/US-001/`  | US-001 specific reviews        | Detailed review documentation   | -     |
| `docs/TESTS/`           | Test specifications            | Test plan and coverage          | -     |

#### Documentation (Updated)

| File                                  | Changes                                              |
| ------------------------------------- | ---------------------------------------------------- |
| `docs/README.md`                      | Updated documentation index and structure references |
| `docs/STORIES/US-004-ORGANISATION-SE` | Updated organisation setup story details             |

#### Documentation (Removed)

| File                                            | Reason                       |
| ----------------------------------------------- | ---------------------------- |
| `docs/REVIEWS/CODE-REVIEW-2026-01-03.md`        | Consolidated into US-001     |
| `docs/REVIEWS/REVIEW-HUSKY-HOOKS-UPDATE-2026-0` | Consolidated and reorganised |

#### Configuration

| File                 | Changes                                               |
| -------------------- | ----------------------------------------------------- |
| `.markdownlint.json` | Updated configuration for new documentation structure |
| `package.json`       | Exclude `.venv` from markdown linting, version bump   |
| `VERSION-HISTORY.md` | Added 0.3.3 release entry                             |
| `RELEASES.md`        | Updated for 0.3.3 release                             |

### Key Documentation Additions

**US-001 User Authentication Plan (203KB):**

- Complete authentication workflow implementation
- Security review findings (6 Critical, 15 High, 12 Medium priority issues)
- Implementation details for all 27 edge cases
- Token hashing consistency fixes (HMAC-SHA256)
- 7 implementation phases with security fixes integrated
- Comprehensive API specifications

**Architecture Review (65KB):**

- Technical architecture analysis
- Component interaction diagrams
- Performance considerations
- Scalability planning

**Security Documentation (43KB):**

- Security hardening checklist
- Threat model analysis
- Authentication flow security
- Token management security
- Rate limiting and brute force protection

### Technical Details

**Documentation Structure:**
Created comprehensive documentation hierarchy for US-001 spanning:

- Plans (implementation roadmap)
- Architecture (technical design)
- Security (threat analysis and hardening)
- Code Review (quality assessments)
- Backend (implementation details)
- Database (schema specifications)
- GDPR (data protection compliance)
- QA (quality assurance)
- Tests (test specifications)

**Tooling Improvements:**

- Updated markdown linting to exclude `.venv` directory
- Enhanced markdownlint configuration for better documentation validation
- Cleaned up outdated review files to reduce repository clutter

### Migration Notes

No migrations required - documentation and configuration only.

### Testing Notes

No new tests required - documentation updates only.

### Deployment Notes

No deployment changes - documentation updates can be merged directly.

---

## [0.3.2] - 06/01/2026

### Summary

Code quality and tooling improvements including replacement of flake8 with ruff across all linting
pipelines, enhanced Husky git hooks with better performance and validation checks, and comprehensive
ruff linting error fixes across plugin and script files.

### Breaking Changes

None - All changes are code quality and tooling improvements.

### Database Migrations

None - No database changes.

### API Changes

None - No API changes.

### Files Changed

#### Git Hooks (Husky)

| File                      | Changes                                                               |
| ------------------------- | --------------------------------------------------------------------- |
| `.husky/pre-commit`       | Replaced flake8 with ruff, added Prettier and markdownlint, optimised |
| `.husky/post-merge`       | Added uv.lock tracking, dependency checks, migration reminders        |
| `.husky/pre-push`         | Replaced flake8 with ruff, enhanced validation checks                 |
| `.pre-commit-config.yaml` | Updated to use ruff-pre-commit instead of flake8                      |

#### Ruff Linting Fixes (Plugin Files)

| File                                | Issues Fixed                                        |
| ----------------------------------- | --------------------------------------------------- |
| `.claude/plugins/ab-test-tool.py`   | F841: Removed unused variable `response`            |
| `.claude/plugins/docker-tool.py`    | F841: Removed unused variable `stdout`              |
| `.claude/plugins/git-tool.py`       | E741: Renamed ambiguous variable `l` to `line`      |
| `.claude/plugins/optimiser-tool.py` | F841: Removed unused variables                      |
| `.claude/plugins/project-tool.py`   | B007: Prefixed unused loop variable with underscore |
| `.claude/plugins/chrome-tool.py`    | F841: Removed unused variable                       |
| `.claude/plugins/db-tool.py`        | F841: Removed unused variable                       |
| `.claude/plugins/env-tool.py`       | F841: Removed unused variable                       |
| `.claude/plugins/feedback-tool.py`  | F841: Removed unused variable                       |
| `.claude/plugins/log-tool.py`       | F841: Removed unused variable                       |
| `.claude/plugins/metrics-tool.py`   | F841: Removed unused variable                       |
| `.claude/plugins/pm-tool.py`        | F841: Removed unused variable                       |
| `.claude/plugins/quality-tool.py`   | F841: Removed unused variable                       |

#### Ruff Linting Fixes (ClickUp Scripts)

| File                                       | Issues Fixed                   |
| ------------------------------------------ | ------------------------------ |
| `scripts/clickup/clickup_client.py`        | F841: Removed unused variables |
| `scripts/clickup/pull_tasks.py`            | F841: Removed unused variable  |
| `scripts/clickup/sync_sprint_stories.py`   | F841: Removed unused variable  |
| `scripts/clickup/sync_sprints.py`          | F841: Removed unused variable  |
| `scripts/clickup/sync_stories.py`          | F841: Removed unused variable  |
| `scripts/clickup/sync_stories_enhanced.py` | F841: Removed unused variable  |

#### Ruff Linting Fixes (API and Middleware)

| File                             | Issues Fixed                  |
| -------------------------------- | ----------------------------- |
| `api/security.py`                | F841: Removed unused variable |
| `config/middleware/audit.py`     | F841: Removed unused variable |
| `config/middleware/ratelimit.py` | F841: Removed unused variable |
| `config/middleware/security.py`  | F841: Removed unused variable |

#### Documentation

| File                                                   | Changes                                         |
| ------------------------------------------------------ | ----------------------------------------------- |
| `.claude/CLAUDE.md`                                    | Added `.claude/plugins/` directory to structure |
| `docs/REVIEWS/REVIEW-HUSKY-HOOKS-UPDATE-2026-01-06.MD` | Comprehensive review of hook changes            |

### Dependencies

No dependency version changes. Updated linting pipeline to use ruff consistently across:

- Pre-commit hooks
- Husky git hooks
- CI/CD pipelines

### Developer Notes

- **Linting Consistency**: All linting now uses ruff instead of flake8 for better performance
  and modern Python support
- **Enhanced Hooks**: Pre-commit hooks now validate formatting (Prettier), markdown (markdownlint),
  and Python code quality (ruff) before allowing commits
- **Performance**: Pre-commit hook optimised to check only staged files, not entire codebase
- **Dependency Tracking**: Post-merge hook now reminds about uv.lock changes and migrations
- **Code Quality**: Fixed all ruff linting errors across 29 Python files (plugins, scripts, API)

### Migration Instructions

No migration required. This is a patch release with code quality and tooling improvements only.

Pull the latest code and the enhanced git hooks will automatically activate.

---

## [0.3.1] - 06/01/2026

### Summary

Code quality improvements including markdown linting fixes, documentation formatting enhancements,
and addition of uv.lock for reproducible Python builds.

### Breaking Changes

None - All changes are code quality and documentation improvements.

### Database Migrations

None - No database changes.

### API Changes

None - No API changes.

### Files Changed

#### Documentation Formatting (Markdown Lint Fixes)

| File                                             | Changes                                                                           |
| ------------------------------------------------ | --------------------------------------------------------------------------------- |
| `.claude/CLAUDE.md`                              | Fixed table column alignment in test naming conventions and coverage requirements |
| `docs/STORIES/*.md`                              | Removed extra blank lines (22 user story files)                                   |
| `docs/REVIEWS/REVIEW-CI-WORKFLOWS-2026-01-06.md` | Added blank lines after headings and list items for consistency                   |

#### Build and Configuration

| File                                 | Changes                                                             |
| ------------------------------------ | ------------------------------------------------------------------- |
| `uv.lock`                            | Added Python package lock file for reproducible builds (1521 lines) |
| `.gitignore`                         | Added clarifying comment about uv.lock requirement                  |
| `config/clickup-sprint-mapping.json` | Added trailing newline for POSIX compliance                         |

### Dependencies

No dependency version changes - only added uv.lock to ensure reproducible builds
across all environments.

### Developer Notes

- **Markdown Formatting**: All documentation now passes markdownlint validation
  with consistent table alignment and blank line usage
- **Reproducible Builds**: uv.lock ensures identical Python package versions
  across development, testing, staging, and production environments
- **Code Quality**: Continued focus on linting and formatting standards across the codebase

### Migration Instructions

No migration required. This is a patch release with formatting and documentation improvements only.

---

## [0.3.0] - 06/01/2026

### Summary

Platform architecture and project management enhancements. This release adds comprehensive CMS platform
documentation, enhanced ClickUp integration with sprint and story synchronisation, Git workflow automation
plugin, and improved development tooling across all environments.

### Breaking Changes

None - All changes are additive enhancements.

### Database Migrations

None - No database changes.

### API Changes

None - No API changes.

### Files Changed

#### Platform Architecture Documentation

| File                                     | Changes                                                |
| ---------------------------------------- | ------------------------------------------------------ |
| `docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md` | New comprehensive 16-phase platform architecture plan  |
| `README.md`                              | Updated with platform architecture references          |
| `.claude/CLAUDE.md`                      | Enhanced with architecture links and platform overview |

#### Sprint and User Story Management

| File                                        | Changes                                           |
| ------------------------------------------- | ------------------------------------------------- |
| `docs/SPRINTS/`                             | New directory with sprint documentation structure |
| `docs/STORIES/`                             | New directory with user story documentation       |
| `config/clickup-sprint-mapping.json`        | Sprint-to-ClickUp mapping configuration           |
| `config/clickup-story-mapping.json`         | Story-to-ClickUp mapping configuration            |
| `docs/PM-INTEGRATION/INTEGRATION-STATUS.md` | New integration status tracking document          |

#### ClickUp Integration Enhancement

| File                                        | Changes                                                 |
| ------------------------------------------- | ------------------------------------------------------- |
| `scripts/clickup/clickup_client.py`         | Enhanced API client with retry logic and error handling |
| `scripts/clickup/sync_sprints.py`           | New sprint synchronisation script                       |
| `scripts/clickup/sync_stories_enhanced.py`  | New enhanced story synchronisation                      |
| `scripts/clickup/README.md`                 | Updated with new sync capabilities                      |
| `config/clickup-config.json`                | Updated configuration with environment variables        |
| `.github/workflows/clickup-sync.yml`        | Enhanced automated sync workflow                        |
| `.github/workflows/clickup-branch-sync.yml` | Updated branch-to-task linking                          |

#### Git Workflow Plugin

| File                              | Changes                                          |
| --------------------------------- | ------------------------------------------------ |
| `.claude/plugins/git-tool.py`     | New comprehensive Git workflow management plugin |
| `.claude/plugins/version-tool.py` | New version detection helper utility             |
| `.claude/plugins/project-tool.py` | New project information utility                  |
| `.claude/README.md`               | Updated plugin documentation                     |
| `.claude/SYNTEK-GUIDE.md`         | Enhanced with Git workflow examples              |

#### Environment Configuration

| File                      | Changes                                              |
| ------------------------- | ---------------------------------------------------- |
| `.env.dev.example`        | Added ClickUp workspace, space, folder, and list IDs |
| `.env.test.example`       | Added ClickUp configuration variables                |
| `.env.staging.example`    | Added ClickUp configuration variables                |
| `.env.production.example` | Added ClickUp configuration variables                |

#### CI/CD and Workflows

| File                                      | Changes                                  |
| ----------------------------------------- | ---------------------------------------- |
| `.github/workflows/dependency-review.yml` | Enhanced security scanning configuration |
| `.github/workflows/README.md`             | Updated workflow documentation           |
| `.github/codeql/codeql-config.yml`        | Improved code analysis configuration     |
| `.github/CODEOWNERS`                      | Updated for new documentation structure  |
| `.github/PULL_REQUEST_TEMPLATE.md`        | Enhanced with ClickUp integration        |

#### Configuration and Tooling

| File                      | Changes                                                 |
| ------------------------- | ------------------------------------------------------- |
| `pyproject.toml`          | Updated dependencies and tool configurations            |
| `package.json`            | Updated scripts and dependencies, version bump to 0.3.0 |
| `.python-version`         | Updated to Python 3.11                                  |
| `.pylintrc`               | Updated linting rules                                   |
| `.hadolint.yaml`          | Updated Docker linting configuration                    |
| `.pre-commit-config.yaml` | Updated hooks for new file structure                    |
| `Makefile`                | Added new targets for ClickUp synchronisation           |

#### Docker Configuration

| File                                   | Changes                                          |
| -------------------------------------- | ------------------------------------------------ |
| `docker/dev/docker-compose.yml`        | Enhanced service definitions and volume mappings |
| `docker/test/docker-compose.yml`       | Updated test database configuration              |
| `docker/staging/docker-compose.yml`    | Improved deployment readiness checks             |
| `docker/production/docker-compose.yml` | Enhanced security and performance settings       |

#### Automation Scripts

| File                        | Changes                                |
| --------------------------- | -------------------------------------- |
| `scripts/env/dev.sh`        | Enhanced with new development commands |
| `scripts/env/test.sh`       | Improved test coverage reporting       |
| `scripts/env/staging.sh`    | Enhanced deployment validation         |
| `scripts/env/production.sh` | Added safety checks and confirmations  |
| `.husky/post-merge`         | Updated for dependency synchronisation |
| `.husky/README.md`          | Enhanced hook documentation            |

#### Comprehensive Documentation Updates

| File                                                 | Changes                                       |
| ---------------------------------------------------- | --------------------------------------------- |
| `docs/README.md`                                     | Updated documentation index with new sections |
| `docs/DEVELOPER-SETUP.md`                            | Enhanced setup guide                          |
| `docs/VERSIONS.md`                                   | Updated version management guide              |
| `docs/DOTFILES.md`                                   | Enhanced dotfile configuration documentation  |
| `docs/DEVOPS/README.md`                              | Updated DevOps practices                      |
| `docs/DEVOPS/CICD-GITHUB-ACTIONS.md`                 | Renamed from .MD, updated content             |
| `docs/PM-INTEGRATION/README.MD`                      | Enhanced integration overview                 |
| `docs/PM-INTEGRATION/CLICKUP-INTEGRATION-SUMMARY.md` | Renamed from .MD                              |
| `docs/PM-INTEGRATION/GITHUB-SECRETS.md`              | Renamed from .MD                              |
| `docs/PM-INTEGRATION/QUICK-REFERENCE.md`             | Renamed from .MD                              |
| `docs/PM-INTEGRATION/SETUP-GUIDE.md`                 | Renamed from .MD                              |
| `docs/PM-INTEGRATION/TROUBLESHOOTING.md`             | Renamed from .MD                              |
| `docs/GDPR/README.md`                                | Updated compliance documentation              |
| `docs/GDPR/COMPLIANCE-ASSESSMENT-2026-01-03.md`      | Enhanced assessment                           |
| `docs/SECURITY/README.md`                            | Updated security overview                     |
| `docs/SECURITY/SECURITY.md`                          | Enhanced implementation guide                 |
| `docs/SECURITY/SECURITY-IMPLEMENTATION-SUMMARY.md`   | Updated summary                               |
| `docs/SECURITY/SECURITY-QUICK-REFERENCE.md`          | Enhanced quick reference                      |
| `docs/LOGGING/README.md`                             | Updated logging strategy                      |
| `docs/LOGGING/IMPLEMENTATION-PLAN-2026-01-03.md`     | Enhanced implementation plan                  |
| `docs/PRETTIER/README.md`                            | Updated formatting overview                   |
| `docs/PRETTIER/PRETTIER-SETUP.md`                    | Enhanced setup guide                          |
| `docs/PRETTIER/PRETTIER-IMPLEMENTATION-SUMMARY.md`   | Updated summary                               |
| `docs/SYNTAX/README.md`                              | Updated linting overview                      |
| `docs/SYNTAX/LINTING-REPORT-2026-01-03.md`           | Enhanced linting report                       |
| `docs/REVIEWS/README.md`                             | Updated review guidelines                     |
| `docs/REVIEWS/CODE-REVIEW-2026-01-03.md`             | Enhanced review report                        |
| `docs/METRICS/README.md`                             | Updated metrics documentation                 |
| `api/README.md`                                      | Updated GraphQL documentation                 |
| `templates/README.md`                                | Enhanced template documentation               |
| `config/README.MD`                                   | Updated configuration guide                   |

#### Code Refactoring

| File                            | Changes                                       |
| ------------------------------- | --------------------------------------------- |
| `config/validators/password.py` | Improved documentation and code clarity       |
| `config/settings/base.py`       | Cleaned up imports and deprecated patterns    |
| `config/urls.py`                | Removed deprecated URL configuration patterns |

### Dependencies Updated

None - No dependency version changes.

### Configuration Changes

| File             | Key                         | Change                      |
| ---------------- | --------------------------- | --------------------------- |
| `package.json`   | `version`                   | Updated from 0.2.0 to 0.3.0 |
| `pyproject.toml` | `version`                   | Updated from 0.2.0 to 0.3.0 |
| `VERSION`        | Version number              | Updated from 0.2.0 to 0.3.0 |
| `.env.*.example` | `CLICKUP_WORKSPACE_ID`      | New required variable       |
| `.env.*.example` | `CLICKUP_SPACE_ID`          | New required variable       |
| `.env.*.example` | `CLICKUP_SPRINT_FOLDER_ID`  | New required variable       |
| `.env.*.example` | `CLICKUP_BACKLOG_FOLDER_ID` | New required variable       |
| `.env.*.example` | `CLICKUP_BACKLOG_LIST_ID`   | New required variable       |

### Performance Notes

- Git workflow plugin enables faster branch operations
- Enhanced ClickUp sync reduces manual project management overhead
- Improved Docker configurations optimise container startup times

### Security Notes

- Environment variable-based ClickUp configuration prevents ID exposure in git
- Enhanced pre-commit hooks for new file structure
- Improved CodeQL analysis configuration

### Documentation Standards

All markdown files standardised to:

- Uppercase file names with lowercase .md extension (SETUP-GUIDE.md)
- Consistent metadata headers across all documentation
- Cross-referencing to platform architecture plan
- Improved table of contents and navigation

### Platform Architecture

This release establishes the complete platform vision:

- **16-Phase Development Plan**: Structured roadmap from Phase 1 (Core Foundation)
  through Phase 16 (Platform Upgrade System)
- **Multi-Repository Architecture**: Backend, UI library, Web frontend, Mobile app
- **Multi-Tenancy Design**: Organisation-based isolation with encrypted data
- **Design Token System**: Database-driven theming for consistent branding
- **Content Branching**: Git-like workflow for content
  (feature → testing → dev → staging → production)
- **9 Site Templates**: E-commerce, Blog, Corporate, Church, Charity, SaaS, Sole Trader,
  Estate Agent, Single Page
- **SaaS Integrations**: Email service, Cloud documents (OnlyOffice),
  Password manager (Vaultwarden)
- **AI Integration**: Anthropic Claude integration planned for Phases 12+

### Git Workflow Plugin Features

The new Git plugin provides:

- Automated branch creation following us###/description pattern
- Multi-environment branch strategy management
- Pre-commit version management integration
- Pull request template generation
- Semantic versioning analysis
- Changelog automation
- Commit message validation
- GitHub CLI integration

### ClickUp Integration Enhancements

Enhanced integration capabilities:

- Automated sprint synchronisation from local documentation
- User story task creation with hierarchy
- Custom field mapping (story points, sprint, priority)
- Branch name to task ID linking
- Commit message to task comment synchronisation
- Bidirectional status updates
- Environment variable-based configuration (no hardcoded IDs)

---

## [0.2.0] - 03/01/2026

### Summary

Version management system initialisation. Added comprehensive versioning documentation,
automated markdown header management, and established semantic versioning workflow for the project.

### Breaking Changes

None - Documentation and tooling improvements only.

### Database Migrations

None - No database changes.

### API Changes

None - No API changes.

### Files Changed

#### Version Management

| File                 | Changes                                                        |
| -------------------- | -------------------------------------------------------------- |
| `VERSION`            | Created version file containing 0.2.0                          |
| `VERSION-HISTORY.md` | Technical change log for developers with detailed file changes |
| `CHANGELOG.md`       | Developer-focused summary following Keep a Changelog format    |
| `RELEASES.md`        | User-facing release notes with feature highlights              |
| `package.json`       | Updated version to 0.2.0                                       |

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

| File           | Key       | Change                      |
| -------------- | --------- | --------------------------- |
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

Initial release of the Django/Wagtail backend template with comprehensive multi-environment Docker setup,
CI/CD pipelines, and developer tooling. This release establishes the foundational architecture for building
scalable backend applications with Django, Wagtail CMS, PostgreSQL, and GraphQL.

### Breaking Changes

None - Initial release.

### Database Migrations

None - Initial setup with no migrations yet.

### API Changes

| Endpoint       | Method | Change                                                |
| -------------- | ------ | ----------------------------------------------------- |
| `/api/graphql` | POST   | GraphQL endpoint initialised with security middleware |
| `/admin/`      | GET    | Wagtail admin interface available                     |

### Files Changed

#### Core Django Configuration

| File                            | Changes                                                                              |
| ------------------------------- | ------------------------------------------------------------------------------------ |
| `config/settings/base.py`       | Base Django settings with security headers, middleware, GraphQL, Wagtail integration |
| `config/settings/dev.py`        | Development settings with debug toolbar, Mailpit, local database                     |
| `config/settings/test.py`       | Test settings with in-memory database, coverage reporting                            |
| `config/settings/staging.py`    | Staging settings with managed services, logging, security                            |
| `config/settings/production.py` | Production settings with strict security, performance optimisation                   |
| `config/urls.py`                | URL routing with GraphQL, Wagtail, admin interfaces                                  |
| `config/wsgi.py`                | WSGI application configuration                                                       |
| `config/asgi.py`                | ASGI application configuration for async support                                     |
| `manage.py`                     | Django management command entry point                                                |

#### API and Security

| File                             | Changes                                                      |
| -------------------------------- | ------------------------------------------------------------ |
| `api/schema.py`                  | GraphQL schema definition with sample queries                |
| `api/security.py`                | JWT authentication, rate limiting, query complexity analysis |
| `api/urls.py`                    | GraphQL endpoint routing                                     |
| `config/middleware/security.py`  | Security headers, CSP, HSTS middleware                       |
| `config/middleware/ratelimit.py` | Rate limiting middleware with Redis/Valkey backend           |
| `config/middleware/audit.py`     | Audit logging middleware for tracking requests               |
| `config/validators/password.py`  | Custom password validators with NCSC recommendations         |

#### Docker Configuration

| File                                   | Changes                                                |
| -------------------------------------- | ------------------------------------------------------ |
| `docker/dev/Dockerfile`                | Development container with hot reload, debugging tools |
| `docker/dev/docker-compose.yml`        | Dev environment with PostgreSQL, Redis, Mailpit        |
| `docker/test/Dockerfile`               | Test container optimised for CI/CD                     |
| `docker/test/docker-compose.yml`       | Test environment with isolated database                |
| `docker/staging/Dockerfile`            | Staging container with production-like setup           |
| `docker/staging/docker-compose.yml`    | Staging environment configuration                      |
| `docker/staging/entrypoint.sh`         | Staging entrypoint with migrations, health checks      |
| `docker/production/Dockerfile`         | Production container with multi-stage build, security  |
| `docker/production/docker-compose.yml` | Production environment configuration                   |
| `docker/production/entrypoint.sh`      | Production entrypoint with comprehensive checks        |
| `.dockerignore`                        | Docker build optimisation                              |
| `.hadolint.yaml`                       | Docker linting configuration                           |

#### CI/CD Pipelines

| File                                        | Changes                                                                |
| ------------------------------------------- | ---------------------------------------------------------------------- |
| `.github/workflows/ci.yml`                  | Continuous integration pipeline with tests, linting, security scanning |
| `.github/workflows/pr-validation.yml`       | Pull request validation with automated checks                          |
| `.github/workflows/deploy-staging.yml`      | Automated staging deployment pipeline                                  |
| `.github/workflows/deploy-production.yml`   | Production deployment with approval gates                              |
| `.github/workflows/codeql.yml`              | CodeQL security analysis                                               |
| `.github/workflows/dependency-review.yml`   | Dependency vulnerability scanning                                      |
| `.github/workflows/clickup-sync.yml`        | ClickUp task synchronisation                                           |
| `.github/workflows/clickup-branch-sync.yml` | Branch-to-task linking automation                                      |
| `.github/PULL_REQUEST_TEMPLATE.md`          | PR template with checklist                                             |
| `.github/CODEOWNERS`                        | Code ownership definitions                                             |
| `.github/dependabot.yml`                    | Automated dependency updates                                           |

#### Pre-commit Hooks

| File                      | Changes                                          |
| ------------------------- | ------------------------------------------------ |
| `.pre-commit-config.yaml` | Pre-commit hook configuration with 15+ checks    |
| `.husky/pre-commit`       | Git pre-commit hook runner                       |
| `.husky/commit-msg`       | Commit message validation (Conventional Commits) |
| `.husky/pre-push`         | Pre-push validation                              |
| `.husky/post-merge`       | Post-merge dependency check                      |

#### Environment Configuration

| File                      | Changes                                                |
| ------------------------- | ------------------------------------------------------ |
| `.env.example`            | General environment template                           |
| `.env.dev.example`        | Development environment variables                      |
| `.env.test.example`       | Test environment variables                             |
| `.env.staging.example`    | Staging environment variables                          |
| `.env.production.example` | Production environment variables                       |
| `.env.chrome.example`     | Headless Chrome configuration for testing              |
| `.envrc`                  | direnv configuration for automatic environment loading |

#### Python Quality Tools

| File              | Changes                                                            |
| ----------------- | ------------------------------------------------------------------ |
| `pyproject.toml`  | Python project configuration with Black, isort, pytest, mypy, Ruff |
| `setup.cfg`       | Additional Python tool configuration                               |
| `.pylintrc`       | Pylint linting rules                                               |
| `.flake8`         | Flake8 linting configuration                                       |
| `.bandit`         | Bandit security scanning rules                                     |
| `.coveragerc`     | Coverage.py configuration with 80% threshold                       |
| `.python-version` | Python version specification (3.12.1)                              |

#### JavaScript and Markdown Formatting

| File                 | Changes                                       |
| -------------------- | --------------------------------------------- |
| `package.json`       | Node.js dependencies for Prettier             |
| `.prettierrc`        | Prettier formatting configuration             |
| `.prettierrc.md`     | Markdown-specific Prettier rules              |
| `.prettierignore`    | Files to exclude from formatting              |
| `.markdownlint.json` | Markdown linting rules                        |
| `.commitlintrc.json` | Commit message linting (Conventional Commits) |
| `.cspell.json`       | Spell checking configuration                  |

#### Shell and Tool Configuration

| File             | Changes                      |
| ---------------- | ---------------------------- |
| `.shellcheckrc`  | Shell script linting rules   |
| `.yamllint.yml`  | YAML linting configuration   |
| `.tool-versions` | asdf tool version management |
| `.graphqlconfig` | GraphQL IDE configuration    |

#### Git Configuration

| File             | Changes                                                      |
| ---------------- | ------------------------------------------------------------ |
| `.gitignore`     | Comprehensive ignore rules for Python, Node.js, Docker, IDEs |
| `.gitattributes` | Git attributes for line endings, diff handling               |
| `.editorconfig`  | Cross-editor coding style configuration                      |

#### Automation Scripts

| File                                | Changes                                               |
| ----------------------------------- | ----------------------------------------------------- |
| `Makefile`                          | Common development tasks (test, lint, format, docker) |
| `scripts/env/dev.sh`                | Development environment management script             |
| `scripts/env/test.sh`               | Test environment runner with coverage                 |
| `scripts/env/staging.sh`            | Staging deployment script                             |
| `scripts/env/production.sh`         | Production deployment script with safeguards          |
| `scripts/setup-ci.sh`               | CI/CD setup automation                                |
| `scripts/run-ci-locally.sh`         | Local CI pipeline runner                              |
| `scripts/setup-prettier.sh`         | Prettier setup automation                             |
| `scripts/clickup/clickup_client.py` | ClickUp API client                                    |
| `scripts/clickup/sync_stories.py`   | User story synchronisation                            |
| `scripts/clickup/pull_tasks.py`     | Task pulling from ClickUp                             |

#### IDE Configuration

| File                             | Changes                        |
| -------------------------------- | ------------------------------ |
| `.vscode/extensions.json`        | Recommended VS Code extensions |
| `.claude/CLAUDE.md`              | Claude AI project instructions |
| `.claude/SYNTEK-GUIDE.md`        | Syntek Dev Suite usage guide   |
| `.claude/commands/dev.md`        | Development command reference  |
| `.claude/commands/test.md`       | Testing command reference      |
| `.claude/commands/staging.md`    | Staging command reference      |
| `.claude/commands/production.md` | Production command reference   |

#### Documentation

| File                                                 | Changes                                |
| ---------------------------------------------------- | -------------------------------------- |
| `README.md`                                          | Project overview and quick start guide |
| `docs/README.md`                                     | Documentation index                    |
| `docs/DEVELOPER-SETUP.md`                            | Comprehensive developer setup guide    |
| `docs/VERSIONS.md`                                   | Version management guide               |
| `docs/DOTFILES.md`                                   | Configuration file documentation       |
| `docs/DEVOPS/README.md`                              | DevOps practices and deployment        |
| `docs/DEVOPS/CICD-GITHUB-ACTIONS.MD`                 | GitHub Actions CI/CD guide             |
| `docs/PM-INTEGRATION/README.MD`                      | ClickUp integration documentation      |
| `docs/PM-INTEGRATION/SETUP-GUIDE.MD`                 | ClickUp setup instructions             |
| `docs/PM-INTEGRATION/CLICKUP-INTEGRATION-SUMMARY.MD` | Integration summary                    |
| `docs/PM-INTEGRATION/QUICK-REFERENCE.MD`             | Quick reference guide                  |
| `docs/PM-INTEGRATION/GITHUB-SECRETS.MD`              | GitHub secrets configuration           |
| `docs/PM-INTEGRATION/TROUBLESHOOTING.MD`             | Troubleshooting guide                  |
| `docs/GDPR/README.md`                                | GDPR compliance overview               |
| `docs/GDPR/COMPLIANCE-ASSESSMENT-2026-01-03.md`      | GDPR assessment report                 |
| `docs/LOGGING/README.md`                             | Logging strategy                       |
| `docs/LOGGING/IMPLEMENTATION-PLAN-2026-01-03.md`     | Logging implementation plan            |
| `docs/SECURITY/README.md`                            | Security overview                      |
| `docs/SECURITY/SECURITY.md`                          | Security implementation guide          |
| `docs/SECURITY/SECURITY-IMPLEMENTATION-SUMMARY.md`   | Security summary                       |
| `docs/SECURITY/SECURITY-QUICK-REFERENCE.md`          | Security quick reference               |
| `docs/PRETTIER/README.md`                            | Prettier formatting overview           |
| `docs/PRETTIER/PRETTIER-SETUP.md`                    | Prettier setup guide                   |
| `docs/PRETTIER/PRETTIER-IMPLEMENTATION-SUMMARY.md`   | Prettier implementation summary        |
| `docs/SYNTAX/README.md`                              | Linting and syntax overview            |
| `docs/SYNTAX/LINTING-REPORT-2026-01-03.md`           | Linting report                         |
| `docs/REVIEWS/README.md`                             | Code review guidelines                 |
| `docs/REVIEWS/CODE-REVIEW-2026-01-03.md`             | Code review report                     |
| `docs/METRICS/README.md`                             | Self-learning metrics                  |
| `docs/METRICS/config.json`                           | Metrics configuration                  |
| `tests/README.md`                                    | Test structure and guidelines          |
| `api/README.md`                                      | GraphQL API documentation              |
| `apps/README.md`                                     | Django apps structure guide            |
| `config/README.md`                                   | Configuration documentation            |
| `config/settings/README.md`                          | Settings module documentation          |
| `config/middleware/README.md`                        | Middleware documentation               |
| `config/validators/README.md`                        | Validator documentation                |
| `docker/README.md`                                   | Docker setup documentation             |
| `docker/dev/README.md`                               | Development Docker guide               |
| `docker/test/README.md`                              | Test Docker guide                      |
| `docker/staging/README.md`                           | Staging Docker guide                   |
| `docker/production/README.md`                        | Production Docker guide                |
| `scripts/README.md`                                  | Scripts documentation                  |
| `scripts/env/README.md`                              | Environment scripts guide              |
| `scripts/clickup/README.md`                          | ClickUp scripts documentation          |
| `static/README.md`                                   | Static assets documentation            |
| `templates/README.md`                                | Django templates documentation         |

### Dependencies Updated

| Package              | Version | Notes                          |
| -------------------- | ------- | ------------------------------ |
| `Django`             | 5.0.x   | Latest stable Django framework |
| `wagtail`            | 6.x     | Wagtail CMS                    |
| `strawberry-graphql` | Latest  | GraphQL library                |
| `psycopg[binary]`    | 3.x     | PostgreSQL adapter             |
| `redis`              | Latest  | Redis client                   |
| `gunicorn`           | Latest  | WSGI HTTP server               |
| `whitenoise`         | Latest  | Static file serving            |
| `pytest`             | Latest  | Testing framework              |
| `pytest-django`      | Latest  | Django pytest plugin           |
| `pytest-cov`         | Latest  | Coverage plugin                |
| `black`              | Latest  | Code formatter                 |
| `ruff`               | Latest  | Linter                         |
| `mypy`               | Latest  | Type checker                   |
| `prettier`           | ^3.4.2  | JavaScript/Markdown formatter  |

### Configuration Changes

| File                      | Key              | Change                                       |
| ------------------------- | ---------------- | -------------------------------------------- |
| `config/settings/base.py` | `ALLOWED_HOSTS`  | Configured per environment                   |
| `config/settings/base.py` | `DATABASES`      | PostgreSQL with environment variables        |
| `config/settings/base.py` | `CACHES`         | Redis/Valkey caching backend                 |
| `config/settings/base.py` | `MIDDLEWARE`     | Security, rate limiting, audit logging       |
| `config/settings/base.py` | `INSTALLED_APPS` | Django, Wagtail, GraphQL, custom apps        |
| `.env.*.example`          | All              | Environment-specific configuration templates |

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
