# Debug Report: US-001 User Authentication

**Date:** 08/01/2026
**Version:** 1.0.0
**Status:** CRITICAL ISSUES IDENTIFIED
**Branch:** us001/user-authentication
**Debugger:** Claude Opus 4.5 (Debug Agent)
**Phase 1 Status**: ✅ Completed

---

## Table of Contents

- [Debug Report: US-001 User Authentication](#debug-report-us-001-user-authentication)
  - [Table of Contents](#table-of-contents)
  - [Executive Summary](#executive-summary)
  - [Implementation Status](#implementation-status)
    - [Phase 1: Core Models and Database](#phase-1-core-models-and-database)
    - [Phase 2: Authentication Service Layer](#phase-2-authentication-service-layer)
    - [Phase 3: GraphQL API Implementation](#phase-3-graphql-api-implementation)
    - [Phase 4: Two-Factor Authentication (2FA)](#phase-4-two-factor-authentication-2fa)
    - [Phase 5: Password Reset and Email Verification](#phase-5-password-reset-and-email-verification)
    - [Phase 6: Audit Logging and Security](#phase-6-audit-logging-and-security)
    - [Phase 7: Testing and Documentation](#phase-7-testing-and-documentation)
  - [Critical Security Issues](#critical-security-issues)
    - [C1: Token Hashing Uses Wrong Key](#c1-token-hashing-uses-wrong-key)
    - [C2: TOTP Encryption Key Not Configured](#c2-totp-encryption-key-not-configured)
    - [C3: Password Reset Token Security Incomplete](#c3-password-reset-token-security-incomplete)
    - [C4: GraphQL CSRF Middleware Not Implemented](#c4-graphql-csrf-middleware-not-implemented)
    - [C5: Email Verification Not Enforced](#c5-email-verification-not-enforced)
    - [C6: IP Encryption Key Rotation Not Implemented](#c6-ip-encryption-key-rotation-not-implemented)
  - [High Priority Issues](#high-priority-issues)
  - [Model Implementation Analysis](#model-implementation-analysis)
    - [User Model](#user-model)
    - [BaseToken Abstract Model](#basetoken-abstract-model)
    - [SessionToken Model](#sessiontoken-model)
    - [TOTPDevice Model](#totpdevice-model)
    - [AuditLog Model](#auditlog-model)
    - [PasswordHistory Model](#passwordhistory-model)
  - [Missing Service Layer](#missing-service-layer)
  - [Migration Analysis](#migration-analysis)
  - [Test Coverage Analysis](#test-coverage-analysis)
  - [Configuration Issues](#configuration-issues)
  - [Data Flow Analysis](#data-flow-analysis)
    - [Registration Flow](#registration-flow)
    - [Login Flow](#login-flow)
    - [Password Reset Flow](#password-reset-flow)
    - [Email Verification Flow](#email-verification-flow)
  - [Root Cause Hypotheses](#root-cause-hypotheses)
  - [Prioritised Recommendations](#prioritised-recommendations)
    - [Critical (Blocking Deployment)](#critical-blocking-deployment)
    - [High (Must Fix Before Production)](#high-must-fix-before-production)
    - [Medium (Should Fix)](#medium-should-fix)
  - [Next Steps](#next-steps)
  - [Appendix A: File Reference](#appendix-a-file-reference)
  - [Appendix B: Environment Variable Checklist](#appendix-b-environment-variable-checklist)

---

## Executive Summary

The US-001 User Authentication implementation is **approximately 35% complete**. Phase 1 (Core Models and Database) is largely implemented with models, migrations, and basic unit tests in place. However, the implementation has **6 critical security vulnerabilities** that must be resolved before deployment, and **the entire service layer (Phases 2-5) is missing**.

**Key Findings:**

| Category      | Status        | Details                                    |
| ------------- | ------------- | ------------------------------------------ |
| Models        | 90% Complete  | All 10 models implemented, minor issues    |
| Migrations    | 100% Complete | 5 migrations successfully created          |
| Service Layer | 0% Complete   | No AuthService, TokenService, EmailService |
| GraphQL API   | 10% Complete  | Schema shell only, no auth mutations       |
| Security      | CRITICAL      | 6 critical vulnerabilities identified      |
| Tests         | 40% Complete  | Unit tests for models, no integration/E2E  |

**Overall Assessment:** The project requires significant work before production readiness. The model layer is solid, but the absence of the service layer means no actual authentication functionality exists.

---

## Implementation Status

### Phase 1: Core Models and Database

| Component                    | Status   | Notes                                       |
| ---------------------------- | -------- | ------------------------------------------- |
| User Model                   | COMPLETE | All fields implemented, proper FK handling  |
| Organisation Model           | COMPLETE | UUID PK, slug validation                    |
| UserProfile Model            | COMPLETE | OneToOne relationship                       |
| TOTPDevice Model             | COMPLETE | Fernet encryption methods                   |
| AuditLog Model               | COMPLETE | ActionType choices, proper indexes          |
| SessionToken Model           | COMPLETE | Inherits BaseToken, adds revocation         |
| PasswordResetToken Model     | COMPLETE | Inherits BaseToken                          |
| EmailVerificationToken Model | COMPLETE | Inherits BaseToken                          |
| PasswordHistory Model        | COMPLETE | Password reuse prevention                   |
| BaseToken Abstract Model     | COMPLETE | HMAC-SHA256 hashing implemented             |
| Migrations                   | COMPLETE | 5 migrations created and applied            |
| Indexes                      | PARTIAL  | Missing composite multi-tenant indexes (H1) |

### Phase 2: Authentication Service Layer

| Component            | Status          | Notes                                        |
| -------------------- | --------------- | -------------------------------------------- |
| AuthService          | NOT IMPLEMENTED | Login, logout, registration missing          |
| TokenService         | NOT IMPLEMENTED | JWT creation, validation missing             |
| PasswordResetService | NOT IMPLEMENTED | Password reset flow missing                  |
| EmailService         | NOT IMPLEMENTED | Email sending missing                        |
| TokenHasher Utility  | NOT IMPLEMENTED | Uses SECRET_KEY instead of TOKEN_SIGNING_KEY |
| Account Lockout      | NOT IMPLEMENTED | Mechanism not built                          |
| Rate Limiting        | PARTIAL         | Middleware exists but not wired to auth      |

### Phase 3: GraphQL API Implementation

| Component             | Status          | Notes                                    |
| --------------------- | --------------- | ---------------------------------------- |
| Schema Definition     | MINIMAL         | Only hello/placeholder queries           |
| Auth Mutations        | NOT IMPLEMENTED | register, login, logout missing          |
| User Queries          | NOT IMPLEMENTED | me, users queries missing                |
| Error Handling        | NOT IMPLEMENTED | No AuthenticationError class             |
| Permission Decorators | NOT IMPLEMENTED | No @login_required, @permission_required |
| DataLoaders           | NOT IMPLEMENTED | N+1 prevention not implemented (H6)      |

### Phase 4: Two-Factor Authentication (2FA)

| Component          | Status          | Notes                         |
| ------------------ | --------------- | ----------------------------- |
| TOTPDevice Model   | COMPLETE        | Encryption methods work       |
| TOTP Setup Flow    | NOT IMPLEMENTED | No mutation to enable 2FA     |
| TOTP Verification  | PARTIAL         | verify_token() method exists  |
| Backup Codes       | NOT IMPLEMENTED | Model and logic missing       |
| QR Code Generation | PARTIAL         | generate_qr_code_uri() exists |

### Phase 5: Password Reset and Email Verification

| Component               | Status          | Notes             |
| ----------------------- | --------------- | ----------------- |
| Token Models            | COMPLETE        | Models exist      |
| Reset Request Flow      | NOT IMPLEMENTED | No service layer  |
| Reset Completion Flow   | NOT IMPLEMENTED | No service layer  |
| Email Verification Flow | NOT IMPLEMENTED | No service layer  |
| Email Templates         | NOT IMPLEMENTED | Templates missing |

### Phase 6: Audit Logging and Security

| Component             | Status          | Notes                                          |
| --------------------- | --------------- | ---------------------------------------------- |
| AuditLog Model        | COMPLETE        | ActionType choices defined                     |
| Audit Service         | NOT IMPLEMENTED | No audit_log() function                        |
| IP Encryption         | PARTIAL         | BinaryField exists, encryption utility missing |
| Device Fingerprinting | PARTIAL         | Field exists, generation missing               |
| Security Headers      | COMPLETE        | Middleware implemented                         |
| Rate Limiting         | COMPLETE        | Middleware implemented                         |
| IP Allowlist          | COMPLETE        | Middleware implemented                         |

### Phase 7: Testing and Documentation

| Component         | Status | Notes                              |
| ----------------- | ------ | ---------------------------------- |
| Unit Tests        | 40%    | Model tests complete               |
| Integration Tests | 0%     | None implemented                   |
| E2E Tests         | 0%     | None implemented                   |
| BDD Tests         | 0%     | Feature files missing              |
| Security Tests    | 0%     | CSRF, XSS, injection tests missing |
| Documentation     | 80%    | Plan and reviews thorough          |

---

## Critical Security Issues

### C1: Token Hashing Uses Wrong Key

**Severity:** CRITICAL
**Status:** NOT FIXED
**Location:** `apps/core/models/base_token.py:66-79`

**Problem:**
The `BaseToken.hash_token()` method uses `settings.SECRET_KEY` instead of a dedicated `TOKEN_SIGNING_KEY`:

```python
@classmethod
def hash_token(cls, token: str) -> str:
    """Generate HMAC-SHA256 hash of token for secure storage."""
    key = settings.SECRET_KEY.encode()  # WRONG: Should be TOKEN_SIGNING_KEY
    return hmac.new(key, token.encode(), hashlib.sha256).hexdigest()
```

**Impact:**

- If `SECRET_KEY` is compromised, all tokens can be forged
- Violates principle of key separation
- Plan explicitly requires `TOKEN_SIGNING_KEY` (line 366 of plan)

**Fix Required:**

1. Add `TOKEN_SIGNING_KEY` to all `.env.*.example` files
2. Update `base_token.py` to use `settings.TOKEN_SIGNING_KEY`
3. Add startup validation to fail if key not set in production

---

### C2: TOTP Encryption Key Not Configured

**Severity:** CRITICAL
**Status:** PARTIALLY IMPLEMENTED
**Location:** `apps/core/models/totp_device.py:67-85`

**Problem:**
The `TOTPDevice._get_cipher()` method correctly requires `TOTP_ENCRYPTION_KEY`, but:

1. The key is not defined in `.env.dev.example` (line 55-56 shows empty value)
2. No startup validation ensures the key is set
3. Tests mock Fernet without testing actual encryption

**Impact:**

- Application will crash on first TOTP operation if key not set
- No validation means silent failures possible
- 2FA secrets could be stored incorrectly

**Fix Required:**

1. Generate and set `TOTP_ENCRYPTION_KEY` in all environment files
2. Add startup validation in `apps.core.apps.CoreConfig.ready()`
3. Add integration tests for actual encryption/decryption

---

### C3: Password Reset Token Security Incomplete

**Severity:** CRITICAL
**Status:** MODEL COMPLETE, SERVICE MISSING
**Location:** `apps/core/models/password_reset_token.py`

**Problem:**
The `PasswordResetToken` model inherits secure hashing from `BaseToken`, but:

1. `PasswordResetService` does not exist
2. No flow to create, send, or validate reset tokens
3. Token hashing still uses `SECRET_KEY` (see C1)

**Impact:**

- Password reset functionality does not work
- Even when implemented, will have C1 vulnerability

**Fix Required:**

1. Fix C1 first (TOKEN_SIGNING_KEY)
2. Implement `apps/core/services/password_reset_service.py`
3. Implement email sending with token URL
4. Add expiration and single-use validation

---

### C4: GraphQL CSRF Middleware Not Implemented

**Severity:** CRITICAL
**Status:** NOT IMPLEMENTED
**Location:** Missing `apps/core/middleware/graphql_csrf.py`

**Problem:**
The plan specifies `GraphQLCSRFMiddleware` (lines 738-861), but:

1. File does not exist
2. Middleware not added to settings
3. GraphQL mutations are vulnerable to CSRF attacks

**Current Middleware Stack (from `config/settings/base.py:50-65`):**

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    # GraphQLCSRFMiddleware is MISSING here
    ...
]
```

**Impact:**

- All GraphQL mutations vulnerable to CSRF
- Attackers can perform actions on behalf of authenticated users

**Fix Required:**

1. Create `apps/core/middleware/graphql_csrf.py` per plan specification
2. Add to MIDDLEWARE after `CsrfViewMiddleware`
3. Update frontend to include CSRF token in mutation headers

---

### C5: Email Verification Not Enforced

**Severity:** CRITICAL
**Status:** NOT IMPLEMENTED
**Location:** Missing `AuthService.login()`

**Problem:**
The plan requires blocking login for unverified users (lines 903-1023), but:

1. `AuthService` does not exist
2. No login mutation exists
3. `email_verified` field exists but is never checked

**Impact:**

- Unverified users can access full functionality
- Spam/bot accounts can be created without verification
- Violates email verification requirement

**Fix Required:**

1. Implement `AuthService.login()` with email verification check
2. Auto-resend verification email on unverified login attempt
3. Return `EMAIL_NOT_VERIFIED` error code

---

### C6: IP Encryption Key Rotation Not Implemented

**Severity:** CRITICAL
**Status:** NOT IMPLEMENTED
**Location:** Missing management command

**Problem:**
The plan specifies IP key rotation (lines 1026-1181), but:

1. `rotate_ip_encryption_key` management command does not exist
2. No key rotation procedure documented
3. `IP_ENCRYPTION_KEY` is empty in example files

**Impact:**

- If encryption key is compromised, all historical IPs are exposed
- No way to rotate keys without manual database updates
- Quarterly rotation schedule cannot be followed

**Fix Required:**

1. Implement `apps/core/management/commands/rotate_ip_encryption_key.py`
2. Document key rotation procedure
3. Set up automated rotation reminders

---

## High Priority Issues

| #   | Issue                                              | Location                    | Status                 |
| --- | -------------------------------------------------- | --------------------------- | ---------------------- |
| H1  | Missing composite indexes for multi-tenant queries | User model                  | NOT FIXED              |
| H2  | Missing `expires_at` indexes on token models       | BaseToken                   | NOT FIXED              |
| H3  | AuditLog CASCADE issue                             | Fixed in model              | FIXED                  |
| H4  | User.organisation nullable                         | Fixed in model              | FIXED                  |
| H5  | Row-Level Security not implemented                 | PostgreSQL                  | NOT STARTED            |
| H6  | N+1 query prevention (DataLoaders)                 | api/dataloaders.py          | NOT IMPLEMENTED        |
| H7  | Race conditions in user creation                   | UserManager                 | NOT ADDRESSED          |
| H8  | Token revocation on password change                | TokenService                | NOT IMPLEMENTED        |
| H9  | Refresh token replay detection                     | SessionToken                | PARTIAL (field exists) |
| H10 | HaveIBeenPwned password checking                   | Password validators         | CONFIGURED             |
| H11 | JWT algorithm and key rotation                     | Not applicable (no JWT yet) | NOT STARTED            |
| H12 | Concurrent session limit                           | SessionToken                | NOT IMPLEMENTED        |
| H13 | Account lockout mechanism                          | AuthService                 | NOT IMPLEMENTED        |

---

## Model Implementation Analysis

### User Model

**File:** `apps/core/models/user.py`
**Status:** COMPLETE with minor issues

**Implemented:**

- UUID primary key
- Email-based authentication (USERNAME_FIELD = "email")
- Organisation FK with SET_NULL (H4 fixed)
- email_verified, email_verified_at fields
- two_factor_enabled flag
- last_login_ip as BinaryField (for encryption)
- password_changed_at tracking
- Custom UserManager with email normalisation

**Issues Found:**

1. **Line 244-247:** `save()` method lowercases entire email, but RFC 5321 specifies only domain should be lowercase:

   ```python
   if self.email:
       self.email = self.email.lower()  # Should preserve local part case
   ```

2. **Missing:** Composite indexes for multi-tenant queries (H1)
   ```python
   # Current indexes (lines 231-234):
   indexes = [
       models.Index(fields=["email"]),
       models.Index(fields=["organisation"]),
   ]
   # Missing: ["organisation", "email"], ["organisation", "is_active"]
   ```

### BaseToken Abstract Model

**File:** `apps/core/models/base_token.py`
**Status:** COMPLETE with C1 vulnerability

**Implemented:**

- UUID primary key
- HMAC-SHA256 hashing (but wrong key - C1)
- token_family for replay detection (H9)
- used/used_at for single-use tokens
- is_expired(), is_valid(), mark_used() methods
- Automatic token generation on save

**Issues Found:**

1. **Line 78:** Uses `settings.SECRET_KEY` instead of `TOKEN_SIGNING_KEY`
2. **Missing:** `expires_at` index (H2)

### SessionToken Model

**File:** `apps/core/models/session_token.py`
**Status:** COMPLETE

**Implemented:**

- Inherits from BaseToken
- token_hash and refresh_token_hash fields
- ip_address as BinaryField
- device_fingerprint field
- is_refresh_token_used for rotation
- revoke() and is_valid() methods
- Proper indexes including token_family

**No issues found** in model itself.

### TOTPDevice Model

**File:** `apps/core/models/totp_device.py`
**Status:** COMPLETE

**Implemented:**

- Fernet encryption via \_get_cipher()
- set_secret() encrypts plain secret
- get_secret() decrypts stored secret
- verify_token() with pyotp
- generate_qr_code_uri() for setup

**No issues found** in model, but C2 (key configuration) affects functionality.

### AuditLog Model

**File:** `apps/core/models/audit_log.py`
**Status:** COMPLETE

**Implemented:**

- ActionType choices for all auth events
- user FK with SET_NULL (preserves logs)
- organisation FK with SET_NULL (H3 fixed)
- ip_address as BinaryField
- device_fingerprint field
- Proper indexes on user, organisation, action, created_at

**No issues found.**

### PasswordHistory Model

**File:** `apps/core/models/password_history.py`
**Status:** COMPLETE

**Implemented:**

- check_password() method using Django's hasher
- check_password_reuse() class method for H11
- record_password() with cleanup (keeps 24 entries)
- Proper indexes

**No issues found.**

---

## Missing Service Layer

The following services are specified in the plan but **do not exist**:

| Service              | Expected Location                              | Purpose                     |
| -------------------- | ---------------------------------------------- | --------------------------- |
| AuthService          | `apps/core/services/auth_service.py`           | Login, logout, registration |
| TokenService         | `apps/core/services/token_service.py`          | JWT/token management        |
| PasswordResetService | `apps/core/services/password_reset_service.py` | Password reset flow         |
| EmailService         | `apps/core/services/email_service.py`          | Email sending               |
| AuditService         | `apps/core/services/audit_service.py`          | Audit logging               |
| TwoFactorService     | `apps/core/services/two_factor_service.py`     | 2FA management              |

**Currently Implemented:**

- `apps/core/services/permission_service.py` - Permission checking (COMPLETE)

**Current services `__init__.py`:**

```python
"""Service layer for core application."""
# Empty - no services exported
```

---

## Migration Analysis

**Migrations Status:** All 5 migrations created and valid

| Migration                  | Description                      | Status  |
| -------------------------- | -------------------------------- | ------- |
| 0001_initial               | All models created               | APPLIED |
| 0002*alter*\*              | SessionToken, TOTPDevice options | APPLIED |
| 0003_create_default_groups | Default permission groups        | APPLIED |
| 0004*alter*\*              | Organisation, User options       | APPLIED |
| 0005*remove*\*             | Index optimisation               | APPLIED |

**Issues Found:**

1. **0001_initial - Line 139:** Uses `is_used` field name, but model uses `used`:

   ```python
   ("is_used", models.BooleanField(default=False)),
   ```

   Model has backwards compatibility property, but this inconsistency could cause confusion.

2. **Missing indexes:**
   - No `expires_at` index on token models (H2)
   - No composite indexes for multi-tenant queries (H1)

3. **Table name inconsistency:**
   - EmailVerificationToken: `core_email_verification_token`
   - PasswordResetToken: `core_password_reset_token`
   - SessionToken in migration: `core_session_token`
   - SessionToken in model Meta: `session_tokens`

   The model Meta `db_table` values don't match migration (model was updated after migration).

---

## Test Coverage Analysis

**Test Files Found:** 15 test files

| Category            | Files | Status      |
| ------------------- | ----- | ----------- |
| Unit Tests (Models) | 10    | COMPLETE    |
| Factories           | 2     | COMPLETE    |
| BDD Step Defs       | 1     | INCOMPLETE  |
| Integration         | 0     | NOT STARTED |
| E2E                 | 0     | NOT STARTED |
| GraphQL             | 0     | NOT STARTED |
| Security            | 0     | NOT STARTED |

**Coverage by Model:**

| Model                  | Test File                              | Tests     |
| ---------------------- | -------------------------------------- | --------- |
| User                   | test_user_model.py                     | 30+ tests |
| UserManager            | test_user_manager.py                   | Tests     |
| Organisation           | test_organisation_model.py             | Tests     |
| BaseToken              | test_base_token_model.py               | 15+ tests |
| SessionToken           | test_session_token_model.py            | Tests     |
| PasswordResetToken     | test_password_reset_token_model.py     | Tests     |
| EmailVerificationToken | test_email_verification_token_model.py | Tests     |
| TOTPDevice             | test_totp_device_model.py              | 20+ tests |
| AuditLog               | test_audit_log_model.py                | Tests     |
| PasswordHistory        | test_password_history_model.py         | Tests     |

**Missing Test Coverage:**

1. **Service Layer Tests** - Cannot test what doesn't exist
2. **GraphQL Mutation Tests** - No mutations implemented
3. **Integration Tests:**
   - Registration flow
   - Login flow (with/without 2FA)
   - Password reset flow
   - Email verification flow
4. **Security Tests:**
   - CSRF protection (C4)
   - Rate limiting
   - Token security
   - SQL injection prevention
5. **BDD Feature Files** - No `.feature` files found

---

## Configuration Issues

**File:** `config/settings/base.py`

| Setting                      | Status      | Issue                         |
| ---------------------------- | ----------- | ----------------------------- |
| AUTH_USER_MODEL              | OK          | Set to "core.User"            |
| PASSWORD_HASHERS             | OK          | Argon2 as primary             |
| AUTH_PASSWORD_VALIDATORS     | OK          | Includes HIBP (H10)           |
| TOTP_ENCRYPTION_KEY          | MISSING     | Empty default, not validated  |
| IP_ENCRYPTION_KEY            | MISSING     | Empty default, not validated  |
| TOKEN_SIGNING_KEY            | NOT DEFINED | Key doesn't exist in settings |
| SESSION_COOKIE_HTTPONLY      | OK          | True                          |
| SESSION_COOKIE_SAMESITE      | OK          | "Lax"                         |
| CSRF_COOKIE_HTTPONLY         | OK          | True                          |
| GRAPHQL_MAX_QUERY_DEPTH      | OK          | 10                            |
| GRAPHQL_MAX_QUERY_COMPLEXITY | OK          | 1000                          |

**Environment Files (.env.dev.example):**

| Variable               | Status                |
| ---------------------- | --------------------- |
| TOTP_ENCRYPTION_KEY    | Empty (line 55)       |
| IP_ENCRYPTION_KEY      | Empty (line 56)       |
| TOKEN_SIGNING_KEY      | NOT PRESENT           |
| DJANGO_SETTINGS_MODULE | OK                    |
| SECRET_KEY             | Instructions provided |
| DATABASE_URL           | OK                    |
| REDIS_URL              | OK                    |

---

## Data Flow Analysis

### Registration Flow

**Expected Flow (from plan):**

1. User submits email, password, organisation
2. Validate email format and uniqueness
3. Validate password against validators
4. Create User with email_verified=False
5. Create EmailVerificationToken
6. Send verification email
7. Return success response

**Current State:** NOT IMPLEMENTED

- No registration mutation
- No EmailService to send verification
- Token models exist but unused

### Login Flow

**Expected Flow (from plan):**

1. User submits email, password
2. Check account lockout status
3. Validate credentials
4. Check email_verified (C5)
5. Check 2FA requirement
6. Create SessionToken
7. Create AuditLog entry
8. Return tokens

**Current State:** NOT IMPLEMENTED

- No login mutation
- No AuthService
- No account lockout logic
- email_verified never checked

### Password Reset Flow

**Expected Flow (from plan):**

1. User requests reset for email
2. Find user (don't reveal if exists)
3. Create PasswordResetToken
4. Send reset email with token
5. User clicks link, submits new password
6. Validate token (not expired, not used)
7. Hash and compare token
8. Update password
9. Mark token as used
10. Revoke all sessions

**Current State:** NOT IMPLEMENTED

- Token model exists
- No PasswordResetService
- No email sending
- No validation logic

### Email Verification Flow

**Expected Flow (from plan):**

1. Token created on registration
2. Email sent with verification link
3. User clicks link
4. Validate token
5. Set email_verified=True
6. Set email_verified_at
7. Mark token as used

**Current State:** NOT IMPLEMENTED

- Token model exists
- No verification logic
- No email sending

---

## Root Cause Hypotheses

### Why is the service layer missing?

**Hypothesis 1: TDD Red Phase**
The project appears to be in the "Red" phase of TDD where tests are written but implementation is pending. Evidence:

- Test files contain "RED phase of TDD" comments
- Models are implemented (needed for tests to run)
- Services are not implemented (tests would pass trivially)

**Hypothesis 2: Phased Implementation**
The plan has 7 phases, and only Phase 1 was intended for this sprint. Evidence:

- All Phase 1 components complete
- Phase 2+ components missing
- Plan structure suggests sequential implementation

**Hypothesis 3: Development Pause**
Development may have paused after model layer. Evidence:

- Last meaningful commit was model/test work
- Documentation is extensive (suggesting planning phase complete)
- Implementation stopped at a logical boundary

### Why are critical security issues present?

**Root Cause: Documentation-Implementation Gap**
The plan was updated with security review findings (C1-C6), but these were not back-ported to the existing implementation:

- `BaseToken` was created before TOKEN_SIGNING_KEY requirement
- CSRF middleware was planned but never created
- Key configuration was documented but not enforced

---

## Prioritised Recommendations

### Critical (Blocking Deployment)

1. **C1: Implement TOKEN_SIGNING_KEY**
   - Priority: 1 (HIGHEST)
   - Effort: 2 hours
   - Files: `base_token.py`, `base.py`, all `.env.*.example`

2. **C4: Implement GraphQLCSRFMiddleware**
   - Priority: 2
   - Effort: 4 hours
   - Files: `apps/core/middleware/graphql_csrf.py`, `base.py`

3. **Implement AuthService**
   - Priority: 3
   - Effort: 16 hours
   - Files: `apps/core/services/auth_service.py`
   - Blocks: Login, registration, email verification (C5)

4. **Implement TokenService**
   - Priority: 4
   - Effort: 8 hours
   - Files: `apps/core/services/token_service.py`

5. **C2/C6: Configure encryption keys**
   - Priority: 5
   - Effort: 4 hours
   - Files: All environment files, `apps.py` validation

### High (Must Fix Before Production)

6. **Implement GraphQL Auth Mutations**
   - Priority: 6
   - Effort: 12 hours
   - Files: `api/mutations/auth.py`, `api/schema.py`

7. **Add composite indexes (H1)**
   - Priority: 7
   - Effort: 2 hours
   - Files: New migration

8. **Implement PasswordResetService**
   - Priority: 8
   - Effort: 8 hours
   - Files: `apps/core/services/password_reset_service.py`

9. **Implement EmailService**
   - Priority: 9
   - Effort: 4 hours
   - Files: `apps/core/services/email_service.py`

10. **Add security tests (H14-15)**
    - Priority: 10
    - Effort: 8 hours
    - Files: `tests/security/`

### Medium (Should Fix)

11. **Implement DataLoaders (H6)**
12. **Add integration tests**
13. **Implement IP encryption utilities**
14. **Create BDD feature files**
15. **Fix email normalisation (RFC 5321)**

---

## Next Steps

1. **Immediate Actions (Today):**
   - Run `/syntek-dev-suite:security` to implement C1 and C4
   - Add TOKEN_SIGNING_KEY to environment files

2. **This Sprint:**
   - Implement AuthService (login, registration)
   - Implement TokenService
   - Add GraphQL auth mutations

3. **Next Sprint:**
   - Implement password reset flow
   - Implement email verification flow
   - Add integration tests

4. **Before Production:**
   - Complete all security tests
   - Implement rate limiting for auth
   - Set up key rotation procedures
   - Conduct security audit

---

## Appendix A: File Reference

| File                                       | Lines | Purpose                     |
| ------------------------------------------ | ----- | --------------------------- |
| `apps/core/models/user.py`                 | 256   | User model                  |
| `apps/core/models/base_token.py`           | 134   | Abstract token model        |
| `apps/core/models/session_token.py`        | 108   | Session token model         |
| `apps/core/models/totp_device.py`          | 163   | TOTP device model           |
| `apps/core/models/audit_log.py`            | 83    | Audit log model             |
| `apps/core/models/password_history.py`     | 118   | Password history model      |
| `apps/core/services/permission_service.py` | 407   | Permission service          |
| `apps/core/utils/signed_urls.py`           | 353   | Signed URL utility          |
| `config/settings/base.py`                  | 252   | Base settings               |
| `api/schema.py`                            | 67    | GraphQL schema              |
| `api/security.py`                          | 319   | GraphQL security extensions |

---

## Appendix B: Environment Variable Checklist

| Variable                     | Required For       | Default     | Production |
| ---------------------------- | ------------------ | ----------- | ---------- |
| SECRET_KEY                   | Django             | insecure    | REQUIRED   |
| TOKEN_SIGNING_KEY            | Token hashing (C1) | NOT DEFINED | REQUIRED   |
| TOTP_ENCRYPTION_KEY          | 2FA secrets (C2)   | Empty       | REQUIRED   |
| IP_ENCRYPTION_KEY            | IP encryption      | Empty       | REQUIRED   |
| DATABASE_URL                 | PostgreSQL         | sqlite      | REQUIRED   |
| REDIS_URL                    | Caching/sessions   | localhost   | REQUIRED   |
| EMAIL_HOST                   | Email sending      | mailpit     | REQUIRED   |
| GRAPHQL_ENABLE_INTROSPECTION | Schema exposure    | True        | False      |

---

**Report Generated:** 08/01/2026
**Debug Agent:** Claude Opus 4.5
**Handoff:** Run `/syntek-dev-suite:backend` to implement missing service layer
