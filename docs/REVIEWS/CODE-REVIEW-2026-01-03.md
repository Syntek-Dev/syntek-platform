# Code Review Report

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

**Date:** 3 January 2026
**Reviewer:** Syntek Code Review Agent
**Scope:** Full codebase analysis
**Status:** Active findings requiring attention

## Table of Contents

- [Code Review Report](#code-review-report)
  - [Table of Contents](#table-of-contents)
  - [Executive Summary](#executive-summary)
  - [Critical Issues](#critical-issues)
    - [MD5 Cache Key Vulnerability](#md5-cache-key-vulnerability)
      - [Problem](#problem)
      - [Solution](#solution)
    - [IP Spoofing via X-Forwarded-For](#ip-spoofing-via-x-forwarded-for)
      - [Problem](#problem-1)
      - [Solution](#solution-1)
    - [DRY Violation in IP Extraction](#dry-violation-in-ip-extraction)
      - [Problem](#problem-2)
      - [Solution](#solution-2)
  - [Warnings](#warnings)
    - [W1: ALLOWED\_HOSTS Wildcard in Staging](#w1-allowed_hosts-wildcard-in-staging)
    - [W2: Missing Rate Limit Headers](#w2-missing-rate-limit-headers)
    - [W3: Naive GraphQL Complexity Calculation](#w3-naive-graphql-complexity-calculation)
    - [W4: Missing Password Validator Tests](#w4-missing-password-validator-tests)
    - [W5: Cache TTL Reset Issue](#w5-cache-ttl-reset-issue)
    - [W6: Sentry Missing Performance Monitoring](#w6-sentry-missing-performance-monitoring)
    - [W7: Missing CSRF Token in GraphQL Mutations](#w7-missing-csrf-token-in-graphql-mutations)
    - [W8: Incomplete Error Message Sanitisation](#w8-incomplete-error-message-sanitisation)
  - [Suggestions](#suggestions)
    - [S1: Refactor RateLimitMiddleware](#s1-refactor-ratelimitmiddleware)
    - [S2: Extract Logging Configuration](#s2-extract-logging-configuration)
    - [S3: Replace Magic Numbers](#s3-replace-magic-numbers)
    - [S4: Add Database Indexes](#s4-add-database-indexes)
    - [S5: Document Security Assumptions](#s5-document-security-assumptions)
    - [S6: Add GraphQL Query Depth Limit](#s6-add-graphql-query-depth-limit)
  - [Positive Notes](#positive-notes)
    - [Excellent Password Validators](#excellent-password-validators)
    - [GraphQL Security Extensions](#graphql-security-extensions)
    - [Comprehensive Audit Logging](#comprehensive-audit-logging)
    - [Environment-Specific Configuration](#environment-specific-configuration)
    - [Clear Documentation Standards](#clear-documentation-standards)
  - [Recommendations](#recommendations)
    - [Immediate Actions (This Sprint)](#immediate-actions-this-sprint)
    - [Next Sprint](#next-sprint)
    - [Ongoing](#ongoing)
  - [Next Steps](#next-steps)
    - [For Development Team](#for-development-team)
    - [For Team Lead](#for-team-lead)
    - [Related Documents](#related-documents)


---

## Executive Summary

The codebase demonstrates solid security foundations with comprehensive audit logging and
environment-specific configurations. However, three critical security issues must be addressed
before production deployment:

1. **Weak hashing for cache keys** - MD5 is cryptographically broken
2. **IP spoofing vulnerability** - Unsafe X-Forwarded-For header handling
3. **Code duplication** - IP extraction logic duplicated in 3 locations

Additionally, 8 warnings and 6 suggestions were identified for improvement.

**Risk Level:** MEDIUM (Critical issues block production deployment)
**Effort Estimate:** 8-16 hours to address all critical issues

---

## Critical Issues

### MD5 Cache Key Vulnerability

**File:** `config/cache/backend.py`
**Line:** 45
**Severity:** CRITICAL
**Risk:** Cryptographic weakness could allow cache poisoning attacks

#### Problem

The application uses MD5 hashing for cache keys, which is cryptographically broken:

```python
# CURRENT (INSECURE)
import hashlib

def generate_cache_key(identifier: str) -> str:
    """Generate cache key using MD5."""
    return hashlib.md5(identifier.encode()).hexdigest()
```

**Why This is Dangerous:**
- MD5 is broken and can be collided with negligible computing power
- Attackers could craft identifiers producing cache key collisions
- Leads to cache poisoning and serving wrong data to users
- Not suitable for any cryptographic purpose

#### Solution

Replace MD5 with SHA256:

```python
# FIXED (SECURE)
import hashlib

def generate_cache_key(identifier: str) -> str:
    """Generate cache key using SHA256.

    SHA256 provides strong cryptographic guarantees and prevents
    cache key collision attacks.

    Args:
        identifier: The cache key identifier.

    Returns:
        SHA256 hash of the identifier.
    """
    return hashlib.sha256(identifier.encode()).hexdigest()
```

**Alternative (Recommended for Django):**
```python
from django.core.cache.backends.base import KEY_FUNC

# Use Django's default key function which is secure
# Set in settings.py:
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'KEY_FUNCTION': KEY_FUNC,  # Uses secure hashing
    }
}
```

**Implementation:**
1. Replace all `hashlib.md5()` calls with `hashlib.sha256()`
2. Update cache key format if necessary (longer hash)
3. Clear all existing cache entries
4. Update tests to expect new hash format

**Timeline:** Immediate (before production)

---

### IP Spoofing via X-Forwarded-For

**File:** `config/middleware/audit.py`
**Lines:** 52-65
**Severity:** CRITICAL
**Risk:** Untrusted proxy headers could bypass IP-based security controls

#### Problem

The middleware blindly trusts the X-Forwarded-For header without validation:

```python
# CURRENT (UNSAFE)
def _get_client_ip(request) -> str:
    """Extract client IP from request headers."""
    # Trusts user-controlled header
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Takes first IP without validation
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR', 'unknown')
```

**Why This is Dangerous:**
- X-Forwarded-For is set by the client (not trusted)
- Attackers can spoof their IP address
- Could bypass IP-based rate limiting
- Could bypass IP-based geographic restrictions
- Could evade abuse detection systems

#### Solution

Only trust X-Forwarded-For from known proxies:

```python
# FIXED (SECURE)
from django.conf import settings
from typing import Optional

def _get_client_ip(request) -> str:
    """Extract client IP from trusted proxy headers only.

    Only trusts X-Forwarded-For if the request comes from a
    configured trusted proxy. This prevents IP spoofing attacks.

    Args:
        request: Django HTTP request object.

    Returns:
        Client IP address or 'unknown' if not available.
    """
    # Get the immediate sender IP
    client_ip = request.META.get('REMOTE_ADDR', 'unknown')

    # Only check X-Forwarded-For if behind a trusted proxy
    trusted_proxies = getattr(settings, 'TRUSTED_PROXIES', [])
    if client_ip in trusted_proxies:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            # Take the rightmost IP (closest to us)
            return x_forwarded_for.split(',')[-1].strip()

    return client_ip
```

**Django Best Practice:**

Use Django's built-in trusted proxy support:

```python
# In settings.py
TRUSTED_PROXIES = [
    '127.0.0.1',           # Local proxy
    '10.0.0.0/8',          # Internal VPC
    'reverse-proxy.local',  # Named proxy
]

# In middleware
from django.http import HttpRequest

def get_client_ip(request: HttpRequest) -> str:
    """Get client IP using Django's proxy handling."""
    # Django's REMOTE_ADDR already handles trusted proxies
    # if configured with TRUSTED_PROXIES
    return request.META.get('REMOTE_ADDR', 'unknown')
```

**Add to Django Settings:**

```python
# config/settings/base.py

# Configure trusted proxies based on deployment
if ENVIRONMENT == 'production':
    TRUSTED_PROXIES = [
        '10.0.0.0/8',      # AWS VPC
        '172.16.0.0/12',   # Private networks
    ]
else:
    TRUSTED_PROXIES = ['127.0.0.1', 'localhost']
```

**Implementation:**
1. Add TRUSTED_PROXIES to settings
2. Update IP extraction to validate proxy trust
3. Add tests for trusted/untrusted proxy scenarios
4. Document proxy configuration in deployment guide
5. Review all IP-based security controls

**Timeline:** IMMEDIATE - blocks production deployment

---

### DRY Violation in IP Extraction

**Files:**
- `config/middleware/audit.py:52` - `_get_client_ip()`
- `config/middleware/rate_limit.py:78` - duplicate function
- `api/security.py:45` - duplicate function

**Severity:** CRITICAL
**Risk:** Code duplication leads to inconsistent behavior and hard-to-maintain code

#### Problem

The `_get_client_ip()` function is implemented three separate times with slight variations:

```python
# audit.py - Version 1
def _get_client_ip(request) -> str:
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR', 'unknown')

# rate_limit.py - Version 2 (slightly different)
def get_client_ip(request) -> str:
    forwarded = request.META.get('X-Forwarded-For', '')
    if forwarded:
        return forwarded.split(';')[0]  # Note: different delimiter!
    return request.META.get('REMOTE_ADDR')

# api/security.py - Version 3
def _extract_client_ip(request) -> str:
    if 'HTTP_X_FORWARDED_FOR' in request.META:
        return request.META['HTTP_X_FORWARDED_FOR'].split(',')[0]
    elif 'HTTP_CLIENT_IP' in request.META:
        return request.META['HTTP_CLIENT_IP']
    return request.META.get('REMOTE_ADDR', '0.0.0.0')
```

**Consequences:**
- Different functions extract IP differently (inconsistent)
- Bug fixes only applied in one location
- Security improvements hard to implement consistently
- Maintenance nightmare

#### Solution

Create a single, centralised utility:

```python
# config/utils/request.py
"""Utilities for handling HTTP requests securely.

This module provides secure request utilities that properly handle
trusted proxies, client IP extraction, and header validation.
"""

from typing import Optional
from django.http import HttpRequest
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def get_client_ip(request: HttpRequest) -> str:
    """Extract client IP address from request, respecting trusted proxies.

    This is the authoritative function for client IP extraction. It properly
    handles X-Forwarded-For headers only from trusted proxies, preventing
    IP spoofing attacks.

    Args:
        request: Django HTTP request object.

    Returns:
        Client IP address as a string. Returns '0.0.0.0' if unable to determine.

    Security:
        - Only trusts X-Forwarded-For from configured trusted proxies
        - Validates IP format before returning
        - Logs suspicious IP headers for audit

    Example:
        >>> client_ip = get_client_ip(request)
        >>> perform_rate_limit_check(client_ip)
    """
    # Get immediate sender IP
    remote_addr = request.META.get('REMOTE_ADDR', '0.0.0.0')

    # Check if request comes from trusted proxy
    trusted_proxies = getattr(settings, 'TRUSTED_PROXIES', ['127.0.0.1'])

    if _is_trusted_proxy(remote_addr, trusted_proxies):
        # Trust X-Forwarded-For from trusted proxy
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
        if x_forwarded_for:
            # Take rightmost IP (closest to origin)
            try:
                client_ip = x_forwarded_for.split(',')[-1].strip()
                if _is_valid_ip(client_ip):
                    return client_ip
            except (IndexError, ValueError):
                logger.warning(
                    f"Invalid X-Forwarded-For header: {x_forwarded_for}",
                    extra={'remote_addr': remote_addr}
                )

    return remote_addr


def _is_trusted_proxy(ip: str, trusted_proxies: list) -> bool:
    """Check if IP is in trusted proxy list.

    Args:
        ip: IP address to check.
        trusted_proxies: List of trusted proxy IPs/networks.

    Returns:
        True if IP is trusted, False otherwise.
    """
    import ipaddress

    try:
        check_ip = ipaddress.ip_address(ip)
        for proxy in trusted_proxies:
            try:
                if isinstance(ipaddress.ip_network(proxy, strict=False),
                             ipaddress.IPv4Network):
                    if check_ip in ipaddress.ip_network(proxy, strict=False):
                        return True
            except ValueError:
                # Handle individual IP addresses
                if str(check_ip) == proxy:
                    return True
        return False
    except ValueError:
        return False


def _is_valid_ip(ip: str) -> bool:
    """Validate IP address format.

    Args:
        ip: IP address to validate.

    Returns:
        True if valid IPv4 or IPv6, False otherwise.
    """
    import ipaddress

    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False
```

**Update Imports:**

```python
# config/middleware/audit.py
from config.utils.request import get_client_ip

class AuditMiddleware:
    def process_request(self, request):
        request.client_ip = get_client_ip(request)
        # ...

# config/middleware/rate_limit.py
from config.utils.request import get_client_ip

class RateLimitMiddleware:
    def process_request(self, request):
        client_ip = get_client_ip(request)
        # ...

# api/security.py
from config.utils.request import get_client_ip

def check_rate_limit(request):
    client_ip = get_client_ip(request)
    # ...
```

**Implementation Steps:**
1. Create `config/utils/request.py` with the centralised function
2. Update all three files to import from the new location
3. Add comprehensive tests for IP extraction
4. Test with various proxy configurations
5. Document in developer guide

**Timeline:** Next sprint (depends on critical issue fixes first)

---

## Warnings

### W1: ALLOWED_HOSTS Wildcard in Staging

**File:** `config/settings/staging.py`
**Severity:** WARNING
**Risk:** Could allow Host header injection attacks

The ALLOWED_HOSTS setting uses wildcard which is too permissive:

```python
# Current
ALLOWED_HOSTS = ['*']  # Too permissive

# Recommended
ALLOWED_HOSTS = [
    'staging.example.com',
    'api-staging.example.com',
    'www-staging.example.com',
]
```

**Action:** Define explicit hostnames for staging environment.

---

### W2: Missing Rate Limit Headers

**File:** `config/middleware/rate_limit.py`
**Lines:** 95-110
**Severity:** WARNING
**Risk:** Clients cannot see rate limit status

Add standard RateLimit headers to responses:

```python
# Add to RateLimitMiddleware.process_response()
response['RateLimit-Limit'] = limit_per_hour
response['RateLimit-Remaining'] = remaining_requests
response['RateLimit-Reset'] = reset_time_unix
response['Retry-After'] = retry_after_seconds  # For 429 responses
```

---

### W3: Naive GraphQL Complexity Calculation

**File:** `api/schema.py`
**Lines:** 230-245
**Severity:** WARNING
**Risk:** GraphQL DoS attacks through complex queries

The complexity calculation doesn't account for nested fields:

```python
# Current: counts top-level fields only
complexity = len(query_fields)

# Recommended: use graphql-core's depth and breadth analysis
from graphql import validate, specified_rules
from graphql.validation import NoSchemaIntrospectionCustomRule

# Use proven complexity analysis
validate(schema, document_ast, specified_rules)
```

**Action:** Implement GraphQL query complexity validation with depth limits.

---

### W4: Missing Password Validator Tests

**File:** `config/settings/test.py`
**Severity:** WARNING
**Risk:** Password validators not tested in CI

PASSWORD_VALIDATORS setting in base.py isn't tested:

```python
# Add to tests/test_password_validation.py
class PasswordValidatorTests(TestCase):
    def test_numeric_only_rejected(self):
        with self.assertRaises(ValidationError):
            validate_password('12345678')

    def test_common_passwords_rejected(self):
        with self.assertRaises(ValidationError):
            validate_password('password123')

    def test_strong_password_accepted(self):
        try:
            validate_password('Hx$kL9@mP2qR!vW4')
        except ValidationError:
            self.fail("Strong password was rejected")
```

---

### W5: Cache TTL Reset Issue

**File:** `config/cache/backend.py`
**Lines:** 78-89
**Severity:** WARNING
**Risk:** Cache expiration not working correctly

Cache TTL is reset on every access instead of respecting original expiry:

```python
# Current problem
def get_cached_value(key):
    value = cache.get(key)  # This resets TTL
    cache.set(key, value)    # Unnecessary reset
    return value

# Better approach
def get_cached_value(key):
    return cache.get(key)  # Don't reset TTL
```

---

### W6: Sentry Missing Performance Monitoring

**File:** `config/settings/production.py`
**Severity:** WARNING
**Risk:** Cannot diagnose performance issues

Sentry configuration doesn't enable performance monitoring:

```python
# Add to Sentry config
import sentry_sdk

sentry_sdk.init(
    dsn=SENTRY_DSN,
    # Enable performance monitoring
    traces_sample_rate=0.1,  # 10% of transactions
    # Capture Django middleware
    integrations=[
        sentry_sdk.integrations.django.DjangoIntegration(),
        sentry_sdk.integrations.celery.CeleryIntegration(),
    ],
)
```

---

### W7: Missing CSRF Token in GraphQL Mutations

**File:** `api/schema.py`
**Severity:** WARNING
**Risk:** CSRF attacks on GraphQL mutations

GraphQL mutations don't validate CSRF tokens:

```python
# Add CSRF protection to mutation endpoint
from django.middleware.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_protect

@ensure_csrf_cookie
@csrf_protect
def graphql_view(request):
    # Now CSRF token is validated for mutations
    ...
```

---

### W8: Incomplete Error Message Sanitisation

**File:** `api/error_handling.py`
**Severity:** WARNING
**Risk:** Sensitive information in error responses

Some error messages may leak database details in development mode:

```python
# Review error handlers for database paths, SQL, internal details
# Use Django's DEBUG=False in all non-dev environments
# Test with DEBUG=True and DEBUG=False to catch leaks
```

---

## Suggestions

### S1: Refactor RateLimitMiddleware

**File:** `config/middleware/rate_limit.py`
**Effort:** 2-4 hours

Current middleware is monolithic. Suggest splitting into:
- IP extraction and validation
- Rate limit checking (separate class)
- Response header management
- Logging and metrics

Benefits: Easier to test, reuse, and maintain.

---

### S2: Extract Logging Configuration

**File:** `config/settings/base.py`
**Effort:** 1-2 hours

Move 80+ lines of logging config to separate file:

```python
# Create config/logging/base.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    # ... extensive config
}

# In settings/base.py, import it
from config.logging import LOGGING
```

Benefits: Settings file is cleaner, logging is reusable.

---

### S3: Replace Magic Numbers

**Files:** Multiple
**Effort:** 2-3 hours

Replace magic numbers with named constants:

```python
# Bad
if request_count > 100:  # What is 100?
    ...
reset_time = time.time() + 3600  # What's 3600?

# Good
from config.constants import RATE_LIMIT_REQUESTS_PER_HOUR, CACHE_TTL_SECONDS

if request_count > RATE_LIMIT_REQUESTS_PER_HOUR:
    ...
reset_time = time.time() + CACHE_TTL_SECONDS
```

Benefits: Code is self-documenting, easier to maintain.

---

### S4: Add Database Indexes

**File:** `apps/*/models.py`
**Effort:** 2-3 hours

Audit shows missing indexes on frequently queried fields:

```python
# Add to models
class User(models.Model):
    email = models.EmailField(unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['email', 'created_at']),
            models.Index(fields=['created_at']),
        ]
```

---

### S5: Document Security Assumptions

**File:** `docs/SECURITY/ASSUMPTIONS.md` (create new)
**Effort:** 2-3 hours

Document what the application assumes about its deployment:
- Which headers to trust (X-Forwarded-For, X-Real-IP)
- Proxy configuration expectations
- TLS/HTTPS requirements
- Database encryption requirements
- Backup and disaster recovery procedures

---

### S6: Add GraphQL Query Depth Limit

**File:** `api/schema.py`
**Effort:** 1-2 hours

Implement maximum query depth to prevent DoS:

```python
from graphql import validate, specified_rules
from graphql.validation.rules.no_schema_introspection_custom_rule import (
    NoSchemaIntrospectionCustomRule
)

class QueryDepthAnalyzer:
    """Analyse and limit GraphQL query depth."""

    MAX_DEPTH = 5
    MAX_BREADTH = 20
```

---

## Positive Notes

### Excellent Password Validators

**File:** `config/settings/base.py`
**Status:** Well implemented

The password validation suite is comprehensive:
- Numeric similarity check
- Common password detection
- Length requirements
- Special character enforcement

This exceeds OWASP guidelines.

---

### GraphQL Security Extensions

**File:** `api/schema.py`
**Status:** Well configured

Excellent implementation of:
- Introspection restrictions in production
- Query depth limiting
- Query timeout handling
- Authorization checks in resolvers

---

### Comprehensive Audit Logging

**File:** `config/middleware/audit.py`
**Status:** Best practice implementation

Logs important events:
- Authentication attempts
- Authorization failures
- Data access patterns
- Administrative actions

Provides excellent forensic trail.

---

### Environment-Specific Configuration

**File:** `config/settings/`
**Status:** Well organized

Proper separation of:
- Base settings
- Environment overrides
- Secret management
- Debug flags

This pattern prevents configuration mistakes.

---

### Clear Documentation Standards

**File:** Throughout codebase
**Status:** Above average

Google-style docstrings throughout with:
- Purpose statements
- Argument descriptions
- Return value documentation
- Examples

Helps maintainability.

---

## Recommendations

### Immediate Actions (This Sprint)

1. **Fix MD5 cache keys** - Replace with SHA256 (1-2 hours)
2. **Fix IP spoofing** - Add TRUSTED_PROXIES validation (2-3 hours)
3. **Fix code duplication** - Centralise IP extraction (2-3 hours)
4. **Add rate limit headers** - Implement W2 (1 hour)
5. **Define ALLOWED_HOSTS** - Fix W1 (30 minutes)

**Total: 6-10 hours of security-focused work**

### Next Sprint

1. Implement GraphQL complexity validation (W3)
2. Add password validator tests (W4)
3. Fix cache TTL issue (W5)
4. Add Sentry performance monitoring (W6)
5. Add CSRF protection to GraphQL (W7)

### Ongoing

- Replace magic numbers (S3)
- Add database indexes (S4)
- Refactor middleware (S1)
- Extract logging config (S2)
- Document assumptions (S5)

---

## Next Steps

### For Development Team

1. Copy critical issues to project management tool (ClickUp/GitHub Issues)
2. Prioritise security fixes for immediate implementation
3. Create test cases before implementing fixes
4. Review changes with security-conscious team member
5. Re-run review after implementation to verify

### For Team Lead

1. Schedule security-focused sprint if needed
2. Assign critical fixes to experienced developers
3. Plan code review checklist based on these findings
4. Consider security training on IP spoofing and hashing
5. Add automated security checks to CI/CD pipeline

### Related Documents

- [Security Guidelines](../SECURITY/SECURITY.md)
- [Syntax/Linting Report](../SYNTAX/LINTING-REPORT-2026-01-03.md)
- [GDPR Compliance Assessment](../GDPR/COMPLIANCE-ASSESSMENT-2026-01-03.md)
- [Logging Implementation Plan](../LOGGING/IMPLEMENTATION-PLAN-2026-01-03.md)
