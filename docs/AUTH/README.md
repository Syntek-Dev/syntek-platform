# Authentication Documentation

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [Authentication Documentation](#authentication-documentation)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [Key Features](#key-features)
    - [Email \& Password Authentication](#email--password-authentication)
    - [Two-Factor Authentication (2FA)](#two-factor-authentication-2fa)
    - [Session Management](#session-management)
    - [Password Management](#password-management)
    - [Security Features](#security-features)
  - [Implementation Status](#implementation-status)
    - [Phase 1: Core Authentication](#phase-1-core-authentication)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains comprehensive documentation for user authentication, including email/
password authentication, two-factor authentication (2FA), session management, and password reset
flows.

---

## Directory Structure

```
AUTH/
├── README.md          # This file
└── US-001/            # User Story 001 - User Authentication
    └── [Implementation docs and technical specifications]
```

---

## Key Features

### Email & Password Authentication

- User registration with email verification
- Secure password hashing (Bcrypt)
- Login with email/password credentials
- Email verification tokens with expiration
- Secure token generation and validation

### Two-Factor Authentication (2FA)

- TOTP-based authentication using authenticator apps
- Backup codes for account recovery
- Device management (multiple devices per user)
- Secure secret storage (encrypted)

### Session Management

- API token-based authentication
- Session token expiration
- IP address tracking (encrypted)
- User agent tracking
- Token revocation and invalidation

### Password Management

- Secure password reset flow
- Password history tracking (prevent reuse)
- Password reset tokens with expiration
- Email verification before allowing password changes

### Security Features

- Bcrypt password hashing
- HMAC-SHA256 token signatures
- IP address encryption
- Time-limited tokens
- Audit logging of authentication events
- Rate limiting on login attempts
- Multi-tenancy support (organisation-scoped auth)

---

## Implementation Status

### Phase 1: Core Authentication

Status: **In Progress**

Includes:

- User model with email/password auth
- TOTP-based 2FA with backup codes
- Session token management
- Password reset with verification
- Email verification workflow
- Audit logging
- Multi-tenancy support

---

## Related Documentation

- [Core Application](../../apps/core/README.md) - User and authentication models
- [User Stories](../STORIES/) - Authentication requirements and acceptance criteria
- [User Story 001](../STORIES/US-001-USER-AUTHENTICATION.md) - Detailed specs
- [Security](../SECURITY/) - Security implementation details
- [Backend API](../BACKEND/) - Authentication API endpoints
- [Testing](../TESTS/) - Authentication test strategy

---

**Project:** Backend Template
**Framework:** Django 6.0
**Last Updated:** 08/01/2026
