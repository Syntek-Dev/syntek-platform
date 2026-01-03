# GitHub Repository Secrets for ClickUp Integration

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

This document lists all GitHub repository secrets required for ClickUp integration to work properly.

## Table of Contents

- [GitHub Repository Secrets for ClickUp Integration](#github-repository-secrets-for-clickup-integration)
  - [Table of Contents](#table-of-contents)
  - [Required Secrets](#required-secrets)
    - [CLICKUP\_API\_KEY](#clickup_api_key)
  - [Optional Secrets](#optional-secrets)
    - [CLICKUP\_WEBHOOK\_SECRET](#clickup_webhook_secret)
  - [Environment Variables (Not Secrets)](#environment-variables-not-secrets)
  - [Verification](#verification)
    - [Test via GitHub Actions](#test-via-github-actions)
    - [Test Locally](#test-locally)
  - [Security Best Practices](#security-best-practices)
    - [API Key Security](#api-key-security)
    - [GitHub Secrets Security](#github-secrets-security)
  - [Troubleshooting Secret Issues](#troubleshooting-secret-issues)
    - [Secret Not Working in Actions](#secret-not-working-in-actions)
    - [Secret Value Has Spaces/Newlines](#secret-value-has-spacesnewlines)
    - [Cannot See Secret Value](#cannot-see-secret-value)
  - [Updating Secrets](#updating-secrets)
    - [When ClickUp API Key Changes](#when-clickup-api-key-changes)
    - [When Workspace Changes](#when-workspace-changes)
  - [Support](#support)

## Required Secrets

### CLICKUP_API_KEY

**Description:** ClickUp API key for authentication with ClickUp API.

**Where to get it:**
1. Log in to ClickUp
2. Click avatar (bottom left) > Settings
3. Navigate to Apps section
4. Scroll to API Token
5. Copy existing token or generate new one

**How to add:**
1. Go to GitHub repository
2. Navigate to Settings > Secrets and variables > Actions
3. Click "New repository secret"
4. Name: `CLICKUP_API_KEY`
5. Value: Your API key (starts with `pk_`)
6. Click "Add secret"

**Used in:**
- `.github/workflows/clickup-sync.yml`
- `.github/workflows/clickup-branch-sync.yml`

**Permissions required:**
- Read access to tasks, lists, folders
- Write access to update task statuses
- Comment creation permissions

---

## Optional Secrets

### CLICKUP_WEBHOOK_SECRET

**Description:** Secret key for verifying webhook signatures from ClickUp.

**Value:** Not set (optional for future webhook implementation)

**Where to get it:**
```bash
# Generate random secret
openssl rand -hex 32
```

**How to add:**
1. Generate secret using command above
2. Go to Settings > Secrets and variables > Actions
3. Click "New repository secret"
4. Name: `CLICKUP_WEBHOOK_SECRET`
5. Value: Generated secret
6. Click "Add secret"

**Used in:**
- Future webhook endpoint (not yet implemented)

**When needed:**
- If implementing bidirectional sync (ClickUp to GitHub)
- If setting up webhook listeners

---

## Environment Variables (Not Secrets)

These are configured in `config/clickup-config.json` and `.env.dev`, NOT as secrets:

| Variable | Value | Description |
|----------|-------|-------------|
| `CLICKUP_TEAM_ID` | `90151635198` | ClickUp team/workspace ID |
| `CLICKUP_SPACE_ID` | `90156744333` | ClickUp space ID (Syntek) |
| `CLICKUP_SPRINTS_FOLDER_ID` | `901512938483` | Sprints folder ID |
| `CLICKUP_BACKLOG_FOLDER_ID` | `901512938469` | Backlog folder ID |
| `CLICKUP_BACKLOG_LIST_ID` | `901519340766` | Backlog list ID |

These values are NOT sensitive and are committed to version control in `config/clickup-config.json`.

---

## Verification

After adding secrets, verify they work:

### Test via GitHub Actions

1. Create test branch:
   ```bash
   git checkout -b test-secrets
   ```

2. Make small change:
   ```bash
   echo "# Test" >> README.md
   git add README.md
   git commit -m "Test secrets"
   git push origin test-secrets
   ```

3. Check Actions tab for workflow run

4. If green checkmark, secrets are configured correctly

### Test Locally

You cannot access GitHub Secrets locally, but you can test with local `.env.dev`:

```bash
# Ensure .env.dev has API key
grep CLICKUP_API_KEY .env.dev

# Export it
export CLICKUP_API_KEY=pk_236614810_KJX43XCVU2BZC4O1Q9FIZA8XNFFSZP8P

# Test API access
python3 <<EOF
from scripts.clickup.clickup_client import get_client
client = get_client()
space = client._request('GET', f'space/{client.space_id}')
print(f"✓ Connected to: {space['name']}")
EOF
```

Expected output: `✓ Connected to: Syntek`

---

## Security Best Practices

### API Key Security

1. **Never commit API keys** to version control
   - Keys should only be in `.env.dev` (gitignored)
   - Or in GitHub Secrets (encrypted)

2. **Rotate keys regularly**
   - Every 90 days or after team member leaves
   - After any suspected compromise

3. **Use minimum required permissions**
   - ClickUp allows scoped API keys
   - Request only necessary permissions

4. **Monitor API key usage**
   - Review ClickUp audit logs periodically
   - Watch for unexpected API calls

### GitHub Secrets Security

1. **Limit repository access**
   - Only trusted contributors should have admin access
   - Use branch protection rules

2. **Audit secret access**
   - Review workflow runs regularly
   - Check who can edit workflows

3. **Use environment protection rules**
   - Require approval for production deployments
   - Settings > Environments > Protection rules

---

## Troubleshooting Secret Issues

### Secret Not Working in Actions

**Symptom:** Workflow fails with authentication error.

**Solutions:**

1. **Verify secret exists**
   - Settings > Secrets and variables > Actions
   - Check `CLICKUP_API_KEY` is listed

2. **Check secret name in workflow**
   ```yaml
   env:
     CLICKUP_API_KEY: ${{ secrets.CLICKUP_API_KEY }}
   ```
   Name must match exactly (case-sensitive)

3. **Regenerate secret**
   - Delete old secret in GitHub
   - Generate new API key in ClickUp
   - Add new secret with same name

### Secret Value Has Spaces/Newlines

**Symptom:** Authentication fails with correct key.

**Solution:**
- Ensure no leading/trailing spaces when pasting
- API key should start with `pk_` and have no line breaks

### Cannot See Secret Value

**Expected Behavior:** GitHub Secrets are encrypted and cannot be viewed after creation.

**If you need to verify:**
1. Delete existing secret
2. Regenerate in ClickUp
3. Add as new secret

---

## Updating Secrets

### When ClickUp API Key Changes

1. **Generate new key in ClickUp**
   - Settings > Apps > API Token > Generate

2. **Update GitHub Secret**
   - Settings > Secrets and variables > Actions
   - Click `CLICKUP_API_KEY`
   - Click "Update secret"
   - Paste new value
   - Click "Update secret"

3. **Update local .env.dev**
   ```bash
   # Edit .env.dev
   CLICKUP_API_KEY=pk_new_key_here
   ```

4. **Test immediately**
   ```bash
   # Trigger workflow
   git commit --allow-empty -m "Test new API key"
   git push
   ```

### When Workspace Changes

If ClickUp workspace structure changes (new folders, etc.):

1. **Update config file**
   ```bash
   # Edit config/clickup-config.json
   # Update folder IDs, list IDs, etc.
   ```

2. **Commit changes**
   ```bash
   git add config/clickup-config.json
   git commit -m "Update ClickUp workspace configuration"
   git push
   ```

3. **No secret changes needed** (IDs are not secrets)

---

## Support

If you encounter issues with secrets:

1. Check [TROUBLESHOOTING.MD](TROUBLESHOOTING.MD)
2. Review GitHub Actions logs
3. Verify ClickUp API key in ClickUp Settings
4. Test locally with exported environment variable

Remember: Secrets are encrypted and secure. You can freely regenerate and update them without security risk.
