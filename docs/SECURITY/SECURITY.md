# Security Documentation

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

> **Last Updated:** 2026-01-03
> **Django Version:** 5.2

## Table of Contents

- [Security Documentation](#security-documentation)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Security Features](#security-features)
  - [HTTP Security Headers](#http-security-headers)
    - [Headers Implemented](#headers-implemented)
    - [Content Security Policy (CSP)](#content-security-policy-csp)
  - [Rate Limiting](#rate-limiting)
    - [Default Rate Limits](#default-rate-limits)
    - [Configuration](#configuration)
    - [Customising Rate Limits](#customising-rate-limits)
  - [Password Security](#password-security)
    - [Password Requirements](#password-requirements)
    - [Password Validators](#password-validators)
    - [Customising Password Rules](#customising-password-rules)
  - [Session Security](#session-security)
    - [Session Configuration](#session-configuration)
    - [Environment-Specific Settings](#environment-specific-settings)
  - [CSRF Protection](#csrf-protection)
  - [GraphQL Security](#graphql-security)
    - [Query Depth Limiting](#query-depth-limiting)
    - [Query Complexity Analysis](#query-complexity-analysis)
    - [Introspection Control](#introspection-control)
    - [Configuration](#configuration-1)
  - [Security Audit Logging](#security-audit-logging)
    - [Events Logged](#events-logged)
    - [Log Format](#log-format)
    - [Accessing Security Logs](#accessing-security-logs)
  - [SSL/TLS Configuration](#ssltls-configuration)
    - [Production Settings](#production-settings)
    - [Development Settings](#development-settings)
  - [Environment Variables](#environment-variables)
    - [Required for Production](#required-for-production)
    - [Optional Security Settings](#optional-security-settings)
  - [Security Checklist](#security-checklist)
    - [Before Deployment](#before-deployment)
    - [Production Environment](#production-environment)
  - [Security Best Practices](#security-best-practices)
    - [Application Security](#application-security)
    - [Infrastructure Security](#infrastructure-security)
    - [Development Practices](#development-practices)
  - [Incident Response](#incident-response)
    - [Security Event Monitoring](#security-event-monitoring)
    - [Responding to Security Events](#responding-to-security-events)
  - [Security Testing](#security-testing)
    - [Automated Testing](#automated-testing)
    - [Manual Testing](#manual-testing)
  - [Additional Resources](#additional-resources)

## Overview

This Django application implements comprehensive security measures following OWASP best
practices and Django security guidelines. Security is implemented at multiple layers:

- **Application Layer**: Middleware, validators, and Django security settings
- **API Layer**: GraphQL query limiting and rate limiting
- **Transport Layer**: SSL/TLS, secure cookies, HSTS
- **Audit Layer**: Security event logging and monitoring

## Security Features

| Feature                 | Status     | Environment         |
| ----------------------- | ---------- | ------------------- |
| HTTPS Enforcement       | ✅ Enabled | Production, Staging |
| HSTS Headers            | ✅ Enabled | Production, Staging |
| Secure Cookies          | ✅ Enabled | Production, Staging |
| CSRF Protection         | ✅ Enabled | All                 |
| XSS Protection Headers  | ✅ Enabled | All                 |
| Rate Limiting           | ✅ Enabled | All                 |
| Password Complexity     | ✅ Enabled | All                 |
| GraphQL Query Limiting  | ✅ Enabled | All                 |
| Security Audit Logging  | ✅ Enabled | All                 |
| Content Security Policy | ✅ Enabled | Production, Staging |

## HTTP Security Headers

### Headers Implemented

The application automatically adds the following security headers to all responses:

| Header                      | Value                                          | Purpose                             |
| --------------------------- | ---------------------------------------------- | ----------------------------------- |
| `X-Content-Type-Options`    | `nosniff`                                      | Prevents MIME type sniffing         |
| `X-Frame-Options`           | `DENY`                                         | Prevents clickjacking attacks       |
| `Referrer-Policy`           | `strict-origin-when-cross-origin`              | Controls referrer information       |
| `Permissions-Policy`        | Multiple directives                            | Disables dangerous browser features |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains; preload` | Enforces HTTPS (production only)    |
| `Content-Security-Policy`   | Configured via django-csp                      | Prevents XSS and injection attacks  |

### Content Security Policy (CSP)

CSP is configured in `config/settings/production.py`:

```python
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'",)
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:", "https:")
CSP_FONT_SRC = ("'self'",)
```

**Customisation:**
Modify these settings in your environment-specific settings file to allow additional sources.

## Rate Limiting

Rate limiting protects against brute force attacks and API abuse. Different endpoints have different
rate limits based on sensitivity.

### Default Rate Limits

| Endpoint Type     | Rate Limit (per minute) | Examples                            |
| ----------------- | ----------------------- | ----------------------------------- |
| Authentication    | 5 requests              | `/admin/`, `/cms/`, login endpoints |
| GraphQL Mutations | 30 requests             | POST to `/graphql/`                 |
| GraphQL Queries   | 100 requests            | GET to `/graphql/`                  |
| General API       | 60 requests             | `/api/*`                            |
| Other Requests    | 120 requests            | All other endpoints                 |

### Configuration

Rate limiting is implemented in `config/middleware/ratelimit.py` using Redis for distributed tracking.

**Key Features:**

- IP-based tracking
- Sliding window approach
- Automatic expiry
- Graceful degradation (allows requests if Redis is unavailable)

### Customising Rate Limits

Set environment variables to override default limits:

```bash
# .env.production
RATELIMIT_AUTH_REQUESTS_PER_MINUTE=5
RATELIMIT_GRAPHQL_MUTATION_REQUESTS_PER_MINUTE=30
RATELIMIT_GRAPHQL_QUERY_REQUESTS_PER_MINUTE=100
RATELIMIT_API_REQUESTS_PER_MINUTE=60
RATELIMIT_DEFAULT_REQUESTS_PER_MINUTE=120
```

**Disabling Rate Limiting in Development:**

```bash
# .env.dev
RATELIMIT_ENABLE_IN_DEBUG=False  # Default behaviour
```

## Password Security

### Password Requirements

All passwords must meet the following requirements:

- **Minimum Length**: 12 characters
- **Maximum Length**: 128 characters
- **Complexity**:
  - At least 1 uppercase letter
  - At least 1 lowercase letter
  - At least 1 digit
  - At least 1 special character (`!@#$%^&*()_+-=[]{}|;:,.<>?`)
- **No sequential characters**: Cannot contain 3+ sequential characters (e.g., `123`, `abc`)
- **No repeated characters**: Cannot contain 3+ repeated characters (e.g., `aaa`, `111`)
- **Not similar to user attributes**: Cannot be similar to username, email, first name, or last name
- **Not a common password**: Checked against Django's common password list

### Password Validators

Configured in `config/settings/base.py`:

```python
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        "OPTIONS": {
            "user_attributes": ("username", "email", "first_name", "last_name"),
            "max_similarity": 0.7,
        },
    },
    {
        "NAME": "config.validators.password.MinimumLengthValidator",
        "OPTIONS": {"min_length": 12},
    },
    {
        "NAME": "config.validators.password.MaximumLengthValidator",
        "OPTIONS": {"max_length": 128},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "config.validators.password.PasswordComplexityValidator",
        "OPTIONS": {
            "min_uppercase": 1,
            "min_lowercase": 1,
            "min_digits": 1,
            "min_special": 1,
        },
    },
    {
        "NAME": "config.validators.password.NoSequentialCharactersValidator",
        "OPTIONS": {"max_sequence_length": 3},
    },
    {
        "NAME": "config.validators.password.NoRepeatedCharactersValidator",
        "OPTIONS": {"max_repeated": 3},
    },
]
```

### Customising Password Rules

To change password requirements, modify the validator options in `config/settings/base.py`.

**Example: Require 14-character passwords:**

```python
{
    "NAME": "config.validators.password.MinimumLengthValidator",
    "OPTIONS": {"min_length": 14},
}
```

## Session Security

### Session Configuration

Sessions are configured with security best practices:

```python
# Base settings (all environments)
SESSION_COOKIE_HTTPONLY = True  # Prevents JavaScript access
SESSION_COOKIE_SAMESITE = "Lax"  # CSRF protection
SESSION_COOKIE_AGE = 1209600  # 2 weeks (dev/test)

# Production settings
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_SAMESITE = "Strict"  # Stricter CSRF protection
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_SAVE_EVERY_REQUEST = True  # Extend session on activity
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
```

### Environment-Specific Settings

| Environment | Cookie Age | SameSite | Secure |
| ----------- | ---------- | -------- | ------ |
| Development | 2 weeks    | Lax      | False  |
| Test        | 2 weeks    | Lax      | False  |
| Staging     | 1 hour     | Strict   | True   |
| Production  | 1 hour     | Strict   | True   |

## CSRF Protection

CSRF protection is enabled by default in Django. Additional hardening:

```python
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"  # "Strict" in production
CSRF_COOKIE_SECURE = True  # Production/staging only
CSRF_USE_SESSIONS = False  # Store in cookie for API compatibility
```

**For API endpoints:**

- Include `X-CSRFToken` header in requests
- Obtain token from `/api/csrf/` endpoint or cookie

## GraphQL Security

### Query Depth Limiting

Prevents deeply nested queries that could cause performance issues:

<!-- prettier-ignore -->
```graphql
# This query would be rejected if depth > 10
query {
  user {
    posts {
      comments {
        author {
          posts {
            comments {
              # ... 10+ levels deep
            }
          }
        }
      }
    }
  }
}
```

**Default:** 10 levels

### Query Complexity Analysis

Calculates a complexity score based on:

- Number of fields requested
- List fields (multiplier of 10)
- Nested queries

**Default Maximum:** 1000

### Introspection Control

Introspection is automatically controlled based on environment:

| Environment | Introspection                      |
| ----------- | ---------------------------------- |
| Development | ✅ Enabled                         |
| Test        | ✅ Enabled                         |
| Staging     | ⚙️ Configurable (default: enabled) |
| Production  | ❌ Disabled                        |

### Configuration

Set in environment variables:

```bash
# GraphQL Security Settings
GRAPHQL_MAX_QUERY_DEPTH=10
GRAPHQL_MAX_QUERY_COMPLEXITY=1000
GRAPHQL_ENABLE_INTROSPECTION=False
```

## Security Audit Logging

All security-relevant events are logged to a separate logger channel (`security.audit`) for monitoring and compliance.

### Events Logged

| Event Type                    | Log Level | Information Captured                |
| ----------------------------- | --------- | ----------------------------------- |
| Successful Login              | INFO      | User, IP, timestamp, user agent     |
| Failed Login                  | WARNING   | Username, IP, timestamp, user agent |
| Logout                        | INFO      | User, IP, timestamp                 |
| Authorization Failure (403)   | WARNING   | User, IP, path, method, referer     |
| Authentication Required (401) | INFO      | IP, path, method                    |
| Rate Limit Exceeded           | WARNING   | IP, path, method, limit             |

### Log Format

Production logs use JSON format for structured logging:

```json
{
  "timestamp": "2026-01-03T10:30:45.123Z",
  "level": "WARNING",
  "event_type": "login_failure",
  "username": "admin",
  "client_ip": "203.0.113.42",
  "user_agent": "Mozilla/5.0...",
  "message": "Failed login attempt for username: admin"
}
```

### Accessing Security Logs

Security logs are sent to the `security.audit` logger. Configure handlers in your logging settings to send these to:

- SIEM systems (Splunk, ELK Stack)
- Log aggregation services (Datadog, New Relic)
- File storage for compliance
- Cloud logging (CloudWatch, Stackdriver)

## SSL/TLS Configuration

### Production Settings

```python
# Force HTTPS for all requests
SECURE_SSL_REDIRECT = True

# Trust X-Forwarded-Proto header from reverse proxy
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# HSTS (HTTP Strict Transport Security)
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

**HSTS Preload:**
To add your domain to the HSTS preload list, visit: <https://hstspreload.org/>

### Development Settings

SSL is disabled in development for easier local testing:

```python
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
```

## Environment Variables

### Required for Production

```bash
# Django Core
SECRET_KEY=<strong-random-key>
DEBUG=False
ALLOWED_HOSTS=example.com,www.example.com

# Database
DATABASE_URL=postgres://user:pass@host:5432/db

# Email
EMAIL_HOST=smtp.example.com
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=<password>
DEFAULT_FROM_EMAIL=noreply@example.com

# Error Tracking
SENTRY_DSN=https://your-sentry-dsn
```

### Optional Security Settings

```bash
# Session Security
SESSION_COOKIE_AGE=3600

# Rate Limiting
RATELIMIT_AUTH_REQUESTS_PER_MINUTE=5
RATELIMIT_GRAPHQL_MUTATION_REQUESTS_PER_MINUTE=30
RATELIMIT_GRAPHQL_QUERY_REQUESTS_PER_MINUTE=100

# GraphQL Security
GRAPHQL_MAX_QUERY_DEPTH=10
GRAPHQL_MAX_QUERY_COMPLEXITY=1000
GRAPHQL_ENABLE_INTROSPECTION=False
```

## Security Checklist

### Before Deployment

- [ ] Strong `SECRET_KEY` generated and set
- [ ] `DEBUG=False` in production
- [ ] `ALLOWED_HOSTS` configured with actual domain(s)
- [ ] Database credentials secured (not default passwords)
- [ ] SSL/TLS certificate configured
- [ ] SENTRY_DSN configured for error tracking
- [ ] Email settings configured for notifications
- [ ] Security logs configured and monitored
- [ ] Rate limiting enabled and tested
- [ ] GraphQL introspection disabled in production
- [ ] CORS settings restricted to known origins
- [ ] Admin and CMS URLs protected (consider custom paths)

### Production Environment

- [ ] Regular security updates applied
- [ ] Security logs monitored daily
- [ ] Failed login attempts monitored
- [ ] Rate limit violations reviewed
- [ ] SSL certificate expiry monitoring
- [ ] Database backups encrypted and tested
- [ ] Secrets rotation schedule established
- [ ] Security incident response plan documented

## Security Best Practices

### Application Security

1. **Never commit secrets**: Use environment variables for all sensitive data
2. **Validate all input**: Even from authenticated users
3. **Use parameterised queries**: Prevent SQL injection (Django ORM does this)
4. **Sanitise output**: Prevent XSS attacks (Django templates do this)
5. **Implement proper authorization**: Check permissions, not just authentication
6. **Log security events**: Monitor for suspicious activity

### Infrastructure Security

1. **Use HTTPS everywhere**: No exceptions
2. **Keep software updated**: Django, Python, OS packages
3. **Restrict database access**: Use firewall rules and VPC
4. **Use managed services**: For Redis, PostgreSQL when possible
5. **Enable automated backups**: And test restore procedures
6. **Implement monitoring**: Application and infrastructure level

### Development Practices

1. **Run security scanners**: Bandit, safety, OWASP ZAP
2. **Keep dependencies updated**: Use Dependabot or similar
3. **Review code for security**: Include security in PR reviews
4. **Test security features**: Include security tests in CI/CD
5. **Document security decisions**: Explain why certain choices were made
6. **Follow Django security guidelines**: <https://docs.djangoproject.com/en/stable/topics/security/>

## Incident Response

### Security Event Monitoring

Monitor the following in production:

- Failed login attempts (> 5 in 5 minutes from same IP)
- Rate limit violations (excessive or from unusual IPs)
- 403/401 errors (especially for sensitive endpoints)
- Unusual GraphQL queries (very deep or complex)
- Changes to user permissions
- Admin login from new locations

### Responding to Security Events

1. **Investigate**: Review security logs for the event
2. **Contain**: Block malicious IPs, revoke compromised credentials
3. **Assess**: Determine scope and impact
4. **Remediate**: Fix vulnerabilities, patch systems
5. **Document**: Record timeline and actions taken
6. **Review**: Update procedures to prevent recurrence

## Security Testing

### Automated Testing

Run security checks in CI/CD:

```bash
# Static security analysis
bandit -r . -ll

# Dependency vulnerability scanning
safety check

# Django security checks
python manage.py check --deploy
```

### Manual Testing

Periodic security testing should include:

- Penetration testing (annually or after major changes)
- Code security review
- Dependency audit
- Configuration review
- Access control testing

## Additional Resources

- [Django Security Documentation](https://docs.djangoproject.com/en/stable/topics/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/)
- [Mozilla Web Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)
- [Let's Encrypt (Free SSL Certificates)](https://letsencrypt.org/)
