# Claude Code Configuration

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

Configuration files for Claude Code development environment and Syntek Dev Suite integration.

## Table of Contents

- [Claude Code Configuration](#claude-code-configuration)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Files](#files)
  - [Configuration](#configuration)
    - [CLAUDE.md](#claudemd)
    - [SYNTEK-GUIDE.md](#syntek-guidemd)
    - [settings.local.json](#settingslocaljson)
    - [commands/](#commands)
  - [Settings](#settings)
    - [Environment Configuration](#environment-configuration)
    - [Documentation Standards](#documentation-standards)
  - [Custom Commands](#custom-commands)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains configuration specific to Claude Code and the Syntek Dev Suite plugin system. These files control how Claude Code understands your project structure, applies development standards, and integrates with external tools like ClickUp for project management.

**Key Point:** The `CLAUDE.md` file is the primary source of truth for development conventions and must be read when starting work on this project.

---

## Files

| File                  | Purpose                                                                                                        |
| --------------------- | -------------------------------------------------------------------------------------------------------------- |
| `CLAUDE.md`           | **Primary configuration file** - Project structure, conventions, documentation standards, command requirements |
| `SYNTEK-GUIDE.md`     | Agent workflow guide - Instructions for using Syntek Dev Suite agents                                          |
| `settings.local.json` | Local Claude Code settings - Editor preferences, workspace configuration                                       |
| `commands/`           | Custom command definitions for Claude Code                                                                     |

---

## Configuration

### CLAUDE.md

This is the primary configuration file for the project. It defines:

- **Project Stack:** Django + Wagtail + PostgreSQL + GraphQL
- **Container Setup:** Docker Compose per environment
- **Development Conventions:** Code style, docstring formats, type hints
- **Documentation Standards:** Markdown requirements, file organization
- **Command Execution:** Required to run commands inside Docker containers
- **Agent Workflows:** How to use Syntek Dev Suite agents

**Always read this file when:**

- Starting work on the project
- Making architectural decisions
- Creating new documentation
- Setting up the development environment

### SYNTEK-GUIDE.md

Guide for using Syntek Dev Suite agents effectively. Documents:

- Available agents and their purposes
- Workflow best practices
- Integration with Git and project management
- Tips for optimal results

### settings.local.json

Local settings for the Claude Code editor in this workspace. Contains:

- Workspace-specific preferences
- Integration credentials (kept private)
- Tool configurations

**Note:** This file may be excluded from version control to protect local settings.

### commands/

Directory for custom command definitions that extend Claude Code functionality. These allow defining shortcuts and automation for common development tasks.

---

## Settings

### Environment Configuration

The project uses environment-specific Docker setups. The `CLAUDE.md` file defines the required approach:

```bash
# Commands MUST run inside Docker containers
# NOT on the host machine

# Example: Running Django migrations
./scripts/env/dev.sh migrate

# NOT
python manage.py migrate
```

### Documentation Standards

All documentation follows:

- **Markdown Files:** Table of Contents required, proper heading structure
- **Section READMEs:** Every folder with 3+ files needs a README
- **Docstrings:** Google-style format for all Python code
- **Type Hints:** Required on all function signatures
- **Comments:** Only for non-obvious business logic

---

## Custom Commands

Custom commands should be added to this directory following Claude Code conventions. These enable efficient workflows for:

- Database migrations
- Running tests
- Code quality checks
- Deployment operations

---

## Related Documentation

- [Root README](../README.md) - Project overview
- [DEVELOPER-SETUP.md](../docs/DEVELOPER-SETUP.md) - Setup instructions
- [CLAUDE.md](./CLAUDE.md) - Full project configuration (read this first)

---

**Last Updated:** 2026-01-03
