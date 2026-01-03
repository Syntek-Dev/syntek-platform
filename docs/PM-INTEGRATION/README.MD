# ClickUp Project Management Integration

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

Complete integration between this Django backend project and ClickUp for project management, task tracking, and workflow automation.

## Table of Contents

- [ClickUp Project Management Integration](#clickup-project-management-integration)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Quick Start](#quick-start)
    - [1. Set Up Environment Variables](#1-set-up-environment-variables)
    - [2. Configure GitHub Secrets](#2-configure-github-secrets)
    - [3. Install Dependencies Locally](#3-install-dependencies-locally)
    - [4. Pull Task IDs from ClickUp](#4-pull-task-ids-from-clickup)
  - [ClickUp Workspace Structure](#clickup-workspace-structure)
    - [Space: Syntek (ID: 90156744333)](#space-syntek-id-90156744333)
      - [Folders](#folders)
    - [Available Statuses](#available-statuses)
  - [Branch Naming Convention](#branch-naming-convention)
    - [Examples](#examples)
    - [What Happens Automatically](#what-happens-automatically)
  - [Workflow: From Story to Deployment](#workflow-from-story-to-deployment)
    - [Step 1: Create User Story in ClickUp](#step-1-create-user-story-in-clickup)
    - [Step 2: Pull Latest Task Mapping](#step-2-pull-latest-task-mapping)
    - [Step 3: Start Development](#step-3-start-development)
    - [Step 4: Create Pull Request](#step-4-create-pull-request)
    - [Step 5: Merge to Staging](#step-5-merge-to-staging)
    - [Step 6: Merge to Production](#step-6-merge-to-production)
  - [Status Mapping Reference](#status-mapping-reference)
    - [Branch/Event to ClickUp Status](#branchevent-to-clickup-status)
  - [Scripts Reference](#scripts-reference)
    - [Pull Tasks from ClickUp](#pull-tasks-from-clickup)
    - [Sync Stories to ClickUp](#sync-stories-to-clickup)
  - [GitHub Actions Workflows](#github-actions-workflows)
    - [clickup-sync.yml](#clickup-syncyml)
    - [clickup-branch-sync.yml](#clickup-branch-syncyml)
  - [Troubleshooting](#troubleshooting)
    - [Task Not Found in Mapping](#task-not-found-in-mapping)
    - [Status Update Fails](#status-update-fails)
    - [API Authentication Fails](#api-authentication-fails)
    - [GitHub Actions Not Triggering](#github-actions-not-triggering)
  - [API Rate Limits](#api-rate-limits)
  - [Security Best Practices](#security-best-practices)
  - [Configuration Files](#configuration-files)
    - [config/clickup-config.json](#configclickup-configjson)
    - [config/clickup-tasks.json](#configclickup-tasksjson)
    - [config/clickup-story-mapping.json](#configclickup-story-mappingjson)
  - [Additional Resources](#additional-resources)

## Overview

This integration provides:

- **Bidirectional Sync**: Sync user stories and tasks between local docs and ClickUp
- **Automated Status Updates**: Branch creation and PR events automatically update task statuses
- **Branch-Based Workflow**: Use branch naming conventions to link code to ClickUp tasks
- **GitHub Actions**: Automatic syncing triggered by Git events

## Quick Start

### 1. Set Up Environment Variables

Copy the ClickUp configuration to your `.env.dev` file:

```bash
# ClickUp Project Management Integration
CLICKUP_API_KEY=
CLICKUP_TEAM_ID=
CLICKUP_SPACE_ID=
CLICKUP_SPRINTS_FOLDER_ID=
CLICKUP_BACKLOG_FOLDER_ID=
CLICKUP_BACKLOG_LIST_ID=
```

### 2. Configure GitHub Secrets

Add these secrets to your GitHub repository for Actions:

- `CLICKUP_API_KEY`: Your ClickUp API key
- `CLICKUP_WEBHOOK_SECRET`: Optional webhook signature secret

**To add secrets:**
1. Go to GitHub repository Settings
2. Navigate to Secrets and variables > Actions
3. Click "New repository secret"
4. Add each secret

### 3. Install Dependencies Locally

```bash
# On your local machine (not in Docker)
pip install requests>=2.31.0
```

### 4. Pull Task IDs from ClickUp

```bash
# Export your API key
export CLICKUP_API_KEY=

# Pull all tasks and generate ID mapping
python scripts/clickup/pull_tasks.py

# Commit the mapping file
git add config/clickup-story-mapping.json config/clickup-tasks.json
git commit -m "Add ClickUp task mapping"
git push
```

## ClickUp Workspace Structure

### Space: Syntek (ID: 90156744333)

#### Folders

**1. Sprint - Backend Template**
- Contains sprint lists (Sprint 01, Sprint 02, etc.)
- Empty initially - lists created as sprints are planned
- Used for active development work

**2. Backlog - UI Template**
- Contains the main backlog list (ID: 901519340766)
- All unassigned stories start here
- Move stories to sprint lists when ready for development

### Available Statuses

The workspace uses these statuses (configured in `config/clickup-config.json`):

| Status | Type | Use Case |
|--------|------|----------|
| Open | open | New tasks, not yet started |
| pending | custom | Awaiting something before starting |
| in progress | custom | Currently being worked on |
| in review | custom | Code review, PR opened |
| accepted | custom | Approved, ready for staging |
| accepted customer | custom | Customer/stakeholder approved |
| rejected | custom | Changes requested |
| rejected customer | custom | Customer requested changes |
| blocked | custom | Cannot proceed due to blocker |
| completed | custom | Work finished, testing passed |
| client accepted | custom | Client final approval |
| client rejected | custom | Client requested changes |
| Closed | closed | Task complete and deployed |

## Branch Naming Convention

Use this pattern to enable automatic ClickUp sync:

```
us{task_number}/{feature_name}
```

### Examples

```bash
# Create feature branch for US-123
git checkout -b us123/add-user-authentication

# Create bugfix branch for US-456
git checkout -b us456/fix-database-migration

# Create enhancement branch for US-789
git checkout -b us789/improve-api-performance
```

### What Happens Automatically

When you create a branch with this pattern:

1. GitHub Actions detects the `us{number}` pattern
2. Looks up the ClickUp task ID from `config/clickup-story-mapping.json`
3. Updates the task status to "in progress"
4. Adds a comment to the ClickUp task with branch details

## Workflow: From Story to Deployment

### Step 1: Create User Story in ClickUp

Option A - Manually in ClickUp:
1. Go to Backlog list in ClickUp
2. Create new task with format: `US-XXX: Story Title`
3. Add description, acceptance criteria, priority
4. Assign to sprint list when ready

Option B - Sync from Local Files:
1. Create markdown file: `docs/STORIES/US-XXX.md`
2. Run sync script: `python scripts/clickup/sync_stories.py`
3. Story appears in ClickUp

### Step 2: Pull Latest Task Mapping

```bash
python scripts/clickup/pull_tasks.py
git add config/clickup-story-mapping.json
git commit -m "Update ClickUp task mapping"
git push
```

### Step 3: Start Development

```bash
# Create feature branch (automatically moves task to "in progress")
git checkout -b us123/implement-feature

# Make your changes
# ... code here ...

# Commit and push
git add .
git commit -m "Implement feature functionality"
git push origin us123/implement-feature
```

### Step 4: Create Pull Request

```bash
# Create PR on GitHub (automatically moves task to "in review")
gh pr create --title "US-123: Implement feature" --body "Implementation details"
```

When PR is created:
- Task status changes to "in review"
- Comment added to ClickUp task with PR link

### Step 5: Merge to Staging

When PR is merged to `staging` branch:
- Task status changes to "accepted"
- Comment added noting the merge

### Step 6: Merge to Production

When staging is merged to `main` branch:
- Task status changes to "Closed"
- Task marked as complete

## Status Mapping Reference

### Branch/Event to ClickUp Status

| Event | Branch | ClickUp Status |
|-------|--------|----------------|
| Branch created | us{number}/... | in progress |
| PR opened | any | in review |
| PR merged | dev | in progress |
| PR merged | testing | in review |
| PR merged | staging | accepted |
| PR merged | main | Closed |
| Push | dev | in progress |
| Push | testing | in review |
| Push | staging | accepted |
| Push | main | Closed |

## Scripts Reference

### Pull Tasks from ClickUp

Fetch all tasks and create ID mapping:

```bash
# Pull all open tasks
python scripts/clickup/pull_tasks.py

# Include closed tasks
python scripts/clickup/pull_tasks.py --include-closed

# Save to custom location
python scripts/clickup/pull_tasks.py --output /tmp/tasks.json
```

Output files:
- `config/clickup-tasks.json` - Full task data
- `config/clickup-story-mapping.json` - Story ID to task ID mapping

### Sync Stories to ClickUp

Upload local story files to ClickUp:

```bash
# Sync all stories
python scripts/clickup/sync_stories.py

# Preview changes without syncing
python scripts/clickup/sync_stories.py --dry-run

# Sync specific folder
python scripts/clickup/sync_stories.py --folder-path docs/STORIES/SPRINT-01
```

Story file format (`docs/STORIES/US-XXX.md`):

```markdown
# Story Title

**Story Points:** 5
**Priority:** Must Have
**Sprint:** Sprint 01
**Status:** Open

Description of the user story goes here.

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
```

## GitHub Actions Workflows

### clickup-sync.yml

**Triggers:**
- Push to main, staging, dev, testing
- Pull request opened, synchronized, closed, reopened
- Manual workflow dispatch

**Actions:**
- Extracts task ID from branch name
- Updates task status based on event
- Adds PR comments to ClickUp tasks

### clickup-branch-sync.yml

**Triggers:**
- Branch creation matching `us*/**` pattern

**Actions:**
- Moves task to "in progress"
- Adds branch creation comment

## Troubleshooting

### Task Not Found in Mapping

**Problem:** GitHub Actions can't find task ID for your branch.

**Solutions:**

1. Check task exists in ClickUp with format `US-XXX: Title`
2. Regenerate mapping:
   ```bash
   python scripts/clickup/pull_tasks.py
   git add config/clickup-story-mapping.json
   git commit -m "Update ClickUp mapping"
   git push
   ```
3. Verify branch naming: must be `us{number}/feature-name`

### Status Update Fails

**Problem:** Task status not updating in ClickUp.

**Solutions:**

1. Verify status name matches exactly (case-sensitive)
2. Check available statuses:
   ```python
   from clickup_client import get_client
   client = get_client()
   statuses = client.get_space_statuses()
   for s in statuses:
       print(f"{s['status']} ({s['type']})")
   ```
3. Update `config/clickup-config.json` status mappings

### API Authentication Fails

**Problem:** Scripts return 401 Unauthorized.

**Solutions:**

1. Verify API key is set:
   ```bash
   echo $CLICKUP_API_KEY
   ```
2. Test API access:
   ```bash
   curl -H "Authorization: $CLICKUP_API_KEY" \
     https://api.clickup.com/api/v2/team
   ```
3. Regenerate API key in ClickUp Settings > Apps

### GitHub Actions Not Triggering

**Problem:** Workflows not running on branch creation or PR.

**Solutions:**

1. Check GitHub Actions are enabled in repository settings
2. Verify secrets are set: Settings > Secrets and variables > Actions
3. Check workflow file syntax: `.github/workflows/clickup-*.yml`
4. Review Actions tab for error messages

## API Rate Limits

ClickUp API has these limits:
- 100 requests per minute per API key
- 10 requests per second per API key

**Best Practices:**
- Don't run bulk sync operations too frequently
- Use `--dry-run` to preview changes before syncing
- Cache task mappings locally (already done in `config/`)

## Security Best Practices

1. Never commit API keys to version control
2. Use GitHub Secrets for Actions
3. Rotate API keys periodically
4. Use read-only keys where possible
5. Keep `.env.dev` in `.gitignore`

## Configuration Files

### config/clickup-config.json

Main configuration defining:
- Workspace and folder IDs
- Status mappings
- Branch naming patterns
- Priority mappings
- Field mappings

### config/clickup-tasks.json

Generated by `pull_tasks.py`:
- Full task details from ClickUp
- Includes assignees, tags, dates
- Updated when you run pull script

### config/clickup-story-mapping.json

Generated by `pull_tasks.py`:
- Maps story IDs (US-XXX) to ClickUp task IDs
- Used by GitHub Actions to find tasks
- Commit this file to version control

## Additional Resources

- [ClickUp API Documentation](https://clickup.com/api)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Scripts README](../../scripts/clickup/README.md)
- [Setup Guide](SETUP-GUIDE.MD)
- [Troubleshooting Guide](TROUBLESHOOTING.MD)
