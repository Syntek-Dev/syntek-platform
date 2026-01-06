# Configuration Directory

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

This directory contains Django settings and project management integration configuration files.

## Table of Contents

- [Configuration Directory](#configuration-directory)
  - [Table of Contents](#table-of-contents)
  - [Django Settings](#django-settings)
  - [ClickUp Integration Configuration](#clickup-integration-configuration)
    - [clickup-config.json](#clickup-configjson)
    - [clickup-tasks.json](#clickup-tasksjson)
    - [clickup-story-mapping.json](#clickup-story-mappingjson)
  - [Environment Variables](#environment-variables)
    - [Required Variables](#required-variables)
    - [How to Set Up](#how-to-set-up)
  - [Security Notes](#security-notes)

## Django Settings

Django settings are split across multiple environment-specific files in the `settings/` subdirectory:

- `base.py` - Common settings shared across all environments
- `dev.py` - Development environment settings
- `test.py` - Test environment settings
- `staging.py` - Staging environment settings
- `production.py` - Production environment settings

Use the `DJANGO_SETTINGS_MODULE` environment variable to specify which settings file to use:

```bash
# Development
DJANGO_SETTINGS_MODULE=config.settings.dev

# Production
DJANGO_SETTINGS_MODULE=config.settings.production
```

## ClickUp Integration Configuration

### clickup-config.json

**Purpose:** Main configuration file for ClickUp integration.

**Contents:**

- Workspace and space IDs (using environment variable placeholders)
- Folder and list IDs for sprints and backlog
- Status mapping between git branches and ClickUp statuses
- Field mapping for custom fields
- Priority mapping for MoSCoW prioritisation
- Branch naming patterns

**Environment Variable Placeholders:**
This file uses `${VARIABLE_NAME}` syntax for environment variable substitution. The Python client resolves these at runtime.

```json
{
  "workspace": {
    "workspace_id": "${CLICKUP_WORKSPACE_ID}",
    "space_id": "${CLICKUP_SPACE_ID}"
  }
}
```

**DO NOT** commit actual IDs or API keys to this file. Use environment variables only.

### clickup-tasks.json

**Purpose:** Generated cache of all ClickUp tasks.

**How it's created:**

```bash
python scripts/clickup/pull_tasks.py
```

**Contents:**

- Full task details from ClickUp
- Task metadata (assignees, tags, dates, status)
- Custom field values
- Task descriptions and acceptance criteria

**Update frequency:** Run the pull script whenever you need fresh task data from ClickUp.

**Git tracking:** This file can be committed to track the current state of tasks, but it should be regenerated regularly.

### clickup-story-mapping.json

**Purpose:** Maps user story IDs (US-XXX) to ClickUp task IDs.

**How it's created:**

```bash
python scripts/clickup/pull_tasks.py
```

**Contents:**

```json
{
  "US-123": "abc123xyz",
  "US-456": "def456uvw"
}
```

**Usage:**

- GitHub Actions workflows read this file to find ClickUp task IDs
- Branch naming convention `us123/feature-name` maps to `US-123`
- The workflow looks up `US-123` in this file to get the ClickUp task ID

**Git tracking:** **MUST be committed** for GitHub Actions to work correctly.

## Environment Variables

### Required Variables

All ClickUp integration scripts and GitHub Actions require these environment variables:

| Variable                    | Description            | Where to Get It            |
| --------------------------- | ---------------------- | -------------------------- |
| `CLICKUP_API_TOKEN`         | Your ClickUp API token | Settings > Apps in ClickUp |
| `CLICKUP_WORKSPACE_ID`      | Workspace ID           | From ClickUp URL or API    |
| `CLICKUP_SPACE_ID`          | Space ID               | From ClickUp URL or API    |
| `CLICKUP_SPRINT_FOLDER_ID`  | Sprint folder ID       | From ClickUp workspace     |
| `CLICKUP_BACKLOG_FOLDER_ID` | Backlog folder ID      | From ClickUp workspace     |
| `CLICKUP_BACKLOG_LIST_ID`   | Backlog list ID        | From ClickUp workspace     |

### How to Set Up

**1. Get Your ClickUp API Token:**

- Go to https://app.clickup.com/settings/apps
- Click "Generate" under API Token
- Copy the token (starts with `pk_`)

**2. Add to your local `.env.dev` file:**

```bash
CLICKUP_API_TOKEN=pk_your_actual_token_here
CLICKUP_WORKSPACE_ID=your_workspace_id
CLICKUP_SPACE_ID=your_space_id
CLICKUP_SPRINT_FOLDER_ID=your_sprint_folder_id
CLICKUP_BACKLOG_FOLDER_ID=your_backlog_folder_id
CLICKUP_BACKLOG_LIST_ID=your_backlog_list_id
```

**Note:** Contact your project administrator for the correct workspace/folder IDs.

**3. Add to GitHub Secrets:**

- Go to repository Settings > Secrets and variables > Actions
- Add `CLICKUP_API_TOKEN` with your token value
- Other IDs are safe to commit in `clickup-config.json` using variable placeholders

**4. Test the configuration:**

```bash
# Export the token
export CLICKUP_API_TOKEN=pk_your_token_here

# Test the ClickUp client
python scripts/clickup/pull_tasks.py

# You should see tasks being pulled
```

## Security Notes

**NEVER commit these to version control:**

- Actual API tokens or keys
- `.env.dev`, `.env.staging`, `.env.production` files (they're in .gitignore)
- Any file containing `pk_`, `sk_`, or other secret prefixes

**ALWAYS commit these:**

- `.env.*.example` files (with empty values)
- `clickup-config.json` (with `${VARIABLE}` placeholders only)
- `clickup-story-mapping.json` (contains no secrets, just IDs)
- `clickup-tasks.json` (optional, contains no secrets)

**GitHub Secrets:**

- Only `CLICKUP_API_TOKEN` needs to be a GitHub secret
- IDs (workspace, space, folder, list) are not sensitive and can use placeholders

**Rotation:**

- Rotate your ClickUp API token every 90 days
- Update both local `.env.dev` and GitHub Secrets when rotating
