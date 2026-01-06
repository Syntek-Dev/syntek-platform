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
    - [1. clickup_client.py](#1-clickup_clientpy)
    - [2. sync_stories.py](#2-sync_storiespy)
    - [3. pull_tasks.py](#3-pull_taskspy)
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
CLICKUP_API_TOKEN=pk_your_actual_token_here
CLICKUP_WORKSPACE_ID=
CLICKUP_SPACE_ID=
CLICKUP_SPRINT_FOLDER_ID=
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

**Features:**

- Task creation, updates, and status management
- Custom field management (Story Points, MoSCoW Priority)
- Subtask creation
- Search and query tasks
- List and folder management

**Usage:**

```python
from clickup_client import get_client

# Initialize client (reads CLICKUP_API_TOKEN from environment)
client = get_client()

# Get folder details
folder = client.get_folder(os.getenv("CLICKUP_SPRINT_FOLDER_ID"))

# Create a task
task = client.create_task(
    list_id=os.getenv("CLICKUP_BACKLOG_LIST_ID"),
    name="US-001: User Authentication",
    description="Implement user login and registration",
    status="Open",
    priority=2,
    tags=["must-have"]
)

# Set custom fields
points_field = client.find_custom_field_by_name(list_id, "Story Points")
client.set_custom_field(task["id"], points_field["id"], 5)

moscow_field = client.find_custom_field_by_name(list_id, "MoSCoW Priority")
client.set_custom_field(task["id"], moscow_field["id"], 0)  # 0 = Must Have

# Create subtasks
subtask = client.create_subtask(
    parent_task_id=task["id"],
    name="[Backend] Create User model",
    status="Open"
)

# Update task status
client.update_task_status(task["id"], "in progress")
```

### 2. sync_stories_enhanced.py (Recommended)

Enhanced sync for user stories from `docs/STORIES/` directory to ClickUp with full support for:

- Custom fields (Story Points, MoSCoW Priority)
- Subtasks from the Tasks section
- ClickUp ID writeback to markdown files

**Usage:**

```bash
# Sync all stories to ClickUp
python scripts/clickup/sync_stories_enhanced.py

# Preview changes without syncing
python scripts/clickup/sync_stories_enhanced.py --dry-run

# Force update existing tasks
python scripts/clickup/sync_stories_enhanced.py --force
```

**Features:**

- Parses user story markdown files (US-001-\*.md format)
- Creates or updates tasks in ClickUp backlog
- Sets "Story Points" custom field from story file
- Sets "MoSCoW Priority" custom field (Must Have, Should Have, Could Have, Won't Have)
- Creates subtasks from the ## Tasks section
- Writes ClickUp task ID back to the markdown file as HTML comment
- Saves story ID to ClickUp task ID mapping in `config/clickup-story-mapping.json`

**Story File Format:**

Stories should be markdown files named `US-XXX-DESCRIPTION.md`:

```markdown
# User Story: User Authentication with Email and Password

<!-- CLICKUP_ID: abc123 -->

## Story

**As a** new user
**I want** to create an account
**So that** I can access the platform

## MoSCoW Priority

- **Must Have:** User registration with validation
- **Should Have:** Welcome email notification
- **Could Have:** Social login integration
- **Won't Have:** Third-party federation

## Acceptance Criteria

### Scenario 1: Successful Registration

**Given** the registration page is open
**When** a user enters valid details
**Then** an account is created

## Tasks

### Backend Tasks

- [ ] Create User model extending AbstractUser
- [ ] Implement email verification system
- [ ] Create registration GraphQL mutation

### Frontend Web Tasks

- [ ] Create registration form component
- [ ] Implement email verification page

## Story Points (Fibonacci)

**Estimate:** 5
```

### 3. sync_sprints.py

Sync sprint files from `docs/SPRINTS/` directory to ClickUp.

**Usage:**

```bash
# Sync all sprints to ClickUp
python scripts/clickup/sync_sprints.py

# Preview changes without syncing
python scripts/clickup/sync_sprints.py --dry-run

# Force update existing sprints
python scripts/clickup/sync_sprints.py --force
```

**Features:**

- Parses sprint markdown files (SPRINT-01-\*.md format)
- Finds or references sprint lists in ClickUp
- Links user stories to sprint lists
- Writes ClickUp list ID back to sprint markdown file
- Saves sprint ID to ClickUp list ID mapping in `config/clickup-sprint-mapping.json`

**Note:** Sprint lists must be created manually in ClickUp first. This script will link existing stories to the sprint lists.

**Sprint File Format:**

```markdown
# Sprint 1: Core Authentication

<!-- CLICKUP_LIST_ID: xyz789 -->

**Sprint Duration:** 06/01/2026 - 20/01/2026 (2 weeks)
**Capacity:** 10/11 points
**Status:** Planned

## Sprint Goal

Establish the foundational authentication system.

## MoSCoW Breakdown

### Must Have (10 points)

| Story ID                                           | Title               | Points | Status  |
| -------------------------------------------------- | ------------------- | ------ | ------- |
| [US-001](../STORIES/US-001-USER-AUTHENTICATION.md) | User Authentication | 5      | Pending |
| [US-003](../STORIES/US-003-PASSWORD-RESET.md)      | Password Reset      | 5      | Pending |
```

### 4. sync_stories.py (Legacy)

Original sync script for basic user story syncing. Use `sync_stories_enhanced.py` instead for full feature support.

**Usage:**

```bash
# Sync all stories
python scripts/clickup/sync_stories.py

# Preview changes without syncing
python scripts/clickup/sync_stories.py --dry-run
```

### 5. pull_tasks.py

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

**Note:** This is useful for pulling back task IDs created outside the sync scripts.

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

| Event     | Target Branch | ClickUp Status |
| --------- | ------------- | -------------- |
| PR opened | any           | in review      |
| PR merged | main          | Closed         |
| PR merged | staging       | accepted       |
| PR merged | dev           | in progress    |
| Push      | main          | Closed         |
| Push      | staging       | accepted       |
| Push      | dev           | in progress    |
| Push      | testing       | in review      |

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

## Quick Start Guide

### First-Time Setup

1. **Configure ClickUp Custom Fields** (One-time setup in ClickUp UI):
   - Go to your ClickUp Space settings
   - Navigate to Custom Fields
   - Create two custom fields:
     - **Story Points** (Type: Number)
     - **MoSCoW Priority** (Type: Dropdown with options: Must Have, Should Have, Could Have, Won't Have)
   - Apply these fields to your lists

2. **Set Environment Variables**:

   ```bash
   # Add to your .env.dev file
   CLICKUP_API_TOKEN=pk_your_token_here
   CLICKUP_WORKSPACE_ID=your_workspace_id
   CLICKUP_SPACE_ID=your_space_id
   CLICKUP_BACKLOG_FOLDER_ID=your_backlog_folder_id
   CLICKUP_SPRINT_FOLDER_ID=your_sprint_folder_id
   CLICKUP_BACKLOG_LIST_ID=your_backlog_list_id
   ```

3. **Install Dependencies**:
   ```bash
   pip install requests>=2.31.0
   ```

### Syncing User Stories to ClickUp

1. **First Sync** (Preview mode):

   ```bash
   python scripts/clickup/sync_stories_enhanced.py --dry-run
   ```

2. **Actual Sync**:

   ```bash
   python scripts/clickup/sync_stories_enhanced.py
   ```

3. **Check Results**:
   - User stories are created in your ClickUp backlog
   - Story Points custom field is set
   - MoSCoW Priority custom field is set
   - Subtasks are created from the Tasks section
   - ClickUp task IDs are written back to story files
   - Mapping saved to `config/clickup-story-mapping.json`

### Syncing Sprints to ClickUp

1. **Create Sprint Lists in ClickUp** (Manual step):
   - Go to your Sprint folder in ClickUp
   - Create a list for each sprint (e.g., "SPRINT-01: Core Authentication")

2. **Sync Sprints** (Preview mode):

   ```bash
   python scripts/clickup/sync_sprints.py --dry-run
   ```

3. **Actual Sync**:

   ```bash
   python scripts/clickup/sync_sprints.py
   ```

4. **Check Results**:
   - Sprint list IDs are written back to sprint files
   - User stories are linked to sprint lists
   - Mapping saved to `config/clickup-sprint-mapping.json`

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
# Verify API token is set
echo $CLICKUP_API_TOKEN

# Test API access
curl -H "Authorization: $CLICKUP_API_TOKEN" \
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
