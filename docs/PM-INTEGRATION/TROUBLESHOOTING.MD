# ClickUp Integration Troubleshooting

Common issues and solutions for the ClickUp project management integration.

## Table of Contents

- [ClickUp Integration Troubleshooting](#clickup-integration-troubleshooting)
  - [Table of Contents](#table-of-contents)
  - [Authentication Issues](#authentication-issues)
    - [401 Unauthorized Error](#401-unauthorized-error)
    - [403 Forbidden Error](#403-forbidden-error)
  - [Task Mapping Issues](#task-mapping-issues)
    - [Task Not Found in Mapping](#task-not-found-in-mapping)
    - [Mapping File Missing](#mapping-file-missing)
  - [Status Update Issues](#status-update-issues)
    - [Status Not Found](#status-not-found)
    - [Status Update Silently Fails](#status-update-silently-fails)
  - [GitHub Actions Issues](#github-actions-issues)
    - [Workflow Not Triggering](#workflow-not-triggering)
    - [Workflow Fails with Error](#workflow-fails-with-error)
    - [Workflow Succeeds but Task Not Updated](#workflow-succeeds-but-task-not-updated)
  - [Script Execution Issues](#script-execution-issues)
    - [ModuleNotFoundError: requests](#modulenotfounderror-requests)
    - [Permission Denied](#permission-denied)
    - [Import Error: clickup\_client](#import-error-clickup_client)
  - [Story Sync Issues](#story-sync-issues)
    - [Story Not Created in ClickUp](#story-not-created-in-clickup)
    - [Duplicate Tasks Created](#duplicate-tasks-created)
  - [Performance Issues](#performance-issues)
    - [Script Takes Too Long](#script-takes-too-long)
    - [GitHub Actions Timeout](#github-actions-timeout)
  - [Configuration Issues](#configuration-issues)
    - [Config File Not Found](#config-file-not-found)
    - [Invalid JSON in Config](#invalid-json-in-config)
  - [API Rate Limiting](#api-rate-limiting)
    - [429 Too Many Requests](#429-too-many-requests)
  - [Network Issues](#network-issues)
    - [Connection Timeout](#connection-timeout)
  - [Data Sync Issues](#data-sync-issues)
    - [Changes Not Appearing](#changes-not-appearing)
    - [Unexpected Task Updates](#unexpected-task-updates)
  - [Getting Help](#getting-help)

## Authentication Issues

### 401 Unauthorized Error

**Symptom:**
```
Error: Failed to update task: 401
Unauthorized
```

**Causes & Solutions:**

1. **Invalid API Key**
   ```bash
   # Verify API key is set correctly
   echo $CLICKUP_API_KEY

   # Should start with: pk_
   ```

   **Fix:** Check `.env.dev` has correct API key, regenerate if needed.

2. **API Key Expired**

   **Fix:** Generate new API key in ClickUp Settings > Apps.

3. **API Key Not Exported**
   ```bash
   # Export the key
   export CLICKUP_API_KEY=pk_your_key_here
   ```

4. **GitHub Secret Missing**

   **Fix:** Add `CLICKUP_API_KEY` to repository secrets.

### 403 Forbidden Error

**Symptom:**
```
Error: 403 Forbidden
```

**Causes & Solutions:**

1. **Insufficient Permissions**

   **Fix:** Ensure API key has write access to tasks and folders.

2. **Workspace Access Denied**

   **Fix:** Verify you're a member of the ClickUp workspace.

## Task Mapping Issues

### Task Not Found in Mapping

**Symptom:**
```
No mapping found for US-123
```

**Causes & Solutions:**

1. **Mapping File Outdated**
   ```bash
   # Regenerate mapping
   python scripts/clickup/pull_tasks.py

   # Commit updated mapping
   git add config/clickup-story-mapping.json
   git commit -m "Update ClickUp task mapping"
   git push
   ```

2. **Task Name Format Incorrect**

   **Expected:** `US-123: Task Title`
   **Wrong:** `Task Title US-123`, `us-123: Title`, `Story 123`

   **Fix:** Rename task in ClickUp to start with `US-XXX:`

3. **Task Not Synced Yet**

   **Fix:** Wait 1-2 minutes after creating task in ClickUp, then pull again.

### Mapping File Missing

**Symptom:**
```
FileNotFoundError: config/clickup-story-mapping.json
```

**Solution:**
```bash
# Generate mapping file
python scripts/clickup/pull_tasks.py

# Verify creation
ls -la config/clickup-*.json

# Commit to git
git add config/clickup-story-mapping.json
git commit -m "Add ClickUp task mapping"
```

## Status Update Issues

### Status Not Found

**Symptom:**
```
Error: Status "in progress" not found
```

**Causes & Solutions:**

1. **Case Sensitivity**

   Status names are case-sensitive:
   - ✅ `in progress`
   - ❌ `In Progress`, `IN PROGRESS`

   **Fix:** Use exact status name from ClickUp.

2. **Status Doesn't Exist in Workspace**
   ```python
   # Check available statuses
   from scripts.clickup.clickup_client import get_client
   client = get_client()
   statuses = client.get_space_statuses()
   for s in statuses:
       print(f"'{s['status']}' (type: {s['type']})")
   ```

   **Fix:** Add missing status in ClickUp Space settings.

3. **Wrong Status Mapping**

   **Fix:** Update `config/clickup-config.json`:
   ```json
   "status_mapping": {
     "in_progress": ["in progress", "doing"]
   }
   ```

### Status Update Silently Fails

**Symptom:** No error but status doesn't change in ClickUp.

**Causes & Solutions:**

1. **Task Already Has That Status**

   **Fix:** This is normal behavior, no action needed.

2. **Rate Limiting**

   **Fix:** Wait 60 seconds between bulk operations.

3. **Network Issues**
   ```bash
   # Test API connectivity
   curl -H "Authorization: $CLICKUP_API_KEY" \
     https://api.clickup.com/api/v2/team
   ```

## GitHub Actions Issues

### Workflow Not Triggering

**Symptom:** Branch created but no status update in ClickUp.

**Causes & Solutions:**

1. **Actions Disabled**

   **Fix:** Enable in Settings > Actions > General.

2. **Wrong Branch Name Pattern**

   ✅ Correct: `us123/feature-name`
   ❌ Wrong: `feature/us123`, `US-123-feature`, `story-123`

   **Fix:** Use `us{number}/description` format.

3. **Workflow File Has Errors**
   ```bash
   # Validate workflow syntax
   cat .github/workflows/clickup-sync.yml
   ```

   **Fix:** Check YAML syntax, ensure proper indentation.

4. **Secret Not Set**

   **Fix:** Add `CLICKUP_API_KEY` to GitHub Secrets.

### Workflow Fails with Error

**Symptom:** Red X on commit, workflow shows failure.

**Solutions:**

1. **Check Workflow Logs**
   - Go to Actions tab in GitHub
   - Click failed workflow
   - Review error messages

2. **Common Error: Python Module Not Found**
   ```yaml
   # Ensure workflow installs dependencies
   - name: Install dependencies
     run: pip install requests
   ```

3. **Common Error: jq Command Not Found**

   Workflow uses `jq` to parse JSON. It should be pre-installed on ubuntu-latest runners.

   **Fix:** Check runner OS in workflow file.

### Workflow Succeeds but Task Not Updated

**Symptom:** Green checkmark but no ClickUp changes.

**Causes & Solutions:**

1. **Task ID Not Found**

   Check workflow logs for:
   ```
   No mapping found for US-XXX
   ```

   **Fix:** Regenerate mapping as described above.

2. **API Key Invalid in GitHub**

   **Fix:** Regenerate secret in GitHub Settings > Secrets.

3. **Conditional Step Skipped**

   Check workflow logs for "Step skipped" messages.

## Script Execution Issues

### ModuleNotFoundError: requests

**Symptom:**
```python
ModuleNotFoundError: No module named 'requests'
```

**Solution:**
```bash
pip install requests>=2.31.0
```

### Permission Denied

**Symptom:**
```bash
bash: ./scripts/clickup/sync_stories.py: Permission denied
```

**Solutions:**

1. **Make Script Executable**
   ```bash
   chmod +x scripts/clickup/sync_stories.py
   ```

2. **Run with Python**
   ```bash
   python scripts/clickup/sync_stories.py
   ```

### Import Error: clickup_client

**Symptom:**
```python
ModuleNotFoundError: No module named 'clickup_client'
```

**Solution:**
```bash
# Ensure you're in the correct directory
cd scripts/clickup

# Run script from that directory
python sync_stories.py

# Or use absolute imports
cd /path/to/project
python -m scripts.clickup.sync_stories
```

## Story Sync Issues

### Story Not Created in ClickUp

**Symptom:** Script runs without error but task doesn't appear.

**Causes & Solutions:**

1. **Invalid Story File Format**

   Required format:
   ```markdown
   # US-XXX: Title

   **Story Points:** 5
   **Priority:** Must Have
   **Sprint:** Sprint 01
   **Status:** Open
   ```

   **Fix:** Ensure all required fields present.

2. **Wrong File Naming**

   ✅ Correct: `US-001.md`, `US-123.md`
   ❌ Wrong: `story-001.md`, `US001.md`, `us-001.md`

   **Fix:** Rename files to `US-XXX.md` format.

3. **List ID Not Found**

   **Fix:** Verify `CLICKUP_BACKLOG_LIST_ID` in `.env.dev`.

### Duplicate Tasks Created

**Symptom:** Multiple tasks with same story ID.

**Causes & Solutions:**

1. **Task Search Failed**

   Script searches by story ID before creating. If search fails, duplicates occur.

   **Fix:** Delete duplicates in ClickUp, run with `--dry-run` first.

2. **Story ID Not in Task Name**

   **Fix:** Ensure existing ClickUp tasks have `US-XXX:` prefix.

## Performance Issues

### Script Takes Too Long

**Symptom:** pull_tasks.py runs for several minutes.

**Causes & Solutions:**

1. **Many Tasks in Workspace**

   Normal if you have 100+ tasks.

   **Fix:** Use `--include-closed false` to skip closed tasks.

2. **Rate Limiting**

   ClickUp limits: 100 req/min, 10 req/sec.

   **Fix:** Run less frequently, cache results.

### GitHub Actions Timeout

**Symptom:** Workflow times out after 6 hours.

**Solution:**
```yaml
# Add timeout to job
jobs:
  sync-to-clickup:
    timeout-minutes: 10
```

## Configuration Issues

### Config File Not Found

**Symptom:**
```
FileNotFoundError: config/clickup-config.json
```

**Solution:**
```bash
# Verify file exists
ls -la config/clickup-config.json

# If missing, restore from git
git checkout config/clickup-config.json

# Or recreate from documentation
```

### Invalid JSON in Config

**Symptom:**
```
json.decoder.JSONDecodeError: Expecting ',' delimiter
```

**Solution:**
```bash
# Validate JSON
python3 -m json.tool config/clickup-config.json

# Fix syntax errors (missing commas, quotes, etc.)
```

## API Rate Limiting

### 429 Too Many Requests

**Symptom:**
```
Error: 429 Too Many Requests
```

**Solution:**
```bash
# Wait 60 seconds before retrying
sleep 60

# Run operations less frequently
# Use cached data from config/clickup-tasks.json
```

**Prevention:**
- Don't run bulk operations in loops
- Use `--dry-run` to test before executing
- Cache task data locally

## Network Issues

### Connection Timeout

**Symptom:**
```
requests.exceptions.ConnectTimeout
```

**Solutions:**

1. **Check Internet Connection**
   ```bash
   ping api.clickup.com
   ```

2. **Firewall Blocking**

   **Fix:** Whitelist `api.clickup.com` in firewall.

3. **VPN Issues**

   **Fix:** Try disabling VPN temporarily.

## Data Sync Issues

### Changes Not Appearing

**Symptom:** Update script succeeds but ClickUp doesn't reflect changes.

**Solutions:**

1. **Browser Cache**

   **Fix:** Hard refresh ClickUp (Ctrl+Shift+R or Cmd+Shift+R).

2. **ClickUp Delay**

   **Fix:** Wait 30-60 seconds for ClickUp to propagate changes.

3. **Wrong Workspace**

   **Fix:** Verify `CLICKUP_SPACE_ID` matches your active workspace.

### Unexpected Task Updates

**Symptom:** Tasks changing status unexpectedly.

**Causes & Solutions:**

1. **Multiple Team Members**

   Other developers' branches may trigger updates.

   **Fix:** Coordinate with team, use clear branch names.

2. **Old Workflows Running**

   **Fix:** Cancel old workflow runs in Actions tab.

## Getting Help

If none of these solutions work:

1. **Check Workflow Logs**
   - GitHub Actions tab
   - Find failed run
   - Download logs

2. **Test Manually**
   ```bash
   # Test API connection
   export CLICKUP_API_KEY=your_key
   python3 <<EOF
   from scripts.clickup.clickup_client import get_client
   client = get_client()
   print(client.get_space_statuses())
   EOF
   ```

3. **Review ClickUp Status**
   - Check [ClickUp Status Page](https://status.clickup.com/)
   - Verify no ongoing outages

4. **Enable Debug Logging**
   ```python
   # Add to scripts for debugging
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

5. **Contact Support**
   - For ClickUp API issues: support@clickup.com
   - For integration issues: Check project repository issues
