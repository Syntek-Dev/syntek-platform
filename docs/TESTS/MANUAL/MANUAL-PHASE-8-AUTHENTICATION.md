# Manual Testing Guide: Phase 8 Authentication Testing

**Last Updated:** 17/01/2026
**Author:** Test Writer Agent
**User Story:** US-001 Phase 8
**Status:** Ready for Manual Testing

---

## Table of Contents

- [Manual Testing Guide: Phase 8 Authentication Testing](#manual-testing-guide-phase-8-authentication-testing)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Test Environment Setup](#test-environment-setup)
  - [Test Scenarios](#test-scenarios)
    - [Scenario 1: Complete Registration to 2FA Workflow (Happy Path)](#scenario-1-complete-registration-to-2fa-workflow-happy-path)
    - [Scenario 2: Password Reset with Token Hashing (Critical Fix C3)](#scenario-2-password-reset-with-token-hashing-critical-fix-c3)
    - [Scenario 3: Session Token Replay Detection (High Priority H9)](#scenario-3-session-token-replay-detection-high-priority-h9)
    - [Scenario 4: Email Verification Enforcement (Critical Fix C5)](#scenario-4-email-verification-enforcement-critical-fix-c5)
    - [Scenario 5: CSRF Protection for GraphQL (Critical Fix C4)](#scenario-5-csrf-protection-for-graphql-critical-fix-c4)
    - [Scenario 6: Concurrent Session Limit (High Priority H12)](#scenario-6-concurrent-session-limit-high-priority-h12)
    - [Scenario 7: Unicode Support in User Names (Edge Case #3)](#scenario-7-unicode-support-in-user-names-edge-case-3)
    - [Scenario 8: SQL Injection Prevention (Edge Case #5)](#scenario-8-sql-injection-prevention-edge-case-5)
    - [Scenario 9: XSS Prevention in User Fields (Edge Case #6)](#scenario-9-xss-prevention-in-user-fields-edge-case-6)
    - [Scenario 10: Rate Limiting Effectiveness (Edge Case #15)](#scenario-10-rate-limiting-effectiveness-edge-case-15)
  - [API Testing](#api-testing)
    - [GraphQL Endpoint: Registration](#graphql-endpoint-registration)
    - [GraphQL Endpoint: Login](#graphql-endpoint-login)
    - [GraphQL Endpoint: Password Reset](#graphql-endpoint-password-reset)
    - [GraphQL Endpoint: 2FA Setup](#graphql-endpoint-2fa-setup)
  - [Database Verification](#database-verification)
  - [Security Verification Checklist](#security-verification-checklist)
  - [Edge Case Verification](#edge-case-verification)
  - [Regression Checklist](#regression-checklist)
  - [Known Issues](#known-issues)
  - [Sign-Off](#sign-off)

---

## Prerequisites

Before beginning manual testing, ensure:

- [ ] Development environment is running (`./scripts/env/dev.sh start`)
- [ ] Database migrations are applied (`./scripts/env/dev.sh migrate`)
- [ ] Test database is clean (or reset with `./scripts/env/dev.sh reset`)
- [ ] GraphQL playground is accessible at `http://localhost:8000/graphql`
- [ ] Mailpit is running at `http://localhost:8025` for email verification
- [ ] You have a TOTP authenticator app (Google Authenticator, Authy, etc.)
- [ ] You have a REST client (Postman, Insomnia, or cURL)

---

## Test Environment Setup

```bash
# 1. Start development environment
./scripts/env/dev.sh start

# 2. Verify services are running
./scripts/env/dev.sh health

# 3. Check GraphQL endpoint
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { queryType { name } } }"}'

# 4. Access Mailpit (for email verification)
# Open browser: http://localhost:8025

# 5. Access GraphQL Playground
# Open browser: http://localhost:8000/graphql
```

---

## Test Scenarios

### Scenario 1: Complete Registration to 2FA Workflow (Happy Path)

**Purpose:** Verify the entire user journey from registration to 2FA setup

**Steps:**

1. **Navigate to GraphQL Playground**
   - URL: `http://localhost:8000/graphql`

2. **Register a New User**

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
         emailVerified
       }
     }
   }
   ```

3. **Verify Email Sent**
   - Open Mailpit: `http://localhost:8025`
   - Confirm email to `testuser@example.com` exists
   - Extract verification token from email

4. **Verify Email Address**

   ```graphql
   mutation {
     verifyEmail(token: "TOKEN_FROM_EMAIL") {
       success
       message
     }
   }
   ```

5. **Login with Verified Account**

   ```graphql
   mutation {
     login(input: { email: "testuser@example.com", password: "SecureP@ssw0rd!2024" }) {
       token
       user {
         id
         email
         hasTwoFactor
       }
     }
   }
   ```

   - **Save the token** for next steps

6. **Enable 2FA**

   ```graphql
   mutation {
     enable2FA {
       secret
       qrCodeUrl
       backupCodes
     }
   }
   ```

   - Use Authorization header: `Bearer <token_from_step_5>`
   - Scan QR code with authenticator app
   - **Save backup codes** securely

7. **Verify 2FA with TOTP Code**

   ```graphql
   mutation {
     verify2FA(code: "123456") {
       success
       message
     }
   }
   ```

   - Use 6-digit code from authenticator app

8. **Logout**

   ```graphql
   mutation {
     logout {
       success
     }
   }
   ```

9. **Login with 2FA Challenge**

   ```graphql
   mutation {
     login(input: { email: "testuser@example.com", password: "SecureP@ssw0rd!2024" }) {
       requiresTwoFactor
       token
     }
   }
   ```

   - Should return `requiresTwoFactor: true`
   - Token should be `null`

10. **Complete Login with TOTP**
    ```graphql
    mutation {
      verifyLogin2FA(code: "123456") {
        token
        user {
          email
        }
      }
    }
    ```

**Expected Result:**

- User successfully registers
- Email verification works
- Login succeeds
- 2FA setup completes
- Login with 2FA challenge works
- User has fully secured account

**Pass Criteria:** All steps complete without errors

---

### Scenario 2: Password Reset with Token Hashing (Critical Fix C3)

**Purpose:** Verify password reset tokens are hashed with HMAC-SHA256

**Steps:**

1. **Request Password Reset**

   ```graphql
   mutation {
     requestPasswordReset(email: "testuser@example.com") {
       success
       message
     }
   }
   ```

2. **Check Mailpit for Reset Email**
   - URL: `http://localhost:8025`
   - Verify reset email sent
   - Extract reset token from email

3. **Verify Token is Hashed in Database**

   ```bash
   # Connect to database
   ./scripts/env/dev.sh shell

   # In Django shell:
   from apps.core.models import PasswordResetToken
   token = PasswordResetToken.objects.latest('created_at')
   print(f"Token hash length: {len(token.token_hash)}")
   print(f"Token hash: {token.token_hash}")
   # Should be 64 characters (SHA-256 hex)
   # Should NOT match the plain token from email
   ```

4. **Reset Password with Plain Token**

   ```graphql
   mutation {
     resetPassword(token: "TOKEN_FROM_EMAIL", newPassword: "NewSecureP@ss2024!") {
       success
       message
     }
   }
   ```

5. **Verify Old Password No Longer Works**

   ```graphql
   mutation {
     login(input: { email: "testuser@example.com", password: "SecureP@ssw0rd!2024" }) {
       token
     }
   }
   ```

   - Should return error

6. **Verify New Password Works**

   ```graphql
   mutation {
     login(input: { email: "testuser@example.com", password: "NewSecureP@ss2024!" }) {
       token
     }
   }
   ```

   - Should succeed

7. **Verify Token Cannot Be Reused**
   ```graphql
   mutation {
     resetPassword(token: "SAME_TOKEN_AS_STEP_4", newPassword: "AnotherP@ss123!") {
       success
     }
   }
   ```

   - Should return error "Token already used"

**Expected Result:**

- Password reset token is hashed in database
- Plain token from email works for reset
- Old password no longer works
- New password works
- Token cannot be reused

**Pass Criteria:** Token hashing verified, password reset works, token reuse blocked

---

### Scenario 3: Session Token Replay Detection (High Priority H9)

**Purpose:** Verify refresh token replay attacks are detected

**Steps:**

1. **Login from Device 1**

   ```graphql
   mutation {
     login(input: { email: "testuser@example.com", password: "SecureP@ssw0rd!2024" }) {
       accessToken
       refreshToken
       tokenFamily
     }
   }
   ```

   - **Save refreshToken as TOKEN_1**

2. **Refresh Token (Device 1)**

   ```graphql
   mutation {
     refreshToken(refreshToken: "TOKEN_1") {
       accessToken
       refreshToken
       tokenFamily
       tokenGeneration
     }
   }
   ```

   - **Save new refreshToken as TOKEN_2**
   - Note tokenGeneration should be 2

3. **Attempt to Replay Old Token (Attack)**

   ```graphql
   mutation {
     refreshToken(refreshToken: "TOKEN_1") {
       accessToken
     }
   }
   ```

   - Should return error "Token revoked" or "Replay detected"

4. **Verify Entire Token Family Invalidated**

   ```graphql
   mutation {
     refreshToken(refreshToken: "TOKEN_2") {
       accessToken
     }
   }
   ```

   - Should also fail (family invalidated)

5. **Verify Security Event Logged**

   ```bash
   ./scripts/env/dev.sh shell

   # In Django shell:
   from apps.core.models import AuditLog
   event = AuditLog.objects.filter(action="token_replay_detected").latest('created_at')
   print(event.metadata)
   ```

**Expected Result:**

- Token refresh works
- Replaying old token fails
- Entire token family is invalidated
- Security event is logged

**Pass Criteria:** Replay detection works, family invalidation occurs

---

### Scenario 4: Email Verification Enforcement (Critical Fix C5)

**Purpose:** Verify unverified users cannot access protected resources

**Steps:**

1. **Register User Without Verifying Email**

   ```graphql
   mutation {
     register(
       input: {
         email: "unverified@example.com"
         password: "TestP@ss123!"
         firstName: "Unverified"
         lastName: "User"
         organisationSlug: "test-org"
       }
     ) {
       user {
         id
         emailVerified
       }
     }
   }
   ```

   - Note: `emailVerified` should be `false`

2. **Attempt Login Before Verification**

   ```graphql
   mutation {
     login(input: { email: "unverified@example.com", password: "TestP@ss123!" }) {
       token
     }
   }
   ```

   - Should return error "Please verify your email address"

3. **Verify Email**
   - Get token from Mailpit
   - Use `verifyEmail` mutation

4. **Attempt Login After Verification**
   ```graphql
   mutation {
     login(input: { email: "unverified@example.com", password: "TestP@ss123!" }) {
       token
     }
   }
   ```

   - Should now succeed

**Expected Result:**

- Unverified users cannot login
- After verification, login succeeds

**Pass Criteria:** Email verification is enforced

---

### Scenario 5: CSRF Protection for GraphQL (Critical Fix C4)

**Purpose:** Verify CSRF protection is enabled for GraphQL mutations

**Steps:**

1. **Attempt Mutation Without CSRF Token**

   ```bash
   curl -X POST http://localhost:8000/graphql/ \
     -H "Content-Type: application/json" \
     -d '{"query": "mutation { login(input: {email: \"test@example.com\", password: \"pass\"}) { token } }"}'
   ```

   - Should return CSRF error (403 Forbidden)

2. **Get CSRF Token**

   ```bash
   curl -X GET http://localhost:8000/csrf-token/
   ```

3. **Attempt Mutation With CSRF Token**
   ```bash
   curl -X POST http://localhost:8000/graphql/ \
     -H "Content-Type: application/json" \
     -H "X-CSRFToken: TOKEN_FROM_STEP_2" \
     -d '{"query": "mutation { login(input: {email: \"test@example.com\", password: \"pass\"}) { token } }"}'
   ```

   - Should succeed (or return authentication error, not CSRF error)

**Expected Result:**

- Mutations without CSRF token are rejected
- Mutations with CSRF token are allowed

**Pass Criteria:** CSRF protection is active

---

### Scenario 6: Concurrent Session Limit (High Priority H12)

**Purpose:** Verify users cannot exceed concurrent session limit

**Steps:**

1. **Login from 5 Different Devices**
   - Use different User-Agent headers
   - Save each access token

2. **Verify 5 Active Sessions**

   ```bash
   ./scripts/env/dev.sh shell

   # In Django shell:
   from apps.core.models import SessionToken, User
   user = User.objects.get(email="testuser@example.com")
   active_sessions = SessionToken.objects.filter(user=user, revoked=False).count()
   print(f"Active sessions: {active_sessions}")
   # Should be 5
   ```

3. **Login from 6th Device**

   ```graphql
   mutation {
     login(input: { email: "testuser@example.com", password: "SecureP@ssw0rd!2024" }) {
       token
       sessionCount
       oldestSessionRevoked
     }
   }
   ```

4. **Verify Oldest Session Revoked**
   - Check `oldestSessionRevoked: true`
   - Verify still only 5 active sessions in database

5. **Verify First Token No Longer Works**
   - Use token from step 1 (first device)
   - Should return "Session revoked" error

**Expected Result:**

- Maximum 5 concurrent sessions enforced
- Oldest session automatically revoked when limit exceeded

**Pass Criteria:** Session limit enforcement works

---

### Scenario 7: Unicode Support in User Names (Edge Case #3)

**Purpose:** Verify Unicode characters are supported in names

**Steps:**

1. **Register with Unicode Names**

   ```graphql
   mutation {
     register(
       input: {
         email: "unicode@example.com"
         password: "TestP@ss123!"
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

2. **Verify Names Stored Correctly**
   - Check response shows "José" and "Müller"

3. **Test Other Unicode Characters**
   - Chinese: 李 明
   - Arabic: محمد أحمد
   - Cyrillic: Владимир Петров

**Expected Result:**

- All Unicode characters stored and retrieved correctly

**Pass Criteria:** Unicode support works for all tested scripts

---

### Scenario 8: SQL Injection Prevention (Edge Case #5)

**Purpose:** Verify SQL injection attempts are prevented

**Steps:**

1. **Attempt SQL Injection in Email**

   ```graphql
   mutation {
     register(
       input: {
         email: "admin@example.com'; DROP TABLE users;--"
         password: "TestP@ss123!"
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

   - Should return validation error
   - Database should be unchanged

2. **Verify Database Intact**

   ```bash
   ./scripts/env/dev.sh shell

   # In Django shell:
   from apps.core.models import User
   user_count = User.objects.count()
   print(f"User count: {user_count}")
   # Should be unchanged
   ```

**Expected Result:**

- SQL injection attempt fails
- Database remains intact

**Pass Criteria:** SQL injection prevented

---

### Scenario 9: XSS Prevention in User Fields (Edge Case #6)

**Purpose:** Verify XSS payloads are escaped

**Steps:**

1. **Register with XSS Payload**

   ```graphql
   mutation {
     register(
       input: {
         email: "xss@example.com"
         password: "TestP@ss123!"
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

2. **Verify Output is Escaped**
   - Response should show escaped HTML
   - No script execution should occur

**Expected Result:**

- XSS payload is escaped
- No script execution

**Pass Criteria:** XSS prevention works

---

### Scenario 10: Rate Limiting Effectiveness (Edge Case #15)

**Purpose:** Verify rate limiting prevents abuse

**Steps:**

1. **Make 5 Login Attempts (Within Limit)**

   ```bash
   for i in {1..5}; do
     curl -X POST http://localhost:8000/graphql/ \
       -H "Content-Type: application/json" \
       -d '{"query": "mutation { login(input: {email: \"test@example.com\", password: \"wrong\"}) { token } }"}'
   done
   ```

2. **Make 6th Attempt (Exceeds Limit)**
   ```bash
   curl -X POST http://localhost:8000/graphql/ \
     -H "Content-Type: application/json" \
     -d '{"query": "mutation { login(input: {email: \"test@example.com\", password: \"wrong\"}) { token } }"}'
   ```

   - Should return rate limit error

**Expected Result:**

- First 5 attempts allowed
- 6th attempt blocked

**Pass Criteria:** Rate limiting works

---

## API Testing

### GraphQL Endpoint: Registration

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation Register($input: RegisterInput!) { register(input: $input) { user { id email } } }",
    "variables": {
      "input": {
        "email": "api@example.com",
        "password": "SecureP@ss123!",
        "firstName": "API",
        "lastName": "Test",
        "organisationSlug": "test-org"
      }
    }
  }'
```

**Expected Response:**

```json
{
  "data": {
    "register": {
      "user": {
        "id": "UUID",
        "email": "api@example.com"
      }
    }
  }
}
```

---

### GraphQL Endpoint: Login

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation Login($input: LoginInput!) { login(input: $input) { token user { email } } }",
    "variables": {
      "input": {
        "email": "api@example.com",
        "password": "SecureP@ss123!"
      }
    }
  }'
```

**Expected Response:**

```json
{
  "data": {
    "login": {
      "token": "JWT_TOKEN_HERE",
      "user": {
        "email": "api@example.com"
      }
    }
  }
}
```

---

### GraphQL Endpoint: Password Reset

```bash
# Step 1: Request reset
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { requestPasswordReset(email: \"api@example.com\") { success message } }"
  }'

# Step 2: Reset with token (get from email)
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { resetPassword(token: \"TOKEN_HERE\", newPassword: \"NewP@ss123!\") { success } }"
  }'
```

---

### GraphQL Endpoint: 2FA Setup

```bash
# Step 1: Enable 2FA (requires authentication)
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "query": "mutation { enable2FA { secret qrCodeUrl backupCodes } }"
  }'

# Step 2: Verify 2FA
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "query": "mutation { verify2FA(code: \"123456\") { success } }"
  }'
```

---

## Database Verification

Check database state after testing:

```bash
./scripts/env/dev.sh shell
```

```python
# In Django shell:

# Verify users created
from apps.core.models import User
users = User.objects.all()
for user in users:
    print(f"{user.email} - Verified: {user.email_verified}")

# Verify session tokens
from apps.core.models import SessionToken
sessions = SessionToken.objects.filter(revoked=False)
print(f"Active sessions: {sessions.count()}")

# Verify TOTP devices
from apps.core.models import TOTPDevice
totp_devices = TOTPDevice.objects.filter(confirmed=True)
print(f"Confirmed 2FA devices: {totp_devices.count()}")

# Verify audit logs
from apps.core.models import AuditLog
recent_logs = AuditLog.objects.order_by('-created_at')[:10]
for log in recent_logs:
    print(f"{log.action} - {log.created_at}")
```

---

## Security Verification Checklist

- [ ] Session tokens hashed with HMAC-SHA256 (C1)
- [ ] TOTP secrets encrypted with Fernet (C2)
- [ ] Password reset tokens hashed (C3)
- [ ] CSRF protection active for mutations (C4)
- [ ] Email verification enforced (C5)
- [ ] IP encryption key rotation works (C6)
- [ ] Token replay detection works (H9)
- [ ] Concurrent session limit enforced (H12)
- [ ] Rate limiting effective (H13)

---

## Edge Case Verification

- [ ] Empty email/password validation (Edge Case #1)
- [ ] Email normalisation (spaces, lowercase) (Edge Case #2)
- [ ] Unicode names supported (Edge Case #3)
- [ ] Very long passwords rejected (>128 chars) (Edge Case #4)
- [ ] SQL injection prevented (Edge Case #5)
- [ ] XSS prevention works (Edge Case #6)
- [ ] CSRF protection active (Edge Case #7)
- [ ] Concurrent sessions handled (Edge Case #8)
- [ ] Token collisions prevented (Edge Case #9)
- [ ] Expired tokens rejected (Edge Case #10)

---

## Regression Checklist

After testing new features, verify these still work:

- [ ] Basic registration still works
- [ ] Basic login still works
- [ ] Password validation still enforced
- [ ] Email sending still works
- [ ] Audit logging still active
- [ ] Organisation boundaries still enforced

---

## Known Issues

Document any known issues discovered during manual testing:

1. **Issue**: [Description]
   - **Severity**: [High/Medium/Low]
   - **Workaround**: [If available]
   - **Fix Required**: [Yes/No]

---

## Sign-Off

| Tester | Date | Status | Notes |
| ------ | ---- | ------ | ----- |
|        |      |        |       |
|        |      |        |       |

**Testing Complete**: [ ] Yes [ ] No

**Issues Found**: [Count]

**Blockers**: [List any blocking issues]

**Approval for Production**: [ ] Approved [ ] Not Approved [ ] Conditional

---

**Last Updated:** 2026-01-17
