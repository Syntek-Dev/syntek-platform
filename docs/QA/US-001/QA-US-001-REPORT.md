# QA Report: User Authentication System (US-001)

**Last Updated**: 08/01/2026
**Version**: 2.1
**Maintained By**: QA Tester Agent
**Date Range**: Phase 1 (Models) & Phase 2 (Services) Implementation
**Localisation**: British English (en_GB)
**Timezone**: Europe/London
**Phase 1 Status**: ✅ Completed (07/01/2026)
**Phase 2 Status**: ✅ Completed (08/01/2026) - Service Layer Implemented
**Next Phase**: Phase 3 - GraphQL API Implementation

---

## Table of Contents

- [QA Report: User Authentication System (US-001) Phase 1](#qa-report-user-authentication-system-us-001-phase-1)
  - [Table of Contents](#table-of-contents)
  - [Executive Summary](#executive-summary)
  - [Overall Assessment](#overall-assessment)
  - [Critical Issues (Blocks Deployment)](#critical-issues-blocks-deployment)
    - [Security Vulnerabilities](#security-vulnerabilities)
      - [1. Session Token Storage Vulnerability](#1-session-token-storage-vulnerability)
      - [2. TOTP Secret Storage Security](#2-totp-secret-storage-security)
      - [3. Password Reset Token Not Hashed](#3-password-reset-token-not-hashed)
      - [4. CSRF Protection for GraphQL NOT Implemented](#4-csrf-protection-for-graphql-not-implemented)
      - [5. Email Verification Not Enforced on Login](#5-email-verification-not-enforced-on-login)
      - [6. IP Encryption Key Rotation NOT Implemented](#6-ip-encryption-key-rotation-not-implemented)
      - [7. TOKEN_SIGNING_KEY Not Configured in Environment Files](#7-token_signing_key-not-configured-in-environment-files)
    - [Missing Implementation Features](#missing-implementation-features)
      - [8. No GraphQL Mutations for Authentication](#8-no-graphql-mutations-for-authentication)
      - [9. No Authentication Service Layer](#9-no-authentication-service-layer)
      - [10. Password Reset Workflow NOT Implemented](#10-password-reset-workflow-not-implemented)
      - [11. Email Verification Workflow NOT Implemented](#11-email-verification-workflow-not-implemented)
      - [12. 2FA Enrollment Workflow NOT Implemented](#12-2fa-enrollment-workflow-not-implemented)
      - [13. Login Flow with 2FA NOT Implemented](#13-login-flow-with-2fa-not-implemented)
      - [14. No Rate Limiting on Authentication Endpoints](#14-no-rate-limiting-on-authentication-endpoints)
      - [15. Account Lockout Mechanism NOT Implemented](#15-account-lockout-mechanism-not-implemented)
      - [16. No Concurrent Session Limit Enforcement](#16-no-concurrent-session-limit-enforcement)
      - [17. No Token Revocation on Password Change](#17-no-token-revocation-on-password-change)
    - [Configuration Issues](#configuration-issues)
      - [18. GraphQL Introspection Enabled in Production](#18-graphql-introspection-enabled-in-production)
  - [High Priority Issues (Must Fix Before Production)](#high-priority-issues-must-fix-before-production)
    - [Database and Query Optimisation](#database-and-query-optimisation)
      - [H1: Missing Composite Indexes for Multi-Tenant Queries](#h1-missing-composite-indexes-for-multi-tenant-queries)
      - [H2: Missing Indexes on Token Expiry Fields](#h2-missing-indexes-on-token-expiry-fields)
      - [H3: AuditLog Uses CASCADE Instead of SET_NULL](#h3-auditlog-uses-cascade-instead-of-set_null)
    - [Security and Concurrency](#security-and-concurrency)
      - [H4: PostgreSQL Row-Level Security (RLS) NOT Configured](#h4-postgresql-row-level-security-rls-not-configured)
      - [H5: N+1 Query Prevention NOT Implemented](#h5-n1-query-prevention-not-implemented)
      - [H6: Race Condition in User Creation](#h6-race-condition-in-user-creation)
      - [H7: Refresh Token Replay Detection NOT Implemented](#h7-refresh-token-replay-detection-not-implemented)
    - [Testing](#testing)
      - [H8: No Integration Tests](#h8-no-integration-tests)
  - [Medium Priority Issues (Should Fix)](#medium-priority-issues-should-fix)
    - [Implementation Gaps](#implementation-gaps)
      - [M1: Module-Level Docstrings Missing](#m1-module-level-docstrings-missing)
      - [M2: Error Messages Lack Codes and Actionable Guidance](#m2-error-messages-lack-codes-and-actionable-guidance)
      - [M3: Email Service Failure Handling NOT Specified](#m3-email-service-failure-handling-not-specified)
      - [M4: Timezone Handling for Edge Cases NOT Addressed](#m4-timezone-handling-for-edge-cases-not-addressed)
      - [M5: User Enumeration Prevention Incomplete](#m5-user-enumeration-prevention-incomplete)
      - [M6: Password History Mechanism NOT TESTED](#m6-password-history-mechanism-not-tested)
      - [M7: 2FA Backup Codes NOT Implemented](#m7-2fa-backup-codes-not-implemented)
      - [M8: JWT Token Payload Structure NOT Specified](#m8-jwt-token-payload-structure-not-specified)
    - [Testing and Documentation](#testing-and-documentation)
      - [M9: Error Response Format Standard Missing](#m9-error-response-format-standard-missing)
      - [M10: Performance Benchmarking Methodology NOT Detailed](#m10-performance-benchmarking-methodology-not-detailed)
  - [Low Priority Issues (Consider Fixing)](#low-priority-issues-consider-fixing)
    - [L1: No Visual Flow Diagrams in Documentation](#l1-no-visual-flow-diagrams-in-documentation)
    - [L2: No Health Check Endpoint for Authentication Services](#l2-no-health-check-endpoint-for-authentication-services)
    - [L3: Audit Log Metadata Not Validated](#l3-audit-log-metadata-not-validated)
  - [Edge Cases and Design Gaps](#edge-cases-and-design-gaps)
    - [User Registration Edge Cases](#user-registration-edge-cases)
      - [E1: Simultaneous Registration with Same Email](#e1-simultaneous-registration-with-same-email)
      - [E2: Organisation Does Not Exist at Registration Time](#e2-organisation-does-not-exist-at-registration-time)
      - [E3: Email Verification Token Expires During Registration](#e3-email-verification-token-expires-during-registration)
      - [E4: User Account Created But Email Service Fails](#e4-user-account-created-but-email-service-fails)
    - [Organisation Edge Cases](#organisation-edge-cases)
      - [E5: Organisation Deactivated During Active Sessions](#e5-organisation-deactivated-during-active-sessions)
      - [E6: Organisation Deleted with Active Users](#e6-organisation-deleted-with-active-users)
      - [E7: First User in Organisation Becomes Owner](#e7-first-user-in-organisation-becomes-owner)
      - [E8: Organisation Slug Conflicts](#e8-organisation-slug-conflicts)
    - [Token and Session Management](#token-and-session-management)
      - [E9: Token Used Exactly at Expiration Timestamp](#e9-token-used-exactly-at-expiration-timestamp)
      - [E10: Multiple Token Verification Attempts in Parallel](#e10-multiple-token-verification-attempts-in-parallel)
      - [E11: Token Reuse After Marked as Used](#e11-token-reuse-after-marked-as-used)
      - [E12: Clock Skew Between Servers](#e12-clock-skew-between-servers)
      - [E13: Token Expiration During Request](#e13-token-expiration-during-request)
      - [E14: Concurrent Session Limit Enforcement](#e14-concurrent-session-limit-enforcement)
      - [E15: Token Expiration During Multi-Step Operation](#e15-token-expiration-during-multi-step-operation)
    - [Two-Factor Authentication](#two-factor-authentication)
      - [E16: TOTP Device Loss and Recovery](#e16-totp-device-loss-and-recovery)
      - [E17: 2FA Device Verification Before Enabling](#e17-2fa-device-verification-before-enabling)
      - [E18: Session Fixation to Bypass 2FA](#e18-session-fixation-to-bypass-2fa)
      - [E19: 2FA Code Reuse Attack](#e19-2fa-code-reuse-attack)
      - [E20: Disable 2FA Without Verification](#e20-disable-2fa-without-verification)
    - [Email and Communication](#email-and-communication)
      - [E21: Registration Email Bombing](#e21-registration-email-bombing)
      - [E22: Password Reset Email Bombing](#e22-password-reset-email-bombing)
      - [E23: Email Verification Resend Abuse](#e23-email-verification-resend-abuse)
      - [E24: Disposable Email Addresses](#e24-disposable-email-addresses)
      - [E25: Email Format Edge Cases](#e25-email-format-edge-cases)
    - [Time Boundaries and Timezone Issues](#time-boundaries-and-timezone-issues)
      - [E26: User in Different Timezone Than Server](#e26-user-in-different-timezone-than-server)
      - [E27: Daylight Saving Time Transitions](#e27-daylight-saving-time-transitions)
      - [E28: Leap Second Handling](#e28-leap-second-handling)
      - [E29: System Clock Changes](#e29-system-clock-changes)
      - [E30: Token Expiration During System Maintenance](#e30-token-expiration-during-system-maintenance)
  - [Error Handling and Validation](#error-handling-and-validation)
    - [Database Error Handling](#database-error-handling)
    - [GraphQL Error Handling](#graphql-error-handling)
    - [Validation Error Standards](#validation-error-standards)
    - [Service Layer Error Handling](#service-layer-error-handling)
  - [Race Conditions and Concurrency](#race-conditions-and-concurrency)
    - [User Creation Race Conditions](#user-creation-race-conditions)
    - [Token Generation Race Conditions](#token-generation-race-conditions)
      - [JWT Token Hash Collision](#jwt-token-hash-collision)
      - [Refresh Token Rotation Race](#refresh-token-rotation-race)
    - [Database Transaction Issues](#database-transaction-issues)
      - [Lost Update Problem](#lost-update-problem)
      - [Read Committed Isolation Level](#read-committed-isolation-level)
      - [Serialisation Anomalies](#serialisation-anomalies)
    - [Redis Concurrency](#redis-concurrency)
      - [Redis Key Expiration Race Condition](#redis-key-expiration-race-condition)
    - [Session Management Concurrency](#session-management-concurrency)
      - [Concurrent Login from Same User](#concurrent-login-from-same-user)
      - [Session Limit Enforcement Race Condition](#session-limit-enforcement-race-condition)
  - [Boundary Conditions](#boundary-conditions)
    - [String Length Boundaries](#string-length-boundaries)
    - [Numeric Boundaries](#numeric-boundaries)
    - [Collection Size Boundaries](#collection-size-boundaries)
  - [Invalid Input and Security Testing](#invalid-input-and-security-testing)
    - [Malicious Input Scenarios](#malicious-input-scenarios)
      - [SQL Injection in GraphQL Variables](#sql-injection-in-graphql-variables)
      - [NoSQL Injection in Metadata JSON](#nosql-injection-in-metadata-json)
      - [GraphQL Injection](#graphql-injection)
      - [Command Injection in User Agent](#command-injection-in-user-agent)
    - [Unicode and Encoding Issues](#unicode-and-encoding-issues)
    - [GraphQL Input Validation](#graphql-input-validation)
  - [Test Coverage Analysis](#test-coverage-analysis)
    - [Current Test Coverage](#current-test-coverage)
    - [Test Coverage Gaps](#test-coverage-gaps)
    - [Test Coverage Summary](#test-coverage-summary)
  - [Security Vulnerabilities Summary](#security-vulnerabilities-summary)
    - [Authentication \& Authorisation](#authentication--authorisation)
    - [Token Management](#token-management)
    - [Data Protection](#data-protection)
    - [Email and Rate Limiting](#email-and-rate-limiting)
  - [Performance Concerns](#performance-concerns)
  - [Best Practices Compliance](#best-practices-compliance)
    - [Security Best Practices](#security-best-practices)
    - [Django Best Practices](#django-best-practices)
    - [GraphQL Best Practices](#graphql-best-practices)
  - [GDPR Compliance Analysis](#gdpr-compliance-analysis)
  - [User Experience Gaps](#user-experience-gaps)
    - [Device Management](#device-management)
    - [Account Recovery](#account-recovery)
    - [Error Messages](#error-messages)
  - [Recommendations](#recommendations)
    - [Immediate Actions (Before Implementation)](#immediate-actions-before-implementation)
    - [High Priority (Before Production)](#high-priority-before-production)
    - [During Implementation](#during-implementation)
    - [Medium Priority (Before Production)](#medium-priority-before-production)
    - [Testing Requirements](#testing-requirements)
  - [Phase 1 Completion Checklist](#phase-1-completion-checklist)
  - [Recommended Implementation Order](#recommended-implementation-order)
    - [Week 1: Foundation \& Service Layer](#week-1-foundation--service-layer)
    - [Week 2: GraphQL Mutations \& CSRF Protection](#week-2-graphql-mutations--csrf-protection)
    - [Week 3: Email Workflows](#week-3-email-workflows)
    - [Week 4: Two-Factor Authentication](#week-4-two-factor-authentication)
    - [Week 5: Security Features](#week-5-security-features)
    - [Week 6: Database Optimisation](#week-6-database-optimisation)
    - [Week 7: IP Encryption Key Rotation](#week-7-ip-encryption-key-rotation)
    - [Week 8: Testing \& QA](#week-8-testing--qa)
    - [Week 9: GDPR \& Documentation](#week-9-gdpr--documentation)
    - [Week 10: Final QA \& Hardening](#week-10-final-qa--hardening)
  - [Handoff Signals](#handoff-signals)
  - [Conclusion](#conclusion)
    - [Key Findings](#key-findings)
    - [Overall Status](#overall-status)
    - [Recommended Next Steps](#recommended-next-steps)
    - [Estimated Timeline](#estimated-timeline)

---

## Executive Summary

After comprehensive analysis of the User Authentication System (US-001), covering both Phase 1 (Models) and Phase 2 (Service Layer) implementations, the project has **progressed significantly but retains critical security vulnerabilities** that must be addressed before Phase 3 (GraphQL API).

### Phase 1 Assessment (Models) - COMPLETED ✅

- **Status**: Models fully implemented and tested
- **Models Implemented**: 11/11 (100%)
- **Test Coverage**: ~90% (comprehensive unit tests)
- **Critical Issues from Plan**: Addressed in Phase 2 design
- **Overall**: ✅ **READY FOR PHASE 2**

### Phase 2 Assessment (Service Layer) - IMPLEMENTED WITH ISSUES ⚠️

- **Status**: Service layer implemented but with **7 critical security issues**
- **Services Implemented**: 6/7 (EmailVerificationService missing)
- **Test Coverage**: 90%+ unit tests (330/330 passing), 0% integration tests
- **Critical Issues**: 7 blocking deployment
- **Security Vulnerabilities**: 4 active vulnerabilities discovered
- **Overall**: ⚠️ **NOT READY FOR PHASE 3 OR DEPLOYMENT**

### Phase 2 Implementation Status

| Component                   | Status             | Test Results | Issues                                     |
| --------------------------- | ------------------ | ------------ | ------------------------------------------ |
| IP Encryption               | ✅ IMPLEMENTED     | ✅ PASSING   | Management command not implemented         |
| Token Hashing (HMAC-SHA256) | ✅ IMPLEMENTED     | ✅ PASSING   | No key strength validation                 |
| Token Service               | ⚠️ PARTIAL         | ✅ PASSING   | Race condition in family update            |
| Authentication Service      | ⚠️ PARTIAL         | ✅ PASSING   | No race condition prevention, timing attack |
| Password Reset Service      | ✅ IMPLEMENTED     | ✅ PASSING   | Wrong token expiry (1h vs 15m)             |
| Email Service               | ❌ STUB ONLY       | ✅ PASSING   | Returns true without sending emails        |
| Audit Service               | ✅ IMPLEMENTED     | ✅ PASSING   | Not integrated into auth flows             |
| EmailVerificationService    | ❌ NOT CREATED     | N/A          | Missing entirely                           |
| Management Commands         | ❌ NOT IMPLEMENTED | N/A          | rotate_ip_keys raises NotImplementedError  |

### Test Results Summary (08/01/2026)

```
Total Tests: 330/330 PASSING ✅
- Unit Tests (Phase 1 Models): 250+ tests passing
- Unit Tests (Phase 2 Services): 80+ tests passing
- Integration Tests: 0 (NOT WRITTEN)
- E2E Tests: 0 (NOT WRITTEN)
- Coverage: ~90% (unit tests only)
```

### Critical Issues Discovered in Phase 2

**7 Critical Blockers**:

1. **C1**: Management command `rotate_ip_keys` not implemented (raises NotImplementedError)
2. **C2**: Race condition in user registration (no database locking)
3. **C3**: EmailVerificationService missing entirely
4. **C4**: Token family not maintained correctly in refresh flow (race condition)
5. **C5**: Email service returns True without sending emails (stub only)
6. **C6**: User enumeration via error messages (privacy/GDPR violation)
7. **C7**: Account lockout not implemented (brute-force vulnerability)

**4 Active Security Vulnerabilities**:

1. **SV1**: Timing attack in login flow (can enumerate users via response time)
2. **SV2**: User enumeration via registration error messages
3. **SV3**: Token family race condition enables replay attack bypass
4. **SV4**: IP encryption key not validated on startup

### Overall Project Status

| Phase                | Status                                      |
| -------------------- | ------------------------------------------- |
| Planning             | ✅ Complete with known gaps                 |
| Phase 1 (Models)     | ✅ COMPLETE (11/11 models, 90%+ test coverage) |
| Phase 2 (Services)   | ⚠️ 60% COMPLETE (7 critical issues)         |
| Phase 3 (GraphQL)    | ❌ BLOCKED (waiting on Phase 2 fixes)       |
| Phase 4 (2FA)        | ❌ NOT STARTED                              |
| Phase 5 (Email)      | ❌ NOT STARTED                              |
| Production Readiness | 🔴 **NOT READY** (multiple critical blockers) |

---

## Overall Assessment

| Area                 | Plan Review            | Implementation     | Combined Status  |
| -------------------- | ---------------------- | ------------------ | ---------------- |
| Security Design      | ❌ UNSAFE              | ❌ VULNERABLE      | **🔴 NOT READY** |
| Core Models          | ✅ GOOD                | ✅ IMPLEMENTED     | ✅ GOOD          |
| Service Layer        | ⚠️ PARTIALLY SPECIFIED | ❌ NOT IMPLEMENTED | **🔴 CRITICAL**  |
| GraphQL API          | ⚠️ SPECIFIED           | ❌ NOT IMPLEMENTED | **🔴 CRITICAL**  |
| Authentication Flows | ❌ GAPS IDENTIFIED     | ❌ NOT IMPLEMENTED | **🔴 CRITICAL**  |
| Testing              | ⚠️ SPECIFIED           | ⚠️ MODELS ONLY     | **⚠️ HIGH RISK** |
| Security Features    | ❌ INCOMPLETE SPEC     | ❌ INCOMPLETE IMPL | **🔴 CRITICAL**  |

**Key Statistics**:

- **Deployment Blockers**: 15 Critical Issues from implementation + 6 Critical from plan = **21 total**
- **Must-Fix Before Production**: 8 high-priority issues (implementation) + 8 high-priority issues (plan) = **16 total**
- **Should Fix Before Production**: 8 medium-priority issues
- **Overall Assessment**: ⚠️ **NOT READY FOR IMPLEMENTATION OR DEPLOYMENT**

---

## Critical Issues (Blocks Deployment)

### Phase 2 Service Layer Critical Issues (NEW)

The following critical issues were discovered during Phase 2 (Service Layer) implementation and must be fixed before proceeding to Phase 3.

#### P2-C1: CRITICAL - Management Command Not Implemented

**Severity**: CRITICAL
**Location**: `apps/core/management/commands/rotate_ip_keys.py`
**Phase**: Phase 2
**Status**: ❌ NOT IMPLEMENTED

**Issue**: The `rotate_ip_keys` management command raises `NotImplementedError` in both `add_arguments()` and `handle()` methods.

**Code**:

```python
def add_arguments(self, parser):
    raise NotImplementedError(
        "Command.add_arguments() not implemented - TDD red phase"
    )

def handle(self, *args, **options):
    raise NotImplementedError("Command.handle() not implemented - TDD red phase")
```

**Impact**: IP encryption key rotation cannot be performed, violating C6 security requirement. If encryption key is compromised, all historical IP addresses in audit logs remain exposed permanently with no recovery path.

**Recommendation**: Implement management command with `--dry-run`, `--backup`, progress reporting, and rollback mechanism.

---

#### P2-C2: CRITICAL - Race Condition in User Registration

**Severity**: CRITICAL
**Location**: `apps/core/services/auth_service.py:75-77`
**Phase**: Phase 2
**Status**: ⚠️ VULNERABLE

**Issue**: User registration checks for duplicate email without database locking. Two concurrent registrations with the same email can both pass the check and create duplicate users or trigger database errors.

**Code**:

```python
# Check if email already exists
if User.objects.filter(email=email).exists():
    raise ValueError(f"Email address {email} is already registered")
# Race window here - no lock prevents concurrent registration
```

**Impact**: Database integrity violation, potential duplicate users, or registration failures under concurrent load.

**Recommendation**: Use `select_for_update()` within transaction to acquire row lock before checking email existence.

---

#### P2-C3: CRITICAL - EmailVerificationService Missing

**Severity**: CRITICAL
**Location**: Missing file - should be `apps/core/services/email_verification_service.py`
**Phase**: Phase 2
**Status**: ❌ NOT CREATED

**Issue**: Phase 2 plan requires email verification service, but no service exists. Email verification tokens can be created via model but there's no service layer for the verification workflow.

**Missing Functionality**:

- Create verification token
- Send verification email
- Verify token and mark email as verified
- Resend verification email with cooldown (5 minutes)
- Single-use token enforcement

**Impact**: Users cannot verify email addresses, blocking C5 requirement (email verification enforcement on login). Phase 3 GraphQL mutations will have no backend to call.

**Recommendation**: Create `EmailVerificationService` following same pattern as `PasswordResetService`.

---

#### P2-C4: CRITICAL - Token Family Race Condition

**Severity**: CRITICAL
**Location**: `apps/core/services/token_service.py:159-164`
**Phase**: Phase 2
**Status**: ⚠️ RACE CONDITION

**Issue**: Token family update in refresh flow doesn't use database locking, creating race condition that breaks replay detection.

**Code**:

```python
# Update token family to maintain chain
new_session = SessionToken.objects.get(
    refresh_token_hash=TokenHasher.hash_token(new_tokens['refresh_token'])
)
new_session.token_family = session_token.token_family
new_session.save(update_fields=['token_family'])
```

**Problem**: No transaction wrapping, no `select_for_update()`, no verification family was updated.

**Impact**: Broken token family chain means replay detection (H9) doesn't work correctly. Stolen refresh tokens can potentially be reused.

**Recommendation**: Wrap in transaction with `select_for_update()` and verify family update succeeded.

---

#### P2-C5: CRITICAL - Email Service Stub Only

**Severity**: CRITICAL
**Location**: `apps/core/services/email_service.py`
**Phase**: Phase 2
**Status**: ❌ STUB ONLY

**Issue**: All email service methods return `True` without actually sending emails. Documentation says "For Phase 2, return True to satisfy tests" but this creates false sense of completion.

**Impact**:

- Password reset emails not sent
- Verification emails not sent
- Users cannot recover accounts
- Tests pass but functionality broken
- Moving to Phase 3 with broken email flow

**Recommendation**: Either implement basic SMTP/Mailpit email sending OR make methods raise `NotImplementedError` so it's clear functionality is missing.

---

#### P2-C6: CRITICAL - User Enumeration via Error Messages

**Severity**: CRITICAL
**Location**: `apps/core/services/auth_service.py`, multiple methods
**Phase**: Phase 2
**Status**: ⚠️ PRIVACY VIOLATION

**Issue**: Error messages reveal whether email addresses exist in system.

**Vulnerable Code**:

```python
# Registration - reveals email exists
if User.objects.filter(email=email).exists():
    raise ValueError(f"Email address {email} is already registered")

# Login - distinguishes non-existent user from wrong password
except User.DoesNotExist:
    return None  # Different from password check failure
```

**Impact**: Privacy violation, GDPR non-compliance, enables targeted phishing attacks.

**Recommendation**: Use generic error messages that don't reveal account existence.

---

#### P2-C7: CRITICAL - Account Lockout Not Implemented

**Severity**: CRITICAL
**Location**: `apps/core/services/auth_service.py:207-218`
**Phase**: Phase 2
**Status**: ❌ STUB ONLY

**Issue**: Account lockout methods are stubs that always return False / do nothing.

**Code**:

```python
@staticmethod
def check_account_lockout(user: User) -> bool:
    # For Phase 2, always return False
    return False
```

**Impact**: No protection against brute-force password attacks. Attackers can attempt unlimited login attempts.

**Recommendation**: Implement basic lockout with Redis tracking of failed attempts.

---

### Phase 2 Security Vulnerabilities (New - Implementation Analysis)

The following security vulnerabilities were discovered during Phase 2 (Service Layer) implementation analysis on 08/01/2026.

#### P2-SV1: Email Verification Bypass in Login Flow

**Severity**: 🔴 CRITICAL
**Location**: `apps/core/services/auth_service.py:96-140`
**Phase**: Phase 2
**Status**: ⚠️ VULNERABLE
**Requirement Violated**: C5 (Email Verification Enforcement)

**Issue**: The `AuthService.login()` method does NOT verify `user.email_verified` before issuing authentication tokens. Users can authenticate with unverified email addresses, violating security requirement C5.

**Code Analysis**:

```python
# apps/core/services/auth_service.py:96-140
def login(email: str, password: str, ...) -> Optional[Dict[str, any]]:
    with transaction.atomic():
        try:
            user = User.objects.select_for_update().get(email=email)
        except User.DoesNotExist:
            return None

        if not user.check_password(password):
            return None

        # ❌ MISSING: if not user.email_verified: return None

        tokens = TokenService.create_tokens(user, device_fingerprint)
        return {'user': user, 'access_token': ..., ...}
```

**Impact**:
- Account takeover via email typos (user registers wrong email, real owner verifies, both can login)
- GDPR compliance violation (unverified contact information)
- Phishing vulnerability (attacker registers victim's email, victim never verifies, attacker logs in)

**Exploit Scenario**:
1. Attacker registers account with `victim@company.com` (typo for `victim@company.co`)
2. Verification email sent to wrong address
3. Attacker immediately logs in **WITHOUT** email verification
4. Account active with unverified/incorrect email

**Fix Required**:

```python
def login(email: str, password: str, ...) -> Optional[Dict[str, any]]:
    # ... existing code ...

    if not user.check_password(password):
        return None

    # ✅ ADD EMAIL VERIFICATION CHECK:
    if not user.email_verified:
        raise ValueError(
            "EMAIL_NOT_VERIFIED",
            "Please verify your email address before logging in. "
            "Check your inbox for the verification link."
        )

    # Check lockout, create tokens...
```

**Test Required**:
- Unit test: Login with unverified email should fail
- Integration test: Register → Attempt login (should fail) → Verify email → Login (should succeed)

---

#### P2-SV2: Account Lockout Mechanism Bypassed (Stub Implementation)

**Severity**: 🔴 CRITICAL
**Location**: `apps/core/services/auth_service.py:206-218`
**Phase**: Phase 2
**Status**: ❌ NOT IMPLEMENTED
**Requirement Violated**: H13 (Account Lockout)

**Issue**: `check_account_lockout()` and `unlock_account()` are stub implementations that always return `False` / do nothing, allowing unlimited brute-force login attempts.

**Code Analysis**:

```python
@staticmethod
def check_account_lockout(user: User) -> bool:
    """Check if user account is locked due to failed login attempts."""
    # For Phase 2, always return False
    # Full lockout implementation will be in Phase 6
    return False  # ❌ ALWAYS ALLOWS LOGIN

@staticmethod
def unlock_account(user: User) -> None:
    """Unlock user account (admin action or timeout)."""
    # For Phase 2, do nothing
    pass  # ❌ NO-OP
```

**Impact**:
- Unlimited brute-force password attempts
- Credential stuffing attacks enabled
- No protection against dictionary attacks
- Violates security best practices (OWASP, NIST)

**Exploit Scenario**:
1. Attacker obtains user email from data breach
2. Attempts 10,000 common passwords
3. **No lockout occurs** - all attempts processed
4. Eventually guesses password or causes DoS

**Fix Required**:

```python
from django.core.cache import cache

@staticmethod
def check_account_lockout(user: User) -> bool:
    """Check if user account is locked due to failed login attempts."""
    cache_key = f"failed_login_attempts:{user.id}"
    failed_attempts = cache.get(cache_key, 0)

    # Lock after 10 failed attempts
    if failed_attempts >= 10:
        return True

    return False

@staticmethod
def record_failed_login(user: User) -> None:
    """Record failed login attempt."""
    cache_key = f"failed_login_attempts:{user.id}"
    attempts = cache.get(cache_key, 0) + 1
    cache.set(cache_key, attempts, timeout=3600)  # 1 hour window
```

**Test Required**:
- Unit test: 10 failed logins → account locked
- Unit test: Lockout expires after 1 hour
- Integration test: Locked account rejects correct password

---

#### P2-SV3: Concurrent Session Limit Not Enforced

**Severity**: 🔴 CRITICAL
**Location**: `apps/core/services/token_service.py:46-86`
**Phase**: Phase 2
**Status**: ⚠️ VULNERABLE
**Requirement Violated**: H12 (Concurrent Session Limit)

**Issue**: `create_tokens()` does NOT enforce maximum concurrent session limit. Users can create unlimited active sessions, increasing risk of session hijacking.

**Code Analysis**:

```python
def create_tokens(user: User, device_fingerprint: str = "") -> Dict[str, str]:
    # ❌ NO CHECK for existing session count

    # Generate tokens...
    SessionToken.objects.create(
        user=user,
        # ... creates unlimited sessions
    )

    return {'access_token': ..., 'refresh_token': ..., 'family_id': ...}
```

**Impact**:
- Stolen/leaked tokens remain valid indefinitely
- Difficult to detect account compromise
- Session hijacking detection impossible
- Violates security requirement H12 (max 5 concurrent sessions)

**Exploit Scenario**:
1. Attacker steals user's session token via XSS/phishing
2. User continues using account normally (doesn't notice)
3. Attacker maintains access for 30 days (token expiry)
4. No session limit alerts user or administrators

**Fix Required**:

```python
@staticmethod
def create_tokens(user: User, device_fingerprint: str = "") -> Dict[str, str]:
    MAX_CONCURRENT_SESSIONS = 5

    # Count active sessions
    active_sessions = SessionToken.objects.filter(
        user=user,
        is_revoked=False,
        expires_at__gt=timezone.now()
    ).count()

    # Revoke oldest session if limit reached
    if active_sessions >= MAX_CONCURRENT_SESSIONS:
        oldest = SessionToken.objects.filter(
            user=user,
            is_revoked=False
        ).order_by('created_at').first()

        if oldest:
            oldest.revoke()

    # Generate new tokens...
```

**Test Required**:
- Unit test: 6th session creation revokes oldest
- Integration test: User can see active sessions and logout specific device

---

#### P2-SV4: Rate Limiting Not Implemented (DoS Vulnerability)

**Severity**: 🔴 CRITICAL
**Location**: All authentication service methods
**Phase**: Phase 2
**Status**: ❌ NOT IMPLEMENTED
**Requirement Violated**: System-wide security requirement

**Issue**: **NO RATE LIMITING** implemented at service layer for authentication operations. This enables:
- Brute-force attacks on login
- Email bombing via password reset
- Resource exhaustion via token generation
- Distributed Denial of Service (DDoS)

**Impact**:
- Service can be overwhelmed with authentication requests
- Email service abuse (password reset bombing)
- Database connection pool exhaustion
- Application-level DoS vulnerability

**Exploit Scenarios**:

1. **Login Brute Force**: 1000 req/sec → server overload
2. **Email Bombing**: Reset password for 1000 users/sec → mail server blacklisted
3. **Token Generation**: Create 10000 tokens/sec → database locks
4. **Registration Spam**: Register 1000 accounts/sec → database bloat

**Fix Required**:

```python
from functools import wraps
from django.core.cache import cache

def rate_limit(key_prefix: str, limit: int, period: int):
    """Rate limiting decorator."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            identifier = kwargs.get('email') or kwargs.get('ip_address', 'unknown')
            cache_key = f"rate_limit:{key_prefix}:{identifier}"

            attempts = cache.get(cache_key, 0)
            if attempts >= limit:
                raise ValueError(
                    f"RATE_LIMIT_EXCEEDED",
                    f"Too many requests. Try again in {period // 60} minutes."
                )

            cache.set(cache_key, attempts + 1, period)
            return func(*args, **kwargs)

        return wrapper
    return decorator

# Usage:
@rate_limit('login', limit=5, period=300)  # 5 attempts per 5 minutes
def login(email: str, password: str, ...) -> Optional[Dict]:
    ...

@rate_limit('password_reset', limit=3, period=3600)  # 3 per hour
def create_reset_token(user: User, ...) -> str:
    ...
```

**Test Required**:
- Unit test: 6th login attempt within 5 minutes should fail with rate limit error
- Unit test: Rate limit resets after timeout period
- Integration test: Rate limiting per IP address

---

#### P2-SV5: Password History Not Enforced

**Severity**: 🟠 HIGH
**Location**: `apps/core/services/auth_service.py:170-204`, `apps/core/services/password_reset_service.py:111-157`
**Phase**: Phase 2
**Status**: ⚠️ VULNERABLE
**Requirement Violated**: H11 (Password History)

**Issue**: Neither `change_password()` nor `reset_password()` check password history. Users can immediately reuse old passwords, violating requirement H11 (prevent reuse of last 5 passwords).

**Code Analysis**:

```python
# auth_service.py:170-204
def change_password(user: User, old_password: str, new_password: str) -> bool:
    # Verify old password...
    # Validate new password...

    # ❌ NO PASSWORD HISTORY CHECK

    user.set_password(new_password)
    user.save()
    return True
```

**Impact**:
- Users rotate through same 2-3 passwords
- Forced password changes become ineffective
- Compliance violations (PCI-DSS requires password history)
- Security incident response compromised

**Exploit Scenario**:
1. User's password compromised in breach
2. Security team forces password reset
3. User changes password to `Password123!` → `Password456!`
4. User immediately changes back to `Password123!`
5. Compromised password remains active

**Fix Required**:

Create `PasswordHistory` model:

```python
# models.py
class PasswordHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['user', '-created_at'])]

# auth_service.py
def change_password(user: User, old_password: str, new_password: str) -> bool:
    # Verify old password...

    # ✅ CHECK PASSWORD HISTORY:
    history = PasswordHistory.objects.filter(user=user).order_by('-created_at')[:5]

    for old_hash in history:
        temp_user = User()
        temp_user.password = old_hash.password_hash
        if temp_user.check_password(new_password):
            raise ValueError(
                "PASSWORD_REUSE_ERROR",
                "Cannot reuse any of your last 5 passwords. "
                "Please choose a different password."
            )

    # Set password...
    user.set_password(new_password)
    user.save()

    # Add to history
    PasswordHistory.objects.create(user=user, password_hash=user.password)

    # Keep only last 5
    PasswordHistory.objects.filter(user=user).exclude(
        id__in=history.values_list('id', flat=True)[:5]
    ).delete()

    return True
```

**Test Required**:
- Unit test: Reusing password from last 5 should fail
- Unit test: 6th password allows reuse of 1st password
- Migration: Create PasswordHistory model

---

#### P2-SV6: Logout Does Not Revoke Token (Session Persistence Vulnerability)

**Severity**: 🟠 HIGH
**Location**: `apps/core/services/auth_service.py:142-156`
**Phase**: Phase 2
**Status**: ❌ STUB ONLY
**Requirement Violated**: H10 (Logout Token Revocation)

**Issue**: `logout()` method is a stub that always returns `True` without actually revoking the session token. This means tokens remain valid after "logout", making logout purely client-side.

**Code Analysis**:

```python
@staticmethod
def logout(user: User, token: str) -> bool:
    """Logout user and revoke session token."""
    # For Phase 2, always return True
    # Full implementation will revoke specific token
    return True  # ❌ TOKEN NOT REVOKED
```

**Impact**:
- Tokens remain valid for 30 days after "logout"
- Stolen tokens can be used after user logs out
- Logout provides **FALSE SENSE OF SECURITY**
- Violates security requirement H10

**Exploit Scenario**:
1. User logs in from public/shared computer
2. User clicks "Logout" (believes session ended)
3. Attacker uses same computer, finds cached/stolen token
4. **Token still valid** - attacker gains access for 30 days

**Fix Required**:

```python
from apps.core.utils.token_hasher import TokenHasher
from apps.core.models import SessionToken

@staticmethod
def logout(user: User, token: str) -> bool:
    """Logout user and revoke session token."""
    # Hash token to find it
    token_hash = TokenHasher.hash_token(token)

    try:
        session_token = SessionToken.objects.get(
            user=user,
            token_hash=token_hash
        )

        # Revoke the token
        session_token.revoke()

        # Log logout event
        from apps.core.services.audit_service import AuditService
        AuditService.log_logout(user)

        return True

    except SessionToken.DoesNotExist:
        # Token not found (already revoked or invalid)
        return False
```

**Test Required**:
- Unit test: Logout revokes token
- Integration test: Logout → Verify token invalid → Login with same credentials works

---

#### P2-SV7: Missing Audit Logging for Authentication Events

**Severity**: 🟠 HIGH
**Location**: `apps/core/services/auth_service.py:96-140`
**Phase**: Phase 2
**Status**: ⚠️ PARTIAL
**Requirement Violated**: Audit logging requirement

**Issue**: `login()` method does NOT create audit logs for **failed login attempts** or **successful logins**. This prevents:
- Security monitoring and alerting
- Brute-force attack detection
- Forensic investigation after breach
- Account lockout mechanism implementation

**Code Analysis**:

```python
def login(email: str, password: str, ...) -> Optional[Dict]:
    try:
        user = User.objects.select_for_update().get(email=email)
    except User.DoesNotExist:
        # ❌ NO AUDIT LOG FOR USER NOT FOUND
        return None

    if not user.check_password(password):
        # ❌ NO AUDIT LOG FOR WRONG PASSWORD
        return None

    # Success - tokens created
    # ❌ NO SUCCESS AUDIT LOG EITHER
    return {'user': user, 'access_token': ..., ...}
```

**Impact**:
- Security incidents undetectable
- No forensic trail for investigations
- Compliance violations (PCI-DSS, HIPAA require audit logs)
- Account lockout cannot be implemented without failed attempt tracking

**Fix Required**:

```python
from apps.core.services.audit_service import AuditService

def login(email: str, password: str, ip_address: str = "", ...) -> Optional[Dict]:
    try:
        user = User.objects.select_for_update().get(email=email)
    except User.DoesNotExist:
        # ✅ LOG FAILED ATTEMPT (user not found)
        AuditService.log_login_failed(
            email=email,
            ip_address=ip_address,
            device_fingerprint=device_fingerprint
        )
        return None

    if not user.check_password(password):
        # ✅ LOG FAILED ATTEMPT (wrong password)
        AuditService.log_login_failed(
            email=email,
            ip_address=ip_address,
            device_fingerprint=device_fingerprint,
            organisation=user.organisation
        )
        return None

    # ✅ LOG SUCCESSFUL LOGIN
    AuditService.log_login(
        user=user,
        ip_address=ip_address,
        device_fingerprint=device_fingerprint
    )

    tokens = TokenService.create_tokens(user, device_fingerprint)
    return {'user': user, ...}
```

**Test Required**:
- Unit test: Failed login creates audit log
- Unit test: Successful login creates audit log
- Integration test: Query audit logs for user

---

#### P2-SV8: Token Service Missing IP Address Storage

**Severity**: 🟠 HIGH
**Location**: `apps/core/services/token_service.py:46-86`
**Phase**: Phase 2
**Status**: ⚠️ MISSING FEATURE

**Issue**: `create_tokens()` accepts `device_fingerprint` but does NOT accept or store IP address. This prevents:
- IP-based session validation
- Geographic anomaly detection
- Forensic investigation after breach

**Code Analysis**:

```python
def create_tokens(user: User, device_fingerprint: str = "") -> Dict[str, str]:
    # ❌ NO IP ADDRESS PARAMETER

    SessionToken.objects.create(
        user=user,
        device_fingerprint=device_fingerprint,
        # ❌ ip_address NOT SET (column exists in model but not populated)
    )
```

**Impact**:
- Cannot detect session hijacking via IP change
- Cannot implement geographic login alerts
- Cannot block sessions from suspicious IPs
- Forensic investigation limited

**Fix Required**:

```python
from apps.core.utils.encryption import IPEncryption

def create_tokens(
    user: User,
    device_fingerprint: str = "",
    ip_address: str = ""  # ✅ ADD IP PARAMETER
) -> Dict[str, str]:
    # Encrypt IP if provided
    encrypted_ip = None
    if ip_address:
        encrypted_ip = IPEncryption.encrypt_ip(ip_address)

    SessionToken.objects.create(
        user=user,
        device_fingerprint=device_fingerprint,
        ip_address=encrypted_ip,  # ✅ STORE ENCRYPTED IP
        ...
    )
```

**Test Required**:
- Unit test: Session token stores encrypted IP
- Integration test: IP change detection alert

---

### Phase 1 Security Vulnerabilities (From Plan Review)

#### 1. Session Token Storage Vulnerability

**Severity**: CRITICAL
**Location**: `SessionToken` model + BaseToken implementation

**Issue**: Session tokens stored with HMAC-SHA256 hashing, but if database is accessed, tokens remain vulnerable to rainbow table attacks without additional key derivation.

**Impact**: Session hijacking vulnerability - attackers with database access could crack JWT tokens.

**Current Implementation**:

```python
# apps/core/models/base_token.py:78
return hmac.new(key=settings.SECRET_KEY.encode(), ...)
```

**Plan Violation**: Tokens should use dedicated TOKEN_SIGNING_KEY, not SECRET_KEY.

**Recommendation**: Use HMAC-SHA256 with dedicated secure key, store as binary for additional entropy.

---

#### 2. TOTP Secret Storage Security

**Severity**: CRITICAL
**Location**: `TOTPDevice` model

**Issue**: TOTP secrets encrypted with Fernet, but encryption method and key management not fully specified. Key rotation mechanism missing.

**Impact**: If TOTP encryption key is compromised, all 2FA secrets exposed, allowing attackers to generate valid codes indefinitely.

**Missing Implementation**:

- Key rotation mechanism
- Key versioning
- Separate encryption key from IP encryption key

---

#### 3. Password Reset Token Not Hashed

**Severity**: CRITICAL
**Location**: `PasswordResetToken` model

**Issue**: While plan specifies tokens should be hashed, implementation details unclear. Plain token storage in database exposes all active password reset links.

**Impact**: Database breach = all active password reset tokens compromised, enabling account takeover.

**Requirement**: Hash tokens using SHA-256, store hash in database, compare on reset attempt.

---

#### 4. CSRF Protection for GraphQL NOT Implemented

**Severity**: CRITICAL
**Location**: `api/schema.py`, `config/settings/base.py`

**Status**: Plan specifies CSRF middleware for GraphQL mutations, but **NOT IMPLEMENTED** in code.

**Impact**: Attackers can trick authenticated users into executing unwanted mutations (logout, disable 2FA, change password) without their knowledge.

**Missing**:

- `GraphQLCSRFMiddleware` class
- CSRF token validation for mutations
- CSRF token in GraphQL client requests
- Integration tests for CSRF protection

---

#### 5. Email Verification Not Enforced on Login

**Severity**: CRITICAL
**Location**: Missing login workflow

**Status**: `User.email_verified` field exists (✅), but login flow NOT IMPLEMENTED, so verification cannot be enforced.

**Impact**: Unverified users can access the system, enabling spam/bot registrations and resource exhaustion.

**Missing**:

- Login authentication service
- Verification check before token creation
- Error response for unverified users

---

#### 6. IP Encryption Key Rotation NOT Implemented

**Severity**: CRITICAL
**Location**: Missing management command

**Status**: Plan requires automated key rotation, but no implementation exists.

**Impact**: If IP encryption key compromised, all historical IP addresses in audit logs exposed permanently.

**Missing**:

- Key rotation management command
- Re-encryption of existing IPs with new key
- Key versioning system
- Automated quarterly rotation schedule

---

#### 7. TOKEN_SIGNING_KEY Not Configured in Environment Files

**Severity**: CRITICAL
**Location**: `.env.dev.example`, `.env.staging.example`, `.env.production.example`

**Status**: Environment variable NOT DEFINED, code falls back to using `SECRET_KEY`.

**Impact**: Token signing key not properly separated from application secret, violates security best practice.

**Issue**: Specification requires dedicated TOKEN_SIGNING_KEY but environment files don't define it.

**Recommendation**:

1. Add `TOKEN_SIGNING_KEY` to all `.env.*.example` files
2. Update `base_token.py` to use `settings.TOKEN_SIGNING_KEY`
3. Fail startup if TOKEN_SIGNING_KEY not set in production

---

### Missing Implementation Features

#### 8. No GraphQL Mutations for Authentication

**Severity**: CRITICAL
**Location**: `api/schema.py`

**Status**: Zero authentication mutations implemented. Users CANNOT:

- Register
- Login
- Logout
- Reset password
- Verify email
- Enable/disable 2FA

**Current State**:

```python
@strawberry.field
def placeholder(self) -> str:
    return "Mutations will be added here"
```

**Missing**: All 9 core mutations (register, login, logout, requestPasswordReset, resetPassword, verifyEmail, enable2FA, confirm2FA, disable2FA)

---

#### 9. No Authentication Service Layer

**Severity**: CRITICAL
**Location**: `apps/core/services/` (missing)

**Status**: Plan requires AuthenticationService, TokenService, EmailService but files NOT CREATED.

**Missing Files**:

- `apps/core/services/authentication_service.py` ❌
- `apps/core/services/token_service.py` ❌
- `apps/core/services/email_service.py` ❌

**Only Found**: `apps/core/services/permission_service.py` ✅

**Impact**: No business logic for authentication workflows. Implementation cannot proceed without service layer.

---

#### 10. Password Reset Workflow NOT Implemented

**Severity**: CRITICAL

**Status**: `PasswordResetToken` model exists, but workflow missing.

**Missing**:

- `requestPasswordReset` mutation
- Email sending for reset tokens
- `resetPassword` mutation
- Token validation and 1-hour expiry checks
- Single-use token enforcement

**Impact**: Users cannot reset forgotten passwords.

---

#### 11. Email Verification Workflow NOT Implemented

**Severity**: CRITICAL

**Status**: `EmailVerificationToken` model exists, but workflow missing.

**Missing**:

- Auto-generate verification token on registration
- Verification email sending
- `verifyEmail` mutation
- `resendVerificationEmail` mutation
- Update `email_verified` flag

**Impact**: Users cannot verify email addresses, blocking login access.

---

#### 12. 2FA Enrollment Workflow NOT Implemented

**Severity**: CRITICAL

**Status**: `TOTPDevice` model exists with encryption (✅), but workflow missing.

**Missing**:

- `enable2FA` mutation (returns QR code URI)
- `confirm2FA` mutation (verifies TOTP code)
- `disable2FA` mutation
- Backup codes generation and validation
- Session invalidation on 2FA enable

**Impact**: 2FA cannot be enabled by users.

---

#### 13. Login Flow with 2FA NOT Implemented

**Severity**: CRITICAL

**Status**: Two-step login flow missing entirely.

**Required Flow**:

1. User submits email/password
2. If 2FA enabled: Return `requires2FA: true` + temporary token
3. User submits TOTP token + temporary token
4. Validate TOTP, create session tokens

**Missing**: Entire 2FA login workflow.

---

#### 14. No Rate Limiting on Authentication Endpoints

**Severity**: CRITICAL

**Status**: Generic rate limiting middleware exists but NOT configured for auth endpoints.

**Missing Auth-Specific Limits**:

- Login: 5 attempts per 15 minutes per IP
- Registration: 3 attempts per hour per IP
- Password reset: 3 attempts per hour per email
- 2FA verification: 5 attempts per 15 minutes per user

**Impact**: Brute force attacks unprotected.

---

#### 15. Account Lockout Mechanism NOT Implemented

**Severity**: CRITICAL

**Status**: No failed login tracking or account lockout feature.

**Missing**:

- `failed_login_attempts` counter on User model
- `locked_until` timestamp
- Account unlock mechanism
- Lockout after 10 failed attempts within 1 hour
- Email notification on lockout

**Impact**: Persistent brute force attacks possible.

---

#### 16. No Concurrent Session Limit Enforcement

**Severity**: CRITICAL

**Status**: Plan specifies max 5 sessions per user, but enforcement NOT IMPLEMENTED.

**Missing**:

- Session count check during login
- Automatic oldest session revocation
- Configuration for `MAX_CONCURRENT_SESSIONS`

**Impact**: Attackers can create unlimited sessions for compromised account.

---

#### 17. No Token Revocation on Password Change

**Severity**: CRITICAL

**Status**: `SessionToken.revoke()` method exists (✅), but never called.

**Missing**:

- Signal handler or service method to revoke sessions on password change
- Clear all Redis cache for user sessions
- Audit log entry for token revocation

**Impact**: Stolen tokens remain valid after password change. User account still compromised after attempting to secure it.

---

### Configuration Issues

#### 18. GraphQL Introspection Enabled in Production

**Severity**: CRITICAL
**Location**: `api/security.py` + `config/settings/production.py`

**Status**: While `IntrospectionControlExtension` exists, production setting must be verified disabled.

**Risk**: Schema exposure in production allows attackers to discover all endpoints and vulnerabilities.

**Requirement**: Verify `GRAPHQL_INTROSPECTION_ENABLED = False` in production settings.

---

## High Priority Issues (Must Fix Before Production)

### Database and Query Optimisation

#### H1: Missing Composite Indexes for Multi-Tenant Queries

**Status**: Plan requires, implementation MISSING.

**Missing Composite Indexes**:

- `User`: `(organisation, is_active)`, `(organisation, created_at)`
- `AuditLog`: `(organisation, event_type, created_at)`
- `SessionToken`: `(user, is_revoked, expires_at)`

**Impact**: Slow queries on organisation-filtered data. Performance degrades with scale.

---

#### H2: Missing Indexes on Token Expiry Fields

**Status**: Plan requires, implementation MISSING.

**Missing Indexes**:

- `SessionToken.expires_at`
- `PasswordResetToken.expires_at`
- `EmailVerificationToken.expires_at`

**Impact**: Slow token validation queries, poor performance on cleanup operations.

---

#### H3: AuditLog Uses CASCADE Instead of SET_NULL

**Status**: Need to verify implementation.

**Requirement**: `AuditLog.organisation` should use `SET_NULL` to preserve logs when organisation deleted.

**Impact**: Audit trail loss violates compliance requirements.

---

### Security and Concurrency

#### H4: PostgreSQL Row-Level Security (RLS) NOT Configured

**Status**: Plan requires, implementation MISSING.

**Missing**:

- RLS policies for multi-tenancy enforcement at database level
- Migration to enable RLS on core tables

**Impact**: Database-level multi-tenancy not enforced. Direct database access bypasses application checks.

---

#### H5: N+1 Query Prevention NOT Implemented

**Status**: Plan requires DataLoaders, implementation MISSING.

**Missing**: DataLoader classes for batch loading related objects.

**Impact**: GraphQL queries will trigger excessive database queries (N+1 problem).

---

#### H6: Race Condition in User Creation

**Status**: Plan requires database locking, implementation MISSING.

**Missing**: `@transaction.atomic` with `select_for_update()` in registration service.

**Scenario**: Two concurrent registrations with same email. Both pass uniqueness check before either commits, resulting in database error or duplicate user.

**Impact**: Duplicate users or registration failures under concurrent load.

---

#### H7: Refresh Token Replay Detection NOT Implemented

**Status**: `SessionToken` has `is_refresh_token_used` field (✅), but logic NOT IMPLEMENTED.

**Missing**: Token refresh service that checks if refresh token already used and revokes entire token family if replay detected.

**Impact**: Stolen refresh tokens can be reused indefinitely. Attackers gain persistent access.

---

### Testing

#### H8: No Integration Tests

**Status**: `tests/integration/` directory exists but EMPTY.

**Missing**:

- Registration → Email verification → Login flow
- Login → 2FA → Session creation flow
- Password reset flow
- Multi-tenancy isolation tests
- Rate limiting tests

**Impact**: No testing of component interactions. Critical bugs not caught.

---

## Medium Priority Issues (Should Fix)

### Implementation Gaps

#### M1: Module-Level Docstrings Missing

**Issue**: Service files missing module-level docstrings (when created).

**Requirement**: Document module purpose, classes, and functions per CLAUDE.md standards.

---

#### M2: Error Messages Lack Codes and Actionable Guidance

**Issue**: Plan requires structured error responses with codes, but not implemented.

**Missing**:

- Error code standards (e.g., `AUTH_INVALID_CREDENTIALS`)
- User-friendly error messages
- Actionable guidance (e.g., "reset password" link)
- Retry information

**Impact**: Poor UX and difficult debugging.

---

#### M3: Email Service Failure Handling NOT Specified

**Issue**: Plan mentions graceful degradation but no implementation details.

**Missing**:

- Email queue (Celery? Django-Q? RQ?)
- Retry logic (max attempts, exponential backoff)
- Dead letter queue for failed emails
- Fallback mechanisms

**Impact**: Silent email failures blocking users from account access.

---

#### M4: Timezone Handling for Edge Cases NOT Addressed

**Issue**: Plan stores UTC but doesn't handle DST transitions, leap seconds, clock skew.

**Missing Tests**:

- DST boundary conditions
- Leap second handling
- System clock backward adjustment
- Server time drift

---

#### M5: User Enumeration Prevention Incomplete

**Issue**: Plan requires identical responses for valid/invalid emails, but not implemented.

**Missing**:

- Generic error messages for password reset
- No differentiation between "email doesn't exist" vs "invalid format"
- Account existence not revealed in responses

**Impact**: Attackers can enumerate registered email addresses for phishing attacks.

---

#### M6: Password History Mechanism NOT TESTED

**Issue**: `PasswordHistory` model exists (✅), `PasswordHistoryValidator` exists (✅), but:

- No unit tests for password history validation
- Integration with password change workflow unclear
- Validator not verified working

**Impact**: Password reuse prevention may not function.

---

#### M7: 2FA Backup Codes NOT Implemented

**Issue**: Plan requires single-use backup codes, but NOT IMPLEMENTED.

**Missing**:

- `BackupCode` model
- Backup code generation during 2FA setup (10 codes)
- Backup code validation during login
- One-time use enforcement

**Impact**: Users locked out if they lose 2FA device and have no backup codes.

---

#### M8: JWT Token Payload Structure NOT Specified

**Issue**: Plan requires JWT structure documentation, but tokens not implemented.

**Missing**:

- JWT payload field documentation
- Token claims specification
- Token type differentiation (access vs refresh)
- Example JWT token

**Impact**: Unclear API contract for token contents.

---

### Testing and Documentation

#### M9: Error Response Format Standard Missing

**Issue**: Plan doesn't specify error response format for GraphQL errors.

**Missing**:

- Structured error response type
- Error code field
- User-friendly message field
- Field-level error details
- Actionable guidance

---

#### M10: Performance Benchmarking Methodology NOT Detailed

**Issue**: Plan requires performance benchmarks but methodology undefined.

**Missing**:

- Login response time target: < 200ms (p95)
- GraphQL query response: < 100ms (p95)
- Token validation: < 10ms
- Database query count limit: < 5 per request

---

---

## Low Priority Issues (Consider Fixing)

#### L1: No Visual Flow Diagrams in Documentation

**Issue**: Plan has text descriptions but no Mermaid/PlantUML diagrams.

**Missing Diagrams**:

- Registration flow
- Login flow (with/without 2FA)
- Password reset flow
- Email verification flow
- Token refresh flow

---

#### L2: No Health Check Endpoint for Authentication Services

**Issue**: Health check endpoint incomplete.

**Missing Checks**:

- Database connectivity
- Email service (SMTP)
- Redis connectivity
- TOTP encryption key validity
- IP encryption key validity

---

#### L3: Audit Log Metadata Not Validated

**Issue**: `AuditLog.metadata` JSONField not validated or size-limited.

**Risk**: Potential DoS via oversized metadata.

---

---

## Edge Cases and Design Gaps

### User Registration Edge Cases

#### E1: Simultaneous Registration with Same Email

**Risk**: Two requests hit server at same time with identical emails. Both pass uniqueness check before either commits.

**Mitigation Not Specified**: Database unique constraint handling at application level.

**Test Required**:

```python
def test_concurrent_registration_same_email():
    """Test two simultaneous registrations with identical email."""
    # CRITICAL: Must result in only ONE user created
    # One request should succeed, other should fail with 409 Conflict
```

---

#### E2: Organisation Does Not Exist at Registration Time

**Risk**: User submits `organisationSlug` for deleted/inactive organisation. Timing attack: organisation deleted between validation and user creation.

**Behaviour Not Defined**: Should registration fail? Create pending user?

---

#### E3: Email Verification Token Expires During Registration

**Risk**: Slow network causes registration to take > 24 hours. Token expires before email sent.

---

#### E4: User Account Created But Email Service Fails

**Risk**: User exists in database but never receives verification email.

**Result**: Orphaned unverified accounts blocking future registration with that email.

---

### Organisation Edge Cases

#### E5: Organisation Deactivated During Active Sessions

**Risk**: `organisation.is_active = False` set during active sessions. Existing tokens still valid.

**Not Specified**: Should tokens be immediately revoked?

---

#### E6: Organisation Deleted with Active Users

**Risk**: Soft delete with "retain 90 days" but no implementation details. Active sessions must be revoked. Audit logs must be preserved.

**Cascade Behaviour Not Specified**

---

#### E7: First User in Organisation Becomes Owner

**Risk**: Two users register simultaneously. Race condition: both could become owner.

**Locking Mechanism Not Specified**

---

#### E8: Organisation Slug Conflicts

**Risk**: Slug "test-org" deleted (soft delete), new org wants same slug.

**Not Specified**: Should soft-deleted slugs be reserved?

---

### Token and Session Management

#### E9: Token Used Exactly at Expiration Timestamp

**Risk**: Token expires_at = 2026-01-07T12:00:00Z. Request arrives at exactly 2026-01-07T12:00:00.000Z.

**Behaviour Not Defined**: Is it valid or expired?

**Recommendation**: Use `expires_at < now()` (exclusive), not `expires_at <= now()`

---

#### E10: Multiple Token Verification Attempts in Parallel

**Risk**: User clicks email link multiple times rapidly. Multiple GraphQL requests hit `/verifyEmail` simultaneously.

**Problem**: All mark token as verified/used, creating race condition.

---

#### E11: Token Reuse After Marked as Used

**Risk**: `PasswordResetToken.used = True`. Attacker captures token before it's marked used. Replays token after legitimate use.

**Gap**: No specification of token hash invalidation in Redis cache.

---

#### E12: Clock Skew Between Servers

**Risk**: Database server time ≠ application server time. Token appears expired on one server, valid on another.

**Mitigation Not Specified**

---

#### E13: Token Expiration During Request

**Risk**: Request processing takes 2 seconds. Token expires mid-request.

**Not Specified**: Check expiration at start only or continuously?

---

#### E14: Concurrent Session Limit Enforcement

**Risk**: User logs in simultaneously on 6 devices (max 5 concurrent). Which session is evicted? Oldest? Random?

**Not Specified**

---

#### E15: Token Expiration During Multi-Step Operation

**Risk**: User starts 2FA setup (generates QR code), token expires before confirming.

**Not Specified**: Should 2FA setup maintain session extension?

---

### Two-Factor Authentication

#### E16: TOTP Device Loss and Recovery

**User Story**: User's phone stolen, no backup codes saved.

**Plan Says**: "Backup codes for account recovery"

**Not Specified**: What if backup codes also lost? Admin recovery process?

---

#### E17: 2FA Device Verification Before Enabling

**Issue**: User enables 2FA, immediately loses device, never verified setup.

**Risk**: User locked out before first successful 2FA login.

**Not Specified**: Require successful 2FA login before fully enabled?

---

#### E18: Session Fixation to Bypass 2FA

**Attack**: Attacker obtains valid password, tries to use old pre-2FA session.

**Mitigation Required**: All sessions invalidated when 2FA enabled.

**Not Specified**: Explicit session invalidation on 2FA enable.

---

#### E19: 2FA Code Reuse Attack

**Attack**: Attacker captures valid TOTP code, tries to reuse within 30-second window.

**Mitigation**: Track used codes within time window.

**Not Specified**: TOTP code reuse prevention.

---

#### E20: Disable 2FA Without Verification

**Attack**: Attacker gains access to authenticated session, disables 2FA.

**Plan Says**: `disableTwoFactor(password: String!)`

**Gap**: Should require 2FA code to disable if already enabled.

---

### Email and Communication

#### E21: Registration Email Bombing

**Attack**: Attacker registers 1000 accounts with `victim@example.com`

**Result**: Victim receives 1000 verification emails.

**Plan Says**: "Registration: 3 per hour per IP"

**Gap**: Rate limit by email address, not just IP.

---

#### E22: Password Reset Email Bombing

**Attack**: Attacker triggers password reset repeatedly for victim.

**Plan Says**: "Password reset: 3 per hour per email" (good)

**Gap**: What if attacker uses multiple accounts to trigger resets for same victim?

---

#### E23: Email Verification Resend Abuse

**Attack**: User repeatedly requests verification email resend.

**Plan Mentions**: `resendVerificationEmail` mutation

**Not Specified**: Rate limiting for resend.

---

#### E24: Disposable Email Addresses

**User**: Registers with `temp@mailinator.com`

**Not Specified**: Should disposable email domains be blocked?

---

#### E25: Email Format Edge Cases

**Not Specified**:

- `user@domain` (no TLD)
- `user@[192.168.1.1]` (IP address)
- `user+tag@example.com` (plus addressing)

---

### Time Boundaries and Timezone Issues

#### E26: User in Different Timezone Than Server

**Risk**: User in UTC+8 registers at 2026-01-07T23:59:59. Server in UTC sees 2026-01-07T15:59:59. Audit logs show "wrong" time from user perspective.

**Not Specified**: How are timezones handled in audit logs?

---

#### E27: Daylight Saving Time Transitions

**Risk**: Token expires at 2026-03-30T02:30:00 (during DST transition). This time doesn't exist in some timezones.

**Not Specified**: UTC storage confirmed but transition handling unclear.

---

#### E28: Leap Second Handling

**Risk**: Rare but real: 2026-06-30T23:59:60 (leap second). PostgreSQL timestamp handling unclear.

---

#### E29: System Clock Changes

**Risk**: Server clock adjusted backwards (NTP correction). Tokens with future expiration suddenly valid again.

**Not Specified**: Clock skew detection.

---

#### E30: Token Expiration During System Maintenance

**Risk**: Server shut down for 1 hour. All tokens that would have expired during shutdown. Are they expired or still valid based on absolute time?

---

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

---

### GraphQL Error Handling

**Overall Rating**: ❌ CRITICAL GAP

**Missing Specifications**:

1. **Query Depth Attack**: Plan mentions "query depth limiting (max 10)". Not specified: What error is returned? HTTP status code?

2. **Query Complexity Exceeds Limit**: User constructs expensive nested query. Not defined: Complexity calculation algorithm. Limit values per user/role?

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

---

### Service Layer Error Handling

**Overall Rating**: ⚠️ NEEDS ATTENTION

**Gaps**:

1. **External Service Failures**: Redis unavailable. Email service down. Partial mitigation: Plan mentions "graceful degradation" but no details.

2. **Encryption/Decryption Failures**: IP encryption key rotated, old key lost. Cannot decrypt stored IP addresses. Not specified: Fallback behaviour.

3. **TOTP Library Errors**: `pyotp` raises exception during code generation/verification. Not specified: Error handling strategy.

---

---

## Race Conditions and Concurrency

### User Creation Race Conditions

**Overall Rating**: ❌ CRITICAL GAP

**Attack Vector: Simultaneous Registration Bomb**:

```python
import asyncio
async def register_bomb():
    tasks = [register("victim@example.com", "Pass123!") for _ in range(100)]
    await asyncio.gather(*tasks)
```

**Expected Behaviour**: Only ONE user created, others fail with 409 Conflict
**Current Spec**: No transaction isolation specified

---

### Token Generation Race Conditions

**Overall Rating**: ❌ CRITICAL GAP

#### JWT Token Hash Collision

**Scenario**: Two users log in simultaneously, tokens generated with same random seed.

**Problem**: `token_hash = hashlib.sha256(jwt_token).hexdigest()` collision possible.

**Mitigation Not Specified**: Retry with new token? Fail?

---

#### Refresh Token Rotation Race

**Scenario**: User has token about to expire. Client sends two refresh requests simultaneously.

**Problem**:

- Both requests see valid refresh token
- Both generate new token and invalidate old refresh token
- One succeeds, one fails
- Not specified: Is this detected as token theft? User locked out?

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

---

#### Read Committed Isolation Level

**PostgreSQL Default**: READ COMMITTED

**Risk**: Non-repeatable reads within transaction

**Not Specified**: Should use REPEATABLE READ for critical operations?

---

#### Serialisation Anomalies

**Example**: Two users try to become first owner simultaneously.

**Mitigation**: Use SERIALIZABLE isolation or explicit locking

**Not Specified**: Isolation level requirements

---

### Redis Concurrency

**Overall Rating**: ⚠️ NEEDS ATTENTION

#### Redis Key Expiration Race Condition

**Scenario**: Check if key exists, then set with expiration.

```python
if not cache.get("rate_limit:user:1"):
    cache.set("rate_limit:user:1", 1, timeout=900)
# Race condition: key might expire between check and set
```

**Mitigation**: Use `SETNX` or Lua scripts

---

### Session Management Concurrency

**Overall Rating**: ❌ CRITICAL GAP

#### Concurrent Login from Same User

**Scenario**: User double-clicks login button.

**Problem**: Two sessions created when only one intended.

**Not Specified**: Deduplication logic.

---

#### Session Limit Enforcement Race Condition

**Scenario**: User has 4 sessions, two devices login simultaneously.

**Expected**: One succeeds, one evicts oldest and succeeds = 5 total

**Actual Race Condition**: Both check count=4, both create session = 6 total

**Mitigation Required**: Atomic check-and-increment

---

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

3. **Token expiration at exact second**: Token expires_at = 2026-01-07T12:00:00. Request at multiple microsecond offsets.

4. **TOTP code time step boundary**: TOTP codes valid for 30-second window. What happens at exact boundary?

---

### Collection Size Boundaries

**Overall Rating**: ⚠️ NEEDS ATTENTION

**Missing Tests**:

1. **Organisation with 10,000+ users**: GraphQL query `users(limit: 10000)`. Pagination required but limits not enforced.

2. **User with hundreds of sessions**: Never logs out, creates new session daily. Session table grows unbounded.

3. **Audit log query with millions of records**: Query performance on large dataset.

---

---

## Invalid Input and Security Testing

### Malicious Input Scenarios

**Overall Rating**: ❌ CRITICAL GAP

**Attack Vectors Not Tested**:

#### SQL Injection in GraphQL Variables

```graphql
mutation {
  login(input: { email: "admin@example.com' OR '1'='1", password: "anything" }) {
    token
  }
}
```

---

#### NoSQL Injection in Metadata JSON

```graphql
mutation {
  register(
    input: { email: "test@example.com", metadata: "{\"$where\": \"this.password == 'secret'\"}" }
  )
}
```

---

#### GraphQL Injection

```graphql
{
  user(id: "1) { password } fakeField: user(id: 1") {
    email
  }
}
```

---

#### Command Injection in User Agent

```
User-Agent: Mozilla/5.0; $(rm -rf /)
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

1. **Null values in required fields**
2. **Empty strings in required fields**
3. **Whitespace-only strings**
4. **Extremely long input strings**: DoS attack vector
5. **Negative IDs or UUIDs**
6. **Invalid UUID format**

---

---

## Test Coverage Analysis

### Current Test Coverage

**Unit Tests**: ✅ GOOD (Models only)

- `test_user_model.py` - ✅ User creation, email normalisation
- `test_user_manager.py` - ✅ UserManager methods
- `test_organisation_model.py` - ✅
- `test_user_profile_model.py` - ✅
- `test_session_token_model.py` - ✅
- `test_password_reset_token_model.py` - ✅
- `test_email_verification_token_model.py` - ✅
- `test_totp_device_model.py` - ✅
- `test_base_token_model.py` - ✅
- `test_audit_log_model.py` - ✅
- `test_password_history_model.py` - ✅
- `test_validators.py` - ✅ Password validators

**BDD Tests**: ⚠️ MINIMAL

- `features/user_registration.feature` - ✅ Exists (backend NOT implemented)
- `step_defs/test_user_registration_steps.py` - ✅ Exists

**Integration Tests**: ❌ NONE

- `tests/integration/` directory exists but empty

**E2E Tests**: ❌ NONE

- `tests/e2e/` directory exists but empty

**GraphQL Tests**: ❌ NONE

- `tests/graphql/` directory exists but empty

---

### Test Coverage Gaps

**Critical Gaps**:

1. ❌ No authentication flow tests (register → verify → login)
2. ❌ No password reset flow tests
3. ❌ No 2FA flow tests
4. ❌ No session management tests
5. ❌ No GraphQL mutation tests
6. ❌ No security tests (CSRF, SQL injection, XSS)
7. ❌ No multi-tenancy isolation tests
8. ❌ No rate limiting tests
9. ❌ No account lockout tests
10. ❌ No concurrent session limit tests

---

### Test Coverage Summary

| Area              | Coverage | Status |
| ----------------- | -------- | ------ |
| Models            | ~90%     | ✅     |
| Services          | 0%       | ❌     |
| GraphQL API       | 0%       | ❌     |
| Integration flows | 0%       | ❌     |
| Security features | 0%       | ❌     |
| **Overall**       | **~15%** | **🔴** |

**Test Coverage Target**: 80% overall (currently ~15%)

---

---

## Security Vulnerabilities Summary

### Authentication & Authorisation

| Vulnerability                       | Impact                           | Severity | Status             |
| ----------------------------------- | -------------------------------- | -------- | ------------------ |
| No CSRF protection on GraphQL       | CSRF attacks on mutations        | CRITICAL | ❌ NOT IMPLEMENTED |
| Email verification not enforced     | Unverified users can login       | CRITICAL | ❌ NOT IMPLEMENTED |
| No rate limiting on auth endpoints  | Brute force attacks              | CRITICAL | ❌ NOT CONFIGURED  |
| No account lockout mechanism        | Persistent brute force           | CRITICAL | ❌ NOT IMPLEMENTED |
| No concurrent session limits        | Unlimited session creation       | CRITICAL | ❌ NOT IMPLEMENTED |
| TOKEN_SIGNING_KEY not configured    | Forged session tokens            | CRITICAL | ❌ NOT CONFIGURED  |
| User enumeration via error messages | Account existence disclosure     | MEDIUM   | ⚠️ PARTIAL         |
| 2FA bypass via session fixation     | 2FA bypass                       | HIGH     | ❌ NOT MITIGATED   |
| Disable 2FA without verification    | 2FA removal without verification | HIGH     | ❌ NOT MITIGATED   |

---

### Token Management

| Vulnerability                          | Impact                      | Severity | Status             |
| -------------------------------------- | --------------------------- | -------- | ------------------ |
| Session token storage weakness         | Session hijacking           | CRITICAL | ⚠️ PARTIAL         |
| TOTP secret storage                    | 2FA bypass                  | CRITICAL | ⚠️ PARTIAL         |
| Password reset token not hashed        | Account takeover            | CRITICAL | ⚠️ PARTIAL         |
| No token revocation on password change | Stolen tokens remain valid  | CRITICAL | ❌ NOT IMPLEMENTED |
| No refresh token replay detection      | Token reuse attacks         | HIGH     | ❌ NOT IMPLEMENTED |
| Token reuse not detected               | Replay attacks              | CRITICAL | ❌ NOT IMPLEMENTED |
| Refresh token rotation not atomic      | Token loss on network error | HIGH     | ❌ NOT SPECIFIED   |

---

### Data Protection

| Vulnerability                              | Impact                                  | Severity | Status                |
| ------------------------------------------ | --------------------------------------- | -------- | --------------------- |
| No PostgreSQL RLS policies                 | Direct DB access bypasses multi-tenancy | HIGH     | ❌ NOT CONFIGURED     |
| No audit log preservation on org delete    | Loss of audit trail                     | HIGH     | ⚠️ NEEDS VERIFICATION |
| IP encryption key rotation not specified   | All IPs exposed if key leaked           | CRITICAL | ❌ NOT IMPLEMENTED    |
| Race condition in user creation            | Duplicate users or corrupted data       | HIGH     | ❌ NOT MITIGATED      |
| Organisation boundary enforcement (TOCTOU) | Data leakage between organisations      | CRITICAL | ⚠️ PARTIAL            |

---

### Email and Rate Limiting

| Vulnerability                | Impact                   | Severity | Status           |
| ---------------------------- | ------------------------ | -------- | ---------------- |
| Registration email bombing   | Email bombing attack     | MEDIUM   | ⚠️ PARTIAL       |
| Password reset email bombing | Email bombing attack     | MEDIUM   | ⚠️ PARTIAL       |
| 2FA rate limiting bypass     | Brute force on 2FA codes | MEDIUM   | ⚠️ PARTIAL       |
| TOTP code reuse possible     | 2FA bypass               | MEDIUM   | ❌ NOT MITIGATED |

---

---

## Performance Concerns

| Operation                   | Expected Time     | Concern                        | Mitigation Status                      |
| --------------------------- | ----------------- | ------------------------------ | -------------------------------------- |
| Login (no 2FA)              | < 200ms           | Argon2 hashing may take longer | ⚠️ Needs benchmarking                  |
| Registration                | < 500ms           | Email sending may block        | ⚠️ Async email queue recommended       |
| Password reset              | < 300ms           | Token generation + email       | ⚠️ Async recommended                   |
| GraphQL user query          | < 100ms           | N+1 query risk                 | ⚠️ Some select_related, not consistent |
| Audit log query             | < 500ms           | Large dataset scanning         | ⚠️ Indexes specified but no pagination |
| Token refresh               | < 100ms           | Redis + database round-trip    | ✅ Acceptable                          |
| 2FA verification            | < 200ms           | TOTP calculation               | ✅ Fast                                |
| IP decryption in audit logs | < 50ms per record | Fernet decryption overhead     | ⚠️ May be slow for bulk operations     |

---

**Recommendations**:

1. Benchmark Argon2: Tune parameters to meet 200ms target
2. Async email queue: Use Celery/Django-Q for non-blocking email
3. Audit log pagination: Enforce max 100 records per query
4. Bulk IP decryption: Cache decrypted IPs for admin views

---

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

---

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

---

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

---

**Recommendation**: Add explicit GDPR compliance features before production deployment.

---

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

---

### Account Recovery

**Issue**: Account recovery scenarios inadequately addressed.

**Missing Scenarios**:

1. User forgets email address (recovery by phone? username? admin help?)
2. Email account compromised (additional verification for sensitive operations?)
3. Locked account recovery (how to unlock? wait duration? contact admin?)
4. Inactive account handling (policy for accounts with no login for 1 year?)
5. Deleted account recovery (can user recover within 90-day soft delete window?)

---

### Error Messages

**Issue**: User-facing error messages not standardised.

**Gaps**:

- Inconsistent error formats
- Error message localisation not specified
- Security vs UX trade-off in error messages not documented
- Error codes for programmatic handling missing

---

---

## Recommendations

### Immediate Actions (Before Implementation)

**CRITICAL - Do not proceed with implementation until these are resolved:**

1. **Address all 6 critical security vulnerabilities from plan**:
   - Session token storage (use HMAC-SHA256 properly)
   - TOTP secret encryption (separate key, key rotation)
   - Password reset tokens (hash using SHA-256)
   - CSRF protection (implement for GraphQL)
   - Email verification enforcement (check on login)
   - IP encryption key rotation (automated quarterly)

2. **Add TOKEN_SIGNING_KEY to environment files** and update BaseToken configuration

3. **Implement all 9 missing GraphQL mutations** (register, login, logout, etc.)

4. **Implement service layer**:
   - AuthenticationService
   - TokenService
   - EmailService

5. **Implement CSRF protection middleware** for GraphQL mutations

6. **Create error response format standard** for GraphQL

7. **Review and approve security architecture** with security team before implementation

---

### High Priority (Before Production)

**Must fix before deployment:**

1. **Add composite database indexes** for multi-tenant queries (H1)
2. **Add indexes on token expiry fields** (H2)
3. **Verify AuditLog uses SET_NULL** instead of CASCADE (H3)
4. **Implement PostgreSQL Row-Level Security (RLS)** policies (H4)
5. **Implement N+1 query prevention** with DataLoaders (H5)
6. **Add database locking in registration** to prevent race conditions (H6)
7. **Implement refresh token replay detection** logic (H7)
8. **Write comprehensive integration tests** for all auth flows (H8)

---

### During Implementation

**Security Features**:

1. Implement account lockout (after 10 failed attempts in 1 hour)
2. Implement CSRF protection for GraphQL
3. Implement query depth and complexity limiting
4. Implement backup code system for 2FA
5. Implement refresh token reuse detection
6. Implement password history validation
7. Implement rate limiting for auth endpoints
8. Implement concurrent session limits (max 5)
9. Implement token revocation on password change
10. Implement IP encryption key rotation

**Performance Optimisations**:

1. Add composite database indexes
2. Implement query prefetching in GraphQL resolvers
3. Use Redis caching for sessions
4. Implement async email queue
5. Add audit log pagination (max 100 records)

**GDPR Compliance**:

1. Data export functionality
2. Account deletion (soft delete with recovery)
3. Consent tracking
4. Data retention enforcement

---

### Medium Priority (Before Production)

1. **Module-level docstrings** on all files (M1)
2. **Structured error responses** with codes and guidance (M2)
3. **Email service failure handling** with retry logic (M3)
4. **Timezone handling edge cases** testing (M4)
5. **User enumeration prevention** with generic error messages (M5)
6. **Password history validation** testing (M6)
7. **2FA backup codes system** implementation (M7)
8. **JWT token payload structure** documentation (M8)

---

### Testing Requirements

**Required Before Deployment**:

- ✅ Unit tests for all models (DONE - ~90%)
- ❌ Unit tests for all services (TODO - HIGH PRIORITY)
- ❌ Integration tests for auth flows (TODO - CRITICAL)
- ❌ E2E tests for user journeys (TODO - CRITICAL)
- ❌ GraphQL API tests for all mutations (TODO - CRITICAL)
- ❌ Security tests (CSRF, XSS, SQLi, JWT) (TODO - HIGH)
- ❌ BDD feature tests for all workflows (TODO - HIGH)
- ❌ Performance tests (TODO - MEDIUM)

**Test Coverage Target**: 80% overall (currently ~15%)

**Test Scenarios to Add**: 27+ critical scenarios, 34+ high-priority scenarios, 18+ medium-priority scenarios

---

---

## Phase 1 Completion Checklist

Before marking Phase 1 as complete, the following MUST be implemented and tested:

**Configuration**:

- [ ] Add TOKEN_SIGNING_KEY to all environment files
- [ ] Disable GraphQL introspection in production
- [ ] Configure rate limiting for auth endpoints

**Critical Features**:

- [ ] Implement all 9 GraphQL authentication mutations
- [ ] Implement AuthenticationService, TokenService, EmailService
- [ ] Implement CSRF protection for GraphQL mutations
- [ ] Enforce email verification on login
- [ ] Implement IP encryption key rotation management command
- [ ] Implement password reset workflow
- [ ] Implement email verification workflow
- [ ] Implement 2FA enrollment workflow
- [ ] Implement login with 2FA
- [ ] Implement account lockout mechanism (10 attempts/1 hour)
- [ ] Implement concurrent session limits (max 5)
- [ ] Implement token revocation on password change

**Database and Query Optimisation**:

- [x] Add composite indexes for multi-tenant queries (H1)
- [x] Add indexes on token expiry fields (H2)
- [x] Verify AuditLog uses SET_NULL (H3)
- [ ] Implement PostgreSQL RLS policies (H4)
- [ ] Implement DataLoaders for N+1 prevention (H5)
- [ ] Add database locking in registration (H6)

**Security**:

- [ ] Implement refresh token replay detection (H7)
- [ ] Implement CSRF protection for GraphQL
- [ ] Verify query depth limiting
- [ ] Implement backup code system for 2FA
- [ ] Implement password history validation
- [ ] Implement user enumeration prevention

**Testing**:

- [ ] Write integration tests for auth flows (H8)
- [ ] Achieve 80%+ test coverage
- [ ] Write security tests (CSRF, SQL injection, XSS)
- [ ] Write BDD feature tests for all workflows
- [ ] Write performance benchmarks

**Documentation**:

- [ ] Add module-level docstrings to all files (M1)
- [ ] Document error response format (M2)
- [ ] Document JWT token payload structure (M8)
- [ ] Add visual flow diagrams to documentation (L1)

---

---

## Recommended Implementation Order

### Week 1: Foundation & Service Layer

- Fix TOKEN_SIGNING_KEY configuration (C1)
- Implement TokenService (token generation, validation, refresh)
- Implement AuthenticationService (register, login, logout)
- Add database transaction locking for registration (H6)

### Week 2: GraphQL Mutations & CSRF Protection

- Implement CSRF middleware for GraphQL (C4)
- Implement register, login, logout mutations
- Implement token refresh mutation
- Add auth-specific rate limiting (C11)

### Week 3: Email Workflows

- Implement EmailService
- Implement email verification workflow (C8)
- Implement password reset workflow (C7)
- Add email failure handling with retry logic (M3)

### Week 4: Two-Factor Authentication

- Implement 2FA enrollment workflow (C9)
- Implement 2FA login flow (C10)
- Implement backup codes system (M7)
- Add TOTP code reuse prevention

### Week 5: Security Features

- Implement account lockout mechanism (C12)
- Implement concurrent session limits (C13)
- Implement token revocation on password change (C14)
- Implement refresh token replay detection (H7)

### Week 6: Database Optimisation

- Add composite indexes (H1)
- Add token expiry indexes (H2)
- Implement PostgreSQL RLS policies (H4)
- Implement DataLoaders for GraphQL (H5)

### Week 7: IP Encryption Key Rotation

- Implement key rotation management command (C6)
- Implement automated quarterly rotation
- Add key versioning system
- Test re-encryption of existing IPs

### Week 8: Testing & QA

- Write integration tests (H8)
- Write E2E tests for all workflows
- Write security tests
- Write performance benchmarks
- Target 80%+ test coverage

### Week 9: GDPR & Documentation

- Implement GDPR features (data export, deletion, consent)
- Add module-level docstrings (M1)
- Document error response format (M2)
- Document JWT payload structure (M8)
- Create visual flow diagrams (L1)

### Week 10: Final QA & Hardening

- Security audit
- Penetration testing
- Load testing (1000+ concurrent users)
- Final compliance review
- Production readiness assessment

---

---

## Handoff Signals

**To fix critical authentication issues:**

```bash
Run `/syntek-dev-suite:backend` to implement GraphQL mutations and service layer
```

**To implement security features:**

```bash
Run `/syntek-dev-suite:security` to add CSRF protection, rate limiting, and account lockout
```

**To write integration and E2E tests:**

```bash
Run `/syntek-dev-suite:test-writer` to create comprehensive test suite
```

**To optimise database queries:**

```bash
Run `/syntek-dev-suite:database` to add composite indexes and RLS policies
```

**To debug specific issues:**

```bash
Run `/syntek-dev-suite:debug` to investigate [specific issue from report]
```

**To review security implementation:**

```bash
Run `/syntek-dev-suite:security` to conduct security review and implement fixes
```

---

---

## Conclusion

The User Authentication System (US-001) demonstrates strong architectural foundations with comprehensive security feature specifications. However, **critical gaps in both the specification and implementation prevent safe deployment**.

### Key Findings

**✅ Strengths** (from plan):

- Strong security architecture (Argon2, 2FA, IP encryption, audit logging)
- Comprehensive multi-tenancy design
- Good separation of concerns (models, services, GraphQL)
- Detailed GraphQL API specifications
- Well-structured database models

**✅ Implementation Progress**:

- Models fully implemented (11/11)
- Unit tests for models (90% coverage)
- PasswordHistoryValidator implemented
- TOTPDevice with Fernet encryption

**❌ Critical Gaps** (MUST FIX):

**From Plan**:

- Token storage vulnerabilities not fully specified
- CSRF protection not included
- Email verification not enforced
- IP encryption key rotation not specified
- Race conditions not mitigated
- Refresh token reuse detection missing
- 2FA bypass vectors not addressed
- Database transaction isolation not defined
- Email bombing prevention incomplete

**From Implementation**:

- GraphQL mutations not implemented (0/9)
- Service layer not implemented
- Authentication workflows not implemented
- Password reset workflow missing
- Email verification workflow missing
- 2FA enrollment and login workflows missing
- Rate limiting not configured for auth endpoints
- Account lockout not implemented
- Concurrent session limits not enforced
- Token revocation on password change not implemented
- IP encryption key rotation not implemented
- Integration tests not written

**⚠️ High Priority Gaps** (SHOULD FIX):

- N+1 query performance risk
- Missing composite database indexes
- Token expiry field indexes missing
- PostgreSQL RLS not configured
- Refresh token replay detection logic missing
- Session timeout configuration undefined
- GraphQL query depth limiting not implemented

---

### Overall Status

**🔴 NOT READY FOR IMPLEMENTATION OR DEPLOYMENT**

| Phase                | Status                                      |
| -------------------- | ------------------------------------------- |
| Planning             | ⚠️ Safe to proceed with revisions           |
| Design Review        | ❌ Critical gaps require resolution         |
| Implementation       | 🔴 Only models done, core workflows missing |
| Testing              | 🔴 Only unit tests, no integration/E2E      |
| Production Readiness | 🔴 Multiple critical blockers               |

---

### Recommended Next Steps

1. **Create addendum document** addressing all critical gaps from plan (estimated 2-3 days)
2. **Update implementation plan** with concurrency mitigations and security specifications
3. **Begin implementation** following recommended 10-week schedule
4. **Conduct parallel code review** using `/syntek-dev-suite:review`
5. **Use `/syntek-dev-suite:security`** to implement critical security features
6. **Use `/syntek-dev-suite:backend`** to build service layer and GraphQL mutations
7. **Use `/syntek-dev-suite:test-writer`** to create comprehensive test suite
8. **Use `/syntek-dev-suite:database`** to optimise queries and add RLS policies
9. **Security audit** by external firm before production
10. **Penetration testing** on staging environment before deployment

---

### Estimated Timeline

- **Planning Revisions**: 2-3 days
- **Implementation**: 8-10 weeks
- **Testing & QA**: 2-3 weeks
- **Security Audit**: 1 week
- **Total to Production**: 12-16 weeks

---

**Reviewed By**: QA Tester Agent
**Date**: 07/01/2026
**Recommendation**: ⚠️ **REVISE PLAN AND COMPLETE IMPLEMENTATION BEFORE DEPLOYMENT**
**Status**: 🔴 **NOT READY**
**Blockers**: 21 Critical + 16 High Priority
**Estimated Completion**: 12-16 weeks at current pace
