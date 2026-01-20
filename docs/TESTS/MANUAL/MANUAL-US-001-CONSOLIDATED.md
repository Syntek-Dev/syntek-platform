# Manual Testing Guide: US-001 User Authentication (Consolidated)

**Last Updated:** 19/01/2026
**Author:** Test Writer Agent
**User Story:** US-001 User Authentication
**Status:** Comprehensive Testing Guide
**Language:** British English (en_GB)
**Timezone:** Europe/London
**Date Format:** DD/MM/YYYY

---

## Table of Contents

- [Manual Testing Guide: US-001 User Authentication (Consolidated)](#manual-testing-guide-us-001-user-authentication-consolidated)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Prerequisites](#prerequisites)
  - [Test Environment Setup](#test-environment-setup)
  - [1. Registration Testing](#1-registration-testing)
    - [Scenario 1.1: Complete Registration Workflow (Happy Path)](#scenario-11-complete-registration-workflow-happy-path)
    - [Scenario 1.2: Registration with Weak Password](#scenario-12-registration-with-weak-password)
    - [Scenario 1.3: Registration with Duplicate Email](#scenario-13-registration-with-duplicate-email)
    - [Scenario 1.4: Registration with Unicode Names](#scenario-14-registration-with-unicode-names)
    - [Scenario 1.5: Registration with Invalid Email Format](#scenario-15-registration-with-invalid-email-format)
  - [2. Login/Authentication Testing](#2-loginauthentication-testing)
    - [Scenario 2.1: Successful Login with Verified Email](#scenario-21-successful-login-with-verified-email)
    - [Scenario 2.2: Login with Unverified Email (Critical C5)](#scenario-22-login-with-unverified-email-critical-c5)
    - [Scenario 2.3: Login with Invalid Credentials](#scenario-23-login-with-invalid-credentials)
    - [Scenario 2.4: Account Lockout After Failed Attempts](#scenario-24-account-lockout-after-failed-attempts)
    - [Scenario 2.5: Login with Race Condition Prevention (High Priority H3)](#scenario-25-login-with-race-condition-prevention-high-priority-h3)
  - [3. Password Reset Testing](#3-password-reset-testing)
    - [Scenario 3.1: Complete Password Reset Flow (Happy Path)](#scenario-31-complete-password-reset-flow-happy-path)
    - [Scenario 3.2: Password Reset Token Hashing (Critical C3)](#scenario-32-password-reset-token-hashing-critical-c3)
    - [Scenario 3.3: Password Reset with Token Expiry](#scenario-33-password-reset-with-token-expiry)
    - [Scenario 3.4: Password History Prevention (High Priority H11)](#scenario-34-password-history-prevention-high-priority-h11)
    - [Scenario 3.5: Session Revocation After Password Reset](#scenario-35-session-revocation-after-password-reset)
  - [4. Email Verification Testing](#4-email-verification-testing)
    - [Scenario 4.1: Email Verification Workflow (Happy Path)](#scenario-41-email-verification-workflow-happy-path)
    - [Scenario 4.2: Email Verification Token Expiry](#scenario-42-email-verification-token-expiry)
    - [Scenario 4.3: Single-Use Token Enforcement (High Priority H12)](#scenario-43-single-use-token-enforcement-high-priority-h12)
    - [Scenario 4.4: Verification Email Resend Cooldown (Medium Priority M2)](#scenario-44-verification-email-resend-cooldown-medium-priority-m2)
    - [Scenario 4.5: Async Email Delivery (High Priority H6)](#scenario-45-async-email-delivery-high-priority-h6)
  - [5. Two-Factor Authentication (2FA/MFA) Testing](#5-two-factor-authentication-2famfa-testing)
    - [Scenario 5.1: Complete 2FA Setup Workflow](#scenario-51-complete-2fa-setup-workflow)
    - [Scenario 5.2: 2FA Login Challenge](#scenario-52-2fa-login-challenge)
    - [Scenario 5.3: TOTP Secret Encryption (Critical C2)](#scenario-53-totp-secret-encryption-critical-c2)
    - [Scenario 5.4: Backup Code Generation and Usage](#scenario-54-backup-code-generation-and-usage)
    - [Scenario 5.5: Account Recovery with Backup Codes (Medium Priority M4)](#scenario-55-account-recovery-with-backup-codes-medium-priority-m4)
  - [6. Session Management Testing](#6-session-management-testing)
    - [Scenario 6.1: Session Token Creation and Refresh](#scenario-61-session-token-creation-and-refresh)
    - [Scenario 6.2: Refresh Token Replay Detection (High Priority H9)](#scenario-62-refresh-token-replay-detection-high-priority-h9)
    - [Scenario 6.3: Concurrent Session Limit (High Priority H12)](#scenario-63-concurrent-session-limit-high-priority-h12)
    - [Scenario 6.4: JWT Token Verification](#scenario-64-jwt-token-verification)
    - [Scenario 6.5: Session Revocation on Logout](#scenario-65-session-revocation-on-logout)
  - [7. GraphQL Security Testing](#7-graphql-security-testing)
    - [Scenario 7.1: CSRF Protection for Mutations (Critical C4)](#scenario-71-csrf-protection-for-mutations-critical-c4)
    - [Scenario 7.2: Queries Without CSRF Token](#scenario-72-queries-without-csrf-token)
    - [Scenario 7.3: Organisation Boundary Enforcement](#scenario-73-organisation-boundary-enforcement)
    - [Scenario 7.4: Query Depth Limiting](#scenario-74-query-depth-limiting)
    - [Scenario 7.5: Query Complexity Limiting](#scenario-75-query-complexity-limiting)
    - [Scenario 7.6: Introspection Control](#scenario-76-introspection-control)
  - [8. Security and Edge Case Testing](#8-security-and-edge-case-testing)
    - [Scenario 8.1: SQL Injection Prevention](#scenario-81-sql-injection-prevention)
    - [Scenario 8.2: XSS Prevention in User Fields](#scenario-82-xss-prevention-in-user-fields)
    - [Scenario 8.3: IP Encryption and Decryption (Critical C6)](#scenario-83-ip-encryption-and-decryption-critical-c6)
    - [Scenario 8.4: IP Encryption Key Rotation](#scenario-84-ip-encryption-key-rotation)
    - [Scenario 8.5: Token Hashing with HMAC-SHA256 (Critical C1)](#scenario-85-token-hashing-with-hmac-sha256-critical-c1)
    - [Scenario 8.6: Rate Limiting Effectiveness](#scenario-86-rate-limiting-effectiveness)
    - [Scenario 8.7: Timezone Handling with DST (Medium Priority M5)](#scenario-87-timezone-handling-with-dst-medium-priority-m5)
  - [API Testing Reference](#api-testing-reference)
    - [GraphQL: User Registration](#graphql-user-registration)
    - [GraphQL: User Login](#graphql-user-login)
    - [GraphQL: Password Reset Request](#graphql-password-reset-request)
    - [GraphQL: Password Reset Completion](#graphql-password-reset-completion)
    - [GraphQL: Email Verification](#graphql-email-verification)
    - [GraphQL: Enable 2FA](#graphql-enable-2fa)
    - [GraphQL: Verify 2FA](#graphql-verify-2fa)
    - [GraphQL: Refresh Token](#graphql-refresh-token)
    - [cURL: Registration](#curl-registration)
    - [cURL: Login](#curl-login)
  - [Database Verification Procedures](#database-verification-procedures)
  - [Email Testing with Mailpit](#email-testing-with-mailpit)
  - [Security Verification Checklist](#security-verification-checklist)
  - [Performance Testing Guidelines](#performance-testing-guidelines)
  - [Regression Testing Checklist](#regression-testing-checklist)
  - [Known Issues and Limitations](#known-issues-and-limitations)
  - [Sign-Off](#sign-off)

---

## Overview

This comprehensive manual testing guide consolidates all testing procedures for US-001 User Authentication across all development phases (1-7). It covers the complete authentication system including registration, login, password reset, email verification, two-factor authentication, session management, and GraphQL security features.

## US-001 Scope Definition

### In Scope (US-001: User Authentication)

**Core Authentication Features:**

- ✅ User registration with email and password
- ✅ User login and logout workflows
- ✅ Password reset and recovery mechanisms
- ✅ Email verification enforcement
- ✅ Two-factor authentication (TOTP) setup and verification
- ✅ Session token management (JWT access and refresh tokens)
- ✅ Token refresh and replay detection
- ✅ Concurrent session limiting
- ✅ Account lockout after failed login attempts

**Security Features:**

- ✅ Password hashing and validation (complexity, history, breach checking)
- ✅ Token hashing (HMAC-SHA256 for session tokens)
- ✅ TOTP secret encryption (Fernet)
- ✅ IP address encryption for audit logs
- ✅ CSRF protection for GraphQL mutations
- ✅ Rate limiting for authentication endpoints
- ✅ Multi-tenancy security (organisation boundary enforcement for authenticated users)
- ✅ SQL injection and XSS prevention in authentication forms
- ✅ User enumeration prevention (consistent error messages)

**Email Workflows:**

- ✅ Verification email sending (async with Celery)
- ✅ Password reset email sending
- ✅ Email resend cooldown mechanisms
- ✅ Email token expiry and single-use enforcement

**Audit and Logging:**

- ✅ Authentication event logging (login, logout, password change)
- ✅ Failed login attempt tracking
- ✅ Suspicious activity detection
- ✅ Security event logging (lockouts, replays, key rotations)

### Out of Scope (Deferred to Other User Stories)

**US-002: Role-Based Access Control (RBAC)**

- ❌ User role management (admin, moderator, user roles)
- ❌ Permission assignment to roles
- ❌ Role-based resource access control
- ❌ Permission checking beyond basic authentication (IsAuthenticated)
- ❌ Fine-grained permissions for specific actions

**US-003: Organisation Management**

- ❌ Creating, updating, or deleting organisations
- ❌ Organisation settings and configuration
- ❌ Inviting users to organisations
- ❌ Organisation owner/admin management
- ❌ Organisation-level feature toggles
- ❌ Multi-organisation user management

**US-011: Admin User Management**

- ❌ Admin dashboard for user management
- ❌ Bulk user operations (import, export, bulk delete)
- ❌ User impersonation by admins
- ❌ Admin-initiated password resets
- ❌ User account suspension/activation by admins

**Other Features Not in US-001:**

- ❌ User profile management (beyond authentication)
- ❌ Avatar uploads and profile customisation
- ❌ API key generation and management
- ❌ OAuth/SSO integration (social login)
- ❌ User preferences and settings
- ❌ Notification preferences

**Note on Organisation Boundaries:**
The multi-tenancy boundary enforcement tested in Scenario 7.3 is **IN SCOPE** for US-001 because it verifies that authenticated users cannot access data from other organisations. This is an authentication security feature, not organisation management. We test that the authentication system correctly scopes queries to the authenticated user's organisation.

**Security Requirements Covered:**

- **Critical:** C1 (Token Hashing), C2 (TOTP Encryption), C3 (Password Reset Hash), C4 (CSRF Protection), C5 (Email Verification), C6 (IP Encryption)
- **High Priority:** H1-H13 (Token families, race conditions, password policies, etc.)
- **Medium Priority:** M1-M5 (Cooldowns, DST handling, account recovery)

---

## Prerequisites

Before beginning manual testing:

- [ ] Development environment running (`./scripts/env/dev.sh start`)
- [ ] Test database configured and migrated (`./scripts/env/dev.sh migrate`)
- [ ] Environment variables configured (`.env.dev`):
  - `TOKEN_SIGNING_KEY` set
  - `IP_ENCRYPTION_KEY` set
  - `TOTP_ENCRYPTION_KEY` set
  - `SECRET_KEY` set
- [ ] GraphQL endpoint accessible at `http://localhost:8000/graphql/`
- [ ] Mailpit running at `http://localhost:8025` for email verification
- [ ] Celery worker running for async tasks (`./scripts/env/dev.sh celery`)
- [ ] TOTP authenticator app installed (Google Authenticator, Authy, etc.)
- [ ] HTTP client available (Postman, Insomnia, cURL, or GraphQL Playground)
- [ ] Test organisation created with slug "test-org"

---

## Test Environment Setup

```bash
# 1. Start development environment
./scripts/env/dev.sh start

# 2. Verify services are running
./scripts/env/dev.sh health

# 3. Run database migrations
./scripts/env/dev.sh migrate

# 4. Create test organisation
./scripts/env/dev.sh shell
>>> from apps.core.models import Organisation
>>> Organisation.objects.get_or_create(
...     slug="test-org",
...     defaults={"name": "Test Organisation", "industry": "Technology"}
... )
>>> exit()

# 5. Verify GraphQL endpoint
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { queryType { name } } }"}'

# 6. Access Mailpit (for email verification)
# Open browser: http://localhost:8025

# 7. Access GraphQL Playground
# Open browser: http://localhost:8000/graphql

# 8. Start Celery worker (in separate terminal)
./scripts/env/dev.sh celery
```

---

## 1. Registration Testing

### Scenario 1.1: Complete Registration Workflow (Happy Path)

**Purpose:** Verify users can successfully register with valid data

**Steps:**

1. Navigate to GraphQL Playground: `http://localhost:8000/graphql`

2. Execute registration mutation:

```graphql
mutation {
  register(
    input: {
      email: "testuser@example.com"
      password: "SecureP@ssw0rd!2024"
      firstName: "Test"
      lastName: "User"
      organisationSlug: "test-org"
    }
  ) {
    user {
      id
      email
      firstName
      lastName
      emailVerified
      organisation {
        name
      }
    }
  }
}
```

3. Verify database record created:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import User
>>> user = User.objects.get(email="testuser@example.com")
>>> print(f"User ID: {user.id}")
>>> print(f"Email verified: {user.email_verified}")
>>> print(f"Organisation: {user.organisation.name}")
>>> exit()
```

4. Check Mailpit for verification email:
   - Open `http://localhost:8025`
   - Verify email sent to testuser@example.com
   - Check email contains user's first name
   - Verify verification link present

**Expected Result:**

- Registration succeeds with HTTP 200
- User record created in database
- `emailVerified` is `false` initially
- Password is hashed (not plain text)
- User assigned to correct organisation
- Verification email delivered within 5 seconds
- Audit log entry created for registration

**Pass Criteria:** All steps complete without errors, user created successfully

---

### Scenario 1.2: Registration with Weak Password

**Purpose:** Verify weak passwords are rejected with clear guidance

**Steps:**

1. Attempt registration with weak password:

```graphql
mutation {
  register(
    input: {
      email: "weak@example.com"
      password: "weak"
      firstName: "Test"
      lastName: "User"
      organisationSlug: "test-org"
    }
  ) {
    user {
      email
    }
  }
}
```

2. Verify error response includes password requirements

**Expected Result:**

- Registration fails with validation error
- Error message includes requirements:
  - Minimum 12 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - At least one special character
- No user record created in database

**Pass Criteria:** Weak passwords rejected with helpful error messages

---

### Scenario 1.3: Registration with Duplicate Email

**Purpose:** Verify duplicate email addresses are prevented

**Steps:**

1. Register user with email "duplicate@example.com"

2. Attempt to register another user with same email:

```graphql
mutation {
  register(
    input: {
      email: "duplicate@example.com"
      password: "SecureP@ss123!@"
      firstName: "Duplicate"
      lastName: "User"
      organisationSlug: "test-org"
    }
  ) {
    user {
      email
    }
  }
}
```

**Expected Result:**

- Registration fails
- Error: "A user with this email already exists"
- Only one user with this email in database

**Pass Criteria:** Duplicate email prevention works correctly

---

### Scenario 1.4: Registration with Unicode Names

**Purpose:** Verify Unicode characters supported in names (Edge Case #3)

**Steps:**

1. Register with Unicode names:

```graphql
mutation {
  register(
    input: {
      email: "unicode@example.com"
      password: "SecureP@ss123!@"
      firstName: "José"
      lastName: "Müller"
      organisationSlug: "test-org"
    }
  ) {
    user {
      firstName
      lastName
    }
  }
}
```

2. Test additional Unicode scripts:
   - Chinese: 李 明
   - Arabic: محمد أحمد
   - Cyrillic: Владимир Петров
   - Emoji: 🔐 User

**Expected Result:**

- All Unicode characters stored correctly
- Names retrieved without corruption
- No encoding errors

**Pass Criteria:** Unicode support works for all tested scripts

---

### Scenario 1.5: Registration with Invalid Email Format

**Purpose:** Verify email validation prevents invalid formats

**Steps:**

1. Test invalid email formats:

```graphql
# Test 1: Missing @
mutation {
  register(
    input: {
      email: "invalidemail.com"
      password: "SecureP@ss123!@"
      firstName: "Test"
      lastName: "User"
      organisationSlug: "test-org"
    }
  ) {
    user {
      email
    }
  }
}

# Test 2: Missing domain
mutation {
  register(
    input: {
      email: "user@"
      password: "SecureP@ss123!@"
      firstName: "Test"
      lastName: "User"
      organisationSlug: "test-org"
    }
  ) {
    user {
      email
    }
  }
}

# Test 3: Invalid characters
mutation {
  register(
    input: {
      email: "user name@example.com"
      password: "SecureP@ss123!@"
      firstName: "Test"
      lastName: "User"
      organisationSlug: "test-org"
    }
  ) {
    user {
      email
    }
  }
}
```

**Expected Result:**

- All invalid formats rejected
- Clear validation error messages
- No user records created

**Pass Criteria:** Email validation prevents invalid formats

---

## 2. Login/Authentication Testing

### Scenario 2.1: Successful Login with Verified Email

**Purpose:** Verify users can login after email verification

**Steps:**

1. Register user and verify email (follow Scenario 1.1 and 4.1)

2. Execute login mutation:

```graphql
mutation {
  login(input: { email: "testuser@example.com", password: "SecureP@ssw0rd!2024" }) {
    token
    refreshToken
    user {
      id
      email
      emailVerified
    }
  }
}
```

3. Save the token for subsequent requests

4. Test token by querying current user:

```graphql
query {
  me {
    id
    email
    firstName
  }
}
```

**Expected Result:**

- Login succeeds with HTTP 200
- Access token and refresh token returned
- Tokens are JWT format (3 parts separated by dots)
- User data returned correctly
- `me` query with token returns user data
- Audit log entry created for successful login

**Pass Criteria:** Login works correctly, tokens are valid

---

### Scenario 2.2: Login with Unverified Email (Critical C5)

**Purpose:** Verify unverified users cannot login (C5 requirement)

**Steps:**

1. Register user WITHOUT verifying email:

```graphql
mutation {
  register(
    input: {
      email: "unverified@example.com"
      password: "SecureP@ss123!@"
      firstName: "Unverified"
      lastName: "User"
      organisationSlug: "test-org"
    }
  ) {
    user {
      emailVerified
    }
  }
}
```

2. Attempt to login:

```graphql
mutation {
  login(input: { email: "unverified@example.com", password: "SecureP@ss123!@" }) {
    token
  }
}
```

**Expected Result:**

- Login fails with error
- Error code: `EMAIL_NOT_VERIFIED`
- Error message: "Please verify your email address before logging in"
- No token returned
- Audit log entry for failed login attempt

**Pass Criteria:** Unverified users blocked from login (C5 satisfied)

---

### Scenario 2.3: Login with Invalid Credentials

**Purpose:** Verify invalid credentials handled securely (prevents user enumeration - M7)

**Steps:**

1. Attempt login with wrong password:

```graphql
mutation {
  login(input: { email: "testuser@example.com", password: "WrongPassword" }) {
    token
  }
}
```

2. Attempt login with non-existent email:

```graphql
mutation {
  login(input: { email: "nonexistent@example.com", password: "AnyPassword" }) {
    token
  }
}
```

**Expected Result:**

- Both return SAME error message (prevent user enumeration)
- Error: "Invalid email or password"
- No indication which field was wrong
- Failed attempts logged in audit log
- Rate limiting applied after multiple attempts

**Pass Criteria:** No user enumeration, consistent error messages

---

### Scenario 2.4: Account Lockout After Failed Attempts

**Purpose:** Verify account lockout after multiple failed login attempts

**Steps:**

1. Make 5 failed login attempts:

```bash
for i in {1..5}; do
  curl -X POST http://localhost:8000/graphql/ \
    -H "Content-Type: application/json" \
    -d '{
      "query": "mutation { login(input: {email: \"testuser@example.com\", password: \"wrong\"}) { token } }"
    }'
  echo "Attempt $i"
  sleep 1
done
```

2. Make 6th attempt:

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { login(input: {email: \"testuser@example.com\", password: \"wrong\"}) { token } }"
  }'
```

3. Attempt with correct password:

```graphql
mutation {
  login(input: { email: "testuser@example.com", password: "SecureP@ssw0rd!2024" }) {
    token
  }
}
```

4. Verify account locked in database:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import User
>>> user = User.objects.get(email="testuser@example.com")
>>> # Check lockout status
>>> exit()
```

**Expected Result:**

- First 5 attempts return "Invalid credentials"
- 6th attempt returns "Account temporarily locked"
- Correct password also fails when locked
- Account can be unlocked by admin or after timeout (30 minutes)
- All attempts logged in audit log

**Pass Criteria:** Account lockout mechanism works correctly

---

### Scenario 2.5: Login with Race Condition Prevention (High Priority H3)

**Purpose:** Verify login uses database locking to prevent race conditions

**Steps:**

1. Create test script for concurrent logins:

```python
# concurrent_login_test.py
import asyncio
import aiohttp

async def login(session, email, password):
    query = """
    mutation {
      login(input: {email: "%s", password: "%s"}) {
        token
      }
    }
    """ % (email, password)

    async with session.post('http://localhost:8000/graphql/',
                           json={'query': query}) as resp:
        return await resp.json()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [login(session, "testuser@example.com", "SecureP@ssw0rd!2024")
                for _ in range(10)]
        results = await asyncio.gather(*tasks)
        print(f"Successful logins: {len([r for r in results if 'token' in r.get('data', {}).get('login', {})])}")

asyncio.run(main())
```

2. Run concurrent login test:

```bash
python3 concurrent_login_test.py
```

3. Verify database consistency (no duplicate sessions)

**Expected Result:**

- All 10 concurrent logins succeed
- Each gets unique session token
- No database constraint violations
- No duplicate or lost updates

**Pass Criteria:** Race conditions prevented with SELECT FOR UPDATE

---

## 3. Password Reset Testing

### Scenario 3.1: Complete Password Reset Flow (Happy Path)

**Purpose:** Verify basic password reset workflow

**Steps:**

1. Request password reset:

```graphql
mutation {
  requestPasswordReset(input: { email: "testuser@example.com" }) {
    success
    message
  }
}
```

2. Check Mailpit for reset email:
   - Open `http://localhost:8025`
   - Verify reset email received
   - Extract reset token from email URL

3. Complete password reset:

```graphql
mutation {
  resetPassword(input: { token: "TOKEN_FROM_EMAIL", newPassword: "NewSecureP@ss2024!!" }) {
    success
    message
  }
}
```

4. Verify old password no longer works:

```graphql
mutation {
  login(input: { email: "testuser@example.com", password: "SecureP@ssw0rd!2024" }) {
    token
  }
}
```

5. Verify new password works:

```graphql
mutation {
  login(input: { email: "testuser@example.com", password: "NewSecureP@ss2024!!" }) {
    token
  }
}
```

**Expected Result:**

- Reset request succeeds
- Email delivered within 5 seconds
- Password reset succeeds
- Old password no longer works
- New password works for login
- All existing sessions revoked

**Pass Criteria:** Complete password reset flow works end-to-end

---

### Scenario 3.2: Password Reset Token Hashing (Critical C3)

**Purpose:** Verify password reset tokens are hashed with HMAC-SHA256 (C3 requirement)

**Steps:**

1. Request password reset for user

2. Before using token, check database:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import PasswordResetToken
>>> token = PasswordResetToken.objects.latest('created_at')
>>> print(f"Token hash: {token.token_hash}")
>>> print(f"Hash length: {len(token.token_hash)}")
>>> # Token hash should be 64 characters (SHA-256 hex)
>>> exit()
```

3. Verify plain token (from email) does NOT appear in database

4. Use token to reset password (verify it works)

**Expected Result:**

- Token hash is 64 characters (SHA-256 hex output)
- Plain token does not appear anywhere in database
- Hash cannot be reversed to obtain plain token
- Plain token from email successfully verifies against hash

**Pass Criteria:** Tokens hashed with HMAC-SHA256 before storage (C3 satisfied)

---

### Scenario 3.3: Password Reset with Token Expiry

**Purpose:** Verify expired reset tokens are rejected

**Steps:**

1. Create user and generate reset token

2. Manually expire token in database:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import PasswordResetToken
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> token = PasswordResetToken.objects.latest('created_at')
>>> token.expires_at = timezone.now() - timedelta(hours=1)
>>> token.save()
>>> exit()
```

3. Attempt to use expired token:

```graphql
mutation {
  resetPassword(input: { token: "EXPIRED_TOKEN", newPassword: "NewP@ssw0rd123!" }) {
    success
    message
  }
}
```

**Expected Result:**

- Password reset fails
- Error: "Password reset token has expired"
- Password unchanged
- User can request new reset token

**Pass Criteria:** Expired tokens rejected with clear error

---

### Scenario 3.4: Password History Prevention (High Priority H11)

**Purpose:** Verify password reset prevents reusing recent passwords (H11 requirement)

**Steps:**

1. Create user with password history:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import User, PasswordHistory
>>> from django.contrib.auth.hashers import make_password
>>> user = User.objects.get(email="testuser@example.com")
>>> # Store current password in history
>>> PasswordHistory.objects.create(
...     user=user,
...     password_hash=user.password
... )
>>> exit()
```

2. Request password reset

3. Attempt to reset to same password:

```graphql
mutation {
  resetPassword(input: { token: "RESET_TOKEN", newPassword: "SecureP@ssw0rd!2024" }) {
    success
    message
  }
}
```

**Expected Result:**

- Password reset fails
- Error: "Cannot reuse recent passwords (last 5)"
- Password unchanged
- Must choose different password

**Pass Criteria:** Password history enforcement prevents reuse (H11 satisfied)

---

### Scenario 3.5: Session Revocation After Password Reset

**Purpose:** Verify all sessions revoked after password reset

**Steps:**

1. Login from 3 different browsers/devices to create 3 sessions

2. Save tokens from each login

3. Reset password via email flow

4. Attempt to use saved tokens:

```graphql
query {
  me {
    email
  }
}
```

5. Verify sessions in database:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import User, SessionToken
>>> user = User.objects.get(email="testuser@example.com")
>>> active = SessionToken.objects.filter(user=user, revoked=False).count()
>>> print(f"Active sessions: {active}")  # Should be 0
>>> exit()
```

**Expected Result:**

- All 3 tokens fail authentication
- Error: "Session has been revoked"
- All session records marked as revoked in database
- User must login again on all devices

**Pass Criteria:** All sessions revoked after password reset

---

## 4. Email Verification Testing

### Scenario 4.1: Email Verification Workflow (Happy Path)

**Purpose:** Verify basic email verification workflow

**Steps:**

1. Register new user (follow Scenario 1.1)

2. Check Mailpit for verification email:
   - Open `http://localhost:8025`
   - Verify email received
   - Check email contains:
     - User's first name
     - Verification link with token
     - 24-hour expiry notice
     - Organisation branding (if configured)

3. Extract verification token from email URL

4. Verify email:

```graphql
mutation {
  verifyEmail(input: { token: "TOKEN_FROM_EMAIL" }) {
    success
    message
    user {
      email
      emailVerified
      emailVerifiedAt
    }
  }
}
```

5. Verify database updated:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import User
>>> user = User.objects.get(email="testuser@example.com")
>>> print(f"Email verified: {user.email_verified}")
>>> print(f"Verified at: {user.email_verified_at}")
>>> exit()
```

**Expected Result:**

- Registration succeeds with `emailVerified: false`
- Verification email delivered within 5 seconds
- Email contains correct information and link
- Verification succeeds with `success: true`
- User's `email_verified` is now `true`
- `email_verified_at` timestamp set
- Token marked as used in database

**Pass Criteria:** Complete email verification flow works

---

### Scenario 4.2: Email Verification Token Expiry

**Purpose:** Verify expired verification tokens are rejected

**Steps:**

1. Create user with verification token

2. Manually expire token:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import User, EmailVerificationToken
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> user = User.objects.get(email="expired@example.com")
>>> token = EmailVerificationToken.objects.filter(user=user).first()
>>> token.expires_at = timezone.now() - timedelta(hours=25)
>>> token.save()
>>> exit()
```

3. Attempt to verify with expired token:

```graphql
mutation {
  verifyEmail(input: { token: "EXPIRED_TOKEN" }) {
    success
    message
  }
}
```

**Expected Result:**

- Verification fails
- Error: "Verification token has expired"
- User's `email_verified` remains `false`
- User can request new verification email

**Pass Criteria:** Expired tokens rejected with appropriate error

---

### Scenario 4.3: Single-Use Token Enforcement (High Priority H12)

**Purpose:** Verify verification tokens can only be used once (H12 requirement)

**Steps:**

1. Register and verify email successfully (follow Scenario 4.1)

2. Attempt to use same verification token again:

```graphql
mutation {
  verifyEmail(input: { token: "ALREADY_USED_TOKEN" }) {
    success
    message
  }
}
```

3. Verify token status in database:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import EmailVerificationToken
>>> token = EmailVerificationToken.objects.latest('created_at')
>>> print(f"Used: {token.used}")
>>> print(f"Used at: {token.used_at}")
>>> exit()
```

**Expected Result:**

- Second verification fails
- Error: "Token has already been used"
- Token record shows `used=True` and `used_at` timestamp
- Email remains verified (doesn't revert)

**Pass Criteria:** Used tokens cannot be reused (H12 satisfied)

---

### Scenario 4.4: Verification Email Resend Cooldown (Medium Priority M2)

**Purpose:** Verify 5-minute cooldown on verification email resend (M2 requirement)

**Steps:**

1. Register user and send verification email

2. Immediately request resend:

```graphql
mutation {
  resendVerificationEmail(input: { email: "testuser@example.com" }) {
    success
    message
  }
}
```

3. Wait 5 minutes and request again:

```graphql
mutation {
  resendVerificationEmail(input: { email: "testuser@example.com" }) {
    success
    message
  }
}
```

**Expected Result:**

- First send succeeds
- Second send (within 5 min) fails
- Error: "Please wait 5 minutes before requesting a new verification email"
- Third send (after 5 min) succeeds with new token
- Old tokens remain valid until expiry

**Pass Criteria:** 5-minute cooldown enforced (M2 satisfied)

---

### Scenario 4.5: Async Email Delivery (High Priority H6)

**Purpose:** Verify emails sent asynchronously via Celery (H6 requirement)

**Steps:**

1. Ensure Celery worker is running:

```bash
# In separate terminal
./scripts/env/dev.sh celery
```

2. Monitor Celery logs while requesting verification email

3. Request verification email:

```graphql
mutation {
  resendVerificationEmail(input: { email: "async@example.com" }) {
    success
  }
}
```

4. Check Celery logs for task execution:

```
[2026-01-19 12:34:56] Task send_verification_email[...] received
[2026-01-19 12:34:57] Task send_verification_email[...] succeeded
```

5. Test retry logic by simulating SMTP failure:
   - Stop Mailpit temporarily
   - Request email
   - Observe Celery retry with exponential backoff
   - Restart Mailpit
   - Verify email eventually delivered

**Expected Result:**

- Email task queued in Celery immediately
- Mutation returns before email sent (async)
- Task processed in background
- Failed tasks retry: 1s, 2s, 4s, 8s, 16s
- After 5 retries, task moves to dead letter queue
- Email delivered within 5 seconds (when Mailpit available)

**Pass Criteria:** Async email delivery with Celery works (H6 satisfied)

---

## 5. Two-Factor Authentication (2FA/MFA) Testing

### Scenario 5.1: Complete 2FA Setup Workflow

**Purpose:** Verify users can enable 2FA with TOTP

**Steps:**

1. Login and get access token:

```graphql
mutation {
  login(input: { email: "testuser@example.com", password: "SecureP@ssw0rd!2024" }) {
    token
  }
}
```

2. Enable 2FA (use Authorization header with token):

```graphql
mutation {
  enable2FA {
    secret
    qrCodeUrl
    backupCodes
  }
}
```

3. Scan QR code with authenticator app (Google Authenticator, Authy)

4. Get 6-digit TOTP code from app

5. Verify 2FA setup:

```graphql
mutation {
  verify2FA(input: { code: "123456" }) {
    success
    message
  }
}
```

6. Verify 2FA enabled in database:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import User
>>> user = User.objects.get(email="testuser@example.com")
>>> print(f"2FA enabled: {user.two_factor_enabled}")
>>> exit()
```

**Expected Result:**

- Enable2FA returns secret, QR code URL, and backup codes
- User can scan QR code
- 6-digit code from app verifies successfully
- User's `two_factor_enabled` is `true`
- Backup codes stored encrypted in database

**Pass Criteria:** Complete 2FA setup workflow works

---

### Scenario 5.2: 2FA Login Challenge

**Purpose:** Verify 2FA challenge during login

**Steps:**

1. Ensure user has 2FA enabled (follow Scenario 5.1)

2. Logout:

```graphql
mutation {
  logout {
    success
  }
}
```

3. Login with credentials:

```graphql
mutation {
  login(input: { email: "testuser@example.com", password: "SecureP@ssw0rd!2024" }) {
    requiresTwoFactor
    token
    twoFactorToken
  }
}
```

4. Get TOTP code from authenticator app

5. Complete 2FA challenge:

```graphql
mutation {
  verifyLogin2FA(input: { twoFactorToken: "TOKEN_FROM_STEP_3", code: "123456" }) {
    token
    refreshToken
    user {
      email
    }
  }
}
```

**Expected Result:**

- Login returns `requiresTwoFactor: true`
- Access token is `null` initially
- Temporary 2FA token provided
- After TOTP verification, full access token granted
- User can access protected resources

**Pass Criteria:** 2FA challenge works correctly

---

### Scenario 5.3: TOTP Secret Encryption (Critical C2)

**Purpose:** Verify TOTP secrets encrypted with Fernet (C2 requirement)

**Steps:**

1. Enable 2FA for user

2. Check database for encrypted secret:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import TOTPDevice
>>> device = TOTPDevice.objects.latest('created_at')
>>> print(f"Encrypted secret (bytes): {device.encrypted_secret}")
>>> print(f"Secret length: {len(device.encrypted_secret)}")
>>> # Should be bytes, not plain text
>>> # Should be longer than plain secret due to encryption
>>> exit()
```

3. Verify secret can be decrypted:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import TOTPDevice
>>> from apps.core.utils.totp import decrypt_totp_secret
>>> device = TOTPDevice.objects.latest('created_at')
>>> plain_secret = decrypt_totp_secret(device.encrypted_secret)
>>> print(f"Decrypted secret: {plain_secret}")
>>> # Should be 32-character base32 string
>>> exit()
```

**Expected Result:**

- TOTP secret stored as encrypted bytes in database
- Plain secret not visible in database
- Secret can be decrypted with correct key
- Wrong key fails to decrypt

**Pass Criteria:** TOTP secrets encrypted with Fernet (C2 satisfied)

---

### Scenario 5.4: Backup Code Generation and Usage

**Purpose:** Verify backup codes generated and can be used for 2FA

**Steps:**

1. Enable 2FA and save backup codes from response

2. Logout and login (trigger 2FA challenge)

3. Use backup code instead of TOTP:

```graphql
mutation {
  verifyLogin2FA(input: { twoFactorToken: "TEMP_TOKEN", backupCode: "1234-5678-90AB" }) {
    token
    user {
      email
    }
  }
}
```

4. Verify backup code marked as used:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import BackupCode
>>> code = BackupCode.objects.filter(used=True).latest('used_at')
>>> print(f"Used: {code.used}")
>>> print(f"Used at: {code.used_at}")
>>> exit()
```

5. Attempt to reuse same backup code (should fail)

**Expected Result:**

- Login with backup code succeeds
- Backup code marked as used
- Used backup code cannot be reused
- User warned when few backup codes remain

**Pass Criteria:** Backup codes work and single-use enforced

---

### Scenario 5.5: Account Recovery with Backup Codes (Medium Priority M4)

**Purpose:** Verify account recovery using backup codes (M4 requirement)

**Steps:**

1. Create user with 2FA enabled and backup codes

2. Simulate user losing authenticator app access

3. Request account recovery with backup code:

```graphql
mutation {
  recoverAccountWithBackupCode(
    input: { email: "testuser@example.com", backupCode: "ABCD-EFGH-IJKL" }
  ) {
    success
    temporaryToken
    message
  }
}
```

4. Use temporary token to disable 2FA or set new TOTP:

```graphql
mutation {
  reset2FA(input: { temporaryToken: "TEMP_TOKEN" }) {
    success
    newSecret
    newQrCodeUrl
    newBackupCodes
  }
}
```

**Expected Result:**

- Recovery with backup code succeeds
- Temporary token granted (15-minute expiry)
- User can disable 2FA or set up new TOTP
- Backup code marked as used
- Original email notified of recovery attempt
- Security audit log entry created

**Pass Criteria:** Account recovery via backup codes works (M4 satisfied)

---

## 6. Session Management Testing

### Scenario 6.1: Session Token Creation and Refresh

**Purpose:** Verify JWT access and refresh token creation (H1)

**Steps:**

1. Login to create token pair:

```graphql
mutation {
  login(input: { email: "testuser@example.com", password: "SecureP@ssw0rd!2024" }) {
    token
    refreshToken
    tokenFamily
    user {
      email
    }
  }
}
```

2. Wait for access token to expire (default 15 minutes) or manually expire:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import SessionToken
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> token = SessionToken.objects.latest('created_at')
>>> token.expires_at = timezone.now() - timedelta(minutes=1)
>>> token.save()
>>> exit()
```

3. Attempt to use expired token (should fail)

4. Refresh token:

```graphql
mutation {
  refreshToken(input: { refreshToken: "REFRESH_TOKEN_FROM_STEP_1" }) {
    token
    refreshToken
    tokenGeneration
  }
}
```

**Expected Result:**

- Login returns access token and refresh token
- Both tokens are JWT format
- Token family ID assigned
- Expired access token rejected
- Refresh succeeds and rotates tokens
- New access token and refresh token returned
- Token generation incremented

**Pass Criteria:** Token creation and refresh work correctly (H1)

---

### Scenario 6.2: Refresh Token Replay Detection (High Priority H9)

**Purpose:** Verify refresh token replay attacks detected (H9 requirement)

**Steps:**

1. Login and get initial refresh token:

```graphql
mutation {
  login(input: { email: "testuser@example.com", password: "SecureP@ssw0rd!2024" }) {
    refreshToken
    tokenFamily
  }
}
```

2. Save refresh token as TOKEN_1

3. Refresh token (first time - should succeed):

```graphql
mutation {
  refreshToken(input: { refreshToken: "TOKEN_1" }) {
    refreshToken
    tokenGeneration
  }
}
```

4. Save new refresh token as TOKEN_2

5. Attempt to replay old token (attack):

```graphql
mutation {
  refreshToken(input: { refreshToken: "TOKEN_1" }) {
    token
  }
}
```

6. Verify entire token family revoked:

```graphql
mutation {
  refreshToken(input: { refreshToken: "TOKEN_2" }) {
    token
  }
}
```

7. Check security event in database:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import AuditLog
>>> event = AuditLog.objects.filter(
...     action="token_replay_detected"
... ).latest('created_at')
>>> print(event.metadata)
>>> exit()
```

**Expected Result:**

- First refresh succeeds, token rotated
- Replay of old token detected
- Error: "Token replay detected - all tokens in family revoked"
- Entire token family invalidated
- New token (TOKEN_2) also fails
- Security event logged
- User must login again

**Pass Criteria:** Replay detection works, family invalidation occurs (H9 satisfied)

---

### Scenario 6.3: Concurrent Session Limit (High Priority H12)

**Purpose:** Verify users cannot exceed concurrent session limit (H12 requirement)

**Steps:**

1. Configure session limit (default is 5 active sessions)

2. Login from 5 different browsers/devices:

```bash
# Use different User-Agent headers to simulate different devices
for i in {1..5}; do
  curl -X POST http://localhost:8000/graphql/ \
    -H "Content-Type: application/json" \
    -H "User-Agent: Device-$i" \
    -d '{
      "query": "mutation { login(input: {email: \"testuser@example.com\", password: \"SecureP@ssw0rd!2024\"}) { token } }"
    }' > token_$i.json
done
```

3. Verify 5 active sessions:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import User, SessionToken
>>> user = User.objects.get(email="testuser@example.com")
>>> active = SessionToken.objects.filter(user=user, revoked=False).count()
>>> print(f"Active sessions: {active}")  # Should be 5
>>> exit()
```

4. Login from 6th device:

```graphql
mutation {
  login(input: { email: "testuser@example.com", password: "SecureP@ssw0rd!2024" }) {
    token
    sessionCount
    oldestSessionRevoked
  }
}
```

5. Verify oldest session revoked:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import User, SessionToken
>>> user = User.objects.get(email="testuser@example.com")
>>> active = SessionToken.objects.filter(user=user, revoked=False).count()
>>> print(f"Active sessions: {active}")  # Should still be 5
>>> exit()
```

6. Test first token no longer works

**Expected Result:**

- Maximum 5 concurrent sessions enforced
- 6th login succeeds
- Oldest session automatically revoked
- Response includes `oldestSessionRevoked: true`
- First device token fails with "Session revoked"
- Active session count remains at 5

**Pass Criteria:** Session limit enforcement works (H12 satisfied)

---

### Scenario 6.4: JWT Token Verification

**Purpose:** Verify JWT access tokens properly signed and verified

**Steps:**

1. Login and get access token:

```graphql
mutation {
  login(input: { email: "testuser@example.com", password: "SecureP@ssw0rd!2024" }) {
    token
  }
}
```

2. Decode JWT token (without verification):

```bash
# Split token into parts
echo "TOKEN_HERE" | cut -d. -f2 | base64 -d | jq
```

3. Verify token signature:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.services.token_service import TokenService
>>> user = TokenService.verify_access_token("TOKEN_HERE")
>>> print(f"User: {user.email if user else 'Invalid'}")
>>> exit()
```

4. Modify token and attempt to use (should fail):

```bash
# Change one character in token
MODIFIED_TOKEN="..."
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $MODIFIED_TOKEN" \
  -d '{"query": "query { me { email } }"}'
```

**Expected Result:**

- Token decodes to show user ID, email, expiry
- Valid token verifies successfully
- Modified token fails verification
- Error: "Invalid token signature"
- Token uses RS256 algorithm (not HS256)

**Pass Criteria:** JWT signing and verification work correctly

---

### Scenario 6.5: Session Revocation on Logout

**Purpose:** Verify logout revokes current session

**Steps:**

1. Login and save token:

```graphql
mutation {
  login(input: { email: "testuser@example.com", password: "SecureP@ssw0rd!2024" }) {
    token
  }
}
```

2. Use token to query user (should succeed):

```graphql
query {
  me {
    email
  }
}
```

3. Logout:

```graphql
mutation {
  logout {
    success
  }
}
```

4. Attempt to use same token (should fail):

```graphql
query {
  me {
    email
  }
}
```

5. Verify session revoked in database:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import SessionToken
>>> token = SessionToken.objects.latest('created_at')
>>> print(f"Revoked: {token.revoked}")
>>> print(f"Revoked at: {token.revoked_at}")
>>> exit()
```

**Expected Result:**

- Logout returns `success: true`
- Token no longer works after logout
- Error: "Session has been revoked"
- Session record marked as revoked
- Audit log entry created for logout

**Pass Criteria:** Logout correctly revokes session

---

## 7. GraphQL Security Testing

### Scenario 7.1: CSRF Protection for Mutations (Critical C4)

**Purpose:** Verify CSRF protection enforced for mutations (C4 requirement)

**Steps:**

1. Get CSRF token:

```bash
curl -X GET http://localhost:8000/graphql/ -c cookies.txt -v
```

2. Extract CSRF token from Set-Cookie header

3. Attempt mutation WITHOUT CSRF token:

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"query": "mutation { logout { success } }"}'
```

4. Attempt mutation WITH CSRF token:

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: CSRF_TOKEN_FROM_STEP_2" \
  -b cookies.txt \
  -d '{"query": "mutation { logout { success } }"}'
```

**Expected Result:**

- Step 3: 403 Forbidden or CSRF error
- Step 4: 200 OK, mutation executes
- CSRF protection only applies to mutations, not queries

**Pass Criteria:** CSRF protection enforced for mutations (C4 satisfied)

---

### Scenario 7.2: Queries Without CSRF Token

**Purpose:** Verify queries do NOT require CSRF token

**Steps:**

1. Send query WITHOUT CSRF token:

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{"query": "query { me { email } }"}'
```

**Expected Result:**

- Query executes successfully
- No CSRF error
- Returns user data

**Pass Criteria:** Queries work without CSRF token

---

### Scenario 7.3: Organisation Boundary Enforcement

**Purpose:** Verify users can only access data from their organisation

**Steps:**

1. Create second organisation and user:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import Organisation, User
>>> org2 = Organisation.objects.create(name="Other Org", slug="other-org")
>>> user2 = User.objects.create_user(
...     email="other@example.com",
...     password="password",
...     organisation=org2,
...     email_verified=True
... )
>>> exit()
```

2. Login as user from Organisation 1

3. Query all users:

```graphql
query {
  users {
    id
    email
    organisation {
      name
    }
  }
}
```

4. Attempt to query specific user from Organisation 2:

```graphql
query {
  user(id: "USER_ID_FROM_ORG_2") {
    email
  }
}
```

**Expected Result:**

- Users query returns only Organisation 1 users
- Users from Organisation 2 not visible
- Specific user query returns null or error
- No cross-organisation data access

**Pass Criteria:** Organisation boundaries enforced correctly

---

### Scenario 7.4: Query Depth Limiting

**Purpose:** Verify deeply nested queries are rejected

**Steps:**

1. Configure max query depth (`.env.dev`):

```
GRAPHQL_MAX_QUERY_DEPTH=5
```

2. Restart server

3. Send shallow query (depth 2):

```graphql
query {
  me {
    organisation {
      name
    }
  }
}
```

4. Send deep query (depth 10):

```graphql
query {
  me {
    organisation {
      users {
        organisation {
          users {
            organisation {
              users {
                organisation {
                  name
                }
              }
            }
          }
        }
      }
    }
  }
}
```

**Expected Result:**

- Shallow query succeeds
- Deep query rejected
- Error: "Query depth of 10 exceeds maximum allowed depth of 5"

**Pass Criteria:** Query depth limiting works

---

### Scenario 7.5: Query Complexity Limiting

**Purpose:** Verify expensive queries rejected by complexity score

**Steps:**

1. Configure max complexity (`.env.dev`):

```
GRAPHQL_MAX_QUERY_COMPLEXITY=100
```

2. Send simple query (low complexity):

```graphql
query {
  me {
    id
    email
  }
}
```

3. Send expensive query (high complexity):

```graphql
query {
  users {
    id
    posts {
      id
      comments {
        id
        author {
          posts {
            id
          }
        }
      }
    }
  }
}
```

**Expected Result:**

- Simple query succeeds
- Expensive query rejected
- Error: "Query complexity exceeds maximum allowed"

**Pass Criteria:** Query complexity limiting works

---

### Scenario 7.6: Introspection Control

**Purpose:** Verify introspection disabled in production

**Steps:**

1. Configure production mode (`.env.dev`):

```
DEBUG=False
GRAPHQL_ENABLE_INTROSPECTION=False
```

2. Restart server

3. Send introspection query:

```graphql
query {
  __schema {
    types {
      name
    }
  }
}
```

4. Send regular query:

```graphql
query {
  me {
    email
  }
}
```

5. Re-enable introspection and test

**Expected Result:**

- Introspection query fails when disabled
- Error: "GraphQL introspection is disabled"
- Regular queries work normally
- Introspection works when re-enabled

**Pass Criteria:** Introspection control works

---

## 8. Security and Edge Case Testing

### Scenario 8.1: SQL Injection Prevention

**Purpose:** Verify SQL injection attempts prevented

**Steps:**

1. Attempt SQL injection in email:

```graphql
mutation {
  register(
    input: {
      email: "admin@example.com'; DROP TABLE users;--"
      password: "TestP@ss123!@"
      firstName: "Test"
      lastName: "User"
      organisationSlug: "test-org"
    }
  ) {
    user {
      email
    }
  }
}
```

2. Verify database intact:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import User
>>> print(User.objects.count())
>>> # Should be unchanged
>>> exit()
```

**Expected Result:**

- Registration fails with validation error
- No SQL executed
- Database unchanged

**Pass Criteria:** SQL injection prevented

---

### Scenario 8.2: XSS Prevention in User Fields

**Purpose:** Verify XSS payloads are escaped

**Steps:**

1. Register with XSS payload:

```graphql
mutation {
  register(
    input: {
      email: "xss@example.com"
      password: "TestP@ss123!@"
      firstName: "<script>alert('XSS')</script>"
      lastName: "User"
      organisationSlug: "test-org"
    }
  ) {
    user {
      firstName
    }
  }
}
```

2. Query user and verify output escaped:

```graphql
query {
  user(id: "USER_ID") {
    firstName
  }
}
```

**Expected Result:**

- Script tags escaped in response
- No script execution
- Payload stored as literal text

**Pass Criteria:** XSS prevention works

---

### Scenario 8.3: IP Encryption and Decryption (Critical C6)

**Purpose:** Verify IP addresses encrypted in database (C6 requirement)

**Steps:**

1. Login from specific IP:

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "X-Forwarded-For: 192.168.1.100" \
  -d '{
    "query": "mutation { login(input: {email: \"testuser@example.com\", password: \"SecureP@ssw0rd!2024\"}) { token } }"
  }'
```

2. Verify IP encrypted in database:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import AuditLog
>>> from apps.core.utils.encryption import IPEncryption
>>> log = AuditLog.objects.latest('created_at')
>>> print(f"Encrypted IP (bytes): {log.ip_address}")
>>> decrypted = IPEncryption.decrypt_ip(log.ip_address)
>>> print(f"Decrypted IP: {decrypted}")
>>> # Should show 192.168.1.100
>>> exit()
```

3. Test IPv6 encryption:

```python
ip = "2001:0db8:85a3::8a2e:0370:7334"
encrypted = IPEncryption.encrypt_ip(ip)
decrypted = IPEncryption.decrypt_ip(encrypted)
assert decrypted == ip
```

**Expected Result:**

- IP addresses stored as encrypted bytes
- Plain IPs not visible in database
- IPs can be decrypted with correct key
- IPv4 and IPv6 both supported

**Pass Criteria:** IP encryption works (C6 satisfied)

---

### Scenario 8.4: IP Encryption Key Rotation

**Purpose:** Verify IP encryption keys can be rotated

**Steps:**

1. Create audit logs with current key

2. Generate new encryption key:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.utils.encryption import IPEncryption
>>> new_key = IPEncryption.generate_key()
>>> print(new_key)
>>> exit()
```

3. Run key rotation command:

```bash
./scripts/env/dev.sh manage rotate_ip_keys --dry-run
```

4. Review rotation statistics

5. Execute rotation:

```bash
./scripts/env/dev.sh manage rotate_ip_keys --confirm
```

**Expected Result:**

- Dry-run shows what would be changed
- Rotation re-encrypts all IPs with new key
- No data loss
- All IPs remain decryptable

**Pass Criteria:** Key rotation works safely

---

### Scenario 8.5: Token Hashing with HMAC-SHA256 (Critical C1)

**Purpose:** Verify tokens hashed with HMAC-SHA256 (C1 requirement)

**Steps:**

1. Generate token:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.utils.token_hasher import TokenHasher
>>> token = TokenHasher.generate_token()
>>> print(f"Token: {token}")
>>> token_hash = TokenHasher.hash_token(token)
>>> print(f"Hash: {token_hash}")
>>> print(f"Hash length: {len(token_hash)}")
>>> # Should be 64 characters (SHA-256 hex)
>>> exit()
```

2. Verify hash is deterministic:

```python
hash1 = TokenHasher.hash_token("same_token")
hash2 = TokenHasher.hash_token("same_token")
assert hash1 == hash2
```

3. Verify different tokens have different hashes:

```python
hash_a = TokenHasher.hash_token("token_a")
hash_b = TokenHasher.hash_token("token_b")
assert hash_a != hash_b
```

4. Verify constant-time comparison:

```python
assert TokenHasher.constant_time_compare("same", "same") is True
assert TokenHasher.constant_time_compare("diff", "erent") is False
```

**Expected Result:**

- Token hashed with HMAC-SHA256
- Hash is 64-character hex string
- Hashing is deterministic
- Constant-time comparison used

**Pass Criteria:** Token hashing correct (C1 satisfied)

---

### Scenario 8.6: Rate Limiting Effectiveness

**Purpose:** Verify rate limiting prevents abuse

**Steps:**

1. Make 5 login attempts (within limit):

```bash
for i in {1..5}; do
  curl -X POST http://localhost:8000/graphql/ \
    -H "Content-Type: application/json" \
    -d '{"query": "mutation { login(input: {email: \"test@example.com\", password: \"wrong\"}) { token } }"}'
  sleep 1
done
```

2. Make 6th attempt (exceeds limit):

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { login(input: {email: \"test@example.com\", password: \"wrong\"}) { token } }"}'
```

**Expected Result:**

- First 5 attempts allowed
- 6th attempt blocked
- Error: "Rate limit exceeded"
- Retry-After header included

**Pass Criteria:** Rate limiting works

---

### Scenario 8.7: Timezone Handling with DST (Medium Priority M5)

**Purpose:** Verify timezone-aware datetime handling with DST (M5 requirement)

**Steps:**

1. Test UTC conversion:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.services.auth_service import AuthService
>>> from datetime import datetime
>>> naive_dt = datetime(2024, 6, 15, 12, 0, 0)
>>> utc_dt = AuthService.get_timezone_aware_datetime(naive_dt, "UTC")
>>> print(f"UTC datetime: {utc_dt}")
>>> assert utc_dt.tzinfo is not None
>>> exit()
```

2. Test DST transition:

```python
# June (BST - UTC+1)
summer_dt = datetime(2024, 6, 15, 12, 0, 0)
london_summer = AuthService.get_timezone_aware_datetime(
    summer_dt, "Europe/London"
)

# December (GMT - UTC+0)
winter_dt = datetime(2024, 12, 15, 12, 0, 0)
london_winter = AuthService.get_timezone_aware_datetime(
    winter_dt, "Europe/London"
)

# Offsets should differ
assert london_summer.utcoffset() != london_winter.utcoffset()
```

**Expected Result:**

- Naive datetimes converted to timezone-aware
- DST offsets calculated correctly
- Summer/winter times have different UTC offsets
- DST transition dates handled

**Pass Criteria:** DST handling correct (M5 satisfied)

---

## API Testing Reference

### GraphQL: User Registration

```graphql
mutation Register($input: RegisterInput!) {
  register(input: $input) {
    user {
      id
      email
      firstName
      lastName
      emailVerified
      organisation {
        name
      }
    }
  }
}
```

**Variables:**

```json
{
  "input": {
    "email": "testuser@example.com",
    "password": "SecureP@ssw0rd!2024",
    "firstName": "Test",
    "lastName": "User",
    "organisationSlug": "test-org"
  }
}
```

---

### GraphQL: User Login

```graphql
mutation Login($input: LoginInput!) {
  login(input: $input) {
    token
    refreshToken
    requiresTwoFactor
    twoFactorToken
    user {
      id
      email
      emailVerified
      twoFactorEnabled
    }
  }
}
```

**Variables:**

```json
{
  "input": {
    "email": "testuser@example.com",
    "password": "SecureP@ssw0rd!2024"
  }
}
```

---

### GraphQL: Password Reset Request

```graphql
mutation RequestPasswordReset($input: PasswordResetRequestInput!) {
  requestPasswordReset(input: $input) {
    success
    message
  }
}
```

**Variables:**

```json
{
  "input": {
    "email": "testuser@example.com"
  }
}
```

---

### GraphQL: Password Reset Completion

```graphql
mutation ResetPassword($input: PasswordResetInput!) {
  resetPassword(input: $input) {
    success
    message
  }
}
```

**Variables:**

```json
{
  "input": {
    "token": "TOKEN_FROM_EMAIL",
    "newPassword": "NewSecureP@ss2024!!"
  }
}
```

---

### GraphQL: Email Verification

```graphql
mutation VerifyEmail($input: EmailVerificationInput!) {
  verifyEmail(input: $input) {
    success
    message
    user {
      email
      emailVerified
      emailVerifiedAt
    }
  }
}
```

**Variables:**

```json
{
  "input": {
    "token": "TOKEN_FROM_EMAIL"
  }
}
```

---

### GraphQL: Enable 2FA

```graphql
mutation Enable2FA {
  enable2FA {
    secret
    qrCodeUrl
    backupCodes
  }
}
```

**Headers:**

```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

### GraphQL: Verify 2FA

```graphql
mutation Verify2FA($input: Verify2FAInput!) {
  verify2FA(input: $input) {
    success
    message
  }
}
```

**Variables:**

```json
{
  "input": {
    "code": "123456"
  }
}
```

---

### GraphQL: Refresh Token

```graphql
mutation RefreshToken($input: RefreshTokenInput!) {
  refreshToken(input: $input) {
    token
    refreshToken
    tokenGeneration
  }
}
```

**Variables:**

```json
{
  "input": {
    "refreshToken": "YOUR_REFRESH_TOKEN"
  }
}
```

---

### cURL: Registration

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation Register($input: RegisterInput!) { register(input: $input) { user { id email } } }",
    "variables": {
      "input": {
        "email": "curl@example.com",
        "password": "SecurePass123!@",
        "firstName": "Curl",
        "lastName": "User",
        "organisationSlug": "test-org"
      }
    }
  }'
```

---

### cURL: Login

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation Login($input: LoginInput!) { login(input: $input) { token user { email } } }",
    "variables": {
      "input": {
        "email": "curl@example.com",
        "password": "SecurePass123!@"
      }
    }
  }'
```

---

## Database Verification Procedures

After running tests, verify database state:

```bash
./scripts/env/dev.sh shell
```

```python
# In Django shell:

# 1. Verify users created
from apps.core.models import User
users = User.objects.all()
for user in users:
    print(f"{user.email} - Verified: {user.email_verified} - 2FA: {user.two_factor_enabled}")

# 2. Verify session tokens
from apps.core.models import SessionToken
active_sessions = SessionToken.objects.filter(revoked=False)
print(f"Active sessions: {active_sessions.count()}")

# 3. Verify TOTP devices
from apps.core.models import TOTPDevice
totp_devices = TOTPDevice.objects.filter(confirmed=True)
print(f"Confirmed 2FA devices: {totp_devices.count()}")

# 4. Verify audit logs
from apps.core.models import AuditLog
recent_logs = AuditLog.objects.order_by('-created_at')[:10]
for log in recent_logs:
    print(f"{log.action} - {log.user.email if log.user else 'System'} - {log.created_at}")

# 5. Verify email verification tokens
from apps.core.models import EmailVerificationToken
unused_tokens = EmailVerificationToken.objects.filter(used=False)
print(f"Unused verification tokens: {unused_tokens.count()}")

# 6. Verify password reset tokens
from apps.core.models import PasswordResetToken
unused_resets = PasswordResetToken.objects.filter(used=False)
print(f"Unused reset tokens: {unused_resets.count()}")

# 7. Verify backup codes
from apps.core.models import BackupCode
unused_backups = BackupCode.objects.filter(used=False)
print(f"Unused backup codes: {unused_backups.count()}")

# 8. Verify token hashing (check one example)
token = PasswordResetToken.objects.latest('created_at')
print(f"Token hash length: {len(token.token_hash)}")  # Should be 64 (SHA-256)

# 9. Verify IP encryption (check one example)
from apps.core.utils.encryption import IPEncryption
log = AuditLog.objects.filter(ip_address__isnull=False).first()
if log:
    print(f"Encrypted IP type: {type(log.ip_address)}")  # Should be bytes
    decrypted = IPEncryption.decrypt_ip(log.ip_address)
    print(f"Decrypted IP: {decrypted}")

# 10. Verify TOTP encryption (check one example)
device = TOTPDevice.objects.first()
if device:
    print(f"Encrypted secret type: {type(device.encrypted_secret)}")  # Should be bytes
    print(f"Encrypted secret length: {len(device.encrypted_secret)}")

exit()
```

---

## Email Testing with Mailpit

Access Mailpit at `http://localhost:8025`

**Verification Checklist:**

- [ ] Emails appear in inbox within 5 seconds
- [ ] Email subject lines clear and descriptive
- [ ] Email content includes user's name
- [ ] Links properly formatted and clickable
- [ ] HTML and plain text versions exist
- [ ] Sender address correct (`noreply@backendtemplate.com`)
- [ ] Expiry times mentioned (24h verification, 15m reset)
- [ ] Email headers include Message-ID and Date
- [ ] No sensitive data in email body
- [ ] Organisation branding applied (if configured)

**Test Email Types:**

1. **Registration Verification Email**
   - Subject: "Verify Your Email Address"
   - Contains: First name, verification link, 24h expiry
   - Link format: `http://localhost:8000/verify-email/TOKEN`

2. **Password Reset Email**
   - Subject: "Password Reset Request"
   - Contains: First name, reset link, 15m expiry
   - Link format: `http://localhost:8000/reset-password/TOKEN`

3. **2FA Enabled Notification**
   - Subject: "Two-Factor Authentication Enabled"
   - Contains: First name, timestamp, IP address
   - Security notice about account change

4. **Security Alert Email**
   - Subject: "Security Alert: Account Activity"
   - Contains: Action taken, timestamp, IP, device info
   - Sent for: Login from new device, password change, 2FA disabled

---

## Security Verification Checklist

Verify all security requirements are met:

**Critical Requirements (C):**

- [ ] **C1:** Session tokens hashed with HMAC-SHA256
- [ ] **C2:** TOTP secrets encrypted with Fernet
- [ ] **C3:** Password reset tokens hashed (not plain text in DB)
- [ ] **C4:** CSRF protection active for GraphQL mutations
- [ ] **C5:** Email verification enforced before login
- [ ] **C6:** IP addresses encrypted in database

**High Priority Requirements (H):**

- [ ] **H1:** JWT token families implemented
- [ ] **H2:** DataLoaders used to prevent N+1 queries
- [ ] **H3:** SELECT FOR UPDATE prevents race conditions
- [ ] **H5:** HaveIBeenPwned integration for password validation
- [ ] **H6:** Async email delivery via Celery
- [ ] **H8:** Device fingerprinting implemented
- [ ] **H9:** Refresh token replay detection works
- [ ] **H11:** Password history prevents reuse (last 5)
- [ ] **H12:** Concurrent session limit enforced (max 5)
- [ ] **H13:** Account lockout after failed attempts

**Medium Priority Requirements (M):**

- [ ] **M2:** Email resend cooldown (5 minutes)
- [ ] **M4:** Account recovery via backup codes
- [ ] **M5:** DST-aware timezone handling
- [ ] **M7:** No user enumeration in error messages

---

## Performance Testing Guidelines

**Token Generation:**

- Token generation: < 100ms
- Hash computation: < 50ms
- Token pair creation: < 50ms per pair

**Email Delivery:**

- Verification email: < 5 seconds to Mailpit
- Password reset email: < 5 seconds to Mailpit
- Async task queue: < 1 second response time

**Database Operations:**

- User lookup: < 10ms
- Session token validation: < 20ms
- Audit log insertion: < 30ms

**GraphQL Queries:**

- Simple query (1-2 fields): < 100ms
- Complex query (3-5 fields): < 250ms
- List query (10 items): < 300ms

**Test Commands:**

```bash
# Measure token generation time
./scripts/env/dev.sh shell
>>> import time
>>> from apps.core.services.token_service import TokenService
>>> from apps.core.models import User
>>> user = User.objects.first()
>>> start = time.time()
>>> for _ in range(100):
...     TokenService.create_tokens(user)
>>> elapsed = time.time() - start
>>> print(f"Average: {elapsed/100*1000:.2f}ms per token pair")
>>> exit()
```

---

## Regression Testing Checklist

After making changes, verify these still work:

**Authentication:**

- [ ] User registration with valid data
- [ ] User login with verified email
- [ ] Password reset via email
- [ ] Email verification workflow
- [ ] 2FA setup and login challenge
- [ ] Session token refresh
- [ ] Logout and session revocation

**Security:**

- [ ] Token hashing (HMAC-SHA256)
- [ ] TOTP secret encryption (Fernet)
- [ ] Password reset token hashing
- [ ] CSRF protection for mutations
- [ ] Email verification enforcement
- [ ] IP address encryption
- [ ] Refresh token replay detection
- [ ] Account lockout mechanism

**GraphQL:**

- [ ] Organisation boundary enforcement
- [ ] Query depth limiting
- [ ] Query complexity limiting
- [ ] Introspection control
- [ ] Permission classes (IsAuthenticated, IsOrganisationOwner)

**Database:**

- [ ] User model creation
- [ ] Password hashing (Argon2id)
- [ ] Organisation relationships
- [ ] Audit logging
- [ ] Session token management

**Email:**

- [ ] Async email delivery (Celery)
- [ ] Email templates rendered correctly
- [ ] Email resend cooldown
- [ ] Mailpit integration

---

## Known Issues and Limitations

**Current Limitations:**

1. **DataLoaders (H2):**
   - Not fully implemented
   - May cause N+1 queries in nested GraphQL queries
   - Workaround: Use select_related and prefetch_related

2. **Device Fingerprinting (H8):**
   - Basic implementation only
   - Does not detect all device changes
   - Enhancement: Add canvas fingerprinting, WebGL detection

3. **Rate Limiting:**
   - IP-based only
   - Can be bypassed with VPN/proxy
   - Enhancement: Add account-based rate limiting

4. **Email Delivery:**
   - Depends on Celery worker running
   - Failed emails go to dead letter queue
   - Manual intervention needed for failed deliveries

5. **CSRF Protection:**
   - Cookie-based CSRF tokens
   - May conflict with stateless JWT authentication
   - Enhancement: Consider double-submit cookie pattern

**Known Bugs:**

- None at this time

**Future Enhancements:**

- WebAuthn support for passwordless login
- Social authentication (OAuth2)
- SMS-based 2FA
- Push notification-based 2FA
- Biometric authentication

---

## Sign-Off

**Testing Phase:** Manual Testing
**Document Version:** 1.0 (Consolidated)
**Testing Status:** Ready for execution

| Role                  | Name | Date | Status | Notes |
| --------------------- | ---- | ---- | ------ | ----- |
| **Test Writer Agent** |      |      |        |       |
| **QA Tester**         |      |      |        |       |
| **Security Reviewer** |      |      |        |       |
| **Product Owner**     |      |      |        |       |
| **Tech Lead**         |      |      |        |       |

**Approval for Production:**

- [ ] All critical tests passed
- [ ] All high priority tests passed
- [ ] Security requirements verified
- [ ] Performance benchmarks met
- [ ] No blocking issues found
- [ ] Approved by security team
- [ ] Approved by product owner

**Issues Found:** [Count to be filled during testing]

**Blockers:** [List to be filled during testing]

---

**Document Status:** ✅ Complete
**Last Updated:** 19/01/2026
**Maintained By:** Test Writer Agent
**Next Review:** After each sprint
