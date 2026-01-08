# User Story 001 - Debugging Guide

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [User Story 001 - Debugging Guide](#user-story-001---debugging-guide)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [Debugging Reports](#debugging-reports)
  - [Common Authentication Issues](#common-authentication-issues)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains debugging guides and issue analysis reports specific to User Story 001
(User Authentication). Use these to diagnose and resolve authentication-related issues.

**Phase**: Phase 1 - Core Authentication
**Focus**: User models, authentication flows, 2FA, session management

---

## Directory Structure

```
US-001/
├── README.md                    # This file
└── DEBUG-US-001-REPORT.md       # Detailed debugging analysis and solutions
```

---

## Debugging Reports

### DEBUG-US-001-REPORT.md

Comprehensive debugging documentation including:

- Known issues and resolutions
- Common error messages and causes
- Step-by-step troubleshooting guides
- Authentication flow debugging
- 2FA configuration issues
- Session management problems
- Token generation and validation issues
- Database-related issues
- GraphQL-specific problems
- Testing authentication locally
- Logging and inspection techniques

**Use this when:**

- Authentication tests are failing
- User registration not working
- Login issues occurring
- 2FA setup problems
- Session token errors
- Password reset failures

---

## Common Authentication Issues

### Login Not Working

**Possible Causes:**

1. User not created
2. Password incorrect or not hashed properly
3. Token generation failing
4. Database connection issues

**Debug Steps:**

1. Check user exists: `./scripts/env/dev.sh shell`
   ```python
   from apps.core.models import User
   User.objects.filter(email='user@example.com').exists()
   ```
2. Verify password: `user.check_password('password')`
3. Check token generation
4. Review application logs

### 2FA Issues

**Possible Causes:**

1. TOTP secret not generated correctly
2. Clock skew on server/device
3. Backup codes not stored
4. Device not marked as verified

**Debug Steps:**

1. Check TOTP device exists
2. Verify secret is encrypted/decrypted correctly
3. Check device verification status
4. Test TOTP code generation

### Session Token Expiration

**Possible Causes:**

1. Token lifetime too short
2. Token not being refreshed
3. Middleware not reading token correctly
4. Database session cleanup running

**Debug Steps:**

1. Check token expiration settings
2. Verify token in database
3. Check authentication middleware
4. Review session cleanup jobs

---

## Related Documentation

- [Parent Debugging](../README.md) - Debugging index
- [Implementation](../../AUTH/US-001/README.md) - Implementation details
- [Testing](../../TESTS/) - Test documentation
- [Core Models](../../../apps/core/models/README.md) - Model definitions
- [Logging](../../LOGGING/) - Logging setup

---

**Project:** Backend Template
**Framework**: Django 5.2
**Last Updated**: 08/01/2026
