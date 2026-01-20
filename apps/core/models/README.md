# Core Models

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team

---

## Table of Contents

- [Core Models](#core-models)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Models Index](#models-index)
  - [Model Relationships](#model-relationships)
  - [Key Patterns](#key-patterns)
    - [1. Timestamps](#1-timestamps)
    - [2. Multi-Tenancy](#2-multi-tenancy)
    - [3. Token Pattern](#3-token-pattern)
    - [4. Encryption Fields](#4-encryption-fields)
    - [5. JSON Fields](#5-json-fields)
    - [6. Indexes](#6-indexes)

---

## Overview

This directory contains all Django models for the core application. Each model represents a key
entity in the authentication and multi-tenancy system.

**File Structure:**

```
models/
├── __init__.py                    # Imports all models for easy access
├── user.py                        # User authentication model
├── organisation.py                # Organisation/tenant model
├── user_profile.py                # Extended user profile
├── totp_device.py                 # Two-factor authentication
├── session_token.py               # Session management tokens
├── audit_log.py                   # Audit trail logging
├── password_history.py            # Password history tracking
├── base_token.py                  # Base token class (abstract)
├── password_reset_token.py        # Password reset tokens
└── email_verification_token.py    # Email verification tokens
```

---

## Models Index

| Model                    | Purpose                          | Key Fields                    |
| ------------------------ | -------------------------------- | ----------------------------- |
| `User`                   | User authentication              | email, password, organisation |
| `Organisation`           | Tenant/organisation              | name, slug, domain            |
| `UserProfile`            | Extended user information        | bio, avatar_url, preferences  |
| `TOTPDevice`             | Two-factor authentication device | secret, confirmed, backup     |
| `SessionToken`           | API session tokens               | token, expires_at, ip_address |
| `AuditLog`               | Action audit trail               | action_type, changes, user    |
| `PasswordHistory`        | Previous password hashes         | password_hash, created_at     |
| `BaseToken`              | Abstract base for token models   | user, created_at, expires_at  |
| `PasswordResetToken`     | Password reset tokens            | token, user, expires_at       |
| `EmailVerificationToken` | Email verification tokens        | token, user, verified_at      |

---

## Model Relationships

```
User (1) ──┬── (Many) SessionToken
           ├── (Many) TOTPDevice
           ├── (Many) PasswordHistory
           ├── (Many) AuditLog (as actor)
           ├── (Many) AuditLog (as target)
           ├── (1) UserProfile
           ├── (1) Organisation (FK)
           └── (Many) Email/Password/etc Tokens

Organisation (1) ──┬── (Many) User
                   ├── (Many) AuditLog
                   └── Other app-specific data
```

---

## Key Patterns

### 1. Timestamps

All models include `created_at` and `updated_at` fields using `auto_now_add` and `auto_now`:

```python
created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)
```

### 2. Multi-Tenancy

Most models include an `organisation` foreign key to scope data:

```python
organisation = models.ForeignKey(
    Organisation,
    on_delete=models.CASCADE,
    related_name='audit_logs'
)
```

### 3. Token Pattern

Token models inherit from `BaseToken` for common functionality:

```python
class MyToken(BaseToken):
    """Custom token model."""

    custom_field = models.CharField(max_length=255)
```

The `BaseToken` provides:

- `token` (unique)
- `created_at`
- `expires_at`
- `is_valid()` method
- `is_expired()` method

### 4. Encryption Fields

Sensitive fields use encryption (e.g., IP addresses, secrets):

```python
ip_address = EncryptedCharField(
    max_length=39,  # Max IPv6 length
    blank=True
)
```

### 5. JSON Fields

Complex data stored as JSON (e.g., audit changes):

```python
changes = models.JSONField(
    default=dict,
    help_text="JSON diff of changes"
)
```

### 6. Indexes

Key models include database indexes for performance:

```python
class Meta:
    indexes = [
        models.Index(fields=['user', '-created_at']),
        models.Index(fields=['organisation', 'action_type']),
    ]
```

---

**Last Updated:** 08/01/2026
