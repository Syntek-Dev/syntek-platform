# ClickUp Integration Status

**Last Updated**: 06/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [ClickUp Integration Status](#clickup-integration-status)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Integration Status: READY](#integration-status-ready)
  - [What's Already Configured](#whats-already-configured)
    - [Environment Variables](#environment-variables)
    - [Configuration Files](#configuration-files)
    - [GitHub Actions Workflows](#github-actions-workflows)
    - [Python Scripts](#python-scripts)
    - [Documentation](#documentation)
  - [Required Setup Steps](#required-setup-steps)
    - [1. Set Your API Token](#1-set-your-api-token)
    - [2. Configure GitHub Secret](#2-configure-github-secret)
    - [3. Test the Integration](#3-test-the-integration)
  - [ClickUp Workspace Details](#clickup-workspace-details)
  - [CRITICAL: Environment Variable Name](#critical-environment-variable-name)
  - [Security Checklist](#security-checklist)
  - [Quick Start Commands](#quick-start-commands)
  - [What Happens Automatically](#what-happens-automatically)
  - [Testing the Integration](#testing-the-integration)
  - [Troubleshooting](#troubleshooting)
  - [Support Documentation](#support-documentation)

## Overview

The ClickUp integration is **fully configured and ready to use**. All infrastructure, workflows,
and scripts are in place. You only need to add your API token to start using the integration.

## Integration Status: READY

| Component             | Status      | Notes                                                  |
| --------------------- | ----------- | ------------------------------------------------------ |
| Configuration Files   | ✅ Complete | `config/clickup-config.json` configured                |
| Environment Templates | ✅ Complete | All `.env.*.example` files have ClickUp variables      |
| GitHub Actions        | ✅ Complete | Two workflows configured and tested                    |
| Python Scripts        | ✅ Complete | Enhanced client with custom fields and subtasks        |
| Story Sync Enhanced   | ✅ Complete | Custom fields + subtasks support                       |
| Sprint Sync           | ✅ Complete | Sprint list linking and ID writeback                   |
| Documentation         | ✅ Complete | Comprehensive guides available                         |
| API Token             | ⚠️ Required | You must add your token                                |
| GitHub Secret         | ⚠️ Required | You must add `CLICKUP_API_TOKEN` secret                |
| Custom Fields Setup   | ⚠️ Required | Create "Story Points" and "MoSCoW Priority" in ClickUp |

## What's Already Configured

### Environment Variables

All environment files have ClickUp variables pre-configured:

**`.env.dev.example`**

```bash
CLICKUP_API_TOKEN=
CLICKUP_WORKSPACE_ID=
CLICKUP_SPACE_ID=
CLICKUP_BACKLOG_FOLDER_ID=
CLICKUP_SPRINT_FOLDER_ID=
CLICKUP_BACKLOG_LIST_ID=
```

**Workspace IDs:**
All IDs are configured via environment variables. The actual IDs are stored in your `.env.*` files
(not committed to version control).

- Workspace ID: `${CLICKUP_WORKSPACE_ID}`
- Space ID: `${CLICKUP_SPACE_ID}`
- Sprint Folder ID: `${CLICKUP_SPRINT_FOLDER_ID}`
- Backlog Folder ID: `${CLICKUP_BACKLOG_FOLDER_ID}`
- Backlog List ID: `${CLICKUP_BACKLOG_LIST_ID}`

### Configuration Files

**`config/clickup-config.json`**

- Status mappings configured
- Branch naming patterns defined
- Field mappings set
- Priority mappings established
- Notification preferences configured

### GitHub Actions Workflows

**`.github/workflows/clickup-sync.yml`**

- Triggers on push to main, staging, dev, testing
- Triggers on PR open, sync, close, reopen
- Updates task status based on branch/event
- Adds PR comments to ClickUp tasks

**`.github/workflows/clickup-branch-sync.yml`**

- Triggers on branch creation matching `us*/**`
- Updates task to "in progress"
- Adds branch creation comment to task

### Python Scripts

**`scripts/clickup/clickup_client.py`**

- Full ClickUp API client
- Handles authentication
- Methods for tasks, lists, folders, statuses

**`scripts/clickup/pull_tasks.py`**

- Pulls tasks from ClickUp
- Generates task mapping files
- Supports closed tasks and custom output

**`scripts/clickup/sync_stories.py`** (Legacy)

- Basic story sync to ClickUp
- Supports dry-run mode

**`scripts/clickup/sync_stories_enhanced.py`** (Recommended)

- Enhanced story sync with custom fields
- Sets Story Points and MoSCoW Priority fields
- Creates subtasks from Tasks section
- Writes ClickUp task IDs back to markdown files
- Generates story mapping file

**`scripts/clickup/sync_sprints.py`**

- Syncs sprint files to ClickUp
- Links stories to sprint lists
- Writes ClickUp list IDs back to markdown files
- Generates sprint mapping file

### Documentation

Complete documentation available in `docs/PM-INTEGRATION/`:

- `README.MD` - Main integration guide
- `SETUP-GUIDE.md` - Step-by-step setup
- `TROUBLESHOOTING.md` - Common issues and solutions
- `GITHUB-SECRETS.md` - Secret configuration guide
- `QUICK-REFERENCE.md` - Command reference
- `CLICKUP-INTEGRATION-SUMMARY.md` - Detailed overview

## Enhanced Features (New)

### Custom Field Mapping

The enhanced sync scripts now support ClickUp custom fields:

**Story Points:**

- Custom field name: "Story Points"
- Type: Number
- Source: `## Story Points (Fibonacci)` section in markdown, `**Estimate:** N`
- Auto-populated during sync

**MoSCoW Priority:**

- Custom field name: "MoSCoW Priority"
- Type: Dropdown
- Options: Must Have, Should Have, Could Have, Won't Have
- Source: `## MoSCoW Priority` section in markdown
- Auto-populated during sync

### Subtask Creation

Tasks from the `## Tasks` section in user stories are automatically created as subtasks:

```markdown
## Tasks

### Backend Tasks

- [ ] Create User model
- [x] Implement email verification

### Frontend Web Tasks

- [ ] Create registration form
```

Each checkbox becomes a subtask in ClickUp with:

- Category prefix (e.g., `[Backend]`, `[Frontend Web]`)
- Completion status (Open or Closed based on checkbox)
- Linked to parent story

### ClickUp ID Writeback

After syncing, story and sprint files are updated with ClickUp IDs:

**Story files:**

```markdown
# User Story: User Authentication

<!-- CLICKUP_ID: abc123xyz -->
```

**Sprint files:**

```markdown
# Sprint 1: Core Authentication

<!-- CLICKUP_LIST_ID: xyz789abc -->
```

### Mapping Files Generated

- `config/clickup-story-mapping.json` - Story ID to ClickUp task ID
- `config/clickup-sprint-mapping.json` - Sprint ID to ClickUp list ID

## Required Setup Steps

### 0. Create Custom Fields in ClickUp (One-Time)

**IMPORTANT:** Create these custom fields in your ClickUp Space before running enhanced sync:

1. Go to ClickUp Space settings
2. Navigate to **Custom Fields**
3. Create:
   - **Story Points** (Type: Number)
   - **MoSCoW Priority** (Type: Dropdown)
     - Options: Must Have, Should Have, Could Have, Won't Have
4. Apply these fields to your Backlog list and all Sprint lists

### 1. Set Your API Token

**Get your ClickUp API token:**

1. Log in to ClickUp
2. Click your avatar (bottom left)
3. Go to **Settings**
4. Navigate to **Apps** section
5. Scroll to **API Token**
6. Click **Generate** or copy existing token

**Add to your local environment:**

```bash
# Copy the example file
cp .env.dev.example .env.dev

# Edit .env.dev and add your token
# CLICKUP_API_TOKEN=pk_your_token_here
```

**For other environments:**

- Copy and configure `.env.staging.example` → `.env.staging`
- Copy and configure `.env.production.example` → `.env.production`

### 2. Configure GitHub Secret

**Add `CLICKUP_API_TOKEN` secret to GitHub:**

1. Go to your GitHub repository
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Name: `CLICKUP_API_TOKEN`
5. Value: Your ClickUp API token (starts with `pk_`)
6. Click **Add secret**

### 3. Test the Integration

```bash
# Pull task mapping from ClickUp
export CLICKUP_API_TOKEN=pk_your_token_here
python scripts/clickup/pull_tasks.py

# Commit the mapping
git add config/clickup-story-mapping.json config/clickup-tasks.json
git commit -m "Add ClickUp task mapping"
git push

# Test branch creation (creates a branch matching us{number}/ pattern)
# This will trigger GitHub Actions to update ClickUp
```

## ClickUp Workspace Details

**Workspace:** Syntek

**Space:** Syntek

**Folders:**

1. **Sprint - Backend Template**
   - Contains sprint lists (Sprint 01, Sprint 02, etc.)
   - For active development work

2. **Backlog - Backend Template**
   - Main backlog list
   - All unassigned stories start here

**Note:** Actual IDs are configured via environment variables and should not be committed to
version control.

**Available Statuses:**

- Open (backlog)
- pending (ready)
- in progress (active development)
- in review (PR opened)
- accepted (merged to staging)
- accepted customer
- rejected
- rejected customer
- blocked
- completed
- client accepted
- client rejected
- Closed (merged to main)

## CRITICAL: Environment Variable Name

**Use `CLICKUP_API_TOKEN` not `CLICKUP_API_KEY`**

The correct environment variable name is **`CLICKUP_API_TOKEN`** in:

- All `.env.*` files
- GitHub Secrets
- Python scripts
- GitHub Actions workflows

Some older documentation may reference `CLICKUP_API_KEY` - this is incorrect and should be `CLICKUP_API_TOKEN`.

## Security Checklist

- [ ] API token stored in `.env.dev` (gitignored)
- [ ] `.env.dev` is in `.gitignore`
- [ ] GitHub Secret `CLICKUP_API_TOKEN` added
- [ ] No tokens committed to version control
- [ ] Workspace IDs in config file (not secrets)
- [ ] API token starts with `pk_`

## Quick Start Commands

### Option 1: Enhanced Sync (Recommended)

```bash
# 1. Set up environment
cp .env.dev.example .env.dev
# Edit .env.dev and add CLICKUP_API_TOKEN and all other IDs

# 2. Create custom fields in ClickUp (one-time setup)
# - Story Points (Number)
# - MoSCoW Priority (Dropdown: Must Have, Should Have, Could Have, Won't Have)

# 3. Sync user stories to ClickUp (preview first)
python scripts/clickup/sync_stories_enhanced.py --dry-run

# 4. Actual sync
python scripts/clickup/sync_stories_enhanced.py

# 5. Check results
# - Stories created in ClickUp backlog
# - Story Points field populated
# - MoSCoW Priority field set
# - Subtasks created
# - ClickUp IDs written to story files

# 6. Create sprint lists manually in ClickUp
# In Sprint folder, create: "SPRINT-01: Core Authentication", etc.

# 7. Sync sprints (preview first)
python scripts/clickup/sync_sprints.py --dry-run

# 8. Actual sprint sync
python scripts/clickup/sync_sprints.py

# 9. Commit updated files
git add docs/STORIES/*.md docs/SPRINTS/*.md config/*.json
git commit -m "Sync stories and sprints to ClickUp"
git push
```

### Option 2: Basic Sync (Legacy)

```bash
# 1. Set up environment
cp .env.dev.example .env.dev
# Edit .env.dev and add CLICKUP_API_TOKEN

# 2. Export token
export CLICKUP_API_TOKEN=pk_your_token_here

# 3. Pull tasks from ClickUp
python scripts/clickup/pull_tasks.py

# 4. Commit mapping files
git add config/clickup-story-mapping.json config/clickup-tasks.json
git commit -m "Add ClickUp task mapping"
git push

# 5. Create feature branch (must match us{number}/ pattern)
git checkout -b us123/test-feature
git push origin us123/test-feature

# 6. Check ClickUp - task US-123 should be "in progress"
```

## What Happens Automatically

When you create a branch matching `us{number}/feature-name`:

1. GitHub Actions extracts the task number
2. Looks up ClickUp task ID from mapping file
3. Updates task status to "in progress"
4. Adds comment with branch details

When you create a PR:

1. Task status changes to "in review"
2. Comment added with PR link

When PR merges:

- To `staging`: status changes to "accepted"
- To `main`: status changes to "Closed"

## Testing the Integration

**Create a test task in ClickUp:**

1. Go to Backlog list
2. Create task: `US-999: Test Integration`
3. Note the task number

**Pull and test:**

```bash
# Pull task mapping
python scripts/clickup/pull_tasks.py

# Create test branch
git checkout -b us999/test-integration
git push origin us999/test-integration

# Check ClickUp - task should be "in progress"

# Create PR
echo "Test" > test.md
git add test.md
git commit -m "Test ClickUp sync"
git push

# Create PR via GitHub (web or CLI)
# Check ClickUp - task should be "in review"
```

## Troubleshooting

**API token not working:**

- Verify token starts with `pk_`
- Check no extra spaces or newlines
- Regenerate token in ClickUp if needed

**GitHub Actions not running:**

- Verify `CLICKUP_API_TOKEN` secret exists in GitHub
- Check Actions are enabled in repository settings
- Review Actions tab for errors

**Task not found:**

- Run `python scripts/clickup/pull_tasks.py` to refresh mapping
- Commit and push `config/clickup-story-mapping.json`
- Ensure task name starts with `US-XXX:`

**Status update fails:**

- Verify status name matches exactly (case-sensitive)
- Check status exists in ClickUp workspace
- Review `config/clickup-config.json` status mappings

## Support Documentation

For detailed help, see:

- [README.MD](README.MD) - Main guide
- [SETUP-GUIDE.md](SETUP-GUIDE.md) - Step-by-step setup
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues
- [GITHUB-SECRETS.md](GITHUB-SECRETS.md) - Secret management
- [QUICK-REFERENCE.md](QUICK-REFERENCE.md) - Command reference

---

**The integration is ready to use. Just add your API token and start working!**
