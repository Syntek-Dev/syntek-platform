# User Authentication System - Security Review

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Reviewed By**: Authentication Security Agent
**Review Date**: 07/01/2026
**Plan Version**: 1.1.0
**Status**: Approved with Recommendations

---

## Table of Contents

- [User Authentication System - Security Review](#user-authentication-system---security-review)
  - [Table of Contents](#table-of-contents)
  - [Executive Summary](#executive-summary)
  - [Review Scope](#review-scope)
  - [1. Password Security](#1-password-security)
    - [1.1 Password Requirements](#11-password-requirements)
    - [1.2 Password Hashing Configuration](#12-password-hashing-configuration)
    - [1.3 Password History Prevention](#13-password-history-prevention)
    - [1.4 Breach Checking](#14-breach-checking)
    - [Security Rating: Password Security](#security-rating-password-security)
  - [2. Multi-Factor Authentication](#2-multi-factor-authentication)
    - [2.1 TOTP Implementation](#21-totp-implementation)
    - [2.2 Backup Codes](#22-backup-codes)
    - [2.3 Device Management](#23-device-management)
    - [2.4 Recovery Flow](#24-recovery-flow)
    - [Security Rating: Multi-Factor Authentication](#security-rating-multi-factor-authentication)
  - [3. Session Management](#3-session-management)
    - [3.1 JWT Implementation](#31-jwt-implementation)
    - [3.2 Refresh Token Rotation](#32-refresh-token-rotation)
    - [3.3 Concurrent Session Limits](#33-concurrent-session-limits)
    - [3.4 Device Tracking](#34-device-tracking)
    - [Security Rating: Session Management](#security-rating-session-management)
  - [4. Account Recovery](#4-account-recovery)
    - [4.1 Password Reset Flow](#41-password-reset-flow)
    - [4.2 Token Expiration](#42-token-expiration)
    - [4.3 Email Verification](#43-email-verification)
    - [4.4 Anti-Enumeration Protection](#44-anti-enumeration-protection)
    - [Security Rating: Account Recovery](#security-rating-account-recovery)
  - [5. Account Lockout and Rate Limiting](#5-account-lockout-and-rate-limiting)
    - [5.1 Rate Limiting Strategy](#51-rate-limiting-strategy)
    - [5.2 Lockout Mechanisms](#52-lockout-mechanisms)
    - [5.3 Unlock Procedures](#53-unlock-procedures)
    - [5.4 Distributed Rate Limiting](#54-distributed-rate-limiting)
    - [Security Rating: Account Lockout and Rate Limiting](#security-rating-account-lockout-and-rate-limiting)
  - [6. Permission System](#6-permission-system)
    - [6.1 RBAC Implementation](#61-rbac-implementation)
    - [6.2 Django Groups Usage](#62-django-groups-usage)
    - [6.3 Organisation Boundaries](#63-organisation-boundaries)
    - [6.4 Permission Checking Patterns](#64-permission-checking-patterns)
    - [Security Rating: Permission System](#security-rating-permission-system)
  - [7. Security Headers and Configuration](#7-security-headers-and-configuration)
    - [7.1 CORS Configuration](#71-cors-configuration)
    - [7.2 Security Middleware](#72-security-middleware)
    - [7.3 IP Encryption](#73-ip-encryption)
    - [7.4 Audit Logging](#74-audit-logging)
    - [Security Rating: Security Headers and Configuration](#security-rating-security-headers-and-configuration)
  - [8. Recommendations](#8-recommendations)
    - [8.1 Critical Priority (Must Implement)](#81-critical-priority-must-implement)
    - [8.2 High Priority (Should Implement)](#82-high-priority-should-implement)
    - [8.3 Medium Priority (Consider Implementing)](#83-medium-priority-consider-implementing)
    - [8.4 Low Priority (Nice to Have)](#84-low-priority-nice-to-have)
  - [9. Security Best Practice Alignment](#9-security-best-practice-alignment)
    - [OWASP Authentication Guidelines](#owasp-authentication-guidelines)
    - [NIST Digital Identity Guidelines](#nist-digital-identity-guidelines)
    - [GDPR Compliance](#gdpr-compliance)
  - [10. Risk Assessment](#10-risk-assessment)
  - [11. Implementation Checklist](#11-implementation-checklist)
    - [Before Development](#before-development)
    - [Phase 1: Core Models (Current)](#phase-1-core-models-current)
    - [Phase 2: Authentication Service (Current)](#phase-2-authentication-service-current)
    - [Phase 3: GraphQL API (Current)](#phase-3-graphql-api-current)
    - [Phase 4: Two-Factor Authentication (Current)](#phase-4-two-factor-authentication-current)
    - [Phase 5: Password Reset and Email (Current)](#phase-5-password-reset-and-email-current)
    - [Phase 6: Audit Logging and Security (Current)](#phase-6-audit-logging-and-security-current)
    - [Phase 7: Testing (Current)](#phase-7-testing-current)
    - [Post-Implementation](#post-implementation)
  - [12. Conclusion](#12-conclusion)

---

## Executive Summary

This review evaluates the User Authentication System implementation plan (US-001) for the Django
backend template. The plan demonstrates a strong security foundation with comprehensive coverage of
authentication, authorisation, and audit logging requirements.

**Overall Security Rating**: 8.5/10 (Very Good)

**Key Strengths:**

- Strong password requirements (12+ character minimum)
- Argon2 password hashing (industry best practice)
- TOTP-based 2FA implementation
- Comprehensive audit logging with IP encryption
- JWT token management with expiration
- Multi-tenancy organisation boundaries
- Rate limiting on authentication endpoints

**Key Concerns:**

- Missing password breach checking integration
- No password history enforcement specified
- Concurrent session limit not implemented
- Missing account lockout mechanisms
- CORS configuration details incomplete
- No explicit security header configuration

**Recommendation**: Approve with critical security enhancements required before production
deployment.

---

## Review Scope

This review covers the following aspects of the authentication plan:

1. Password security requirements and hashing
2. Multi-factor authentication implementation
3. Session management and JWT handling
4. Account recovery procedures
5. Rate limiting and brute force protection
6. Permission system and RBAC
7. Security headers and middleware
8. Compliance with security standards (OWASP, NIST, GDPR)

---

## 1. Password Security

### 1.1 Password Requirements

**Planned Implementation:**

- Minimum 12 characters
- Maximum 128 characters
- At least one uppercase letter (A-Z)
- At least one lowercase letter (a-z)
- At least one number (0-9)
- At least one special character

**Analysis:**

The 12-character minimum aligns with NIST recommendations and provides adequate entropy against
brute force attacks. The complexity requirements balance security with usability.

**Strengths:**

- 12-character minimum exceeds common 8-character requirements
- Maximum 128 characters allows for passphrases
- Validation enforced at application level
- Clear error messages for user feedback

**Concerns:**

1. No mention of password strength meter for user guidance
2. Missing integration with breached password databases (e.g., Have I Been Pwned)
3. No documentation of password complexity scoring

**Recommendations:**

```python
# Add to config/validators/password.py

import requests
import hashlib

def check_breached_password(password: str) -> bool:
    """Check if password appears in breach databases.

    Uses Have I Been Pwned API with k-anonymity to preserve privacy.

    Args:
        password: The password to check.

    Returns:
        True if password is breached, False otherwise.
    """
    sha1_password = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix = sha1_password[:5]
    suffix = sha1_password[5:]

    try:
        response = requests.get(
            f'https://api.pwnedpasswords.com/range/{prefix}',
            timeout=2
        )
        if response.status_code == 200:
            hashes = response.text.split('\r\n')
            for hash_count in hashes:
                hash_part, count = hash_count.split(':')
                if hash_part == suffix:
                    return True
        return False
    except requests.RequestException:
        # If API unavailable, don't block password change
        return False
```

### 1.2 Password Hashing Configuration

**Planned Implementation:**

```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]
```

**Analysis:**

Argon2 is the optimal choice for password hashing (winner of Password Hashing Competition 2015).
The configuration includes fallback hashers for legacy support.

**Strengths:**

- Argon2 as primary hasher (OWASP recommended)
- Automatic rehashing on login for legacy passwords
- Memory-hard algorithm resistant to GPU attacks

**Concerns:**

1. No specification of Argon2 parameters (time cost, memory cost, parallelism)
2. Default parameters may not be optimal for security vs performance

**Recommendations:**

```python
# config/settings/base.py

# Argon2 parameters optimised for security (adjust based on server capacity)
ARGON2_TIME_COST = 4          # Number of iterations
ARGON2_MEMORY_COST = 65536    # Memory usage in KB (64 MB)
ARGON2_PARALLELISM = 2        # Number of parallel threads

# Add to PASSWORD_HASHERS configuration
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

# Target: password hashing should take 300-500ms on production hardware
```

### 1.3 Password History Prevention

**Planned Implementation:**

Mentioned in requirements: "Password history to prevent reuse"

**Analysis:**

Password history is mentioned but not detailed in database schema or implementation.

**Concerns:**

1. No `PasswordHistory` model defined in database schema
2. No specification of how many historical passwords to check
3. No implementation details provided

**Recommendations:**

```python
# apps/core/models/password_history.py

from django.db import models
from django.contrib.auth.hashers import check_password

class PasswordHistory(models.Model):
    """Historical passwords for preventing reuse.

    Stores hashed passwords to prevent users from reusing recent passwords.

    Attributes:
        user: Foreign key to User
        password_hash: Hashed password (stored using same hasher as User)
        created_at: When this password was set
    """

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
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def check_password(self, password: str) -> bool:
        """Check if provided password matches this historical password.

        Args:
            password: Plain text password to check.

        Returns:
            True if passwords match, False otherwise.
        """
        return check_password(password, self.password_hash)


# Add to apps/core/services/auth_service.py

def change_password(user, new_password: str, history_count: int = 5) -> None:
    """Change user password with history checking.

    Args:
        user: User instance
        new_password: New password (plain text)
        history_count: Number of historical passwords to check (default: 5)

    Raises:
        ValidationError: If new password matches recent password
    """
    # Check against recent passwords
    recent_passwords = user.password_history.all()[:history_count]
    for history in recent_passwords:
        if history.check_password(new_password):
            raise ValidationError(
                f"Password must not match any of your last {history_count} passwords"
            )

    # Save current password to history before changing
    PasswordHistory.objects.create(
        user=user,
        password_hash=user.password
    )

    # Set new password
    user.set_password(new_password)
    user.save()

    # Clean up old history (keep last 10)
    old_passwords = user.password_history.all()[10:]
    for old_password in old_passwords:
        old_password.delete()
```

### 1.4 Breach Checking

**Planned Implementation:**

Not mentioned in the plan.

**Analysis:**

Integration with breach databases (Have I Been Pwned) is a security best practice that prevents
users from selecting compromised passwords.

**Concerns:**

1. No integration with breach checking services
2. Risk of users selecting previously compromised passwords

**Recommendations:**

Implement breach checking during registration and password change operations. See recommendation
in section 1.1.

### Security Rating: Password Security

**Rating**: 7.5/10 (Good)

**Justification:**

- Strong foundation with Argon2 and 12-character minimum
- Missing breach checking integration (-1.0)
- Incomplete password history implementation (-1.0)
- Missing Argon2 parameter tuning (-0.5)

---

## 2. Multi-Factor Authentication

### 2.1 TOTP Implementation

**Planned Implementation:**

- TOTP-based 2FA (compatible with Google Authenticator, Authy)
- QR code generation for setup
- TOTP secret encryption before storage
- 30-second time window (standard TOTP)

**Analysis:**

TOTP is an excellent choice for 2FA, providing strong security without relying on SMS (which is
vulnerable to SIM swapping attacks).

**Strengths:**

- TOTP preferred over SMS-based OTP (NIST recommends against SMS)
- Secrets encrypted before storage
- Standard 30-second time window
- Compatible with major authenticator apps

**Concerns:**

1. No specification of TOTP algorithm (SHA-1, SHA-256, SHA-512)
2. No mention of time window tolerance for clock skew
3. No rate limiting specifically for 2FA verification attempts

**Recommendations:**

```python
# apps/core/services/totp_service.py

import pyotp
from cryptography.fernet import Fernet
from django.conf import settings
from django.core.cache import cache

class TOTPService:
    """Service for managing TOTP two-factor authentication."""

    TOTP_ALGORITHM = 'SHA256'  # Use SHA-256 instead of SHA-1
    TOTP_DIGITS = 6
    TOTP_INTERVAL = 30  # seconds
    TOTP_TOLERANCE = 1  # Allow 1 time step before/after (90 second window)

    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret.

        Returns:
            Base32-encoded secret string.
        """
        return pyotp.random_base32()

    @staticmethod
    def encrypt_secret(secret: str) -> bytes:
        """Encrypt TOTP secret before storage.

        Args:
            secret: Plain text TOTP secret.

        Returns:
            Encrypted secret as bytes.
        """
        cipher = Fernet(settings.TOTP_ENCRYPTION_KEY)
        return cipher.encrypt(secret.encode())

    @staticmethod
    def decrypt_secret(encrypted_secret: bytes) -> str:
        """Decrypt TOTP secret.

        Args:
            encrypted_secret: Encrypted secret bytes.

        Returns:
            Plain text secret.
        """
        cipher = Fernet(settings.TOTP_ENCRYPTION_KEY)
        return cipher.decrypt(encrypted_secret).decode()

    @staticmethod
    def verify_totp(user, totp_code: str) -> bool:
        """Verify TOTP code with rate limiting.

        Args:
            user: User instance
            totp_code: 6-digit TOTP code

        Returns:
            True if code is valid, False otherwise.
        """
        # Check rate limit (5 attempts per 15 minutes)
        cache_key = f'totp_attempts:{user.id}'
        attempts = cache.get(cache_key, 0)

        if attempts >= 5:
            return False

        # Get user's TOTP device
        device = user.totp_devices.filter(confirmed=True).first()
        if not device:
            return False

        # Decrypt secret
        secret = TOTPService.decrypt_secret(device.secret)

        # Verify code with tolerance
        totp = pyotp.TOTP(
            secret,
            digest=TOTPService.TOTP_ALGORITHM,
            digits=TOTPService.TOTP_DIGITS,
            interval=TOTPService.TOTP_INTERVAL
        )

        is_valid = totp.verify(
            totp_code,
            valid_window=TOTPService.TOTP_TOLERANCE
        )

        if not is_valid:
            # Increment failed attempts
            cache.set(cache_key, attempts + 1, timeout=900)  # 15 minutes
        else:
            # Clear failed attempts on success
            cache.delete(cache_key)
            device.last_used_at = timezone.now()
            device.save()

        return is_valid
```

### 2.2 Backup Codes

**Planned Implementation:**

- Backup codes for account recovery
- Generated during 2FA setup

**Analysis:**

Backup codes are essential for account recovery when 2FA device is lost.

**Strengths:**

- Backup codes included in implementation plan
- Prevents account lockout scenarios

**Concerns:**

1. No specification of backup code format or count
2. No mention of hashing backup codes before storage
3. No indication of one-time use enforcement

**Recommendations:**

```python
# apps/core/services/backup_code_service.py

import secrets
import hashlib
from typing import List

class BackupCodeService:
    """Service for managing 2FA backup codes."""

    CODE_COUNT = 10  # Generate 10 backup codes
    CODE_LENGTH = 8  # 8-character codes

    @staticmethod
    def generate_backup_codes() -> List[str]:
        """Generate backup codes for 2FA recovery.

        Returns:
            List of 10 randomly generated backup codes.
        """
        codes = []
        for _ in range(BackupCodeService.CODE_COUNT):
            # Generate cryptographically secure random code
            code = secrets.token_hex(BackupCodeService.CODE_LENGTH // 2).upper()
            # Format as XXXX-XXXX for readability
            formatted = f"{code[:4]}-{code[4:]}"
            codes.append(formatted)
        return codes

    @staticmethod
    def hash_backup_code(code: str) -> str:
        """Hash backup code before storage.

        Args:
            code: Plain text backup code.

        Returns:
            SHA-256 hash of the code.
        """
        return hashlib.sha256(code.encode()).hexdigest()

    @staticmethod
    def verify_backup_code(user, code: str) -> bool:
        """Verify backup code and mark as used.

        Args:
            user: User instance
            code: Backup code provided by user

        Returns:
            True if code is valid and unused, False otherwise.
        """
        code_hash = BackupCodeService.hash_backup_code(code)

        # Find matching unused backup code
        backup_code = user.backup_codes.filter(
            code_hash=code_hash,
            used=False
        ).first()

        if backup_code:
            # Mark as used
            backup_code.used = True
            backup_code.used_at = timezone.now()
            backup_code.save()
            return True

        return False


# Add BackupCode model to apps/core/models/backup_code.py

class BackupCode(models.Model):
    """Backup codes for 2FA recovery.

    Attributes:
        user: Foreign key to User
        code_hash: Hashed backup code (SHA-256)
        used: Whether code has been used
        used_at: When code was used
        created_at: When code was generated
    """

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='backup_codes'
    )
    code_hash = models.CharField(max_length=64, unique=True)
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'backup_codes'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'used']),
        ]
```

### 2.3 Device Management

**Planned Implementation:**

- TOTPDevice model with device name
- Multiple devices per user supported
- Device confirmation requirement

**Analysis:**

Device management allows users to register multiple authenticators for flexibility.

**Strengths:**

- Support for multiple 2FA devices
- Device naming for identification
- Confirmation requirement before activation

**Concerns:**

1. No device revocation workflow specified
2. No last-used timestamp tracking (mentioned in model but not in workflow)
3. No notification when new device is added

**Recommendations:**

Add device management operations to GraphQL API:

```graphql
type Mutation {
  """
  Remove a 2FA device.
  """
  removeTwoFactorDevice(deviceId: ID!, password: String!): Boolean!

  """
  Rename a 2FA device.
  """
  renameTwoFactorDevice(deviceId: ID!, name: String!): Boolean!

  """
  List all 2FA devices for current user.
  """
  listTwoFactorDevices: [TOTPDevice!]!
}

type TOTPDevice {
  id: ID!
  name: String!
  confirmed: Boolean!
  lastUsedAt: DateTime
  createdAt: DateTime!
}
```

### 2.4 Recovery Flow

**Planned Implementation:**

- Backup codes for recovery
- Admin recovery process mentioned in risk mitigation

**Analysis:**

Recovery flow is partially specified but lacks detail.

**Concerns:**

1. No self-service recovery flow if all backup codes used
2. Admin recovery process not detailed
3. No emergency contact option

**Recommendations:**

Implement tiered recovery approach:

1. **Backup codes** (primary recovery)
2. **Support ticket** (secondary recovery with identity verification)
3. **Admin override** (emergency only with full audit logging)

```python
# Add to apps/core/services/auth_service.py

def initiate_2fa_recovery(user, support_ticket_id: str) -> None:
    """Initiate 2FA recovery process via support ticket.

    Creates a time-limited recovery token that support staff can use
    to temporarily disable 2FA after identity verification.

    Args:
        user: User instance
        support_ticket_id: Reference to support ticket

    Returns:
        Recovery token (send to user via verified email)
    """
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    RecoveryToken.objects.create(
        user=user,
        token_hash=token_hash,
        support_ticket_id=support_ticket_id,
        expires_at=timezone.now() + timedelta(hours=24)
    )

    # Send email with recovery instructions
    EmailService.send_2fa_recovery_email(user, token)

    # Log audit event
    AuditService.log_event(
        action='2fa_recovery_initiated',
        user=user,
        metadata={'support_ticket_id': support_ticket_id}
    )
```

### Security Rating: Multi-Factor Authentication

**Rating**: 8.0/10 (Very Good)

**Justification:**

- Strong TOTP implementation foundation
- Backup codes included
- Missing rate limiting on 2FA attempts (-0.5)
- Incomplete recovery workflow (-1.0)
- No device management operations (-0.5)

---

## 3. Session Management

### 3.1 JWT Implementation

**Planned Implementation:**

- JWT tokens for authentication
- 24-hour token expiration
- Token stored in Redis for revocation
- Token hashes stored in database

**Analysis:**

JWT with server-side storage provides good balance of statelessness and revocation capability.

**Strengths:**

- JWT tokens with expiration
- Server-side token storage for revocation
- Redis caching for performance

**Concerns:**

1. No specification of JWT signing algorithm (HS256, RS256, ES256)
2. No mention of JWT claims (user ID, organisation ID, roles)
3. Token expiration is inactivity-based but not clearly documented

**Recommendations:**

```python
# apps/core/services/token_service.py

import jwt
from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache

class TokenService:
    """Service for managing JWT authentication tokens."""

    # Use RS256 (asymmetric) for enhanced security
    ALGORITHM = 'RS256'
    TOKEN_EXPIRY = timedelta(hours=24)
    REFRESH_TOKEN_EXPIRY = timedelta(days=30)

    @staticmethod
    def create_token(user, request) -> dict:
        """Create JWT access and refresh tokens.

        Args:
            user: User instance
            request: HTTP request for IP/user agent

        Returns:
            Dict with 'token', 'refresh_token', and 'expires_at'
        """
        now = datetime.utcnow()
        expires_at = now + TokenService.TOKEN_EXPIRY

        # JWT payload claims
        payload = {
            'user_id': str(user.id),
            'email': user.email,
            'organisation_id': str(user.organisation_id),
            'roles': list(user.groups.values_list('name', flat=True)),
            'iat': now,  # Issued at
            'exp': expires_at,  # Expiration
            'jti': secrets.token_urlsafe(16),  # Unique token ID
        }

        # Sign token with private key
        token = jwt.encode(
            payload,
            settings.JWT_PRIVATE_KEY,
            algorithm=TokenService.ALGORITHM
        )

        # Generate refresh token
        refresh_token = secrets.token_urlsafe(32)
        refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

        # Store session in database
        SessionToken.objects.create(
            user=user,
            token_hash=hashlib.sha256(token.encode()).hexdigest(),
            refresh_token_hash=refresh_token_hash,
            ip_address=IPEncryption.encrypt_ip(get_client_ip(request)),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            expires_at=expires_at
        )

        # Cache token for fast validation
        cache.set(
            f'token:{payload["jti"]}',
            {'user_id': str(user.id), 'valid': True},
            timeout=int(TokenService.TOKEN_EXPIRY.total_seconds())
        )

        return {
            'token': token,
            'refresh_token': refresh_token,
            'expires_at': expires_at.isoformat()
        }

    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify JWT token and return payload.

        Args:
            token: JWT token string

        Returns:
            Decoded payload dict

        Raises:
            jwt.InvalidTokenError: If token is invalid or expired
        """
        try:
            # Decode and verify token
            payload = jwt.decode(
                token,
                settings.JWT_PUBLIC_KEY,
                algorithms=[TokenService.ALGORITHM]
            )

            # Check if token is revoked (Redis cache)
            jti = payload.get('jti')
            cached = cache.get(f'token:{jti}')
            if cached and not cached.get('valid'):
                raise jwt.InvalidTokenError('Token has been revoked')

            return payload

        except jwt.ExpiredSignatureError:
            raise jwt.InvalidTokenError('Token has expired')
        except jwt.InvalidTokenError as e:
            raise e
```

### 3.2 Refresh Token Rotation

**Planned Implementation:**

- Refresh tokens with 30-day expiration
- Refresh token rotation mentioned in session management

**Analysis:**

Refresh token rotation is mentioned but not detailed.

**Concerns:**

1. Refresh token rotation mechanism not specified
2. No detection of refresh token reuse (attack indicator)
3. No automatic family invalidation on suspicious activity

**Recommendations:**

Implement refresh token rotation with family tracking:

```python
# Add to TokenService

@staticmethod
def refresh_token(refresh_token: str) -> dict:
    """Refresh authentication token with rotation.

    Args:
        refresh_token: Current refresh token

    Returns:
        New token and refresh_token

    Raises:
        jwt.InvalidTokenError: If refresh token is invalid or reused
    """
    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

    # Find session with this refresh token
    session = SessionToken.objects.filter(
        refresh_token_hash=refresh_token_hash,
        expires_at__gt=timezone.now()
    ).first()

    if not session:
        # Potential token reuse attack
        AuditService.log_event(
            action='refresh_token_reuse_detected',
            user=None,
            metadata={'token_hash': refresh_token_hash}
        )
        raise jwt.InvalidTokenError('Invalid or expired refresh token')

    user = session.user

    # Revoke old session
    session.delete()

    # Issue new tokens
    new_tokens = TokenService.create_token(user, request)

    # Log successful refresh
    AuditService.log_event(
        action='token_refreshed',
        user=user,
        metadata={'old_session_id': str(session.id)}
    )

    return new_tokens
```

### 3.3 Concurrent Session Limits

**Planned Implementation:**

Open question: "What is the maximum number of active sessions per user?"
Decision: 5 sessions per user, oldest revoked automatically

**Analysis:**

Concurrent session limit is decided but not implemented in the plan.

**Concerns:**

1. Session limit enforcement not implemented in code examples
2. No mechanism to display active sessions to users
3. No user notification when session is forcibly revoked

**Recommendations:**

```python
# Add to TokenService

@staticmethod
def enforce_session_limit(user, max_sessions: int = 5) -> None:
    """Enforce maximum concurrent sessions per user.

    Args:
        user: User instance
        max_sessions: Maximum allowed sessions (default: 5)
    """
    active_sessions = SessionToken.objects.filter(
        user=user,
        expires_at__gt=timezone.now()
    ).order_by('-last_activity')

    if active_sessions.count() >= max_sessions:
        # Revoke oldest sessions
        sessions_to_revoke = active_sessions[max_sessions - 1:]
        for session in sessions_to_revoke:
            # Invalidate in cache
            cache.delete(f'token:{session.token_hash}')
            # Delete from database
            session.delete()

        # Log session revocation
        AuditService.log_event(
            action='session_limit_enforced',
            user=user,
            metadata={
                'revoked_count': len(sessions_to_revoke),
                'max_sessions': max_sessions
            }
        )


# Add GraphQL query for listing active sessions

@strawberry.field
def active_sessions(self, info: Info) -> List[SessionInfo]:
    """List active sessions for current user.

    Returns:
        List of active sessions with device info
    """
    user = info.context.request.user
    sessions = SessionToken.objects.filter(
        user=user,
        expires_at__gt=timezone.now()
    ).order_by('-last_activity')

    return [
        SessionInfo(
            id=str(session.id),
            ip_address=IPEncryption.decrypt_ip(session.ip_address),
            user_agent=session.user_agent,
            last_activity=session.last_activity,
            created_at=session.created_at
        )
        for session in sessions
    ]
```

### 3.4 Device Tracking

**Planned Implementation:**

- IP address captured and encrypted
- User agent stored
- Last activity timestamp

**Analysis:**

Basic device tracking is present but could be enhanced.

**Strengths:**

- IP encryption preserves privacy
- User agent stored for identification
- Last activity tracking

**Concerns:**

1. No device fingerprinting beyond user agent
2. No anomaly detection (login from unusual location)
3. No user notification for new device login

**Recommendations:**

Add device fingerprinting and anomaly detection:

```python
# apps/core/services/device_service.py

import user_agents

class DeviceService:
    """Service for device tracking and anomaly detection."""

    @staticmethod
    def get_device_fingerprint(request) -> dict:
        """Generate device fingerprint from request.

        Args:
            request: HTTP request

        Returns:
            Dict with device information
        """
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        ua = user_agents.parse(user_agent_string)

        return {
            'browser': ua.browser.family,
            'browser_version': ua.browser.version_string,
            'os': ua.os.family,
            'os_version': ua.os.version_string,
            'device': ua.device.family,
            'is_mobile': ua.is_mobile,
            'is_tablet': ua.is_tablet,
            'is_pc': ua.is_pc,
        }

    @staticmethod
    def check_suspicious_login(user, request) -> bool:
        """Check if login is from unusual location or device.

        Args:
            user: User instance
            request: HTTP request

        Returns:
            True if login appears suspicious, False otherwise
        """
        ip_address = get_client_ip(request)

        # Get recent login locations
        recent_sessions = SessionToken.objects.filter(
            user=user,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).order_by('-created_at')[:10]

        recent_ips = [
            IPEncryption.decrypt_ip(session.ip_address)
            for session in recent_sessions
        ]

        # Check if IP is new
        if ip_address not in recent_ips:
            # Send notification email
            EmailService.send_new_device_alert(user, request)

            # Log suspicious activity
            AuditService.log_event(
                action='suspicious_login_detected',
                user=user,
                request=request,
                metadata={
                    'new_ip': ip_address,
                    'recent_ips': recent_ips[:3]  # Last 3 IPs
                }
            )

            return True

        return False
```

### Security Rating: Session Management

**Rating**: 7.0/10 (Good)

**Justification:**

- JWT with server-side storage is solid approach
- Missing refresh token rotation details (-1.0)
- Concurrent session limit not implemented (-1.0)
- Basic device tracking but no anomaly detection (-1.0)

---

## 4. Account Recovery

### 4.1 Password Reset Flow

**Planned Implementation:**

1. User requests reset via email
2. Token generated with 15-minute expiration
3. Reset link sent via email
4. User sets new password with token
5. Token marked as used
6. All sessions invalidated

**Analysis:**

Password reset flow is well-designed with appropriate security measures.

**Strengths:**

- Short token expiration (15 minutes)
- Single-use tokens
- Session invalidation after password change
- Email-based delivery

**Concerns:**

1. No mention of rate limiting on password reset requests
2. No CAPTCHA to prevent automated abuse
3. Email enumeration protection not explicitly stated

**Recommendations:**

Add rate limiting and CAPTCHA:

```python
# apps/core/mutations/auth.py

@strawberry.mutation
def request_password_reset(
    self,
    info: Info,
    email: str,
    captcha_token: str
) -> bool:
    """Request password reset email.

    Args:
        info: GraphQL context
        email: User email address
        captcha_token: CAPTCHA verification token

    Returns:
        Always returns True (prevents email enumeration)
    """
    # Verify CAPTCHA first
    if not CaptchaService.verify_token(captcha_token):
        # Still return True to prevent enumeration
        return True

    # Rate limit check (3 per hour per IP)
    ip_address = get_client_ip(info.context.request)
    cache_key = f'password_reset_requests:{ip_address}'
    attempts = cache.get(cache_key, 0)

    if attempts >= 3:
        # Still return True but don't send email
        return True

    # Increment attempt counter
    cache.set(cache_key, attempts + 1, timeout=3600)

    # Find user (don't reveal if user exists)
    try:
        user = User.objects.get(email=email)

        # Generate reset token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # Create reset token record
        PasswordResetToken.objects.create(
            user=user,
            token=token_hash,
            expires_at=timezone.now() + timedelta(minutes=15)
        )

        # Send reset email
        EmailService.send_password_reset_email(user, token)

        # Log audit event
        AuditService.log_event(
            action='password_reset_request',
            user=user,
            request=info.context.request
        )

    except User.DoesNotExist:
        # Don't reveal that user doesn't exist
        pass

    # Always return True regardless of whether user exists
    return True
```

### 4.2 Token Expiration

**Planned Implementation:**

- Password reset tokens: 15 minutes
- Email verification tokens: 24 hours

**Analysis:**

Token expiration times are appropriate and follow security best practices.

**Strengths:**

- Short password reset expiration (15 minutes)
- Longer email verification expiration (24 hours) for usability
- Clear expiration tracking in database

**Concerns:**

None identified. Token expiration is well-configured.

**Recommendations:**

No changes recommended. Current implementation is secure.

### 4.3 Email Verification

**Planned Implementation:**

- Verification email sent on registration
- 24-hour token expiration
- Resend verification option
- Email verified flag on user model

**Analysis:**

Email verification flow is comprehensive and user-friendly.

**Strengths:**

- Verification required before full access
- Resend option for usability
- Appropriate expiration time

**Concerns:**

1. No specification of what actions are allowed for unverified users
2. No automatic account cleanup for never-verified users

**Recommendations:**

```python
# Add to User model

def has_permission(self, permission: str) -> bool:
    """Check if user has permission with email verification check.

    Args:
        permission: Permission string to check

    Returns:
        True if user has permission and is verified, False otherwise
    """
    # Unverified users have limited permissions
    if not self.email_verified:
        allowed_permissions = [
            'core.view_own_profile',
            'core.change_own_profile',
            'core.resend_verification_email',
        ]
        if permission not in allowed_permissions:
            return False

    return super().has_permission(permission)


# Add management command to cleanup unverified accounts

# apps/core/management/commands/cleanup_unverified_users.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.core.models import User

class Command(BaseCommand):
    """Delete user accounts that were never verified after 7 days."""

    help = 'Clean up unverified user accounts older than 7 days'

    def handle(self, *args, **options):
        cutoff_date = timezone.now() - timedelta(days=7)

        unverified_users = User.objects.filter(
            email_verified=False,
            created_at__lt=cutoff_date
        )

        count = unverified_users.count()
        unverified_users.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Deleted {count} unverified user accounts older than 7 days'
            )
        )
```

### 4.4 Anti-Enumeration Protection

**Planned Implementation:**

Mentioned in password reset flow: "Always return success message to prevent email enumeration"

**Analysis:**

Anti-enumeration is mentioned but not consistently applied across all endpoints.

**Strengths:**

- Password reset returns same message regardless of user existence
- Prevents attackers from discovering valid email addresses

**Concerns:**

1. No mention of anti-enumeration for registration endpoint
2. Login error messages may reveal user existence

**Recommendations:**

Apply anti-enumeration consistently:

```python
# Registration endpoint

@strawberry.mutation
def register(self, info: Info, input: RegisterInput) -> AuthPayload:
    """Register new user with anti-enumeration protection.

    Args:
        info: GraphQL context
        input: Registration input data

    Returns:
        AuthPayload with token

    Raises:
        ValidationError: Generic error message for any failure
    """
    try:
        # Check if email already exists
        if User.objects.filter(email=input.email).exists():
            # Don't reveal that email is taken
            # Return same error as invalid input
            raise ValidationError('Registration failed. Please check your input.')

        # Continue with registration...

    except ValidationError as e:
        # Return generic error message
        raise ValidationError('Registration failed. Please check your input.')


# Login endpoint

@strawberry.mutation
def login(self, info: Info, input: LoginInput) -> AuthPayload:
    """Login with anti-enumeration protection.

    Args:
        info: GraphQL context
        input: Login credentials

    Returns:
        AuthPayload with token

    Raises:
        ValidationError: Generic error for any authentication failure
    """
    try:
        user = User.objects.get(email=input.email)

        if not user.check_password(input.password):
            # Same error message as user not found
            raise ValidationError('Invalid email or password')

        # Continue with login...

    except User.DoesNotExist:
        # Same error message as wrong password
        raise ValidationError('Invalid email or password')
```

### Security Rating: Account Recovery

**Rating**: 8.5/10 (Very Good)

**Justification:**

- Well-designed password reset flow
- Appropriate token expiration times
- Anti-enumeration protection mentioned
- Missing rate limiting on reset requests (-0.5)
- No CAPTCHA implementation (-1.0)

---

## 5. Account Lockout and Rate Limiting

### 5.1 Rate Limiting Strategy

**Planned Implementation:**

- Login attempts: 5 per 15 minutes per IP
- Registration attempts: 3 per hour per IP
- Password reset: 3 per hour per email
- 2FA attempts: 5 per 15 minutes per user

**Analysis:**

Rate limiting strategy is comprehensive and covers all authentication endpoints.

**Strengths:**

- Multiple rate limiting rules for different endpoints
- IP-based limiting for login/registration
- User-based limiting for 2FA
- Redis-backed for performance

**Concerns:**

1. No distributed rate limiting implementation details
2. No rate limiting bypass for trusted IPs (corporate networks)
3. Rate limit headers not mentioned in API responses

**Recommendations:**

Enhance rate limiting implementation:

```python
# apps/core/middleware/rate_limit.py

from django.core.cache import cache
from django.http import JsonResponse
import time

class RateLimitMiddleware:
    """Rate limiting middleware for authentication endpoints."""

    LIMITS = {
        'login': {'requests': 5, 'window': 900, 'key': 'ip'},  # 15 min
        'register': {'requests': 3, 'window': 3600, 'key': 'ip'},  # 1 hour
        'password_reset': {'requests': 3, 'window': 3600, 'key': 'email'},  # 1 hour
        '2fa_verify': {'requests': 5, 'window': 900, 'key': 'user'},  # 15 min
    }

    # Trusted IP ranges (bypass rate limiting)
    TRUSTED_IPS = [
        '10.0.0.0/8',      # Internal network
        '172.16.0.0/12',   # Internal network
        '192.168.0.0/16',  # Internal network
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if IP is trusted
        if self.is_trusted_ip(request):
            return self.get_response(request)

        # Determine rate limit rule
        endpoint = self.get_endpoint(request)
        if endpoint in self.LIMITS:
            limit_config = self.LIMITS[endpoint]

            # Get rate limit key
            key = self.get_rate_limit_key(request, limit_config['key'])

            # Check rate limit
            if not self.check_rate_limit(key, limit_config):
                # Calculate retry-after time
                retry_after = self.get_retry_after(key, limit_config)

                return JsonResponse(
                    {
                        'error': 'Rate limit exceeded',
                        'retry_after': retry_after
                    },
                    status=429,
                    headers={
                        'Retry-After': str(retry_after),
                        'X-RateLimit-Limit': str(limit_config['requests']),
                        'X-RateLimit-Remaining': '0',
                        'X-RateLimit-Reset': str(int(time.time() + retry_after))
                    }
                )

            # Increment counter
            self.increment_counter(key, limit_config)

            # Add rate limit headers to response
            response = self.get_response(request)
            self.add_rate_limit_headers(response, key, limit_config)
            return response

        return self.get_response(request)

    def check_rate_limit(self, key: str, config: dict) -> bool:
        """Check if request is within rate limit.

        Args:
            key: Rate limit key
            config: Rate limit configuration

        Returns:
            True if within limit, False if exceeded
        """
        count = cache.get(key, 0)
        return count < config['requests']

    def increment_counter(self, key: str, config: dict) -> None:
        """Increment rate limit counter.

        Args:
            key: Rate limit key
            config: Rate limit configuration
        """
        count = cache.get(key, 0)
        cache.set(key, count + 1, timeout=config['window'])

    def add_rate_limit_headers(self, response, key: str, config: dict) -> None:
        """Add rate limit headers to response.

        Args:
            response: HTTP response
            key: Rate limit key
            config: Rate limit configuration
        """
        count = cache.get(key, 0)
        remaining = max(0, config['requests'] - count)

        response['X-RateLimit-Limit'] = str(config['requests'])
        response['X-RateLimit-Remaining'] = str(remaining)
        response['X-RateLimit-Reset'] = str(
            int(time.time() + config['window'])
        )
```

### 5.2 Lockout Mechanisms

**Planned Implementation:**

- Failed login attempts tracked
- Account lockout mentioned in rate limiting

**Analysis:**

Account lockout is mentioned but not fully implemented.

**Concerns:**

1. No dedicated lockout mechanism (only rate limiting)
2. No distinction between temporary rate limit and permanent lockout
3. No user notification when account is locked

**Recommendations:**

Implement dedicated account lockout:

```python
# Add to User model

class User(AbstractBaseUser, PermissionsMixin):
    # ... existing fields ...

    # Account lockout fields
    failed_login_attempts = models.IntegerField(default=0)
    locked_out_at = models.DateTimeField(null=True, blank=True)
    lockout_reason = models.CharField(max_length=255, blank=True)

    def is_locked_out(self) -> bool:
        """Check if account is currently locked out.

        Returns:
            True if account is locked, False otherwise
        """
        if not self.locked_out_at:
            return False

        # Check if lockout has expired (1 hour)
        lockout_duration = timedelta(hours=1)
        if timezone.now() > self.locked_out_at + lockout_duration:
            # Auto-unlock after 1 hour
            self.unlock_account()
            return False

        return True

    def increment_failed_login(self) -> None:
        """Increment failed login attempts and lock if threshold exceeded."""
        self.failed_login_attempts += 1
        self.save()

        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.lock_account('Too many failed login attempts')

    def lock_account(self, reason: str = '') -> None:
        """Lock account and send notification.

        Args:
            reason: Reason for lockout
        """
        self.locked_out_at = timezone.now()
        self.lockout_reason = reason
        self.save()

        # Send lockout notification email
        EmailService.send_account_locked_email(self)

        # Log audit event
        AuditService.log_event(
            action='account_locked',
            user=self,
            metadata={'reason': reason}
        )

    def unlock_account(self) -> None:
        """Unlock account and reset failed attempts."""
        self.failed_login_attempts = 0
        self.locked_out_at = None
        self.lockout_reason = ''
        self.save()

        # Log audit event
        AuditService.log_event(
            action='account_unlocked',
            user=self
        )

    def reset_failed_attempts(self) -> None:
        """Reset failed login attempts on successful login."""
        self.failed_login_attempts = 0
        self.save()
```

### 5.3 Unlock Procedures

**Planned Implementation:**

Not specified in the plan.

**Analysis:**

No unlock procedure is documented.

**Concerns:**

1. No self-service unlock mechanism
2. No admin unlock workflow
3. No automatic unlock after time period

**Recommendations:**

Implement tiered unlock procedures:

```python
# Self-service unlock via email

@strawberry.mutation
def request_account_unlock(self, email: str, captcha_token: str) -> bool:
    """Request account unlock email.

    Args:
        email: User email address
        captcha_token: CAPTCHA verification token

    Returns:
        Always returns True (prevents enumeration)
    """
    # Verify CAPTCHA
    if not CaptchaService.verify_token(captcha_token):
        return True

    try:
        user = User.objects.get(email=email)

        if user.is_locked_out():
            # Generate unlock token
            token = secrets.token_urlsafe(32)
            token_hash = hashlib.sha256(token.encode()).hexdigest()

            # Create unlock token
            UnlockToken.objects.create(
                user=user,
                token=token_hash,
                expires_at=timezone.now() + timedelta(hours=1)
            )

            # Send unlock email
            EmailService.send_account_unlock_email(user, token)

    except User.DoesNotExist:
        pass

    return True


# Admin unlock via Django Admin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # ... existing configuration ...

    actions = ['unlock_selected_accounts']

    def unlock_selected_accounts(self, request, queryset):
        """Admin action to unlock selected user accounts."""
        for user in queryset:
            if user.is_locked_out():
                user.unlock_account()

                # Send notification to user
                EmailService.send_account_unlocked_by_admin_email(user)

        self.message_user(
            request,
            f'{queryset.count()} accounts have been unlocked.'
        )

    unlock_selected_accounts.short_description = 'Unlock selected accounts'
```

### 5.4 Distributed Rate Limiting

**Planned Implementation:**

Redis mentioned for rate limiting storage.

**Analysis:**

Redis is appropriate for distributed rate limiting but implementation details are sparse.

**Strengths:**

- Redis backend for shared state across servers
- Fast in-memory operations

**Concerns:**

1. No specification of Redis cluster configuration
2. No fallback if Redis is unavailable
3. No rate limit synchronisation strategy

**Recommendations:**

Implement robust distributed rate limiting:

```python
# apps/core/services/rate_limit_service.py

import redis
from django.conf import settings

class RateLimitService:
    """Distributed rate limiting service using Redis."""

    def __init__(self):
        """Initialise Redis connection with cluster support."""
        self.redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD,
            db=settings.REDIS_RATE_LIMIT_DB,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
            retry_on_timeout=True
        )

    def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window: int
    ) -> tuple[bool, int]:
        """Check rate limit using sliding window algorithm.

        Args:
            key: Rate limit key
            max_requests: Maximum requests allowed
            window: Time window in seconds

        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        try:
            # Use Lua script for atomic operations
            lua_script = """
            local key = KEYS[1]
            local max_requests = tonumber(ARGV[1])
            local window = tonumber(ARGV[2])
            local now = tonumber(ARGV[3])

            -- Remove old entries outside window
            redis.call('ZREMRANGEBYSCORE', key, 0, now - window)

            -- Count current requests
            local count = redis.call('ZCARD', key)

            if count < max_requests then
                -- Add current request
                redis.call('ZADD', key, now, now)
                redis.call('EXPIRE', key, window)
                return {1, max_requests - count - 1}
            else
                return {0, 0}
            end
            """

            now = int(time.time())
            result = self.redis_client.eval(
                lua_script,
                1,
                key,
                max_requests,
                window,
                now
            )

            is_allowed = bool(result[0])
            remaining = int(result[1])

            return (is_allowed, remaining)

        except redis.RedisError as e:
            # If Redis is unavailable, allow request but log error
            logger.error(f'Redis rate limit error: {e}')
            # Fail open (allow request)
            return (True, max_requests)
```

### Security Rating: Account Lockout and Rate Limiting

**Rating**: 6.5/10 (Adequate)

**Justification:**

- Good rate limiting strategy defined
- Missing account lockout implementation (-1.5)
- No unlock procedures specified (-1.0)
- Basic Redis usage without distributed considerations (-1.0)

---

## 6. Permission System

### 6.1 RBAC Implementation

**Planned Implementation:**

- Django Groups for role-based access control
- Three-tier hierarchy: Platform → Organisation → Website
- Custom permissions in model Meta classes

**Analysis:**

RBAC implementation leverages Django's built-in system effectively.

**Strengths:**

- Established Django permissions framework
- Clear permission hierarchy
- Extensible for future needs

**Concerns:**

1. Website-level permissions deferred to future phase
2. No permission inheritance documentation
3. Role assignment on user creation is basic

**Recommendations:**

No critical changes needed for Phase 1. Current implementation is appropriate.

### 6.2 Django Groups Usage

**Planned Implementation:**

- Platform Admin, Platform Support (platform level)
- Organisation Owner, Admin, Member, Viewer (organisation level)
- Website Admin, Editor, Viewer (future)

**Analysis:**

Group structure is well-designed for multi-tenancy.

**Strengths:**

- Clear group hierarchy
- Role names are intuitive
- Supports future expansion

**Concerns:**

1. No migration script to create default groups
2. Group assignment logic could be more sophisticated

**Recommendations:**

```python
# apps/core/management/commands/create_default_groups.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    """Create default permission groups."""

    help = 'Create default permission groups for RBAC'

    def handle(self, *args, **options):
        # Platform level groups
        self.create_platform_groups()

        # Organisation level groups
        self.create_organisation_groups()

        self.stdout.write(
            self.style.SUCCESS('Default groups created successfully')
        )

    def create_platform_groups(self):
        """Create platform-level permission groups."""
        # Platform Admin (superuser-like)
        platform_admin, _ = Group.objects.get_or_create(
            name='Platform Admin'
        )
        # Grant all permissions
        platform_admin.permissions.set(Permission.objects.all())

        # Platform Support (read-only cross-org)
        platform_support, _ = Group.objects.get_or_create(
            name='Platform Support'
        )
        view_permissions = Permission.objects.filter(
            codename__startswith='view_'
        )
        platform_support.permissions.set(view_permissions)

    def create_organisation_groups(self):
        """Create organisation-level permission groups."""
        # Organisation Owner
        org_owner, _ = Group.objects.get_or_create(
            name='Organisation Owner'
        )
        owner_permissions = Permission.objects.filter(
            content_type__app_label__in=['core', 'cms', 'design']
        )
        org_owner.permissions.set(owner_permissions)

        # Organisation Admin
        org_admin, _ = Group.objects.get_or_create(
            name='Organisation Admin'
        )
        admin_permissions = Permission.objects.filter(
            content_type__app_label__in=['core', 'cms', 'design']
        ).exclude(
            codename__in=['delete_organisation', 'delete_user']
        )
        org_admin.permissions.set(admin_permissions)

        # Organisation Member
        org_member, _ = Group.objects.get_or_create(
            name='Organisation Member'
        )
        member_permissions = Permission.objects.filter(
            codename__in=[
                'add_page', 'change_page', 'view_page',
                'add_media', 'view_media',
                'view_organisation', 'view_user',
            ]
        )
        org_member.permissions.set(member_permissions)

        # Organisation Viewer
        org_viewer, _ = Group.objects.get_or_create(
            name='Organisation Viewer'
        )
        viewer_permissions = Permission.objects.filter(
            codename__startswith='view_',
            content_type__app_label__in=['core', 'cms', 'design']
        )
        org_viewer.permissions.set(viewer_permissions)
```

### 6.3 Organisation Boundaries

**Planned Implementation:**

- Organisation foreign key on User model
- Queries filtered by organisation
- GraphQL resolvers enforce boundaries

**Analysis:**

Organisation boundary enforcement is comprehensive.

**Strengths:**

- All queries filtered by organisation
- Database-level foreign keys
- GraphQL resolver checks

**Concerns:**

1. No database row-level security (PostgreSQL RLS)
2. Reliance on application-level enforcement
3. No mention of organisation switching for multi-org users (future consideration)

**Recommendations:**

Consider PostgreSQL Row-Level Security for defence-in-depth:

```sql
-- Enable RLS on sensitive tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE pages ENABLE ROW LEVEL SECURITY;

-- Create policy for organisation isolation
CREATE POLICY org_isolation ON users
    USING (organisation_id = current_setting('app.current_organisation_id')::uuid);

CREATE POLICY org_isolation ON audit_logs
    USING (organisation_id = current_setting('app.current_organisation_id')::uuid);

CREATE POLICY org_isolation ON pages
    USING (organisation_id = current_setting('app.current_organisation_id')::uuid);
```

```python
# Set organisation context in Django middleware

class OrganisationContextMiddleware:
    """Set PostgreSQL session variable for RLS."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SET app.current_organisation_id = %s",
                    [str(request.user.organisation_id)]
                )

        response = self.get_response(request)
        return response
```

### 6.4 Permission Checking Patterns

**Planned Implementation:**

- `user.has_perm()` checks in resolvers
- Strawberry permission classes
- Organisation boundary checks in queries

**Analysis:**

Permission checking is applied at multiple layers.

**Strengths:**

- Multiple permission checking methods
- Explicit permission decorators
- Organisation boundary enforcement

**Concerns:**

1. Inconsistent permission checking across mutations
2. Some examples check permissions, others don't
3. No centralised permission checking utility

**Recommendations:**

Create centralised permission checking:

```python
# api/permissions.py

from functools import wraps
from strawberry.types import Info

def require_permission(permission: str):
    """Decorator to require specific permission.

    Args:
        permission: Django permission string (e.g., 'cms.publish_page')

    Returns:
        Decorated function that checks permission before execution
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, info: Info, **kwargs):
            user = info.context.request.user

            if not user.is_authenticated:
                raise PermissionError('Authentication required')

            if not user.has_perm(permission):
                raise PermissionError(
                    f'Permission required: {permission}'
                )

            return func(*args, info=info, **kwargs)

        return wrapper
    return decorator


def require_organisation_owner(func):
    """Decorator to require organisation owner role.

    Args:
        func: Function to decorate

    Returns:
        Decorated function that checks ownership before execution
    """
    @wraps(func)
    def wrapper(*args, info: Info, **kwargs):
        user = info.context.request.user

        if not user.is_authenticated:
            raise PermissionError('Authentication required')

        if not user.groups.filter(name='Organisation Owner').exists():
            raise PermissionError('Organisation owner permission required')

        return func(*args, info=info, **kwargs)

    return wrapper


# Usage in GraphQL mutations

@strawberry.mutation
@require_permission('cms.publish_page')
def publish_page(self, info: Info, page_id: strawberry.ID) -> Page:
    """Publish a page (requires cms.publish_page permission)."""
    user = info.context.request.user
    page = Page.objects.get(id=page_id)

    # Check organisation boundary
    if page.organisation != user.organisation:
        raise PermissionError('Cannot publish pages from other organisations')

    page.published = True
    page.save()

    return page
```

### Security Rating: Permission System

**Rating**: 8.0/10 (Very Good)

**Justification:**

- Django Groups provide solid RBAC foundation
- Organisation boundaries well-enforced
- Missing database row-level security (-1.0)
- Permission checking could be more consistent (-1.0)

---

## 7. Security Headers and Configuration

### 7.1 CORS Configuration

**Planned Implementation:**

- CORS settings mentioned in security section
- "Configure CORS settings" in Phase 6

**Analysis:**

CORS is mentioned but not configured.

**Concerns:**

1. No CORS middleware configuration specified
2. No allowed origins documented
3. No credentials policy defined

**Recommendations:**

```python
# config/settings/base.py

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    'https://app.example.com',  # Web frontend
    'https://www.example.com',  # Marketing site
]

# For development
if DEBUG:
    CORS_ALLOWED_ORIGINS += [
        'http://localhost:3000',
        'http://localhost:3001',
    ]

CORS_ALLOW_CREDENTIALS = True  # Allow cookies for authentication

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# Don't allow all origins in production
CORS_ALLOW_ALL_ORIGINS = False

# Expose custom headers
CORS_EXPOSE_HEADERS = [
    'x-ratelimit-limit',
    'x-ratelimit-remaining',
    'x-ratelimit-reset',
]
```

### 7.2 Security Middleware

**Planned Implementation:**

- "Add security headers middleware" in Phase 6
- Rate limiting middleware specified

**Analysis:**

Security middleware is planned but not configured.

**Concerns:**

1. No Django security middleware configuration
2. Missing security headers (CSP, HSTS, X-Frame-Options)
3. No HTTPS enforcement configuration

**Recommendations:**

```python
# config/settings/base.py

# Security Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Must be first
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.core.middleware.rate_limit.RateLimitMiddleware',
    'apps.core.middleware.audit.AuditMiddleware',
    'apps.core.middleware.organisation.OrganisationContextMiddleware',
]

# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS Configuration (production only)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Content Security Policy
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")  # Minimise unsafe-inline in production
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", 'data:', 'https:')
CSP_FONT_SRC = ("'self'", 'https:', 'data:')
CSP_CONNECT_SRC = ("'self'",)
CSP_FRAME_ANCESTORS = ("'none'",)
CSP_BASE_URI = ("'self'",)
CSP_FORM_ACTION = ("'self'",)

# Session Security
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_NAME = 'sessionid'  # Don't reveal framework

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_NAME = 'csrftoken'

# Additional Security Settings
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
```

### 7.3 IP Encryption

**Planned Implementation:**

- Fernet symmetric encryption
- IP addresses encrypted before storage
- Encryption key in environment variables

**Analysis:**

IP encryption is well-designed for privacy compliance.

**Strengths:**

- Fernet encryption (NIST-approved)
- All IP addresses encrypted
- Key management via environment variables

**Concerns:**

1. No key rotation strategy specified
2. No key versioning for re-encryption
3. Single encryption key (no key hierarchy)

**Recommendations:**

Implement key rotation:

```python
# apps/core/utils/encryption.py

from cryptography.fernet import Fernet, MultiFernet
from django.conf import settings

class IPEncryption:
    """Utility for encrypting and decrypting IP addresses with key rotation."""

    @staticmethod
    def get_ciphers():
        """Get Fernet cipher suite with key rotation support.

        Returns:
            MultiFernet instance supporting multiple keys
        """
        keys = [
            settings.IP_ENCRYPTION_KEY_CURRENT,
            settings.IP_ENCRYPTION_KEY_OLD,  # For rotation
        ]

        # Remove None values
        keys = [key for key in keys if key]

        # Create Fernet instances
        fernets = [Fernet(key) for key in keys]

        return MultiFernet(fernets)

    @staticmethod
    def encrypt_ip(ip_address: str) -> bytes:
        """Encrypt an IP address with current key.

        Args:
            ip_address: The IP address to encrypt.

        Returns:
            Encrypted IP address as bytes.
        """
        cipher = Fernet(settings.IP_ENCRYPTION_KEY_CURRENT)
        return cipher.encrypt(ip_address.encode())

    @staticmethod
    def decrypt_ip(encrypted_ip: bytes) -> str:
        """Decrypt an IP address using any valid key.

        Supports decryption with old keys during rotation.

        Args:
            encrypted_ip: The encrypted IP address.

        Returns:
            Decrypted IP address as string.
        """
        cipher = IPEncryption.get_ciphers()
        return cipher.decrypt(encrypted_ip).decode()

    @staticmethod
    def rotate_key(old_key: str, new_key: str) -> int:
        """Rotate encryption key for all stored IP addresses.

        Args:
            old_key: Previous encryption key
            new_key: New encryption key

        Returns:
            Number of records re-encrypted
        """
        from apps.core.models import AuditLog, SessionToken

        old_cipher = Fernet(old_key)
        new_cipher = Fernet(new_key)

        count = 0

        # Re-encrypt audit logs
        for log in AuditLog.objects.all():
            try:
                # Decrypt with old key
                ip = old_cipher.decrypt(log.ip_address).decode()
                # Encrypt with new key
                log.ip_address = new_cipher.encrypt(ip.encode())
                log.save()
                count += 1
            except Exception as e:
                logger.error(f'Failed to rotate key for audit log {log.id}: {e}')

        # Re-encrypt session tokens
        for session in SessionToken.objects.all():
            try:
                ip = old_cipher.decrypt(session.ip_address).decode()
                session.ip_address = new_cipher.encrypt(ip.encode())
                session.save()
                count += 1
            except Exception as e:
                logger.error(f'Failed to rotate key for session {session.id}: {e}')

        return count
```

### 7.4 Audit Logging

**Planned Implementation:**

- Immutable audit log
- All authentication events logged
- IP addresses encrypted
- Metadata in JSON field

**Analysis:**

Audit logging is comprehensive and well-designed.

**Strengths:**

- Immutable logs (read-only in admin)
- Comprehensive event coverage
- IP encryption for privacy
- Flexible metadata field

**Concerns:**

1. No log retention policy specified
2. No log archival strategy
3. No log integrity verification (hashing)

**Recommendations:**

Enhance audit log integrity:

```python
# apps/core/models/audit_log.py

import hashlib
import json

class AuditLog(models.Model):
    # ... existing fields ...

    # Add integrity field
    log_hash = models.CharField(max_length=64, editable=False)
    previous_hash = models.CharField(max_length=64, blank=True)

    def save(self, *args, **kwargs):
        """Save audit log with integrity hash."""
        if not self.log_hash:
            # Get previous log hash
            previous_log = AuditLog.objects.order_by('-created_at').first()
            if previous_log:
                self.previous_hash = previous_log.log_hash

            # Calculate hash of this log
            log_data = {
                'user_id': str(self.user_id) if self.user_id else None,
                'organisation_id': str(self.organisation_id) if self.organisation_id else None,
                'action': self.action,
                'ip_address': self.ip_address.hex() if self.ip_address else '',
                'metadata': json.dumps(self.metadata, sort_keys=True),
                'previous_hash': self.previous_hash,
                'created_at': str(self.created_at),
            }

            log_string = json.dumps(log_data, sort_keys=True)
            self.log_hash = hashlib.sha256(log_string.encode()).hexdigest()

        super().save(*args, **kwargs)

    @classmethod
    def verify_integrity(cls) -> tuple[bool, list]:
        """Verify integrity of entire audit log chain.

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        previous_hash = ''

        for log in cls.objects.order_by('created_at'):
            # Check previous hash matches
            if log.previous_hash != previous_hash:
                issues.append(
                    f'Log {log.id}: Previous hash mismatch'
                )

            previous_hash = log.log_hash

        is_valid = len(issues) == 0
        return (is_valid, issues)


# Add management command for log archival

# apps/core/management/commands/archive_audit_logs.py

class Command(BaseCommand):
    """Archive old audit logs to cold storage."""

    help = 'Archive audit logs older than 90 days'

    def handle(self, *args, **options):
        cutoff_date = timezone.now() - timedelta(days=90)

        old_logs = AuditLog.objects.filter(created_at__lt=cutoff_date)

        # Export to JSON file
        archive_file = f'audit_logs_{cutoff_date.strftime("%Y%m%d")}.json'

        with open(archive_file, 'w') as f:
            data = list(old_logs.values())
            json.dump(data, f, default=str, indent=2)

        count = old_logs.count()

        # Delete archived logs (optional)
        # old_logs.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Archived {count} audit logs to {archive_file}'
            )
        )
```

### Security Rating: Security Headers and Configuration

**Rating**: 5.5/10 (Adequate)

**Justification:**

- CORS not configured (-1.5)
- Security headers missing (-1.5)
- IP encryption well-designed (+1.0)
- Audit logging comprehensive (+0.5)
- Missing key rotation strategy (-1.0)

---

## 8. Recommendations

### 8.1 Critical Priority (Must Implement)

**Priority**: P0 (Blocking for production)

1. **Implement Password Breach Checking**
   - Integrate Have I Been Pwned API
   - Check passwords on registration and change
   - Estimated effort: 4 hours

2. **Configure Security Headers**
   - HSTS, CSP, X-Frame-Options
   - HTTPS enforcement in production
   - Estimated effort: 2 hours

3. **Implement Account Lockout**
   - Dedicated lockout mechanism (separate from rate limiting)
   - User notification on lockout
   - Self-service unlock flow
   - Estimated effort: 8 hours

4. **Configure CORS Properly**
   - Define allowed origins
   - Set credentials policy
   - Test cross-origin requests
   - Estimated effort: 2 hours

5. **Add Concurrent Session Limits**
   - Enforce 5 session maximum
   - Automatic oldest session revocation
   - User session management UI
   - Estimated effort: 6 hours

### 8.2 High Priority (Should Implement)

**Priority**: P1 (Required for security best practices)

1. **Implement Password History**
   - PasswordHistory model
   - Check last 5 passwords on change
   - Cleanup old history entries
   - Estimated effort: 4 hours

2. **Add CAPTCHA to Public Endpoints**
   - Registration
   - Password reset
   - Account unlock
   - Estimated effort: 3 hours

3. **Implement Refresh Token Rotation**
   - Rotation on each refresh
   - Token reuse detection
   - Family invalidation
   - Estimated effort: 6 hours

4. **Add Device Anomaly Detection**
   - Track login locations
   - Detect unusual activity
   - Email notifications
   - Estimated effort: 8 hours

5. **Implement Key Rotation for IP Encryption**
   - Key versioning
   - Re-encryption script
   - Quarterly rotation schedule
   - Estimated effort: 4 hours

### 8.3 Medium Priority (Consider Implementing)

**Priority**: P2 (Enhanced security)

1. **Add Password Strength Meter**
   - Client-side strength indicator
   - Real-time feedback
   - Estimated effort: 4 hours

2. **Implement PostgreSQL Row-Level Security**
   - Database-level organisation isolation
   - Defence-in-depth
   - Estimated effort: 6 hours

3. **Add Audit Log Integrity Verification**
   - Hash chaining
   - Periodic integrity checks
   - Estimated effort: 5 hours

4. **Implement Trusted IP Bypass**
   - Corporate network exclusions
   - Rate limit bypass for trusted IPs
   - Estimated effort: 3 hours

5. **Add 2FA Recovery Workflow**
   - Support ticket recovery
   - Identity verification
   - Admin override with audit
   - Estimated effort: 8 hours

### 8.4 Low Priority (Nice to Have)

**Priority**: P3 (Future enhancements)

1. **Add Biometric Authentication Support**
   - WebAuthn integration
   - Fingerprint/Face ID
   - Estimated effort: 16 hours

2. **Implement Risk-Based Authentication**
   - Adaptive MFA based on risk score
   - Behaviour analysis
   - Estimated effort: 24 hours

3. **Add Login Notification System**
   - Email on new device
   - SMS alerts (optional)
   - Estimated effort: 4 hours

4. **Implement Hardware Security Keys**
   - FIDO2 support
   - YubiKey integration
   - Estimated effort: 12 hours

5. **Add Security Dashboard**
   - User security score
   - Recent activity
   - Security recommendations
   - Estimated effort: 16 hours

---

## 9. Security Best Practice Alignment

### OWASP Authentication Guidelines

| OWASP Requirement                  | Status      | Notes                                           |
| ---------------------------------- | ----------- | ----------------------------------------------- |
| Strong password requirements       | Implemented | 12-character minimum with complexity            |
| Secure password storage            | Implemented | Argon2 hashing                                  |
| Multi-factor authentication        | Implemented | TOTP-based                                      |
| Account lockout                    | Partial     | Rate limiting present, dedicated lockout needed |
| Password reset security            | Implemented | 15-minute tokens, single-use                    |
| Session management                 | Implemented | JWT with expiration                             |
| HTTPS enforcement                  | Partial     | Planned but not configured                      |
| Security headers                   | Missing     | Not configured                                  |
| CSRF protection                    | Implemented | Django CSRF middleware                          |
| Rate limiting                      | Implemented | Multiple endpoints covered                      |
| Breach password checking           | Missing     | Not implemented                                 |
| Password history                   | Partial     | Mentioned but not implemented                   |
| Anti-enumeration                   | Implemented | Generic error messages                          |
| Audit logging                      | Implemented | Comprehensive coverage                          |
| Input validation                   | Implemented | Django validators                               |
| Secure token generation            | Implemented | Cryptographically secure random                 |
| Token expiration                   | Implemented | Appropriate timeouts                            |
| Remember me functionality          | Implemented | 30-day refresh tokens                           |
| Concurrent session limits          | Missing     | Decided but not implemented                     |
| Device tracking                    | Implemented | IP and user agent captured                      |
| Anomaly detection                  | Missing     | Not implemented                                 |
| **Overall OWASP Compliance Score** | **75%**     | Good foundation, critical gaps remain           |

### NIST Digital Identity Guidelines

| NIST SP 800-63B Requirement            | Status      | Notes                                             |
| -------------------------------------- | ----------- | ------------------------------------------------- |
| Minimum 8-character password           | Exceeded    | 12-character minimum                              |
| Maximum 64-character password          | Exceeded    | 128-character maximum                             |
| All ASCII and Unicode supported        | Implemented | No character restrictions beyond requirements     |
| No composition rules enforced          | Non-Conform | Complexity rules enforced (uppercase, numbers)    |
| Breach password checking               | Missing     | Recommended but not implemented                   |
| Password strength meter                | Missing     | Not implemented                                   |
| MFA required for privileged users      | Implemented | Optional for all, can be enforced per role        |
| TOTP preferred over SMS                | Implemented | TOTP-based 2FA                                    |
| Rate limiting on authentication        | Implemented | 5 attempts per 15 minutes                         |
| Session timeout                        | Implemented | 24-hour inactivity timeout                        |
| Reauthentication for sensitive actions | Missing     | Not specified                                     |
| **Overall NIST Compliance Score**      | **70%**     | Good but password composition rules non-compliant |

### GDPR Compliance

| GDPR Requirement                  | Status      | Notes                                      |
| --------------------------------- | ----------- | ------------------------------------------ |
| Data minimisation                 | Implemented | Only necessary data collected              |
| Purpose limitation                | Implemented | Audit logs for security only               |
| Storage limitation                | Partial     | No retention policy specified              |
| Right to access                   | Missing     | User data export not implemented           |
| Right to rectification            | Implemented | Users can update profile                   |
| Right to erasure                  | Planned     | User deletion planned                      |
| Right to data portability         | Missing     | No export functionality                    |
| Security of processing            | Implemented | Encryption, hashing, audit logs            |
| Data protection by design         | Implemented | Multi-tenancy, IP encryption               |
| Data breach notification          | Missing     | No breach detection/notification system    |
| Privacy by default                | Implemented | Email verification, optional 2FA           |
| Lawful basis for processing       | N/A         | Legitimate interest (security)             |
| **Overall GDPR Compliance Score** | **65%**     | Security measures strong, user rights gaps |

---

## 10. Risk Assessment

| Risk                                | Likelihood | Impact | Current Mitigation                   | Residual Risk | Recommendation                              |
| ----------------------------------- | ---------- | ------ | ------------------------------------ | ------------- | ------------------------------------------- |
| Brute force password attack         | High       | High   | Rate limiting (5/15min)              | Low           | Add account lockout for additional layer    |
| Credential stuffing                 | High       | High   | None (breach checking missing)       | High          | **Implement breach checking (P0)**          |
| Session hijacking                   | Medium     | High   | JWT expiration, HTTPS planned        | Medium        | **Configure HTTPS and secure cookies (P0)** |
| 2FA bypass                          | Low        | High   | TOTP verification, backup codes      | Low           | Add device management, recovery flow        |
| Account takeover via password reset | Medium     | High   | 15-min expiration, single-use tokens | Low           | Add CAPTCHA to prevent automation (P1)      |
| Cross-site scripting (XSS)          | Medium     | Medium | Django auto-escaping                 | Medium        | **Add CSP headers (P0)**                    |
| Cross-site request forgery (CSRF)   | Low        | High   | Django CSRF protection               | Low           | Ensure CSRF for all mutations               |
| SQL injection                       | Low        | High   | Django ORM, parameterised queries    | Very Low      | Continue using ORM, avoid raw SQL           |
| Multi-tenancy data leak             | Low        | High   | Organisation boundaries enforced     | Low           | Consider PostgreSQL RLS (P2)                |
| Audit log tampering                 | Low        | High   | Immutable logs, admin read-only      | Medium        | Add hash chaining for integrity (P2)        |
| IP encryption key compromise        | Low        | High   | Environment variables                | Medium        | **Implement key rotation (P1)**             |
| Concurrent session abuse            | Medium     | Medium | None (limit not enforced)            | Medium        | **Enforce 5 session limit (P0)**            |
| Device fingerprint evasion          | Medium     | Low    | Basic user agent tracking            | Medium        | Add device anomaly detection (P1)           |
| Social engineering (password reset) | Medium     | High   | Email delivery, generic messages     | Medium        | Add additional verification (P2)            |
| Insider threat (admin access)       | Low        | High   | Audit logging, permissions           | Low           | Regular access reviews, MFA for admins      |
| Denial of service (DoS)             | High       | Medium | Rate limiting, Redis caching         | Medium        | Add DDoS protection at infrastructure       |
| Man-in-the-middle (MITM)            | Medium     | High   | HTTPS planned                        | Medium        | **Enforce HTTPS with HSTS (P0)**            |
| Token theft via XSS                 | Low        | High   | HttpOnly cookies planned             | Low           | **Configure secure session cookies (P0)**   |
| Refresh token reuse attack          | Medium     | High   | Rotation mentioned, not implemented  | High          | **Implement token rotation detection (P1)** |
| Phishing (credential capture)       | High       | High   | User education (out of scope)        | High          | Add login notifications, device tracking    |
| Account enumeration                 | Medium     | Low    | Generic error messages               | Low           | Ensure consistency across all endpoints     |
| **Overall Risk Level**              | **Medium** | -      | -                                    | **Medium**    | Implement P0 and P1 recommendations         |

---

## 11. Implementation Checklist

### Before Development

- [ ] Review and approve this security review document
- [ ] Prioritise P0 (critical) recommendations
- [ ] Allocate resources for security enhancements
- [ ] Set up security testing environment

### Phase 1: Core Models (Current)

- [ ] Add PasswordHistory model
- [ ] Add BackupCode model for 2FA
- [ ] Add account lockout fields to User model
- [ ] Create default permission groups migration

### Phase 2: Authentication Service (Current)

- [ ] Implement password breach checking service
- [ ] Implement password history checking
- [ ] Configure Argon2 parameters
- [ ] Implement account lockout logic
- [ ] Add backup code generation and verification

### Phase 3: GraphQL API (Current)

- [ ] Add CAPTCHA verification to public mutations
- [ ] Implement concurrent session limit enforcement
- [ ] Add device management mutations
- [ ] Ensure consistent anti-enumeration
- [ ] Add rate limit headers to responses

### Phase 4: Two-Factor Authentication (Current)

- [ ] Implement TOTP with SHA-256
- [ ] Add time window tolerance for clock skew
- [ ] Implement 2FA recovery workflow
- [ ] Add device management operations
- [ ] Implement backup code verification

### Phase 5: Password Reset and Email (Current)

- [ ] Add CAPTCHA to password reset request
- [ ] Implement account unlock via email
- [ ] Add unverified user cleanup job
- [ ] Configure email rate limiting

### Phase 6: Audit Logging and Security (Current)

- [ ] Configure CORS with specific origins
- [ ] Add security headers (HSTS, CSP, X-Frame-Options)
- [ ] Implement IP encryption key rotation
- [ ] Add audit log integrity hashing
- [ ] Configure HTTPS enforcement in production

### Phase 7: Testing (Current)

- [ ] Security penetration testing
- [ ] Rate limiting stress tests
- [ ] Session management tests
- [ ] 2FA flow testing
- [ ] CAPTCHA integration tests
- [ ] CORS and security header validation

### Post-Implementation

- [ ] Security audit by external firm
- [ ] Compliance review (GDPR, OWASP, NIST)
- [ ] Documentation updates
- [ ] User security documentation
- [ ] Incident response plan
- [ ] Key rotation schedule

---

## 12. Conclusion

The User Authentication System implementation plan demonstrates a strong security foundation with
comprehensive coverage of authentication, authorisation, and audit logging. The plan incorporates
industry best practices including Argon2 password hashing, TOTP-based multi-factor authentication,
JWT token management, and detailed audit logging.

**Key Achievements:**

- Strong password requirements exceeding industry standards
- Modern password hashing with Argon2
- TOTP-based 2FA implementation
- Comprehensive audit logging with IP encryption
- Multi-tenancy with organisation boundaries
- Rate limiting across authentication endpoints

**Critical Gaps Requiring Attention:**

1. Password breach checking integration (P0)
2. Security headers configuration (P0)
3. Dedicated account lockout mechanism (P0)
4. CORS configuration (P0)
5. Concurrent session limits (P0)

**Overall Assessment:**

The plan is **approved for implementation** with the requirement that all P0 (critical priority)
recommendations be implemented before production deployment. The P1 (high priority) recommendations
should be implemented in Phase 6 or shortly after initial release.

**Compliance Summary:**

- OWASP Authentication: 75% compliant (Good)
- NIST Digital Identity: 70% compliant (Good, minor non-conformance on password rules)
- GDPR: 65% compliant (Adequate, user rights gaps)

**Estimated Effort for Critical Recommendations:**

- P0 (Critical): 22 hours
- P1 (High): 29 hours
- P2 (Medium): 26 hours
- Total: 77 hours (approximately 2 weeks of dedicated security work)

**Risk Level:**

- Pre-Implementation: High
- Post-Implementation (with P0): Medium-Low
- Post-Implementation (with P0 + P1): Low

**Final Recommendation:**

Proceed with implementation following the phased approach outlined in the plan. Allocate dedicated
time for security enhancements (P0 and P1 recommendations) during Phase 6 before production
deployment. Schedule external security audit after Phase 7 completion.

---

**Reviewer**: Authentication Security Agent
**Approval Date**: 07/01/2026
**Next Review**: After Phase 6 completion
