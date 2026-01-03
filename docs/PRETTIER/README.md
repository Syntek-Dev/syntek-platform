# Prettier Documentation

> Code formatting configuration for non-Python files

## Table of Contents

- [Prettier Documentation](#prettier-documentation)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Documents](#documents)
  - [Quick Start](#quick-start)
  - [Related Files](#related-files)

## Overview

This directory contains documentation for Prettier code formatting in the Django/Wagtail backend template. Prettier handles formatting for all non-Python files (JSON, YAML, Markdown, HTML templates, CSS, JavaScript, GraphQL).

**Python files** are formatted with **Black** (separate configuration).

## Documents

| Document                                                                 | Purpose                                                                   |
| ------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| [PRETTIER-SETUP.md](PRETTIER-SETUP.md)                                   | Complete setup guide, configuration, VS Code integration, troubleshooting |
| [PRETTIER-IMPLEMENTATION-SUMMARY.md](PRETTIER-IMPLEMENTATION-SUMMARY.md) | Implementation details, decisions made, and current status                |

## Quick Start

```bash
# Install Prettier
npm install

# Format all files
npm run format

# Check formatting (CI)
npm run format:check

# Format specific types
npx prettier --write "**/*.json"
npx prettier --write "**/*.md"
```

## Related Files

| File                      | Location   | Purpose                        |
| ------------------------- | ---------- | ------------------------------ |
| `.prettierrc`             | Root       | Prettier configuration         |
| `.prettierignore`         | Root       | Files excluded from formatting |
| `package.json`            | Root       | npm scripts for formatting     |
| `.vscode/settings.json`   | `.vscode/` | VS Code auto-format settings   |
| `.pre-commit-config.yaml` | Root       | Git hook configuration         |

---

**Last Updated:** 2026-01-03
