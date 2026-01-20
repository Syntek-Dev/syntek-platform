# Core Application

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [Core Application](#core-application)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [Models](#models)
    - [User Model (`models/user.py`)](#user-model-modelsuserpy)
    - [Organisation Model (`models/organisation.py`)](#organisation-model-modelsorganisationpy)
    - [Session Token Model (`models/session_token.py`)](#session-token-model-modelssession_tokenpy)
    - [TOTP Device Model (`models/totp_device.py`)](#totp-device-model-modelstotp_devicepy)
    - [Audit Log Model (`models/audit_log.py`)](#audit-log-model-modelsaudit_logpy)
    - [Password History Model (`models/password_history.py`)](#password-history-model-modelspassword_historypy)
    - [Email Verification Token \& Password Reset Token](#email-verification-token--password-reset-token)
  - [Services](#services)
    - [Permission Service (`services/permission_service.py`)](#permission-service-servicespermission_servicepy)
  - [Utils](#utils)
    - [Signed URLs (`utils/signed_urls.py`)](#signed-urls-utilssigned_urlspy)
  - [Views](#views)
    - [Health Check View (`views/health.py`)](#health-check-view-viewshealthpy)
  - [Managers](#managers)
  - [Key Features](#key-features)
    - [Multi-Tenancy](#multi-tenancy)
    - [Two-Factor Authentication](#two-factor-authentication)
    - [Audit Logging](#audit-logging)
    - [Password Management](#password-management)
  - [Usage Examples](#usage-examples)
    - [User Registration](#user-registration)
    - [Enable Two-Factor Authentication](#enable-two-factor-authentication)
    - [Check Permissions](#check-permissions)
  - [Related Documentation](#related-documentation)

---

## Overview

The core application is the foundation of the CMS platform (Phase 1). It provides essential
functionality for user authentication, organisation management, and multi-tenancy support.

This app implements:

- User authentication with email/password
- Two-factor authentication (2FA) with TOTP
- Organisation and multi-tenancy
- User profiles and roles
- Password reset and email verification
- Session management with tokens
- Password history tracking
- Audit logging
- Health check endpoints

---

## Directory Structure

```
core/
├── README.md              # This file
├── migrations/            # Database migrations (excluded from docs)
├── __init__.py
├── admin.py               # Django admin configuration
├── apps.py                # App configuration
├── managers/              # Custom database managers (empty)
├── models/                # Core data models
│   ├── __init__.py
│   ├── user.py            # User model with auth
│   ├── organisation.py     # Organisation model for tenancy
│   ├── user_profile.py     # Extended user profile
│   ├── totp_device.py      # Two-factor authentication
│   ├── session_token.py    # Session management
│   ├── audit_log.py        # Audit trail logging
│   ├── password_history.py # Password history
│   ├── base_token.py       # Base token class
│   ├── password_reset_token.py
│   └── email_verification_token.py
├── services/              # Business logic
│   ├── __init__.py
│   └── permission_service.py
├── utils/                 # Utility functions
│   ├── __init__.py
│   └── signed_urls.py
├── views/                 # View endpoints
│   ├── __init__.py
│   └── health.py
└── urls.py                # URL routing
```

---

## Models

### User Model (`models/user.py`)

The core user model extending Django's AbstractBaseUser.

**Key Fields:**

- `email` - Unique email address (login credential)
- `password` - Bcrypt hashed password
- `first_name` / `last_name` - User display name
- `organisation` - Foreign key to Organisation (multi-tenancy)
- `is_active` - Account status
- `email_verified` - Email verification flag
- `is_staff` / `is_superuser` - Admin flags
- `created_at` / `updated_at` - Timestamps

**Key Methods:**

- `get_full_name()` - Returns "First Last"
- `get_short_name()` - Returns first name
- `has_perm()` - Permission checking (multi-tenant)

### Organisation Model (`models/organisation.py`)

Represents a tenant/organisation in the multi-tenant system.

**Key Fields:**

- `name` - Organisation name
- `slug` - URL-friendly identifier
- `domain` - Custom domain (optional)
- `is_active` - Tenancy status
- `created_at` / `updated_at` - Timestamps

### Session Token Model (`models/session_token.py`)

Manages secure session tokens for API authentication.

**Key Fields:**

- `user` - Foreign key to User
- `token` - Unique token value
- `ip_address` - Encrypted IP address
- `user_agent` - Browser/client information
- `last_used_at` - Last activity timestamp
- `expires_at` - Token expiration
- `is_valid` - Token validity flag

### TOTP Device Model (`models/totp_device.py`)

Manages two-factor authentication (2FA) with TOTP.

**Key Fields:**

- `user` - Foreign key to User
- `name` - Device name (e.g., "Authenticator App")
- `secret` - Encrypted TOTP secret
- `confirmed` - Confirmation status
- `backup_codes` - Encrypted backup codes
- `created_at` / `updated_at` - Timestamps

### Audit Log Model (`models/audit_log.py`)

Tracks all significant system actions for compliance and debugging.

**Key Fields:**

- `user` - User who performed action
- `organisation` - Tenant being modified
- `action_type` - Type of action (create, update, delete, etc.)
- `model_name` - Model that was affected
- `object_id` - ID of affected object
- `changes` - JSON diff of changes
- `ip_address` - Encrypted source IP
- `user_agent` - Browser/client info
- `timestamp` - When action occurred

### Password History Model (`models/password_history.py`)

Prevents users from reusing old passwords.

**Key Fields:**

- `user` - Foreign key to User
- `password_hash` - Bcrypt hash of old password
- `created_at` - When password was set

### Email Verification Token & Password Reset Token

Secure tokens for email verification and password reset flows.

---

## Services

### Permission Service (`services/permission_service.py`)

Handles permission checking and multi-tenancy boundaries.

**Key Methods:**

- `has_organisation_access(user, org)` - Check user can access organisation
- `get_user_organisations(user)` - List organisations user belongs to
- `can_manage_user(user, target_user)` - Check if can modify user
- `filter_by_organisation(queryset, user)` - Filter queryset to user's tenant

---

## Utils

### Signed URLs (`utils/signed_urls.py`)

Generates secure, time-limited URLs for email verification and password reset.

**Key Functions:**

- `generate_email_verification_token(user)` - Create verification link
- `verify_email_token(token)` - Validate and verify email token
- `generate_password_reset_token(user)` - Create reset link
- `verify_password_reset_token(token)` - Validate reset token

**Security Features:**

- Time-limited tokens (configurable expiry)
- HMAC-SHA256 signatures
- IP address binding (optional)
- User-specific tokens (cannot be reused for other users)

---

## Views

### Health Check View (`views/health.py`)

Provides system health status endpoint.

**Endpoint:** `GET /api/health/`

**Response:**

```json
{
  "status": "healthy",
  "database": "ok",
  "cache": "ok",
  "timestamp": "2026-01-08T12:34:56Z"
}
```

---

## Managers

The `managers/` directory is currently empty but available for custom Django query managers
if needed in future. See the main apps README for examples.

---

## Key Features

### Multi-Tenancy

All data is scoped to organisations. Users belong to organisations, and data access is controlled
by organisation boundaries.

```python
# Get user's organisations
organisations = user.organisations.all()

# Get users in organisation
users = User.objects.filter(organisation=org)

# Audit logs filtered by tenant
logs = AuditLog.objects.filter(organisation=org)
```

### Two-Factor Authentication

TOTP-based 2FA with backup codes.

```python
# Create 2FA device
device = TOTPDevice.objects.create(
    user=user,
    name="Authenticator App"
)

# Confirm device (requires valid TOTP)
device.confirmed = device.verify_token(user_token)
device.save()

# Check 2FA during login
if user.totp_devices.filter(confirmed=True).exists():
    # Require TOTP verification
    pass
```

### Audit Logging

Automatic audit trail for compliance.

```python
# Manually log action
AuditLog.objects.create(
    user=user,
    organisation=org,
    action_type='delete',
    model_name='User',
    object_id=target_user.id,
    changes={'email': 'old@example.com', 'is_active': True},
    ip_address=encrypted_ip
)

# Query audit logs
logs = AuditLog.objects.filter(
    organisation=org,
    action_type='delete'
).order_by('-timestamp')
```

### Password Management

Secure password reset with history tracking.

```python
# Reset password
from apps.core.utils import signed_urls

token = signed_urls.generate_password_reset_token(user)
# Send email with token link

# Verify and update password
if signed_urls.verify_password_reset_token(token):
    user.set_password(new_password)
    user.save()
```

---

## Usage Examples

### User Registration

```python
from apps.core.models import User, Organisation
from apps.core.utils.signed_urls import generate_email_verification_token

# Create user
user = User.objects.create_user(
    email='user@example.com',
    password='secure123',
    first_name='John',
    last_name='Doe',
    organisation=organisation
)

# Generate email verification
token = generate_email_verification_token(user)
verification_link = f"https://example.com/verify/{token}/"
# Send email to user with link
```

### Enable Two-Factor Authentication

```python
from apps.core.models import TOTPDevice
import pyotp

# Create device
device = TOTPDevice.objects.create(
    user=user,
    name="My Authenticator",
    secret=pyotp.random_base32()
)

# Generate QR code for scanning
qr_uri = device.totp_key.provisioning_uri(
    name=user.email,
    issuer_name='CMS Platform'
)

# User scans QR and confirms with TOTP
user_code = input("Enter TOTP code: ")
if device.verify_token(user_code):
    device.confirmed = True
    device.save()
```

### Check Permissions

```python
from apps.core.services.permission_service import PermissionService

service = PermissionService()

# Check organisation access
if service.has_organisation_access(user, org):
    # User can access this organisation
    pass

# Filter data to user's tenant
users_in_org = service.filter_by_organisation(
    User.objects.all(),
    user
)
```

---

## Related Documentation

- [Authentication Flow](../../docs/AUTH/) - Detailed authentication documentation
- [User Stories](../../docs/STORIES/) - User requirements and acceptance criteria
- [Backend API](../../docs/BACKEND/) - API endpoint documentation
- [Database Schema](../../docs/DATABASE/) - Database architecture
- [Testing Guide](../../docs/GUIDES/TESTING.md) - Testing standards
- [GDPR Compliance](../../docs/GDPR/) - Data protection and privacy
- [Code Standards](./.claude/CLAUDE.md) - Coding conventions

---

**Last Updated:** 08/01/2026
