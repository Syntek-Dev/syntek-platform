# ClickUp Integration Setup Guide

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

Step-by-step instructions for setting up ClickUp integration with this Django backend project.

## Table of Contents

- [ClickUp Integration Setup Guide](#clickup-integration-setup-guide)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Part 1: ClickUp Configuration](#part-1-clickup-configuration)
    - [Step 1: Get Your ClickUp API Key](#step-1-get-your-clickup-api-key)
    - [Step 2: Find Your Workspace IDs](#step-2-find-your-workspace-ids)
    - [Step 3: Verify Workspace Statuses](#step-3-verify-workspace-statuses)
  - [Part 2: Local Environment Setup](#part-2-local-environment-setup)
    - [Step 1: Create .env.dev File](#step-1-create-envdev-file)
    - [Step 2: Add ClickUp Credentials](#step-2-add-clickup-credentials)
    - [Step 3: Install Python Dependencies](#step-3-install-python-dependencies)
    - [Step 4: Test API Connection](#step-4-test-api-connection)
    - [Step 5: Pull Initial Task Data](#step-5-pull-initial-task-data)
  - [Part 3: GitHub Repository Setup](#part-3-github-repository-setup)
    - [Step 1: Add GitHub Secrets](#step-1-add-github-secrets)
    - [Step 2: Commit Configuration Files](#step-2-commit-configuration-files)
    - [Step 3: Enable GitHub Actions](#step-3-enable-github-actions)
  - [Part 4: Verification and Testing](#part-4-verification-and-testing)
    - [Step 1: Test Branch Creation Sync](#step-1-test-branch-creation-sync)
    - [Step 2: Test Pull Request Sync](#step-2-test-pull-request-sync)
    - [Step 3: Test PR Merge](#step-3-test-pr-merge)
    - [Step 4: Clean Up Test](#step-4-clean-up-test)
  - [Part 5: Optional Webhook Setup](#part-5-optional-webhook-setup)
    - [Step 1: Generate Webhook Secret](#step-1-generate-webhook-secret)
    - [Step 2: Create Webhook Endpoint](#step-2-create-webhook-endpoint)
  - [Part 6: Team Onboarding](#part-6-team-onboarding)
    - [Step 1: Document for Team](#step-1-document-for-team)
    - [Step 2: Add to Team README](#step-2-add-to-team-readme)
  - [Troubleshooting Setup](#troubleshooting-setup)
    - [API Key Invalid](#api-key-invalid)
    - [GitHub Actions Not Running](#github-actions-not-running)
    - [Task Mapping Not Found](#task-mapping-not-found)
    - [Python Module Not Found](#python-module-not-found)
  - [Next Steps](#next-steps)
  - [Maintenance](#maintenance)
    - [Weekly Tasks](#weekly-tasks)
    - [Monthly Tasks](#monthly-tasks)
    - [As Needed](#as-needed)

## Prerequisites

Before starting, ensure you have:

- [ ] ClickUp account with access to the workspace
- [ ] Admin access to create API keys in ClickUp
- [ ] Admin access to the GitHub repository
- [ ] Python 3.11+ installed locally
- [ ] Git installed and configured

## Part 1: ClickUp Configuration

### Step 1: Get Your ClickUp API Key

1. Log in to ClickUp
2. Click your avatar (bottom left)
3. Go to **Settings**
4. Navigate to **Apps** section
5. Scroll to **API Token**
6. Click **Generate** (or use existing token)
7. Copy the token (starts with `pk_`)

**Important:** Store this token securely. You'll need it for environment variables.

### Step 2: Find Your Workspace IDs

The workspace IDs are required please contact the lead dev.

You can verify these by visiting your ClickUp workspace and checking the URLs.

### Step 3: Verify Workspace Statuses

Ensure your ClickUp workspace has these statuses configured:

1. Go to Space settings in ClickUp
2. Click **Statuses**
3. Verify these exist:
   - Open (open type)
   - pending (custom type)
   - in progress (custom type)
   - in review (custom type)
   - accepted (custom type)
   - blocked (custom type)
   - completed (custom type)
   - Closed (closed type)

If any are missing, add them in Space settings.

## Part 2: Local Environment Setup

### Step 1: Create .env.dev File

Copy the example environment file:

```bash
cp .env.dev.example .env.dev
```

### Step 2: Add ClickUp Credentials

Edit `.env.dev` and add your API key:

```bash
# ClickUp Project Management Integration
CLICKUP_API_KEY=
CLICKUP_TEAM_ID=
CLICKUP_SPACE_ID=
CLICKUP_SPRINTS_FOLDER_ID=
CLICKUP_BACKLOG_FOLDER_ID=
CLICKUP_BACKLOG_LIST_ID=
```

Replace `pk_YOUR_API_KEY_HERE` with your actual API key from Step 1.1.

### Step 3: Install Python Dependencies

```bash
# Install requests library for API calls
pip install requests>=2.31.0
```

### Step 4: Test API Connection

```bash
# Export API key
export CLICKUP_API_KEY=pk_YOUR_API_KEY_HERE

# Test connection
python3 -c "
from scripts.clickup.clickup_client import get_client
client = get_client()
space = client._request('GET', f'space/{client.space_id}')
print(f'Connected to: {space[\"name\"]}')
"
```

Expected output: `Connected to: Syntek`

### Step 5: Pull Initial Task Data

```bash
# Pull all tasks from ClickUp
python scripts/clickup/pull_tasks.py

# Verify files were created
ls -la config/clickup-*.json
```

You should see:

- `config/clickup-tasks.json`
- `config/clickup-story-mapping.json`

## Part 3: GitHub Repository Setup

### Step 1: Add GitHub Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Add these secrets:

| Secret Name       | Value                          |
| ----------------- | ------------------------------ |
| `CLICKUP_API_KEY` | Your ClickUp API key (pk\_...) |

Optional:

- `CLICKUP_WEBHOOK_SECRET` - For webhook signature verification

### Step 2: Commit Configuration Files

```bash
# Add ClickUp configuration
git add config/clickup-config.json
git add config/clickup-story-mapping.json
git add config/clickup-tasks.json

# Add GitHub workflows
git add .github/workflows/clickup-sync.yml
git add .github/workflows/clickup-branch-sync.yml

# Add environment template
git add .env.dev.example

# Commit
git commit -m "Add ClickUp integration configuration"
git push origin main
```

### Step 3: Enable GitHub Actions

1. Go to repository **Settings** > **Actions** > **General**
2. Under **Actions permissions**, select:
   - "Allow all actions and reusable workflows"
3. Under **Workflow permissions**, select:
   - "Read and write permissions"
4. Click **Save**

## Part 4: Verification and Testing

### Step 1: Test Branch Creation Sync

```bash
# Create a test task in ClickUp first
# Name it: US-999: Test Integration

# Pull the new task
python scripts/clickup/pull_tasks.py
git add config/clickup-story-mapping.json
git commit -m "Update task mapping"
git push

# Create test branch
git checkout -b us999/test-integration
git push origin us999/test-integration
```

Check ClickUp:

- Task US-999 should move to "in progress"
- A comment should be added with branch details

### Step 2: Test Pull Request Sync

```bash
# Make a small change
echo "# Test" > test.md
git add test.md
git commit -m "Test ClickUp integration"
git push origin us999/test-integration

# Create PR via GitHub CLI or web interface
gh pr create --title "US-999: Test integration" \
  --body "Testing ClickUp integration" \
  --base main
```

Check ClickUp:

- Task US-999 should move to "in review"
- A comment should be added with PR details

### Step 3: Test PR Merge

```bash
# Merge the PR (via GitHub web or CLI)
gh pr merge --squash
```

Check ClickUp:

- Task US-999 should move to "Closed"
- A comment should be added about the merge

### Step 4: Clean Up Test

```bash
# Delete test branch
git checkout main
git pull
git branch -d us999/test-integration
git push origin --delete us999/test-integration

# Remove test file
git rm test.md
git commit -m "Remove test file"
git push

# Archive or delete test task in ClickUp
```

## Part 5: Optional Webhook Setup

For bidirectional sync (ClickUp to GitHub), set up webhooks.

### Step 1: Generate Webhook Secret

```bash
# Generate random secret
openssl rand -hex 32
```

Add to `.env.dev`:

```bash
CLICKUP_WEBHOOK_SECRET=your_generated_secret
```

### Step 2: Create Webhook Endpoint

This requires a publicly accessible server. Options:

1. Deploy webhook endpoint to your staging/production server
2. Use ngrok for local testing
3. Use GitHub Actions only (unidirectional)

For now, webhooks are optional. GitHub Actions provide sufficient automation for most workflows.

## Part 6: Team Onboarding

### Step 1: Document for Team

Share this information with your team:

1. Branch naming convention: `us{number}/feature-name`
2. How to find task numbers in ClickUp
3. Expected workflow: Create branch → PR → Merge
4. How to run pull_tasks.py before starting work

### Step 2: Add to Team README

Add this to your project README.md:

```markdown
## ClickUp Integration

This project integrates with ClickUp for task tracking.

**Branch naming:** Use `us{task_number}/feature-name` format.

Example: `us123/add-user-authentication`

This automatically:

- Moves tasks to "in progress" when you create the branch
- Updates to "in review" when you open a PR
- Marks as "Closed" when merged to main

See [docs/PM-INTEGRATION/README.MD](docs/PM-INTEGRATION/README.MD) for details.
```

## Troubleshooting Setup

### API Key Invalid

**Symptom:** 401 Unauthorized errors

**Solution:**

1. Verify API key is correct in `.env.dev`
2. Check API key hasn't expired in ClickUp
3. Ensure API key has sufficient permissions

### GitHub Actions Not Running

**Symptom:** No status updates in ClickUp

**Solution:**

1. Check Actions are enabled in repository settings
2. Verify `CLICKUP_API_KEY` secret exists in GitHub
3. Check Actions tab for error logs
4. Ensure workflow files have correct syntax

### Task Mapping Not Found

**Symptom:** "No mapping found for US-XXX"

**Solution:**

1. Run `python scripts/clickup/pull_tasks.py`
2. Commit and push `config/clickup-story-mapping.json`
3. Ensure task name in ClickUp starts with `US-XXX:`

### Python Module Not Found

**Symptom:** `ModuleNotFoundError: No module named 'requests'`

**Solution:**

```bash
pip install requests>=2.31.0
```

## Next Steps

After setup is complete:

1. Read [README.MD](README.MD) for daily usage
2. Review [TROUBLESHOOTING.MD](TROUBLESHOOTING.MD) for common issues
3. Set up your first sprint in ClickUp
4. Create user stories using the format
5. Start using branch naming convention

## Maintenance

### Weekly Tasks

- [ ] Pull latest task mappings if new stories added
- [ ] Review closed tasks in ClickUp
- [ ] Archive completed sprints

### Monthly Tasks

- [ ] Audit API key usage
- [ ] Review status mappings for accuracy
- [ ] Update documentation if workflow changes

### As Needed

- [ ] Rotate API keys if compromised
- [ ] Update status mappings when ClickUp workspace changes
- [ ] Add new team members to ClickUp workspace

## Overview
