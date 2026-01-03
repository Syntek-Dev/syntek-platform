# ClickUp Integration Quick Reference

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

One-page reference for daily ClickUp integration usage.

## Table of Contents

- [ClickUp Integration Quick Reference](#clickup-integration-quick-reference)
  - [Table of Contents](#table-of-contents)
  - [Branch Naming Pattern](#branch-naming-pattern)
  - [Common Commands](#common-commands)
    - [Pull Latest Tasks](#pull-latest-tasks)
    - [Sync Stories to ClickUp](#sync-stories-to-clickup)
    - [Create Feature Branch](#create-feature-branch)
    - [Create Pull Request](#create-pull-request)
  - [Automatic Status Updates](#automatic-status-updates)
  - [Status Flow](#status-flow)
  - [ClickUp Workspace IDs](#clickup-workspace-ids)
  - [GitHub Secrets](#github-secrets)
  - [Story File Format](#story-file-format)
  - [Troubleshooting](#troubleshooting)
    - [Task Not Found](#task-not-found)
    - [Workflow Not Running](#workflow-not-running)
    - [Status Not Updating](#status-not-updating)
  - [Quick Links](#quick-links)
  - [Support](#support)

## Branch Naming Pattern

```
us{task_number}/{feature_name}
```

**Examples:**
- `us123/add-authentication`
- `us456/fix-bug`
- `us789/refactor-api`

## Common Commands

### Pull Latest Tasks
```bash
export CLICKUP_API_KEY=pk_your_key_here
python scripts/clickup/pull_tasks.py
git add config/clickup-story-mapping.json
git commit -m "Update ClickUp mapping"
git push
```

### Sync Stories to ClickUp
```bash
# Preview changes
python scripts/clickup/sync_stories.py --dry-run

# Sync all stories
python scripts/clickup/sync_stories.py
```

### Create Feature Branch
```bash
git checkout -b us123/feature-name
git push origin us123/feature-name
# ✓ Task moves to "in progress" automatically
```

### Create Pull Request
```bash
gh pr create --title "US-123: Feature name" --body "Description"
# ✓ Task moves to "in review" automatically
```

## Automatic Status Updates

| Action | Result in ClickUp |
|--------|-------------------|
| Create branch `us123/...` | Task US-123 → "in progress" |
| Open PR from `us123/...` | Task US-123 → "in review" |
| Merge PR to staging | Task US-123 → "accepted" |
| Merge PR to main | Task US-123 → "Closed" |

## Status Flow

```
Open → pending → in progress → in review → accepted → Closed
                      ↓
                   blocked
```

## ClickUp Workspace IDs

Talk to your lead dev for the IDs

## GitHub Secrets

**Required:**
- `CLICKUP_API_KEY` = Your API key

**Optional:**
- `CLICKUP_WEBHOOK_SECRET` = Webhook signature key

Add at: Settings > Secrets and variables > Actions

## Story File Format

`docs/STORIES/US-XXX.md`:

```markdown
# Story Title

**Story Points:** 5
**Priority:** Must Have
**Sprint:** Sprint 01
**Status:** Open

Story description here.

## Acceptance Criteria

- [ ] Criterion 1
- [ ] Criterion 2
```

## Troubleshooting

### Task Not Found
```bash
python scripts/clickup/pull_tasks.py
```

### Workflow Not Running
1. Check branch name matches `us{number}/...`
2. Verify `CLICKUP_API_KEY` secret exists
3. Check Actions tab for errors

### Status Not Updating
1. Check status name matches exactly (case-sensitive)
2. Verify mapping file is up to date
3. Review workflow logs

## Quick Links

- **Full Docs:** [README.MD](README.MD)
- **Setup:** [SETUP-GUIDE.MD](SETUP-GUIDE.MD)
- **Troubleshooting:** [TROUBLESHOOTING.MD](TROUBLESHOOTING.MD)
- **Secrets:** [GITHUB-SECRETS.MD](GITHUB-SECRETS.MD)
- **Scripts:** [../../scripts/clickup/README.md](../../scripts/clickup/README.md)

## Support

- ClickUp API: https://clickup.com/api
- GitHub Actions: https://docs.github.com/en/actions
- Check workflow logs: Actions tab in GitHub
