# Manual Testing Guide: Phase 6 - Email Verification and Password Reset

**Last Updated:** 17/01/2026
**Author:** Test Writer Agent
**Phase:** 6 - Email Verification and Password Reset
**Security Requirements:** C3, H6, H11, H12, M2, M4

---

## Table of Contents

- [Manual Testing Guide: Phase 6 - Email Verification and Password Reset](#manual-testing-guide-phase-6---email-verification-and-password-reset)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Test Environment Setup](#test-environment-setup)
  - [Test Scenarios](#test-scenarios)
    - [Scenario 1: Email Verification - Happy Path](#scenario-1-email-verification---happy-path)
    - [Scenario 2: Email Verification - Token Expiry](#scenario-2-email-verification---token-expiry)
    - [Scenario 3: Email Verification - Single-Use Token (H12)](#scenario-3-email-verification---single-use-token-h12)
    - [Scenario 4: Email Verification - Resend Cooldown (M2)](#scenario-4-email-verification---resend-cooldown-m2)
    - [Scenario 5: Password Reset - Happy Path](#scenario-5-password-reset---happy-path)
    - [Scenario 6: Password Reset - Token Hash Verification (C3)](#scenario-6-password-reset---token-hash-verification-c3)
    - [Scenario 7: Password Reset - Password History (H11)](#scenario-7-password-reset---password-history-h11)
    - [Scenario 8: Password Reset - Session Revocation](#scenario-8-password-reset---session-revocation)
    - [Scenario 9: Async Email Delivery (H6)](#scenario-9-async-email-delivery-h6)
    - [Scenario 10: Account Recovery with Backup Codes (M4)](#scenario-10-account-recovery-with-backup-codes-m4)
  - [Email Testing (Mailpit)](#email-testing-mailpit)
  - [Database Verification](#database-verification)
  - [Security Checks](#security-checks)
  - [Performance Testing](#performance-testing)
  - [Regression Checklist](#regression-checklist)
  - [Known Issues](#known-issues)
  - [Sign-Off](#sign-off)

---

## Prerequisites

- [ ] Docker containers running (`./scripts/env/dev.sh start`)
- [ ] Database migrated (`./scripts/env/dev.sh migrate`)
- [ ] Mailpit accessible at `http://localhost:8025`
- [ ] Celery worker running (for async email tests)
- [ ] Test organisation created in database
- [ ] Test user accounts available

## Test Environment Setup

```bash
# Start development environment
./scripts/env/dev.sh start

# Run database migrations
./scripts/env/dev.sh migrate

# Create test organisation
./scripts/env/dev.sh shell
>>> from apps.core.models import Organisation
>>> org = Organisation.objects.create(name="Test Org", slug="test-org")
>>> exit()

# Start Celery worker (in separate terminal)
./scripts/env/dev.sh celery

# Access Mailpit for email testing
# Open browser to: http://localhost:8025
```

---

## Test Scenarios

### Scenario 1: Email Verification - Happy Path

**Purpose:** Verify basic email verification workflow works as expected

**Steps:**

1. Register a new user via GraphQL mutation:

   ```graphql
   mutation {
     register(
       input: {
         email: "newuser@example.com"
         password: "SecurePass123!@"
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

2. Open Mailpit at `http://localhost:8025`

3. Verify email received for "newuser@example.com"

4. Check email contains:
   - User's first name ("Test")
   - Verification link with token
   - 24-hour expiry notice
   - Sender address matches `DEFAULT_FROM_EMAIL`

5. Extract verification token from email URL

6. Submit verification via GraphQL mutation:

   ```graphql
   mutation {
     verifyEmail(token: "EXTRACTED_TOKEN_HERE") {
       success
       user {
         email
         emailVerified
       }
     }
   }
   ```

**Expected Result:**

- Registration succeeds with `emailVerified: false`
- Email delivered to Mailpit within 5 seconds
- Email contains correct user information and link
- Verification mutation returns `success: true`
- User's `emailVerified` field is now `true`
- Token is marked as `used` in database

**Pass Criteria:** All steps complete without errors, email is verified

---

### Scenario 2: Email Verification - Token Expiry

**Purpose:** Verify expired verification tokens are rejected

**Steps:**

1. Create a user with email verification token

2. Access database and manually expire the token:

   ```bash
   ./scripts/env/dev.sh shell
   >>> from apps.core.models import User, EmailVerificationToken
   >>> from django.utils import timezone
   >>> from datetime import timedelta
   >>> user = User.objects.get(email="expired@example.com")
   >>> token = EmailVerificationToken.objects.filter(user=user).first()
   >>> token.expires_at = timezone.now() - timedelta(hours=1)
   >>> token.save()
   >>> exit()
   ```

3. Attempt to verify email with the expired token:

   ```graphql
   mutation {
     verifyEmail(token: "EXPIRED_TOKEN_HERE") {
       success
       error
     }
   }
   ```

**Expected Result:**

- Mutation returns `success: false`
- Error message: "Verification token has expired"
- User's `emailVerified` remains `false`

**Pass Criteria:** Expired tokens are rejected with appropriate error

---

### Scenario 3: Email Verification - Single-Use Token (H12)

**Purpose:** Verify tokens cannot be reused after verification

**Steps:**

1. Create user and verify email successfully (follow Scenario 1)

2. Attempt to use the same verification token again:

   ```graphql
   mutation {
     verifyEmail(token: "ALREADY_USED_TOKEN") {
       success
       error
     }
   }
   ```

3. Check database to verify token is marked as used:

   ```bash
   ./scripts/env/dev.sh shell
   >>> from apps.core.models import EmailVerificationToken
   >>> token = EmailVerificationToken.objects.filter(token_hash="...").first()
   >>> print(token.used, token.used_at)
   True 2026-01-17 12:34:56+00:00
   ```

**Expected Result:**

- Second verification fails with `success: false`
- Error message: "Token has already been used"
- Token record shows `used=True` and `used_at` timestamp

**Pass Criteria:** Used tokens cannot be reused (H12 requirement)

---

### Scenario 4: Email Verification - Resend Cooldown (M2)

**Purpose:** Verify 5-minute cooldown on verification email resend

**Steps:**

1. Create user and send verification email:

   ```graphql
   mutation {
     resendVerificationEmail(email: "cooldown@example.com") {
       success
       message
     }
   }
   ```

2. Immediately request resend again (within 5 minutes):

   ```graphql
   mutation {
     resendVerificationEmail(email: "cooldown@example.com") {
       success
       error
     }
   }
   ```

3. Wait 5 minutes and request again:

   ```graphql
   mutation {
     resendVerificationEmail(email: "cooldown@example.com") {
       success
     }
   }
   ```

**Expected Result:**

- First send succeeds
- Second send (within 5 min) fails with error: "Please wait 5 minutes before requesting a new email"
- Third send (after 5 min) succeeds with new token

**Pass Criteria:** 5-minute cooldown enforced (M2 requirement)

---

### Scenario 5: Password Reset - Happy Path

**Purpose:** Verify basic password reset workflow

**Steps:**

1. Create user with known password:

   ```bash
   ./scripts/env/dev.sh shell
   >>> from apps.core.models import User, Organisation
   >>> org = Organisation.objects.get(slug="test-org")
   >>> user = User.objects.create(email="reset@example.com", organisation=org)
   >>> user.set_password("OldPassword123!@")
   >>> user.save()
   >>> exit()
   ```

2. Request password reset:

   ```graphql
   mutation {
     requestPasswordReset(email: "reset@example.com") {
       success
       message
     }
   }
   ```

3. Check Mailpit for reset email

4. Extract reset token from email URL

5. Reset password with new password:

   ```graphql
   mutation {
     resetPassword(token: "RESET_TOKEN_HERE", newPassword: "NewSecurePass456!@") {
       success
       user {
         email
       }
     }
   }
   ```

6. Attempt to log in with new password:

   ```graphql
   mutation {
     login(email: "reset@example.com", password: "NewSecurePass456!@") {
       user {
         email
       }
       token
     }
   }
   ```

**Expected Result:**

- Reset request succeeds
- Email delivered with reset link
- Password reset succeeds
- Login with new password succeeds
- Login with old password fails

**Pass Criteria:** Complete password reset flow works end-to-end

---

### Scenario 6: Password Reset - Token Hash Verification (C3)

**Purpose:** Verify tokens are hashed before database storage (C3 requirement)

**Steps:**

1. Request password reset for user

2. Before using token, check database:

   ```bash
   ./scripts/env/dev.sh shell
   >>> from apps.core.models import PasswordResetToken
   >>> token = PasswordResetToken.objects.latest('created_at')
   >>> print(f"Token hash: {token.token_hash}")
   >>> print(f"Hash length: {len(token.token_hash)}")
   ```

3. Verify the plain token (from email) does NOT appear in database

4. Verify the hash uses HMAC-SHA256 (64-character hex string)

**Expected Result:**

- Token hash is 64 characters (SHA-256 hex)
- Plain token does not appear anywhere in database
- Hash cannot be reversed to obtain plain token

**Pass Criteria:** Tokens are hashed with HMAC-SHA256 before storage (C3)

---

### Scenario 7: Password Reset - Password History (H11)

**Purpose:** Verify password reset prevents reusing recent passwords

**Steps:**

1. Create user with password history:

   ```bash
   ./scripts/env/dev.sh shell
   >>> from apps.core.models import User, PasswordHistory, Organisation
   >>> from django.contrib.auth.hashers import make_password
   >>> from django.utils import timezone
   >>> from datetime import timedelta
   >>> org = Organisation.objects.get(slug="test-org")
   >>> user = User.objects.create(email="history@example.com", organisation=org)
   >>> user.set_password("CurrentPassword123!@")
   >>> user.save()
   >>> # Create password history
   >>> for i in range(5):
   ...     PasswordHistory.objects.create(
   ...         user=user,
   ...         password_hash=make_password(f"OldPassword{i}!@"),
   ...         created_at=timezone.now() - timedelta(days=i+1)
   ...     )
   >>> exit()
   ```

2. Request password reset

3. Attempt to reset to one of the old passwords:

   ```graphql
   mutation {
     resetPassword(token: "RESET_TOKEN", newPassword: "OldPassword2!@") {
       success
       error
     }
   }
   ```

**Expected Result:**

- Password reset fails
- Error message: "Cannot reuse recent passwords"
- Last 5 passwords are blocked

**Pass Criteria:** Password history enforcement prevents reuse (H11)

---

### Scenario 8: Password Reset - Session Revocation

**Purpose:** Verify all sessions are revoked after password reset

**Steps:**

1. Create user and log in from multiple devices/browsers:

   ```graphql
   mutation {
     login(email: "sessions@example.com", password: "Password123!@") {
       token
       refreshToken
     }
   }
   ```

2. Repeat login mutation 3 times to create 3 active sessions

3. Verify sessions in database:

   ```bash
   ./scripts/env/dev.sh shell
   >>> from apps.core.models import User, SessionToken
   >>> user = User.objects.get(email="sessions@example.com")
   >>> print(SessionToken.objects.filter(user=user, used=False).count())
   3
   ```

4. Reset password via email flow

5. Check sessions are revoked:

   ```bash
   ./scripts/env/dev.sh shell
   >>> from apps.core.models import User, SessionToken
   >>> user = User.objects.get(email="sessions@example.com")
   >>> print(SessionToken.objects.filter(user=user, used=False).count())
   0
   ```

**Expected Result:**

- All 3 sessions are marked as `used=True`
- User must log in again on all devices

**Pass Criteria:** All sessions revoked after password reset

---

### Scenario 9: Async Email Delivery (H6)

**Purpose:** Verify emails are sent asynchronously via Celery

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
     resendVerificationEmail(email: "async@example.com") {
       success
     }
   }
   ```

4. Check Celery logs for task execution:

   ```
   [2026-01-17 12:34:56] Task send_verification_email_task[...] received
   [2026-01-17 12:34:57] Task send_verification_email_task[...] succeeded
   ```

5. Check email delivered in Mailpit

6. Test retry logic by simulating SMTP failure:
   - Stop Mailpit temporarily
   - Request email
   - Observe Celery retry with exponential backoff
   - Restart Mailpit
   - Verify email eventually delivered

**Expected Result:**

- Email task queued in Celery
- Task processed asynchronously
- Mutation returns immediately (non-blocking)
- Failed tasks retry with exponential backoff (1s, 2s, 4s, 8s)
- After 5 retries, task moves to dead letter queue

**Pass Criteria:** Async email delivery with Celery works (H6)

---

### Scenario 10: Account Recovery with Backup Codes (M4)

**Purpose:** Verify account recovery using backup codes

**Steps:**

1. Create user with 2FA enabled and backup codes:

   ```bash
   ./scripts/env/dev.sh shell
   >>> from apps.core.models import User, BackupCode, Organisation
   >>> org = Organisation.objects.get(slug="test-org")
   >>> user = User.objects.create(
   ...     email="recovery@example.com",
   ...     organisation=org,
   ...     two_factor_enabled=True
   ... )
   >>> user.set_password("Password123!@")
   >>> user.save()
   >>> # Generate backup codes
   >>> for i in range(10):
   ...     plain_code = f"{i:04d}-{i:04d}-{i:04d}"
   ...     code_hash = BackupCode.hash_code(plain_code)
   ...     BackupCode.objects.create(user=user, code_hash=code_hash)
   >>> print("Backup code 0: 0000-0000-0000")
   >>> exit()
   ```

2. Simulate user losing email access

3. Request account recovery with backup code:

   ```graphql
   mutation {
     recoverAccountWithBackupCode(email: "recovery@example.com", backupCode: "0000-0000-0000") {
       success
       temporaryToken
     }
   }
   ```

4. Use temporary token to set new email:

   ```graphql
   mutation {
     updateRecoveryEmail(temporaryToken: "TEMP_TOKEN", newEmail: "newemail@example.com") {
       success
     }
   }
   ```

**Expected Result:**

- Recovery with backup code succeeds
- Temporary token granted (15-minute expiry)
- User can update email address
- Backup code is marked as used
- Original email receives notification of recovery attempt

**Pass Criteria:** Account recovery via backup codes works (M4)

---

## Email Testing (Mailpit)

Access Mailpit at `http://localhost:8025`

**Checks:**

- [ ] Emails appear in inbox within 5 seconds
- [ ] Email subject lines are clear and descriptive
- [ ] Email content includes user's name
- [ ] Links are properly formatted and clickable
- [ ] HTML and plain text versions exist
- [ ] Sender address is correct (`noreply@backendtemplate.com`)
- [ ] Expiry times are mentioned (24h for verification, 15m for reset)

---

## Database Verification

**Token Hash Verification (C3):**

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import PasswordResetToken
>>> token = PasswordResetToken.objects.latest('created_at')
>>> print(f"Hash length: {len(token.token_hash)}")
64
>>> print(token.token_hash)
a7f3e2b1c9d8... (64-character hex)
```

**Token Usage Verification (H12):**

```bash
>>> from apps.core.models import EmailVerificationToken
>>> token = EmailVerificationToken.objects.latest('created_at')
>>> print(f"Used: {token.used}, Used At: {token.used_at}")
Used: True, Used At: 2026-01-17 12:34:56+00:00
```

---

## Security Checks

- [ ] **C3:** Tokens are hashed (HMAC-SHA256) before database storage
- [ ] **H6:** Emails sent asynchronously via Celery with retry logic
- [ ] **H11:** Password history prevents reuse of last 5 passwords
- [ ] **H12:** Tokens can only be used once (single-use enforcement)
- [ ] **M2:** Verification email resend has 5-minute cooldown
- [ ] **M4:** Account recovery via backup codes works

---

## Performance Testing

**Email Delivery Timing:**

- Verification email: < 5 seconds to Mailpit
- Password reset email: < 5 seconds to Mailpit
- Async task queue: < 1 second response time

**Token Generation:**

- Token generation: < 100ms
- Hash computation: < 50ms

---

## Regression Checklist

After making changes, verify these still work:

- [ ] User registration with email verification
- [ ] User login after email verification
- [ ] Password reset via email
- [ ] 2FA login (from Phase 5)
- [ ] Session token refresh (from Phase 4)
- [ ] Audit logging for email-related actions
- [ ] Rate limiting on email requests

---

## Known Issues

- None at this time

---

## Sign-Off

| Tester | Date | Status | Notes |
| ------ | ---- | ------ | ----- |
|        |      |        |       |
