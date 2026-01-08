# ClickUp Sync Enhancement Summary

**Date**: 06/01/2026
**Version**: 0.2.0

---

## Overview

Summary of enhancements made to the ClickUp integration, including custom field support (Story Points and MoSCoW Priority), subtask creation from markdown files, ClickUp ID writeback, mapping file generation, and enhanced sync scripts with comprehensive configuration.

## Table of Contents

- [ClickUp Sync Enhancement Summary](#clickup-sync-enhancement-summary)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [What Was Implemented](#what-was-implemented)
    - [1. Custom Field Support](#1-custom-field-support)
    - [2. Subtask Creation](#2-subtask-creation)
    - [3. ClickUp ID Writeback](#3-clickup-id-writeback)
    - [4. Mapping Files](#4-mapping-files)
  - [New Scripts](#new-scripts)
  - [Enhanced ClickUp Client](#enhanced-clickup-client)
  - [Configuration Updates](#configuration-updates)
  - [Setup Requirements](#setup-requirements)
  - [Usage Workflow](#usage-workflow)
  - [What Gets Updated](#what-gets-updated)
  - [Documentation](#documentation)
  - [Next Steps](#next-steps)
  - [Support](#support)

---

## What Was Implemented

Your ClickUp integration has been enhanced with the following features:

### 1. Custom Field Support

**Story Points:**

- Automatically extracts story points from `## Story Points (Fibonacci)` section
- Maps to ClickUp "Story Points" custom field (Number type)
- Example: `**Estimate:** 5` → ClickUp Story Points = 5

**MoSCoW Priority:**

- Automatically extracts priority from `## MoSCoW Priority` section
- Maps to ClickUp "MoSCoW Priority" custom field (Dropdown type)
- Options: Must Have, Should Have, Could Have, Won't Have
- Example: First priority found in section is used

### 2. Subtask Creation

- Parses `## Tasks` section in user stories
- Creates subtasks in ClickUp for each checkbox item
- Preserves task categories (Backend, Frontend Web, Frontend Mobile, Shared UI)
- Sets completion status based on checkbox state
- Example:

  ```markdown
  ### Backend Tasks

  - [ ] Create User model
  - [x] Implement email verification
  ```

  Creates:
  - `[Backend Tasks] Create User model` (Open)
  - `[Backend Tasks] Implement email verification` (Closed)

### 3. ClickUp ID Writeback

**Story Files:**

- After sync, story files are updated with ClickUp task ID
- Format: `<!-- CLICKUP_ID: abc123xyz -->` (added after title)
- Allows script to find and update existing tasks

**Sprint Files:**

- After sync, sprint files are updated with ClickUp list ID
- Format: `<!-- CLICKUP_LIST_ID: xyz789abc -->` (added after title)
- Allows script to link stories to correct sprint

### 4. Mapping Files

**Story Mapping** (`config/clickup-story-mapping.json`):

<!-- prettier-ignore -->
```json
{
  "US-001": "clickup_task_id_1",
  "US-002": "clickup_task_id_2"
}
```

**Sprint Mapping** (`config/clickup-sprint-mapping.json`):

<!-- prettier-ignore -->
```json
{
  "SPRINT-01": "clickup_list_id_1",
  "SPRINT-02": "clickup_list_id_2"
}
```

---

## New Scripts

### 1. `scripts/clickup/sync_stories_enhanced.py`

**Purpose:** Sync user stories to ClickUp with full custom field and subtask support

**Usage:**

```bash
# Preview what will be synced
python scripts/clickup/sync_stories_enhanced.py --dry-run

# Sync all stories
python scripts/clickup/sync_stories_enhanced.py

# Force update existing tasks
python scripts/clickup/sync_stories_enhanced.py --force
```

**Features:**

- ✅ Creates tasks in ClickUp backlog
- ✅ Sets Story Points custom field
- ✅ Sets MoSCoW Priority custom field
- ✅ Creates subtasks from Tasks section
- ✅ Writes ClickUp task ID to story file
- ✅ Generates story mapping file
- ✅ Dry-run mode for safe testing

### 2. `scripts/clickup/sync_sprints.py`

**Purpose:** Sync sprint files to ClickUp and link stories

**Usage:**

```bash
# Preview what will be synced
python scripts/clickup/sync_sprints.py --dry-run

# Sync all sprints
python scripts/clickup/sync_sprints.py

# Force update existing sprints
python scripts/clickup/sync_sprints.py --force
```

**Features:**

- ✅ Finds sprint lists in ClickUp
- ✅ Links user stories to sprint lists
- ✅ Writes ClickUp list ID to sprint file
- ✅ Generates sprint mapping file
- ✅ Dry-run mode for safe testing

**Note:** Sprint lists must be created manually in ClickUp before syncing.

---

## Enhanced ClickUp Client

The `scripts/clickup/clickup_client.py` file now includes:

**New Methods:**

```python
# Set custom field value
client.set_custom_field(task_id, field_id, value)

# Get all custom fields for a list
client.get_list_custom_fields(list_id)

# Find custom field by name
field = client.find_custom_field_by_name(list_id, "Story Points")

# Create subtask
client.create_subtask(parent_task_id, name, description, status)
```

---

## Configuration Updates

### `config/clickup-config.json`

Added custom field configuration:

```json
{
  "field_mapping": {
    "story_points": "Story Points",
    "moscow_priority": "MoSCoW Priority",
    "sprint": "list",
    "assignee": "assignee"
  },
  "custom_field_types": {
    "Story Points": "number",
    "MoSCoW Priority": "drop_down"
  },
  "moscow_priority_options": {
    "Must Have": "must_have",
    "Should Have": "should_have",
    "Could Have": "could_have",
    "Won't Have": "wont_have"
  }
}
```

---

## Setup Requirements

### Before First Sync

1. **Create Custom Fields in ClickUp** (One-time setup):
   - Go to your ClickUp Space settings
   - Navigate to Custom Fields
   - Create:
     - **Story Points** (Type: Number)
     - **MoSCoW Priority** (Type: Dropdown)
       - Options: Must Have, Should Have, Could Have, Won't Have
   - Apply these fields to your Backlog list and Sprint lists

2. **Set Environment Variables**:
   - Ensure all ClickUp IDs are in `.env.dev`:
     ```bash
     CLICKUP_API_TOKEN=pk_your_token_here
     CLICKUP_WORKSPACE_ID=your_workspace_id
     CLICKUP_SPACE_ID=your_space_id
     CLICKUP_BACKLOG_FOLDER_ID=your_backlog_folder_id
     CLICKUP_SPRINT_FOLDER_ID=your_sprint_folder_id
     CLICKUP_BACKLOG_LIST_ID=your_backlog_list_id
     ```

3. **Create Sprint Lists in ClickUp** (For sprint sync):
   - Manually create a list for each sprint in your Sprint folder
   - Name format: "SPRINT-01: Core Authentication"

---

## Usage Workflow

### Complete Sync Process

```bash
# 1. Preview story sync
python scripts/clickup/sync_stories_enhanced.py --dry-run

# 2. Sync stories to ClickUp
python scripts/clickup/sync_stories_enhanced.py

# 3. Verify in ClickUp
# - Check tasks created in backlog
# - Verify Story Points field
# - Verify MoSCoW Priority field
# - Check subtasks created

# 4. Create sprint lists in ClickUp (manual)

# 5. Preview sprint sync
python scripts/clickup/sync_sprints.py --dry-run

# 6. Sync sprints
python scripts/clickup/sync_sprints.py

# 7. Commit updated files
git add docs/STORIES/*.md docs/SPRINTS/*.md config/*.json
git commit -m "Sync stories and sprints to ClickUp"
git push
```

---

## What Gets Updated

### Story Files

Before:

```markdown
# User Story: User Authentication with Email and Password

## Story

...
```

After:

```markdown
# User Story: User Authentication with Email and Password

<!-- CLICKUP_ID: abc123xyz -->

## Story

...
```

### Sprint Files

Before:

```markdown
# Sprint 1: Core Authentication

**Sprint Duration:** 06/01/2026 - 20/01/2026
```

After:

```markdown
# Sprint 1: Core Authentication

<!-- CLICKUP_LIST_ID: xyz789abc -->

**Sprint Duration:** 06/01/2026 - 20/01/2026
```

### Generated Mapping Files

- `config/clickup-story-mapping.json` (auto-generated)
- `config/clickup-sprint-mapping.json` (auto-generated)

Both should be committed to version control for GitHub Actions to use.

---

## Documentation

### Updated Files

- `scripts/clickup/README.md` - Added documentation for enhanced scripts
- `scripts/clickup/clickup_client.py` - Enhanced with new methods
- `config/clickup-config.json` - Added custom field mappings
- `docs/PM-INTEGRATION/INTEGRATION-STATUS.md` - Updated with new features

### Complete Documentation

See:

- `scripts/clickup/README.md` - Complete script usage guide
- `docs/PM-INTEGRATION/INTEGRATION-STATUS.md` - Integration status and quick start
- `docs/PM-INTEGRATION/README.MD` - Main PM integration guide

---

## Next Steps

1. **Create Custom Fields in ClickUp:**
   - Story Points (Number)
   - MoSCoW Priority (Dropdown with 4 options)

2. **Run Dry-Run Sync:**

   ```bash
   python scripts/clickup/sync_stories_enhanced.py --dry-run
   ```

3. **Run Actual Sync:**

   ```bash
   python scripts/clickup/sync_stories_enhanced.py
   ```

4. **Verify Results in ClickUp:**
   - Check tasks in backlog
   - Verify custom fields populated
   - Check subtasks created

5. **Create Sprint Lists:**
   - Manually create lists in ClickUp Sprint folder

6. **Sync Sprints:**

   ```bash
   python scripts/clickup/sync_sprints.py
   ```

7. **Commit Changes:**
   ```bash
   git add docs/STORIES/*.md docs/SPRINTS/*.md config/*.json
   git commit -m "Sync stories and sprints to ClickUp"
   git push
   ```

---

## Support

For issues or questions:

- Check `scripts/clickup/README.md` for detailed usage
- Review `docs/PM-INTEGRATION/INTEGRATION-STATUS.md` for troubleshooting
- Verify custom fields exist in ClickUp
- Check environment variables are set correctly

---

**All features are implemented and ready to use!**
