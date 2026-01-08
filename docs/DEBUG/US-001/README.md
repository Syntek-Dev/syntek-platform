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

**Phases Completed**: Phase 1 (Models) + Phase 2 (Services) ✅
**Current Focus**: Phase 3 - GraphQL API Implementation
**Status**: All critical security issues resolved, service layer production-ready

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

**Phase 1 & 2 Resolved Issues:**
- ✅ All 6 critical security vulnerabilities resolved
- ✅ Token hashing with HMAC-SHA256 (C1)
- ✅ IP encryption and key rotation (C6)
- ✅ Password reset hash-then-store pattern (C3)
- ✅ Email verification enforcement (C5)
- ✅ Race condition prevention (H3)
- ✅ Timezone handling with DST (M5)

**Current Debugging Guides:**
- Phase 2 service layer implementation status
- Authentication flow debugging (login, registration, logout)
- Token generation and validation issues
- Session management and replay detection
- Password reset flow troubleshooting
- Email service debugging
- Audit logging verification
- IP encryption/decryption issues

**Use this when:**

- Authentication service issues
- Token hashing or validation errors
- IP encryption problems
- Email sending failures
- Audit logging not working
- Race condition debugging
- Timezone handling issues
- Password reset flow problems

---

## Common Authentication Issues (Phase 2 Updated)

### Login Not Working

**Possible Causes:**

1. Email not verified (C5 - now enforced)
2. Account locked after failed attempts (new in Phase 2)
3. Token generation failing
4. Race condition during concurrent logins
5. IP encryption issues

**Debug Steps:**

1. Check email verification status:
   ```python
   ./scripts/env/dev.sh shell
   from apps.core.models import User
   user = User.objects.get(email='user@example.com')
   print(f"Verified: {user.email_verified}")
   ```

2. Check account lockout status:
   ```python
   from apps.core.services.auth_service import AuthService
   # Check failed login count and lockout time
   ```

3. Verify token hashing:
   ```python
   from apps.core.utils.token_hasher import TokenHasher
   token = "test_token"
   hashed = TokenHasher.hash_token(token)
   print(f"Hash: {hashed}")
   ```

4. Check audit logs for login attempts:
   ```python
   from apps.core.models import AuditLog
   logs = AuditLog.objects.filter(
       user=user,
       action='LOGIN_FAILED'
   ).order_by('-created_at')[:5]
   ```

### Token Generation/Validation Errors

**Possible Causes:**

1. TOKEN_SIGNING_KEY not configured (C1)
2. Token hash mismatch
3. Token expired
4. Refresh token replay detected (H9)

**Debug Steps:**

1. Verify environment variables:
   ```bash
   ./scripts/env/dev.sh shell
   from django.conf import settings
   print(f"TOKEN_SIGNING_KEY configured: {bool(settings.TOKEN_SIGNING_KEY)}")
   ```

2. Test token hashing:
   ```python
   from apps.core.utils.token_hasher import TokenHasher
   token = TokenHasher.generate_token()
   token_hash = TokenHasher.hash_token(token)
   is_valid = TokenHasher.verify_token(token, token_hash)
   print(f"Valid: {is_valid}")  # Should be True
   ```

3. Check for replay attacks:
   ```python
   from apps.core.models import SessionToken
   # Check if refresh token already used
   session = SessionToken.objects.get(token_family='...')
   print(f"Refresh used: {session.is_refresh_token_used}")
   ```

### IP Encryption Issues

**Possible Causes:**

1. IP_ENCRYPTION_KEY not configured (C6)
2. Invalid IP address format
3. Encryption/decryption key mismatch

**Debug Steps:**

1. Test IP encryption:
   ```python
   from apps.core.utils.encryption import IPEncryption

   ip = "192.168.1.1"
   encrypted = IPEncryption.encrypt_ip(ip)
   decrypted = IPEncryption.decrypt_ip(encrypted)

   print(f"Original: {ip}")
   print(f"Decrypted: {decrypted}")
   assert ip == decrypted
   ```

2. Check audit log IP encryption:
   ```python
   from apps.core.models import AuditLog
   log = AuditLog.objects.first()
   if log and log.ip_address:
       from apps.core.utils.encryption import IPEncryption
       decrypted = IPEncryption.decrypt_ip(log.ip_address)
       print(f"Audit log IP: {decrypted}")
   ```

### Password Reset Not Working

**Possible Causes:**

1. Token not generated correctly (C3)
2. Email not sending
3. Token expired
4. Token already used

**Debug Steps:**

1. Check token generation:
   ```python
   from apps.core.services.password_reset_service import PasswordResetService
   from apps.core.models import User

   user = User.objects.get(email='user@example.com')
   token = PasswordResetService.create_reset_token(user)
   print(f"Reset token created: {token}")
   ```

2. Verify email sent:
   ```python
   from apps.core.models import AuditLog
   logs = AuditLog.objects.filter(
       action='PASSWORD_RESET_REQUESTED',
       user__email='user@example.com'
   )
   print(f"Reset requests: {logs.count()}")
   ```

### Email Verification Blocking Login

**Status:** This is now expected behaviour (C5 resolved)

**Fix:**

1. Resend verification email:
   ```python
   from apps.core.services.email_service import EmailService
   from apps.core.models import User

   user = User.objects.get(email='user@example.com')
   EmailService.send_verification_email(user)
   ```

2. Manually verify user (development only):
   ```python
   user.email_verified = True
   user.email_verified_at = timezone.now()
   user.save()
   ```

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
