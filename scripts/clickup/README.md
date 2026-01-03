# ClickUp Integration Scripts

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

Python scripts for syncing user stories, sprints, and tasks between this Django project and ClickUp project management tool.

## Table of Contents

- [ClickUp Integration Scripts](#clickup-integration-scripts)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
    - [Environment Variables](#environment-variables)
    - [Configuration File](#configuration-file)
  - [Scripts](#scripts)
    - [1. clickup\_client.py](#1-clickup_clientpy)
    - [2. sync\_stories.py](#2-sync_storiespy)
    - [3. pull\_tasks.py](#3-pull_taskspy)
  - [GitHub Actions Integration](#github-actions-integration)
    - [clickup-sync.yml](#clickup-syncyml)
    - [clickup-branch-sync.yml](#clickup-branch-syncyml)
  - [Branch Naming Convention](#branch-naming-convention)
  - [Workflow Examples](#workflow-examples)
    - [Creating a New Feature](#creating-a-new-feature)
    - [Syncing Stories to ClickUp](#syncing-stories-to-clickup)
  - [Troubleshooting](#troubleshooting)
    - [API Key Issues](#api-key-issues)
    - [Task Not Found in Mapping](#task-not-found-in-mapping)
    - [Status Update Failures](#status-update-failures)
  - [API Rate Limits](#api-rate-limits)
  - [Security](#security)


## Prerequisites

1. Python 3.11 or higher (on your local machine or CI/CD environment)
2. ClickUp API key with appropriate permissions
3. Environment variables configured (see Setup below)

**Note:** These scripts run on your local machine or in GitHub Actions, NOT inside Docker containers. They interact with the ClickUp API to sync project management data.

## Installation

```bash
# Install dependencies on your local machine
pip install requests>=2.31.0

# Or if you have the project's pyproject.toml
pip install -e .
```

## Configuration

### Environment Variables

Add to your `.env.dev` file:

```bash
CLICKUP_API_KEY=pk_your_api_key_here
CLICKUP_TEAM_ID=
CLICKUP_SPACE_ID=
CLICKUP_SPRINTS_FOLDER_ID=
CLICKUP_BACKLOG_FOLDER_ID=
CLICKUP_BACKLOG_LIST_ID=
```

### Configuration File

The ClickUp integration configuration is stored in `config/clickup-config.json`. This file defines:

- Workspace and folder IDs
- Status mappings between local states and ClickUp statuses
- Branch naming conventions
- Priority mappings
- Field mappings for custom fields

## Scripts

### 1. clickup_client.py

Python client library for ClickUp API v2.

**Usage:**

```python
from clickup_client import get_client

# Initialize client (reads CLICKUP_API_KEY from environment)
client = get_client()

# Get folder details
folder = client.get_folder("901512938483")

# Create a task
task = client.create_task(
    list_id="901519340766",
    name="US-001: User Authentication",
    description="Implement user login and registration",
    status="Open",
    priority=2,
    tags=["must-have"]
)

# Update task status
client.update_task_status(task["id"], "in progress")
```

### 2. sync_stories.py

Sync user stories from `docs/STORIES/` directory to ClickUp.

**Usage:**

```bash
# Sync all stories
python scripts/clickup/sync_stories.py

# Preview changes without syncing
python scripts/clickup/sync_stories.py --dry-run

# Sync specific folder
python scripts/clickup/sync_stories.py --folder-path docs/STORIES/SPRINT-01
```

**Story File Format:**

Stories should be markdown files named `US-XXX.md` with the following format:

```markdown
# User Story Title

**Story Points:** 5
**Priority:** Must Have
**Sprint:** Sprint 01
**Status:** Open

Brief description of the user story goes here.

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3
```

### 3. pull_tasks.py

Pull all tasks from ClickUp and save IDs for local reference.

**Usage:**

```bash
# Pull all open tasks
python scripts/clickup/pull_tasks.py

# Pull all tasks including closed
python scripts/clickup/pull_tasks.py --include-closed

# Output only story ID mapping
python scripts/clickup/pull_tasks.py --mapping-only

# Save to custom location
python scripts/clickup/pull_tasks.py --output /tmp/tasks.json
```

**Output Files:**

- `config/clickup-tasks.json` - Full task details
- `config/clickup-story-mapping.json` - Story ID to ClickUp task ID mapping

## GitHub Actions Integration

The ClickUp integration includes GitHub Actions workflows for automatic syncing:

### clickup-sync.yml

Triggers on:
- Push to main, staging, dev, testing branches
- Pull request opened, synchronized, closed
- Manual workflow dispatch

**Behavior:**

- Extracts task ID from branch name (e.g., `us123/feature-name`)
- Updates ClickUp task status based on branch/PR event
- Adds comments to ClickUp tasks for PR events

**Status Mapping:**

| Event | Target Branch | ClickUp Status |
|-------|--------------|----------------|
| PR opened | any | in review |
| PR merged | main | Closed |
| PR merged | staging | accepted |
| PR merged | dev | in progress |
| Push | main | Closed |
| Push | staging | accepted |
| Push | dev | in progress |
| Push | testing | in review |

### clickup-branch-sync.yml

Triggers on:
- Branch creation matching pattern `us*/**`

**Behavior:**

- Detects task ID from branch name
- Updates task status to "in progress"
- Adds branch creation comment to ClickUp task

## Branch Naming Convention

To enable automatic ClickUp sync, use this branch naming pattern:

```
us{task_number}/{feature_name}
```

**Examples:**

```bash
# Good branch names
git checkout -b us123/add-user-authentication
git checkout -b us456/fix-database-migration
git checkout -b us789/update-api-docs

# Bad branch names (won't sync)
git checkout -b feature/user-auth
git checkout -b bugfix-migration
git checkout -b US-123-auth  # Wrong format
```

## Workflow Examples

### Creating a New Feature

1. Pull latest tasks from ClickUp:
   ```bash
   python scripts/clickup/pull_tasks.py
   ```

2. Find your task in `config/clickup-story-mapping.json`

3. Create feature branch:
   ```bash
   git checkout -b us123/my-feature
   ```
   This automatically moves the task to "in progress" in ClickUp.

4. Make your changes and push:
   ```bash
   git add .
   git commit -m "Implement feature"
   git push origin us123/my-feature
   ```

5. Create pull request - this updates task to "in review"

6. When PR is merged to staging - task moves to "accepted"

7. When staging is merged to main - task moves to "Closed"

### Syncing Stories to ClickUp

1. Create story files in `docs/STORIES/`:
   ```bash
   docs/STORIES/
   ├── US-001.md
   ├── US-002.md
   └── SPRINT-01/
       ├── US-003.md
       └── US-004.md
   ```

2. Preview sync:
   ```bash
   python scripts/clickup/sync_stories.py --dry-run
   ```

3. Sync to ClickUp:
   ```bash
   python scripts/clickup/sync_stories.py
   ```

4. Pull updated task IDs:
   ```bash
   python scripts/clickup/pull_tasks.py
   ```

## Troubleshooting

### API Key Issues

If you get authentication errors:

```bash
# Verify API key is set
echo $CLICKUP_API_KEY

# Test API access
curl -H "Authorization: $CLICKUP_API_KEY" \
  https://api.clickup.com/api/v2/team
```

### Task Not Found in Mapping

If GitHub Actions can't find your task:

1. Ensure task exists in ClickUp
2. Task name should start with `US-XXX:` format
3. Regenerate mapping:
   ```bash
   python scripts/clickup/pull_tasks.py
   git add config/clickup-story-mapping.json
   git commit -m "Update ClickUp task mapping"
   git push
   ```

### Status Update Failures

If status updates fail:

1. Check that status names match exactly (case-sensitive)
2. Verify status exists in your ClickUp workspace
3. View available statuses:
   ```python
   from clickup_client import get_client
   client = get_client()
   statuses = client.get_space_statuses()
   for s in statuses:
       print(f"{s['status']} ({s['type']})")
   ```

## API Rate Limits

ClickUp API has rate limits:
- 100 requests per minute per API key
- 10 requests per second per API key

The scripts include basic rate limiting, but avoid running bulk operations too frequently.

## Security

- Never commit `.env.dev` or files containing API keys
- Store API keys in GitHub Secrets for Actions
- Use read-only API keys where possible
- Rotate API keys periodically
