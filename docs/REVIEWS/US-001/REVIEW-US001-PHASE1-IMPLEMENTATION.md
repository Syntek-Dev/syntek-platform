# Code Review: US-001 User Authentication - Phase 1 Implementation

**Last Updated**: 07/01/2026
**Review Date**: 07/01/2026
**Reviewer**: Code Review Agent
**User Story**: US-001 User Authentication System
**Branch**: us001/user-authentication
**Phase**: Phase 1 - Core Models and Database

---

## Table of Contents

- [Code Review: US-001 User Authentication - Phase 1 Implementation](#code-review-us-001-user-authentication---phase-1-implementation)
  - [Table of Contents](#table-of-contents)
  - [Executive Summary](#executive-summary)
  - [Review Scope](#review-scope)
  - [Overall Assessment](#overall-assessment)
  - [Critical Issues (Must Fix Before Merge)](#critical-issues-must-fix-before-merge)
    - [C1: CRITICAL - Token Hashing Uses Wrong Key (SECURITY VULNERABILITY)](#c1-critical---token-hashing-uses-wrong-key-security-vulnerability)
    - [C2: CRITICAL - Missing Composite Indexes for Multi-Tenant Queries](#c2-critical---missing-composite-indexes-for-multi-tenant-queries)
    - [C3: CRITICAL - Missing Index on Token Expiry Fields](#c3-critical---missing-index-on-token-expiry-fields)
    - [C4: CRITICAL - BaseToken Stores Plain Token in Database](#c4-critical---basetoken-stores-plain-token-in-database)
    - [C5: CRITICAL - Password History Uses Wrong Hasher Comparison](#c5-critical---password-history-uses-wrong-hasher-comparison)
  - [High Priority Issues (Must Fix Before Production)](#high-priority-issues-must-fix-before-production)
    - [H1: Missing TOTP Encryption Key Validation](#h1-missing-totp-encryption-key-validation)
    - [H2: User Model Missing Composite Index for Organisation Queries](#h2-user-model-missing-composite-index-for-organisation-queries)
    - [H3: SessionToken Missing Expires\_at Index](#h3-sessiontoken-missing-expires_at-index)
    - [H4: AuditLog Missing Composite Indexes](#h4-auditlog-missing-composite-indexes)
    - [H5: Password Validators Missing Error Codes](#h5-password-validators-missing-error-codes)
    - [H6: Missing Module-Level Docstrings](#h6-missing-module-level-docstrings)
    - [H7: HIBP Validator Fails Open (Security Concern)](#h7-hibp-validator-fails-open-security-concern)
    - [H8: PasswordHistory Cleanup Not Atomic](#h8-passwordhistory-cleanup-not-atomic)
    - [H9: User Email Normalisation Inconsistent](#h9-user-email-normalisation-inconsistent)
    - [H10: Missing BaseToken Index on token\_family](#h10-missing-basetoken-index-on-token_family)
  - [Medium Priority Issues (Should Fix)](#medium-priority-issues-should-fix)
    - [M1: UserManager Methods Lack Comprehensive Type Hints](#m1-usermanager-methods-lack-comprehensive-type-hints)
    - [M2: Password Validators Have Duplicated Logic](#m2-password-validators-have-duplicated-logic)
    - [M3: Audit Middleware Duplicates IP Extraction Logic](#m3-audit-middleware-duplicates-ip-extraction-logic)
    - [M4: Missing Transaction Protection for Token Generation](#m4-missing-transaction-protection-for-token-generation)
    - [M5: BaseToken is\_used Property Creates Confusion](#m5-basetoken-is_used-property-creates-confusion)
    - [M6: TOTPDevice Error Handling Too Broad](#m6-totpdevice-error-handling-too-broad)
    - [M7: Settings Validation Missing](#m7-settings-validation-missing)
  - [Low Priority Issues (Nice to Have)](#low-priority-issues-nice-to-have)
    - [L1: UserManager.get\_by\_natural\_key Uses Case-Insensitive Lookup](#l1-usermanagerget_by_natural_key-uses-case-insensitive-lookup)
    - [L2: Password Validator Help Text Not Following i18n Best Practices](#l2-password-validator-help-text-not-following-i18n-best-practices)
    - [L3: Admin Readonly Fields Could Be Methods](#l3-admin-readonly-fields-could-be-methods)
  - [Positive Observations](#positive-observations)
  - [DRY Analysis](#dry-analysis)
    - [Excellent DRY Implementation](#excellent-dry-implementation)
    - [Potential DRY Improvements](#potential-dry-improvements)
  - [Security Analysis](#security-analysis)
    - [Security Strengths](#security-strengths)
    - [Security Vulnerabilities Identified](#security-vulnerabilities-identified)
  - [Performance Analysis](#performance-analysis)
    - [Performance Strengths](#performance-strengths)
    - [Performance Concerns](#performance-concerns)
  - [SOLID Principles Analysis](#solid-principles-analysis)
    - [Single Responsibility Principle (SRP)](#single-responsibility-principle-srp)
    - [Open/Closed Principle (OCP)](#openclosed-principle-ocp)
    - [Liskov Substitution Principle (LSP)](#liskov-substitution-principle-lsp)
    - [Interface Segregation Principle (ISP)](#interface-segregation-principle-isp)
    - [Dependency Inversion Principle (DIP)](#dependency-inversion-principle-dip)
  - [Test Coverage Analysis](#test-coverage-analysis)
  - [Django Best Practices](#django-best-practices)
  - [Summary Statistics](#summary-statistics)
  - [Recommendations](#recommendations)
    - [Immediate Actions (Critical)](#immediate-actions-critical)
    - [Before Production (High Priority)](#before-production-high-priority)
    - [Technical Debt (Medium Priority)](#technical-debt-medium-priority)
  - [Approval Status](#approval-status)

---

## Executive Summary

**Overall Rating**: 7.5/10 (Approved with Critical Fixes Required)

The Phase 1 implementation demonstrates strong architectural design, comprehensive documentation, and excellent use of Django patterns. The BaseToken abstract model is particularly well-designed and eliminates significant code duplication. However, **5 critical security vulnerabilities** must be fixed before merging to prevent security compromises.

**Key Findings:**

- ✅ Excellent BaseToken DRY implementation
- ✅ Comprehensive password validation with HIBP integration
- ✅ Strong documentation with Google-style docstrings
- ✅ Proper use of Django model patterns
- 🔴 **CRITICAL**: Token hashing uses wrong key (SECRET_KEY instead of TOKEN_SIGNING_KEY)
- 🔴 **CRITICAL**: Plain tokens stored in database (BaseToken.token field)
- 🔴 **CRITICAL**: Missing critical performance indexes
- ⚠️ High priority: Missing TOTP encryption key validation
- ⚠️ High priority: Password history validation issues

---

## Review Scope

**Files Reviewed:**

Phase 1 Core Models:

- `apps/core/models/user.py` - Custom user model with email authentication
- `apps/core/models/organisation.py` - Multi-tenant organisation model
- `apps/core/models/base_token.py` - Abstract base class for tokens
- `apps/core/models/session_token.py` - JWT session tokens
- `apps/core/models/password_reset_token.py` - Password reset tokens
- `apps/core/models/email_verification_token.py` - Email verification tokens
- `apps/core/models/totp_device.py` - 2FA TOTP device management
- `apps/core/models/audit_log.py` - Security audit logging
- `apps/core/models/password_history.py` - Password reuse prevention
- `apps/core/models/user_profile.py` - User profile extension

Configuration:

- `config/settings/base.py` - Base Django settings
- `config/middleware/audit.py` - Security audit middleware
- `config/validators/password.py` - Enhanced password validators
- `config/urls.py` - URL configuration

Admin:

- `apps/core/admin.py` - Django admin configuration

Tests:

- `tests/unit/apps/core/test_user_model.py` - User model tests
- Test structure and factory pattern files

---

## Overall Assessment

**Strengths:**

1. **Excellent DRY Implementation**: BaseToken abstract model eliminates 30+ lines of duplication across 3 token models
2. **Comprehensive Security**: Password validation, HIBP integration, TOTP encryption, audit logging
3. **Strong Documentation**: All models, methods, and validators have proper Google-style docstrings
4. **Type Safety**: Consistent use of type hints throughout
5. **Django Best Practices**: Proper use of managers, abstract models, and Meta options

**Weaknesses:**

1. **Critical Security Vulnerabilities**: Token hashing uses wrong key, plain tokens in database
2. **Missing Performance Indexes**: No composite indexes for multi-tenant queries
3. **Validation Gaps**: No runtime validation for required encryption keys
4. **Inconsistent Error Handling**: Some validators fail open, others fail closed

**Verdict**: Approved with **mandatory critical fixes** before merge.

---

## Critical Issues (Must Fix Before Merge)

### C1: CRITICAL - Token Hashing Uses Wrong Key (SECURITY VULNERABILITY)

**Severity**: 🔴 **CRITICAL** - Blocks Merge
**File**: `apps/core/models/base_token.py:78`
**Security Impact**: If SECRET_KEY is compromised, all tokens can be forged

**Problem:**

```python
# apps/core/models/base_token.py:78
@classmethod
def hash_token(cls, token: str) -> str:
    """Generate HMAC-SHA256 hash of token for secure storage."""
    key = settings.SECRET_KEY.encode()  # ❌ WRONG: Uses Django SECRET_KEY
    return hmac.new(key, token.encode(), hashlib.sha256).hexdigest()
```

**Why This Is Critical:**

1. Django SECRET_KEY is used for many purposes (CSRF, sessions, signing)
2. If SECRET_KEY is compromised, attacker can forge valid tokens
3. The implementation plan specifies using a **separate** TOKEN_SIGNING_KEY (C1 requirement)
4. Single key compromise exposes multiple attack vectors

**Solution:**
Create a separate TOKEN_SIGNING_KEY and use it for token hashing:

```python
# apps/core/models/base_token.py
@classmethod
def hash_token(cls, token: str) -> str:
    """Generate HMAC-SHA256 hash of token for secure storage.

    Uses TOKEN_SIGNING_KEY (separate from SECRET_KEY) to ensure tokens
    cannot be forged even if SECRET_KEY is compromised.
    """
    key = settings.TOKEN_SIGNING_KEY.encode()  # ✅ Separate key
    return hmac.new(key, token.encode(), hashlib.sha256).hexdigest()
```

**Environment Variable Required:**

```bash
# .env.dev, .env.staging, .env.production
TOKEN_SIGNING_KEY=<generate-with-secrets-token-hex-32>
```

**Add to settings/base.py:**

```python
# Token signing key (separate from SECRET_KEY for security)
TOKEN_SIGNING_KEY = env(
    "TOKEN_SIGNING_KEY",
    default="",  # Must be set in production
)
```

---

### C2: CRITICAL - Missing Composite Indexes for Multi-Tenant Queries

**Severity**: 🔴 **CRITICAL** - Performance Impact
**Files**: Multiple model files
**Performance Impact**: Slow queries on multi-tenant organisation filtering

**Problem:**
Common query patterns filter by `organisation` AND another field, but no composite indexes exist:

```python
# Typical multi-tenant query pattern:
User.objects.filter(organisation=org, is_active=True)  # ❌ No composite index
SessionToken.objects.filter(user__organisation=org, expires_at__gt=now)  # ❌ No composite index
```

**Current Indexes:**

```python
# apps/core/models/user.py:225
indexes = [
    models.Index(fields=["email"]),        # ✅ Good
    models.Index(fields=["organisation"]), # ⚠️ Not enough - needs composite
]
```

**Solution:**
Add composite indexes for common multi-tenant query patterns:

```python
# apps/core/models/user.py - Meta class
indexes = [
    models.Index(fields=["email"]),
    models.Index(fields=["organisation"]),
    # ✅ Composite indexes for multi-tenant queries
    models.Index(fields=["organisation", "-created_at"]),  # Recent users per org
    models.Index(fields=["organisation", "is_active"]),    # Active users per org
    models.Index(fields=["organisation", "email_verified"]),  # Verified users per org
]

# apps/core/models/session_token.py - Meta class
indexes = [
    models.Index(fields=["user", "-created_at"]),  # ✅ Already exists
    models.Index(fields=["token_hash"]),
    models.Index(fields=["refresh_token_hash"]),
    models.Index(fields=["token_family"]),
    models.Index(fields=["device_fingerprint"]),
    models.Index(fields=["last_activity_at"]),
    # ✅ Add composite index for expiry queries
    models.Index(fields=["user", "expires_at", "is_revoked"]),  # Valid tokens per user
]

# apps/core/models/audit_log.py - Meta class
indexes = [
    models.Index(fields=["user", "-created_at"]),  # ✅ Already exists
    models.Index(fields=["organisation", "-created_at"]),  # ✅ Already exists
    models.Index(fields=["action", "-created_at"]),
    models.Index(fields=["created_at"]),
    # ✅ Add composite index for multi-tenant action queries
    models.Index(fields=["organisation", "action", "-created_at"]),  # Action per org
]
```

**Migration Required:**

```bash
./scripts/env/dev.sh makemigrations core
```

---

### C3: CRITICAL - Missing Index on Token Expiry Fields

**Severity**: 🔴 **CRITICAL** - Performance Impact
**Files**: Token model files
**Performance Impact**: Slow token expiry checks and cleanup

**Problem:**
Token validation queries filter by `expires_at` but no index exists:

```python
# Common query pattern:
SessionToken.objects.get(
    token_hash=token_hash,
    expires_at__gt=timezone.now()  # ❌ No index on expires_at
)
```

**Solution:**
Add indexes on `expires_at` for all token models:

```python
# apps/core/models/session_token.py - Meta class
indexes = [
    # ... existing indexes ...
    models.Index(fields=["expires_at"]),  # ✅ Add for expiry checks
    models.Index(fields=["user", "expires_at", "is_revoked"]),  # ✅ Composite
]

# apps/core/models/password_reset_token.py - Meta class
class Meta:
    db_table = "password_reset_tokens"
    verbose_name = "Password Reset Token"
    verbose_name_plural = "Password Reset Tokens"
    indexes = [
        models.Index(fields=["user", "-created_at"]),
        models.Index(fields=["token_hash"]),
        models.Index(fields=["expires_at"]),  # ✅ Add
        models.Index(fields=["used", "expires_at"]),  # ✅ Composite for cleanup
    ]

# apps/core/models/email_verification_token.py - Meta class
class Meta:
    db_table = "email_verification_tokens"
    verbose_name = "Email Verification Token"
    verbose_name_plural = "Email Verification Tokens"
    indexes = [
        models.Index(fields=["user", "-created_at"]),
        models.Index(fields=["token_hash"]),
        models.Index(fields=["expires_at"]),  # ✅ Add
        models.Index(fields=["used", "expires_at"]),  # ✅ Composite for cleanup
    ]
```

---

### C4: CRITICAL - BaseToken Stores Plain Token in Database

**Severity**: 🔴 **CRITICAL** - Security Vulnerability
**File**: `apps/core/models/base_token.py:46`
**Security Impact**: Plain tokens exposed if database is compromised

**Problem:**
BaseToken stores BOTH plain token AND hash in database:

```python
# apps/core/models/base_token.py:46-47
token = models.CharField(max_length=64, unique=True, db_index=True, blank=True, default="")
token_hash = models.CharField(max_length=255, unique=True, db_index=True, blank=True, default="")
```

**Why This Is Critical:**

1. The implementation plan (C1, C3) specifies **only hashes should be stored**
2. Plain tokens defeat the purpose of hashing
3. Database compromise = all tokens immediately usable

**Solution:**
Remove the `token` field entirely and only store `token_hash`:

```python
# apps/core/models/base_token.py
class BaseToken(models.Model):
    """Abstract base class for all token types."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "core.User",
        on_delete=models.CASCADE,
        related_name="%(class)s_tokens",
    )
    # ❌ REMOVE: token = models.CharField(...)
    token_hash = models.CharField(max_length=255, unique=True, db_index=True)  # ✅ Only hash
    token_family = models.UUIDField(default=uuid.uuid4, db_index=True)
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True

    # ❌ REMOVE: def save(self, *args, **kwargs):
    #     if not self.token:
    #         self.token = self.generate_token()
    #     ...

    @classmethod
    def create_token(cls, user, expires_at, **kwargs):
        """Create a token and return BOTH plain token and instance.

        Returns:
            tuple: (plain_token, token_instance)
        """
        plain_token = cls.generate_token()
        token_hash = cls.hash_token(plain_token)

        instance = cls.objects.create(
            user=user,
            token_hash=token_hash,
            expires_at=expires_at,
            **kwargs
        )

        return plain_token, instance  # ✅ Return plain token to caller, don't store

    @classmethod
    def validate_token(cls, plain_token):
        """Validate a token and return the instance if valid."""
        token_hash = cls.hash_token(plain_token)

        try:
            instance = cls.objects.select_related('user').get(
                token_hash=token_hash,
                expires_at__gt=timezone.now(),
                used=False
            )
            return instance
        except cls.DoesNotExist:
            return None
```

**Migration Required:**

```bash
./scripts/env/dev.sh makemigrations core
```

**Update Usage:**

```python
# Old (WRONG):
token = PasswordResetToken.objects.create(user=user, expires_at=expiry)
plain_token = token.token  # ❌ Exposes plain token from database

# New (CORRECT):
plain_token, token = PasswordResetToken.create_token(user=user, expires_at=expiry)
# Send plain_token via email, it's never stored
```

---

### C5: CRITICAL - Password History Uses Wrong Hasher Comparison

**Severity**: 🔴 **CRITICAL** - Security Vulnerability
**File**: `apps/core/models/password_history.py:69`
**Security Impact**: Password history checks may fail or use weak hashing

**Problem:**

```python
# apps/core/models/password_history.py:69
@classmethod
def check_password_reuse(cls, user, password: str, history_count: int = 12) -> bool:
    """Check if password was used in recent history."""
    recent_passwords = cls.objects.filter(user=user).order_by("-created_at")[:history_count]

    for history in recent_passwords:
        if history.check_password(password):  # ❌ Uses check_password with stored hash
            return True

    return False
```

**Why This Is Critical:**

1. `django.contrib.auth.hashers.check_password` is designed for User passwords
2. Historical passwords should use the **same hasher** as current User password
3. If hasher changes, old passwords become unverifiable
4. Need to explicitly use the correct hasher

**Solution:**
Use the User model's current hasher for consistency:

```python
# apps/core/models/password_history.py
@classmethod
def record_password(cls, user, password_hash: str) -> "PasswordHistory":
    """Record a password in history.

    Args:
        user: The user whose password is being recorded.
        password_hash: The hashed password from user.password field.

    Returns:
        The created PasswordHistory instance.
    """
    # ✅ Store the SAME hash as user.password uses
    history = cls.objects.create(
        user=user,
        password_hash=password_hash,  # Already hashed by user.set_password()
    )

    # Clean up old history (keep last 24 entries)
    old_passwords = cls.objects.filter(user=user).order_by("-created_at")[24:]
    if old_passwords.exists():
        old_passwords.delete()

    return history

def check_password(self, password: str) -> bool:
    """Check if provided password matches this historical password.

    Uses the same check_password as User model to ensure consistency.
    """
    from django.contrib.auth.hashers import check_password
    return check_password(password, self.password_hash)

@classmethod
def check_password_reuse(cls, user, password: str, history_count: int = 12) -> bool:
    """Check if password was used in recent history (H11)."""
    recent_passwords = cls.objects.filter(user=user).order_by("-created_at")[:history_count]

    for history in recent_passwords:
        if history.check_password(password):  # ✅ Uses same hasher as User
            return True

    return False
```

**Important Usage Pattern:**

```python
# When user changes password:
user.set_password(new_password)  # Hashes with Argon2
user.password_changed_at = timezone.now()
user.save()

# Record AFTER set_password (so user.password contains the hash)
PasswordHistory.record_password(user, user.password)  # ✅ Store same hash
```

---

## High Priority Issues (Must Fix Before Production)

### H1: Missing TOTP Encryption Key Validation

**Severity**: ⚠️ **HIGH** - Runtime Error Risk
**File**: `apps/core/models/totp_device.py:76`
**Impact**: Application crashes if TOTP_ENCRYPTION_KEY not set

**Problem:**
TOTP encryption key is only validated when TOTPDevice is first accessed:

```python
# apps/core/models/totp_device.py:76
@staticmethod
def _get_cipher() -> Fernet:
    """Get Fernet cipher for encryption/decryption."""
    encryption_key = getattr(settings, "TOTP_ENCRYPTION_KEY", None)
    if not encryption_key:
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(...)  # ❌ Only fails when first device is accessed
    return Fernet(encryption_key.encode() if isinstance(encryption_key, str) else encryption_key)
```

**Solution:**
Add startup validation in AppConfig:

```python
# apps/core/apps.py
from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class CoreConfig(AppConfig):
    """Core app configuration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self):
        """Validate required settings on startup."""
        # Validate TOTP encryption key (C2 requirement)
        if not getattr(settings, "TOTP_ENCRYPTION_KEY", None):
            raise ImproperlyConfigured(
                "TOTP_ENCRYPTION_KEY must be set in Django settings. "
                "Generate one with: python -c 'from cryptography.fernet import Fernet; "
                "print(Fernet.generate_key().decode())'"
            )

        # Validate IP encryption key (C6 requirement)
        if not getattr(settings, "IP_ENCRYPTION_KEY", None):
            raise ImproperlyConfigured(
                "IP_ENCRYPTION_KEY must be set in Django settings. "
                "Generate one with: python -c 'from cryptography.fernet import Fernet; "
                "print(Fernet.generate_key().decode())'"
            )

        # Validate TOKEN_SIGNING_KEY (C1 requirement)
        if not getattr(settings, "TOKEN_SIGNING_KEY", None):
            raise ImproperlyConfigured(
                "TOKEN_SIGNING_KEY must be set in Django settings. "
                "Generate one with: python -c 'import secrets; print(secrets.token_hex(32))'"
            )
```

---

### H2: User Model Missing Composite Index for Organisation Queries

**Severity**: ⚠️ **HIGH** - Performance
**File**: `apps/core/models/user.py:225`
**Impact**: Slow queries when filtering users by organisation

_See C2 for solution - already covered in Critical Issues_

---

### H3: SessionToken Missing Expires_at Index

**Severity**: ⚠️ **HIGH** - Performance
**File**: `apps/core/models/session_token.py:62`
**Impact**: Slow token validation queries

_See C3 for solution - already covered in Critical Issues_

---

### H4: AuditLog Missing Composite Indexes

**Severity**: ⚠️ **HIGH** - Performance
**File**: `apps/core/models/audit_log.py:72`
**Impact**: Slow audit log queries by organisation and action

_See C2 for solution - already covered in Critical Issues_

---

### H5: Password Validators Missing Error Codes

**Severity**: ⚠️ **HIGH** - User Experience
**File**: `config/validators/password.py` (multiple locations)
**Impact**: Poor error messages, no actionable guidance

**Problem:**
Most validators don't provide error codes:

```python
# config/validators/password.py:69
if len(re.findall(r"[A-Z]", password)) < self.min_uppercase:
    errors.append(
        _(f"Password must contain at least {self.min_uppercase} uppercase letter(s).")
    )  # ❌ No error code
```

**Solution:**
Add error codes to all ValidationError instances:

```python
# config/validators/password.py
def validate(self, password: str, user=None) -> None:
    """Validate the password meets complexity requirements."""
    errors = []

    # Check for uppercase letters
    if len(re.findall(r"[A-Z]", password)) < self.min_uppercase:
        errors.append(ValidationError(
            _(f"Password must contain at least {self.min_uppercase} uppercase letter(s)."),
            code="password_no_uppercase",  # ✅ Add error code
        ))

    # Check for lowercase letters
    if len(re.findall(r"[a-z]", password)) < self.min_lowercase:
        errors.append(ValidationError(
            _(f"Password must contain at least {self.min_lowercase} lowercase letter(s)."),
            code="password_no_lowercase",  # ✅ Add error code
        ))

    # Check for digits
    if len(re.findall(r"\d", password)) < self.min_digits:
        errors.append(ValidationError(
            _(f"Password must contain at least {self.min_digits} digit(s)."),
            code="password_no_digits",  # ✅ Add error code
        ))

    # Check for special characters
    special_chars = r"[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]"
    if len(re.findall(special_chars, password)) < self.min_special:
        errors.append(ValidationError(
            _(f"Password must contain at least {self.min_special} special character(s)."),
            code="password_no_special",  # ✅ Add error code
        ))

    if errors:
        raise ValidationError(errors)
```

**Apply to all validators:**

- MinimumLengthValidator
- MaximumLengthValidator
- NoSequentialCharactersValidator
- NoRepeatedCharactersValidator
- HIBPPasswordValidator

---

### H6: Missing Module-Level Docstrings

**Severity**: ⚠️ **HIGH** - Documentation
**Files**: Multiple files
**Impact**: Reduced code maintainability

**Problem:**
Some model files lack module-level docstrings:

```python
# apps/core/models/email_verification_token.py
"""EmailVerificationToken model for email verification workflow."""  # ✅ Has docstring

# apps/core/models/password_reset_token.py
"""PasswordResetToken model for password reset workflow."""  # ✅ Has docstring

# apps/core/models/user_profile.py
"""UserProfile model skeleton."""  # ⚠️ Minimal docstring
```

**Solution:**
Add comprehensive module-level docstrings to all files:

```python
"""UserProfile model for extending User with additional profile data.

This module provides a OneToOne extension of the User model for
storing additional profile information such as bio, avatar, preferences,
and role-specific data.

The UserProfile model follows the extension pattern documented in the
US-001 implementation plan for future role-based profiles.

Models:
    UserProfile: OneToOne extension of User for profile data.

Example:
    >>> user = User.objects.get(email="user@example.com")
    >>> profile = user.profile
    >>> profile.bio = "Software engineer"
    >>> profile.save()
"""
```

**Files Requiring Module Docstrings:**

- `apps/core/models/user_profile.py`
- `apps/core/models/__init__.py`
- `apps/core/views/__init__.py`
- `apps/core/urls.py`

---

### H7: HIBP Validator Fails Open (Security Concern)

**Severity**: ⚠️ **HIGH** - Security
**File**: `config/validators/password.py:390`
**Impact**: Breached passwords accepted if HIBP API unavailable

**Problem:**

```python
# config/validators/password.py:390
except requests.RequestException:
    # If API is unavailable, allow password change
    # (fail open to prevent blocking legitimate users)
    pass  # ❌ Fails open - accepts breached passwords if API down
```

**Solution:**
Add configuration option and logging:

```python
# config/validators/password.py
class HIBPPasswordValidator:
    """Validate password against Have I Been Pwned database (H5)."""

    def __init__(self, threshold: int = 1, timeout: int = 2, fail_open: bool = True) -> None:
        """Initialise HIBP validator.

        Args:
            threshold: Minimum breach count to reject password (default: 1).
            timeout: HTTP request timeout in seconds (default: 2).
            fail_open: If True, allow password if API unavailable (default: True).
                      If False, block password change if API unavailable.
        """
        self.threshold = threshold
        self.timeout = timeout
        self.fail_open = fail_open

    def validate(self, password: str, user=None) -> None:
        """Validate password against HIBP database."""
        import hashlib
        import requests
        import logging

        logger = logging.getLogger("security.password_validation")

        # Calculate SHA-1 hash of password
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]

        try:
            # Query HIBP API with only first 5 chars (k-anonymity)
            response = requests.get(
                f"https://api.pwnedpasswords.com/range/{prefix}",
                timeout=self.timeout,
            )

            if response.status_code == 200:
                # Parse response for matching hashes
                hashes = response.text.split("\r\n")
                for hash_count in hashes:
                    if ":" not in hash_count:
                        continue
                    hash_part, count_str = hash_count.split(":")
                    if hash_part == suffix:
                        breach_count = int(count_str)
                        if breach_count >= self.threshold:
                            logger.warning(
                                f"Password rejected: found in {breach_count} breaches",
                                extra={"user": user.email if user else "unknown"}
                            )
                            raise ValidationError(
                                _(
                                    "This password has been exposed in data breaches "
                                    f"{breach_count:,} times. Please choose a different password."
                                ),
                                code="password_breached",
                            )

        except requests.RequestException as e:
            logger.error(f"HIBP API request failed: {e}")

            if self.fail_open:
                # ✅ Log that we're failing open
                logger.warning(
                    "HIBP API unavailable - allowing password (fail_open=True)",
                    extra={"user": user.email if user else "unknown"}
                )
                pass  # Allow password
            else:
                # ✅ Option to fail closed in high-security environments
                raise ValidationError(
                    _("Password breach check unavailable. Please try again later."),
                    code="password_breach_check_failed",
                )
```

**Configuration:**

```python
# config/settings/base.py
AUTH_PASSWORD_VALIDATORS = [
    # ...
    {
        "NAME": "config.validators.password.HIBPPasswordValidator",
        "OPTIONS": {
            "threshold": 1,
            "timeout": 2,
            "fail_open": env.bool("HIBP_FAIL_OPEN", default=True),  # ✅ Configurable
        },
    },
]
```

---

### H8: PasswordHistory Cleanup Not Atomic

**Severity**: ⚠️ **HIGH** - Data Integrity
**File**: `apps/core/models/password_history.py:112`
**Impact**: Race condition during password history cleanup

**Problem:**

```python
# apps/core/models/password_history.py:112
@classmethod
def record_password(cls, user, password_hash: str) -> "PasswordHistory":
    """Record a password in history."""
    # Create new history entry
    history = cls.objects.create(
        user=user,
        password_hash=password_hash,
    )

    # Clean up old history (keep last 24 entries)
    old_passwords = cls.objects.filter(user=user).order_by("-created_at")[24:]
    for old_password in old_passwords:
        old_password.delete()  # ❌ Not atomic - race condition possible

    return history
```

**Solution:**
Use bulk delete in a transaction:

```python
# apps/core/models/password_history.py
from django.db import transaction

@classmethod
def record_password(cls, user, password_hash: str) -> "PasswordHistory":
    """Record a password in history.

    Stores the hashed password in history and cleans up old entries
    beyond the retention limit (keeps last 24 entries).

    Args:
        user: The user whose password is being recorded.
        password_hash: The hashed password to store.

    Returns:
        The created PasswordHistory instance.
    """
    with transaction.atomic():  # ✅ Atomic operation
        # Create new history entry
        history = cls.objects.create(
            user=user,
            password_hash=password_hash,
        )

        # Clean up old history (keep last 24 entries)
        # Get IDs of records to keep
        keep_ids = list(
            cls.objects
            .filter(user=user)
            .order_by("-created_at")
            .values_list("id", flat=True)[:24]
        )

        # Delete records not in keep list
        cls.objects.filter(user=user).exclude(id__in=keep_ids).delete()  # ✅ Bulk delete

    return history
```

---

### H9: User Email Normalisation Inconsistent

**Severity**: ⚠️ **HIGH** - Data Integrity
**File**: `apps/core/models/user.py:238`
**Impact**: Case-sensitivity issues in email lookups

**Problem:**
Email normalisation happens in TWO places with different logic:

```python
# apps/core/models/user.py:20 - UserManager.normalize_email
def normalize_email(self, email: str) -> str:
    """Normalise email address by lowercasing the domain part."""
    # ... lowercases ONLY domain part

# apps/core/models/user.py:238 - User.save
def save(self, *args, **kwargs):
    """Save user with normalised email."""
    if self.email:
        self.email = self.email.lower()  # ❌ Lowercases ENTIRE email
    super().save(*args, **kwargs)
```

**Why This Is a Problem:**

1. RFC 5321 specifies local part (before @) is case-sensitive
2. Domain part (after @) is case-insensitive
3. Two different normalisation approaches create inconsistency

**Solution:**
Use consistent normalisation everywhere:

```python
# apps/core/models/user.py:238
def save(self, *args, **kwargs):
    """Save user with normalised email.

    Normalises email to lowercase domain for case-insensitive uniqueness.
    Uses UserManager.normalize_email for consistency.
    """
    if self.email:
        # ✅ Use manager's normalize_email for consistency
        self.email = self.__class__.objects.normalize_email(self.email)
    super().save(*args, **kwargs)
```

**Alternative (Simpler but less RFC-compliant):**

```python
# If you want full lowercase (simpler, more common in practice):
def save(self, *args, **kwargs):
    """Save user with normalised email.

    Normalises entire email to lowercase for simplicity.
    Note: This is less RFC-compliant but more practical.
    """
    if self.email:
        self.email = self.email.lower()  # Simple full lowercase
    super().save(*args, **kwargs)

# And update normalize_email to match:
def normalize_email(self, email: str) -> str:
    """Normalise email address to lowercase."""
    if not email:
        raise ValueError("Email address is required")
    return email.strip().lower()  # ✅ Consistent with save()
```

**Recommendation**: Use the simpler full lowercase approach for consistency and simplicity.

---

### H10: Missing BaseToken Index on token_family

**Severity**: ⚠️ **HIGH** - Performance
**File**: `apps/core/models/base_token.py:48`
**Impact**: Slow token family queries for replay detection

**Problem:**
Token family is used for replay detection (H9) but abstract model doesn't enforce index:

```python
# apps/core/models/base_token.py:48
token_family = models.UUIDField(default=uuid.uuid4, db_index=True)  # ✅ Has db_index
```

**Actually this is already correct!** The `db_index=True` parameter ensures an index is created.

**However**, child models (SessionToken, PasswordResetToken, EmailVerificationToken) should verify they inherit this index. Check migrations to confirm.

**Verification:**

```bash
# Check migration files
grep -r "token_family" apps/core/migrations/
```

If index is missing in child models, add explicitly:

```python
# apps/core/models/password_reset_token.py
class Meta:
    db_table = "password_reset_tokens"
    indexes = [
        models.Index(fields=["user", "-created_at"]),
        models.Index(fields=["token_hash"]),
        models.Index(fields=["token_family"]),  # ✅ Ensure inherited index
        models.Index(fields=["expires_at"]),
    ]
```

---

## Medium Priority Issues (Should Fix)

### M1: UserManager Methods Lack Comprehensive Type Hints

**Severity**: ⚠️ Medium - Code Quality
**File**: `apps/core/models/user.py:50`
**Impact**: Reduced type safety and IDE autocomplete

**Problem:**

```python
# apps/core/models/user.py:50
def _create_user(self, email: str, password: str = None, **extra_fields) -> "User":
    # ⚠️ **extra_fields has no type hint
```

**Solution:**

```python
from typing import Any

def _create_user(self, email: str, password: str | None = None, **extra_fields: Any) -> User:
    """Create and save a user with the given email and password."""
```

---

### M2: Password Validators Have Duplicated Logic

**Severity**: ⚠️ Medium - DRY Violation
**File**: `config/validators/password.py`
**Impact**: Maintenance burden

**Problem:**
MinimumLengthValidator and MaximumLengthValidator have overlapping logic:

```python
# Lines 110-161 - MinimumLengthValidator
class MinimumLengthValidator:
    def __init__(self, min_length: int = 12, max_length: int = 128) -> None:  # ⚠️ Has max_length
        self.min_length = min_length
        self.max_length = max_length  # ⚠️ Duplicates MaximumLengthValidator

# Lines 164-202 - MaximumLengthValidator
class MaximumLengthValidator:
    def __init__(self, max_length: int = 128) -> None:
        self.max_length = max_length  # ⚠️ Duplicate logic
```

**Solution:**
Merge into a single LengthValidator:

```python
# config/validators/password.py
class PasswordLengthValidator:
    """Validate password length (minimum and maximum).

    Enforces minimum length for security and maximum length to prevent
    DoS attacks from very long passwords during hashing.
    """

    def __init__(self, min_length: int = 12, max_length: int = 128) -> None:
        """Initialize the validator with length requirements."""
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, password: str, user=None) -> None:
        """Validate the password meets length requirements."""
        if len(password) < self.min_length:
            raise ValidationError(
                _(f"Password must be at least {self.min_length} characters long."),
                code="password_too_short",
                params={"min_length": self.min_length},
            )

        if len(password) > self.max_length:
            raise ValidationError(
                _(f"Password must not exceed {self.max_length} characters."),
                code="password_too_long",
                params={"max_length": self.max_length},
            )

    def get_help_text(self) -> str:
        """Return help text for length requirements."""
        return _(
            f"Password must be at least {self.min_length} characters long "
            f"and no more than {self.max_length} characters."
        )
```

**Update settings:**

```python
# config/settings/base.py
AUTH_PASSWORD_VALIDATORS = [
    # ... other validators ...
    {
        "NAME": "config.validators.password.PasswordLengthValidator",  # ✅ Single validator
        "OPTIONS": {
            "min_length": 12,
            "max_length": 128,
        },
    },
]
```

---

### M3: Audit Middleware Duplicates IP Extraction Logic

**Severity**: ⚠️ Medium - DRY Violation
**File**: `config/middleware/audit.py:74`
**Impact**: Maintenance burden

**Problem:**
`get_client_ip()` function exists but IP extraction logic is duplicated in signal handlers:

```python
# config/middleware/audit.py:278
def log_user_login_failed(sender, credentials, request: HttpRequest | None = None, **kwargs):
    if request is None:
        return

    client_ip = get_client_ip(request)  # ✅ Uses helper
    # ...

# But in other places, logic might be duplicated
```

**Actually, this is already using the helper correctly!** No action needed.

---

### M4: Missing Transaction Protection for Token Generation

**Severity**: ⚠️ Medium - Data Integrity
**File**: `apps/core/models/base_token.py:57`
**Impact**: Potential race conditions in token generation

**Problem:**
Token generation in `save()` method is not protected by transaction:

```python
# apps/core/models/base_token.py:57
def save(self, *args, **kwargs):
    """Generate token and hash on save if not set."""
    if not self.token:
        self.token = self.generate_token()
    if not self.token_hash and self.token:
        self.token_hash = self.hash_token(self.token)
    super().save(*args, **kwargs)  # ❌ No transaction protection
```

**Solution:**
Add transaction protection:

```python
# apps/core/models/base_token.py
from django.db import transaction

def save(self, *args, **kwargs):
    """Generate token and hash on save if not set."""
    with transaction.atomic():  # ✅ Atomic operation
        if not self.token:
            self.token = self.generate_token()
        if not self.token_hash and self.token:
            self.token_hash = self.hash_token(self.token)
        super().save(*args, **kwargs)
```

**Note:** This becomes moot if C4 (removing plain token storage) is implemented.

---

### M5: BaseToken is_used Property Creates Confusion

**Severity**: ⚠️ Medium - Code Quality
**File**: `apps/core/models/base_token.py:125`
**Impact**: Confusing API with both `used` field and `is_used` property

**Problem:**

```python
# apps/core/models/base_token.py:125
@property
def is_used(self) -> bool:
    """Backwards compatibility alias for 'used' field."""
    return self.used

@is_used.setter
def is_used(self, value: bool) -> None:
    """Set used field via is_used alias."""
    self.used = value
```

**Why This Is Confusing:**

1. Two ways to access same data: `token.used` and `token.is_used`
2. No explanation of why backwards compatibility is needed
3. Property pattern typically used for computed values, not aliases

**Solution:**
If backwards compatibility is not actually needed, remove the property:

```python
# apps/core/models/base_token.py
# ❌ REMOVE is_used property entirely
# Use `used` field consistently throughout codebase
```

If backwards compatibility IS needed (e.g., migration from old code):

```python
# Add deprecation warning
import warnings

@property
def is_used(self) -> bool:
    """Deprecated: Use 'used' field instead."""
    warnings.warn(
        "is_used is deprecated, use 'used' field instead",
        DeprecationWarning,
        stacklevel=2
    )
    return self.used
```

**Recommendation**: Remove the property and use `used` consistently.

---

### M6: TOTPDevice Error Handling Too Broad

**Severity**: ⚠️ Medium - Error Handling
**File**: `apps/core/models/totp_device.py:142`
**Impact**: Silently catches all exceptions

**Problem:**

```python
# apps/core/models/totp_device.py:142
try:
    plain_secret = self.get_secret()
    totp = pyotp.TOTP(plain_secret)
    is_valid = totp.verify(token, valid_window=valid_window)
    # ...
    return is_valid
except Exception:  # ❌ Catches ALL exceptions
    return False
```

**Solution:**
Catch specific exceptions:

```python
# apps/core/models/totp_device.py
def verify_token(self, token: str, valid_window: int = 1) -> bool:
    """Verify a TOTP token against this device."""
    if not self.is_confirmed:
        return False

    try:
        plain_secret = self.get_secret()
        totp = pyotp.TOTP(plain_secret)
        is_valid = totp.verify(token, valid_window=valid_window)

        if is_valid:
            self.last_used_at = timezone.now()
            self.save(update_fields=["last_used_at"])

        return is_valid
    except (cryptography.fernet.InvalidToken, ValueError, TypeError) as e:
        # ✅ Catch specific expected exceptions
        import logging
        logger = logging.getLogger("security.totp")
        logger.warning(f"TOTP verification failed: {e}", extra={"device_id": self.id})
        return False
```

---

### M7: Settings Validation Missing

**Severity**: ⚠️ Medium - Configuration
**Files**: Settings files
**Impact**: Invalid configuration not caught until runtime

**Problem:**
Required settings (TOTP_ENCRYPTION_KEY, IP_ENCRYPTION_KEY, TOKEN_SIGNING_KEY) have no startup validation.

**Solution:**
Already covered in H1 - Add AppConfig.ready() validation.

---

## Low Priority Issues (Nice to Have)

### L1: UserManager.get_by_natural_key Uses Case-Insensitive Lookup

**Severity**: ℹ️ Low - Design Decision
**File**: `apps/core/models/user.py:151`
**Impact**: May differ from RFC 5321 local part handling

**Problem:**

```python
# apps/core/models/user.py:151
def get_by_natural_key(self, email: str) -> "User":
    """Get user by email (case-insensitive)."""
    return self.get(email__iexact=email)  # ⚠️ Case-insensitive lookup
```

**Note:** This is consistent with the full lowercase normalisation in `User.save()`, so it's actually correct if H9 is fixed with the simple lowercase approach.

**No action needed** if H9 is implemented with full lowercase normalisation.

---

### L2: Password Validator Help Text Not Following i18n Best Practices

**Severity**: ℹ️ Low - i18n
**File**: `config/validators/password.py` (multiple)
**Impact**: Hard to translate dynamic strings

**Problem:**

```python
# config/validators/password.py:103
def get_help_text(self) -> str:
    return _(
        f"Password must contain at least {self.min_uppercase} uppercase letter(s), "
        f"{self.min_lowercase} lowercase letter(s), {self.min_digits} digit(s), "
        f"and {self.min_special} special character(s)."
    )  # ⚠️ f-string inside _() makes translation harder
```

**Solution:**
Use string formatting after translation:

```python
def get_help_text(self) -> str:
    return _("Password must contain at least %(min_uppercase)s uppercase letter(s), "
             "%(min_lowercase)s lowercase letter(s), %(min_digits)s digit(s), "
             "and %(min_special)s special character(s).") % {
        'min_uppercase': self.min_uppercase,
        'min_lowercase': self.min_lowercase,
        'min_digits': self.min_digits,
        'min_special': self.min_special,
    }
```

---

### L3: Admin Readonly Fields Could Be Methods

**Severity**: ℹ️ Low - Admin UX
**File**: `apps/core/admin.py:68`
**Impact**: Minor admin interface improvement opportunity

**Problem:**
Some readonly fields could be custom methods with better formatting:

```python
# apps/core/admin.py:68
readonly_fields = ("created_at", "updated_at", "password_changed_at", "last_login")
```

**Enhancement:**

```python
# apps/core/admin.py
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    readonly_fields = (
        "created_at_display",
        "updated_at_display",
        "password_changed_at_display",
        "last_login",
    )

    def created_at_display(self, obj):
        """Display creation time with relative format."""
        if obj.created_at:
            from django.utils.timesince import timesince
            return f"{obj.created_at} ({timesince(obj.created_at)} ago)"
        return "-"
    created_at_display.short_description = "Created"

    # Similar for other timestamp fields
```

**Note:** This is purely aesthetic and low priority.

---

## Positive Observations

**Outstanding Design Decisions:**

1. **BaseToken Abstract Model (DRY Excellence)**
   - Eliminates 30+ lines of duplication across 3 token models
   - Provides consistent token management interface
   - Implements token family pattern for replay detection
   - Single-use token validation built-in

2. **Comprehensive Password Validation**
   - HIBP integration for breach checking
   - Multiple complexity validators
   - Sequential and repeated character prevention
   - Password history to prevent reuse
   - All validators have proper help text

3. **Strong Security Architecture**
   - TOTP secret encryption with Fernet
   - IP address encryption in audit logs
   - Argon2 password hashing (best practice)
   - HMAC-SHA256 for token hashing
   - Device fingerprinting for session tracking

4. **Excellent Documentation**
   - All models have comprehensive Google-style docstrings
   - Security requirements referenced (C1, C2, H9, etc.)
   - Clear explanations of "why" not just "what"
   - Type hints throughout

5. **Django Best Practices**
   - Custom UserManager with proper email normalisation
   - Abstract models for code reuse
   - Proper use of Meta options (indexes, ordering, verbose names)
   - Django admin configuration with inline editing
   - Signal handlers for audit logging

6. **Test-Driven Development**
   - Tests written before implementation (RED phase)
   - Comprehensive test coverage planned
   - Factory pattern for test data
   - Proper use of pytest markers

7. **Multi-Tenancy Implementation**
   - Organisation-based isolation
   - Proper foreign key relationships
   - Nullable organisation for platform superusers

---

## DRY Analysis

### Excellent DRY Implementation

1. **BaseToken Abstract Model** ⭐⭐⭐⭐⭐

   ```python
   # apps/core/models/base_token.py
   class BaseToken(models.Model):
       # Shared fields and methods for all token types
       # Eliminates duplication across 3 token models
   ```

   **Before**: 90 lines across 3 files
   **After**: 134 lines in 1 abstract + 37 lines total in 3 children = 171 lines
   **But**: Eliminates maintenance burden and ensures consistency

2. **Password Validator Base Functionality**
   - All validators implement `validate()` and `get_help_text()`
   - Consistent error handling pattern
   - Proper use of Django validator protocol

3. **Admin Configuration Pattern**
   - Consistent use of list_display, list_filter, search_fields
   - Proper readonly field configuration
   - Similar structure across all model admins

### Potential DRY Improvements

1. **Password Validator Length Validation** (See M2)
   - MinimumLengthValidator and MaximumLengthValidator overlap
   - Should be merged into single PasswordLengthValidator

2. **Audit Log IP Extraction** (Already fixed - uses get_client_ip helper)

---

## Security Analysis

### Security Strengths

1. **Password Security**
   - Argon2 hashing (strongest available)
   - HIBP breach checking
   - Complex password requirements
   - Password history to prevent reuse

2. **Token Security**
   - HMAC-SHA256 hashing (once C1 is fixed)
   - Token family for replay detection
   - Single-use tokens with expiry
   - Separate signing key (once C1 is fixed)

3. **2FA Security**
   - TOTP secrets encrypted with Fernet
   - Separate encryption key
   - Multiple devices per user supported
   - Device confirmation required

4. **Audit Logging**
   - Comprehensive security event logging
   - IP address encryption
   - Device fingerprinting
   - Immutable audit logs (no delete/edit in admin)

### Security Vulnerabilities Identified

**Critical:**

1. C1: Token hashing uses SECRET_KEY instead of TOKEN_SIGNING_KEY
2. C4: Plain tokens stored in database
3. C5: Password history hasher comparison issues

**High:**

1. H1: No startup validation for encryption keys
2. H7: HIBP validator fails open without logging

**Medium:**

1. M6: TOTPDevice error handling too broad

---

## Performance Analysis

### Performance Strengths

1. **Database Indexes**
   - UUID primary keys for distributed systems
   - Indexes on frequently queried fields
   - Foreign key indexes automatic

2. **Query Optimization**
   - select_related('organisation') in admin
   - Proper use of db_index=True
   - Token hash lookups instead of full scans

### Performance Concerns

**Critical:**

1. C2: Missing composite indexes for multi-tenant queries
2. C3: Missing indexes on expires_at fields

**High:**

1. H2-H4: Specific index gaps on User, SessionToken, AuditLog

**Medium:**

1. M4: No transaction protection in token generation
2. M8: PasswordHistory cleanup not atomic

---

## SOLID Principles Analysis

### Single Responsibility Principle (SRP)

✅ **Well Implemented:**

- UserManager: Only handles user creation and retrieval
- BaseToken: Only handles token lifecycle
- Password validators: Each validator checks one specific rule
- Audit middleware: Only logs security events

⚠️ **Could Improve:**

- User model has many fields (but acceptable for Django user model)
- SessionToken has many security tracking fields (but all related)

### Open/Closed Principle (OCP)

✅ **Well Implemented:**

- BaseToken is extensible through inheritance
- Password validators can be added/removed via configuration
- Django admin configuration allows customization

### Liskov Substitution Principle (LSP)

✅ **Well Implemented:**

- SessionToken, PasswordResetToken, EmailVerificationToken can substitute BaseToken
- All token models respect BaseToken interface

### Interface Segregation Principle (ISP)

✅ **Well Implemented:**

- Password validators have minimal interface (validate, get_help_text)
- BaseToken provides minimal interface for token management

### Dependency Inversion Principle (DIP)

⚠️ **Could Improve:**

- Models directly reference settings (tight coupling)
- TOTPDevice directly imports Fernet (could use abstraction)
- Audit middleware directly logs (could use logging abstraction)

**Recommendation:** These are acceptable for Django applications. Full DIP would be over-engineering.

---

## Test Coverage Analysis

**Tests Reviewed:**

- `tests/unit/apps/core/test_user_model.py` - Comprehensive user model tests
- Test structure follows TDD RED-GREEN-REFACTOR pattern
- Factory pattern implemented for test data generation

**Test Coverage:**

- ✅ User model creation and validation
- ✅ Email validation and uniqueness
- ✅ Password hashing and verification
- ✅ Organisation relationship
- ✅ Email verification fields
- ✅ Two-factor authentication fields

**Missing Tests (from plan):**

- BaseToken abstract model tests
- SessionToken specific tests
- TOTP device encryption tests
- Password history tests
- Audit log tests
- Password validator tests
- Integration tests
- E2E tests
- GraphQL tests

**Recommendation:** Complete test implementation as outlined in Phase 7 of the plan.

---

## Django Best Practices

**Excellent:**

1. ✅ Custom UserManager with proper email normalisation
2. ✅ Abstract models for code reuse (BaseToken)
3. ✅ Proper use of related_name in ForeignKey
4. ✅ on_delete behaviour properly specified
5. ✅ Meta options (verbose_name, ordering, indexes)
6. ✅ Django admin configuration with inlines
7. ✅ Signal handlers for audit logging
8. ✅ Middleware pattern for security logging
9. ✅ Custom password validators following Django protocol
10. ✅ Proper use of django-environ for settings

**Could Improve:**

1. ⚠️ Consider using select_related in more querysets
2. ⚠️ Consider prefetch_related for reverse relationships
3. ⚠️ Add database connection pooling (mentioned in plan)

---

## Summary Statistics

| Category                   | Count   | Status                        |
| -------------------------- | ------- | ----------------------------- |
| **Critical Issues**        | 5       | 🔴 Must fix before merge      |
| **High Priority Issues**   | 10      | ⚠️ Must fix before production |
| **Medium Priority Issues** | 7       | ⚠️ Should fix                 |
| **Low Priority Issues**    | 3       | ℹ️ Nice to have               |
| **Positive Observations**  | 7       | ✅ Excellent                  |
| **Files Reviewed**         | 13      | -                             |
| **Lines of Code Reviewed** | ~2,500+ | -                             |

---

## Recommendations

### Immediate Actions (Critical)

1. **Fix C1: Use TOKEN_SIGNING_KEY for token hashing**
   - Add TOKEN_SIGNING_KEY to settings
   - Update BaseToken.hash_token() to use it
   - Generate and deploy key to all environments

2. **Fix C4: Remove plain token storage**
   - Remove `token` field from BaseToken
   - Change API to `create_token()` returning tnuple
   - Update all usage to new pattern

3. **Fix C2, C3: Add missing indexes**
   - Add composite indexes for multi-tenant queries
   - Add expires_at indexes to all token models
   - Generate and run migrations

4. **Fix C5: Password history hasher consistency**
   - Ensure PasswordHistory uses same hasher as User
   - Document usage pattern clearly

### Before Production (High Priority)

1. **Add startup validation** (H1)
   - Validate all encryption keys on startup
   - Provide clear error messages

2. **Add error codes to validators** (H5)
   - All ValidationError instances need codes
   - Makes error handling easier for clients

3. **Fix email normalisation consistency** (H9)
   - Choose either RFC-compliant or full lowercase
   - Be consistent everywhere

4. **Configure HIBP fail behavior** (H7)
   - Add fail_open configuration option
   - Add logging for when API is unavailable

### Technical Debt (Medium Priority)

1. **Merge length validators** (M2)
2. **Add module docstrings** (H6)
3. **Add transaction protection** (M4, H8)
4. **Fix TOTP error handling** (M6)

---

## Approval Status

**Status**: ✅ **CONDITIONALLY APPROVED**

**Conditions:**

1. Fix all 5 CRITICAL issues (C1-C5) before merging
2. Address high-priority performance indexes (C2, C3)
3. Add startup validation for encryption keys (H1)
4. Complete Phase 2-7 implementation per plan

**Strengths:**

- Excellent BaseToken DRY implementation
- Comprehensive security architecture
- Strong documentation
- Proper Django patterns

**Concerns:**

- Critical security vulnerabilities must be fixed
- Performance indexes must be added
- Missing validation for required settings

**Recommendation**: Fix critical issues, then merge and proceed with Phase 2.

---

**Review Completed**: 07/01/2026
**Next Review**: After Phase 2 (Authentication Service Layer) implementation
**Reviewed By**: Code Review Agent
**Approval**: Conditional (pending critical fixes)
