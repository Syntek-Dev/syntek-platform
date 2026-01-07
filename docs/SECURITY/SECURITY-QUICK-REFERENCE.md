# Security Quick Reference

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

> **Quick reference for common security tasks and configurations**

## Table of Contents

- [Security Quick Reference](#security-quick-reference)
  - [Table of Contents](#table-of-contents)
  - [Rate Limiting](#rate-limiting)
  - [Password Requirements](#password-requirements)
  - [GraphQL Security](#graphql-security)
  - [Session Configuration](#session-configuration)
  - [Security Headers](#security-headers)
  - [Common Security Tasks](#common-security-tasks)
    - [Generating a Secret Key](#generating-a-secret-key)
    - [Blocking an IP Address](#blocking-an-ip-address)
    - [Viewing Security Logs](#viewing-security-logs)
    - [Testing Rate Limiting](#testing-rate-limiting)
  - [Environment-Specific Settings](#environment-specific-settings)
  - [Emergency Procedures](#emergency-procedures)
    - [Suspected Brute Force Attack](#suspected-brute-force-attack)
    - [Compromised Admin Account](#compromised-admin-account)
    - [Security Vulnerability Discovered](#security-vulnerability-discovered)

## Rate Limiting

| Endpoint Type     | Default Limit (per minute) | Environment Variable                             |
| ----------------- | -------------------------- | ------------------------------------------------ |
| Authentication    | 5                          | `RATELIMIT_AUTH_REQUESTS_PER_MINUTE`             |
| GraphQL Mutations | 30                         | `RATELIMIT_GRAPHQL_MUTATION_REQUESTS_PER_MINUTE` |
| GraphQL Queries   | 100                        | `RATELIMIT_GRAPHQL_QUERY_REQUESTS_PER_MINUTE`    |
| General API       | 60                         | `RATELIMIT_API_REQUESTS_PER_MINUTE`              |
| Default           | 120                        | `RATELIMIT_DEFAULT_REQUESTS_PER_MINUTE`          |

**Temporarily adjust limits:**

```bash
# .env
RATELIMIT_AUTH_REQUESTS_PER_MINUTE=10  # Double the auth limit
```

**Disable in development:**

```bash
# .env.dev
RATELIMIT_ENABLE_IN_DEBUG=False
```

## Password Requirements

```
✓ Minimum 12 characters
✓ At least 1 uppercase letter
✓ At least 1 lowercase letter
✓ At least 1 digit
✓ At least 1 special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
✓ No more than 2 sequential characters (123, abc)
✓ No more than 2 repeated characters (aaa, 111)
✓ Not similar to username/email
✓ Not a common password
```

**Adjust minimum length:**

```python
# config/settings/base.py
{
    "NAME": "config.validators.password.MinimumLengthValidator",
    "OPTIONS": {"min_length": 14},  # Change from 12 to 14
}
```

## GraphQL Security

| Setting              | Default  | Environment Variable           |
| -------------------- | -------- | ------------------------------ |
| Max Query Depth      | 10       | `GRAPHQL_MAX_QUERY_DEPTH`      |
| Max Complexity       | 1000     | `GRAPHQL_MAX_QUERY_COMPLEXITY` |
| Introspection (Dev)  | Enabled  | `GRAPHQL_ENABLE_INTROSPECTION` |
| Introspection (Prod) | Disabled | `GRAPHQL_ENABLE_INTROSPECTION` |

**Enable introspection in staging:**

```bash
# .env.staging
GRAPHQL_ENABLE_INTROSPECTION=True
```

**Increase query depth limit:**

```bash
# .env
GRAPHQL_MAX_QUERY_DEPTH=15
```

## Session Configuration

| Environment | Cookie Age | SameSite | Secure | Extends on Activity |
| ----------- | ---------- | -------- | ------ | ------------------- |
| Development | 2 weeks    | Lax      | No     | No                  |
| Production  | 1 hour     | Strict   | Yes    | Yes                 |
| Staging     | 1 hour     | Strict   | Yes    | Yes                 |

**Adjust session timeout:**

```bash
# .env.production
SESSION_COOKIE_AGE=7200  # 2 hours instead of 1
```

## Security Headers

Automatically applied headers:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: geolocation=(), microphone=(), camera=()...
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload (production)
Content-Security-Policy: <configured via django-csp>
```

**Customise CSP:**

```python
# config/settings/production.py
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "https://cdn.example.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://fonts.googleapis.com")
CSP_IMG_SRC = ("'self'", "data:", "https:")
```

## Common Security Tasks

### Generating a Secret Key

```bash
# Generate a new Django secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Blocking an IP Address

Temporarily block at the application level (add middleware):

```python
# config/middleware/ip_block.py
class IPBlockMiddleware:
    BLOCKED_IPS = ['203.0.113.42', '198.51.100.1']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip()
        if not client_ip:
            client_ip = request.META.get('REMOTE_ADDR')

        if client_ip in self.BLOCKED_IPS:
            return HttpResponseForbidden("Access denied")

        return self.get_response(request)
```

**Better approach:** Block at infrastructure level (firewall, load balancer, CDN)

### Viewing Security Logs

```bash
# Development (Docker)
./scripts/env/dev.sh logs web | grep "security.audit"

# Production
# Configure your logging service to filter by logger: security.audit
```

### Testing Rate Limiting

```bash
# Test auth endpoint rate limit (should block after 5 requests)
for i in {1..10}; do
  curl -X POST http://localhost:8000/admin/login/ \
    -d "username=test&password=test" \
    -w "\n%{http_code}\n"
  sleep 1
done
```

## Environment-Specific Settings

**Development (.env.dev):**

```bash
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
GRAPHQL_ENABLE_INTROSPECTION=True
RATELIMIT_ENABLE_IN_DEBUG=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
```

**Production (.env.production):**

```bash
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com
GRAPHQL_ENABLE_INTROSPECTION=False
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_AGE=3600
SECURE_SSL_REDIRECT=True
```

**Staging (.env.staging):**

```bash
DEBUG=False
ALLOWED_HOSTS=staging.example.com
GRAPHQL_ENABLE_INTROSPECTION=True  # Optional for testing
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_AGE=3600
SECURE_SSL_REDIRECT=True
```

## Emergency Procedures

### Suspected Brute Force Attack

1. **Identify the attack:**

   ```bash
   # Check security logs for repeated login failures
   grep "login_failure" logs/security.log | grep <IP>
   ```

2. **Block the IP address:**
   - At infrastructure level (preferred)
   - Or temporarily in application (see "Blocking an IP Address")

3. **Review affected accounts:**
   - Check if any accounts were compromised
   - Reset passwords for targeted accounts
   - Enable MFA if not already enabled

4. **Adjust rate limits if needed:**
   ```bash
   # Temporarily reduce auth rate limit
   RATELIMIT_AUTH_REQUESTS_PER_MINUTE=3
   ```

### Compromised Admin Account

1. **Immediately disable the account:**

   ```python
   # Django shell
   from django.contrib.auth import get_user_model
   User = get_user_model()
   user = User.objects.get(username='compromised_admin')
   user.is_active = False
   user.save()
   ```

2. **Force logout all sessions:**

   ```python
   # Clear all sessions
   from django.contrib.sessions.models import Session
   Session.objects.all().delete()
   ```

3. **Review security logs:**
   - Check what actions were taken
   - Identify what data was accessed
   - Look for privilege escalation attempts

4. **Reset credentials:**
   - Generate new passwords
   - Rotate API keys/tokens
   - Review and revoke permissions

### Security Vulnerability Discovered

1. **Assess severity:**
   - Critical: Patch immediately
   - High: Patch within 24 hours
   - Medium: Patch within 1 week
   - Low: Include in next regular update

2. **Apply patches:**

   ```bash
   # Update dependencies
   pip install --upgrade <package>

   # Run security checks
   python manage.py check --deploy
   bandit -r .
   ```

3. **Deploy to production:**
   - Test in staging first
   - Deploy during low-traffic period if possible
   - Monitor for issues after deployment

4. **Document:**
   - Record vulnerability details
   - Document remediation steps
   - Update security procedures if needed
