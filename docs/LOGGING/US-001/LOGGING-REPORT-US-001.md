# Logging and Audit Implementation Report - US-001

**Date**: 08/01/2026
**Report Type**: Implementation Status Analysis
**User Story**: US-001 User Authentication
**Overall Status**: ✅ **PHASE 2 COMPLETE** - Service Layer Implemented
**Analyst**: Logging Infrastructure Specialist

---

## Table of Contents

- [Logging and Audit Implementation Report - US-001](#logging-and-audit-implementation-report---us-001)
  - [Table of Contents](#table-of-contents)
  - [Executive Summary](#executive-summary)
  - [1. Implementation Timeline](#1-implementation-timeline)
    - [1.1 Phase 1: Core Models and Database](#11-phase-1-core-models-and-database)
    - [1.2 Phase 2: Authentication Service Layer](#12-phase-2-authentication-service-layer)
    - [1.3 Upcoming Phases](#13-upcoming-phases)
  - [2. Current Logging Infrastructure](#2-current-logging-infrastructure)
    - [2.1 Django Logging Configuration](#21-django-logging-configuration)
    - [2.2 Sentry Integration](#22-sentry-integration)
    - [2.3 Log Files and Storage](#23-log-files-and-storage)
    - [2.4 SecurityAuditMiddleware](#24-securityauditmiddleware)
  - [3. Audit Logging Implementation](#3-audit-logging-implementation)
    - [3.1 AuditLog Model](#31-auditlog-model)
    - [3.2 AuditService](#32-auditservice)
    - [3.3 Audit Event Types](#33-audit-event-types)
  - [4. IP Encryption Implementation](#4-ip-encryption-implementation)
    - [4.1 IPEncryption Utility](#41-ipencryption-utility)
    - [4.2 Key Rotation Support](#42-key-rotation-support)
    - [4.3 Security Features](#43-security-features)
  - [5. Token Security Implementation](#5-token-security-implementation)
    - [5.1 TokenHasher Utility](#51-tokenhasher-utility)
    - [5.2 Hash-Then-Store Pattern](#52-hash-then-store-pattern)
    - [5.3 Security Features](#53-security-features)
  - [6. Service Layer Audit Integration](#6-service-layer-audit-integration)
    - [6.1 AuthService](#61-authservice)
    - [6.2 TokenService](#62-tokenservice)
    - [6.3 PasswordResetService](#63-passwordresetservice)
    - [6.4 EmailService](#64-emailservice)
  - [7. Sensitive Data Protection](#7-sensitive-data-protection)
    - [7.1 Data NEVER Logged](#71-data-never-logged)
    - [7.2 Data Encrypted Before Storage](#72-data-encrypted-before-storage)
    - [7.3 Data Logged Safely](#73-data-logged-safely)
  - [8. Security Events Tracked](#8-security-events-tracked)
    - [8.1 Authentication Events](#81-authentication-events)
    - [8.2 Token Management](#82-token-management)
    - [8.3 Password Management](#83-password-management)
  - [9. Logging Architecture](#9-logging-architecture)
    - [9.1 Database Audit Trail (Phase 2 - Implemented)](#91-database-audit-trail-phase-2---implemented)
    - [9.2 Application Logging (Phase 6 - Deferred)](#92-application-logging-phase-6---deferred)
    - [9.3 Environment-Specific Behaviour](#93-environment-specific-behaviour)
  - [10. Configuration Requirements](#10-configuration-requirements)
    - [10.1 Environment Variables](#101-environment-variables)
    - [10.2 Django Settings](#102-django-settings)
    - [10.3 Production Enforcement](#103-production-enforcement)
  - [11. Testing Status](#11-testing-status)
    - [11.1 Phase 1 Tests (Models)](#111-phase-1-tests-models)
    - [11.2 Phase 2 Tests (Services and Security)](#112-phase-2-tests-services-and-security)
    - [11.3 Missing Tests (Phase 7)](#113-missing-tests-phase-7)
  - [12. Gap Analysis](#12-gap-analysis)
    - [12.1 Implemented Features](#121-implemented-features)
    - [12.2 Deferred to Phase 3 (GraphQL)](#122-deferred-to-phase-3-graphql)
    - [12.3 Deferred to Phase 6 (Production Logging)](#123-deferred-to-phase-6-production-logging)
  - [13. Compliance and Security](#13-compliance-and-security)
    - [13.1 GDPR Compliance](#131-gdpr-compliance)
    - [13.2 Security Best Practices](#132-security-best-practices)
    - [13.3 Audit Log Retention](#133-audit-log-retention)
  - [14. Recommendations](#14-recommendations)
    - [14.1 Before Phase 3 (GraphQL)](#141-before-phase-3-graphql)
    - [14.2 Phase 3 Requirements](#142-phase-3-requirements)
    - [14.3 Phase 6 Requirements (Production)](#143-phase-6-requirements-production)
  - [15. Next Steps](#15-next-steps)
  - [16. References](#16-references)

---

## Executive Summary

**Overall Status**: US-001 Phases 1 and 2 are complete with comprehensive audit logging infrastructure.

**Phase 1 Achievement (Database Layer)**:

- ✅ `AuditLog` model with encrypted IP storage
- ✅ Composite indexes for multi-tenant queries
- ✅ `SecurityAuditMiddleware` for HTTP event logging
- ✅ Django Admin configuration for audit log viewing
- ✅ 30+ unit tests for `AuditLog` model

**Phase 2 Achievement (Service Layer)**:

- ✅ `AuditService` - Centralised audit logging with IP encryption
- ✅ `IPEncryption` - Fernet encryption with key rotation support
- ✅ `TokenHasher` - HMAC-SHA256 token hashing with hash-then-store pattern
- ✅ `AuthService` - Authentication with race condition prevention
- ✅ `TokenService` - Token management with replay detection
- ✅ `PasswordResetService` - Secure password reset flow
- ✅ Comprehensive unit tests for all utilities and services

**Security Compliance**:

- ✅ Passwords and tokens NEVER logged in plain text
- ✅ IP addresses encrypted before database storage (GDPR)
- ✅ HMAC-SHA256 token hashing prevents rainbow table attacks
- ✅ Hash-then-store pattern for all authentication tokens
- ✅ Constant-time comparison prevents timing attacks
- ✅ Key rotation support for IP encryption keys

**Deployment Readiness**:

- ✅ Phase 1 + 2: READY for Phase 3 (GraphQL integration)
- ⚠️ Requires environment variable configuration
- ⚠️ File-based logging deferred to Phase 6
- ⚠️ Audit log retention policy deferred to Phase 6

---

## 1. Implementation Timeline

### 1.1 Phase 1: Core Models and Database

**Status**: ✅ **COMPLETE**

**Implemented**:

- ✅ `AuditLog` model with UUID primary key
- ✅ Binary field for encrypted IP addresses
- ✅ Device fingerprint field
- ✅ JSON metadata field
- ✅ Composite indexes for multi-tenant queries
- ✅ `SecurityAuditMiddleware` for HTTP event logging
- ✅ Django Admin configuration (read-only)
- ✅ Unit tests (30+ test cases)

**Key Features**:

- Immutable audit trail (no updates/deletes)
- Organisation-scoped access
- Support for failed login attempts (nullable user field)
- SET_NULL on organisation delete (preserves audit history)

### 1.2 Phase 2: Authentication Service Layer

**Status**: ✅ **COMPLETE**

**Implemented**:

| Component              | Location                                       | Purpose                             |
| ---------------------- | ---------------------------------------------- | ----------------------------------- |
| `AuditService`         | `apps/core/services/audit_service.py`          | Centralised audit event logging     |
| `IPEncryption`         | `apps/core/utils/encryption.py`                | Fernet IP encryption + rotation     |
| `TokenHasher`          | `apps/core/utils/token_hasher.py`              | HMAC-SHA256 token hashing           |
| `AuthService`          | `apps/core/services/auth_service.py`           | Authentication logic                |
| `TokenService`         | `apps/core/services/token_service.py`          | Token management + replay detection |
| `PasswordResetService` | `apps/core/services/password_reset_service.py` | Password reset with hash-then-store |
| `EmailService`         | `apps/core/services/email_service.py`          | Email sending (stub)                |

**Security Fixes Implemented**:

| Issue | Description                    | Solution                          |
| ----- | ------------------------------ | --------------------------------- |
| C1    | HMAC-SHA256 token hashing      | `TokenHasher` utility             |
| C3    | Password reset hash-then-store | `PasswordResetService`            |
| C6    | IP encryption key rotation     | `IPEncryption.rotate_key()`       |
| H3    | Race condition prevention      | `select_for_update()` in services |
| H9    | Refresh token replay detection | Token families in `TokenService`  |
| M5    | Timezone/DST handling          | `pytz` integration                |

### 1.3 Upcoming Phases

**Phase 3** (GraphQL API):

- Integrate `AuditService` calls in GraphQL mutations
- Add GraphQL queries for viewing audit logs
- Implement device fingerprinting utility
- Add organisation boundary enforcement

**Phase 6** (Production Logging):

- File-based logging with rotation
- Audit log retention policy (90 days security, 30 days general)
- Request ID tracking
- Performance logging decorators
- Centralised log aggregation

**Phase 7** (Testing):

- Integration tests for audit logging flow
- BDD tests for security event scenarios
- End-to-end tests for complete audit trail

---

## 2. Current Logging Infrastructure

### 2.1 Django Logging Configuration

**Development Environment** (`config/settings/dev.py`):

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "security_console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
            "level": "INFO",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "security.audit": {
            "handlers": ["security_console"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
```

**Production Environment** (`config/settings/production.py`):

```python
LOGGING = {
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
        },
        "security_console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "level": "INFO",
        },
    },
    "loggers": {
        "security.audit": {
            "handlers": ["security_console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
```

**Status**:

- ✅ Console logging configured
- ✅ JSON formatter for production
- ✅ `security.audit` logger configured
- ❌ File handlers NOT configured (deferred to Phase 6)

### 2.2 Sentry Integration

**Configuration** (`config/settings/production.py`):

```python
SENTRY_DSN = env("SENTRY_DSN", default="")
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        environment="production",
        traces_sample_rate=0.1,
        send_default_pii=False,
    )
```

**Status**:

- ✅ Configured (optional - only if DSN provided)
- ✅ PII sending disabled by default
- ✅ Performance tracing configured (10% sample rate)

**Dependencies**:

- `sentry-sdk>=2.19.2` (production extras)

### 2.3 Log Files and Storage

**Current State**: ❌ **NOT IMPLEMENTED**

**Expected Structure** (Phase 6):

```
logs/
├── app.log          # General application logs
├── error.log        # Error logs
├── security.log     # Security audit logs
└── sql.log          # Database queries (dev only)
```

**Deferred to Phase 6**:

- File handlers with rotation
- Separate files by log level/concern
- Log rotation (10MB per file, 5 backups)

### 2.4 SecurityAuditMiddleware

**Location**: `config/middleware/audit.py`

**Status**: ✅ **IMPLEMENTED**

**Features**:

- Logs HTTP 403 (Forbidden) responses
- Logs HTTP 401 (Unauthorised) responses
- Logs CSRF validation failures
- Signal handlers for Django authentication:
  - `user_logged_in` → logs successful login
  - `user_logged_out` → logs logout
  - `user_login_failed` → logs failed login

**Current Behaviour**:

```
Authentication Event
    ↓
Django Signal
    ↓
SecurityAuditMiddleware
    ↓
Python Logger (security.audit)
    ↓
Console/Sentry (NOT database)
```

**Phase 3 Behaviour** (After GraphQL Integration):

```
GraphQL Mutation
    ↓
Service Method (AuthService, etc.)
    ↓
AuditService.log_event()
    ↓
IPEncryption.encrypt_ip()
    ↓
AuditLog Database Record
```

---

## 3. Audit Logging Implementation

### 3.1 AuditLog Model

**Location**: `apps/core/models/audit_log.py`

**Status**: ✅ **FULLY IMPLEMENTED**

**Schema**:

```python
class AuditLog(models.Model):
    """Audit log for tracking security-relevant user actions."""

    class ActionType(models.TextChoices):
        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        LOGIN_FAILED = "LOGIN_FAILED", "Login Failed"
        PASSWORD_CHANGE = "PASSWORD_CHANGE", "Password Change"
        PASSWORD_RESET = "PASSWORD_RESET", "Password Reset"
        EMAIL_VERIFIED = "EMAIL_VERIFIED", "Email Verified"
        TWO_FACTOR_ENABLED = "TWO_FACTOR_ENABLED", "Two Factor Enabled"
        TWO_FACTOR_DISABLED = "TWO_FACTOR_DISABLED", "Two Factor Disabled"
        ACCOUNT_LOCKED = "ACCOUNT_LOCKED", "Account Locked"
        ACCOUNT_UNLOCKED = "ACCOUNT_UNLOCKED", "Account Unlocked"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("core.User", on_delete=models.SET_NULL, null=True, blank=True)
    organisation = models.ForeignKey("core.Organisation", on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=50, choices=ActionType.choices)
    ip_address = models.BinaryField(null=True, blank=True)  # Encrypted with Fernet
    user_agent = models.TextField(blank=True, default="")
    device_fingerprint = models.CharField(max_length=64, blank=True, default="")
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Indexes**:

```python
indexes = [
    models.Index(fields=["user", "-created_at"]),
    models.Index(fields=["organisation", "-created_at"]),
    models.Index(fields=["action", "-created_at"]),
    models.Index(fields=["created_at"]),
]
```

**Security Features**:

- UUID primary key (security and distributed systems)
- Nullable `user` field (failed login attempts)
- `SET_NULL` on organisation delete (preserves audit history)
- Encrypted IP addresses (binary field for Fernet encryption)
- Device fingerprinting support
- JSON metadata for flexible event data

### 3.2 AuditService

**Location**: `apps/core/services/audit_service.py`

**Status**: ✅ **FULLY IMPLEMENTED**

**Core Method**:

```python
@staticmethod
def log_event(
    action: str,
    user: User | None = None,
    organisation: Organisation | None = None,
    ip_address: str = "",
    user_agent: str = "",
    device_fingerprint: str = "",
    metadata: dict | None = None,
) -> AuditLog:
    """Log a security event with encrypted IP address."""
    # Encrypt IP address if provided
    encrypted_ip = None
    if ip_address:
        encrypted_ip = IPEncryption.encrypt_ip(ip_address)

    # Create audit log
    return AuditLog.objects.create(
        action=action,
        user=user,
        organisation=organisation or (user.organisation if user else None),
        ip_address=encrypted_ip,
        user_agent=user_agent,
        device_fingerprint=device_fingerprint,
        metadata=metadata or {},
    )
```

**Convenience Methods**:

| Method                  | Event Type        | User Required | Example Usage                                |
| ----------------------- | ----------------- | ------------- | -------------------------------------------- |
| `log_login()`           | `LOGIN`           | Yes           | `AuditService.log_login(user, ip, device)`   |
| `log_login_failed()`    | `LOGIN_FAILED`    | No            | `AuditService.log_login_failed(email, ip)`   |
| `log_logout()`          | `LOGOUT`          | Yes           | `AuditService.log_logout(user, ip)`          |
| `log_password_change()` | `PASSWORD_CHANGE` | Yes           | `AuditService.log_password_change(user, ip)` |

**Query Methods**:

```python
# Get user's audit logs
logs = AuditService.get_user_logs(user, limit=100)

# Get organisation's audit logs
logs = AuditService.get_organisation_logs(organisation, limit=100)
```

### 3.3 Audit Event Types

**Implemented Actions**:

| Action Type           | When Triggered                     | Phase |
| --------------------- | ---------------------------------- | ----- |
| `LOGIN`               | Successful user login              | P3    |
| `LOGIN_FAILED`        | Failed login attempt               | P3    |
| `LOGOUT`              | User logout                        | P3    |
| `PASSWORD_CHANGE`     | User changes password              | P3    |
| `PASSWORD_RESET`      | User resets password via email     | P3    |
| `EMAIL_VERIFIED`      | User verifies email                | P3    |
| `TWO_FACTOR_ENABLED`  | User enables 2FA                   | P4    |
| `TWO_FACTOR_DISABLED` | User disables 2FA                  | P4    |
| `ACCOUNT_LOCKED`      | Account locked after failed logins | P6    |
| `ACCOUNT_UNLOCKED`    | Account unlocked by admin          | P6    |

---

## 4. IP Encryption Implementation

### 4.1 IPEncryption Utility

**Location**: `apps/core/utils/encryption.py`

**Status**: ✅ **FULLY IMPLEMENTED**

**Encryption Algorithm**: Fernet (AES-128-CBC with HMAC-SHA256 authentication)

**Encryption Method**:

```python
@staticmethod
def encrypt_ip(ip_address: str, key: bytes | None = None) -> bytes:
    """Encrypt an IP address using Fernet encryption.

    Args:
        ip_address: IP address string (IPv4 or IPv6)
        key: Optional encryption key (defaults to IP_ENCRYPTION_KEY)

    Returns:
        Encrypted IP address as bytes

    Raises:
        ValueError: If IP address is invalid or empty
    """
    if not ip_address:
        raise ValueError("IP address cannot be empty")

    if not IPEncryption.validate_ip_address(ip_address):
        raise ValueError(f"Invalid IP address: {ip_address}")

    if key is None:
        key = settings.IP_ENCRYPTION_KEY.encode()

    fernet = Fernet(key)
    encrypted = fernet.encrypt(ip_address.encode())
    return encrypted
```

**Decryption Method**:

```python
@staticmethod
def decrypt_ip(encrypted_ip: bytes, key: bytes | None = None) -> str:
    """Decrypt an encrypted IP address.

    Supports multi-key decryption for key rotation.
    """
    if key is None:
        key = settings.IP_ENCRYPTION_KEY.encode()

    fernet = Fernet(key)
    decrypted = fernet.decrypt(encrypted_ip)
    return decrypted.decode()
```

**Validation**:

```python
@staticmethod
def validate_ip_address(ip_address: str) -> bool:
    """Validate IPv4 or IPv6 address format."""
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False
```

### 4.2 Key Rotation Support

**Key Rotation Method**:

```python
@staticmethod
def rotate_key(old_key: bytes, new_key: bytes) -> dict:
    """Rotate encryption key and re-encrypt all IP addresses.

    Returns:
        Dictionary with statistics:
            {
                'audit_logs_updated': int,
                'session_tokens_updated': int,
                'errors': list,
            }
    """
    # Re-encrypts all IPs in:
    # - AuditLog.ip_address
    # - SessionToken.ip_address
```

**Key Generation**:

```python
@staticmethod
def generate_key() -> bytes:
    """Generate a new Fernet encryption key."""
    return Fernet.generate_key()
```

**Management Command** (Phase 2):

```bash
python manage.py rotate_ip_keys
```

### 4.3 Security Features

- ✅ **Fernet Encryption**: AES-128-CBC with HMAC-SHA256
- ✅ **IP Validation**: IPv4 and IPv6 support
- ✅ **Key Rotation**: Re-encrypts all historical IPs
- ✅ **Multi-Model Support**: `AuditLog` and `SessionToken`
- ✅ **Error Handling**: Returns error list for failed operations

---

## 5. Token Security Implementation

### 5.1 TokenHasher Utility

**Location**: `apps/core/utils/token_hasher.py`

**Status**: ✅ **FULLY IMPLEMENTED**

**Algorithm**: HMAC-SHA256 with dedicated `TOKEN_SIGNING_KEY`

**Why HMAC-SHA256 instead of plain SHA-256?**

- ❌ Plain SHA-256: Vulnerable to rainbow table attacks
- ✅ HMAC-SHA256: Requires secret key, prevents precomputation
- ✅ Dedicated Key: Uses `TOKEN_SIGNING_KEY`, not `SECRET_KEY`

**Hash Method**:

```python
@staticmethod
def hash_token(token: str, key: bytes | None = None) -> str:
    """Hash a token using HMAC-SHA256.

    Args:
        token: Plain token string to hash
        key: Optional signing key (defaults to TOKEN_SIGNING_KEY)

    Returns:
        Base64-encoded HMAC-SHA256 hash as string
    """
    if not token:
        raise ValueError("Token cannot be empty")

    if key is None:
        key = settings.TOKEN_SIGNING_KEY.encode()

    # Create HMAC-SHA256 hash
    token_bytes = token.encode("utf-8")
    hmac_hash = hmac.new(key, token_bytes, hashlib.sha256).digest()

    # Base64 encode for storage
    return base64.b64encode(hmac_hash).decode("utf-8")
```

**Verification Method**:

```python
@staticmethod
def verify_token(token: str, token_hash: str, key: bytes | None = None) -> bool:
    """Verify a token against its hash using constant-time comparison."""
    computed_hash = TokenHasher.hash_token(token, key)
    return TokenHasher.constant_time_compare(computed_hash, token_hash)
```

**Token Generation**:

```python
@staticmethod
def generate_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token.

    Default length provides 256 bits of entropy.

    Raises:
        ValueError: If length < 16 (insufficient entropy)
    """
    if length < 16:
        raise ValueError("Token length must be at least 16 bytes")

    return secrets.token_hex(length)
```

### 5.2 Hash-Then-Store Pattern

**Pattern**: Plain tokens are NEVER stored, only hashes.

**Flow**:

1. Generate cryptographically secure random token
2. Hash token with HMAC-SHA256
3. Store only hash in database
4. Return plain token to user (only once)
5. Verify by hashing and comparing

**Example** (Password Reset):

```python
# Create token
plain_token = TokenHasher.generate_token()
token_hash = TokenHasher.hash_token(plain_token)

# Store only hash
PasswordResetToken.objects.create(
    user=user,
    token_hash=token_hash,
    expires_at=timezone.now() + timedelta(hours=1)
)

# Return plain token (sent via email, never stored again)
return plain_token

# Later: Verify token
token_hash = TokenHasher.hash_token(user_provided_token)
reset_token = PasswordResetToken.objects.get(token_hash=token_hash)
```

### 5.3 Security Features

- ✅ **HMAC-SHA256**: Keyed hash with `TOKEN_SIGNING_KEY`
- ✅ **Constant-Time Comparison**: `hmac.compare_digest()` prevents timing attacks
- ✅ **Cryptographic Random**: `secrets.token_hex()` provides 256-bit entropy
- ✅ **Base64 Encoding**: Safe database storage
- ✅ **Minimum Entropy**: Enforces at least 128 bits

---

## 6. Service Layer Audit Integration

### 6.1 AuthService

**Location**: `apps/core/services/auth_service.py`

**Audit Integration Status**: ⚠️ **Prepared for Phase 3**

**Methods**:

- `register_user()` - Will log registration (Phase 3)
- `login()` - Will log successful/failed login (Phase 3)
- `logout()` - Will log logout (Phase 3)
- `change_password()` - Will log password change (Phase 3)

**Security Features**:

- Race condition prevention with `select_for_update()` (H3)
- Timezone-aware datetime handling with `pytz` (M5)
- Account lockout support (Phase 6)

**Sensitive Data Protection**:

```python
# ❌ NEVER logged:
# - password parameter
# - password hash

# ✅ Logged safely:
# - email (only in metadata for failed logins)
# - encrypted IP address
# - device fingerprint
```

### 6.2 TokenService

**Location**: `apps/core/services/token_service.py`

**Audit Integration Status**: ⚠️ **Prepared for Phase 3**

**Security Features**:

- Token family tracking for replay detection (H9)
- HMAC-SHA256 token hashing (C1)
- Hash-then-store pattern
- Automatic token revocation on password change

**Methods**:

- `create_tokens()` - Creates access + refresh token pair
- `verify_access_token()` - Verifies token and returns user
- `refresh_tokens()` - Rotates tokens with replay detection
- `revoke_token_family()` - Revokes all tokens in family (replay attack)
- `revoke_user_tokens()` - Revokes all user tokens (password change)

**Sensitive Data Protection**:

```python
# ❌ NEVER logged or stored:
# - Plain access tokens
# - Plain refresh tokens

# ✅ Stored safely:
# - Token hashes only (HMAC-SHA256)
# - Encrypted IP addresses
```

### 6.3 PasswordResetService

**Location**: `apps/core/services/password_reset_service.py`

**Audit Integration Status**: ⚠️ **Prepared for Phase 3**

**Security Features**:

- Hash-then-store pattern (C3)
- HMAC-SHA256 token hashing
- Single-use tokens
- 1-hour token expiry

**Methods**:

- `create_reset_token()` - Generates and stores hashed token
- `verify_reset_token()` - Verifies token and returns user
- `reset_password()` - Completes password reset
- `cleanup_expired_tokens()` - Maintenance task

**Sensitive Data Protection**:

```python
# ❌ NEVER logged or stored:
# - Plain password reset tokens
# - New passwords

# ✅ Stored safely:
# - Token hashes only (HMAC-SHA256)
# - User audit log entry (PASSWORD_RESET action)
```

### 6.4 EmailService

**Location**: `apps/core/services/email_service.py`

**Status**: Stub implementation (Phase 5)

**Methods** (all return `True` in Phase 2):

- `send_verification_email()`
- `send_password_reset_email()`
- `send_welcome_email()`
- `send_password_changed_notification()`
- `send_2fa_enabled_notification()`

**Sensitive Data Protection**:

```python
# ❌ NEVER logged:
# - Email content
# - Tokens sent in emails

# ✅ Future logging (Phase 5):
# - Email send success/failure events
```

---

## 7. Sensitive Data Protection

### 7.1 Data NEVER Logged

**Critical Security Requirement**: The following data is NEVER logged or stored in audit logs:

| Data Type            | Reason                  | Compliance   |
| -------------------- | ----------------------- | ------------ |
| Plain passwords      | Security best practice  | OWASP, PCI   |
| Plain session tokens | Prevents token theft    | OWASP        |
| Plain refresh tokens | Prevents replay attacks | OWASP        |
| Plain reset tokens   | Single-use security     | OWASP        |
| Hashed passwords     | No business need        | Minimisation |
| Credit card numbers  | PCI-DSS requirement     | PCI-DSS      |
| API keys             | Security best practice  | OWASP        |

**Code Example** (Password Reset):

```python
# ❌ WRONG - NEVER do this:
logger.info(f"Password reset token: {plain_token}")
logger.info(f"New password: {new_password}")

# ✅ CORRECT - Only log action:
AuditService.log_event(
    action=AuditLog.ActionType.PASSWORD_RESET,
    user=user,
    ip_address=encrypted_ip  # Encrypted, not plain
)
```

### 7.2 Data Encrypted Before Storage

| Data Type    | Encryption Method    | Storage Location          | Purpose          |
| ------------ | -------------------- | ------------------------- | ---------------- |
| IP addresses | Fernet (AES-128-CBC) | `AuditLog.ip_address`     | GDPR compliance  |
| IP addresses | Fernet (AES-128-CBC) | `SessionToken.ip_address` | Session tracking |

### 7.3 Data Logged Safely

| Data Type            | Storage Format | Location                      | Purpose               |
| -------------------- | -------------- | ----------------------------- | --------------------- |
| User ID              | Foreign key    | `AuditLog.user`               | User tracking         |
| Organisation ID      | Foreign key    | `AuditLog.organisation`       | Multi-tenancy         |
| Action type          | Enum string    | `AuditLog.action`             | Event classification  |
| User agent           | Plain text     | `AuditLog.user_agent`         | Device identification |
| Device fingerprint   | Hash           | `AuditLog.device_fingerprint` | Session tracking      |
| Email (failed login) | Plain text     | `AuditLog.metadata`           | Failed login tracking |
| Timestamp            | DateTime       | `AuditLog.created_at`         | Event chronology      |

---

## 8. Security Events Tracked

### 8.1 Authentication Events

| Event            | Action Type    | When Logged          | Data Captured               |
| ---------------- | -------------- | -------------------- | --------------------------- |
| Successful login | `LOGIN`        | User authenticates   | User, IP, device, UA        |
| Failed login     | `LOGIN_FAILED` | Wrong password/email | Email, IP, device (no user) |
| Logout           | `LOGOUT`       | User logs out        | User, IP                    |

**Example**:

```python
# Successful login
AuditService.log_login(
    user=user,
    ip_address="192.168.1.1",  # Encrypted before storage
    device_fingerprint="abc123def456",
    user_agent="Mozilla/5.0..."
)

# Failed login
AuditService.log_login_failed(
    email="attacker@example.com",
    ip_address="203.0.113.5",  # Encrypted before storage
    metadata={"reason": "invalid_password"}
)
```

### 8.2 Token Management

**Current Implementation**: Token operations logged indirectly through authentication events.

| Operation        | Logged As    | Rationale                             |
| ---------------- | ------------ | ------------------------------------- |
| Token creation   | `LOGIN`      | Part of login flow                    |
| Token revocation | `LOGOUT`     | Part of logout flow                   |
| Token refresh    | (Not logged) | Transparent operation (reduces noise) |
| Family revoked   | (Future)     | Replay attack detected (Phase 6)      |

### 8.3 Password Management

| Event           | Action Type       | When Logged              | Data Captured |
| --------------- | ----------------- | ------------------------ | ------------- |
| Password change | `PASSWORD_CHANGE` | User changes password    | User, IP      |
| Password reset  | `PASSWORD_RESET`  | Reset via email complete | User, IP      |

**Security Notes**:

- ❌ Old password never logged
- ❌ New password never logged
- ✅ All user tokens revoked after password change
- ✅ Email sent to user confirming password change

---

## 9. Logging Architecture

### 9.1 Database Audit Trail (Phase 2 - Implemented)

**Current Flow**:

```
GraphQL Mutation (Phase 3)
    ↓
Service Method (AuthService, TokenService, etc.)
    ↓
AuditService.log_event()
    ↓
IPEncryption.encrypt_ip() [if IP provided]
    ↓
AuditLog.objects.create()
    ↓
PostgreSQL Database
```

**Features**:

- ✅ Immutable audit trail (no updates/deletes)
- ✅ IP addresses encrypted before storage
- ✅ Organisation-scoped access
- ✅ Queryable via Django ORM
- ✅ Indexed for performance

**Query Examples**:

```python
# Get user's recent logs
logs = AuditService.get_user_logs(user, limit=50)

# Get organisation's logs
logs = AuditService.get_organisation_logs(org, limit=100)

# Filter by action type
failed_logins = AuditLog.objects.filter(
    action=AuditLog.ActionType.LOGIN_FAILED,
    created_at__gte=timezone.now() - timedelta(days=7)
)
```

### 9.2 Application Logging (Phase 6 - Deferred)

**Deferred Features**:

- File-based logging with rotation
- Separate log files by concern:
  - `logs/app.log` - General application
  - `logs/error.log` - Errors
  - `logs/security.log` - Security events
  - `logs/sql.log` - Database queries (dev only)
- Log rotation (10MB per file, 5 backups)
- Request ID tracking
- Performance logging decorators

**Current State**:

- Console logging only (development)
- JSON logging (production)
- `SecurityAuditMiddleware` logs to Python logger
- No file handlers configured

### 9.3 Environment-Specific Behaviour

| Environment | DB Audit Trail | File Logging | Sentry | IP Encryption |
| ----------- | -------------- | ------------ | ------ | ------------- |
| Development | ✅ Enabled     | ❌ Deferred  | ❌ No  | ✅ Required   |
| Testing     | ✅ Enabled     | ❌ Deferred  | ❌ No  | ✅ Required   |
| Staging     | ✅ Enabled     | ❌ Deferred  | ✅ Yes | ✅ Required   |
| Production  | ✅ Enabled     | ❌ Deferred  | ✅ Yes | ✅ Required   |

---

## 10. Configuration Requirements

### 10.1 Environment Variables

**Critical** (Required for Phase 2):

```bash
# IP Encryption Key (Fernet - 32-byte base64-encoded)
IP_ENCRYPTION_KEY=<fernet-key>

# Token Signing Key (HMAC-SHA256 - 32-byte URL-safe base64)
TOKEN_SIGNING_KEY=<signing-key>

# TOTP Encryption Key (for 2FA in Phase 4)
TOTP_ENCRYPTION_KEY=<fernet-key>
```

**Key Generation Commands**:

```python
# IP Encryption Key (Fernet)
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
# Output: gAAAAABkxxx...xxx=

# Token Signing Key (URL-safe base64)
import secrets
print(secrets.token_urlsafe(32))
# Output: abcd1234...wxyz

# TOTP Encryption Key (Fernet)
print(Fernet.generate_key().decode())
# Output: gAAAAABkxxx...xxx=
```

**Optional** (Sentry for production):

```bash
SENTRY_DSN=https://xxx@sentry.io/project
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1
```

### 10.2 Django Settings

**Base Settings** (`config/settings/base.py`):

```python
# Encryption and signing keys
IP_ENCRYPTION_KEY = env("IP_ENCRYPTION_KEY", default="")
TOKEN_SIGNING_KEY = env("TOKEN_SIGNING_KEY", default="")
TOTP_ENCRYPTION_KEY = env("TOTP_ENCRYPTION_KEY", default="")
```

**Development Settings** (`config/settings/dev.py`):

```python
# Allow empty keys in development (NOT recommended for production-like testing)
if not IP_ENCRYPTION_KEY:
    IP_ENCRYPTION_KEY = Fernet.generate_key().decode()

if not TOKEN_SIGNING_KEY:
    TOKEN_SIGNING_KEY = secrets.token_urlsafe(32)
```

### 10.3 Production Enforcement

**Production Settings** (`config/settings/production.py`):

```python
# Enforce encryption keys in production
if not IP_ENCRYPTION_KEY:
    raise ImproperlyConfigured("IP_ENCRYPTION_KEY must be set in production")

if not TOKEN_SIGNING_KEY:
    raise ImproperlyConfigured("TOKEN_SIGNING_KEY must be set in production")

if not TOTP_ENCRYPTION_KEY:
    raise ImproperlyConfigured("TOTP_ENCRYPTION_KEY must be set in production")
```

**Documentation**:

Add to `.env.production.example`:

```bash
# Encryption Keys (REQUIRED)
# Generate IP encryption key:
#   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
IP_ENCRYPTION_KEY=

# Generate token signing key:
#   python -c "import secrets; print(secrets.token_urlsafe(32))"
TOKEN_SIGNING_KEY=

# Generate TOTP encryption key:
#   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
TOTP_ENCRYPTION_KEY=
```

---

## 11. Testing Status

### 11.1 Phase 1 Tests (Models)

**Location**: `tests/unit/apps/core/test_audit_log_model.py`

**Status**: ✅ **COMPREHENSIVE** (30+ test cases)

**Coverage**:

- ✅ Model creation with valid data
- ✅ All action types
- ✅ User foreign key (nullable)
- ✅ Organisation foreign key (`SET_NULL`)
- ✅ IP address binary field
- ✅ User agent storage
- ✅ Device fingerprint
- ✅ Metadata JSON field
- ✅ UUID primary key
- ✅ Timestamps
- ✅ Indexes
- ✅ Ordering
- ✅ Filtering

### 11.2 Phase 2 Tests (Services and Security)

**Location**: `tests/unit/apps/core/test_phase2_security.py`

**Status**: ✅ **COMPREHENSIVE**

**Coverage**:

- ✅ IP encryption and decryption
- ✅ IP address validation (IPv4 and IPv6)
- ✅ Invalid IP address handling
- ✅ Token hashing with HMAC-SHA256
- ✅ Constant-time token comparison
- ✅ Token generation with sufficient entropy
- ✅ AuditService event logging
- ✅ IP encryption integration in AuditService
- ✅ Hash-then-store pattern for password reset tokens
- ✅ Token family management (replay detection)

**Example Test**:

```python
def test_audit_service_encrypts_ip_address(self):
    """Test AuditService encrypts IP addresses before storage."""
    user = User.objects.create_user(
        email="test@example.com",
        password="password123",
        organisation=self.organisation,
    )

    log = AuditService.log_login(
        user=user,
        ip_address="192.168.1.1",
        device_fingerprint="abc123"
    )

    # Verify IP is encrypted
    assert log.ip_address is not None
    assert isinstance(log.ip_address, bytes)
    assert b"192.168.1.1" not in log.ip_address

    # Verify IP can be decrypted
    decrypted_ip = IPEncryption.decrypt_ip(log.ip_address)
    assert decrypted_ip == "192.168.1.1"
```

### 11.3 Missing Tests (Phase 7)

**Integration Tests** - 🔴 **NOT IMPLEMENTED**:

- End-to-end audit logging flow (GraphQL → Service → Database)
- GraphQL mutation triggering audit log creation
- Audit log retrieval with organisation boundaries
- IP encryption key rotation with historical data

**BDD Tests** - 🔴 **NOT IMPLEMENTED**:

- `audit_logging.feature` - Audit log creation scenarios
- `security_events.feature` - Security event logging scenarios

---

## 12. Gap Analysis

### 12.1 Implemented Features

**Phase 1 + 2 Complete**:

- ✅ `AuditLog` model with encrypted IP storage
- ✅ `AuditService` with database integration
- ✅ `IPEncryption` utility with key rotation
- ✅ `TokenHasher` utility with HMAC-SHA256
- ✅ `AuthService` with race condition prevention
- ✅ `TokenService` with replay detection
- ✅ `PasswordResetService` with hash-then-store
- ✅ `SecurityAuditMiddleware` for HTTP events
- ✅ Django Admin configuration (read-only)
- ✅ Comprehensive unit tests

**Security Features**:

- ✅ IP addresses encrypted before storage
- ✅ Token hash-then-store pattern
- ✅ HMAC-SHA256 token hashing
- ✅ Constant-time comparison
- ✅ Key rotation support
- ✅ Device fingerprinting support
- ✅ Race condition prevention

### 12.2 Deferred to Phase 3 (GraphQL)

- ⚠️ Actual audit logging calls from GraphQL mutations
- ⚠️ Device fingerprinting utility
- ⚠️ GraphQL query for viewing audit logs
- ⚠️ Organisation boundary enforcement in queries
- ⚠️ GraphQL error handling with audit logging

### 12.3 Deferred to Phase 6 (Production Logging)

- 🔴 File-based logging with rotation
- 🔴 Log aggregation
- 🔴 Request ID tracking
- 🔴 Performance logging decorators
- 🔴 Sensitive data redaction filter
- 🔴 Audit log retention policy (90 days security, 30 days general)
- 🔴 Cleanup management command
- 🔴 Centralised log management

---

## 13. Compliance and Security

### 13.1 GDPR Compliance

**Data Protection Measures**:

- ✅ IP addresses encrypted at rest (Fernet AES-128-CBC)
- ✅ Email only logged in metadata for failed login attempts
- ✅ No unnecessary PII collected
- ✅ Legitimate interest documented (security)
- ⚠️ Retention policy NOT IMPLEMENTED (deferred to Phase 6)
- ⚠️ Right-to-erasure workflow NOT IMPLEMENTED (deferred to Phase 6)

**Legitimate Interest (GDPR Article 6(1)(f)**:

Storing encrypted IP addresses in security audit logs is justified for:

- Fraud detection and prevention
- Unauthorised access prevention
- Security incident response
- Regulatory compliance (SOC 2, ISO 27001)
- Legal requirements (data breach notification)

**Anonymisation Function** (`config/middleware/audit.py`):

```python
def anonymise_ip(ip_address: str) -> str:
    """Anonymise IP address for GDPR-compliant non-security logging.

    IPv4: Zeros last octet (192.168.1.45 -> 192.168.1.0)
    IPv6: Zeros last 80 bits (keeps /48 prefix)
    """
```

### 13.2 Security Best Practices

**Implemented**:

- ✅ Passwords never logged (plain or hashed)
- ✅ Tokens never logged (plain)
- ✅ Token hashes stored using HMAC-SHA256
- ✅ IP addresses encrypted before storage
- ✅ Constant-time comparison prevents timing attacks
- ✅ Cryptographic random token generation (256-bit entropy)
- ✅ Key rotation support
- ✅ Immutable audit trail (no updates/deletes)
- ✅ Race condition prevention with database locks
- ✅ Token replay detection with token families

**Not Yet Implemented**:

- ⚠️ Log file encryption (deferred to Phase 6)
- ⚠️ Audit log integrity verification (deferred to Phase 6)
- ⚠️ Centralised log aggregation (deferred to Phase 6)
- ⚠️ Anomaly detection (deferred to future)

### 13.3 Audit Log Retention

**Plan Requirement** (Phase 6):

- Security logs: 90 days
- General logs: 30 days
- Configurable via environment variables

**Current State**:

- 🔴 No retention policy implemented
- 🔴 No cleanup job scheduled
- 🔴 Unlimited growth (risk of database bloat)

**Recommendation** (Phase 6):

```python
# Management command
python manage.py cleanup_audit_logs --days=90 --dry-run

# Cron job (daily at 2am)
0 2 * * * python manage.py cleanup_audit_logs --days=90
```

---

## 14. Recommendations

### 14.1 Before Phase 3 (GraphQL)

**Priority: HIGH**

1. **Update Environment Variable Documentation**:

   ```bash
   # .env.production.example
   IP_ENCRYPTION_KEY=  # Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   TOKEN_SIGNING_KEY=  # Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Enforce Encryption Keys in Production**:

   ```python
   # config/settings/production.py (ALREADY DONE - verify)
   if not IP_ENCRYPTION_KEY:
       raise ImproperlyConfigured("IP_ENCRYPTION_KEY must be set")
   ```

3. **Document Key Rotation Procedure**:
   - Create `docs/OPERATIONS/KEY-ROTATION.md`
   - Document backup procedures
   - Document rollback procedures

### 14.2 Phase 3 Requirements

**Priority: CRITICAL**

1. **Integrate AuditService in GraphQL Mutations**:

   ```python
   # api/mutations/auth.py
   @strawberry.mutation
   def login(email: str, password: str, info) -> LoginPayload:
       request = info.context.request
       ip_address = get_client_ip(request)
       device_fingerprint = generate_device_fingerprint(request)

       result = AuthService.login(email, password, device_fingerprint, ip_address)

       if result:
           AuditService.log_login(
               user=result["user"],
               ip_address=ip_address,
               device_fingerprint=device_fingerprint,
               user_agent=request.META.get("HTTP_USER_AGENT", "")
           )
       else:
           AuditService.log_login_failed(
               email=email,
               ip_address=ip_address,
               device_fingerprint=device_fingerprint
           )
   ```

2. **Implement Device Fingerprinting**:

   ```python
   # apps/core/utils/fingerprint.py
   def generate_device_fingerprint(request) -> str:
       user_agent = request.META.get("HTTP_USER_AGENT", "")
       accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
       data = f"{user_agent}|{accept_language}".encode()
       return hashlib.sha256(data).hexdigest()
   ```

3. **Add GraphQL Query for Audit Logs**:

   ```python
   # api/queries/audit.py
   @strawberry.field
   def my_audit_logs(info, limit: int = 100) -> List[AuditLogType]:
       user = info.context.request.user
       logs = AuditService.get_user_logs(user, limit)
       return [AuditLogType.from_django(log) for log in logs]
   ```

### 14.3 Phase 6 Requirements (Production)

**Priority: MEDIUM**

1. **Implement File Logging with Rotation**:

   ```python
   # config/settings/production.py
   LOGGING["handlers"]["file"] = {
       "class": "logging.handlers.RotatingFileHandler",
       "filename": "/var/log/backend_template/app.log",
       "maxBytes": 10 * 1024 * 1024,  # 10MB
       "backupCount": 5,
       "formatter": "json",
   }
   ```

2. **Implement Audit Log Retention**:

   ```python
   # apps/core/management/commands/cleanup_audit_logs.py
   class Command(BaseCommand):
       def handle(self, *args, **options):
           cutoff = timezone.now() - timedelta(days=90)
           count, _ = AuditLog.objects.filter(created_at__lt=cutoff).delete()
           self.stdout.write(f"Deleted {count} audit logs older than 90 days")
   ```

3. **Implement Request ID Middleware**:
   - Generate UUID for each request
   - Add to all log entries and responses
   - Enable correlation across distributed systems

---

## 15. Next Steps

**Immediate** (Before Phase 3):

1. ✅ Update `.env.*.example` files with encryption key documentation
2. ✅ Verify production settings enforce encryption keys
3. Document key generation procedures in README
4. Document key rotation procedures

**Phase 3** (GraphQL Integration):

1. Integrate `AuditService` calls in all GraphQL mutations
2. Implement device fingerprinting utility
3. Add GraphQL queries for viewing audit logs
4. Add integration tests for audit logging flow
5. Verify organisation boundary enforcement

**Phase 6** (Production Logging):

1. Implement file-based logging with rotation
2. Implement audit log retention policy (90 days)
3. Implement request ID tracking
4. Implement performance logging decorators
5. Configure log aggregation (ELK, CloudWatch, etc.)

**Phase 7** (Testing):

1. Write integration tests for end-to-end audit flow
2. Write BDD tests for security event scenarios
3. Load testing for audit log write performance

---

## 16. References

**Project Documentation**:

- `docs/PLANS/US-001-USER-AUTHENTICATION.md` - Complete authentication plan
- `docs/QA/US-001/QA-US-001-REPORT.md` - QA report with security requirements
- `docs/REVIEWS/US-001/REVIEW-US-001.md` - Code review with security fixes
- `docs/SECURITY/US-001/SECURITY-US-001-IMPLEMENTATION.md` - Security implementation
- `.claude/CLAUDE.md` - Project standards and conventions

**Code Files** (Phase 1):

- `apps/core/models/audit_log.py` - AuditLog model
- `config/middleware/audit.py` - SecurityAuditMiddleware

**Code Files** (Phase 2):

- `apps/core/services/audit_service.py` - AuditService implementation
- `apps/core/services/auth_service.py` - AuthService implementation
- `apps/core/services/token_service.py` - TokenService implementation
- `apps/core/services/password_reset_service.py` - PasswordResetService
- `apps/core/utils/encryption.py` - IPEncryption utility
- `apps/core/utils/token_hasher.py` - TokenHasher utility

**Tests**:

- `tests/unit/apps/core/test_audit_log_model.py` - Phase 1 model tests (30+ tests)
- `tests/unit/apps/core/test_phase2_security.py` - Phase 2 security tests

**Dependencies**:

- `cryptography>=42.0.0` - Fernet encryption for IP addresses
- `python-json-logger>=3.0.0` - JSON log formatting (production)
- `sentry-sdk>=2.19.2` - Error tracking (production, optional)
- `pytz>=2024.1` - Timezone handling

---

**Report Compiled By**: Logging Infrastructure Specialist
**Date**: 08/01/2026
**Branch**: us001/user-authentication
**Version**: 0.4.1
**Status**: Phase 1 + 2 Complete, Ready for Phase 3 (GraphQL Integration)
