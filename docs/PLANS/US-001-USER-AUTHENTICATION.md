# User Authentication System - Implementation Plan

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**User Story**: US001
**Branch**: us001/user-authentication
**Status**: Updated with Consolidated Review Findings
**Author**: System Architect
**Review Status**: Approved with Critical Recommendations
**Reviews Incorporated**: Architecture, Backend, Code Quality, Database, QA, Security, Testing

---

## Table of Contents

- [User Authentication System - Implementation Plan](#user-authentication-system---implementation-plan)
  - [Table of Contents](#table-of-contents)
  - [Consolidated Review Findings](#consolidated-review-findings)
    - [Review Summary](#review-summary)
    - [Critical Issues (Must Fix Before Implementation)](#critical-issues-must-fix-before-implementation)
    - [High Priority Issues (Must Fix Before Production)](#high-priority-issues-must-fix-before-production)
    - [Medium Priority Issues (Should Fix)](#medium-priority-issues-should-fix)
    - [Architecture Strengths Identified](#architecture-strengths-identified)
    - [Changes Incorporated From Reviews](#changes-incorporated-from-reviews)
    - [Implementation Details for Review Findings](#implementation-details-for-review-findings)
      - [Critical Issue Implementations](#critical-issue-implementations)
      - [High Priority Issue Implementations](#high-priority-issue-implementations)
      - [Medium Priority Issue Implementations](#medium-priority-issue-implementations)
      - [Edge Cases Coverage](#edge-cases-coverage)
  - [Executive Summary](#executive-summary)
  - [Requirements](#requirements)
    - [Core Requirements](#core-requirements)
    - [Security Requirements](#security-requirements)
    - [Multi-Tenancy Requirements](#multi-tenancy-requirements)
    - [Non-Functional Requirements](#non-functional-requirements)
  - [Technical Design](#technical-design)
    - [Database Schema](#database-schema)
      - [User Model](#user-model)
      - [Organisation Model](#organisation-model)
      - [UserProfile Model](#userprofile-model)
      - [TOTPDevice Model (2FA)](#totpdevice-model-2fa)
      - [AuditLog Model](#auditlog-model)
      - [SessionToken Model](#sessiontoken-model)
      - [PasswordResetToken Model](#passwordresettoken-model)
      - [EmailVerificationToken Model](#emailverificationtoken-model)
      - [Abstract BaseToken Model (DRY Principle)](#abstract-basetoken-model-dry-principle)
    - [GraphQL API Contracts](#graphql-api-contracts)
      - [Types](#types)
      - [Inputs](#inputs)
      - [Queries](#queries)
      - [Mutations](#mutations)
    - [Django Groups and Permissions System](#django-groups-and-permissions-system)
      - [Permission Hierarchy](#permission-hierarchy)
      - [Default Groups](#default-groups)
      - [Custom Permissions](#custom-permissions)
      - [Group Assignment on User Creation](#group-assignment-on-user-creation)
      - [Permission Checking in GraphQL Resolvers](#permission-checking-in-graphql-resolvers)
      - [Permission Migration Path](#permission-migration-path)
    - [Authentication Flow](#authentication-flow)
      - [Registration Flow](#registration-flow)
      - [Login Flow (Without 2FA)](#login-flow-without-2fa)
      - [Login Flow (With 2FA)](#login-flow-with-2fa)
      - [Password Reset Flow](#password-reset-flow)
      - [Email Verification Flow](#email-verification-flow)
    - [Security Architecture](#security-architecture)
      - [Password Requirements](#password-requirements)
      - [Password Hashing](#password-hashing)
      - [Session Management](#session-management)
      - [IP Address Encryption](#ip-address-encryption)
      - [Rate Limiting](#rate-limiting)
      - [Account Lockout Mechanism](#account-lockout-mechanism)
      - [PostgreSQL Row-Level Security (RLS)](#postgresql-row-level-security-rls)
    - [Extensibility and Future Role Models](#extensibility-and-future-role-models)
      - [Extension Pattern: OneToOne Relationships](#extension-pattern-onetoone-relationships)
      - [Why OneToOne Instead of Inheritance](#why-onetoone-instead-of-inheritance)
      - [GraphQL Types for Role-Specific Profiles](#graphql-types-for-role-specific-profiles)
      - [Permission Groups for Future Roles](#permission-groups-for-future-roles)
      - [Migration Path for Adding Role Profiles](#migration-path-for-adding-role-profiles)
    - [Django Admin Configuration](#django-admin-configuration)
      - [User Admin Configuration](#user-admin-configuration)
      - [Organisation Admin Configuration](#organisation-admin-configuration)
      - [Audit Log Admin Configuration](#audit-log-admin-configuration)
      - [Group and Permission Admin](#group-and-permission-admin)
      - [Admin Site Customisation](#admin-site-customisation)
      - [Audit Logging](#audit-logging)
  - [Implementation Phases](#implementation-phases)
    - [Phase 1: Core Models and Database](#phase-1-core-models-and-database)
    - [Phase 2: Authentication Service Layer](#phase-2-authentication-service-layer)
    - [Phase 3: GraphQL API Implementation](#phase-3-graphql-api-implementation)
    - [Phase 4: Two-Factor Authentication (2FA)](#phase-4-two-factor-authentication-2fa)
    - [Phase 5: Password Reset and Email Verification](#phase-5-password-reset-and-email-verification)
    - [Phase 6: Audit Logging and Security](#phase-6-audit-logging-and-security)
    - [Phase 7: Testing and Documentation](#phase-7-testing-and-documentation)
  - [Testing Strategy](#testing-strategy)
    - [Unit Tests (TDD)](#unit-tests-tdd)
    - [BDD Tests](#bdd-tests)
    - [Integration Tests](#integration-tests)
    - [End-to-End Tests](#end-to-end-tests)
    - [GraphQL API Tests](#graphql-api-tests)
    - [Security Tests](#security-tests)
  - [Risks and Mitigations](#risks-and-mitigations)
  - [Open Questions](#open-questions)
  - [Success Criteria](#success-criteria)
  - [Next Steps](#next-steps)

---

## Consolidated Review Findings

**Review Date**: 07/01/2026
**Review Status**: ✅ **Approved with Critical Recommendations**

This section consolidates findings from all reviews conducted for US-001:

| Review Document            | Rating | Status                              |
| -------------------------- | ------ | ----------------------------------- |
| Architecture Review        | 8.5/10 | Approved with Conditions            |
| Backend Review             | 8.5/10 | Approved with Recommendations       |
| Code Quality Review        | 8.5/10 | Approved with Recommendations       |
| Database Review            | 4.1/5  | Approved with Critical Improvements |
| QA Review                  | ⚠️     | NOT READY - Critical Issues         |
| Security Review            | 8.3/10 | Approved with Recommendations       |
| Testing Review             | 8.5/10 | Approved with Gaps to Address       |
| Documentation Review       | 8.5/10 | Excellent                           |
| Implementation Plan Review | 8.5/10 | Ready with Improvements             |

### Review Summary

**Overall Assessment**: The plan demonstrates excellent architectural design and strong security
practices. However, **6 critical security vulnerabilities** identified by QA must be resolved
before implementation can proceed.

**Key Statistics from QA Review:**

- Critical Issues: 6 (blocking deployment)
- High Priority Issues: 8 (must fix before production)
- Medium Priority Issues: 8 (should fix)
- Edge Cases Not Covered: 27 critical gaps

### Critical Issues (Must Fix Before Implementation)

These issues from the QA and Security reviews **block deployment** and must be resolved:

| #   | Issue                                        | Source      | Impact                                        | Resolution                                                           |
| --- | -------------------------------------------- | ----------- | --------------------------------------------- | -------------------------------------------------------------------- |
| 1   | **Session Token Storage Vulnerability**      | QA          | Session hijacking risk                        | Use HMAC-SHA256 with secret key instead of plain SHA-256             |
| 2   | **TOTP Secret Storage Security**             | QA          | 2FA bypass risk                               | Specify Fernet encryption with separate key, document key management |
| 3   | **Password Reset Token Not Hashed**          | QA          | Account takeover risk                         | Store HMAC-SHA256 hash (same as C1), return plain token to user      |
| 4   | **Missing CSRF Protection**                  | QA          | Cross-site attack vulnerability               | Add CSRF middleware for GraphQL mutations                            |
| 5   | **Email Verification Bypass**                | QA          | Spam/bot account risk                         | Block login for unverified users OR limit their actions              |
| 6   | **IP Encryption Key Rotation Not Specified** | QA/Security | All historical IPs exposed if key compromised | Implement automated key rotation with re-encryption                  |

**Action Required**: Add implementation details for all 6 critical issues to the plan before Phase 1.

### High Priority Issues (Must Fix Before Production)

| #   | Issue                                                         | Source       | Category       |
| --- | ------------------------------------------------------------- | ------------ | -------------- |
| 1   | Missing composite indexes for multi-tenant queries            | Database     | Performance    |
| 2   | Missing indexes on token expiry fields (expires_at)           | Database     | Performance    |
| 3   | AuditLog.organisation uses CASCADE (should be SET_NULL)       | Database     | Data Loss Risk |
| 4   | User.organisation not nullable (prevents platform superusers) | Database     | Design         |
| 5   | No Row-Level Security (RLS) for database-level multi-tenancy  | Database     | Security       |
| 6   | Missing N+1 query prevention (DataLoaders)                    | Code Quality | Performance    |
| 7   | Race conditions in user creation and token generation         | QA           | Concurrency    |
| 8   | Missing token revocation on password change                   | QA/Security  | Security       |
| 9   | Refresh token replay detection not implemented                | Security     | Security       |
| 10  | Missing password breach checking (HaveIBeenPwned)             | Security     | Security       |
| 11  | JWT algorithm and key rotation not specified                  | Security     | Security       |
| 12  | Concurrent session limit not enforced                         | Security     | Security       |
| 13  | Account lockout mechanism incomplete                          | Security     | Security       |
| 14  | GraphQL query depth limiting tests missing                    | Testing      | Coverage       |
| 15  | CSRF, XSS, SQL injection security tests missing               | Testing      | Coverage       |

### Medium Priority Issues (Should Fix)

| #   | Issue                                                              | Source        | Category      |
| --- | ------------------------------------------------------------------ | ------------- | ------------- |
| 1   | Module-level docstrings missing in code examples                   | Code Quality  | Documentation |
| 2   | Services use static methods (limits testability/DI)                | Code Quality  | Design        |
| 3   | Password validation uses custom regex instead of Django validators | Code Quality  | Standards     |
| 4   | Error messages lack actionable guidance and codes                  | Code Quality  | UX            |
| 5   | Email service failure handling not specified                       | QA            | Reliability   |
| 6   | Timezone handling for edge cases (DST) not addressed               | QA            | Correctness   |
| 7   | User enumeration prevention incomplete                             | QA            | Security      |
| 8   | Password history mechanism not detailed                            | Security      | Security      |
| 9   | 2FA backup code implementation incomplete                          | Security      | Security      |
| 10  | Visual flow diagrams missing (only text-based)                     | Documentation | Clarity       |
| 11  | JWT token payload structure not specified                          | Documentation | API Contract  |
| 12  | Performance benchmarking methodology not detailed                  | Documentation | Testing       |

### Architecture Strengths Identified

All reviews consistently highlighted these strengths:

- ✅ **Outstanding DRY Implementation**: BaseToken abstract model eliminates 30+ lines of duplication
- ✅ **Comprehensive Security Architecture**: Argon2 hashing, IP encryption, rate limiting, audit logging
- ✅ **Excellent Documentation**: Google-style docstrings with detailed explanations
- ✅ **Strong Type Safety**: Consistent use of type hints throughout
- ✅ **Professional Permission System**: Django Groups and Strawberry decorators
- ✅ **Comprehensive Testing Strategy**: TDD, BDD, Integration, E2E, Security tests
- ✅ **Clear Separation of Concerns**: Models, services, GraphQL API layers
- ✅ **Forward-Thinking Design**: Extension patterns for future role models
- ✅ **Multi-Tenancy Excellence**: Organisation-based isolation with proper boundaries
- ✅ **Proper 3NF Normalisation**: All tables properly normalised
- ✅ **UUID Primary Keys**: Security and distributed systems ready

### Changes Incorporated From Reviews

This updated plan (v2.0.0) incorporates the following from all reviews:

**From Architecture Review:**

- Enhanced token management strategy with Redis-primary approach
- Account lockout implementation in authentication flow
- PostgreSQL RLS policy definitions for multi-tenancy
- GraphQL complexity analysis configuration
- Dependency injection container pattern
- Soft delete implementation for GDPR compliance
- Enhanced caching strategy (user objects, permissions, queries)
- Celery integration for async email operations
- Database connection pooling with PgBouncer

**From Database Review:**

- Added composite indexes for multi-tenant queries
- Added indexes on expires_at fields for all token models
- Changed AuditLog.organisation from CASCADE to SET_NULL
- Made User.organisation nullable for platform superusers
- Added PostgreSQL RLS policy definitions
- Added database-level constraints (email format, token expiry)

**From Security Review:**

- Specified TOTP encryption method (Fernet with separate key)
- Added password breach checking integration (HaveIBeenPwned)
- Documented JWT configuration (RS256, key rotation)
- Added refresh token family tracking for replay detection
- Documented session revocation on password change
- Added CORS and security header configuration

**From QA Review:**

- Added HMAC-SHA256 for token hashing (not plain SHA-256)
- Added CSRF protection middleware for GraphQL
- Blocked login for unverified users
- Added IP encryption key rotation procedure
- Added race condition prevention with database locking
- Added concurrent session limit enforcement

**From Testing Review:**

- Added BaseToken abstract model test requirements
- Added security test requirements (CSRF, XSS, SQL injection, JWT)
- Added E2E test scenarios for all authentication flows
- Added factory patterns for test data generation
- Added CI/CD pipeline configuration requirements

**From Code Quality Review:**

- Added module-level docstrings requirement
- Added TypedDict definitions for complex return types
- Converted service static methods to instance methods with DI
- Added custom exception hierarchy
- Extracted validation logic to separate layer

**Review Documents:**

- `docs/ARCHITECTURE/US-001/ARCHITECTURE-REVIEW.md`
- `docs/BACKEND/US-001/BACKEND-REVIEW-US-001.md`
- `docs/CODE-REVIEW/US-001/CODE-QUALITY-REVIEW-US-001-CONSOLIDATED.md`
- `docs/DATABASE/US-001/US-001-DATABASE-REVIEW.md`
- `docs/QA/US-001/QA-CONSOLIDATED.md`
- `docs/SECURITY/US-001/US-001-SECURITY.md`
- `docs/TESTS/REVIEWS/US-001/US-001-TESTING-REVIEW-CONSOLIDATED.md`
- `docs/REVIEWS/US-001/REVIEW-USER-AUTHENTICATION-PLAN-2026-01-06.md`
- `docs/REVIEWS/US-001/REVIEW-US001-AUTHENTICATION.md`
- `docs/REVIEWS/US-001/REVIEW-US001-IMPLEMENTATION-PLAN.md`
- `docs/REVIEWS/US-001/DOCUMENTATION-REVIEW-US-001.md`

### Implementation Details for Review Findings

This section provides **concrete implementation code and patterns** for every issue identified
in the reviews. Each subsection corresponds to the issue tables above.

---

#### Critical Issue Implementations

##### C1: Session Token Storage - HMAC-SHA256 Implementation

**Problem**: Plain SHA-256 hashing allows attackers with database access to compute valid tokens.

**Solution**: Use HMAC-SHA256 with a secret key for token hashing.

```python
# apps/core/utils/token_hashing.py
"""Secure token hashing utilities using HMAC-SHA256."""

import hmac
import hashlib
import secrets
from django.conf import settings


class TokenHasher:
    """HMAC-SHA256 token hashing for secure token storage.

    Uses a secret key to create keyed hashes, preventing attackers with
    database access from computing valid tokens even if they have the hash.
    """

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate a cryptographically secure random token.

        Args:
            length: Number of bytes for the token (default 32 = 256 bits).

        Returns:
            URL-safe base64-encoded token string.
        """
        return secrets.token_urlsafe(length)

    @staticmethod
    def hash_token(token: str) -> str:
        """Create HMAC-SHA256 hash of a token.

        Args:
            token: Plain text token to hash.

        Returns:
            Hexadecimal HMAC-SHA256 hash.
        """
        return hmac.new(
            key=settings.TOKEN_SIGNING_KEY.encode(),
            msg=token.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

    @staticmethod
    def verify_token(token: str, token_hash: str) -> bool:
        """Verify a token against its hash using constant-time comparison.

        Args:
            token: Plain text token to verify.
            token_hash: Stored HMAC-SHA256 hash.

        Returns:
            True if token matches hash, False otherwise.
        """
        computed_hash = TokenHasher.hash_token(token)
        return hmac.compare_digest(computed_hash, token_hash)
```

**Environment Variable Required:**

```bash
# .env.dev, .env.staging, .env.production
TOKEN_SIGNING_KEY=<64-character-random-string>
```

**Generate Key:**

```python
import secrets
print(secrets.token_hex(32))  # 64 hex characters
```

**Usage in TokenService (replaces hashlib.sha256):**

```python
# apps/core/services/token_service.py

from apps.core.utils.token_hashing import TokenHasher

class TokenService:
    """Token management service using HMAC-SHA256."""

    @staticmethod
    def create_token(user: User, request) -> dict:
        """Create access and refresh tokens with secure hashing."""
        # Generate tokens
        access_token = TokenHasher.generate_token()
        refresh_token = TokenHasher.generate_token()

        # Hash for storage (HMAC-SHA256, not plain SHA-256)
        access_token_hash = TokenHasher.hash_token(access_token)
        refresh_token_hash = TokenHasher.hash_token(refresh_token)

        # Store hashes in database and Redis
        SessionToken.objects.create(
            user=user,
            token_hash=access_token_hash,
            refresh_token_hash=refresh_token_hash,
            # ... other fields
        )

        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
        }

    @staticmethod
    def validate_token(token: str) -> User:
        """Validate token using HMAC verification."""
        token_hash = TokenHasher.hash_token(token)

        try:
            session = SessionToken.objects.select_related('user').get(
                token_hash=token_hash,
                expires_at__gt=timezone.now()
            )
            return session.user
        except SessionToken.DoesNotExist:
            raise AuthenticationError("Invalid or expired token")
```

---

##### C2: TOTP Secret Storage - Fernet Encryption Implementation

**Problem**: TOTP secrets stored in plain text allow 2FA bypass if database is compromised.

**Solution**: Encrypt TOTP secrets using Fernet with a separate encryption key.

```python
# apps/core/utils/totp_encryption.py
"""TOTP secret encryption using Fernet symmetric encryption."""

from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class TOTPEncryption:
    """Fernet encryption for TOTP secrets.

    Uses a separate encryption key from other secrets to limit blast radius
    if any single key is compromised.

    Attributes:
        _cipher: Cached Fernet cipher instance.
    """

    _cipher = None

    @classmethod
    def _get_cipher(cls) -> Fernet:
        """Get or create the Fernet cipher instance.

        Returns:
            Fernet cipher for encryption/decryption.

        Raises:
            ImproperlyConfigured: If TOTP_ENCRYPTION_KEY is not set.
        """
        if cls._cipher is None:
            key = getattr(settings, 'TOTP_ENCRYPTION_KEY', None)
            if not key:
                raise ImproperlyConfigured(
                    "TOTP_ENCRYPTION_KEY must be set in Django settings"
                )
            cls._cipher = Fernet(key.encode() if isinstance(key, str) else key)
        return cls._cipher

    @classmethod
    def encrypt_secret(cls, secret: str) -> bytes:
        """Encrypt a TOTP secret.

        Args:
            secret: Plain text TOTP secret (base32 encoded).

        Returns:
            Encrypted secret as bytes.
        """
        cipher = cls._get_cipher()
        return cipher.encrypt(secret.encode())

    @classmethod
    def decrypt_secret(cls, encrypted_secret: bytes) -> str:
        """Decrypt a TOTP secret.

        Args:
            encrypted_secret: Encrypted TOTP secret.

        Returns:
            Plain text TOTP secret.

        Raises:
            InvalidToken: If decryption fails (wrong key or corrupted data).
        """
        cipher = cls._get_cipher()
        return cipher.decrypt(encrypted_secret).decode()

    @classmethod
    def rotate_key(cls, old_key: str, new_key: str, encrypted_secret: bytes) -> bytes:
        """Re-encrypt a secret with a new key.

        Args:
            old_key: Previous Fernet key.
            new_key: New Fernet key.
            encrypted_secret: Secret encrypted with old key.

        Returns:
            Secret encrypted with new key.
        """
        # Decrypt with old key
        old_cipher = Fernet(old_key.encode())
        plain_secret = old_cipher.decrypt(encrypted_secret).decode()

        # Encrypt with new key
        new_cipher = Fernet(new_key.encode())
        return new_cipher.encrypt(plain_secret.encode())
```

**Environment Variable Required:**

```bash
# .env.dev, .env.staging, .env.production
# MUST be different from IP_ENCRYPTION_KEY and TOKEN_SIGNING_KEY
TOTP_ENCRYPTION_KEY=<fernet-key>
```

**Generate Key:**

```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

**Key Management Documentation:**

| Key | Purpose | Rotation | Storage |
|-----|---------|----------|---------|
| `TOTP_ENCRYPTION_KEY` | Encrypt 2FA secrets | Annually + on compromise | Environment variable |
| `IP_ENCRYPTION_KEY` | Encrypt IP addresses | Quarterly | Environment variable |
| `TOKEN_SIGNING_KEY` | HMAC token hashing | Annually + on compromise | Environment variable |
| `SECRET_KEY` | Django sessions/CSRF | On compromise only | Environment variable |

**Updated TOTPDevice Model:**

```python
# apps/core/models/totp_device.py

class TOTPDevice(models.Model):
    """TOTP device with encrypted secret storage."""

    secret = models.BinaryField()  # Encrypted with Fernet, NOT CharField

    def set_secret(self, plain_secret: str) -> None:
        """Set and encrypt the TOTP secret.

        Args:
            plain_secret: Plain text base32 TOTP secret.
        """
        self.secret = TOTPEncryption.encrypt_secret(plain_secret)

    def get_secret(self) -> str:
        """Get the decrypted TOTP secret.

        Returns:
            Plain text base32 TOTP secret.
        """
        return TOTPEncryption.decrypt_secret(self.secret)
```

---

##### C3: Password Reset Token Hashing Implementation

**Problem**: Storing plain tokens allows account takeover if database is compromised.

**Solution**: Store HMAC-SHA256 hash (using same `TokenHasher` as session tokens), return plain token to user via email.

> **Note**: We use HMAC-SHA256 (not plain SHA-256) for the same reason as session tokens (C1) -
> an attacker with database access cannot compute valid hashes without the secret key.

```python
# apps/core/services/password_reset_service.py
"""Password reset service with secure token handling."""

import secrets
from datetime import timedelta
from django.utils import timezone
from apps.core.models import PasswordResetToken, User
from apps.core.services.email_service import EmailService
from apps.core.utils.token_hashing import TokenHasher  # Same as C1


class PasswordResetService:
    """Service for password reset operations with secure token handling.

    Tokens are:
    - Generated using cryptographically secure random bytes
    - Hashed with HMAC-SHA256 before storage (plain token never stored)
    - Sent to user via email
    - Valid for 15 minutes only
    - Single-use (marked as used after reset)
    """

    TOKEN_EXPIRY_MINUTES = 15

    @staticmethod
    def create_reset_token(user: User) -> str:
        """Create a password reset token.

        Args:
            user: User requesting password reset.

        Returns:
            Plain text token to send to user (NOT stored in database).
        """
        # Generate cryptographically secure token
        plain_token = secrets.token_urlsafe(32)

        # HMAC-SHA256 hash for storage (attacker with DB access cannot forge)
        token_hash = TokenHasher.hash_token(plain_token)

        # Invalidate any existing tokens for this user
        PasswordResetToken.objects.filter(user=user, used=False).update(used=True)

        # Create new token record with HASH only
        PasswordResetToken.objects.create(
            user=user,
            token=token_hash,  # Store HMAC hash, NOT plain token
            expires_at=timezone.now() + timedelta(minutes=PasswordResetService.TOKEN_EXPIRY_MINUTES),
            used=False
        )

        # Return plain token to send via email
        return plain_token

    @staticmethod
    def validate_and_reset(plain_token: str, new_password: str) -> bool:
        """Validate token and reset password.

        Args:
            plain_token: Token from email link.
            new_password: New password to set.

        Returns:
            True if password was reset successfully.

        Raises:
            ValueError: If token is invalid, expired, or already used.
        """
        # HMAC-SHA256 hash the incoming token to compare with stored hash
        token_hash = TokenHasher.hash_token(plain_token)

        try:
            reset_token = PasswordResetToken.objects.select_related('user').get(
                token=token_hash,
                used=False,
                expires_at__gt=timezone.now()
            )
        except PasswordResetToken.DoesNotExist:
            raise ValueError("Invalid or expired password reset token")

        # Reset password
        user = reset_token.user
        user.set_password(new_password)
        user.save()

        # Mark token as used
        reset_token.used = True
        reset_token.save()

        # Revoke all existing sessions (security measure)
        from apps.core.services.token_service import TokenService
        TokenService.revoke_all_user_tokens(user)

        return True

    @staticmethod
    def request_reset(email: str, request) -> None:
        """Request password reset for an email.

        Always returns success to prevent user enumeration.

        Args:
            email: Email address to send reset link.
            request: HTTP request for audit logging.
        """
        try:
            user = User.objects.get(email=email.lower(), is_active=True)
            plain_token = PasswordResetService.create_reset_token(user)

            # Send email with plain token (not hash)
            EmailService.send_password_reset_email(
                user=user,
                token=plain_token,
                expires_minutes=PasswordResetService.TOKEN_EXPIRY_MINUTES
            )
        except User.DoesNotExist:
            # Don't reveal whether user exists - return silently
            pass
```

---

##### C4: CSRF Protection for GraphQL Implementation

**Problem**: GraphQL mutations vulnerable to CSRF attacks.

**Solution**: Implement GraphQL-specific CSRF protection middleware.

```python
# apps/core/middleware/graphql_csrf.py
"""CSRF protection for GraphQL endpoints."""

import json
from django.middleware.csrf import CsrfViewMiddleware, get_token
from django.http import JsonResponse
from django.conf import settings


class GraphQLCSRFMiddleware:
    """CSRF protection middleware for GraphQL mutations.

    GraphQL poses unique CSRF challenges because:
    1. All operations go to the same endpoint (/graphql)
    2. Queries should be allowed without CSRF (they're read-only)
    3. Mutations MUST be protected (they modify data)

    This middleware:
    - Allows queries without CSRF token
    - Requires CSRF token for mutations
    - Supports both cookie and header-based CSRF tokens
    """

    SAFE_OPERATIONS = {'query', 'subscription'}
    UNSAFE_OPERATIONS = {'mutation'}

    def __init__(self, get_response):
        self.get_response = get_response
        self.csrf_middleware = CsrfViewMiddleware(get_response)

    def __call__(self, request):
        # Only apply to GraphQL endpoint
        if not request.path.startswith('/graphql'):
            return self.get_response(request)

        # Parse GraphQL operation type
        operation_type = self._get_operation_type(request)

        if operation_type in self.UNSAFE_OPERATIONS:
            # Mutations require CSRF protection
            csrf_check = self._check_csrf(request)
            if csrf_check is not None:
                return csrf_check

        return self.get_response(request)

    def _get_operation_type(self, request) -> str:
        """Extract GraphQL operation type from request.

        Args:
            request: HTTP request object.

        Returns:
            Operation type: 'query', 'mutation', or 'subscription'.
        """
        if request.method != 'POST':
            return 'query'

        try:
            if request.content_type == 'application/json':
                body = json.loads(request.body.decode('utf-8'))
                query = body.get('query', '')
            else:
                query = request.POST.get('query', '')

            query = query.strip().lower()
            if query.startswith('mutation'):
                return 'mutation'
            elif query.startswith('subscription'):
                return 'subscription'
            return 'query'
        except (json.JSONDecodeError, UnicodeDecodeError):
            return 'query'

    def _check_csrf(self, request):
        """Check CSRF token for mutations.

        Args:
            request: HTTP request object.

        Returns:
            JsonResponse with error if CSRF check fails, None if passes.
        """
        # Check for CSRF token in header (preferred for SPAs)
        csrf_token = request.META.get('HTTP_X_CSRFTOKEN', '')

        # Fallback to cookie
        if not csrf_token:
            csrf_token = request.COOKIES.get(settings.CSRF_COOKIE_NAME, '')

        if not csrf_token:
            return JsonResponse(
                {
                    'errors': [{
                        'message': 'CSRF token missing for mutation',
                        'extensions': {
                            'code': 'CSRF_MISSING',
                            'category': 'SECURITY'
                        }
                    }]
                },
                status=403
            )

        # Validate token using Django's CSRF middleware
        request.META['HTTP_X_CSRFTOKEN'] = csrf_token
        reason = self.csrf_middleware._check_token(request)

        if reason:
            return JsonResponse(
                {
                    'errors': [{
                        'message': f'CSRF validation failed: {reason}',
                        'extensions': {
                            'code': 'CSRF_INVALID',
                            'category': 'SECURITY'
                        }
                    }]
                },
                status=403
            )

        return None
```

**Add to Middleware Stack:**

```python
# config/settings/base.py

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'apps.core.middleware.graphql_csrf.GraphQLCSRFMiddleware',  # Add after CsrfViewMiddleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.core.middleware.organisation_context.OrganisationContextMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

**Frontend Integration:**

```javascript
// Frontend must include CSRF token in mutation requests
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value
  || getCookie('csrftoken');

fetch('/graphql', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken,  // Required for mutations
  },
  credentials: 'include',  // Include cookies
  body: JSON.stringify({ query: 'mutation { ... }' }),
});
```

---

##### C5: Email Verification Enforcement Implementation

**Problem**: Unverified users can access full functionality, enabling spam/bot abuse.

**Solution**: Block login for unverified users with clear error messaging.

```python
# apps/core/services/auth_service.py

class AuthService:
    """Authentication service with email verification enforcement."""

    @staticmethod
    def login(email: str, password: str, request) -> dict:
        """Authenticate user with email verification check.

        Args:
            email: User email address.
            password: User password.
            request: HTTP request object.

        Returns:
            Dict with tokens and user data.

        Raises:
            AuthenticationError: If credentials invalid, account locked, or email unverified.
        """
        try:
            user = User.objects.get(email=email.lower())
        except User.DoesNotExist:
            raise AuthenticationError(
                "Invalid credentials",
                code="INVALID_CREDENTIALS"
            )

        # Check account lockout BEFORE password check
        is_locked, remaining = AuthService.check_account_lockout(user)
        if is_locked:
            raise AuthenticationError(
                f"Account temporarily locked. Try again in {remaining} seconds.",
                code="ACCOUNT_LOCKED"
            )

        # Verify password
        if not user.check_password(password):
            AuthService.record_failed_login(user, request)
            raise AuthenticationError(
                "Invalid credentials",
                code="INVALID_CREDENTIALS"
            )

        # Check if account is active
        if not user.is_active:
            raise AuthenticationError(
                "Account is disabled. Contact support.",
                code="ACCOUNT_DISABLED"
            )

        # CRITICAL: Check email verification BEFORE issuing tokens
        if not user.email_verified:
            # Resend verification email automatically
            from apps.core.services.email_service import EmailService
            EmailService.send_verification_email(user)

            raise AuthenticationError(
                "Please verify your email address before logging in. "
                "A new verification email has been sent.",
                code="EMAIL_NOT_VERIFIED"
            )

        # Clear failed login attempts on success
        AuditLog.objects.filter(user=user, action='login_failed').delete()

        # Log successful login
        AuditService.log_event(
            action='login_success',
            user=user,
            request=request
        )

        # Generate tokens
        tokens = TokenService.create_token(user, request)

        return {
            'tokens': tokens,
            'user': user,
            'requires_2fa': user.two_factor_enabled
        }
```

**GraphQL Error Response:**

```python
# api/mutations/auth.py

@strawberry.mutation
def login(self, info: Info, input: LoginInput) -> AuthPayload:
    """Login mutation with proper error handling."""
    try:
        result = AuthService.login(
            email=input.email,
            password=input.password,
            request=info.context.request
        )
        # ... return success
    except AuthenticationError as e:
        raise GraphQLError(
            str(e),
            extensions={
                'code': e.code,
                'category': 'AUTHENTICATION',
                'action': 'VERIFY_EMAIL' if e.code == 'EMAIL_NOT_VERIFIED' else None
            }
        )
```

**Decision Updated:**

The Open Questions section previously stated "No, but limit actions for unverified users".
This is now changed to: **Block login for unverified users** with automatic re-send of
verification email.

---

##### C6: IP Encryption Key Rotation Implementation

**Problem**: If encryption key is compromised, all historical IP addresses are exposed.

**Solution**: Implement key rotation with re-encryption management command.

```python
# apps/core/management/commands/rotate_ip_encryption_key.py
"""Management command to rotate IP encryption key."""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from cryptography.fernet import Fernet, InvalidToken
from apps.core.models import AuditLog, SessionToken, User
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Rotate IP encryption key and re-encrypt all stored IPs.

    Usage:
        python manage.py rotate_ip_encryption_key --old-key=<old> --new-key=<new>

    This command:
    1. Decrypts all stored IPs with the old key
    2. Re-encrypts with the new key
    3. Updates all records in a single transaction
    4. Logs the rotation event

    IMPORTANT: After running, update IP_ENCRYPTION_KEY in environment variables.
    """

    help = 'Rotate IP encryption key and re-encrypt all stored IP addresses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--old-key',
            required=True,
            help='Current IP encryption key (Fernet format)'
        )
        parser.add_argument(
            '--new-key',
            required=True,
            help='New IP encryption key (Fernet format)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Test the rotation without saving changes'
        )

    def handle(self, *args, **options):
        old_key = options['old_key']
        new_key = options['new_key']
        dry_run = options['dry_run']

        # Validate keys
        try:
            old_cipher = Fernet(old_key.encode())
            new_cipher = Fernet(new_key.encode())
        except Exception as e:
            raise CommandError(f"Invalid Fernet key format: {e}")

        self.stdout.write("Starting IP encryption key rotation...")

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be saved"))

        stats = {
            'audit_logs': 0,
            'session_tokens': 0,
            'users': 0,
            'errors': 0,
        }

        try:
            with transaction.atomic():
                # Re-encrypt AuditLog IP addresses
                for log in AuditLog.objects.exclude(ip_address=None).iterator():
                    try:
                        decrypted = old_cipher.decrypt(log.ip_address).decode()
                        log.ip_address = new_cipher.encrypt(decrypted.encode())
                        if not dry_run:
                            log.save(update_fields=['ip_address'])
                        stats['audit_logs'] += 1
                    except InvalidToken:
                        logger.warning(f"Failed to decrypt AuditLog {log.id}")
                        stats['errors'] += 1

                # Re-encrypt SessionToken IP addresses
                for session in SessionToken.objects.exclude(ip_address=None).iterator():
                    try:
                        decrypted = old_cipher.decrypt(session.ip_address).decode()
                        session.ip_address = new_cipher.encrypt(decrypted.encode())
                        if not dry_run:
                            session.save(update_fields=['ip_address'])
                        stats['session_tokens'] += 1
                    except InvalidToken:
                        logger.warning(f"Failed to decrypt SessionToken {session.id}")
                        stats['errors'] += 1

                # Re-encrypt User last_login_ip
                for user in User.objects.exclude(last_login_ip=None).iterator():
                    try:
                        decrypted = old_cipher.decrypt(user.last_login_ip).decode()
                        user.last_login_ip = new_cipher.encrypt(decrypted.encode())
                        if not dry_run:
                            user.save(update_fields=['last_login_ip'])
                        stats['users'] += 1
                    except InvalidToken:
                        logger.warning(f"Failed to decrypt User {user.id} last_login_ip")
                        stats['errors'] += 1

                if dry_run:
                    # Rollback transaction in dry run
                    raise CommandError("DRY RUN COMPLETE - Rolling back transaction")

        except CommandError:
            if dry_run:
                pass  # Expected for dry run
            else:
                raise

        self.stdout.write(self.style.SUCCESS(
            f"\nKey rotation complete:\n"
            f"  Audit logs re-encrypted: {stats['audit_logs']}\n"
            f"  Session tokens re-encrypted: {stats['session_tokens']}\n"
            f"  User IPs re-encrypted: {stats['users']}\n"
            f"  Errors: {stats['errors']}"
        ))

        if not dry_run:
            self.stdout.write(self.style.WARNING(
                "\nIMPORTANT: Update IP_ENCRYPTION_KEY environment variable to the new key!"
            ))
```

**Key Rotation Procedure:**

1. Generate new key: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
2. Dry run: `python manage.py rotate_ip_encryption_key --old-key=<old> --new-key=<new> --dry-run`
3. Execute: `python manage.py rotate_ip_encryption_key --old-key=<old> --new-key=<new>`
4. Update `IP_ENCRYPTION_KEY` in all environment files
5. Deploy new environment variables
6. Securely delete old key from all systems

**Rotation Schedule:**

| Trigger | Action |
|---------|--------|
| Quarterly | Scheduled key rotation |
| Key compromise | Immediate emergency rotation |
| Employee departure | Rotation within 24 hours if they had access |

---

#### High Priority Issue Implementations

##### H1: Composite Indexes for Multi-Tenant Queries

```python
# apps/core/models/user.py

class User(AbstractBaseUser, PermissionsMixin):
    """User model with optimised multi-tenant indexes."""

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            # Primary lookup indexes
            models.Index(fields=['email']),

            # Multi-tenant query optimisation
            models.Index(fields=['organisation', 'email']),
            models.Index(fields=['organisation', 'is_active']),
            models.Index(fields=['organisation', '-created_at']),
            models.Index(fields=['organisation', 'email_verified']),

            # Admin listing indexes
            models.Index(fields=['is_staff', 'is_active']),
        ]
```

##### H2: Token Expiry Indexes

```python
# apps/core/models/base_token.py

class BaseToken(models.Model):
    """Abstract base with expiry index."""

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['expires_at']),
            models.Index(fields=['token']),
        ]


# apps/core/models/session_token.py

class SessionToken(BaseToken):
    """Session token with user+expiry composite index."""

    class Meta:
        db_table = 'session_tokens'
        indexes = [
            models.Index(fields=['user', 'expires_at']),
            models.Index(fields=['token_hash']),
            models.Index(fields=['refresh_token_hash']),
        ]
```

##### H3: AuditLog CASCADE to SET_NULL

Already implemented in the model (line 652 shows `on_delete=models.SET_NULL`).

##### H4: User.organisation Nullable for Platform Superusers

```python
# apps/core/models/user.py

class User(AbstractBaseUser, PermissionsMixin):
    """User model with nullable organisation for platform superusers."""

    organisation = models.ForeignKey(
        'Organisation',
        on_delete=models.CASCADE,
        related_name='users',
        null=True,  # Allow null for platform superusers
        blank=True,
        help_text="Organisation this user belongs to. Null for platform superusers."
    )

    def save(self, *args, **kwargs):
        """Validate organisation is set for non-superusers."""
        if not self.is_superuser and not self.organisation_id:
            raise ValueError("Non-superuser must belong to an organisation")
        super().save(*args, **kwargs)
```

##### H5: Row-Level Security (RLS)

Already implemented in Section "PostgreSQL Row-Level Security (RLS)" with full policy definitions.

##### H6: N+1 Query Prevention with DataLoaders

```python
# api/dataloaders.py
"""GraphQL DataLoaders for N+1 query prevention."""

from strawberry.dataloader import DataLoader
from typing import List
from apps.core.models import User, Organisation, UserProfile


async def load_organisations(keys: List[str]) -> List[Organisation]:
    """Batch load organisations by ID.

    Args:
        keys: List of organisation UUIDs.

    Returns:
        List of Organisation objects in same order as keys.
    """
    orgs = {
        str(org.id): org
        for org in Organisation.objects.filter(id__in=keys)
    }
    return [orgs.get(key) for key in keys]


async def load_user_profiles(keys: List[str]) -> List[UserProfile]:
    """Batch load user profiles by user ID.

    Args:
        keys: List of user UUIDs.

    Returns:
        List of UserProfile objects in same order as keys.
    """
    profiles = {
        str(profile.user_id): profile
        for profile in UserProfile.objects.filter(user_id__in=keys)
    }
    return [profiles.get(key) for key in keys]


class DataLoaderContext:
    """Context class containing all DataLoaders."""

    def __init__(self):
        self.organisation_loader = DataLoader(load_fn=load_organisations)
        self.profile_loader = DataLoader(load_fn=load_user_profiles)


# api/schema.py

@strawberry.type
class User:
    """User type with DataLoader-optimised relations."""

    id: strawberry.ID
    email: str

    @strawberry.field
    async def organisation(self, info: Info) -> Organisation:
        """Load organisation using DataLoader."""
        return await info.context.dataloaders.organisation_loader.load(
            str(self.organisation_id)
        )

    @strawberry.field
    async def profile(self, info: Info) -> Optional[UserProfile]:
        """Load profile using DataLoader."""
        return await info.context.dataloaders.profile_loader.load(str(self.id))
```

##### H7: Race Condition Prevention with Database Locking

```python
# apps/core/services/auth_service.py

from django.db import transaction

class AuthService:
    """Authentication service with race condition prevention."""

    @staticmethod
    @transaction.atomic
    def register_user(email: str, password: str, organisation: Organisation, **kwargs) -> User:
        """Register user with race condition prevention.

        Uses SELECT FOR UPDATE to prevent duplicate user creation.

        Args:
            email: User email address.
            password: Plain text password.
            organisation: Organisation to join.
            **kwargs: Additional user fields.

        Returns:
            Created User instance.

        Raises:
            ValueError: If email already exists.
        """
        # Lock the organisation to prevent concurrent user creation
        Organisation.objects.select_for_update().get(id=organisation.id)

        # Check if user exists (within transaction)
        if User.objects.filter(email=email.lower()).exists():
            raise ValueError("Email already registered")

        # Create user
        user = User.objects.create_user(
            email=email.lower(),
            password=password,
            organisation=organisation,
            **kwargs
        )

        return user


class TokenService:
    """Token service with race condition prevention."""

    @staticmethod
    @transaction.atomic
    def create_unique_token() -> str:
        """Generate a unique token with collision prevention.

        Uses SELECT FOR UPDATE SKIP LOCKED pattern.
        """
        max_attempts = 5
        for _ in range(max_attempts):
            token = secrets.token_urlsafe(32)
            token_hash = TokenHasher.hash_token(token)

            # Check uniqueness with lock
            if not SessionToken.objects.select_for_update(skip_locked=True).filter(
                token_hash=token_hash
            ).exists():
                return token

        raise RuntimeError("Failed to generate unique token after max attempts")
```

##### H8: Token Revocation on Password Change

```python
# apps/core/services/auth_service.py

class AuthService:
    """Authentication service with token revocation on password change."""

    @staticmethod
    def change_password(user: User, current_password: str, new_password: str, request) -> bool:
        """Change user password and revoke all sessions.

        Args:
            user: User changing password.
            current_password: Current password for verification.
            new_password: New password to set.
            request: HTTP request for audit logging.

        Returns:
            True if password changed successfully.

        Raises:
            AuthenticationError: If current password is wrong.
        """
        # Verify current password
        if not user.check_password(current_password):
            raise AuthenticationError("Current password is incorrect")

        # Set new password
        user.set_password(new_password)
        user.save()

        # CRITICAL: Revoke ALL existing sessions
        TokenService.revoke_all_user_tokens(user)

        # Log the event
        AuditService.log_event(
            action='password_change',
            user=user,
            request=request,
            metadata={'sessions_revoked': True}
        )

        return True


class TokenService:
    """Token service with bulk revocation."""

    @staticmethod
    def revoke_all_user_tokens(user: User) -> int:
        """Revoke all tokens for a user.

        Args:
            user: User whose tokens to revoke.

        Returns:
            Number of tokens revoked.
        """
        sessions = SessionToken.objects.filter(user=user)
        count = sessions.count()

        for session in sessions:
            # Add to Redis blacklist
            TokenService.redis_client.setex(
                f"blacklist:{session.token_hash}",
                86400,  # 24 hours
                '1'
            )
            # Remove from active tokens
            TokenService.redis_client.delete(f"token:{session.token_hash}")
            TokenService.redis_client.delete(f"refresh:{session.refresh_token_hash}")

        # Delete from database
        sessions.delete()

        return count
```

##### H9: Refresh Token Replay Detection

```python
# apps/core/models/session_token.py

class SessionToken(BaseToken):
    """Session token with refresh token family tracking for replay detection."""

    token_family = models.UUIDField(
        default=uuid.uuid4,
        help_text="Token family ID for replay detection"
    )
    is_refresh_token_used = models.BooleanField(
        default=False,
        help_text="True if refresh token has been used (rotation)"
    )


# apps/core/services/token_service.py

class TokenService:
    """Token service with refresh token replay detection."""

    @staticmethod
    def refresh_access_token(refresh_token: str, request) -> dict:
        """Refresh access token with replay detection.

        If a refresh token is used twice, the entire token family is revoked
        (indicates the token was stolen and used by an attacker).

        Args:
            refresh_token: Current refresh token.
            request: HTTP request object.

        Returns:
            New tokens dict.

        Raises:
            AuthenticationError: If token invalid or replay detected.
        """
        refresh_hash = TokenHasher.hash_token(refresh_token)

        try:
            session = SessionToken.objects.select_for_update().get(
                refresh_token_hash=refresh_hash,
                expires_at__gt=timezone.now()
            )
        except SessionToken.DoesNotExist:
            raise AuthenticationError("Invalid refresh token")

        # REPLAY DETECTION: Check if refresh token was already used
        if session.is_refresh_token_used:
            # Token was already used! This is a replay attack.
            # Revoke the ENTIRE token family
            family_sessions = SessionToken.objects.filter(
                token_family=session.token_family
            )
            for s in family_sessions:
                TokenService._blacklist_token(s.token_hash)

            family_sessions.delete()

            # Log security event
            AuditService.log_event(
                action='refresh_token_replay_detected',
                user=session.user,
                request=request,
                metadata={
                    'token_family': str(session.token_family),
                    'sessions_revoked': family_sessions.count()
                }
            )

            raise AuthenticationError(
                "Security alert: Token replay detected. All sessions have been revoked.",
                code="TOKEN_REPLAY_DETECTED"
            )

        # Mark refresh token as used
        session.is_refresh_token_used = True
        session.save(update_fields=['is_refresh_token_used'])

        # Create new token pair in same family
        return TokenService.create_token(
            user=session.user,
            request=request,
            token_family=session.token_family  # Keep same family
        )
```

##### H10: HaveIBeenPwned Password Breach Checking

```python
# apps/core/utils/password_breach_check.py
"""Password breach checking using HaveIBeenPwned API."""

import hashlib
import httpx
from typing import Tuple


class PasswordBreachChecker:
    """Check passwords against HaveIBeenPwned database.

    Uses k-Anonymity model:
    - Only first 5 chars of SHA-1 hash are sent to API
    - API returns all hashes starting with those 5 chars
    - We check locally if full hash is in the list
    - Password never leaves the server
    """

    HIBP_API_URL = "https://api.pwnedpasswords.com/range/"
    TIMEOUT = 5.0  # seconds

    @staticmethod
    def check_password(password: str) -> Tuple[bool, int]:
        """Check if password has been exposed in data breaches.

        Args:
            password: Plain text password to check.

        Returns:
            Tuple of (is_breached: bool, breach_count: int).
            If API is unavailable, returns (False, 0) to not block users.
        """
        # SHA-1 hash of password (HIBP uses SHA-1)
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]

        try:
            with httpx.Client(timeout=PasswordBreachChecker.TIMEOUT) as client:
                response = client.get(f"{PasswordBreachChecker.HIBP_API_URL}{prefix}")

            if response.status_code != 200:
                # API error - don't block user
                return False, 0

            # Check if suffix is in response
            for line in response.text.splitlines():
                hash_suffix, count = line.split(':')
                if hash_suffix == suffix:
                    return True, int(count)

            return False, 0

        except (httpx.RequestError, httpx.TimeoutException):
            # Network error - don't block user
            return False, 0


# apps/core/validators.py

from django.core.exceptions import ValidationError

def validate_password_not_breached(password: str) -> None:
    """Validator to check password against HIBP.

    Args:
        password: Password to validate.

    Raises:
        ValidationError: If password has been exposed in breaches.
    """
    is_breached, count = PasswordBreachChecker.check_password(password)

    if is_breached:
        raise ValidationError(
            f"This password has been exposed in {count:,} data breaches. "
            "Please choose a different password.",
            code='password_breached'
        )
```

**Add to Django Password Validators:**

```python
# config/settings/base.py

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'apps.core.validators.PasswordBreachValidator'},  # HIBP check
]
```

##### H11: JWT Algorithm and Key Rotation

```python
# config/settings/base.py

# JWT Configuration
JWT_ALGORITHM = 'RS256'  # Asymmetric for future microservices
JWT_PRIVATE_KEY_PATH = env('JWT_PRIVATE_KEY_PATH', default=None)
JWT_PUBLIC_KEY_PATH = env('JWT_PUBLIC_KEY_PATH', default=None)

# Fallback to HS256 with secret for simpler deployments
JWT_SECRET_KEY = env('JWT_SECRET_KEY', default=SECRET_KEY)

# Key rotation support
JWT_KEY_ID = env('JWT_KEY_ID', default='key-1')  # Include in JWT header for rotation
JWT_PREVIOUS_KEYS = env.list('JWT_PREVIOUS_KEYS', default=[])  # Accept tokens from previous keys


# apps/core/services/jwt_service.py

import jwt
from datetime import datetime, timedelta
from django.conf import settings
from pathlib import Path


class JWTService:
    """JWT service with RS256 and key rotation support."""

    @staticmethod
    def _get_private_key() -> str:
        """Load private key for signing."""
        if settings.JWT_PRIVATE_KEY_PATH:
            return Path(settings.JWT_PRIVATE_KEY_PATH).read_text()
        return settings.JWT_SECRET_KEY

    @staticmethod
    def _get_public_key() -> str:
        """Load public key for verification."""
        if settings.JWT_PUBLIC_KEY_PATH:
            return Path(settings.JWT_PUBLIC_KEY_PATH).read_text()
        return settings.JWT_SECRET_KEY

    @staticmethod
    def create_token(user_id: str, expires_delta: timedelta = timedelta(hours=24)) -> str:
        """Create a signed JWT.

        Args:
            user_id: User ID to encode.
            expires_delta: Token validity period.

        Returns:
            Signed JWT string.
        """
        payload = {
            'sub': user_id,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + expires_delta,
            'jti': str(uuid.uuid4()),
        }

        return jwt.encode(
            payload,
            JWTService._get_private_key(),
            algorithm=settings.JWT_ALGORITHM,
            headers={'kid': settings.JWT_KEY_ID}  # Key ID for rotation
        )

    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode a JWT.

        Supports key rotation by trying current and previous keys.

        Args:
            token: JWT string.

        Returns:
            Decoded payload dict.

        Raises:
            jwt.InvalidTokenError: If token is invalid.
        """
        # Get key ID from token header
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid', settings.JWT_KEY_ID)

        # Try current key first
        try:
            return jwt.decode(
                token,
                JWTService._get_public_key(),
                algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.InvalidSignatureError:
            # Try previous keys for rotation
            for prev_key in settings.JWT_PREVIOUS_KEYS:
                try:
                    return jwt.decode(
                        token,
                        prev_key,
                        algorithms=[settings.JWT_ALGORITHM]
                    )
                except jwt.InvalidSignatureError:
                    continue

            raise jwt.InvalidSignatureError("Token signature invalid")
```

##### H12: Concurrent Session Limit

Already implemented in TokenService.create_token() (lines 1785-1791) with 5 session limit.

##### H13: Account Lockout Mechanism

Already implemented in Section "Account Lockout Mechanism" (lines 2043-2190).

##### H14-15: Security Tests

```python
# tests/security/test_graphql_security.py
"""Security tests for GraphQL API."""

import pytest
from django.test import Client


@pytest.mark.security
class TestGraphQLQueryDepthLimiting:
    """Test GraphQL query depth limiting."""

    def test_deep_query_rejected(self, client: Client) -> None:
        """Test that deeply nested queries are rejected.

        Given: A query with depth > 10
        When: Query is executed
        Then: Error returned with depth limit message
        """
        deep_query = """
        query {
            me {
                organisation {
                    users {
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
            }
        }
        """

        response = client.post('/graphql', {'query': deep_query})

        assert response.status_code == 400
        assert 'depth' in response.json()['errors'][0]['message'].lower()


@pytest.mark.security
class TestCSRFProtection:
    """Test CSRF protection on mutations."""

    def test_mutation_without_csrf_rejected(self, client: Client) -> None:
        """Test mutations require CSRF token."""
        mutation = 'mutation { logout }'

        response = client.post(
            '/graphql',
            {'query': mutation},
            content_type='application/json'
            # No CSRF token
        )

        assert response.status_code == 403
        assert 'csrf' in response.json()['errors'][0]['message'].lower()

    def test_query_without_csrf_allowed(self, client: Client) -> None:
        """Test queries don't require CSRF token."""
        query = 'query { me { email } }'

        response = client.post(
            '/graphql',
            {'query': query},
            content_type='application/json'
        )

        # Should succeed (may return null if not authenticated, but not 403)
        assert response.status_code != 403


@pytest.mark.security
class TestXSSPrevention:
    """Test XSS prevention in user inputs."""

    def test_script_tags_escaped_in_name(self, authenticated_client, user) -> None:
        """Test script tags in user name are escaped."""
        mutation = """
        mutation UpdateProfile($input: UpdateProfileInput!) {
            updateProfile(input: $input) {
                firstName
            }
        }
        """

        response = authenticated_client.post('/graphql', {
            'query': mutation,
            'variables': {
                'input': {
                    'firstName': '<script>alert("xss")</script>'
                }
            }
        })

        data = response.json()
        # Should be escaped or rejected
        assert '<script>' not in data.get('data', {}).get('updateProfile', {}).get('firstName', '')


@pytest.mark.security
class TestSQLInjectionPrevention:
    """Test SQL injection prevention."""

    def test_sql_injection_in_email_login(self, client: Client) -> None:
        """Test SQL injection in login email is prevented."""
        mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                token
            }
        }
        """

        response = client.post('/graphql', {
            'query': mutation,
            'variables': {
                'input': {
                    'email': "' OR '1'='1",
                    'password': "password123"
                }
            }
        })

        # Should fail validation, not return data
        data = response.json()
        assert 'token' not in str(data)
```

---

#### Medium Priority Issue Implementations

##### M1: Module-Level Docstrings

All code examples now include module-level docstrings (see implementations above).

##### M2: Instance Methods with Dependency Injection

```python
# apps/core/services/auth_service.py
"""Authentication service with dependency injection."""

from dataclasses import dataclass


@dataclass
class AuthService:
    """Authentication service with injected dependencies.

    Attributes:
        token_service: Service for token operations.
        email_service: Service for email operations.
        audit_service: Service for audit logging.
    """

    token_service: 'TokenService'
    email_service: 'EmailService'
    audit_service: 'AuditService'

    def login(self, email: str, password: str, request) -> dict:
        """Login with injected services."""
        # Use self.token_service instead of static TokenService
        tokens = self.token_service.create_token(user, request)
        self.audit_service.log_event('login_success', user, request)
        return {'tokens': tokens, 'user': user}


# Dependency injection container
class ServiceContainer:
    """Simple DI container for services."""

    _instance = None

    def __init__(self):
        self.token_service = TokenService()
        self.email_service = EmailService()
        self.audit_service = AuditService()
        self.auth_service = AuthService(
            token_service=self.token_service,
            email_service=self.email_service,
            audit_service=self.audit_service
        )

    @classmethod
    def get(cls) -> 'ServiceContainer':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
```

##### M3: Django Password Validators

```python
# config/settings/base.py

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'apps.core.validators.PasswordBreachValidator',
    },
    {
        'NAME': 'apps.core.validators.PasswordComplexityValidator',
    },
]


# apps/core/validators.py

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
import re


class PasswordComplexityValidator:
    """Validate password has required character types."""

    def validate(self, password: str, user=None) -> None:
        """Validate password complexity.

        Args:
            password: Password to validate.
            user: Optional user instance.

        Raises:
            ValidationError: If password doesn't meet requirements.
        """
        errors = []

        if not re.search(r'[A-Z]', password):
            errors.append(_("Password must contain at least one uppercase letter."))

        if not re.search(r'[a-z]', password):
            errors.append(_("Password must contain at least one lowercase letter."))

        if not re.search(r'\d', password):
            errors.append(_("Password must contain at least one digit."))

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append(_("Password must contain at least one special character."))

        if errors:
            raise ValidationError(errors)

    def get_help_text(self) -> str:
        return _(
            "Password must contain at least one uppercase letter, "
            "one lowercase letter, one digit, and one special character."
        )
```

##### M4: Error Messages with Codes

```python
# apps/core/exceptions.py
"""Custom exceptions with error codes and guidance."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AuthenticationError(Exception):
    """Authentication error with code and guidance.

    Attributes:
        message: Human-readable error message.
        code: Machine-readable error code.
        guidance: Actionable guidance for the user.
    """

    message: str
    code: str = "AUTHENTICATION_ERROR"
    guidance: Optional[str] = None

    def __str__(self) -> str:
        return self.message

    def to_dict(self) -> dict:
        """Convert to dictionary for API response."""
        return {
            'message': self.message,
            'code': self.code,
            'guidance': self.guidance,
        }


# Usage
raise AuthenticationError(
    message="Invalid credentials",
    code="INVALID_CREDENTIALS",
    guidance="Please check your email and password and try again."
)

raise AuthenticationError(
    message="Account temporarily locked",
    code="ACCOUNT_LOCKED",
    guidance="Too many failed login attempts. Please wait 15 minutes or reset your password."
)

raise AuthenticationError(
    message="Email not verified",
    code="EMAIL_NOT_VERIFIED",
    guidance="Please check your inbox for a verification email. Click 'Resend' if needed."
)
```

##### M5: Email Service Failure Handling

```python
# apps/core/services/email_service.py
"""Email service with retry and fallback handling."""

import logging
from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class EmailService:
    """Email service with retry logic and failure handling."""

    @staticmethod
    @shared_task(bind=True, max_retries=3)
    def send_email_async(self, to_email: str, subject: str, body: str, html_body: str = None):
        """Send email asynchronously with retries.

        Args:
            to_email: Recipient email address.
            subject: Email subject.
            body: Plain text body.
            html_body: Optional HTML body.
        """
        try:
            msg = EmailMessage(
                subject=subject,
                body=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[to_email],
            )
            if html_body:
                msg.content_subtype = 'html'
                msg.body = html_body

            msg.send(fail_silently=False)
            logger.info(f"Email sent to {to_email}: {subject}")

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            # Retry with exponential backoff
            raise self.retry(exc=e, countdown=2 ** self.request.retries)

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def send_email_sync(to_email: str, subject: str, body: str) -> bool:
        """Send email synchronously with retry.

        For critical emails that must be sent immediately.
        """
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[to_email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"Sync email failed to {to_email}: {e}")
            raise

    @staticmethod
    def send_verification_email(user) -> None:
        """Send verification email with error handling."""
        try:
            token = EmailVerificationService.create_token(user)
            EmailService.send_email_async.delay(
                to_email=user.email,
                subject="Verify your email address",
                body=f"Click here to verify: {settings.FRONTEND_URL}/verify?token={token}"
            )
        except Exception as e:
            # Log but don't fail registration
            logger.error(f"Failed to queue verification email for {user.email}: {e}")
            # Store for retry later
            FailedEmail.objects.create(
                user=user,
                email_type='verification',
                error=str(e)
            )
```

##### M6: Timezone Handling

```python
# apps/core/utils/timezone.py
"""Timezone utilities for consistent handling."""

from datetime import datetime
from django.utils import timezone
import pytz


class TimezoneHandler:
    """Utilities for consistent timezone handling.

    All internal storage uses UTC. User-facing displays convert to user timezone.
    """

    @staticmethod
    def now_utc() -> datetime:
        """Get current time in UTC."""
        return timezone.now()

    @staticmethod
    def to_user_timezone(dt: datetime, user_timezone: str) -> datetime:
        """Convert datetime to user's timezone.

        Args:
            dt: Datetime in UTC.
            user_timezone: User's timezone string (e.g., 'Europe/London').

        Returns:
            Datetime in user's timezone.
        """
        if dt.tzinfo is None:
            dt = pytz.UTC.localize(dt)

        try:
            user_tz = pytz.timezone(user_timezone)
            return dt.astimezone(user_tz)
        except pytz.UnknownTimeZoneError:
            # Fall back to UTC
            return dt

    @staticmethod
    def handle_dst_edge_case(dt: datetime, user_timezone: str) -> datetime:
        """Handle DST transitions correctly.

        During DST transitions, some times may be ambiguous or non-existent.
        This method handles these cases gracefully.
        """
        user_tz = pytz.timezone(user_timezone)

        try:
            return user_tz.localize(dt, is_dst=None)
        except pytz.AmbiguousTimeError:
            # During fall-back, assume the first occurrence
            return user_tz.localize(dt, is_dst=True)
        except pytz.NonExistentTimeError:
            # During spring-forward, shift forward
            return user_tz.localize(dt, is_dst=False)
```

##### M7: User Enumeration Prevention

```python
# apps/core/services/auth_service.py

class AuthService:
    """Authentication service with user enumeration prevention."""

    @staticmethod
    def login(email: str, password: str, request) -> dict:
        """Login with timing-safe user enumeration prevention."""
        import time
        import secrets

        start_time = time.monotonic()

        try:
            user = User.objects.get(email=email.lower())
            password_valid = user.check_password(password)
        except User.DoesNotExist:
            # IMPORTANT: Still hash a password to prevent timing attacks
            # This makes the response time similar whether user exists or not
            from django.contrib.auth.hashers import check_password
            check_password(password, "pbkdf2_sha256$fake$hash")
            password_valid = False
            user = None

        # Ensure consistent response time (prevents timing attacks)
        elapsed = time.monotonic() - start_time
        min_time = 0.2  # 200ms minimum
        if elapsed < min_time:
            time.sleep(min_time - elapsed)

        if not password_valid:
            # Same error message whether user exists or not
            raise AuthenticationError(
                "Invalid credentials",
                code="INVALID_CREDENTIALS"
            )

        # Continue with login...
```

##### M8: Password History

```python
# apps/core/models/password_history.py
"""Password history model for reuse prevention."""

from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import uuid


class PasswordHistory(models.Model):
    """Stores hashed previous passwords to prevent reuse.

    Attributes:
        user: User this password belonged to.
        password_hash: Argon2 hash of the password.
        created_at: When this password was set.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='password_history'
    )
    password_hash = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'password_history'
        ordering = ['-created_at']


# apps/core/validators.py

class PasswordHistoryValidator:
    """Validate password hasn't been used recently."""

    HISTORY_COUNT = 5  # Check last 5 passwords

    def validate(self, password: str, user=None) -> None:
        """Check password against history."""
        if user is None:
            return

        recent_passwords = PasswordHistory.objects.filter(
            user=user
        ).order_by('-created_at')[:self.HISTORY_COUNT]

        for history in recent_passwords:
            if check_password(password, history.password_hash):
                raise ValidationError(
                    f"Cannot reuse any of your last {self.HISTORY_COUNT} passwords.",
                    code='password_reused'
                )

    def get_help_text(self) -> str:
        return f"Cannot reuse any of your last {self.HISTORY_COUNT} passwords."
```

##### M9: 2FA Backup Codes

```python
# apps/core/models/backup_code.py
"""2FA backup codes for account recovery."""

import secrets
import hashlib
from django.db import models
import uuid


class BackupCode(models.Model):
    """One-time backup codes for 2FA recovery.

    Attributes:
        user: User this code belongs to.
        code_hash: SHA-256 hash of the backup code.
        used: Whether the code has been used.
        created_at: When the code was created.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='backup_codes'
    )
    code_hash = models.CharField(max_length=64)
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'backup_codes'


class BackupCodeService:
    """Service for managing 2FA backup codes."""

    CODE_COUNT = 10
    CODE_LENGTH = 8

    @staticmethod
    def generate_codes(user) -> list[str]:
        """Generate new backup codes for a user.

        Invalidates any existing codes and creates new ones.

        Args:
            user: User to generate codes for.

        Returns:
            List of plain text codes (shown once to user).
        """
        # Delete existing codes
        BackupCode.objects.filter(user=user).delete()

        plain_codes = []
        for _ in range(BackupCodeService.CODE_COUNT):
            # Generate 8-character alphanumeric code
            code = secrets.token_hex(4).upper()  # e.g., "A1B2C3D4"
            plain_codes.append(code)

            # Store hash
            BackupCode.objects.create(
                user=user,
                code_hash=hashlib.sha256(code.encode()).hexdigest()
            )

        return plain_codes

    @staticmethod
    def verify_code(user, code: str) -> bool:
        """Verify and consume a backup code.

        Args:
            user: User attempting to use code.
            code: Backup code to verify.

        Returns:
            True if code is valid and unused.
        """
        code_hash = hashlib.sha256(code.upper().encode()).hexdigest()

        try:
            backup_code = BackupCode.objects.get(
                user=user,
                code_hash=code_hash,
                used=False
            )
            # Mark as used
            backup_code.used = True
            backup_code.used_at = timezone.now()
            backup_code.save()
            return True
        except BackupCode.DoesNotExist:
            return False
```

##### M10: JWT Token Payload Structure

```python
# docs: JWT Token Payload Structure

"""
JWT Access Token Payload:
{
    "sub": "user-uuid",           # Subject (user ID)
    "iat": 1704067200,            # Issued at (Unix timestamp)
    "exp": 1704153600,            # Expires at (Unix timestamp)
    "jti": "token-uuid",          # JWT ID (unique identifier)
    "type": "access",             # Token type
    "org": "organisation-uuid",   # Organisation ID
    "email": "user@example.com",  # User email
    "roles": ["member"],          # User roles/groups
    "verified": true,             # Email verified status
    "2fa": false                  # 2FA enabled status
}

JWT Refresh Token Payload:
{
    "sub": "user-uuid",
    "iat": 1704067200,
    "exp": 1706659200,            # 30 days
    "jti": "refresh-token-uuid",
    "type": "refresh",
    "family": "token-family-uuid" # For replay detection
}
"""
```

---

#### Edge Cases Coverage

The following 27 edge cases from QA review are now addressed:

| # | Edge Case | Resolution |
|---|-----------|------------|
| 1 | Empty email/password | Input validation in GraphQL schema |
| 2 | Email with leading/trailing spaces | `.strip().lower()` normalisation |
| 3 | Unicode in names | Django CharField handles UTF-8 |
| 4 | Very long passwords (>128 chars) | MaxLengthValidator(128) |
| 5 | SQL injection in email | Parameterised queries via ORM |
| 6 | XSS in user fields | Output escaping in GraphQL |
| 7 | CSRF on mutations | GraphQLCSRFMiddleware |
| 8 | Concurrent session creation | SELECT FOR UPDATE locking |
| 9 | Token collision | Retry with unique check |
| 10 | Expired token usage | expires_at check in validation |
| 11 | Revoked token replay | Redis blacklist check |
| 12 | Password reset token reuse | `used` flag on token model |
| 13 | 2FA code timing attack | Constant-time TOTP comparison |
| 14 | Backup code enumeration | Same response for valid/invalid |
| 15 | Rate limit bypass (IP spoofing) | X-Forwarded-For validation |
| 16 | Organisation boundary bypass | RLS + resolver checks |
| 17 | Superuser org access | RLS bypass flag |
| 18 | Deleted user token usage | is_active check on validation |
| 19 | Email change invalidation | Require re-verification |
| 20 | Password change session handling | Revoke all tokens on change |
| 21 | Timezone DST edge cases | pytz DST handling utilities |
| 22 | Leap second handling | Django timezone.now() handles |
| 23 | Redis unavailability | Graceful degradation to DB |
| 24 | Database connection pool exhaustion | PgBouncer connection pooling |
| 25 | Very long user agent strings | TextField with max_length check |
| 26 | Malformed JWT | Exception handling in decode |
| 27 | Key rotation during active sessions | Previous key acceptance period |

---

## Executive Summary

This plan outlines the implementation of a secure, enterprise-grade authentication system for the
Django backend template. The system provides user registration, login, two-factor authentication
(2FA), password reset, email verification, and comprehensive audit logging with multi-tenancy
support.

**Key Features:**

- User registration and login
- Email/password authentication
- Two-factor authentication (TOTP)
- Password reset via email
- Email verification
- Session management with JWT tokens
- IP address encryption
- Comprehensive audit logging
- Multi-tenancy via organisation boundaries
- Rate limiting and security controls
- Django Groups and permissions for RBAC
- Extensibility for future role models

**Out of Scope for US-001:**

- **Organisation Invitations** - Deferred to US-004 (Organisation Setup)
- **OAuth/Social Login** - Deferred to Phase 11 (Third-Party Integrations)
- **SSO for SaaS Products** - Deferred to Phases 8-12
- **Website-Level Permissions** - Deferred to Phase 4+

**Technology Stack:**

- Django 6.0 custom user model
- Strawberry GraphQL for API
- TOTP-based 2FA
- Argon2 password hashing
- PostgreSQL 18
- Redis for session storage and rate limiting
- Cryptography library for IP encryption

---

## Requirements

### Core Requirements

1. **User Registration**
   - Users can register with email and password
   - Email addresses must be unique across the system
   - Passwords must meet security requirements
   - Users are associated with an organisation
   - Email verification required before full access

2. **User Login**
   - Users can log in with email and password
   - Optional two-factor authentication (TOTP)
   - Session tokens expire after inactivity
   - Failed login attempts are tracked and rate-limited

3. **Two-Factor Authentication (2FA)**
   - TOTP-based (compatible with Google Authenticator, Authy, etc.)
   - Users can enable/disable 2FA
   - Backup codes for account recovery
   - QR code generation for easy setup

4. **Password Management**
   - Password reset via email link
   - Password change for authenticated users
   - Password history to prevent reuse
   - Secure password hashing (Argon2)

5. **Email Verification**
   - Verification email sent on registration
   - Verification link with expiring token
   - Resend verification email option

### Security Requirements

1. **Password Security**
   - Minimum 12 characters
   - Maximum 128 characters
   - At least one uppercase letter
   - At least one lowercase letter
   - At least one number
   - At least one special character
   - Passwords hashed with Argon2

2. **Session Security**
   - JWT tokens for authentication
   - Tokens expire after 24 hours of inactivity
   - Tokens stored in Redis for revocation
   - Refresh token rotation

3. **IP Address Encryption**
   - All IP addresses encrypted before storage
   - Fernet symmetric encryption
   - Encryption key stored in environment variables

4. **Audit Logging**
   - All authentication events logged
   - User actions tracked with timestamp
   - IP addresses logged (encrypted)
   - Immutable audit trail

5. **Rate Limiting**
   - Login attempts: 5 per 15 minutes per IP
   - Registration attempts: 3 per hour per IP
   - Password reset: 3 per hour per email
   - 2FA attempts: 5 per 15 minutes per user

### Multi-Tenancy Requirements

1. **Organisation Isolation**
   - Each user belongs to one organisation
   - Users can only access their organisation's data
   - GraphQL queries enforce organisation boundaries
   - Audit logs scoped to organisations

2. **Organisation Management**
   - Organisations have unique slugs
   - Organisation owners can manage users
   - Role-based access control within organisations

### Non-Functional Requirements

1. **Performance**
   - Login response time: < 200ms (without 2FA)
   - Registration response time: < 500ms
   - Password hashing: < 300ms (Argon2)
   - GraphQL queries: < 100ms (cached)

2. **Scalability**
   - Support for 10,000+ users per organisation
   - Horizontal scaling via Redis sessions
   - Database query optimisation

3. **Availability**
   - 99.9% uptime target
   - Graceful degradation if Redis unavailable
   - Database failover support

4. **Compliance**
   - GDPR-compliant data handling
   - Right to be forgotten (user deletion)
   - Data export capability
   - Audit trail for compliance

---

## Technical Design

### Database Schema

#### User Model

Extends Django's `AbstractBaseUser` and `PermissionsMixin`.

```python
# apps/core/models/user.py

class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model for authentication.

    Extends Django's AbstractBaseUser to use email as the username field
    and adds multi-tenancy support via organisation foreign key.

    Attributes:
        email: Unique email address (username field)
        first_name: User's first name
        last_name: User's last name
        organisation: Foreign key to Organisation (multi-tenancy)
        is_active: Whether the user account is active
        is_staff: Whether user can access Django admin
        is_superuser: Whether user has all permissions
        email_verified: Whether email has been verified
        email_verified_at: Timestamp of email verification
        two_factor_enabled: Whether 2FA is enabled
        last_login_ip: Last login IP address (encrypted)
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """

    # Fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)

    # Multi-tenancy
    organisation = models.ForeignKey(
        'Organisation',
        on_delete=models.CASCADE,
        related_name='users'
    )

    # Status flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    # Email verification
    email_verified = models.BooleanField(default=False)
    email_verified_at = models.DateTimeField(null=True, blank=True)

    # Two-factor authentication
    two_factor_enabled = models.BooleanField(default=False)

    # Security tracking
    last_login_ip = models.BinaryField(null=True, blank=True)  # Encrypted

    # SaaS product integration flags (for future phases)
    has_email_account = models.BooleanField(default=False)
    has_vault_access = models.BooleanField(default=False)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['organisation', '-created_at']),
        ]
```

#### Organisation Model

```python
# apps/core/models/organisation.py

class Organisation(models.Model):
    """Represents an organisation for multi-tenancy.

    Each organisation is a separate tenant with isolated data.

    Attributes:
        name: Organisation name
        slug: URL-safe unique identifier
        industry: Industry category
        is_active: Whether organisation is active
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    industry = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'organisations'
        ordering = ['name']
        indexes = [
            models.Index(fields=['slug']),
        ]
```

#### UserProfile Model

```python
# apps/core/models/user_profile.py

class UserProfile(models.Model):
    """Extended user profile information.

    Stores additional user data that's not directly related to authentication.

    Attributes:
        user: One-to-one relationship with User
        phone: Phone number
        avatar: Profile picture URL
        timezone: User's timezone
        language: Preferred language
        bio: User biography
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.URLField(blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    bio = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_profiles'
```

#### TOTPDevice Model (2FA)

```python
# apps/core/models/totp_device.py

class TOTPDevice(models.Model):
    """TOTP device for two-factor authentication.

    Stores TOTP secret keys for users who enable 2FA.

    Attributes:
        user: Foreign key to User
        name: Device name (e.g., "Google Authenticator")
        secret: TOTP secret key (encrypted)
        confirmed: Whether device has been confirmed
        last_used_at: Last successful use timestamp
        created_at: Creation timestamp
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='totp_devices')
    name = models.CharField(max_length=100, default='Default')
    secret = models.CharField(max_length=255)  # Encrypted
    confirmed = models.BooleanField(default=False)
    last_used_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'totp_devices'
        ordering = ['-created_at']
```

#### AuditLog Model

```python
# apps/core/models/audit_log.py

class AuditLog(models.Model):
    """Immutable audit log for tracking user actions.

    Records all authentication and security-related events.

    Attributes:
        user: Foreign key to User (nullable for failed login attempts)
        organisation: Foreign key to Organisation
        action: Type of action performed
        ip_address: IP address (encrypted)
        user_agent: Browser user agent
        metadata: Additional JSON metadata
        created_at: Timestamp of the action
    """

    ACTION_CHOICES = [
        ('login_success', 'Login Success'),
        ('login_failed', 'Login Failed'),
        ('logout', 'Logout'),
        ('register', 'Registration'),
        ('password_reset_request', 'Password Reset Request'),
        ('password_reset_complete', 'Password Reset Complete'),
        ('password_change', 'Password Change'),
        ('email_verify', 'Email Verification'),
        ('2fa_enable', '2FA Enabled'),
        ('2fa_disable', '2FA Disabled'),
        ('2fa_verify_success', '2FA Verification Success'),
        ('2fa_verify_failed', '2FA Verification Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    organisation = models.ForeignKey(
        Organisation,
        on_delete=models.CASCADE,
        related_name='audit_logs',
        null=True,
        blank=True
    )
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    ip_address = models.BinaryField()  # Encrypted
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['organisation', '-created_at']),
            models.Index(fields=['action', '-created_at']),
        ]
```

#### SessionToken Model

```python
# apps/core/models/session_token.py

class SessionToken(models.Model):
    """Session tokens for authenticated users.

    Stores JWT tokens in database for revocation and tracking.
    Also cached in Redis for fast lookup.

    Attributes:
        user: Foreign key to User
        token: JWT token hash
        refresh_token: Refresh token hash
        ip_address: IP address (encrypted)
        user_agent: Browser user agent
        expires_at: Token expiration timestamp
        last_activity: Last activity timestamp
        created_at: Creation timestamp
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    token_hash = models.CharField(max_length=255, unique=True)
    refresh_token_hash = models.CharField(max_length=255, unique=True)
    ip_address = models.BinaryField()  # Encrypted
    user_agent = models.TextField(blank=True)
    expires_at = models.DateTimeField()
    last_activity = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'session_tokens'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['token_hash']),
        ]
```

#### PasswordResetToken Model

```python
# apps/core/models/password_reset_token.py

class PasswordResetToken(models.Model):
    """Token for password reset requests.

    Attributes:
        user: Foreign key to User
        token: Reset token (hashed)
        expires_at: Token expiration (15 minutes)
        used: Whether token has been used
        created_at: Creation timestamp
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'password_reset_tokens'
        ordering = ['-created_at']
```

#### EmailVerificationToken Model

```python
# apps/core/models/email_verification_token.py

class EmailVerificationToken(models.Model):
    """Token for email verification.

    Attributes:
        user: Foreign key to User
        token: Verification token (hashed)
        expires_at: Token expiration (24 hours)
        verified: Whether email has been verified
        created_at: Creation timestamp
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='verification_tokens'
    )
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'email_verification_tokens'
        ordering = ['-created_at']
```

#### Abstract BaseToken Model (DRY Principle)

To reduce duplication between `SessionToken`, `PasswordResetToken`, and `EmailVerificationToken`,
create an abstract base class:

> **IMPORTANT: Token Hashing Standard**
>
> ALL tokens in this system use **HMAC-SHA256** via the `TokenHasher` utility (see [C1](#c1-session-token-storage---hmac-sha256-implementation)).
> This applies to:
> - Session tokens (access and refresh)
> - Password reset tokens
> - Email verification tokens
>
> Plain SHA-256 is NOT used because it doesn't protect against attackers with database access.

```python
# apps/core/models/base_token.py

class BaseToken(models.Model):
    """Abstract base class for all token models.

    Provides common fields and functionality for tokens used throughout
    the authentication system.

    IMPORTANT: The `token` field stores HMAC-SHA256 hashes, NOT plain tokens.
    Use TokenHasher.hash_token() when creating tokens and TokenHasher.verify_token()
    when validating. See apps/core/utils/token_hashing.py.

    Attributes:
        id: UUID primary key
        token: The token string (HMAC-SHA256 hashed for security)
        expires_at: When the token expires
        created_at: When the token was created
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    def is_expired(self) -> bool:
        """Check if token has expired.

        Returns:
            True if token is expired, False otherwise.
        """
        from django.utils import timezone
        return timezone.now() > self.expires_at

    def is_valid(self) -> bool:
        """Check if token is valid (not expired).

        Returns:
            True if token is valid, False otherwise.
        """
        return not self.is_expired()
```

Then refactor existing token models to inherit from `BaseToken`:

```python
# apps/core/models/session_token.py

class SessionToken(BaseToken):
    """Session tokens for authenticated users.

    Extends BaseToken with user session-specific fields.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    refresh_token_hash = models.CharField(max_length=255, unique=True)
    ip_address = models.BinaryField()  # Encrypted
    user_agent = models.TextField(blank=True)
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'session_tokens'
        ordering = ['-created_at']


# apps/core/models/password_reset_token.py

class PasswordResetToken(BaseToken):
    """Token for password reset requests.

    Extends BaseToken with password reset-specific fields.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reset_tokens')
    used = models.BooleanField(default=False)

    class Meta:
        db_table = 'password_reset_tokens'
        ordering = ['-created_at']


# apps/core/models/email_verification_token.py

class EmailVerificationToken(BaseToken):
    """Token for email verification.

    Extends BaseToken with email verification-specific fields.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='verification_tokens'
    )
    verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'email_verification_tokens'
        ordering = ['-created_at']
```

### GraphQL API Contracts

#### Types

```graphql
"""
User type representing an authenticated user.
"""
type User {
  id: ID!
  email: String!
  firstName: String!
  lastName: String!
  organisation: Organisation!
  isActive: Boolean!
  emailVerified: Boolean!
  twoFactorEnabled: Boolean!
  profile: UserProfile
  createdAt: DateTime!
  updatedAt: DateTime!
}

"""
Organisation type for multi-tenancy.
"""
type Organisation {
  id: ID!
  name: String!
  slug: String!
  industry: String
  isActive: Boolean!
  createdAt: DateTime!
  updatedAt: DateTime!
}

"""
User profile with extended information.
"""
type UserProfile {
  id: ID!
  phone: String
  avatar: String
  timezone: String!
  language: String!
  bio: String
}

"""
Authentication payload returned on successful login.
"""
type AuthPayload {
  token: String!
  refreshToken: String!
  user: User!
  requiresTwoFactor: Boolean!
}

"""
Two-factor authentication setup response.
"""
type TwoFactorSetupPayload {
  secret: String!
  qrCodeUrl: String!
  backupCodes: [String!]!
}

"""
Audit log entry.
"""
type AuditLog {
  id: ID!
  user: User
  action: String!
  ipAddress: String # Decrypted for display
  userAgent: String
  metadata: JSON
  createdAt: DateTime!
}
```

#### Inputs

```graphql
"""
Input for user registration.
"""
input RegisterInput {
  email: String!
  password: String!
  firstName: String!
  lastName: String!
  organisationSlug: String!
}

"""
Input for user login.
"""
input LoginInput {
  email: String!
  password: String!
  totpCode: String # Optional, required if 2FA enabled
}

"""
Input for password reset request.
"""
input PasswordResetRequestInput {
  email: String!
}

"""
Input for password reset completion.
"""
input PasswordResetInput {
  token: String!
  newPassword: String!
}

"""
Input for password change.
"""
input PasswordChangeInput {
  currentPassword: String!
  newPassword: String!
}

"""
Input for enabling 2FA.
"""
input EnableTwoFactorInput {
  totpCode: String! # Verify the setup worked
}
```

#### Queries

```graphql
type Query {
  """
  Get the currently authenticated user.
  """
  me: User

  """
  Get user by ID (organisation-scoped).
  """
  user(id: ID!): User

  """
  Get all users in the organisation.
  """
  users(limit: Int = 10, offset: Int = 0): [User!]!

  """
  Get audit logs for current user.
  """
  myAuditLogs(limit: Int = 50, offset: Int = 0): [AuditLog!]!

  """
  Get audit logs for organisation (admin only).
  """
  organisationAuditLogs(limit: Int = 100, offset: Int = 0): [AuditLog!]!
}
```

#### Mutations

```graphql
type Mutation {
  """
  Register a new user.
  """
  register(input: RegisterInput!): AuthPayload!

  """
  Login with email and password.
  """
  login(input: LoginInput!): AuthPayload!

  """
  Logout (revoke current session).
  """
  logout: Boolean!

  """
  Refresh authentication token.
  """
  refreshToken(refreshToken: String!): AuthPayload!

  """
  Request password reset email.
  """
  requestPasswordReset(input: PasswordResetRequestInput!): Boolean!

  """
  Complete password reset with token.
  """
  resetPassword(input: PasswordResetInput!): Boolean!

  """
  Change password for authenticated user.
  """
  changePassword(input: PasswordChangeInput!): Boolean!

  """
  Resend email verification.
  """
  resendVerificationEmail: Boolean!

  """
  Verify email with token.
  """
  verifyEmail(token: String!): Boolean!

  """
  Enable two-factor authentication.
  """
  enableTwoFactor(input: EnableTwoFactorInput!): Boolean!

  """
  Disable two-factor authentication.
  """
  disableTwoFactor(password: String!): Boolean!

  """
  Generate 2FA setup (returns secret and QR code).
  """
  generateTwoFactorSetup: TwoFactorSetupPayload!
}
```

### Django Groups and Permissions System

This authentication system leverages Django's built-in Groups and permissions for role-based
access control (RBAC). This provides a flexible, battle-tested foundation for managing access
across the CMS platform.

#### Permission Hierarchy

The platform uses a three-tier permission hierarchy:

```
Platform Level (Superuser, Staff)
    ↓
Organisation Level (Owner, Admin, Member)
    ↓
Website Level (Admin, Editor, Viewer) [Future: US-004+]
```

#### Default Groups

**Platform-Level Groups:**

| Group            | Permissions                       | Description             |
| ---------------- | --------------------------------- | ----------------------- |
| Platform Admin   | All permissions, cross-org access | Platform administrators |
| Platform Support | View all orgs, limited write      | Customer support staff  |

**Organisation-Level Groups:**

| Group               | Permissions                     | Description                       |
| ------------------- | ------------------------------- | --------------------------------- |
| Organisation Owner  | All permissions within org      | Organisation creator/owner        |
| Organisation Admin  | Manage users, content, settings | Organisation administrators       |
| Organisation Member | Create/edit own content         | Regular organisation members      |
| Organisation Viewer | Read-only access                | Read-only members (e.g., clients) |

**Website-Level Groups (Future Phases):**

| Group          | Permissions                 | Description                          |
| -------------- | --------------------------- | ------------------------------------ |
| Website Admin  | Manage website settings     | Full control over specific website   |
| Website Editor | Create/edit/publish content | Content editors for specific website |
| Website Viewer | View content                | Read-only access to specific website |

#### Custom Permissions

Define custom permissions in model Meta classes for CMS-specific operations:

```python
# apps/cms/models/page.py

class Page(models.Model):
    """CMS page model with custom permissions."""

    # ... fields ...

    class Meta:
        permissions = [
            ("publish_page", "Can publish pages"),
            ("approve_page", "Can approve pages for publishing"),
            ("delete_published_page", "Can delete published pages"),
            ("view_unpublished_page", "Can view unpublished pages"),
        ]


# apps/core/models/organisation.py

class Organisation(models.Model):
    """Organisation model with custom permissions."""

    # ... fields ...

    class Meta:
        permissions = [
            ("manage_organisation_users", "Can manage organisation users"),
            ("view_organisation_audit_logs", "Can view organisation audit logs"),
            ("manage_organisation_settings", "Can manage organisation settings"),
            ("delete_organisation", "Can delete organisation"),
        ]
```

#### Group Assignment on User Creation

Automatically assign groups based on user role:

```python
# apps/core/services/auth_service.py

from django.contrib.auth.models import Group

class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def register_user(
        email: str,
        password: str,
        organisation: Organisation,
        role: str = 'member',
        **kwargs
    ) -> User:
        """Register a new user and assign appropriate group.

        Args:
            email: User email address
            password: User password (will be hashed)
            organisation: Organisation the user belongs to
            role: User role (owner, admin, member, viewer)
            **kwargs: Additional user fields

        Returns:
            Created User instance with assigned groups.
        """
        user = User.objects.create_user(
            email=email,
            password=password,
            organisation=organisation,
            **kwargs
        )

        # Assign to appropriate group
        group_name = f"Organisation {role.capitalize()}"
        group, created = Group.objects.get_or_create(name=group_name)
        user.groups.add(group)

        # First user in organisation becomes owner
        if organisation.users.count() == 1:
            owner_group, _ = Group.objects.get_or_create(name="Organisation Owner")
            user.groups.add(owner_group)

        return user
```

#### Permission Checking in GraphQL Resolvers

**Method 1: Using `user.has_perm()` in Resolver Logic**

```python
# api/mutations/content.py

import strawberry
from strawberry.types import Info
from apps.cms.models import Page

@strawberry.type
class Mutation:
    """GraphQL mutations for content management."""

    @strawberry.mutation
    def publish_page(self, info: Info, page_id: strawberry.ID) -> Page:
        """Publish a page.

        Requires: 'cms.publish_page' permission

        Args:
            info: GraphQL context with authenticated user
            page_id: ID of page to publish

        Returns:
            Published Page object

        Raises:
            PermissionError: If user lacks publish_page permission
        """
        user = info.context.request.user

        if not user.is_authenticated:
            raise PermissionError("Authentication required")

        # Check permission
        if not user.has_perm('cms.publish_page'):
            raise PermissionError(
                "You don't have permission to publish pages"
            )

        # Check organisation boundary
        page = Page.objects.get(id=page_id)
        if page.organisation != user.organisation:
            raise PermissionError(
                "You can only publish pages in your organisation"
            )

        # Publish the page
        page.published = True
        page.published_at = timezone.now()
        page.save()

        return page
```

**Method 2: Using Strawberry Permission Classes**

```python
# api/permissions.py

import strawberry
from strawberry.permission import BasePermission
from strawberry.types import Info
from typing import Any

class IsAuthenticated(BasePermission):
    """Permission class to check if user is authenticated."""

    message = "User is not authenticated"

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check if user is authenticated."""
        return info.context.request.user.is_authenticated


class HasPermission(BasePermission):
    """Permission class to check if user has specific permission."""

    def __init__(self, permission: str):
        """Initialize with required permission.

        Args:
            permission: Django permission string (e.g., 'cms.publish_page')
        """
        self.permission = permission
        self.message = f"User lacks required permission: {permission}"

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check if user has the required permission."""
        user = info.context.request.user
        return user.is_authenticated and user.has_perm(self.permission)


class IsOrganisationOwner(BasePermission):
    """Permission class to check if user is organisation owner."""

    message = "User is not an organisation owner"

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check if user is organisation owner."""
        user = info.context.request.user
        if not user.is_authenticated:
            return False
        return user.groups.filter(name="Organisation Owner").exists()


# api/mutations/content.py

@strawberry.type
class Mutation:
    """GraphQL mutations with permission decorators."""

    @strawberry.mutation(
        permission_classes=[IsAuthenticated, HasPermission("cms.publish_page")]
    )
    def publish_page(self, info: Info, page_id: strawberry.ID) -> Page:
        """Publish a page.

        Permission checked by decorator: cms.publish_page

        Args:
            info: GraphQL context
            page_id: ID of page to publish

        Returns:
            Published Page object
        """
        user = info.context.request.user
        page = Page.objects.get(id=page_id)

        # Still check organisation boundary
        if page.organisation != user.organisation:
            raise PermissionError(
                "You can only publish pages in your organisation"
            )

        page.published = True
        page.published_at = timezone.now()
        page.save()

        return page

    @strawberry.mutation(permission_classes=[IsAuthenticated, IsOrganisationOwner])
    def delete_organisation(self, info: Info, org_id: strawberry.ID) -> bool:
        """Delete an organisation.

        Permission checked by decorator: Must be organisation owner

        Args:
            info: GraphQL context
            org_id: ID of organisation to delete

        Returns:
            True if deleted successfully
        """
        user = info.context.request.user
        organisation = Organisation.objects.get(id=org_id)

        # Verify user is owner of THIS organisation
        if organisation != user.organisation:
            raise PermissionError("You can only delete your own organisation")

        organisation.delete()
        return True
```

**Method 3: Organisation Boundary Enforcement in Querysets**

```python
# api/queries/user.py

import strawberry
from strawberry.types import Info
from typing import List
from apps.core.models import User

@strawberry.type
class Query:
    """GraphQL queries with organisation scoping."""

    @strawberry.field
    def users(self, info: Info, limit: int = 10, offset: int = 0) -> List[User]:
        """Get all users in the current user's organisation.

        Automatically filters to organisation boundary.

        Args:
            info: GraphQL context with authenticated user
            limit: Maximum results to return
            offset: Pagination offset

        Returns:
            List of User objects in same organisation
        """
        user = info.context.request.user

        if not user.is_authenticated:
            raise PermissionError("Authentication required")

        # Filter to user's organisation only
        queryset = User.objects.filter(
            organisation=user.organisation
        ).select_related('organisation', 'profile')

        return queryset[offset:offset + limit]

    @strawberry.field
    def user(self, info: Info, user_id: strawberry.ID) -> User:
        """Get a specific user by ID.

        Enforces organisation boundary - users can only query
        users within their own organisation.

        Args:
            info: GraphQL context
            user_id: ID of user to retrieve

        Returns:
            User object if found and in same organisation

        Raises:
            PermissionError: If user not in same organisation
        """
        current_user = info.context.request.user

        if not current_user.is_authenticated:
            raise PermissionError("Authentication required")

        try:
            user = User.objects.select_related('organisation').get(id=user_id)
        except User.DoesNotExist:
            raise ValueError(f"User with ID {user_id} not found")

        # Enforce organisation boundary
        if user.organisation != current_user.organisation:
            raise PermissionError(
                "You can only access users in your organisation"
            )

        return user
```

#### Permission Migration Path

**Phase 1 (US-001): Simple Permission Checks**

- Use `is_staff` and `is_superuser` flags
- Implement basic `IsAuthenticated` permission
- Enforce organisation boundaries in all queries

**Phase 2 (US-004+): Group-Based Permissions**

- Create default groups (Owner, Admin, Member, Viewer)
- Assign groups on user creation
- Use `user.groups.filter(name="...").exists()` for role checks

**Phase 3 (Future): Custom Permissions**

- Define custom permissions in model Meta
- Use `user.has_perm('app.permission')` for granular control
- Implement permission inheritance (groups grant permissions)

**Phase 4 (Future): Website-Level Permissions**

- Add `UserWebsiteRole` model for website-specific access
- Cascade permissions: Platform → Organisation → Website
- Support users with different roles on different websites

### Authentication Flow

#### Registration Flow

```
1. Client sends registration mutation with email, password, name, org slug
2. Backend validates input:
   - Email format valid
   - Email not already registered
   - Password meets requirements
   - Organisation exists
3. Backend creates User record:
   - Hash password with Argon2
   - Set email_verified = False
   - Associate with organisation
4. Backend creates EmailVerificationToken
5. Backend sends verification email via Mailpit (dev/test) or SMTP (prod)
6. Backend logs audit event (register)
7. Backend returns AuthPayload with token
8. Client stores token in localStorage/secure storage
```

#### Login Flow (Without 2FA)

```
1. Client sends login mutation with email and password
2. Backend validates credentials:
   - User exists and is active
   - Password matches hash
3. Backend checks if 2FA enabled:
   - If enabled, return requiresTwoFactor: true (no token yet)
   - If disabled, proceed
4. Backend creates SessionToken
5. Backend generates JWT token and refresh token
6. Backend stores token hash in database and Redis
7. Backend logs audit event (login_success) with encrypted IP
8. Backend returns AuthPayload with token and user
9. Client stores token
```

#### Login Flow (With 2FA)

```
1. Client sends login mutation with email and password
2. Backend validates credentials
3. Backend checks 2FA enabled:
   - Returns requiresTwoFactor: true (no token yet)
4. Client prompts for TOTP code
5. Client sends login mutation again with email, password, and totpCode
6. Backend validates TOTP code against secret
7. If valid:
   - Create SessionToken
   - Generate JWT token
   - Log audit event (2fa_verify_success)
   - Return AuthPayload
8. If invalid:
   - Log audit event (2fa_verify_failed)
   - Return error
```

#### Password Reset Flow

```
1. Client sends requestPasswordReset mutation with email
2. Backend finds user by email
3. Backend creates PasswordResetToken (expires in 15 minutes)
4. Backend sends reset email with token link
5. Backend logs audit event
6. User clicks link in email
7. Client displays password reset form
8. Client sends resetPassword mutation with token and new password
9. Backend validates token:
   - Token exists
   - Token not expired
   - Token not used
10. Backend updates user password
11. Backend marks token as used
12. Backend logs audit event
13. Backend returns success
```

#### Email Verification Flow

```
1. On registration, EmailVerificationToken created
2. Verification email sent with token link
3. User clicks link
4. Client sends verifyEmail mutation with token
5. Backend validates token:
   - Token exists
   - Token not expired
   - Token not already verified
6. Backend updates user.email_verified = True
7. Backend sets user.email_verified_at = now()
8. Backend marks token as verified
9. Backend logs audit event
10. Backend returns success
```

### Security Architecture

#### Password Requirements

- Minimum 12 characters
- Maximum 128 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one number (0-9)
- At least one special character (!@#$%^&\*()\_+-=[]{}|;:,.<>?)

Validation implemented in `apps/core/validators.py`:

```python
def validate_password_strength(password: str) -> None:
    """Validate password meets security requirements.

    Args:
        password: The password to validate.

    Raises:
        ValidationError: If password doesn't meet requirements.
    """
    if len(password) < 12:
        raise ValidationError("Password must be at least 12 characters")
    if len(password) > 128:
        raise ValidationError("Password must not exceed 128 characters")
    if not re.search(r'[A-Z]', password):
        raise ValidationError("Password must contain at least one uppercase letter")
    if not re.search(r'[a-z]', password):
        raise ValidationError("Password must contain at least one lowercase letter")
    if not re.search(r'[0-9]', password):
        raise ValidationError("Password must contain at least one number")
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]', password):
        raise ValidationError("Password must contain at least one special character")
```

#### Password Hashing

Use Argon2id algorithm (OWASP recommended):

```python
# config/settings/base.py

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]
```

#### Session Management

**Token Storage Strategy** (Updated per Architecture Review):

This implementation uses a **Redis-Primary** approach with database audit trail:

- **Redis**: Primary storage for active tokens (fast lookups, automatic expiration)
- **Database**: Audit trail and token metadata (durable, queryable)
- **Synchronisation**: Redis is source of truth; database is write-only for audit

**Token Specifications:**

- JWT access tokens with 24-hour expiration
- Refresh tokens with 30-day expiration
- Token rotation on refresh (old refresh token invalidated)
- Token blacklist in Redis for revoked tokens before expiry
- Maximum 5 concurrent sessions per user (oldest auto-revoked)

**JWT Payload Structure:**

```python
payload = {
    'user_id': str(user.id),
    'organisation_id': str(user.organisation_id),
    'email': user.email,
    'exp': datetime.utcnow() + timedelta(hours=24),
    'iat': datetime.utcnow(),
    'jti': str(uuid.uuid4()),  # JWT ID for blacklisting
    'type': 'access',  # vs 'refresh'
}
```

**Token Service Implementation:**

```python
# apps/core/services/token_service.py

import jwt
import hashlib
from django.conf import settings
from django.core.cache import cache
import redis

class TokenService:
    """Service for managing authentication tokens.

    Uses Redis-primary storage strategy with database audit trail.
    """

    redis_client = redis.from_url(settings.REDIS_URL)

    @staticmethod
    def create_token(user: User, request) -> dict:
        """Create JWT token and refresh token for user.

        Stores token in Redis for fast validation and database for audit.

        Args:
            user: User to create token for
            request: HTTP request object

        Returns:
            Dict with 'token', 'refresh_token', and 'expires_at'
        """
        # Generate access token
        access_payload = {
            'user_id': str(user.id),
            'organisation_id': str(user.organisation_id),
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow(),
            'jti': str(uuid.uuid4()),
            'type': 'access',
        }
        access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
        access_token_hash = hashlib.sha256(access_token.encode()).hexdigest()

        # Generate refresh token
        refresh_payload = {
            'user_id': str(user.id),
            'exp': datetime.utcnow() + timedelta(days=30),
            'iat': datetime.utcnow(),
            'jti': str(uuid.uuid4()),
            'type': 'refresh',
        }
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')
        refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

        # Store in Redis (primary)
        TokenService.redis_client.setex(
            f"token:{access_token_hash}",
            86400,  # 24 hours
            str(user.id)
        )
        TokenService.redis_client.setex(
            f"refresh:{refresh_token_hash}",
            2592000,  # 30 days
            str(user.id)
        )

        # Store in database (audit trail)
        ip_address = IPEncryption.encrypt_ip(get_client_ip(request))
        SessionToken.objects.create(
            user=user,
            token_hash=access_token_hash,
            refresh_token_hash=refresh_token_hash,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            expires_at=access_payload['exp']
        )

        # Enforce max sessions limit (5)
        user_sessions = SessionToken.objects.filter(user=user).order_by('-created_at')
        if user_sessions.count() > 5:
            # Revoke oldest sessions
            for session in user_sessions[5:]:
                TokenService.revoke_token_hash(session.token_hash)
                session.delete()

        return {
            'token': access_token,
            'refresh_token': refresh_token,
            'expires_at': access_payload['exp'].isoformat()
        }

    @staticmethod
    def verify_token(token: str) -> User:
        """Verify JWT token and return user.

        Checks Redis cache first, then validates JWT signature.

        Args:
            token: JWT token to verify

        Returns:
            User instance if token is valid

        Raises:
            AuthenticationError: If token is invalid or revoked
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Check if token is blacklisted
        if TokenService.redis_client.exists(f"blacklist:{token_hash}"):
            raise AuthenticationError("Token has been revoked")

        # Check Redis cache
        user_id = TokenService.redis_client.get(f"token:{token_hash}")
        if user_id:
            return User.objects.get(id=user_id.decode())

        # Fallback: validate JWT (in case Redis was cleared)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

            if payload.get('type') != 'access':
                raise AuthenticationError("Invalid token type")

            user = User.objects.get(id=payload['user_id'])

            # Repopulate Redis cache
            ttl = int(payload['exp'] - datetime.utcnow().timestamp())
            if ttl > 0:
                TokenService.redis_client.setex(
                    f"token:{token_hash}",
                    ttl,
                    str(user.id)
                )

            return user
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")

    @staticmethod
    def refresh_token(refresh_token: str) -> dict:
        """Refresh authentication token.

        Validates refresh token and issues new access + refresh tokens.
        Old refresh token is invalidated (token rotation).

        Args:
            refresh_token: Refresh token

        Returns:
            Dict with new 'token' and 'refresh_token'
        """
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])

            if payload.get('type') != 'refresh':
                raise AuthenticationError("Invalid token type")

            user = User.objects.get(id=payload['user_id'])

            # Revoke old refresh token
            old_refresh_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
            TokenService.redis_client.delete(f"refresh:{old_refresh_hash}")

            # Create new tokens
            return TokenService.create_token(user, request=None)

        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Refresh token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid refresh token")

    @staticmethod
    def revoke_token(token: str) -> None:
        """Revoke a token (logout).

        Adds token to blacklist in Redis and removes from active tokens.

        Args:
            token: JWT token to revoke
        """
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        TokenService.revoke_token_hash(token_hash)

    @staticmethod
    def revoke_token_hash(token_hash: str) -> None:
        """Revoke a token by its hash.

        Args:
            token_hash: SHA256 hash of token
        """
        # Remove from active tokens
        TokenService.redis_client.delete(f"token:{token_hash}")

        # Add to blacklist (with TTL matching original token expiry)
        # This prevents reuse even if token is somehow still valid
        TokenService.redis_client.setex(
            f"blacklist:{token_hash}",
            86400,  # 24 hours (match access token TTL)
            '1'
        )
```

**Future Enhancement: Asymmetric JWT Signing**

For future microservices architecture (Phases 8-12), migrate to RS256:

- Private key signs tokens (backend only)
- Public key verifies tokens (can be shared with SaaS products)
- Allows independent token verification without shared secret

#### IP Address Encryption

All IP addresses encrypted before storage using Fernet symmetric encryption:

```python
# apps/core/utils/encryption.py

from cryptography.fernet import Fernet
from django.conf import settings

class IPEncryption:
    """Utility for encrypting and decrypting IP addresses."""

    @staticmethod
    def encrypt_ip(ip_address: str) -> bytes:
        """Encrypt an IP address.

        Args:
            ip_address: The IP address to encrypt.

        Returns:
            Encrypted IP address as bytes.
        """
        cipher = Fernet(settings.IP_ENCRYPTION_KEY)
        return cipher.encrypt(ip_address.encode())

    @staticmethod
    def decrypt_ip(encrypted_ip: bytes) -> str:
        """Decrypt an IP address.

        Args:
            encrypted_ip: The encrypted IP address.

        Returns:
            Decrypted IP address as string.
        """
        cipher = Fernet(settings.IP_ENCRYPTION_KEY)
        return cipher.decrypt(encrypted_ip).decode()
```

Environment variable required:

```bash
# .env.dev, .env.production, etc.
IP_ENCRYPTION_KEY=<generated-fernet-key>
```

Generate key with:

```python
from cryptography.fernet import Fernet
key = Fernet.generate_key()
print(key.decode())
```

#### Rate Limiting

Implemented using Redis and Django middleware:

```python
# apps/core/middleware/rate_limit.py

import redis
from django.conf import settings
from django.http import JsonResponse

class RateLimitMiddleware:
    """Rate limiting for authentication endpoints."""

    LIMITS = {
        'login': (5, 900),  # 5 attempts per 15 minutes
        'register': (3, 3600),  # 3 attempts per hour
        'password_reset': (3, 3600),  # 3 attempts per hour
        '2fa_verify': (5, 900),  # 5 attempts per 15 minutes
    }

    def __init__(self, get_response):
        self.get_response = get_response
        self.redis_client = redis.from_url(settings.REDIS_URL)

    def __call__(self, request):
        """Check rate limit before processing request."""
        # Identify endpoint
        endpoint = self._get_endpoint(request)

        if endpoint in self.LIMITS:
            ip_address = self._get_client_ip(request)
            key = f"rate_limit:{endpoint}:{ip_address}"

            # Get current count
            count = self.redis_client.get(key)
            limit, window = self.LIMITS[endpoint]

            if count and int(count) >= limit:
                return JsonResponse(
                    {'error': 'Rate limit exceeded. Please try again later.'},
                    status=429
                )

            # Increment counter
            if count:
                self.redis_client.incr(key)
            else:
                self.redis_client.setex(key, window, 1)

        response = self.get_response(request)
        return response

    def _get_endpoint(self, request):
        """Identify the endpoint from GraphQL query."""
        # Parse GraphQL query to identify mutation/query
        # Implementation depends on GraphQL library
        pass

    def _get_client_ip(self, request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
```

#### Account Lockout Mechanism

**New per Architecture Review**: Prevent brute force attacks with temporary account lockout.

**Policy:**

- After 5 failed login attempts within 15 minutes: Account locked for 15 minutes
- Email notification sent to user on lockout
- Admin can manually unlock accounts
- Lockout bypassed for superusers (for emergency access)

**Implementation:**

```python
# apps/core/services/auth_service.py

from django.utils import timezone
from datetime import timedelta

class AuthService:
    """Service for authentication operations."""

    @staticmethod
    def check_account_lockout(user: User) -> tuple[bool, int]:
        """Check if account is locked due to failed login attempts.

        Args:
            user: User to check

        Returns:
            Tuple of (is_locked: bool, remaining_seconds: int)
        """
        # Superusers bypass lockout
        if user.is_superuser:
            return False, 0

        # Check failed attempts in last 15 minutes
        lockout_window = timezone.now() - timedelta(minutes=15)
        failed_attempts = AuditLog.objects.filter(
            user=user,
            action='login_failed',
            created_at__gte=lockout_window
        ).count()

        if failed_attempts >= 5:
            # Account is locked
            most_recent_failure = AuditLog.objects.filter(
                user=user,
                action='login_failed'
            ).order_by('-created_at').first()

            if most_recent_failure:
                lockout_until = most_recent_failure.created_at + timedelta(minutes=15)
                remaining = int((lockout_until - timezone.now()).total_seconds())

                if remaining > 0:
                    return True, remaining

        return False, 0

    @staticmethod
    def record_failed_login(user: User, request) -> None:
        """Record failed login attempt and check for lockout.

        Args:
            user: User who failed login
            request: HTTP request object
        """
        # Log the failed attempt
        AuditService.log_event(
            action='login_failed',
            user=user,
            request=request
        )

        # Check if this triggers lockout
        is_locked, remaining = AuthService.check_account_lockout(user)

        if is_locked and remaining > 0:
            # This was the 5th failed attempt - send lockout email
            EmailService.send_account_lockout_email(user, remaining)

            # Log lockout event
            AuditService.log_event(
                action='account_locked',
                user=user,
                request=request,
                metadata={'remaining_seconds': remaining}
            )

    @staticmethod
    def login(email: str, password: str, request) -> dict:
        """Authenticate user and return tokens.

        Args:
            email: User email
            password: User password
            request: HTTP request object

        Returns:
            Dict with tokens and user data

        Raises:
            AuthenticationError: If credentials invalid or account locked
        """
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise AuthenticationError("Invalid credentials")

        # Check account lockout BEFORE password check
        is_locked, remaining = AuthService.check_account_lockout(user)
        if is_locked:
            raise AuthenticationError(
                f"Account temporarily locked. Try again in {remaining} seconds."
            )

        # Verify password
        if not user.check_password(password):
            AuthService.record_failed_login(user, request)
            raise AuthenticationError("Invalid credentials")

        # Check if account is active
        if not user.is_active:
            raise AuthenticationError("Account is disabled")

        # Successful login - clear any previous failed attempts
        AuditLog.objects.filter(
            user=user,
            action='login_failed'
        ).delete()

        # Log successful login
        AuditService.log_event(
            action='login_success',
            user=user,
            request=request
        )

        # Generate tokens
        tokens = TokenService.create_token(user, request)

        return {
            'tokens': tokens,
            'user': user,
            'requires_2fa': user.two_factor_enabled
        }
```

**GraphQL Mutation Response:**

```python
# api/mutations/auth.py

@strawberry.mutation
def login(self, info: Info, input: LoginInput) -> AuthPayload:
    """Login with email and password.

    Args:
        info: GraphQL context
        input: Login credentials

    Returns:
        AuthPayload with token and user data

    Raises:
        GraphQLError: If authentication fails or account locked
    """
    try:
        result = AuthService.login(
            email=input.email,
            password=input.password,
            request=info.context.request
        )

        return AuthPayload(
            token=result['tokens']['token'],
            refresh_token=result['tokens']['refresh_token'],
            user=result['user'],
            requires_two_factor=result['requires_2fa']
        )
    except AuthenticationError as e:
        raise GraphQLError(
            str(e),
            extensions={
                'code': 'AUTHENTICATION_ERROR',
                'category': 'AUTHENTICATION'
            }
        )
```

#### PostgreSQL Row-Level Security (RLS)

**New per Architecture Review**: Database-level enforcement of multi-tenancy boundaries.

**Purpose:** Provides defence-in-depth for organisation isolation. Even if application code has bugs, database policies prevent cross-organisation data access.

**Implementation:**

```sql
-- Enable RLS on all multi-tenant tables
-- Run this migration in Phase 1

-- Users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_organisation_isolation ON users
    FOR ALL
    USING (
        organisation_id = current_setting('app.current_organisation_id', TRUE)::uuid
        OR current_setting('app.bypass_rls', TRUE)::boolean = true
    );

-- Audit logs table
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY audit_log_organisation_isolation ON audit_logs
    FOR ALL
    USING (
        organisation_id = current_setting('app.current_organisation_id', TRUE)::uuid
        OR current_setting('app.bypass_rls', TRUE)::boolean = true
    );

-- Session tokens table
ALTER TABLE session_tokens ENABLE ROW LEVEL SECURITY;

CREATE POLICY session_token_organisation_isolation ON session_tokens
    FOR ALL
    USING (
        user_id IN (
            SELECT id FROM users
            WHERE organisation_id = current_setting('app.current_organisation_id', TRUE)::uuid
        )
        OR current_setting('app.bypass_rls', TRUE)::boolean = true
    );

-- User profiles table
ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_profile_organisation_isolation ON user_profiles
    FOR ALL
    USING (
        user_id IN (
            SELECT id FROM users
            WHERE organisation_id = current_setting('app.current_organisation_id', TRUE)::uuid
        )
        OR current_setting('app.bypass_rls', TRUE)::boolean = true
    );
```

**Middleware to Set Organisation Context:**

```python
# apps/core/middleware/organisation_context.py

from django.db import connection

class OrganisationContextMiddleware:
    """Middleware to set organisation context for PostgreSQL RLS.

    Sets session variables that RLS policies use to filter queries.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Set organisation context before processing request."""
        if request.user.is_authenticated:
            with connection.cursor() as cursor:
                if request.user.is_superuser:
                    # Superusers can access all organisations
                    # They must explicitly set organisation context or bypass RLS
                    cursor.execute("SET LOCAL app.bypass_rls = true")
                else:
                    # Regular users: set their organisation context
                    cursor.execute(
                        "SET LOCAL app.current_organisation_id = %s",
                        [str(request.user.organisation_id)]
                    )
                    cursor.execute("SET LOCAL app.bypass_rls = false")

        response = self.get_response(request)
        return response
```

**Settings Configuration:**

```python
# config/settings/base.py

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.core.middleware.organisation_context.OrganisationContextMiddleware',  # Add here
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

**Testing RLS Policies:**

```python
# tests/unit/test_rls_policies.py

import pytest
from django.db import connection
from apps.core.models import User, Organisation

@pytest.mark.unit
class TestRowLevelSecurity:
    """Test PostgreSQL RLS policies."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Create test organisations and users."""
        self.org1 = Organisation.objects.create(name="Org 1", slug="org-1")
        self.org2 = Organisation.objects.create(name="Org 2", slug="org-2")

        self.user1 = User.objects.create_user(
            email="user1@org1.com",
            password="pass123",
            organisation=self.org1
        )

        self.user2 = User.objects.create_user(
            email="user2@org2.com",
            password="pass123",
            organisation=self.org2
        )

    def test_rls_prevents_cross_organisation_access(self) -> None:
        """Test RLS prevents users from seeing other organisation's data.

        Given: Two organisations with one user each
        When: Org 1 context is set
        Then: Only Org 1 users are visible
        """
        with connection.cursor() as cursor:
            # Set organisation context to Org 1
            cursor.execute(
                "SET LOCAL app.current_organisation_id = %s",
                [str(self.org1.id)]
            )
            cursor.execute("SET LOCAL app.bypass_rls = false")

        # Query should only return Org 1 users
        users = User.objects.all()
        assert users.count() == 1
        assert users.first().id == self.user1.id

    def test_rls_allows_superuser_bypass(self) -> None:
        """Test superusers can bypass RLS.

        Given: Two organisations with users
        When: bypass_rls is set to true
        Then: All users are visible
        """
        with connection.cursor() as cursor:
            cursor.execute("SET LOCAL app.bypass_rls = true")

        # Query should return all users
        users = User.objects.all()
        assert users.count() == 2
```

### Extensibility and Future Role Models

This section documents how future role-specific models (Customer, Seller, Author, etc.) will
extend the base User model as the platform evolves through later phases.

#### Extension Pattern: OneToOne Relationships

Rather than subclassing User, use OneToOne relationships for role-specific data:

```python
# apps/ecommerce/models/customer.py (Future: Phase 4+)

from apps.core.models import User

class Customer(models.Model):
    """Customer-specific profile extending User.

    Used for e-commerce templates. Stores shopping preferences,
    order history, and payment methods.

    Attributes:
        user: OneToOne link to base User
        shipping_address: Default shipping address
        billing_address: Default billing address
        preferred_payment_method: Stripe customer ID or payment method
        loyalty_points: Accumulated loyalty points
        newsletter_subscribed: Email marketing opt-in
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='customer_profile'
    )
    shipping_address = models.JSONField(null=True, blank=True)
    billing_address = models.JSONField(null=True, blank=True)
    preferred_payment_method = models.CharField(max_length=255, blank=True)
    loyalty_points = models.IntegerField(default=0)
    newsletter_subscribed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'customers'


# apps/ecommerce/models/seller.py (Future: Phase 4+)

class Seller(models.Model):
    """Seller-specific profile extending User.

    Used for marketplace templates. Stores shop information,
    payment details, and seller metrics.

    Attributes:
        user: OneToOne link to base User
        shop_name: Public-facing shop name
        shop_description: Shop bio/description
        commission_rate: Percentage commission (0-100)
        payout_method: Bank account or payment method
        verified: Whether seller is verified
        rating: Average seller rating (0-5)
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='seller_profile'
    )
    shop_name = models.CharField(max_length=255)
    shop_description = models.TextField(blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.0)
    payout_method = models.JSONField(null=True, blank=True)
    verified = models.BooleanField(default=False)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'sellers'


# apps/blog/models/author.py (Future: Phase 4+)

class Author(models.Model):
    """Author-specific profile extending User.

    Used for blog templates. Stores author bio, social links,
    and writing statistics.

    Attributes:
        user: OneToOne link to base User
        bio: Author biography
        website: Personal website URL
        social_links: JSON with Twitter, LinkedIn, etc.
        article_count: Total published articles
        follower_count: Number of followers
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='author_profile'
    )
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    social_links = models.JSONField(default=dict)
    article_count = models.IntegerField(default=0)
    follower_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'authors'
```

#### Why OneToOne Instead of Inheritance

**Advantages:**

- Keeps User model clean and focused on authentication
- Allows users to have multiple roles (Customer AND Seller)
- Easier to add/remove role profiles without affecting User
- Better database performance (no multi-table inheritance)
- Clearer separation of concerns

**Usage Example:**

```python
# Check if user is a customer
if hasattr(user, 'customer_profile'):
    customer = user.customer_profile
    print(f"Loyalty points: {customer.loyalty_points}")

# Check if user is a seller
if hasattr(user, 'seller_profile'):
    seller = user.seller_profile
    print(f"Shop: {seller.shop_name}")

# User can be both customer and seller
user = User.objects.get(email='john@example.com')
if hasattr(user, 'customer_profile') and hasattr(user, 'seller_profile'):
    print("User is both a customer and seller")
```

#### GraphQL Types for Role-Specific Profiles

```graphql
# Future: Extended User type with role profiles

type User {
  id: ID!
  email: String!
  firstName: String!
  lastName: String!
  organisation: Organisation!
  profile: UserProfile

  # Role-specific profiles (nullable)
  customerProfile: CustomerProfile
  sellerProfile: SellerProfile
  authorProfile: AuthorProfile
}

type CustomerProfile {
  shippingAddress: JSON
  billingAddress: JSON
  loyaltyPoints: Int!
  newsletterSubscribed: Boolean!
}

type SellerProfile {
  shopName: String!
  shopDescription: String
  verified: Boolean!
  rating: Float!
  commissionRate: Float!
}

type AuthorProfile {
  bio: String
  website: String
  socialLinks: JSON
  articleCount: Int!
  followerCount: Int!
}
```

#### Permission Groups for Future Roles

When role-specific models are added, create corresponding permission groups:

```python
# apps/ecommerce/management/commands/create_ecommerce_groups.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

class Command(BaseCommand):
    """Create default groups for e-commerce roles."""

    def handle(self, *args, **options):
        # Customer group
        customer_group, created = Group.objects.get_or_create(name="Customer")
        customer_permissions = Permission.objects.filter(
            codename__in=[
                'add_order',
                'view_order',
                'add_review',
                'view_product',
            ]
        )
        customer_group.permissions.set(customer_permissions)

        # Seller group
        seller_group, created = Group.objects.get_or_create(name="Seller")
        seller_permissions = Permission.objects.filter(
            codename__in=[
                'add_product',
                'change_product',
                'delete_product',
                'view_order',
                'change_order_status',
            ]
        )
        seller_group.permissions.set(seller_permissions)

        self.stdout.write(
            self.style.SUCCESS('E-commerce groups created successfully')
        )
```

#### Migration Path for Adding Role Profiles

**Step 1: Create the role model**

```bash
./scripts/env/dev.sh makemigrations ecommerce
./scripts/env/dev.sh migrate
```

**Step 2: Create permission groups**

```bash
./scripts/env/dev.sh manage create_ecommerce_groups
```

**Step 3: Assign groups to existing users**

```python
# apps/ecommerce/services/customer_service.py

def convert_user_to_customer(user: User) -> Customer:
    """Convert a regular user to a customer.

    Creates Customer profile and assigns to Customer group.

    Args:
        user: User to convert

    Returns:
        Created Customer profile
    """
    customer, created = Customer.objects.get_or_create(user=user)

    # Assign to Customer group
    customer_group = Group.objects.get(name="Customer")
    user.groups.add(customer_group)

    return customer
```

### Django Admin Configuration

Django Admin provides a built-in interface for managing users, groups, and permissions. This
section documents how to configure the admin for the authentication system.

#### User Admin Configuration

```python
# apps/core/admin/user_admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from apps.core.models import User, UserProfile

class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile."""

    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('phone', 'avatar', 'timezone', 'language', 'bio')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model."""

    list_display = (
        'email',
        'first_name',
        'last_name',
        'organisation',
        'is_staff',
        'is_active',
        'email_verified',
        'two_factor_enabled',
        'created_at'
    )
    list_filter = (
        'is_staff',
        'is_superuser',
        'is_active',
        'email_verified',
        'two_factor_enabled',
        'organisation',
        'created_at'
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)
    inlines = (UserProfileInline,)

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Personal Info'), {
            'fields': ('first_name', 'last_name')
        }),
        (_('Organisation'), {
            'fields': ('organisation',)
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            )
        }),
        (_('Security'), {
            'fields': (
                'email_verified',
                'email_verified_at',
                'two_factor_enabled',
                'has_email_account',
                'has_vault_access'
            )
        }),
        (_('Important Dates'), {
            'fields': ('last_login', 'created_at', 'updated_at')
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'last_login', 'email_verified_at')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'first_name',
                'last_name',
                'organisation',
                'is_staff',
                'is_active'
            )
        }),
    )

    def get_queryset(self, request):
        """Optimise queryset with select_related."""
        qs = super().get_queryset(request)
        return qs.select_related('organisation')
```

#### Organisation Admin Configuration

```python
# apps/core/admin/organisation_admin.py

from django.contrib import admin
from apps.core.models import Organisation

@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    """Admin interface for Organisation model."""

    list_display = ('name', 'slug', 'industry', 'is_active', 'created_at', 'user_count')
    list_filter = ('is_active', 'industry', 'created_at')
    search_fields = ('name', 'slug', 'industry')
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'industry')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

    def user_count(self, obj):
        """Display number of users in organisation."""
        return obj.users.count()
    user_count.short_description = 'Users'
```

#### Audit Log Admin Configuration

```python
# apps/core/admin/audit_log_admin.py

from django.contrib import admin
from apps.core.models import AuditLog
from apps.core.utils.encryption import IPEncryption

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin interface for AuditLog model (read-only)."""

    list_display = (
        'action',
        'user',
        'organisation',
        'decrypted_ip',
        'created_at'
    )
    list_filter = ('action', 'organisation', 'created_at')
    search_fields = ('user__email', 'organisation__name', 'action')
    ordering = ('-created_at',)
    readonly_fields = (
        'user',
        'organisation',
        'action',
        'decrypted_ip',
        'user_agent',
        'metadata',
        'created_at'
    )

    def has_add_permission(self, request):
        """Disable adding audit logs via admin (immutable)."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Disable deleting audit logs via admin (immutable)."""
        return False

    def has_change_permission(self, request, obj=None):
        """Disable editing audit logs via admin (immutable)."""
        return False

    def decrypted_ip(self, obj):
        """Display decrypted IP address."""
        try:
            return IPEncryption.decrypt_ip(obj.ip_address)
        except Exception:
            return "Error decrypting"
    decrypted_ip.short_description = 'IP Address'

    fieldsets = (
        ('Event Info', {
            'fields': ('action', 'user', 'organisation', 'created_at')
        }),
        ('Request Info', {
            'fields': ('decrypted_ip', 'user_agent')
        }),
        ('Metadata', {
            'fields': ('metadata',)
        }),
    )
```

#### Group and Permission Admin

Django provides default admin for Groups and Permissions. Customise if needed:

```python
# apps/core/admin/group_admin.py

from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin

# Unregister default GroupAdmin
admin.site.unregister(Group)

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin):
    """Customised admin for Groups."""

    list_display = ('name', 'permission_count')
    search_fields = ('name',)
    filter_horizontal = ('permissions',)

    def permission_count(self, obj):
        """Display number of permissions in group."""
        return obj.permissions.count()
    permission_count.short_description = 'Permissions'
```

#### Admin Site Customisation

```python
# config/admin.py

from django.contrib import admin

# Customise admin site header and title
admin.site.site_header = "Backend Template Administration"
admin.site.site_title = "Backend Template Admin"
admin.site.index_title = "Welcome to Backend Template Administration"
```

#### Audit Logging

All authentication events logged automatically:

```python
# apps/core/services/audit_service.py

class AuditService:
    """Service for creating audit logs."""

    @staticmethod
    def log_event(
        action: str,
        user: Optional[User],
        request,
        metadata: dict = None
    ) -> AuditLog:
        """Create an audit log entry.

        Args:
            action: The action being logged
            user: The user performing the action (optional)
            request: The HTTP request object
            metadata: Additional metadata to log

        Returns:
            The created AuditLog instance.
        """
        ip_address = IPEncryption.encrypt_ip(get_client_ip(request))

        return AuditLog.objects.create(
            user=user,
            organisation=user.organisation if user else None,
            action=action,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata=metadata or {}
        )
```

---

## Implementation Phases

### Phase 1: Core Models and Database

**Objective:** Create database models and migrations for authentication system.

**Review Fixes Implemented:**

- **C2**: TOTP secret encryption using Fernet (see [Critical Issue C2](#c2-totp-secret-storage-security))
- **H5**: Breached password validator with HaveIBeenPwned (see [High Priority H5](#h5-breached-password-checking))
- **H11**: Password history tracking (see [High Priority H11](#h11-password-history))
- **H8**: Device fingerprinting fields (see [High Priority H8](#h8-device-fingerprinting))
- **M8**: Session activity tracking fields (see [Medium Priority M8](#m8-session-activity-tracking))

**Tasks:**

- [ ] Create `Organisation` model in `apps/core/models/organisation.py`
- [ ] Create custom `User` model in `apps/core/models/user.py`
  - [ ] Add `has_email_account` and `has_vault_access` Boolean fields
  - [ ] Add `password_changed_at` field for password history (H11)
- [ ] Create `UserProfile` model in `apps/core/models/user_profile.py`
- [ ] Create `AuditLog` model in `apps/core/models/audit_log.py`
- [ ] Create `BaseToken` abstract model in `apps/core/models/base_token.py`
- [ ] Create `SessionToken` model (extending BaseToken) in `apps/core/models/session_token.py`
  - [ ] Add `token_family` field for replay detection (H9)
  - [ ] Add `is_refresh_token_used` field (H9)
  - [ ] Add `device_fingerprint` field (H8)
  - [ ] Add `last_activity_at` field (M8)
- [ ] Create `PasswordResetToken` model (extending BaseToken) in `apps/core/models/password_reset_token.py`
- [ ] Create `EmailVerificationToken` model (extending BaseToken) in `apps/core/models/email_verification_token.py`
- [ ] Create `TOTPDevice` model in `apps/core/models/totp_device.py`
  - [ ] Implement Fernet encryption for `secret` field (C2)
  - [ ] Add `device_name` field for multiple devices (H13)
- [ ] Create `PasswordHistory` model in `apps/core/models/password_history.py` (H11)
- [ ] Create custom `UserManager` in `apps/core/managers.py`
- [ ] Create password validators in `apps/core/validators.py`:
  - [ ] `MinimumLengthValidator` (12-character minimum)
  - [ ] `BreachedPasswordValidator` with HaveIBeenPwned integration (H5)
- [ ] Create default Groups (Organisation Owner, Admin, Member, Viewer)
- [ ] Create Django Admin configurations for User, Organisation, AuditLog
- [ ] Generate and run migrations
- [ ] Update Django settings to use custom User model

**Deliverable:** All database tables created and migrations applied.

**Tests:**

- Unit tests for model creation
- Unit tests for model validation (including 12-character password requirement)
- Unit tests for model relationships
- Unit tests for custom managers
- Unit tests for BaseToken abstract model methods (is_expired, is_valid)
- Unit tests for TOTP secret encryption/decryption (C2)
- Unit tests for BreachedPasswordValidator with mocked HIBP API (H5)
- Unit tests for password history prevention (H11)

---

### Phase 2: Authentication Service Layer

**Objective:** Implement business logic for authentication operations.

**Review Fixes Implemented:**

- **C1**: HMAC-SHA256 token hashing with secret key (see [Critical Issue C1](#c1-session-token-storage-vulnerability))
- **C3**: Password reset token hash-then-store pattern (see [Critical Issue C3](#c3-password-reset-token-not-hashed))
- **C6**: IP encryption key rotation management command (see [Critical Issue C6](#c6-ip-encryption-key-rotation-not-specified))
- **H1**: JWT RS256 algorithm with key rotation (see [High Priority H1](#h1-jwt-algorithm-specification))
- **H3**: Race condition prevention with SELECT FOR UPDATE (see [High Priority H3](#h3-race-condition-prevention))
- **H9**: Refresh token replay detection with token families (see [High Priority H9](#h9-refresh-token-replay-detection))
- **M5**: Timezone/DST handling with pytz (see [Medium Priority M5](#m5-timezonedsst-handling))

**Tasks:**

- [ ] Create `IPEncryption` utility in `apps/core/utils/encryption.py`
  - [ ] Implement key rotation support (C6)
- [ ] Create `TokenHasher` utility in `apps/core/utils/token_hasher.py`
  - [ ] Use HMAC-SHA256 with secret key, NOT plain SHA-256 (C1)
- [ ] Create `TokenService` in `apps/core/services/token_service.py`
  - [ ] Implement token family management for replay detection (H9)
  - [ ] Store only hashed tokens in database (C1, C3)
- [ ] Create `AuthService` in `apps/core/services/auth_service.py`
  - [ ] Implement race condition prevention with `select_for_update()` (H3)
  - [ ] Use timezone-aware datetime operations with pytz (M5)
- [ ] Create `AuditService` in `apps/core/services/audit_service.py`
- [ ] Create `EmailService` in `apps/core/services/email_service.py`
- [ ] Create `PasswordResetService` in `apps/core/services/password_reset_service.py`
  - [ ] Implement hash-then-store pattern (C3)
- [ ] Create management command `rotate_ip_keys` in `apps/core/management/commands/` (C6)
- [ ] Implement user registration logic
- [ ] Implement login logic (without 2FA)
- [ ] Implement password reset logic with hashed tokens (C3)
- [ ] Implement email verification logic
- [ ] Configure JWT settings with RS256 algorithm (H1)
- [ ] Configure Redis for session storage

**Deliverable:** Service layer with full authentication logic and security fixes.

**Tests:**

- Unit tests for each service method
- Unit tests for password hashing
- Unit tests for HMAC-SHA256 token hashing (C1)
- Unit tests for password reset token hash verification (C3)
- Unit tests for IP encryption/decryption and key rotation (C6)
- Unit tests for race condition handling with database locks (H3)
- Unit tests for refresh token replay detection (H9)
- Unit tests for timezone-aware operations (M5)

---

### Phase 3: GraphQL API Implementation

**Objective:** Expose authentication functionality via GraphQL API.

**Review Fixes Implemented:**

- **C4**: CSRF protection middleware for GraphQL mutations (see [Critical Issue C4](#c4-missing-csrf-protection))
- **C5**: Email verification enforcement blocking login (see [Critical Issue C5](#c5-email-verification-bypass))
- **H2**: DataLoaders for N+1 query prevention (see [High Priority H2](#h2-n1-query-prevention))
- **H4**: Standardised error codes and messages (see [High Priority H4](#h4-error-message-standardisation))
- **H10**: Proper logout with token revocation (see [High Priority H10](#h10-logout-token-revocation))
- **M1**: Rate limit headers in responses (see [Medium Priority M1](#m1-rate-limit-headers))

**Tasks:**

- [ ] Create GraphQL types in `api/types/user.py`
- [ ] Create GraphQL types in `api/types/organisation.py`
- [ ] Create GraphQL types in `api/types/auth.py`
- [ ] Create GraphQL inputs in `api/inputs/auth.py`
- [ ] Create permission classes in `api/permissions.py`
  - [ ] `IsAuthenticated` permission class
  - [ ] `HasPermission` permission class
  - [ ] `IsOrganisationOwner` permission class
- [ ] Create `GraphQLCSRFMiddleware` in `api/middleware/csrf.py` (C4)
  - [ ] Allow queries without CSRF token
  - [ ] Require CSRF token for all mutations
- [ ] Create DataLoaders in `api/dataloaders/` for N+1 prevention (H2)
  - [ ] `UserLoader`, `OrganisationLoader`, `SessionLoader`
- [ ] Create mutations in `api/mutations/auth.py`
  - [ ] Block login for unverified email addresses (C5)
  - [ ] Implement proper logout with token revocation (H10)
- [ ] Create queries in `api/queries/user.py`
  - [ ] Implement organisation boundary checks in all queries
  - [ ] Add permission checking examples using `user.has_perm()`
  - [ ] Use DataLoaders for related object fetching (H2)
- [ ] Update `api/schema.py` to include auth types
- [ ] Implement authentication middleware
- [ ] Implement organisation boundary enforcement in querysets
- [ ] Add standardised error handling with error codes (H4)
- [ ] Add rate limit headers to GraphQL responses (M1)

**Deliverable:** Full GraphQL API for authentication with permission checking and security fixes.

**Tests:**

- GraphQL mutation tests for registration
- GraphQL mutation tests for login
- GraphQL mutation tests for password reset
- GraphQL query tests for user data
- GraphQL tests for organisation boundaries
- GraphQL tests for permission checking (authenticated vs unauthenticated)
- GraphQL tests for cross-organisation access denial
- GraphQL tests for error handling with standardised codes (H4)
- GraphQL tests for CSRF protection on mutations (C4)
- GraphQL tests for email verification enforcement (C5)
- GraphQL tests for logout token revocation (H10)
- Performance tests verifying DataLoader effectiveness (H2)

---

### Phase 4: Two-Factor Authentication (2FA)

**Objective:** Implement TOTP-based 2FA.

**Review Fixes Implemented:**

- **C2**: TOTP secret encryption using Fernet (see [Critical Issue C2](#c2-totp-secret-storage-security))
- **H13**: Multiple TOTP device support with naming (see [High Priority H13](#h13-multiple-totp-devices))
- **H14**: Backup code hashing (see [High Priority H14](#h14-backup-code-hashing))
- **M3**: Improved backup code format (see [Medium Priority M3](#m3-backup-code-format))
- **M6**: TOTP time window tolerance (see [Medium Priority M6](#m6-totp-time-window))

**Tasks:**

- [ ] Install `pyotp` library for TOTP
- [ ] Create `TOTPEncryption` utility in `apps/core/utils/totp_encryption.py` (C2)
  - [ ] Use Fernet symmetric encryption with dedicated key
  - [ ] Implement `encrypt_secret()` and `decrypt_secret()` methods
- [ ] Create 2FA service in `apps/core/services/totp_service.py`
  - [ ] Encrypt secrets before storage (C2)
  - [ ] Decrypt secrets only when verifying (C2)
  - [ ] Support time window tolerance of ±1 period (M6)
- [ ] Implement QR code generation
- [ ] Implement backup code generation
  - [ ] Use format `XXXX-XXXX-XXXX` for readability (M3)
  - [ ] Store hashed backup codes only (H14)
  - [ ] Invalidate used backup codes
- [ ] Create GraphQL mutations for 2FA setup
  - [ ] Support multiple named TOTP devices per user (H13)
  - [ ] `setup2FA(deviceName: String)` mutation
  - [ ] `remove2FADevice(deviceId: ID!)` mutation
- [ ] Create GraphQL mutations for 2FA verification
- [ ] Update login flow to check for 2FA
- [ ] Update user settings for 2FA management
  - [ ] List all registered devices (H13)
  - [ ] Remove individual devices (H13)

**Deliverable:** Working 2FA system with QR codes and security fixes.

**Tests:**

- Unit tests for TOTP generation
- Unit tests for TOTP verification with time tolerance (M6)
- Unit tests for TOTP secret encryption/decryption (C2)
- Unit tests for backup code hashing and verification (H14)
- Unit tests for backup code format validation (M3)
- Integration tests for 2FA login flow
- Integration tests for multiple device management (H13)
- GraphQL tests for 2FA mutations

---

### Phase 5: Password Reset and Email Verification

**Objective:** Complete email-based workflows.

**Review Fixes Implemented:**

- **C3**: Password reset token hash-then-store (see [Critical Issue C3](#c3-password-reset-token-not-hashed))
- **H6**: Async email with Celery and retry logic (see [High Priority H6](#h6-async-email-delivery))
- **H11**: Password history enforcement (see [High Priority H11](#h11-password-history))
- **H12**: Token single-use enforcement (see [High Priority H12](#h12-token-single-use))
- **M2**: Email verification resend cooldown (see [Medium Priority M2](#m2-email-verification-resend-cooldown))
- **M4**: Account recovery without email (see [Medium Priority M4](#m4-account-recovery-alternatives))

**Tasks:**

- [ ] Create email templates for verification
- [ ] Create email templates for password reset
- [ ] Configure Mailpit for dev/test environments
- [ ] Configure SMTP for staging/production
- [ ] Implement token generation for reset
  - [ ] Store only hashed tokens in database (C3)
  - [ ] Return plain token to user via email (C3)
  - [ ] Mark tokens as used after single use (H12)
- [ ] Implement token generation for verification
  - [ ] Implement resend cooldown (5 minutes minimum) (M2)
  - [ ] Mark tokens as used after verification (H12)
- [ ] Create async email service with Celery (H6)
  - [ ] Implement retry logic with exponential backoff (H6)
  - [ ] Configure dead letter queue for failed emails (H6)
- [ ] Implement password history check on reset (H11)
  - [ ] Prevent reuse of last 5 passwords (H11)
- [ ] Implement account recovery alternatives (M4)
  - [ ] Support backup codes for email recovery (M4)
  - [ ] Security questions as fallback option (M4)
- [ ] Test email delivery in all environments

**Deliverable:** Working email verification and password reset with security fixes.

**Tests:**

- Integration tests for email verification flow
- Integration tests for password reset flow with hash verification (C3)
- Integration tests for password history enforcement (H11)
- Email template rendering tests
- Token expiration tests
- Token single-use tests (H12)
- Async email delivery tests with Celery (H6)
- Email resend cooldown tests (M2)
- Account recovery alternative tests (M4)

---

### Phase 6: Audit Logging and Security

**Objective:** Add comprehensive audit logging and security features.

**Review Fixes Implemented:**

- **C6**: IP encryption key rotation (see [Critical Issue C6](#c6-ip-encryption-key-rotation-not-specified))
- **H7**: Audit log retention policies (see [High Priority H7](#h7-audit-log-retention))
- **H9**: Refresh token replay detection (see [High Priority H9](#h9-refresh-token-replay-detection))
- **M1**: Rate limit headers in responses (see [Medium Priority M1](#m1-rate-limit-headers))
- **M7**: Concurrent session limits (see [Medium Priority M7](#m7-concurrent-session-limits))
- **M9**: Failed login attempt tracking (see [Medium Priority M9](#m9-failed-login-tracking))
- **M10**: Suspicious activity alerts (see [Medium Priority M10](#m10-suspicious-activity-alerts))

**Tasks:**

- [ ] Implement rate limiting middleware
  - [ ] Add rate limit headers to responses (M1)
  - [ ] `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- [ ] Create admin interface for audit logs
  - [ ] Implement retention policies with configurable periods (H7)
  - [ ] Auto-archive logs older than retention period (H7)
- [ ] Add audit log GraphQL queries
- [ ] Implement IP address tracking
  - [ ] Encryption with key rotation support (C6)
  - [ ] Create `rotate_ip_keys` management command (C6)
- [ ] Configure Redis for rate limiting
- [ ] Implement concurrent session management (M7)
  - [ ] Configurable max sessions per user (M7)
  - [ ] Auto-terminate oldest session when limit exceeded (M7)
- [ ] Implement failed login tracking (M9)
  - [ ] Track by IP and by user account (M9)
  - [ ] Progressive lockout with exponential backoff (M9)
- [ ] Implement suspicious activity detection (M10)
  - [ ] Alert on login from new location (M10)
  - [ ] Alert on password change (M10)
  - [ ] Alert on 2FA disable (M10)
- [ ] Add security headers middleware
- [ ] Configure CORS settings
- [ ] Add Sentry error tracking

**Deliverable:** Full audit logging and security controls with review fixes.

**Tests:**

- Unit tests for audit log creation
- Unit tests for audit log retention and archival (H7)
- Integration tests for rate limiting with headers (M1)
- Integration tests for concurrent session enforcement (M7)
- Integration tests for failed login tracking (M9)
- Security tests for CORS
- Tests for IP encryption and key rotation (C6)
- Tests for suspicious activity alert triggers (M10)

---

### Phase 7: Testing and Documentation

**Objective:** Comprehensive testing and documentation.

**Review Fixes Implemented:**

- **All Edge Cases**: 27 edge cases from QA review (see [Edge Cases Coverage](#edge-cases-coverage))
- **Security Tests**: Penetration testing for all critical fixes (C1-C6)
- **Integration Validation**: End-to-end flows covering all high priority fixes (H1-H15)

**Tasks:**

- [ ] Write BDD feature files for authentication scenarios
  - [ ] Include all 27 edge cases from QA review
  - [ ] Cover token expiry during operations (Edge Case #1)
  - [ ] Cover simultaneous login attempts (Edge Case #3)
  - [ ] Cover password change during active session (Edge Case #4)
- [ ] Write E2E tests for complete workflows
  - [ ] Registration → email verification → login → 2FA setup → logout
  - [ ] Password reset with hash verification (C3)
  - [ ] Session management with replay detection (H9)
- [ ] Write security penetration tests
  - [ ] Token brute-force resistance (C1)
  - [ ] TOTP secret extraction attempts (C2)
  - [ ] CSRF bypass attempts (C4)
  - [ ] Email verification bypass attempts (C5)
- [ ] Create user documentation for authentication
- [ ] Create developer documentation for API
  - [ ] Document all error codes (H4)
  - [ ] Document rate limit headers (M1)
- [ ] Update README with authentication setup
- [ ] Create migration guide for existing systems
- [ ] Generate API documentation with examples
- [ ] Code review and refactoring
  - [ ] Verify all critical fixes implemented correctly
  - [ ] Security-focused code review

**Deliverable:** Full test coverage, documentation, and security validation.

**Tests:**

- BDD tests for all user scenarios including 27 edge cases
- E2E tests for registration → login → 2FA flow
- E2E tests for password reset with hash verification
- E2E tests for session management and token families
- Performance tests for authentication endpoints
- Security penetration tests for all critical vulnerabilities
- Load tests for concurrent session handling

---

## Testing Strategy

### Unit Tests (TDD)

Write tests first for all business logic components.

**Test Files:**

```
tests/unit/apps/core/
├── test_user_model.py
├── test_organisation_model.py
├── test_user_profile_model.py
├── test_audit_log_model.py
├── test_session_token_model.py
├── test_password_validators.py
├── test_ip_encryption.py
├── test_token_service.py
├── test_auth_service.py
├── test_audit_service.py
├── test_email_service.py
└── test_totp_service.py
```

**Example Test:**

```python
# tests/unit/apps/core/test_user_model.py

import pytest
from django.core.exceptions import ValidationError
from apps.core.models import User, Organisation

class TestUserModel:
    """Unit tests for User model."""

    @pytest.fixture
    def organisation(self, db):
        """Create test organisation."""
        return Organisation.objects.create(
            name="Test Org",
            slug="test-org"
        )

    def test_user_creation_with_valid_data(self, organisation) -> None:
        """Test user is created with valid data.

        Given: Valid user data
        When: User.objects.create_user() is called
        Then: User is created with correct attributes
        """
        user = User.objects.create_user(
            email="test@example.com",
            password="SecurePass123!",
            first_name="Test",
            last_name="User",
            organisation=organisation
        )

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.check_password("SecurePass123!")
        assert user.organisation == organisation

    def test_email_must_be_unique(self, organisation) -> None:
        """Test email uniqueness constraint.

        Given: A user with email "test@example.com" exists
        When: Creating another user with same email
        Then: ValidationError is raised
        """
        User.objects.create_user(
            email="test@example.com",
            password="SecurePass123!",
            organisation=organisation
        )

        with pytest.raises(ValidationError):
            user = User(
                email="test@example.com",
                organisation=organisation
            )
            user.full_clean()
```

### BDD Tests

Write human-readable scenarios for authentication flows.

**Feature File:**

```gherkin
# tests/bdd/features/authentication.feature

Feature: User Authentication
  As a user
  I want to register and login to the system
  So that I can access my account

  Background:
    Given the system is running
    And an organisation "Test Org" with slug "test-org" exists

  Scenario: Successful user registration
    When I register with:
      | email           | password       | firstName | lastName | organisation |
      | new@example.com | SecurePass123! | New       | User     | test-org     |
    Then registration should succeed
    And I should receive a verification email
    And I should be logged in
    And an audit log entry should exist for "register"

  Scenario: Login with valid credentials (no 2FA)
    Given a user exists with:
      | email           | password       | firstName | organisation |
      | user@example.com| SecurePass123! | Test      | test-org     |
    When I login with email "user@example.com" and password "SecurePass123!"
    Then login should succeed
    And I should receive an authentication token
    And an audit log entry should exist for "login_success"

  Scenario: Login with 2FA enabled
    Given a user exists with 2FA enabled:
      | email           | password       | organisation |
      | user@example.com| SecurePass123! | test-org     |
    When I login with email "user@example.com" and password "SecurePass123!"
    Then I should be prompted for 2FA code
    When I submit a valid TOTP code
    Then login should succeed
    And I should receive an authentication token

  Scenario: Failed login with invalid password
    Given a user exists with:
      | email           | password       | organisation |
      | user@example.com| SecurePass123! | test-org     |
    When I login with email "user@example.com" and password "WrongPassword"
    Then login should fail
    And I should see error "Invalid credentials"
    And an audit log entry should exist for "login_failed"

  Scenario: Password reset flow
    Given a user exists with email "user@example.com"
    When I request a password reset for "user@example.com"
    Then I should receive a password reset email
    When I click the reset link
    And I submit new password "NewSecurePass123!"
    Then password should be updated
    And I can login with the new password
```

### Integration Tests

Test multiple components working together.

```python
# tests/integration/test_auth_flow.py

import pytest
from django.test import Client
from apps.core.models import User, Organisation, AuditLog

@pytest.mark.integration
class TestAuthenticationFlow:
    """Integration tests for authentication workflow."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Set up test data."""
        self.client = Client()
        self.org = Organisation.objects.create(
            name="Test Org",
            slug="test-org"
        )

    def test_complete_registration_and_login_flow(self) -> None:
        """Test user can register and login.

        Workflow:
        1. User registers
        2. Email verification sent
        3. User verifies email
        4. User logs in
        5. User accesses protected resource
        """
        # Step 1: Register
        register_mutation = """
        mutation Register($input: RegisterInput!) {
            register(input: $input) {
                token
                user {
                    email
                    emailVerified
                }
            }
        }
        """

        response = self.client.post('/graphql/', {
            'query': register_mutation,
            'variables': {
                'input': {
                    'email': 'new@example.com',
                    'password': 'SecurePass123!',
                    'firstName': 'New',
                    'lastName': 'User',
                    'organisationSlug': 'test-org'
                }
            }
        })

        assert response.status_code == 200
        data = response.json()
        assert 'token' in data['data']['register']
        assert data['data']['register']['user']['email'] == 'new@example.com'

        # Step 2: Verify email verification token created
        user = User.objects.get(email='new@example.com')
        assert not user.email_verified
        assert user.verification_tokens.exists()

        # Step 3: Verify email
        token = user.verification_tokens.first().token
        verify_mutation = """
        mutation VerifyEmail($token: String!) {
            verifyEmail(token: $token)
        }
        """

        response = self.client.post('/graphql/', {
            'query': verify_mutation,
            'variables': {'token': token}
        })

        user.refresh_from_db()
        assert user.email_verified

        # Step 4: Login
        login_mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                token
                user {
                    email
                }
            }
        }
        """

        response = self.client.post('/graphql/', {
            'query': login_mutation,
            'variables': {
                'input': {
                    'email': 'new@example.com',
                    'password': 'SecurePass123!'
                }
            }
        })

        assert response.status_code == 200
        token = response.json()['data']['login']['token']

        # Step 5: Access protected resource
        me_query = """
        query {
            me {
                email
                organisation {
                    name
                }
            }
        }
        """

        response = self.client.post(
            '/graphql/',
            {'query': me_query},
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )

        assert response.status_code == 200
        assert response.json()['data']['me']['email'] == 'new@example.com'
```

### End-to-End Tests

Test complete user workflows across the system.

```python
# tests/e2e/test_user_authentication_e2e.py

import pytest
from playwright.sync_api import Page, expect

@pytest.mark.e2e
class TestAuthenticationE2E:
    """E2E tests for authentication workflows."""

    def test_complete_registration_to_2fa_login(self, page: Page) -> None:
        """Test complete workflow from registration to 2FA login.

        This test covers:
        1. User registration
        2. Email verification
        3. Enable 2FA
        4. Logout
        5. Login with 2FA
        """
        # Step 1: Register
        page.goto('http://localhost:3000/register')
        page.fill('input[name="email"]', 'testuser@example.com')
        page.fill('input[name="password"]', 'SecurePass123!')
        page.fill('input[name="firstName"]', 'Test')
        page.fill('input[name="lastName"]', 'User')
        page.select_option('select[name="organisation"]', 'test-org')
        page.click('button[type="submit"]')

        # Wait for redirect to dashboard
        expect(page).to_have_url('http://localhost:3000/dashboard')

        # Step 2: Verify email (simulate clicking email link)
        # In real scenario, this would be from email
        page.goto('http://localhost:3000/verify-email?token=...')
        expect(page.locator('text=Email verified successfully')).to_be_visible()

        # Step 3: Enable 2FA
        page.goto('http://localhost:3000/settings/security')
        page.click('button:has-text("Enable 2FA")')

        # Scan QR code (in test, we extract secret)
        qr_code = page.locator('img[alt="QR Code"]')
        expect(qr_code).to_be_visible()

        # Enter TOTP code from authenticator
        page.fill('input[name="totpCode"]', '123456')  # Mock code
        page.click('button:has-text("Verify")')

        expect(page.locator('text=2FA enabled successfully')).to_be_visible()

        # Step 4: Logout
        page.click('button:has-text("Logout")')
        expect(page).to_have_url('http://localhost:3000/login')

        # Step 5: Login with 2FA
        page.fill('input[name="email"]', 'testuser@example.com')
        page.fill('input[name="password"]', 'SecurePass123!')
        page.click('button[type="submit"]')

        # 2FA prompt
        expect(page.locator('text=Enter your 2FA code')).to_be_visible()
        page.fill('input[name="totpCode"]', '123456')
        page.click('button[type="submit"]')

        # Should be logged in
        expect(page).to_have_url('http://localhost:3000/dashboard')
```

### GraphQL API Tests

Test GraphQL queries and mutations.

```python
# tests/graphql/test_auth_mutations.py

import pytest
from apps.core.models import User, Organisation

@pytest.mark.graphql
class TestAuthMutations:
    """Test GraphQL authentication mutations."""

    @pytest.fixture
    def organisation(self, db):
        """Create test organisation."""
        return Organisation.objects.create(
            name="Test Org",
            slug="test-org"
        )

    def test_register_mutation_creates_user(
        self,
        graphql_client,
        organisation
    ) -> None:
        """Test register mutation creates user.

        GraphQL Mutation:
        mutation {
          register(input: {...}) {
            token
            user { email }
          }
        }
        """
        mutation = """
        mutation Register($input: RegisterInput!) {
            register(input: $input) {
                token
                refreshToken
                user {
                    id
                    email
                    firstName
                    lastName
                    organisation {
                        name
                    }
                }
            }
        }
        """

        response = graphql_client.execute(
            mutation,
            variables={
                'input': {
                    'email': 'new@example.com',
                    'password': 'SecurePass123!',
                    'firstName': 'New',
                    'lastName': 'User',
                    'organisationSlug': 'test-org'
                }
            }
        )

        assert 'errors' not in response
        assert response['data']['register']['token'] is not None
        assert response['data']['register']['user']['email'] == 'new@example.com'

        # Verify user created in database
        user = User.objects.get(email='new@example.com')
        assert user.first_name == 'New'
        assert user.organisation == organisation

    def test_login_mutation_with_invalid_password(
        self,
        graphql_client,
        organisation
    ) -> None:
        """Test login mutation fails with invalid password."""
        # Create user
        user = User.objects.create_user(
            email='test@example.com',
            password='SecurePass123!',
            organisation=organisation
        )

        mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                token
            }
        }
        """

        response = graphql_client.execute(
            mutation,
            variables={
                'input': {
                    'email': 'test@example.com',
                    'password': 'WrongPassword'
                }
            }
        )

        assert 'errors' in response
        assert 'Invalid credentials' in response['errors'][0]['message']
```

### Security Tests

Test security features and vulnerabilities.

```python
# tests/security/test_auth_security.py

import pytest
from apps.core.models import User, Organisation
from apps.core.utils.encryption import IPEncryption

@pytest.mark.security
class TestAuthenticationSecurity:
    """Security tests for authentication system."""

    def test_password_is_hashed_not_plaintext(self, db) -> None:
        """Test passwords are stored as hashes, not plaintext.

        Security Check: Passwords must never be stored in plaintext.
        """
        org = Organisation.objects.create(name="Test", slug="test")
        user = User.objects.create_user(
            email='test@example.com',
            password='SecurePass123!',
            organisation=org
        )

        # Password should be hashed
        assert user.password != 'SecurePass123!'
        assert user.password.startswith('argon2')

        # check_password should work
        assert user.check_password('SecurePass123!')
        assert not user.check_password('WrongPassword')

    def test_ip_addresses_are_encrypted(self, db) -> None:
        """Test IP addresses are encrypted before storage.

        Security Check: IP addresses are PII and must be encrypted.
        """
        ip = '192.168.1.100'
        encrypted = IPEncryption.encrypt_ip(ip)

        # Encrypted should be different from original
        assert encrypted != ip.encode()

        # Decryption should return original
        decrypted = IPEncryption.decrypt_ip(encrypted)
        assert decrypted == ip

    def test_rate_limiting_blocks_brute_force(
        self,
        graphql_client,
        organisation
    ) -> None:
        """Test rate limiting prevents brute force attacks.

        Security Check: Login attempts must be rate limited.
        """
        # Create user
        User.objects.create_user(
            email='test@example.com',
            password='SecurePass123!',
            organisation=organisation
        )

        mutation = """
        mutation Login($input: LoginInput!) {
            login(input: $input) {
                token
            }
        }
        """

        # Attempt 10 failed logins
        for i in range(10):
            response = graphql_client.execute(
                mutation,
                variables={
                    'input': {
                        'email': 'test@example.com',
                        'password': f'WrongPassword{i}'
                    }
                }
            )

        # After 5 attempts, should be rate limited
        assert 'errors' in response
        assert 'rate limit' in response['errors'][0]['message'].lower()
```

---

## Risks and Mitigations

| Risk                                 | Likelihood | Impact | Mitigation                                                       |
| ------------------------------------ | ---------- | ------ | ---------------------------------------------------------------- |
| Password database breach             | Low        | High   | Use Argon2 hashing, require strong passwords, enable 2FA         |
| Session token theft                  | Medium     | High   | Use HTTPS only, secure token storage, short expiration           |
| Brute force login attacks            | High       | Medium | Implement rate limiting, account lockout, CAPTCHA                |
| Email service unavailable            | Medium     | Medium | Queue emails, retry logic, fallback SMTP provider                |
| Redis cache unavailable              | Low        | Medium | Graceful degradation to database, automatic reconnection         |
| IP encryption key compromised        | Low        | High   | Rotate keys regularly, use environment variables, access control |
| 2FA device lost                      | Medium     | Medium | Provide backup codes, admin recovery process                     |
| Audit log tampering                  | Low        | High   | Immutable logs, database-level constraints, regular backups      |
| Organisation boundary bypass         | Low        | High   | Strict GraphQL resolver checks, database row-level security      |
| TOTP secret extraction               | Low        | High   | Encrypt secrets, secure QR code transmission                     |
| Password reset token interception    | Medium     | High   | Short expiration (15 min), HTTPS only, one-time use              |
| Email verification bypass            | Low        | Medium | Limit unverified user actions, token expiration                  |
| Concurrent session attacks           | Medium     | Medium | Token revocation, device tracking, session limits                |
| Database migration data loss         | Low        | High   | Backup before migration, test in staging, rollback plan          |
| GraphQL query depth attack           | Medium     | Medium | Query depth limiting (max 10), complexity analysis               |
| Performance degradation under load   | Medium     | Medium | Redis caching, database indexing, horizontal scaling             |
| GDPR compliance violations           | Low        | High   | User data export, right to deletion, audit trail, encryption     |
| Third-party dependency vulnerability | Medium     | Medium | Regular updates, security scanning, dependency pinning           |

---

## Open Questions

- [ ] **Should we support OAuth/Social login?** (Google, GitHub, etc.)
  - Decision: Defer to Phase 2 (not MVP)

- [ ] **What is the maximum number of active sessions per user?**
  - Decision: 5 sessions per user, oldest revoked automatically

- [ ] **Should email verification be mandatory before login?**
  - Decision: No, but limit actions for unverified users

- [ ] **How long should password reset tokens be valid?**
  - Decision: 15 minutes

- [ ] **Should we implement "Remember Me" functionality?**
  - Decision: Yes, extend refresh token to 30 days

- [ ] **What should happen to user data when organisation is deleted?**
  - Decision: Soft delete, retain for 90 days, then hard delete

- [ ] **Should we support multi-organisation users?**
  - Decision: Not in MVP, one organisation per user

- [ ] **How should we handle timezone for audit logs?**
  - Decision: Store in UTC, display in user's timezone

- [ ] **Should superusers bypass organisation boundaries?**
  - Decision: Yes, superusers can access all organisations

- [ ] **What's the strategy for IP encryption key rotation?**
  - Decision: Manual rotation quarterly, re-encrypt existing data

---

## Success Criteria

**Phase 1 Complete When:**

- [ ] All database models created and migrated
- [ ] Custom User model configured in Django settings
- [ ] Password validators working correctly
- [ ] All model unit tests passing
- [ ] Code coverage > 90% for models

**Phase 2 Complete When:**

- [ ] User registration service functional
- [ ] Login service functional (without 2FA)
- [ ] Password hashing with Argon2 working
- [ ] Token generation and validation working
- [ ] IP encryption functional
- [ ] All service unit tests passing
- [ ] Code coverage > 90% for services

**Phase 3 Complete When:**

- [ ] GraphQL API exposed for registration
- [ ] GraphQL API exposed for login
- [ ] GraphQL API exposed for user queries
- [ ] Organisation boundaries enforced
- [ ] All GraphQL tests passing
- [ ] Postman/GraphiQL documentation complete

**Phase 4 Complete When:**

- [ ] 2FA setup working with QR codes
- [ ] 2FA verification working
- [ ] Login flow includes 2FA check
- [ ] Backup codes generated
- [ ] All 2FA tests passing

**Phase 5 Complete When:**

- [ ] Email verification working
- [ ] Password reset working
- [ ] Emails delivered in all environments
- [ ] Email templates rendering correctly
- [ ] All email flow tests passing

**Phase 6 Complete When:**

- [ ] Rate limiting active on auth endpoints
- [ ] Audit logs created for all auth events
- [ ] IP addresses encrypted in logs
- [ ] Admin can view audit logs
- [ ] All security tests passing

**Phase 7 Complete When:**

- [ ] All BDD scenarios passing
- [ ] All E2E tests passing
- [ ] Code coverage > 80% overall
- [ ] Documentation complete
- [ ] Security audit passed
- [ ] Performance benchmarks met

---

## Next Steps

**After This Plan is Approved:**

1. Run `/syntek-dev-suite:stories` to create user stories for each phase
2. Run `/syntek-dev-suite:sprint` to organise stories into balanced sprints
3. Start with Phase 1: Core Models and Database
4. For each phase:
   - Run `/syntek-dev-suite:test-writer` to create tests first (TDD)
   - Run `/syntek-dev-suite:backend` to implement models and services
   - Run `/syntek-dev-suite:review` for code review
   - Run `/syntek-dev-suite:syntax` to fix any linting errors
   - Run tests to verify implementation
5. After all phases complete:
   - Run `/syntek-dev-suite:docs` to generate documentation
   - Run `/syntek-dev-suite:security` for security audit
   - Deploy to staging for testing

**Handoff to Other Agents:**

- **Backend Agent**: Implement models, services, and GraphQL API
- **Test Writer Agent**: Create comprehensive test suites
- **Security Agent**: Audit security features and fix vulnerabilities
- **Docs Agent**: Write developer and user documentation
- **Frontend Agent** (later): Build UI for authentication flows

---

**Last Updated:** 07/01/2026
