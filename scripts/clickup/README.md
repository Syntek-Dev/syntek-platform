# ClickUp Integration Scripts

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team

---

Collection of Python scripts for syncing user stories, sprints, and tasks between local
markdown files and ClickUp project management system.

## Table of Contents

- [ClickUp Integration Scripts](#clickup-integration-scripts)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Quick Start](#quick-start)
  - [Scripts](#scripts)
    - [sync_sprint_stories.py (Recommended)](#sync_sprint_storiespy-recommended)
    - [sync_stories_enhanced.py](#sync_stories_enhancedpy)
    - [sync_sprints.py](#sync_sprintspy)
    - [pull_tasks.py](#pull_taskspy)
    - [clickup_client.py](#clickup_clientpy)
  - [Workflow Comparison](#workflow-comparison)
    - [Integrated Workflow (Recommended)](#integrated-workflow-recommended)
    - [Separate Scripts Workflow](#separate-scripts-workflow)
  - [Common Issues and Solutions](#common-issues-and-solutions)
    - [Issue: Stories Not Moving to Sprint Lists](#issue-stories-not-moving-to-sprint-lists)
    - [Issue: Custom Fields Not Set](#issue-custom-fields-not-set)
    - [Issue: Subtasks Not Created](#issue-subtasks-not-created)
  - [File Structure](#file-structure)

## Overview

These scripts provide bidirectional synchronisation between:

- **Local:** Markdown files in `docs/STORIES/` and `docs/SPRINTS/`
- **ClickUp:** Tasks in backlog and sprint lists

**Key Features:**

- Create/update stories in ClickUp from markdown files
- Set custom fields (Story Points, MoSCoW Priority)
- Create subtasks from Tasks section
- Create sprint lists in ClickUp
- Move stories from backlog to sprint lists
- Pull existing tasks from ClickUp to generate ID mappings

## Quick Start

1. Set up environment variables in `.env.dev`:

   ```bash
   export CLICKUP_API_TOKEN="your-api-token"
   export CLICKUP_WORKSPACE_ID="your-workspace-id"
   export CLICKUP_SPACE_ID="your-space-id"
   export CLICKUP_SPRINT_FOLDER_ID="sprint-folder-id"
   export CLICKUP_BACKLOG_FOLDER_ID="backlog-folder-id"
   export CLICKUP_BACKLOG_LIST_ID="backlog-list-id"
   ```

2. Install dependencies:

   ```bash
   pip install requests
   ```

3. Run the integrated sync:

   ```bash
   # Preview changes
   python scripts/clickup/sync_sprint_stories.py --dry-run

   # Apply changes
   python scripts/clickup/sync_sprint_stories.py
   ```

## Scripts

### sync_sprint_stories.py (Recommended)

**Purpose:** Integrated workflow that handles story metadata, sprint creation, and story
movement in one command.

**What it does:**

1. Reads sprint files to identify story assignments
2. Updates story markdown files with `**Sprint:**` metadata
3. Syncs stories to ClickUp (creates if missing)
4. Creates sprint lists in ClickUp
5. Moves stories from backlog to sprint lists

**Usage:**

```bash
# Full sync of all sprints
python scripts/clickup/sync_sprint_stories.py

# Preview changes without applying
python scripts/clickup/sync_sprint_stories.py --dry-run

# Sync specific sprint only
python scripts/clickup/sync_sprint_stories.py --sprint SPRINT-01

# Skip updating story files (if you've already added Sprint metadata manually)
python scripts/clickup/sync_sprint_stories.py --skip-story-metadata
```

**When to use:**

- You have sprint files in `docs/SPRINTS/` with story assignments
- You want stories automatically moved to the correct sprint lists
- First-time setup or major reorganisation

**Prerequisites:**

- Sprint files must exist in `docs/SPRINTS/` with MoSCoW tables
- Stories must already be created in ClickUp (run `sync_stories_enhanced.py` first if not)

### sync_stories_enhanced.py

**Purpose:** Create or update stories in the backlog with custom fields and subtasks.

**What it does:**

1. Parses story markdown files
2. Creates/updates tasks in ClickUp backlog
3. Sets custom fields (Story Points, MoSCoW Priority)
4. Creates subtasks from Tasks section
5. Writes ClickUp task ID back to markdown file

**Usage:**

```bash
# Sync all stories to backlog
python scripts/clickup/sync_stories_enhanced.py

# Preview changes
python scripts/clickup/sync_stories_enhanced.py --dry-run

# Force update existing stories
python scripts/clickup/sync_stories_enhanced.py --force

# Sync specific folder
python scripts/clickup/sync_stories_enhanced.py --folder-path docs/STORIES
```

**When to use:**

- Creating new stories in ClickUp
- Updating story descriptions or acceptance criteria
- Setting up custom fields for the first time
- Before running sprint sync (if stories don't exist yet)

**Output:**

- Updates `config/clickup-story-mapping.json` with story ID to task ID mappings
- Adds `<!-- CLICKUP_ID: xxx -->` to story markdown files

### sync_sprints.py

**Purpose:** Create sprint lists and move stories that already have sprint metadata.

**What it does:**

1. Parses sprint markdown files
2. Creates sprint lists in ClickUp
3. Moves stories to sprint lists (requires `**Sprint:**` metadata in story files)

**Usage:**

```bash
# Sync all sprints
python scripts/clickup/sync_sprints.py

# Preview changes
python scripts/clickup/sync_sprints.py --dry-run

# Force update existing sprint lists
python scripts/clickup/sync_sprints.py --force
```

**When to use:**

- Stories already have `**Sprint:**` metadata
- You want more control over the sync process
- Updating sprint descriptions or goals

**Important:** This script will NOT add sprint metadata to story files. Stories must
already have `**Sprint:** Sprint XX` in their markdown files.

**Output:**

- Updates `config/clickup-sprint-mapping.json` with sprint ID to list ID mappings
- Adds `<!-- CLICKUP_LIST_ID: xxx -->` to sprint markdown files

### pull_tasks.py

**Purpose:** Fetch existing tasks from ClickUp to generate ID mappings.

**What it does:**

1. Fetches all tasks from ClickUp workspace
2. Extracts story IDs from task names
3. Creates mapping files for use by other scripts

**Usage:**

```bash
# Pull all open tasks
python scripts/clickup/pull_tasks.py

# Include closed tasks
python scripts/clickup/pull_tasks.py --include-closed

# Save to custom location
python scripts/clickup/pull_tasks.py --output /tmp/tasks.json
```

**When to use:**

- Setting up integration for the first time
- After manually creating tasks in ClickUp
- When GitHub Actions can't find task mappings
- Periodically to refresh mappings

**Output:**

- `config/clickup-tasks.json` - Full task details
- `config/clickup-story-mapping.json` - Story ID to task ID mapping

### clickup_client.py

**Purpose:** Python client library for ClickUp API v2.

**What it provides:**

- Authentication handling
- HTTP request wrapper
- Methods for tasks, lists, folders, custom fields
- Environment variable resolution for config

**Not a standalone script** - imported by other scripts.

## Workflow Comparison

### Integrated Workflow (Recommended)

**Best for:** First-time setup, sprint planning, major reorganisations

```bash
# Step 1: Create stories in backlog (if not already in ClickUp)
python scripts/clickup/sync_stories_enhanced.py

# Step 2: Run integrated sync (adds sprint metadata, creates sprint lists, moves stories)
python scripts/clickup/sync_sprint_stories.py --dry-run  # Preview
python scripts/clickup/sync_sprint_stories.py            # Apply
```

**Advantages:**

- Single command to handle everything
- Automatically adds sprint metadata to story files
- Fewer chances for errors
- Clear preview with dry-run mode

### Separate Scripts Workflow

**Best for:** Ongoing maintenance, individual story updates

```bash
# Step 1: Create/update stories in backlog
python scripts/clickup/sync_stories_enhanced.py

# Step 2: Manually add **Sprint:** metadata to story files
# Edit docs/STORIES/US-XXX.md and add: **Sprint:** Sprint 01

# Step 3: Create sprint lists and move stories
python scripts/clickup/sync_sprints.py
```

**Advantages:**

- More control over each step
- Update stories without affecting sprint assignments
- Useful for incremental changes

## Common Issues and Solutions

### Issue: Stories Not Moving to Sprint Lists

**Symptoms:**

- Sprint lists created in ClickUp
- Stories remain in backlog
- No errors reported

**Cause:** Stories don't have `**Sprint:**` metadata in markdown files.

**Solution:**

Use the integrated sync script:

```bash
python scripts/clickup/sync_sprint_stories.py
```

Or manually add `**Sprint:** Sprint 01` to each story file and run:

```bash
python scripts/clickup/sync_sprints.py
```

### Issue: Custom Fields Not Set

**Symptoms:**

- Stories created in ClickUp
- Story Points or MoSCoW Priority fields are empty

**Cause:** Story files missing MoSCoW Priority or Story Points sections.

**Solution:**

1. Ensure story files have these sections:

   ```markdown
   ## MoSCoW Priority

   - **Must Have:** Description

   ## Story Points (Fibonacci)

   **Estimate:** 5
   ```

2. Re-sync with force flag:

   ```bash
   python scripts/clickup/sync_stories_enhanced.py --force
   ```

### Issue: Subtasks Not Created

**Symptoms:**

- Story created in ClickUp
- No subtasks appear

**Cause:** Story file missing Tasks section or incorrect format.

**Solution:**

1. Add Tasks section to story file:

   ```markdown
   ## Tasks

   ### Backend Tasks

   - [ ] Create User model
   - [ ] Add email verification

   ### Frontend Tasks

   - [ ] Create registration form
   ```

2. Re-sync with force flag:

   ```bash
   python scripts/clickup/sync_stories_enhanced.py --force
   ```

## File Structure

```
scripts/clickup/
├── README.md                      # This file
├── clickup_client.py              # ClickUp API client library
├── sync_sprint_stories.py         # Integrated sync (recommended)
├── sync_stories_enhanced.py       # Sync stories to backlog
├── sync_sprints.py                # Create sprint lists and move stories
├── pull_tasks.py                  # Fetch tasks from ClickUp
└── sync_stories.py                # Basic story sync (deprecated)

config/
├── clickup-config.json            # ClickUp configuration
├── clickup-story-mapping.json     # Story ID to task ID mapping
├── clickup-sprint-mapping.json    # Sprint ID to list ID mapping
└── clickup-tasks.json             # Full task data from ClickUp

docs/
├── STORIES/                       # User story markdown files
│   ├── US-001-*.md
│   └── US-002-*.md
└── SPRINTS/                       # Sprint planning files
    ├── SPRINT-01-*.md
    └── SPRINT-02-*.md
```

---

For complete documentation, see `docs/PM-INTEGRATION/README.md`.
