# Prettier Setup Documentation

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

> **Last Updated:** 2026-01-03
> **Status:** Active

## Table of Contents

- [Prettier Setup Documentation](#prettier-setup-documentation)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
    - [Why This Approach?](#why-this-approach)
  - [Installation](#installation)
    - [Prerequisites](#prerequisites)
    - [Quick Setup](#quick-setup)
  - [Configuration](#configuration)
    - [Configuration Files](#configuration-files)
    - [Prettier Configuration (`.prettierrc`)](#prettier-configuration-prettierrc)
    - [Key Settings Explained](#key-settings-explained)
  - [Usage](#usage)
    - [Command Line](#command-line)
    - [Common Workflows](#common-workflows)
      - [Before Committing](#before-committing)
      - [Formatting Specific Files](#formatting-specific-files)
      - [CI/CD Check](#cicd-check)
  - [VS Code Integration](#vs-code-integration)
    - [Required Extension](#required-extension)
    - [Auto-format on Save](#auto-format-on-save)
    - [Manual Formatting in VS Code](#manual-formatting-in-vs-code)
  - [Pre-commit Integration](#pre-commit-integration)
    - [How It Works](#how-it-works)
    - [Pre-commit Configuration](#pre-commit-configuration)
    - [Skip Pre-commit (Not Recommended)](#skip-pre-commit-not-recommended)
  - [Troubleshooting](#troubleshooting)
    - [Issue: Prettier not found](#issue-prettier-not-found)
    - [Issue: Pre-commit hook fails](#issue-pre-commit-hook-fails)
    - [Issue: VS Code not formatting](#issue-vs-code-not-formatting)
    - [Issue: Files not formatting on save](#issue-files-not-formatting-on-save)
    - [Issue: Conflicting formatters](#issue-conflicting-formatters)
    - [Issue: Prettier breaking YAML structure](#issue-prettier-breaking-yaml-structure)
  - [Advanced Configuration](#advanced-configuration)
    - [Ignoring Files](#ignoring-files)
    - [Custom Overrides](#custom-overrides)
    - [Integration with Other Tools](#integration-with-other-tools)
  - [Resources](#resources)
  - [Questions?](#questions)

---

## Overview

This Django/Python project uses **Prettier** for formatting non-Python files. While Python code is
formatted with **Black**, Prettier handles:

- **JSON** files (`.json`, `.jsonc`)
- **YAML** files (`.yml`, `.yaml`)
- **Markdown** files (`.md`)
- **HTML templates** (`.html` - Django/Jinja templates)
- **CSS** files (`.css`)
- **JavaScript** files (`.js` - if any)
- **GraphQL** schema files (`.graphql`)

### Why This Approach?

- **Best tool for each job:**
  - Python: Black (Python-specific, opinionated)
  - Everything else: Prettier (universal, consistent)
- **Team consistency:** Same formatting across all file types
- **Editor support:** VS Code auto-formats on save
- **CI/CD integration:** Pre-commit hooks ensure quality

---

## Installation

### Prerequisites

- **Node.js** v20+ (already installed via nvm)
- **npm** v10+

### Quick Setup

Run the setup script:

```bash
./scripts/setup-prettier.sh
```

Or manually:

```bash
# Install npm dependencies
npm install

# Install pre-commit hooks (if not already done)
pip install pre-commit
pre-commit install
```

---

## Configuration

### Configuration Files

| File                      | Purpose                                   |
| ------------------------- | ----------------------------------------- |
| `.prettierrc`             | Prettier configuration (formatting rules) |
| `.prettierignore`         | Files to exclude from formatting          |
| `package.json`            | npm package definition and scripts        |
| `.vscode/settings.json`   | VS Code Prettier integration              |
| `.pre-commit-config.yaml` | Git pre-commit hook configuration         |

### Prettier Configuration (`.prettierrc`)

```json
{
  "semi": false,
  "singleQuote": true,
  "tabWidth": 2,
  "useTabs": false,
  "trailingComma": "es5",
  "bracketSpacing": true,
  "bracketSameLine": false,
  "arrowParens": "always",
  "printWidth": 100,
  "endOfLine": "lf",
  "plugins": ["prettier-plugin-jinja-template"],
  "overrides": [
    {
      "files": "*.html",
      "options": {
        "parser": "jinja-template",
        "printWidth": 120,
        "tabWidth": 2
      }
    }
  ]
}
```

### Key Settings Explained

| Setting         | Value            | Why                             |
| --------------- | ---------------- | ------------------------------- |
| `semi`          | `false`          | No semicolons (cleaner)         |
| `singleQuote`   | `true`           | Consistency with Black (Python) |
| `tabWidth`      | `2`              | Standard for JSON/YAML/HTML     |
| `printWidth`    | `100`            | Matches Black's line length     |
| `endOfLine`     | `lf`             | Unix line endings (consistency) |
| `parser` (HTML) | `jinja-template` | Support Django/Jinja templates  |

---

## Usage

### Command Line

```bash
# Format all files
npm run format

# Check formatting without changes
npm run format:check

# Format only staged files (pre-commit)
npm run format:staged

# Format specific file types
npx prettier --write "**/*.json"
npx prettier --write "**/*.{yml,yaml}"
npx prettier --write "**/*.md"
```

### Common Workflows

#### Before Committing

```bash
# Check what would be formatted
npm run format:check

# Format everything
npm run format

# Or just commit (pre-commit hook handles it)
git commit -m "Your message"
```

#### Formatting Specific Files

```bash
# Format a single file
npx prettier --write path/to/file.json

# Format all YAML files
npx prettier --write "**/*.{yml,yaml}"

# Check a specific file
npx prettier --check path/to/file.md
```

#### CI/CD Check

```bash
# Run the same check as CI
npm run format:check
```

---

## VS Code Integration

### Required Extension

Install the **Prettier - Code formatter** extension:

1. Open VS Code
2. Press `Ctrl+P` (or `Cmd+P` on macOS)
3. Type: `ext install esbenp.prettier-vscode`
4. Press Enter

### Auto-format on Save

The `.vscode/settings.json` file configures auto-formatting:

```json
{
  "editor.formatOnSave": true,
  "[json]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[yaml]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[markdown]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### Manual Formatting in VS Code

- **Format entire file:** `Shift+Alt+F` (or `Shift+Opt+F` on macOS)
- **Format selection:** Select text → `Ctrl+K Ctrl+F`

---

## Pre-commit Integration

Prettier runs automatically on Git commits via **pre-commit hooks**.

### How It Works

1. You stage files: `git add .`
2. You commit: `git commit -m "Message"`
3. Pre-commit runs Prettier on staged files
4. If formatting fails, commit is rejected
5. Files are auto-formatted
6. You review and commit again

### Pre-commit Configuration

From `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/pre-commit/mirrors-prettier
  rev: v4.0.0-alpha.8
  hooks:
    - id: prettier
      types_or: [json, yaml, markdown, html, css, javascript, graphql]
      additional_dependencies:
        - prettier@3.4.2
        - prettier-plugin-jinja-template@2.0.0
```

### Skip Pre-commit (Not Recommended)

```bash
# Skip all hooks (emergency only)
git commit --no-verify -m "Message"
```

---

## Troubleshooting

### Issue: Prettier not found

**Solution:**

```bash
# Reinstall npm dependencies
npm install

# Check installation
npx prettier --version
```

### Issue: Pre-commit hook fails

**Solution:**

```bash
# Update pre-commit hooks
pre-commit autoupdate

# Run manually to see detailed errors
pre-commit run prettier --all-files
```

### Issue: VS Code not formatting

**Solution:**

1. Check Prettier extension is installed
2. Check `.prettierrc` exists in project root
3. Open VS Code settings (`Ctrl+,`)
4. Search for "Default Formatter"
5. Set to "Prettier - Code formatter"

### Issue: Files not formatting on save

**Solution:**

1. Check `.vscode/settings.json` has `"editor.formatOnSave": true`
2. Ensure file type has Prettier as default formatter
3. Reload VS Code window (`Ctrl+Shift+P` → "Reload Window")

### Issue: Conflicting formatters

**Solution:**

Remove other formatters for the same file types:

<!-- prettier-ignore -->
```jsonc
// In VS Code settings
"[json]": {
  "editor.defaultFormatter": "esbenp.prettier-vscode"  // Only Prettier
}
```

### Issue: Prettier breaking YAML structure

**Solution:**

Check `.yamllint.yml` and `.prettierrc` rules align:

```yaml
# .yamllint.yml
rules:
  line-length:
    max: 100 # Matches Prettier's printWidth
```

---

## Advanced Configuration

### Ignoring Files

Add patterns to `.prettierignore`:

```
# Ignore generated files
/staticfiles/
/migrations/

# Ignore lock files
*.lock
package-lock.json
```

### Custom Overrides

Add file-specific rules to `.prettierrc`:

```json
{
  "overrides": [
    {
      "files": "*.test.json",
      "options": {
        "tabWidth": 4
      }
    }
  ]
}
```

### Integration with Other Tools

Prettier works alongside:

- **Black** (Python formatting)
- **markdownlint** (Markdown linting)
- **yamllint** (YAML linting)
- **ESLint** (JavaScript linting)

**Note:** Prettier formats, linters check logic/style. Both can coexist.

---

## Resources

- **Prettier Docs:** <https://prettier.io/docs/en/>
- **Prettier Playground:** <https://prettier.io/playground/>
- **Jinja Template Plugin:** <https://github.com/davidodenwald/prettier-plugin-jinja-template>
- **VS Code Extension:** <https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode>

---

## Questions?

If you encounter issues not covered here, check:

1. **Prettier GitHub Issues:** <https://github.com/prettier/prettier/issues>
2. **Project CLAUDE.md:** `.claude/CLAUDE.md`
3. **Team documentation:** `docs/`

---

**Happy formatting!**
