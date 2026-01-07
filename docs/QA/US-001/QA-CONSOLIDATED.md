# QA Review: User Authentication System (US-001)

**Date**: 07/01/2026
**Analyst**: QA Tester Agent
**Plan Version**: 1.1.0
**Status**: CRITICAL ISSUES IDENTIFIED
**Localisation**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [Executive Summary](#executive-summary)
- [Critical Findings Overview](#critical-findings-overview)
- [Security Vulnerabilities (Blocking Deployment)](#security-vulnerabilities-blocking-deployment)
  - [1. Session Token Storage Vulnerability](#1-session-token-storage-vulnerability)
  - [2. TOTP Secret Storage Security](#2-totp-secret-storage-security)
  - [3. Password Reset Token Not Hashed](#3-password-reset-token-not-hashed)
  - [4. Missing CSRF Protection](#4-missing-csrf-protection)
  - [5. Email Verification Bypass](#5-email-verification-bypass)
  - [6. IP Encryption Key Rotation Not Specified](#6-ip-encryption-key-rotation-not-specified)
- [Edge Cases and Design Gaps](#edge-cases-and-design-gaps)
  - [1. User Registration Edge Cases](#1-user-registration-edge-cases)
  - [2. Organisation Edge Cases](#2-organisation-edge-cases)
  - [3. Token Edge Cases](#3-token-edge-cases)
  - [4. Password Edge Cases](#4-password-edge-cases)
  - [5. Time Boundaries and Timezone Issues](#5-time-boundaries-and-timezone-issues)
- [Error Handling and Validation](#error-handling-and-validation)
  - [Database Error Handling](#database-error-handling)
  - [GraphQL Error Handling](#graphql-error-handling)
  - [Validation Error Standards](#validation-error-standards)
  - [Service Layer Error Handling](#service-layer-error-handling)
- [Race Conditions and Concurrency](#race-conditions-and-concurrency)
  - [User Creation Race Conditions](#user-creation-race-conditions)
  - [Token Generation Race Conditions](#token-generation-race-conditions)
  - [Session Token Race Conditions](#session-token-race-conditions)
  - [Database Transaction Issues](#database-transaction-issues)
  - [Redis Concurrency](#redis-concurrency)
  - [Session Management Concurrency](#session-management-concurrency)
- [Boundary Conditions](#boundary-conditions)
  - [String Length Boundaries](#string-length-boundaries)
  - [Numeric Boundaries](#numeric-boundaries)
  - [Collection Size Boundaries](#collection-size-boundaries)
- [Invalid Input and Security Testing](#invalid-input-and-security-testing)
  - [Malicious Input Scenarios](#malicious-input-scenarios)
  - [Unicode and Encoding Issues](#unicode-and-encoding-issues)
  - [GraphQL Input Validation](#graphql-input-validation)
- [Token and Session Management Issues](#token-and-session-management-issues)
  - [Token Expiration Edge Cases](#token-expiration-edge-cases)
  - [Token Revocation](#token-revocation)
  - [Refresh Token Critical Issues](#refresh-token-critical-issues)
- [Two-Factor Authentication Gaps](#two-factor-authentication-gaps)
  - [TOTP Device Loss and Recovery](#totp-device-loss-and-recovery)
  - [Backup Codes Implementation](#backup-codes-implementation)
  - [2FA Bypass Attempts](#2fa-bypass-attempts)
- [Email and Communication Issues](#email-and-communication-issues)
  - [SMTP Failure Handling](#smtp-failure-handling)
  - [Email Validation](#email-validation)
  - [Email Bombing Prevention](#email-bombing-prevention)
- [High Priority Implementation Gaps](#high-priority-implementation-gaps)
  - [N+1 Query Risk](#n1-query-risk)
  - [Missing Token Revocation on Password Change](#missing-token-revocation-on-password-change)
  - [Organisation Boundary Enforcement](#organisation-boundary-enforcement)
  - [Rate Limiting Implementation](#rate-limiting-implementation)
  - [Audit Log Performance](#audit-log-performance)
  - [Session Timeout Configuration](#session-timeout-configuration)
  - [2FA Backup Codes](#2fa-backup-codes)
  - [GraphQL Query Depth Limiting](#graphql-query-depth-limiting)
- [Medium Priority Issues](#medium-priority-issues)
  - [Email Service Failure Handling](#email-service-failure-handling)
  - [Timezone Handling](#timezone-handling)
  - [User Enumeration](#user-enumeration)
  - [Account Lockout](#account-lockout)
  - [Password History](#password-history)
  - [User Agent Validation](#user-agent-validation)
  - [Error Message Standards](#error-message-standards)
  - [Concurrent Session Limits](#concurrent-session-limits)
- [Low Priority Issues](#low-priority-issues)
- [Test Scenarios That Must Be Added](#test-scenarios-that-must-be-added)
- [Security Vulnerabilities Summary](#security-vulnerabilities-summary)
- [Performance Concerns](#performance-concerns)
- [Best Practices Compliance](#best-practices-compliance)
- [GDPR Compliance Analysis](#gdpr-compliance-analysis)
- [User Experience Gaps](#user-experience-gaps)
- [Recommendations](#recommendations)
- [Conclusion](#conclusion)

---

## Executive Summary

After comprehensive hostile analysis of the User Authentication System plan (US-001 v1.1.0), **critical security vulnerabilities and design gaps have been identified that block deployment**.

**Key Statistics:**

- **Critical Issues:** 6 (blocking deployment)
- **High Issues:** 8 (must fix before production)
- **Medium Issues:** 8 (should fix)
- **Low Issues:** 5 (consider fixing)
- **Edge Cases Not Covered:** 27 critical gaps, 34 areas needing attention
- **Overall Assessment**: ⚠️ **NOT READY FOR IMPLEMENTATION**

**Primary Concerns:**

1. **Token Storage Vulnerabilities**: Session tokens, TOTP secrets, and password reset tokens lack proper hashing/encryption specifications
2. **Race Condition Vulnerabilities**: No locking mechanism for user creation, token generation, and session management
3. **Email Verification Bypass**: Users can access the system before email verification
4. **Missing CSRF Protection**: GraphQL mutations vulnerable to cross-site attacks
5. **Inadequate Error Handling**: Database errors, GraphQL errors, and validation errors not comprehensively specified
6. **Email Bombing**: Registration email bombing not prevented (rate limit by IP only, not email)
7. **2FA Bypass Vectors**: Session fixation, TOTP code reuse, disable 2FA without verification
8. **Refresh Token Security**: Token reuse detection missing, rotation not atomic
9. **Time Synchronisation**: Timezone handling, DST transitions, leap seconds not addressed
10. **Concurrency Control**: No transaction isolation levels specified, potential lost update problems

**Recommended Action**: **DO NOT PROCEED** with implementation until all critical issues are resolved.

**Estimated Additional Planning Time**: 2-3 days for revisions

---

## Critical Findings Overview

| Area                     | Rating | Critical Issues | Needs Attention | Total Issues |
| ------------------------ | ------ | --------------- | --------------- | ------------ |
| Security Vulnerabilities | ❌     | 6               | 0               | 6            |
| Edge Cases               | ❌     | 8               | 6               | 14           |
| Error Scenarios          | ❌     | 5               | 3               | 8            |
| Race Conditions          | ❌     | 4               | 2               | 6            |
| Token Management         | ❌     | 4               | 2               | 6            |
| 2FA                      | ❌     | 3               | 2               | 5            |
| Boundary Conditions      | ⚠️     | 2               | 5               | 7            |
| Invalid Input            | ❌     | 4               | 2               | 6            |
| Email                    | ⚠️     | 1               | 3               | 4            |
| Concurrency              | ❌     | 4               | 1               | 5            |
| User Experience          | ⚠️     | 1               | 4               | 5            |
| Implementation Gaps      | ❌     | 8               | 0               | 8            |

---

## Security Vulnerabilities (Blocking Deployment)

### 1. Session Token Storage Vulnerability

**Severity**: CRITICAL
**Location**: `SessionToken` model

**Issue**: The plan stores JWT tokens in the database using `token_hash`, but the hashing mechanism is not specified. If tokens are stored as plain SHA-256 hashes, they remain vulnerable to rainbow table attacks.

**Impact**: An attacker with database access could potentially crack JWT tokens using rainbow tables, leading to session hijacking.

**Reproduction**:

1. Create a user session with JWT token
2. Access database and retrieve `token_hash`
3. Use rainbow table to reverse SHA-256 hash
4. Extract JWT token and hijack session

**Recommendation**:

Use HMAC-SHA256 with secret key instead of plain hashing:

```python
import hmac
from django.conf import settings

def hash_token(token: str) -> str:
    """Hash token using HMAC-SHA256 with secret key."""
    return hmac.new(
        settings.SECRET_KEY.encode(),
        token.encode(),
        'sha256'
    ).hexdigest()
```

**Priority**: CRITICAL - Fix before implementation

---

### 2. TOTP Secret Storage Security

**Severity**: CRITICAL
**Location**: `TOTPDevice` model

**Issue**: The `TOTPDevice` model stores TOTP secrets as encrypted strings, but the encryption method is not specified. The plan mentions encryption but doesn't define key management or encryption algorithm.

**Impact**: If TOTP secrets are compromised, attackers can generate valid 2FA codes indefinitely.

**Reproduction**:

1. User enables 2FA
2. TOTP secret stored in database
3. Attacker gains database access
4. If encryption is weak or key is compromised, attacker extracts TOTP secret
5. Attacker bypasses 2FA

**Recommendation**:

```python
from cryptography.fernet import Fernet
from django.conf import settings

class TOTPDevice(models.Model):
    secret = models.BinaryField()  # Store as binary, not CharField

    def set_secret(self, secret: str) -> None:
        """Encrypt TOTP secret before storage."""
        cipher = Fernet(settings.TOTP_ENCRYPTION_KEY)
        self.secret = cipher.encrypt(secret.encode())

    def get_secret(self) -> str:
        """Decrypt TOTP secret for verification."""
        cipher = Fernet(settings.TOTP_ENCRYPTION_KEY)
        return cipher.decrypt(self.secret).decode()
```

**Additional Requirements**:

- Use separate encryption key for TOTP secrets (not IP encryption key)
- Implement key rotation mechanism
- Store encryption key in secrets manager (not `.env`)

**Priority**: CRITICAL - Fix before Phase 4

---

### 3. Password Reset Token Not Hashed

**Severity**: CRITICAL
**Location**: `PasswordResetToken` model

**Issue**: The `PasswordResetToken` model stores tokens as plain strings. This allows attackers with database access to use tokens directly without cracking.

**Impact**: Database breach exposes all active password reset tokens, allowing attackers to reset user passwords and take over accounts.

**Reproduction**:

1. User requests password reset
2. Token stored in database as plain text
3. Attacker gains read access to database
4. Attacker uses token from database to reset password
5. Account takeover

**Recommendation**:

```python
import secrets
import hashlib

class PasswordResetToken(BaseToken):
    token_hash = models.CharField(max_length=64, unique=True)  # SHA-256 hash

    @staticmethod
    def generate_token() -> tuple[str, str]:
        """Generate token and return (plain_token, hash)."""
        plain_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
        return plain_token, token_hash

    @classmethod
    def verify_token(cls, plain_token: str) -> 'PasswordResetToken':
        """Verify token by comparing hashes."""
        token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
        return cls.objects.get(token_hash=token_hash, used=False)
```

**Priority**: CRITICAL - Fix before Phase 5

---

### 4. Missing CSRF Protection

**Severity**: CRITICAL
**Location**: GraphQL API section

**Issue**: The plan does not mention CSRF (Cross-Site Request Forgery) protection for GraphQL mutations. GraphQL APIs are vulnerable to CSRF attacks if not properly protected.

**Impact**: Attackers can trick authenticated users into executing unwanted mutations (logout, password change, 2FA disable) without their knowledge.

**Reproduction**:

1. User is authenticated and logged in
2. Attacker sends malicious link to user
3. User clicks link, which submits GraphQL mutation
4. Mutation executes with user's authentication token
5. User account compromised (2FA disabled, password changed, etc.)

**Recommendation**:

```python
# config/settings/base.py

GRAPHQL_SETTINGS = {
    'CSRF_PROTECTION': True,
    'CSRF_EXEMPT_MUTATIONS': [],  # No mutations should be exempt
}

# api/middleware/csrf.py

class GraphQLCSRFMiddleware:
    """Validate CSRF tokens for GraphQL mutations."""

    def resolve(self, next, root, info, **kwargs):
        if info.operation.operation == 'mutation':
            csrf_token = info.context.request.META.get('HTTP_X_CSRF_TOKEN')
            if not self._validate_csrf(csrf_token, info.context.request):
                raise PermissionError("CSRF validation failed")
        return next(root, info, **kwargs)
```

**Priority**: CRITICAL - Fix before Phase 3

---

### 5. Email Verification Bypass

**Severity**: CRITICAL
**Location**: Registration flow

**Issue**: The plan allows users to log in and receive authentication tokens before email verification. This violates security best practice and enables spam/bot registrations.

**Impact**:

- Bot/spam accounts can register and access the system
- No way to contact users if email is fake
- Resource exhaustion from fake accounts

**Reproduction**:

1. Register with fake email address
2. Receive authentication token immediately
3. Access protected resources without email verification
4. Create hundreds of fake accounts

**Recommendation**:

```python
# api/mutations/auth.py

@strawberry.mutation
def login(self, info: Info, input: LoginInput) -> AuthPayload:
    """Login with email verification check."""
    user = authenticate(email=input.email, password=input.password)

    if not user:
        raise ValueError("Invalid credentials")

    # CRITICAL: Check email verification before allowing login
    if not user.email_verified:
        raise PermissionError(
            "Please verify your email before logging in. "
            "Check your inbox for verification link."
        )

    # Continue with token generation...
```

**Alternative**: Allow limited access for unverified users but restrict critical actions.

**Priority**: CRITICAL - Fix before Phase 3

---

### 6. IP Encryption Key Rotation Not Specified

**Severity**: CRITICAL
**Location**: Key management section

**Issue**: The plan mentions IP encryption key rotation as "manual rotation quarterly, re-encrypt existing data" but provides no implementation details or mechanism.

**Impact**:

- If key is compromised, all historical IP addresses are exposed
- No automated rotation means key may never be rotated
- Re-encrypting existing data could take hours/days with large audit logs
- Cannot comply with security requirements for key rotation

**Reproduction**:

1. System runs for 2 years without key rotation
2. Encryption key compromised
3. All historical IP addresses in audit logs exposed
4. Cannot decrypt IP addresses for compliance/security investigations

**Recommendation**:

```python
# apps/core/management/commands/rotate_ip_key.py

from django.core.management.base import BaseCommand
from apps.core.models import AuditLog, SessionToken
from apps.core.utils.encryption import IPEncryption

class Command(BaseCommand):
    """Rotate IP encryption key and re-encrypt all data."""

    def handle(self, *args, **options):
        old_key = settings.IP_ENCRYPTION_KEY
        new_key = Fernet.generate_key()

        # Re-encrypt all audit logs
        for log in AuditLog.objects.all().iterator(chunk_size=1000):
            decrypted_ip = IPEncryption.decrypt_ip(log.ip_address, old_key)
            log.ip_address = IPEncryption.encrypt_ip(decrypted_ip, new_key)
            log.save(update_fields=['ip_address'])

        # Re-encrypt session tokens
        for session in SessionToken.objects.all().iterator(chunk_size=1000):
            decrypted_ip = IPEncryption.decrypt_ip(session.ip_address, old_key)
            session.ip_address = IPEncryption.encrypt_ip(decrypted_ip, new_key)
            session.save(update_fields=['ip_address'])

        self.stdout.write(self.style.SUCCESS('Key rotation complete'))
```

**Additional Requirements**:

- Schedule automated key rotation (quarterly)
- Store old keys in secure vault for historical decryption
- Implement blue-green key rotation (support both old and new keys during transition)

**Priority**: CRITICAL - Define before Phase 6

---

## Edge Cases and Design Gaps

### 1. User Registration Edge Cases

**Overall Rating**: ❌ CRITICAL GAP

**Issue**: Plan does not specify behaviour for critical registration edge cases.

#### 1.1 Simultaneous Registration with Same Email

**Risk**: Two requests hit the server at exactly the same time with identical emails. Both pass uniqueness check before either commits, resulting in database integrity error or duplicate users.

**Mitigation Not Specified**: Database unique constraint handling at application level.

**Test Required**:

```python
def test_concurrent_registration_same_email():
    """Test two simultaneous registrations with identical email."""
    # CRITICAL: Must result in only ONE user created
    # One request should succeed, other should fail with 409 Conflict
```

#### 1.2 Organisation Does Not Exist at Registration Time

**Risk**: User submits `organisationSlug` for deleted/inactive organisation. Potential timing attack: organisation deleted between validation and user creation.

**Behaviour Not Defined**: Should registration fail? Create pending user?

#### 1.3 User Registers Twice Simultaneously

**Risk**: First request still processing, second request arrives. Email verification token generation may conflict.

**Not Specified**: Should second request be rejected? Queued?

#### 1.4 Email Verification Token Expires During Registration

**Risk**: Slow network causes registration to take > 24 hours. Token expires before email sent.

#### 1.5 User Account Created But Email Service Fails

**Risk**: User exists in database but never receives verification email.

**Plan Gap**: No compensation transaction specified.

**Result**: Orphaned unverified accounts that block future registration with that email.

---

### 2. Organisation Edge Cases

**Overall Rating**: ❌ CRITICAL GAP

**Issue**: Multi-tenancy edge cases not fully addressed.

#### 2.1 Organisation Deactivated During Active Sessions

**Risk**: `organisation.is_active = False` set during active sessions. Existing tokens still valid.

**Not Specified**: Should tokens be immediately revoked?

#### 2.2 User Transferred Between Organisations

**Risk**: Plan states "one organisation per user" but doesn't prohibit future transfers. What happens to existing sessions? What happens to organisation-scoped data?

**Migration Path Not Defined**

#### 2.3 Organisation Deleted with Active Users

**Risk**: Plan mentions "soft delete, retain 90 days" but no implementation details. Active sessions must be revoked. Audit logs must be preserved.

**Cascade Behaviour Not Specified**

#### 2.4 First User in Organisation Becomes Owner

**Risk**: What if two users register simultaneously? Race condition: both could become owner.

**Locking Mechanism Not Specified**

#### 2.5 Organisation Slug Conflicts

**Risk**: Slug "test-org" deleted (soft delete), new org wants same slug.

**Not Specified**: Should soft-deleted slugs be reserved?

---

### 3. Token Edge Cases

**Overall Rating**: ⚠️ NEEDS ATTENTION

#### 3.1 Token Used Exactly at Expiration Timestamp

**Risk**: Token expires_at = 2026-01-07T12:00:00Z. Request arrives at 2026-01-07T12:00:00.000Z (exact match).

**Behaviour Not Defined**: Is it valid or expired?

**Recommendation**: Use `expires_at < now()` (exclusive), not `expires_at <= now()`

#### 3.2 Multiple Token Verification Attempts in Parallel

**Risk**: User clicks email link multiple times rapidly. Multiple GraphQL requests hit `/verifyEmail` simultaneously.

**Risk**: All mark token as verified/used, creating race condition.

#### 3.3 Token Reuse After Marked as Used

**Risk**: `PasswordResetToken.used = True`. Attacker captures token before it's marked used. Replays token after legitimate use.

**Gap**: No specification of token hash invalidation in Redis cache.

#### 3.4 Clock Skew Between Servers

**Risk**: Database server time ≠ application server time. Token appears expired on one server, valid on another.

**Mitigation Not Specified**

---

### 4. Password Edge Cases

**Overall Rating**: ⚠️ NEEDS ATTENTION

#### 4.1 Password Contains Null Bytes

**Input**: `"SecurePass\x00123!"`

**Risk**: May be truncated at null byte by some systems.

**Validation Not Specified**

#### 4.2 Password is Exactly 128 Characters

**Risk**: Boundary condition: maximum allowed. Some hash algorithms have input limits. Argon2 handling not confirmed.

#### 4.3 Password Contains Only Special Characters

**Input**: `"!@#$%^&*()_+-=[]{}|;:,.<?>"`

**Risk**: Technically meets requirements (if 12+ chars). Allowed or rejected?

#### 4.4 Password History Implementation

**Plan Mentions**: "password history to prevent reuse"

**Not Specified**:

- How many previous passwords stored?
- How are old password hashes stored securely?
- What happens when user tries to reuse?

#### 4.5 Password Change During Active Session

**Risk**: User changes password while logged in on multiple devices.

**Not Specified**: Should other sessions be terminated?

---

### 5. Time Boundaries and Timezone Issues

**Overall Rating**: ❌ CRITICAL GAP

#### 5.1 User in Different Timezone Than Server

**Risk**: User in UTC+8 registers at 2026-01-07T23:59:59. Server in UTC sees 2026-01-07T15:59:59. Audit logs show "wrong" time from user perspective.

**Not Specified**: How are timezones handled in audit logs?

#### 5.2 Daylight Saving Time Transitions

**Risk**: Token expires at 2026-03-30T02:30:00 (during DST transition). This time doesn't exist in some timezones.

**Not Specified**: UTC storage confirmed but transition handling unclear.

#### 5.3 Leap Second Handling

**Risk**: Rare but real: 2026-06-30T23:59:60 (leap second). PostgreSQL timestamp handling unclear.

#### 5.4 System Clock Changes

**Risk**: Server clock adjusted backwards (NTP correction). Tokens with future expiration suddenly valid again.

**Not Specified**: Clock skew detection.

#### 5.5 Token Expiration During System Maintenance

**Risk**: Server shut down for 1 hour. All tokens that would have expired during shutdown. Are they expired or still valid based on absolute time?

---

## Error Handling and Validation

### Database Error Handling

**Overall Rating**: ❌ CRITICAL GAP

**Missing Error Handling**:

1. **Database Connection Pool Exhausted**: All connections in use, new request arrives. Not specified: Queue request? Reject with 503?

2. **Database Deadlock During Transaction**: Two transactions try to create users simultaneously. PostgreSQL raises deadlock error. Not specified: Retry logic? Backoff strategy?

3. **Foreign Key Constraint Violation**: Organisation deleted mid-transaction. `User.organisation_id` becomes orphaned. Not specified: Transaction rollback? Error message to user?

4. **Unique Constraint Violation**: Email uniqueness violated at database level. Not specified: Map to user-friendly error vs 500 error.

5. **Database Read Replica Lag**: Write goes to primary, immediate read from replica. User not found yet on replica. Not specified: Retry logic? Read-your-writes consistency?

**Test Scenarios Required**:

```python
def test_database_connection_pool_exhausted():
    """Test graceful degradation when DB connections exhausted."""

def test_database_deadlock_retry():
    """Test automatic retry on database deadlock."""

def test_foreign_key_violation_handling():
    """Test transaction rollback on FK constraint violation."""

def test_unique_constraint_violation_friendly_error():
    """Test database unique violation maps to 409 Conflict, not 500 error."""

def test_read_replica_lag_handling():
    """Test read-your-writes consistency for immediate reads after write."""
```

---

### GraphQL Error Handling

**Overall Rating**: ❌ CRITICAL GAP

**Missing Specifications**:

1. **Query Depth Attack**: Plan mentions "query depth limiting (max 10)". Not specified: What error is returned? HTTP status code? Is depth counted from root or per level?

2. **Query Complexity Exceeds Limit**: User constructs expensive nested query. Not defined: Complexity calculation algorithm. Not defined: Limit values per user/role.

3. **Malformed GraphQL Syntax**: Invalid GraphQL query sent. Not specified: Error format, security implications.

4. **Field-Level Errors vs Query-Level Errors**: Some fields succeed, some fail in single query. Not specified: Partial result handling.

5. **GraphQL Batch Query Abuse**: User sends 1000 operations in single request. Bypasses rate limiting. Not specified: Batch size limit.

---

### Validation Error Standards

**Overall Rating**: ⚠️ NEEDS ATTENTION

**Gaps**:

1. **Multiple Validation Errors Simultaneously**: Email invalid AND password too short AND name missing. Not specified: Return all errors or first error only?

2. **Validation Error Messages Expose Sensitive Info**: "Email already registered" reveals account existence (user enumeration). Security trade-off not documented.

3. **Localised Error Messages**: Plan specifies British English. Not specified: Error message localisation strategy.

**Test Scenarios Required**:

```python
def test_multiple_validation_errors_returned():
    """Test all validation errors returned in single response."""

def test_validation_errors_prevent_user_enumeration():
    """Test error messages don't reveal account existence."""

def test_validation_errors_british_english():
    """Test error messages use British English spelling."""
```

---

### Service Layer Error Handling

**Overall Rating**: ⚠️ NEEDS ATTENTION

**Gaps**:

1. **External Service Failures**: Redis unavailable. Email service down. Partial mitigation: Plan mentions "graceful degradation" but no details.

2. **Encryption/Decryption Failures**: IP encryption key rotated, old key lost. Cannot decrypt stored IP addresses. Not specified: Fallback behaviour.

3. **TOTP Library Errors**: `pyotp` raises exception during code generation/verification. Not specified: Error handling strategy.

---

## Race Conditions and Concurrency

### User Creation Race Conditions

**Overall Rating**: ❌ CRITICAL GAP

**Issue**: No locking mechanism specified for user creation.

#### Attack Vector: Simultaneous Registration Bomb

```python
import asyncio
async def register_bomb():
    tasks = [register("victim@example.com", "Pass123!") for _ in range(100)]
    await asyncio.gather(*tasks)
```

**Expected Behaviour**: Only ONE user created, others fail with 409 Conflict
**Current Spec**: No transaction isolation specified

**Mitigation Required**:

```python
from django.db import transaction

@transaction.atomic
def register_user(email, password, organisation):
    # Select for update to lock
    org = Organisation.objects.select_for_update().get(slug=organisation_slug)

    # Check uniqueness within transaction
    if User.objects.filter(email=email).exists():
        raise ValidationError("Email already registered")

    user = User.objects.create(...)
    return user
```

#### Race Condition: First User Becomes Owner

**Scenario**: Organisation "new-org" has 0 users. Two users register simultaneously.

**Problem**:

```python
if organisation.users.count() == 1:  # Both see count=1
    owner_group = Group.objects.get(name="Organisation Owner")
    user.groups.add(owner_group)  # Both become owner!
```

**Impact**: CRITICAL - Two organisation owners violates security model

**Mitigation Required**: Use database-level locking or unique constraint

#### Race Condition: Email Verification Token Collision

**Scenario**: Two users register at exactly same microsecond.

**Risk**: UUID collision (extremely rare but possible).

**Mitigation**: Add compound unique constraint on (user_id, token).

---

### Token Generation Race Conditions

**Overall Rating**: ❌ CRITICAL GAP

#### JWT Token Hash Collision

**Scenario**: Two users log in simultaneously, tokens generated with same random seed.

**Problem**:

```python
token_hash = hashlib.sha256(jwt_token).hexdigest()
SessionToken.objects.create(token_hash=token_hash)  # IntegrityError?
```

**Mitigation Not Specified**: Retry with new token? Fail?

#### Refresh Token Rotation Race

**Scenario**: User has token about to expire. Client sends two refresh requests simultaneously.

**Problem**:

- Both requests see valid refresh token
- Both generate new token and invalidate old refresh token
- One succeeds, one fails (refresh token already used)
- Not specified: Is this detected as token theft? User locked out?

#### Password Reset Token Generation During Active Reset

**Scenario**: User requests password reset twice rapidly.

**Problem**: Two valid tokens exist.

**Not Specified**: Should previous tokens be invalidated?

---

### Session Token Race Conditions

**Overall Rating**: ⚠️ NEEDS ATTENTION

#### Logout During Active Request

**Scenario**: User sends GraphQL query. Before response returns, logout request processed. Token revoked mid-flight.

**Not Specified**: Should in-flight requests complete or fail?

#### Token Expiration During Request

**Scenario**: Request starts with valid token (expires_at 1 second away). Request processing takes 2 seconds. Token expires mid-request.

**Not Specified**: Check expiration at start only or continuously?

#### Concurrent Session Limit Enforcement

**Scenario**: Plan mentions "5 sessions per user". User logs in simultaneously on 5 devices. 6th device logs in.

**Not Specified**: Which session is evicted? Oldest? Random?

---

### Database Transaction Issues

**Overall Rating**: ❌ CRITICAL GAP

#### Lost Update Problem

**Scenario**: Two requests update same user simultaneously.

```python
user = User.objects.get(id=1)  # Request A
user = User.objects.get(id=1)  # Request B

user.first_name = "Alice"      # Request A
user.save()  # last_login also updated

user.last_name = "Smith"       # Request B
user.save()  # Overwrites A's changes!
```

**Mitigation Not Specified**: Use `select_for_update()` or optimistic locking

#### Read Committed Isolation Level

**PostgreSQL Default**: READ COMMITTED

**Risk**: Non-repeatable reads within transaction

**Not Specified**: Should use REPEATABLE READ for critical operations?

#### Serialisation Anomalies

**Example**: Two users try to become first owner simultaneously.

**Mitigation**: Use SERIALIZABLE isolation or explicit locking

**Not Specified**: Isolation level requirements

#### Deadlock Prevention Strategy

**Plan Mentions**: "Retry logic" in Risks section

**Not Detailed**: Exponential backoff? Max retries?

#### Long-Running Transactions

**Risk**: Holding locks too long

**Example**: 2FA setup takes 30 seconds (user scans QR code)

**Not Specified**: Transaction timeout limits

---

### Redis Concurrency

**Overall Rating**: ⚠️ NEEDS ATTENTION

#### Redis WATCH/MULTI/EXEC for Atomic Operations

**Use Case**: Increment rate limit counter atomically.

**Not Specified**: Redis transaction usage.

#### Redis Key Expiration Race Condition

**Scenario**: Check if key exists, then set with expiration.

```python
if not cache.get("rate_limit:user:1"):
    cache.set("rate_limit:user:1", 1, timeout=900)
# Race condition: key might expire between check and set
```

**Mitigation**: Use `SETNX` or Lua scripts

#### Redis Connection Pool Exhaustion

**Problem**: All Redis connections in use.

**Not Specified**: Connection pool size, timeout behaviour.

---

### Session Management Concurrency

**Overall Rating**: ❌ CRITICAL GAP

#### Concurrent Login from Same User

**Scenario**: User double-clicks login button.

**Problem**: Two sessions created when only one intended.

**Not Specified**: Deduplication logic.

#### Session Limit Enforcement Race Condition

**Scenario**: User has 4 sessions, two devices login simultaneously.

**Expected**: One succeeds, one evicts oldest and succeeds = 5 total

**Actual Race Condition**: Both check count=4, both create session = 6 total

**Mitigation Required**: Atomic check-and-increment

#### Concurrent Logout and Request

**Scenario**: User sends logout, immediately sends another request.

**Problem**: Second request might succeed with revoked token (timing).

#### Session Cleanup During Active Use

**Scenario**: Background task deletes expired sessions.

**Problem**: Deletes session currently being used (edge of expiration).

---

## Boundary Conditions

### String Length Boundaries

**Overall Rating**: ⚠️ NEEDS ATTENTION

**Missing Tests**:

1. **Email exactly 255 characters** (max length)
2. **First name exactly 150 characters** (max length)
3. **Password exactly 12 characters** (minimum length)
4. **Password exactly 128 characters** (maximum length)
5. **Organisation name exactly 255 characters**
6. **User agent string exceeding database field length**

---

### Numeric Boundaries

**Overall Rating**: ⚠️ NEEDS ATTENTION

**Missing Tests**:

1. **Rate limiting at exact boundary**: Exactly 5 login attempts in 15 minutes. Is 6th attempt blocked or allowed?

2. **Session limit at exact boundary**: User has exactly 5 sessions (max). 6th login should evict oldest.

3. **Token expiration at exact second**: Token expires_at = 2026-01-07T12:00:00. Request at 11:59:59.999 (valid)? Request at 12:00:00.000 (expired?)? Request at 12:00:00.001 (expired)?

4. **TOTP code time step boundary**: TOTP codes valid for 30-second window. What happens at exact boundary?

---

### Collection Size Boundaries

**Overall Rating**: ⚠️ NEEDS ATTENTION

**Missing Tests**:

1. **Organisation with 10,000+ users**: GraphQL query `users(limit: 10000)`. Pagination required but limits not enforced.

2. **User with hundreds of sessions**: Never logs out, creates new session daily. Session table grows unbounded. Not specified: Session cleanup policy.

3. **Audit log query with millions of records**: `organisationAuditLogs(limit: 100)`. Query performance on large dataset. Not specified: Indexes confirmed but no performance benchmarks.

---

## Invalid Input and Security Testing

### Malicious Input Scenarios

**Overall Rating**: ❌ CRITICAL GAP

**Attack Vectors Not Tested**:

#### SQL Injection in GraphQL Variables

**Attack**:

```graphql
mutation {
  login(input: { email: "admin@example.com' OR '1'='1", password: "anything" }) {
    token
  }
}
```

**Mitigation**: Django ORM should prevent, but explicit test required.

#### NoSQL Injection in Metadata JSON

**Attack**:

```graphql
mutation {
  register(
    input: { email: "test@example.com", metadata: "{\"$where\": \"this.password == 'secret'\"}" }
  )
}
```

**Risk**: JSON fields in `AuditLog.metadata` could be vulnerable.

#### GraphQL Injection

**Attack**:

```graphql
{
  user(id: "1) { password } fakeField: user(id: 1") {
    email
  }
}
```

#### Command Injection in User Agent

**Attack**: User agent string containing shell commands.

```
User-Agent: Mozilla/5.0; $(rm -rf /)
```

#### LDAP Injection in Email

**Attack**: If future LDAP integration added.

```
email: "admin@example.com)(uid=*"
```

#### XML External Entity (XXE) Injection

**Attack**: If any XML processing added to imports/exports.

#### Header Injection

**Attack**: Malicious HTTP headers.

```
X-Forwarded-For: 127.0.0.1\r\nSet-Cookie: admin=true
```

---

### Unicode and Encoding Issues

**Overall Rating**: ⚠️ NEEDS ATTENTION

**Gaps**:

1. **Emoji in names**: `first_name = "John 😀"` - Valid or rejected?

2. **Right-to-left text (Arabic, Hebrew)**: `first_name = "مستخدم"` - Handled correctly?

3. **Zero-width characters**: `email = "test\u200B@example.com"` - Zero-width space

4. **Homograph attacks**: `email = "admin@exаmple.com"` - Cyrillic 'а' instead of Latin 'a'

5. **Normalisation issues**:
   ```python
   password1 = "café"  # NFC normalisation
   password2 = "café"  # NFD normalisation
   # Are these the same password?
   ```

---

### GraphQL Input Validation

**Overall Rating**: ❌ CRITICAL GAP

**Missing Validations**:

1. **Null values in required fields**:

   ```graphql
   mutation {
     register(input: { email: null, password: "Pass123!", firstName: "Test" })
   }
   ```

2. **Empty strings in required fields**:

   ```graphql
   mutation {
     register(input: { email: "", password: "Pass123!", firstName: "Test" })
   }
   ```

3. **Whitespace-only strings**:

   ```graphql
   mutation {
     register(input: { email: "test@example.com", password: "Pass123!", firstName: "   " })
   }
   ```

4. **Extremely long input strings**: DoS attack vector.

5. **Negative IDs or UUIDs**:

   ```graphql
   query {
     user(id: "-1") {
       email
     }
   }
   ```

6. **Invalid UUID format**:
   ```graphql
   query {
     user(id: "not-a-uuid") {
       email
     }
   }
   ```

---

## Token and Session Management Issues

### Token Expiration Edge Cases

**Overall Rating**: ❌ CRITICAL GAP

#### Token Expiration During Multi-Step Operation

**Scenario**: User starts 2FA setup (generates QR code), token expires before confirming.

**Problem**: 2FA device added but not confirmed, user locked out.

**Not Specified**: Should 2FA setup maintain session extension?

#### Grace Period for Expired Tokens

**Question**: Is there a grace period for recently expired tokens?

**Security Trade-off**:

- Grace period improves UX (no sudden logouts)
- But weakens security (token usable after expiration)

**Not Specified**: Plan says "24 hours" but no grace period mentioned.

#### Token Refresh During Expiration Window

**Scenario**: Token expires_at = 12:00:00, refresh request arrives at 11:59:59.

**Problem**: Refresh processed slowly, by the time validation happens it's 12:00:01.

**Not Specified**: Is refresh request timestamped at arrival or validation?

#### Expired Token in Redis but Not Database

**Scenario**: Redis evicts expired token, but database record remains.

**Problem**: Token validation checks Redis first (fast), falls back to database (slow).

**Not Specified**: Are Redis and database kept in sync for expiration?

#### Token Expiration During Password Reset

**Scenario**: User resets password, old tokens should be invalidated.

**Not Specified**: Are all existing sessions terminated? Just current session?

---

### Token Revocation

**Overall Rating**: ⚠️ NEEDS ATTENTION

#### Logout from All Devices

**User Story**: User suspects account compromise, wants to logout everywhere.

**Not Specified**: GraphQL mutation for "logout all sessions".

#### Admin-Initiated Token Revocation

**Scenario**: Admin detects suspicious activity, needs to revoke user's tokens.

**Not Specified**: Admin interface for token management.

#### Token Revocation Propagation Delay

**Problem**: Token revoked in database, Redis cache still has it (TTL not expired).

**Not Specified**: Cache invalidation strategy.

#### Partial Token Revocation

**Scenario**: Revoke only refresh tokens but keep access tokens valid until expiration.

**Not Specified**: Granular revocation support.

---

### Refresh Token Critical Issues

**Overall Rating**: ❌ CRITICAL GAP

#### Refresh Token Reuse Detection Missing

**Attack**: Attacker steals refresh token, uses it before legitimate user.

**Plan Gap**: No mention of refresh token reuse detection.

**Industry Standard**: OAuth 2.0 recommends detecting reuse and revoking all tokens.

**Mitigation Required**:

```python
def refresh_token(refresh_token: str) -> dict:
    session = SessionToken.objects.get(refresh_token_hash=hash(refresh_token))

    if session.refresh_used:
        # Token reuse detected - potential theft
        # Revoke ALL sessions for this user
        SessionToken.objects.filter(user=session.user).delete()
        raise SecurityError("Token reuse detected")

    session.refresh_used = True
    session.save()

    # Generate new tokens...
```

#### Refresh Token Rotation Not Atomic

**Problem**: Old refresh token invalidated before new token generated.

**Risk**: Network error during rotation = user locked out.

#### Refresh Token Family Tracking Missing

**Concept**: Track lineage of refresh tokens to detect theft.

**Not Specified**: Token family IDs for tracking rotation chains.

#### Refresh Token Sliding Expiration

**Question**: Does refresh token expiration extend on use?

**Plan Says**: "30-day expiration"

**Not Specified**: Is this 30 days from creation or 30 days from last use?

#### Refresh Token Limit per User

**Attack**: Attacker generates unlimited refresh tokens.

**Not Specified**: Max refresh tokens per user.

---

## Two-Factor Authentication Gaps

### TOTP Device Loss and Recovery

**Overall Rating**: ⚠️ NEEDS ATTENTION

#### User Loses 2FA Device with No Backup Codes

**User Story**: User's phone stolen, no backup codes saved.

**Plan Says**: "Backup codes for account recovery"

**Not Specified**: What if backup codes also lost? Admin recovery process?

#### Backup Code Generation Not Detailed

**Questions**:

- How many backup codes generated?
- One-time use or reusable?
- Stored hashed or encrypted?
- Can user regenerate backup codes?

#### 2FA Device Verification Before Enabling

**Issue**: User enables 2FA, immediately loses device, never verified setup.

**Risk**: User locked out before first successful 2FA login.

**Not Specified**: Require successful 2FA login before fully enabled?

---

### Backup Codes Implementation

**Overall Rating**: ❌ CRITICAL GAP

**Critical Missing Details**:

#### Backup Code Format

- Length? (8 digits? 16 chars?)
- Character set? (numbers only? alphanumeric?)
- Entropy sufficient?

#### Backup Code Storage

**Questions**:

- Separate `BackupCode` model?
- JSON field in `TOTPDevice`?
- Hashed like passwords?

#### Backup Code Usage Tracking

- After using backup code, is it invalidated?
- Can user see which backup codes are unused?

#### Backup Code Regeneration

- User regenerates backup codes
- Are old ones immediately invalidated?
- Requires password confirmation?

#### Backup Code Rate Limiting

- Attacker tries all possible backup codes
- Not specified: Rate limiting for backup code attempts

---

### 2FA Bypass Attempts

**Overall Rating**: ❌ CRITICAL GAP

#### Session Fixation to Bypass 2FA

**Attack**: Attacker obtains valid password, tries to use old pre-2FA session.

**Mitigation Required**: All sessions invalidated when 2FA enabled.

**Not Specified**: Explicit session invalidation on 2FA enable.

#### 2FA Code Reuse Attack

**Attack**: Attacker captures valid TOTP code, tries to reuse within 30-second window.

**Mitigation**: Track used codes within time window.

**Not Specified**: TOTP code reuse prevention.

#### Disable 2FA Without Verification

**Attack**: Attacker gains access to authenticated session, disables 2FA.

**Plan Says**: `disableTwoFactor(password: String!)`

**Gap**: What if password already compromised? Should require 2FA code to disable?

#### 2FA Rate Limiting Bypass

**Attack**: Attacker rotates IP addresses to bypass rate limiting.

**Plan Says**: "5 per 15 minutes per user"

**Mitigation**: Rate limit by user ID, not just IP.

#### Time Synchronisation Attack

**Attack**: Manipulate server time to make old TOTP codes valid.

**Mitigation**: Use NTP, validate time synchronisation.

**Not Specified**: Time sync validation.

---

## Email and Communication Issues

### SMTP Failure Handling

**Overall Rating**: ⚠️ NEEDS ATTENTION

**Plan Says**: "Queue emails, retry logic, fallback SMTP provider"

**Gaps**:

1. **Email queue implementation not detailed**: Celery tasks? Django Q? RQ? Persistent queue (database) or in-memory (Redis)? Max retry attempts?

2. **Email delivery status tracking**: How to know if email was delivered? Bounce handling? User notification of failed delivery?

3. **Fallback SMTP provider switching**: Primary SMTP fails, switch to fallback. Not specified: Automatic or manual failover? How to detect primary is back online?

---

### Email Validation

**Overall Rating**: ⚠️ NEEDS ATTENTION

#### Disposable Email Addresses

**User**: Registers with `temp@mailinator.com`

**Not Specified**: Should disposable email domains be blocked?

#### Email Format Validation

**Django's `EmailField` used**: Good

**Edge Cases**:

- `user@domain` (no TLD)
- `user@[192.168.1.1]` (IP address)
- `user+tag@example.com` (plus addressing)

**Not Specified**: Are these allowed?

#### Email Case Sensitivity

**Problem**: `User@Example.com` vs `user@example.com`

**Plan Does Not Specify**: Case-insensitive comparison?

#### Email Change Process

**User**: Wants to change email address

**Not Specified**: Mutation for email change. Require verification of new email before switch?

---

### Email Bombing Prevention

**Overall Rating**: ❌ CRITICAL GAP

#### Registration Email Bombing

**Attack**: Attacker registers 1000 accounts with `victim@example.com`

**Result**: Victim receives 1000 verification emails.

**Plan Says**: "Registration: 3 per hour per IP"

**Gap**: Rate limit by email address, not just IP.

**Mitigation Required**:

```python
# Rate limit by BOTH IP and email
registration_attempts = cache.get(f"register:{email}") or 0
if registration_attempts >= 3:
    raise RateLimitError("Too many registration attempts")
```

#### Password Reset Email Bombing

**Attack**: Attacker triggers password reset repeatedly for victim.

**Plan Says**: "Password reset: 3 per hour per email"

**Good**: Rate limited by email

**Gap**: What if attacker uses multiple accounts to trigger resets for same victim?

#### Email Verification Resend Abuse

**Attack**: User repeatedly requests verification email resend.

**Plan Mentions**: `resendVerificationEmail` mutation

**Not Specified**: Rate limiting for resend.

#### Email as DoS Vector

**Attack**: Trigger expensive email operations (with attachments) to overload email service.

**Not Applicable**: No attachments in plan, but worth considering.

---

## High Priority Implementation Gaps

### N+1 Query Risk

**Severity**: HIGH
**Location**: GraphQL queries

**Issue**: The GraphQL user query uses `select_related('organisation')` but doesn't prefetch related data like `profile`, `totp_devices`, or `groups`.

**Impact**: Each user query triggers multiple additional database queries for related objects, causing severe performance degradation with large datasets.

**Reproduction**:

1. Query list of 100 users
2. For each user, GraphQL resolves `profile`, `totp_devices`, `groups`
3. Results in 300+ database queries instead of 4

**Recommendation**:

```python
@strawberry.field
def users(self, info: Info, limit: int = 10) -> List[User]:
    """Get users with optimised prefetching."""
    queryset = User.objects.filter(
        organisation=info.context.request.user.organisation
    ).select_related(
        'organisation',
        'profile'
    ).prefetch_related(
        'totp_devices',
        'groups',
        'sessions'
    )
    return queryset[offset:offset + limit]
```

---

### Missing Token Revocation on Password Change

**Severity**: HIGH

**Issue**: The plan doesn't specify that all existing session tokens should be revoked when a user changes their password.

**Impact**: If a user's account is compromised and they change their password, the attacker can still use existing session tokens to access the account.

**Reproduction**:

1. Attacker steals user's session token
2. User realises account is compromised
3. User changes password
4. Attacker still has valid session token and maintains access

**Recommendation**:

```python
# apps/core/services/auth_service.py

def change_password(user: User, new_password: str) -> None:
    """Change password and revoke all sessions."""
    user.set_password(new_password)
    user.save()

    # Revoke all existing sessions
    SessionToken.objects.filter(user=user).delete()

    # Clear Redis cache
    cache.delete_pattern(f'session:user:{user.id}:*')

    # Audit log
    AuditService.log_event('password_change', user, request)
```

---

### Organisation Boundary Enforcement

**Severity**: HIGH

**Issue**: The GraphQL queries check organisation boundaries after fetching the object, creating a TOCTOU (Time-of-Check-Time-of-Use) race condition.

**Impact**: In concurrent environments, a user could be moved to another organisation between the fetch and the boundary check, leading to data leakage.

**Reproduction**:

1. User A queries User B (same organisation)
2. Admin moves User B to different organisation
3. Query completes, returning User B's data to User A
4. Organisation boundary violated

**Recommendation**:

```python
@strawberry.field
def user(self, info: Info, user_id: strawberry.ID) -> User:
    """Get user with atomic organisation check."""
    current_user = info.context.request.user

    # Atomic query with organisation boundary
    user = User.objects.select_related('organisation').select_for_update().get(
        id=user_id,
        organisation=current_user.organisation  # Atomic check
    )

    return user
```

---

### Rate Limiting Implementation

**Severity**: HIGH

**Issue**: The plan specifies rate limits but doesn't address:

- Rate limiting per IP + user combination
- Distributed rate limiting across multiple servers
- Rate limit bypass via IP rotation

**Impact**:

- Attackers can bypass rate limits by rotating IPs
- Rate limiting doesn't work in horizontally scaled environments
- No protection against distributed brute force attacks

**Recommendation**:

```python
# apps/core/middleware/rate_limit.py

import redis
from django.core.cache import cache

class RateLimitMiddleware:
    """Distributed rate limiting using Redis."""

    def check_rate_limit(self, key: str, limit: int, window: int) -> bool:
        """Check rate limit using sliding window algorithm."""
        now = time.time()
        pipe = cache.client.pipeline()

        # Add current timestamp
        pipe.zadd(key, {now: now})

        # Remove old entries outside window
        pipe.zremrangebyscore(key, 0, now - window)

        # Count attempts
        pipe.zcard(key)

        # Set expiry
        pipe.expire(key, window)

        results = pipe.execute()
        count = results[2]

        return count <= limit

    def get_rate_limit_key(self, action: str, request) -> str:
        """Generate rate limit key combining IP and user."""
        ip = get_client_ip(request)
        email = request.data.get('email', '')
        return f"{action}:{ip}:{email}"
```

---

### Audit Log Performance

**Severity**: HIGH

**Issue**: The `AuditLog` model has indexes on `user`, `organisation`, and `action` but not on `created_at`, which is used in all queries.

**Impact**: Audit log queries without timestamp filtering will perform full table scans, degrading performance as logs grow.

**Reproduction**:

1. System runs for 6 months, accumulating 10 million audit logs
2. Query: "Get all login attempts for user X"
3. Database performs full table scan
4. Query takes 30+ seconds

**Recommendation**:

```python
class AuditLog(models.Model):
    # ... existing fields ...

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),  # Composite index
            models.Index(fields=['organisation', '-created_at']),  # Composite index
            models.Index(fields=['action', '-created_at']),  # Composite index
            models.Index(fields=['-created_at']),  # For global queries
        ]
```

**Additional Recommendation**: Implement audit log archival after 90 days to separate historical data.

---

### Session Timeout Configuration

**Severity**: HIGH

**Issue**: The plan mentions "24-hour inactivity" but doesn't specify how inactivity is tracked or how timeout is enforced.

**Impact**:

- Sessions may never expire if timeout is not properly enforced
- No clear definition of "inactivity" (no API calls? no mutations?)
- Stale sessions accumulate in database and Redis

**Recommendation**:

```python
# apps/core/middleware/session_timeout.py

class SessionTimeoutMiddleware:
    """Enforce session timeout based on inactivity."""

    INACTIVITY_TIMEOUT = 24 * 60 * 60  # 24 hours

    def __call__(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')

        if token:
            session = SessionToken.objects.get(token_hash=hash_token(token))

            # Check last activity
            time_since_activity = timezone.now() - session.last_activity

            if time_since_activity.total_seconds() > self.INACTIVITY_TIMEOUT:
                session.delete()
                raise PermissionError("Session expired due to inactivity")

            # Update last activity (auto_now on last_activity field)
            session.save(update_fields=['last_activity'])

        return self.get_response(request)
```

---

### 2FA Backup Codes

**Severity**: HIGH

**Issue**: The plan mentions backup codes but provides no implementation details.

**Recommendation**:

```python
# apps/core/models/backup_code.py

class BackupCode(models.Model):
    """Backup codes for 2FA recovery.

    Each user gets 10 backup codes. Each code can only be used once.
    Codes are hashed using bcrypt before storage.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='backup_codes')
    code_hash = models.CharField(max_length=255)
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'backup_codes'

    @staticmethod
    def generate_codes(user: User, count: int = 10) -> list[str]:
        """Generate backup codes for user.

        Returns:
            List of plain text backup codes (shown once to user)
        """
        codes = []
        for _ in range(count):
            plain_code = secrets.token_hex(4).upper()  # 8-character hex
            code_hash = bcrypt.hashpw(plain_code.encode(), bcrypt.gensalt())

            BackupCode.objects.create(
                user=user,
                code_hash=code_hash.decode()
            )
            codes.append(plain_code)

        return codes
```

---

### GraphQL Query Depth Limiting

**Severity**: HIGH

**Issue**: The plan mentions query depth limiting but provides no implementation details.

**Example Attack**:

<!-- prettier-ignore -->
```graphql
query {
  users {
    organisation {
      users {
        organisation {
          users {
            # ... nested 50 levels deep
          }
        }
      }
    }
  }
}
```

**Recommendation**:

```python
# api/middleware/query_complexity.py

from strawberry.extensions import QueryDepthLimiter

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        QueryDepthLimiter(max_depth=10),  # Maximum query depth
    ]
)
```

---

## Medium Priority Issues

### Email Service Failure Handling

**Severity**: MEDIUM

**Issue**: The plan mentions email service failure but doesn't specify retry logic, dead letter queues, or fallback mechanisms.

**Impact**: Registration and password reset emails may silently fail, blocking users from accessing the system.

**Recommendation**:

- Implement email queue with Celery
- Add retry logic (3 attempts with exponential backoff)
- Store failed emails in dead letter queue for manual review
- Provide alternative verification methods (admin approval)

---

### Timezone Handling

**Severity**: MEDIUM

**Issue**: The plan stores timestamps in UTC but doesn't specify how timezone conversion is handled in GraphQL responses.

**Impact**: Users see timestamps in UTC instead of their local timezone, causing confusion.

**Recommendation**:

```python
@strawberry.type
class AuditLog:
    created_at: datetime

    @strawberry.field
    def created_at_local(self, info: Info) -> datetime:
        """Return timestamp in user's timezone."""
        user_tz = info.context.request.user.profile.timezone
        return self.created_at.astimezone(timezone(user_tz))
```

---

### User Enumeration

**Severity**: MEDIUM

**Issue**: The registration endpoint returns different errors for "email already exists" vs "invalid email format", allowing attackers to enumerate registered users.

**Impact**: Attackers can build a list of all registered email addresses for phishing attacks.

**Recommendation**: Return generic error for all registration failures: "Registration failed. Please check your email."

---

### Account Lockout

**Severity**: MEDIUM

**Issue**: Rate limiting (5 attempts per 15 minutes) is not the same as account lockout. The plan doesn't specify account lockout after repeated failed login attempts.

**Impact**: Attackers can continue brute force attempts indefinitely by waiting 15 minutes between batches.

**Recommendation**:

- Lock account after 10 failed login attempts within 1 hour
- Require email verification or admin unlock to re-enable account
- Notify user via email when account is locked

---

### Password History

**Severity**: MEDIUM

**Issue**: The plan mentions "password history to prevent reuse" but provides no implementation.

**Impact**: Users can reuse recently compromised passwords.

**Recommendation**:

```python
class PasswordHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @classmethod
    def check_password_reuse(cls, user: User, new_password: str, history_count: int = 5) -> bool:
        """Check if password was used in last N passwords."""
        recent_passwords = cls.objects.filter(user=user)[:history_count]

        for old_password in recent_passwords:
            if check_password(new_password, old_password.password_hash):
                return True  # Password was used before

        return False
```

---

### User Agent Validation

**Severity**: MEDIUM

**Issue**: User agent is stored but not validated. Malformed or excessively long user agents could cause database issues.

**Impact**: Potential database field overflow or injection attacks.

**Recommendation**: Validate and truncate user agent to 500 characters.

---

### Error Message Standards

**Severity**: MEDIUM

**Issue**: The plan doesn't specify error message standards. GraphQL mutations should return structured errors, not plain strings.

**Impact**: Frontend cannot programmatically handle errors.

**Recommendation**:

```python
@strawberry.type
class Error:
    code: str
    message: str
    field: Optional[str] = None

@strawberry.type
class AuthPayload:
    token: Optional[str]
    user: Optional[User]
    errors: Optional[List[Error]]
```

---

### Concurrent Session Limits

**Severity**: MEDIUM

**Issue**: The plan mentions "5 sessions per user" but doesn't specify implementation.

**Impact**: Attackers can create unlimited sessions for a compromised account.

**Recommendation**:

```python
def create_session(user: User) -> SessionToken:
    """Create session and enforce limit."""
    # Count active sessions
    session_count = SessionToken.objects.filter(
        user=user,
        expires_at__gt=timezone.now()
    ).count()

    if session_count >= 5:
        # Revoke oldest session
        oldest = SessionToken.objects.filter(user=user).order_by('created_at').first()
        oldest.delete()

    # Create new session
    return SessionToken.objects.create(...)
```

---

## Low Priority Issues

1. **BaseToken Abstract Model Lacks Validation**: The `BaseToken.is_expired()` method doesn't handle null `expires_at`.

2. **Missing Database Indexes on Foreign Keys**: Foreign keys like `SessionToken.user` should have composite indexes with `created_at` for efficient queries.

3. **Audit Log Metadata Not Validated**: The `metadata` JSONField is not validated or size-limited.

4. **UserProfile Creation Not Automated**: The plan doesn't specify auto-creation of `UserProfile` when a user is created.

5. **Organisation Slug Validation Missing**: Organisation slug should be validated to prevent special characters or SQL injection attempts.

---

## Test Scenarios That Must Be Added

### Critical Priority Tests (27+ scenarios)

**Concurrency and Race Conditions**:

- Concurrent registration with same email (single user created)
- First user owner race condition (single owner only)
- Concurrent token verification (idempotency)
- Refresh token reuse detection (security lockdown)
- Refresh token rotation (atomic)
- JWT token hash collision (retry)
- Concurrent user updates (no lost updates)
- Database deadlock (automatic retry)
- Session limit enforcement (atomic)
- Concurrent login (single session created)

**Security Vulnerabilities**:

- SQL injection blocked
- NoSQL injection in JSON fields
- GraphQL injection attempts
- 2FA enable invalidates sessions
- TOTP code reuse prevention
- Disable 2FA requires code
- Registration rate limit by email
- Password reset email bombing
- Backup code rate limiting
- Command injection in user agent

**Token and Session Management**:

- Token expiration during 2FA setup
- No grace period for expired tokens
- Token refresh timestamps at arrival
- Password reset invalidates sessions
- Token reuse after marked used
- Clock skew handling
- Redis/database token expiration sync

---

### High Priority Tests (34+ scenarios)

**Boundary Conditions**:

- Email max length (255 chars)
- Password min length (12 chars)
- Password max length (128 chars)
- Token expiration precision
- Rate limit exact boundary
- Session limit exact boundary
- GraphQL pagination limits
- Audit log performance

**Error Handling and Validation**:

- GraphQL null in required fields
- GraphQL empty string validation
- GraphQL oversized input (DoS)
- GraphQL query depth limit
- GraphQL batch query limit
- Multiple validation errors
- User enumeration prevention

**Email and Communication**:

- Email queued on SMTP failure
- Email retry logic
- Email delivery tracking
- SMTP fallback failover
- Verification email resend rate limit
- Email case-insensitive
- Email change requires verification

**Organisation and Multi-Tenancy**:

- Organisation deactivation invalidates sessions
- Organisation deletion preserves audit logs
- Soft delete slug conflict handling
- Register with deleted organisation

---

### Medium Priority Tests (18+ scenarios)

**User Experience**:

- Session list shows device info
- Logout specific device
- New device login notification
- Error response format standard
- Error codes for programmatic handling
- Admin account recovery
- Deleted account recovery within 90 days

**Edge Cases and Unicode**:

- Emoji in names
- Right-to-left text
- Zero-width character rejection
- Homograph attack prevention
- Unicode normalisation
- Null bytes in password
- Special-character-only password

**Time and Timezone**:

- User timezone in audit logs
- DST transition handling
- System clock backward adjustment
- Token expiration during downtime

---

## Security Vulnerabilities Summary

| Vulnerability                        | Severity | OWASP Category                                        | Mitigation Status             |
| ------------------------------------ | -------- | ----------------------------------------------------- | ----------------------------- |
| User enumeration via error messages  | Medium   | A07:2021 – Identification and Authentication Failures | ⚠️ Partially addressed        |
| Race condition in user creation      | High     | A04:2021 – Insecure Design                            | ❌ Not mitigated              |
| Token reuse not detected             | Critical | A07:2021 – Identification and Authentication Failures | ❌ Not implemented            |
| Email bombing attack vector          | Medium   | A05:2021 – Security Misconfiguration                  | ⚠️ Partial rate limiting      |
| 2FA bypass via session fixation      | High     | A07:2021 – Identification and Authentication Failures | ❌ Not mitigated              |
| SQL injection in metadata            | Medium   | A03:2021 – Injection                                  | ⚠️ ORM protection assumed     |
| Refresh token rotation not atomic    | High     | A02:2021 – Cryptographic Failures                     | ❌ Not specified              |
| Password reuse not prevented         | Medium   | A07:2021 – Identification and Authentication Failures | ⚠️ Mentioned but not detailed |
| Rate limiting bypass via IP rotation | Medium   | A05:2021 – Security Misconfiguration                  | ⚠️ Partially mitigated        |
| TOTP code reuse possible             | Medium   | A07:2021 – Identification and Authentication Failures | ❌ Not mitigated              |
| Backup codes not implemented         | High     | A07:2021 – Identification and Authentication Failures | ❌ Not specified              |
| Time synchronisation attack          | Low      | A04:2021 – Insecure Design                            | ❌ Not addressed              |
| Organisation boundary bypass         | Critical | A01:2021 – Broken Access Control                      | ⚠️ Partially specified        |
| Concurrent session race condition    | Medium   | A04:2021 – Insecure Design                            | ❌ Race conditions possible   |
| CSRF protection missing              | Critical | A05:2021 – Security Misconfiguration                  | ❌ Not implemented            |
| Email verification bypass            | Critical | A07:2021 – Identification and Authentication Failures | ❌ Not enforced               |
| Token storage vulnerability          | Critical | A02:2021 – Cryptographic Failures                     | ❌ Not hashed properly        |
| TOTP secret storage                  | Critical | A02:2021 – Cryptographic Failures                     | ⚠️ Encryption not detailed    |
| Password reset tokens plaintext      | Critical | A02:2021 – Cryptographic Failures                     | ❌ Not hashed                 |
| IP key rotation not specified        | Critical | A04:2021 – Insecure Design                            | ❌ Not implemented            |

---

## Performance Concerns

| Operation                   | Expected Time     | Concern                        | Mitigation Status                                        |
| --------------------------- | ----------------- | ------------------------------ | -------------------------------------------------------- |
| Login (no 2FA)              | < 200ms           | Argon2 hashing may take longer | ⚠️ Needs benchmarking                                    |
| Registration                | < 500ms           | Email sending may block        | ⚠️ Async email queue recommended                         |
| Password reset              | < 300ms           | Token generation + email       | ⚠️ Async recommended                                     |
| GraphQL user query          | < 100ms           | N+1 query risk                 | ⚠️ Some select_related, not consistent                   |
| Audit log query             | < 500ms           | Large dataset scanning         | ⚠️ Indexes specified but no pagination limit enforcement |
| Token refresh               | < 100ms           | Redis + database round-trip    | ✅ Acceptable                                            |
| 2FA verification            | < 200ms           | TOTP calculation               | ✅ Fast                                                  |
| IP decryption in audit logs | < 50ms per record | Fernet decryption overhead     | ⚠️ May be slow for bulk operations                       |

**Recommendations**:

1. Benchmark Argon2: Tune parameters to meet 200ms target
2. Async email queue: Use Celery/Django-Q for non-blocking email
3. Audit log pagination: Enforce max 100 records per query
4. Bulk IP decryption: Cache decrypted IPs for admin views

---

## Best Practices Compliance

### Security Best Practices

| Practice                   | Status | Notes                                   |
| -------------------------- | ------ | --------------------------------------- |
| Password hashing (Argon2)  | ✅     | Compliant                               |
| Token-based authentication | ✅     | JWT with refresh tokens                 |
| Two-factor authentication  | ✅     | TOTP with QR codes                      |
| Rate limiting              | ⚠️     | Specified but implementation gaps       |
| CSRF protection            | ❌     | Not mentioned for GraphQL               |
| IP address encryption      | ✅     | Fernet encryption specified             |
| Audit logging              | ✅     | Comprehensive event tracking            |
| Session expiration         | ⚠️     | Specified but enforcement unclear       |
| Password complexity        | ✅     | 12+ chars, uppercase, lowercase, number |
| Account lockout            | ❌     | Not implemented                         |
| Password reset security    | ⚠️     | 15-minute expiry but tokens not hashed  |
| Email verification         | ⚠️     | Implemented but not enforced            |

### Django Best Practices

| Practice               | Status | Notes                              |
| ---------------------- | ------ | ---------------------------------- |
| Custom User model      | ✅     | Extends AbstractBaseUser           |
| Model field validation | ✅     | Custom validators defined          |
| Database indexing      | ⚠️     | Some indexes missing               |
| Signal handlers        | ❌     | Not specified for profile creation |
| Manager methods        | ✅     | Custom UserManager                 |
| Admin configuration    | ✅     | Comprehensive admin setup          |
| Permissions and groups | ✅     | Django groups for RBAC             |
| Multi-tenancy          | ✅     | Organisation-based isolation       |
| Timezone handling      | ⚠️     | UTC storage but display unclear    |
| GDPR compliance        | ✅     | Data export, deletion, audit       |

### GraphQL Best Practices

| Practice                | Status | Notes                               |
| ----------------------- | ------ | ----------------------------------- |
| Input validation        | ✅     | Input types defined                 |
| Error handling          | ⚠️     | Error structure not specified       |
| Query depth limiting    | ❌     | Mentioned but not implemented       |
| Complexity analysis     | ❌     | Not implemented                     |
| N+1 query prevention    | ⚠️     | Some select_related, not consistent |
| Permission decorators   | ✅     | Permission classes defined          |
| Pagination              | ⚠️     | Offset/limit but no cursor          |
| Field-level permissions | ❌     | Not implemented                     |
| DataLoader pattern      | ❌     | Not mentioned                       |

---

## GDPR Compliance Analysis

| Requirement               | Status | Implementation                       |
| ------------------------- | ------ | ------------------------------------ |
| Right to access           | ✅     | User can query own data via GraphQL  |
| Right to rectification    | ✅     | User can update profile              |
| Right to erasure          | ⚠️     | Not specified (should soft delete)   |
| Right to data portability | ⚠️     | Export functionality not implemented |
| Right to restriction      | ❌     | No account suspension functionality  |
| Data breach notification  | ❌     | No notification mechanism specified  |
| Privacy by design         | ✅     | IP encryption, password hashing      |
| Consent management        | ❌     | No consent tracking                  |
| Data retention            | ⚠️     | Specified (90 days) but not enforced |
| Data minimisation         | ✅     | Only essential data collected        |

**Recommendation**: Add explicit GDPR compliance features before production deployment.

---

## User Experience Gaps

### Device Management

**Issue**: Users cannot see which devices they're logged in on or manage individual sessions.

**Missing**:

- Session list showing device info (parsed user agent)
- Device-specific logout mutation
- Session custom naming ("Work Laptop", "Home Phone")
- Last activity timestamp in UI
- New device login notifications

### Account Recovery

**Issue**: Account recovery scenarios inadequately addressed.

**Missing Scenarios**:

1. User forgets email address (recovery by phone? username? admin help?)
2. Email account compromised (additional verification for sensitive operations?)
3. Locked account recovery (how to unlock? wait duration? contact admin?)
4. Inactive account handling (policy for accounts with no login for 1 year?)
5. Deleted account recovery (can user recover within 90-day soft delete window?)

### Error Messages

**Issue**: User-facing error messages not standardised.

**Gaps**:

- Inconsistent error formats
- Error message localisation not specified
- Security vs UX trade-off in error messages not documented
- Error codes for programmatic handling missing

---

## Recommendations

### Immediate Actions Required (Before Implementation)

1. **Address all 6 CRITICAL security vulnerabilities** - Do not proceed until resolved
2. **Review and approve security architecture** with security team
3. **Specify token hashing algorithms** for all token types
4. **Define CSRF protection mechanism** for GraphQL
5. **Document key rotation procedures** for encryption keys
6. **Create error response format standard** for GraphQL

### During Implementation

1. **Implement missing security features**:
   - Account lockout after failed attempts
   - CSRF protection for GraphQL
   - Query depth and complexity limiting
   - Backup code system for 2FA
   - Refresh token reuse detection
   - Password history validation

2. **Add performance optimisations**:
   - Composite database indexes
   - Query prefetching in GraphQL resolvers
   - Redis caching for sessions
   - Async audit log writes

3. **Enhance GDPR compliance**:
   - Data export functionality
   - Account deletion (soft delete with recovery)
   - Consent tracking
   - Data retention enforcement

4. **Write comprehensive tests** for all identified scenarios

### Before Production Deployment

1. **Security audit** by external firm
2. **Penetration testing** on staging environment
3. **Load testing** with 1000+ concurrent users
4. **GDPR compliance review** by legal team
5. **Documentation completion** and review
6. **Disaster recovery procedures** for key compromise
7. **Monitoring and alerting setup** for security events

---

## Conclusion

The User Authentication System plan (US-001 v1.1.0) demonstrates strong architectural foundations with comprehensive security features. However, **critical gaps in security implementation, concurrency control, and edge case specifications MUST be addressed before implementation**.

### Key Takeaways

**✅ Strengths**:

- Strong security architecture (Argon2, 2FA, IP encryption, audit logging)
- Comprehensive multi-tenancy design
- Good separation of concerns (models, services, GraphQL)
- Detailed GraphQL API specifications
- Well-structured database models

**❌ Critical Gaps** (MUST FIX):

- Token storage vulnerabilities (session, password reset, TOTP secrets)
- CSRF protection missing from GraphQL
- Email verification not enforced
- IP encryption key rotation not specified
- Race conditions in user creation and token generation
- Refresh token reuse detection missing
- 2FA bypass vectors not mitigated
- Backup code implementation not specified
- Database transaction isolation not defined
- Email bombing prevention incomplete

**⚠️ High Priority Gaps** (SHOULD FIX):

- N+1 query performance risk
- Token revocation on password change missing
- Organisation boundary enforcement (TOCTOU race condition)
- Rate limiting implementation gaps
- Audit log performance concerns
- Session timeout configuration undefined
- GraphQL query depth limiting not implemented

**Overall Status**: ⚠️ **NOT READY FOR IMPLEMENTATION**

### Recommended Next Steps

1. Create addendum document addressing all critical gaps (estimated 2-3 days)
2. Update implementation plan with concurrency mitigations
3. Create comprehensive test plan covering all identified scenarios
4. Review with security team before implementation begins
5. Use `/syntek-dev-suite:security` to address critical vulnerabilities
6. Use `/syntek-dev-suite:backend` to implement missing features
7. Use `/syntek-dev-suite:test-writer` to create comprehensive tests

---

**Reviewed By**: QA Tester Agent
**Date**: 07/01/2026
**Recommendation**: ⚠️ **REVISE PLAN BEFORE IMPLEMENTATION**
**Estimated Additional Planning Time**: 2-3 days
**Estimated Implementation Blockers**: 6 critical, 8 high, 8 medium priority items
