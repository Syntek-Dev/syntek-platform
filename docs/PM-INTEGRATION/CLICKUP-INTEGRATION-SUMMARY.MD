# ClickUp Integration Summary

Complete ClickUp project management integration for backend_template Django project.

**Date:** 2026-01-03
**Status:** Configured and ready to use

---

## Table of Contents

- [ClickUp Integration Summary](#clickup-integration-summary)
  - [Table of Contents](#table-of-contents)
  - [What Was Implemented](#what-was-implemented)
    - [1. Environment Configuration](#1-environment-configuration)
    - [2. Configuration Files](#2-configuration-files)
    - [3. Python Scripts](#3-python-scripts)
      - [clickup\_client.py](#clickup_clientpy)
      - [sync\_stories.py](#sync_storiespy)
      - [pull\_tasks.py](#pull_taskspy)
      - [README.md](#readmemd)
    - [4. GitHub Actions Workflows](#4-github-actions-workflows)
      - [clickup-sync.yml](#clickup-syncyml)
      - [clickup-branch-sync.yml](#clickup-branch-syncyml)
    - [5. Documentation](#5-documentation)
      - [README.MD](#readmemd-1)
      - [SETUP-GUIDE.MD](#setup-guidemd)
      - [TROUBLESHOOTING.MD](#troubleshootingmd)
      - [GITHUB-SECRETS.MD](#github-secretsmd)
  - [ClickUp Workspace Structure](#clickup-workspace-structure)
    - [Space: Syntek](#space-syntek)
    - [Folders](#folders)
    - [Available Statuses](#available-statuses)
  - [Branch Naming Convention](#branch-naming-convention)
  - [Required GitHub Secrets](#required-github-secrets)
    - [CLICKUP\_API\_KEY (Required)](#clickup_api_key-required)
    - [CLICKUP\_WEBHOOK\_SECRET (Optional)](#clickup_webhook_secret-optional)
  - [Quick Start Guide](#quick-start-guide)
    - [1. Set Up Environment](#1-set-up-environment)
    - [2. Install Dependencies](#2-install-dependencies)
    - [3. Add GitHub Secret](#3-add-github-secret)
    - [4. Pull Task Mapping](#4-pull-task-mapping)
    - [5. Test Integration](#5-test-integration)
  - [Daily Workflow](#daily-workflow)
    - [Starting a New Feature](#starting-a-new-feature)
  - [File Structure](#file-structure)
  - [Status Mapping Reference](#status-mapping-reference)
    - [Git Event → ClickUp Status](#git-event--clickup-status)
  - [Dependencies](#dependencies)
    - [Python (pyproject.toml)](#python-pyprojecttoml)
    - [GitHub Actions](#github-actions)
  - [Testing the Integration](#testing-the-integration)
    - [Test 1: API Connection](#test-1-api-connection)
    - [Test 2: Pull Tasks](#test-2-pull-tasks)
    - [Test 3: Branch Sync](#test-3-branch-sync)
    - [Test 4: PR Sync](#test-4-pr-sync)
  - [Maintenance Tasks](#maintenance-tasks)
    - [Weekly](#weekly)
    - [Monthly](#monthly)
    - [As Needed](#as-needed)
  - [Troubleshooting](#troubleshooting)
    - [Task Not Found](#task-not-found)
    - [GitHub Actions Fails](#github-actions-fails)
    - [Status Not Updating](#status-not-updating)
  - [Next Steps](#next-steps)
  - [Support Resources](#support-resources)
  - [Summary](#summary)

## What Was Implemented

### 1. Environment Configuration

**File:** `.env.dev.example`

Added ClickUp environment variables:
```bash
CLICKUP_API_KEY=
CLICKUP_TEAM_ID=
CLICKUP_SPACE_ID=
CLICKUP_SPRINTS_FOLDER_ID=
CLICKUP_BACKLOG_FOLDER_ID=
CLICKUP_BACKLOG_LIST_ID=
```

**Action Required:** Copy to `.env.dev` and add your API key.

---

### 2. Configuration Files

**File:** `config/clickup-config.json`

Main configuration defining:
- Workspace and folder IDs
- Status mappings (Open, pending, in progress, in review, accepted, blocked, completed, Closed)
- Branch naming pattern: `us{task_id}/{feature_name}`
- Priority mappings (must_have, should_have, could_have, wont_have)
- Field and label mappings

---

### 3. Python Scripts

**Location:** `scripts/clickup/`

#### clickup_client.py
- ClickUp API v2 client library
- Handles authentication, requests, task operations
- Provides methods for creating, updating, searching tasks
- Google-style docstrings throughout

#### sync_stories.py
- Syncs user stories from `docs/STORIES/` to ClickUp
- Parses markdown story files (US-XXX.md format)
- Creates or updates tasks in ClickUp
- Supports dry-run mode for testing

#### pull_tasks.py
- Fetches all tasks from ClickUp workspace
- Generates story ID to task ID mapping
- Saves to `config/clickup-tasks.json` and `config/clickup-story-mapping.json`
- Used by GitHub Actions to find task IDs

#### README.md
- Comprehensive documentation for scripts
- Installation instructions
- Usage examples
- Troubleshooting guide

---

### 4. GitHub Actions Workflows

**Location:** `.github/workflows/`

#### clickup-sync.yml
**Triggers:**
- Push to main, staging, dev, testing branches
- Pull request opened, synchronized, closed, reopened
- Manual workflow dispatch

**Actions:**
- Extracts task ID from branch name (us{number}/feature-name)
- Loads task mapping from config/clickup-story-mapping.json
- Updates ClickUp task status based on event:
  - PR opened → "in review"
  - PR merged to staging → "accepted"
  - PR merged to main → "Closed"
  - Push to dev → "in progress"
- Adds PR comments to ClickUp tasks

#### clickup-branch-sync.yml
**Triggers:**
- Branch creation matching `us*/**` pattern

**Actions:**
- Extracts task number from branch name
- Finds ClickUp task ID from mapping
- Updates task status to "in progress"
- Adds branch creation comment to task

---

### 5. Documentation

**Location:** `docs/PM-INTEGRATION/`

#### README.MD
- Complete integration overview
- Quick start guide
- ClickUp workspace structure
- Branch naming convention
- Full workflow from story to deployment
- Status mapping reference
- Scripts usage guide

#### SETUP-GUIDE.MD
- Step-by-step setup instructions
- ClickUp configuration
- Local environment setup
- GitHub repository setup
- Verification and testing procedures
- Team onboarding guide

#### TROUBLESHOOTING.MD
- Common issues and solutions
- Authentication problems
- Task mapping issues
- Status update failures
- GitHub Actions problems
- Script execution errors
- Performance issues

#### GITHUB-SECRETS.MD
- Required repository secrets
- How to add secrets to GitHub
- Security best practices
- Verification procedures
- Updating secrets guide

---

## ClickUp Workspace Structure

### Space: Syntek
- **ID:** 90156744333
- **Team ID:** 90151635198

### Folders

1. **Sprint - Backend Template**
   - **ID:** 901512938483
   - **Purpose:** Active sprint lists
   - **Status:** Empty initially, lists created per sprint

2. **Backlog - Backend Template**
   - **ID:** 901512938469
   - **List ID:** 901519340766
   - **Purpose:** Unassigned stories and backlog items

### Available Statuses

| Status | Type | Use Case |
|--------|------|----------|
| Open | open | New tasks |
| pending | custom | Waiting to start |
| in progress | custom | Active development |
| in review | custom | Code review/PR |
| accepted | custom | Approved for staging |
| accepted customer | custom | Stakeholder approved |
| rejected | custom | Changes requested |
| rejected customer | custom | Client changes requested |
| blocked | custom | Cannot proceed |
| completed | custom | Work finished |
| client accepted | custom | Client final approval |
| client rejected | custom | Client requested changes |
| Closed | closed | Complete and deployed |

---

## Branch Naming Convention

**Pattern:** `us{task_number}/{feature_name}`

**Examples:**
```bash
us123/add-user-authentication
us456/fix-database-migration
us789/improve-api-performance
```

**What Happens Automatically:**
1. Branch created → Task moves to "in progress"
2. PR opened → Task moves to "in review"
3. PR merged to staging → Task moves to "accepted"
4. PR merged to main → Task moves to "Closed"

---

## Required GitHub Secrets

Add to: **Settings > Secrets and variables > Actions**

### CLICKUP_API_KEY (Required)
- **Value:** `pk_236614810_KJX43XCVU2BZC4O1Q9FIZA8XNFFSZP8P`
- **Purpose:** Authentication with ClickUp API
- **Used in:** Both workflow files

### CLICKUP_WEBHOOK_SECRET (Optional)
- **Value:** Not set (for future webhook implementation)
- **Purpose:** Webhook signature verification
- **Used in:** Future bidirectional sync

---

## Quick Start Guide

### 1. Set Up Environment

```bash
# Copy example to actual env file
cp .env.dev.example .env.dev

# Add your API key
# Edit .env.dev and set CLICKUP_API_KEY=pk_236614810_KJX43XCVU2BZC4O1Q9FIZA8XNFFSZP8P
```

### 2. Install Dependencies

```bash
# On your local machine (not in Docker)
pip install requests>=2.31.0
```

### 3. Add GitHub Secret

1. Go to GitHub repository Settings
2. Navigate to Secrets and variables > Actions
3. Click "New repository secret"
4. Name: `CLICKUP_API_KEY`
5. Value: `pk_236614810_KJX43XCVU2BZC4O1Q9FIZA8XNFFSZP8P`
6. Click "Add secret"

### 4. Pull Task Mapping

```bash
# Export API key
export CLICKUP_API_KEY=pk_236614810_KJX43XCVU2BZC4O1Q9FIZA8XNFFSZP8P

# Pull tasks
python scripts/clickup/pull_tasks.py

# Commit mapping files
git add config/clickup-story-mapping.json config/clickup-tasks.json
git commit -m "Add ClickUp task mapping"
git push
```

### 5. Test Integration

```bash
# Create test task in ClickUp named: US-999: Test Integration
# Then pull mapping again
python scripts/clickup/pull_tasks.py

# Create branch (automatically moves to "in progress")
git checkout -b us999/test-integration
git push origin us999/test-integration

# Check ClickUp - task should be "in progress" with comment
```

---

## Daily Workflow

### Starting a New Feature

1. **Find your task in ClickUp** (e.g., US-123)

2. **Pull latest mapping** (if needed):
   ```bash
   python scripts/clickup/pull_tasks.py
   ```

3. **Create feature branch**:
   ```bash
   git checkout -b us123/implement-feature
   git push origin us123/implement-feature
   ```
   ✓ Task automatically moves to "in progress"

4. **Develop and commit**:
   ```bash
   # Make changes
   git add .
   git commit -m "Implement feature"
   git push
   ```

5. **Create pull request**:
   ```bash
   gh pr create --title "US-123: Implement feature"
   ```
   ✓ Task automatically moves to "in review"

6. **Merge to staging**:
   ```bash
   # After approval, merge PR
   gh pr merge --squash
   ```
   ✓ Task automatically moves to "accepted"

7. **Deploy to production**:
   ```bash
   # Merge staging to main
   git checkout main
   git pull
   git merge staging
   git push
   ```
   ✓ Task automatically moves to "Closed"

---

## File Structure

```
backend_template/
├── .env.dev.example          # Environment template with ClickUp vars
├── .github/workflows/
│   ├── clickup-sync.yml      # Main sync workflow
│   └── clickup-branch-sync.yml  # Branch creation workflow
├── config/
│   ├── clickup-config.json   # Main configuration
│   ├── clickup-tasks.json    # Task data (generated)
│   └── clickup-story-mapping.json  # ID mapping (generated)
├── scripts/clickup/
│   ├── clickup_client.py     # API client library
│   ├── sync_stories.py       # Story sync script
│   ├── pull_tasks.py         # Task fetch script
│   └── README.md             # Scripts documentation
└── docs/PM-INTEGRATION/
    ├── README.MD             # Main integration docs
    ├── SETUP-GUIDE.MD        # Setup instructions
    ├── TROUBLESHOOTING.MD    # Common issues
    └── GITHUB-SECRETS.MD     # Secrets guide
```

---

## Status Mapping Reference

### Git Event → ClickUp Status

| Event | Branch | ClickUp Status |
|-------|--------|----------------|
| Branch created | us{n}/... | in progress |
| PR opened | any | in review |
| PR merged | dev | in progress |
| PR merged | testing | in review |
| PR merged | staging | accepted |
| PR merged | main | Closed |
| Push | dev | in progress |
| Push | testing | in review |
| Push | staging | accepted |
| Push | main | Closed |

---

## Dependencies

### Python (pyproject.toml)
```toml
dependencies = [
    "requests>=2.31.0",  # For ClickUp API integration
]
```

### GitHub Actions
- ubuntu-latest runner (includes Python 3.11, jq, curl)
- checkout@v4
- setup-python@v5

---

## Testing the Integration

### Test 1: API Connection
```bash
export CLICKUP_API_KEY=pk_236614810_KJX43XCVU2BZC4O1Q9FIZA8XNFFSZP8P
python3 -c "from scripts.clickup.clickup_client import get_client; client = get_client(); print(client.get_space_statuses())"
```

### Test 2: Pull Tasks
```bash
python scripts/clickup/pull_tasks.py
ls -la config/clickup-*.json
```

### Test 3: Branch Sync
```bash
git checkout -b us999/test-branch
git push origin us999/test-branch
# Check ClickUp for status update
```

### Test 4: PR Sync
```bash
gh pr create --title "US-999: Test" --body "Test integration"
# Check ClickUp for PR comment
```

---

## Maintenance Tasks

### Weekly
- Pull updated task mapping if new stories added
- Review closed tasks in ClickUp

### Monthly
- Audit API key usage
- Review and update status mappings if needed

### As Needed
- Rotate API keys if compromised
- Update folder IDs if ClickUp structure changes
- Add new statuses to mappings

---

## Troubleshooting

### Task Not Found
```bash
# Regenerate mapping
python scripts/clickup/pull_tasks.py
git add config/clickup-story-mapping.json
git commit -m "Update mapping"
git push
```

### GitHub Actions Fails
1. Check Actions tab for error logs
2. Verify `CLICKUP_API_KEY` secret exists
3. Check branch naming matches `us{number}/...`
4. Ensure mapping file committed

### Status Not Updating
1. Verify status name matches exactly (case-sensitive)
2. Check `config/clickup-config.json` status mappings
3. Review ClickUp workspace statuses

---

## Next Steps

1. ✅ Configuration files created
2. ✅ Scripts implemented with full documentation
3. ✅ GitHub Actions workflows configured
4. ✅ Documentation complete

**To activate:**
1. Add API key to `.env.dev`
2. Add `CLICKUP_API_KEY` secret to GitHub
3. Run `python scripts/clickup/pull_tasks.py`
4. Commit mapping files
5. Start using `us{number}/feature-name` branch naming

---

## Support Resources

- **ClickUp API Docs:** https://clickup.com/api
- **GitHub Actions Docs:** https://docs.github.com/en/actions
- **Project Docs:** `docs/PM-INTEGRATION/README.MD`
- **Setup Guide:** `docs/PM-INTEGRATION/SETUP-GUIDE.MD`
- **Troubleshooting:** `docs/PM-INTEGRATION/TROUBLESHOOTING.MD`

---

## Summary

The ClickUp integration is fully configured and ready to use. All scripts, workflows, and documentation are in place. Simply add your API key to GitHub Secrets and `.env.dev`, pull the task mapping, and start using the branch naming convention. The integration will automatically sync task statuses as you develop, create PRs, and deploy code.
