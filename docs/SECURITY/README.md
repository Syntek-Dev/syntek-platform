# Security Documentation

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

> Comprehensive security implementation for Django/Wagtail

## Table of Contents

- [Security Documentation](#security-documentation)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Documents](#documents)
  - [Security Features](#security-features)
  - [Quick Reference](#quick-reference)
    - [Rate Limits (per minute)](#rate-limits-per-minute)
    - [Password Requirements](#password-requirements)
    - [Environment Variables](#environment-variables)
  - [Related Files](#related-files)

## Overview

This directory contains security documentation for the Django/Wagtail backend template. The implementation follows OWASP best practices and Django security guidelines.

## Documents

| Document                                                                 | Purpose                                                    |
| ------------------------------------------------------------------------ | ---------------------------------------------------------- |
| [SECURITY.md](SECURITY.md)                                               | Comprehensive security documentation covering all features |
| [SECURITY-QUICK-REFERENCE.md](SECURITY-QUICK-REFERENCE.md)               | Quick reference for common tasks and emergency procedures  |
| [SECURITY-IMPLEMENTATION-SUMMARY.md](SECURITY-IMPLEMENTATION-SUMMARY.md) | Implementation details and deployment checklist            |

## Security Features

| Feature                | Status | Location                         |
| ---------------------- | ------ | -------------------------------- |
| HTTP Security Headers  | Active | `config/middleware/security.py`  |
| Rate Limiting          | Active | `config/middleware/ratelimit.py` |
| Security Audit Logging | Active | `config/middleware/audit.py`     |
| Password Validators    | Active | `config/validators/password.py`  |
| GraphQL Security       | Active | `api/security.py`                |
| Session Security       | Active | `config/settings/*.py`           |
| CSRF Protection        | Active | Django built-in                  |
| SSL/TLS (Production)   | Active | `config/settings/production.py`  |

## Quick Reference

### Rate Limits (per minute)

| Endpoint          | Limit |
| ----------------- | ----- |
| Authentication    | 5     |
| GraphQL Mutations | 30    |
| GraphQL Queries   | 100   |
| General API       | 60    |
| Default           | 120   |

### Password Requirements

- Minimum 12 characters
- 1 uppercase, 1 lowercase, 1 digit, 1 special character
- No sequential/repeated characters
- Not similar to username/email

### Environment Variables

```bash
# Rate Limiting
RATELIMIT_AUTH_REQUESTS_PER_MINUTE=5

# GraphQL
GRAPHQL_MAX_QUERY_DEPTH=10
GRAPHQL_ENABLE_INTROSPECTION=False  # Production

# Sessions
SESSION_COOKIE_AGE=3600  # 1 hour (production)
```

## Related Files

| File            | Location             | Purpose                      |
| --------------- | -------------------- | ---------------------------- |
| `security.py`   | `config/middleware/` | Security headers middleware  |
| `ratelimit.py`  | `config/middleware/` | Rate limiting middleware     |
| `audit.py`      | `config/middleware/` | Security audit logging       |
| `password.py`   | `config/validators/` | Custom password validators   |
| `security.py`   | `api/`               | GraphQL security extensions  |
| `production.py` | `config/settings/`   | Production security settings |

---

**Last Updated:** 2026-01-03
