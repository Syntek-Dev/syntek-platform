# Custom Middleware

Custom Django middleware for security, rate limiting, and audit logging.

## Table of Contents

- [Custom Middleware](#custom-middleware)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Middleware Files](#middleware-files)
    - [security.py](#securitypy)
    - [audit.py](#auditpy)
    - [ratelimit.py](#ratelimitpy)
  - [How Middleware Works](#how-middleware-works)
    - [Request Flow](#request-flow)
    - [Middleware Order](#middleware-order)
  - [Creating New Middleware](#creating-new-middleware)
    - [Step 1: Create Middleware Class](#step-1-create-middleware-class)
    - [Step 2: Register in Settings](#step-2-register-in-settings)
    - [Step 3: Test Middleware](#step-3-test-middleware)
    - [Step 4: Documentation](#step-4-documentation)
  - [Advanced Patterns](#advanced-patterns)
    - [Conditional Middleware](#conditional-middleware)
    - [Middleware with Database Access](#middleware-with-database-access)
    - [Middleware with Caching](#middleware-with-caching)
  - [Related Documentation](#related-documentation)

---

## Overview

Middleware components that process requests and responses for the entire Django application.

**Key Point:** Middleware runs on every request in the order it's registered in `settings.MIDDLEWARE`.

---

## Middleware Files

### security.py

Security headers and protections middleware.

**Responsibility:**

- Sets security headers (HSTS, X-Frame-Options, etc.)
- Enforces HTTPS in production
- Protects against common web vulnerabilities
- Manages CORS headers

**Headers Added:**

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Content-Security-Policy: [configured policy]
```

**Configuration:**

- Environment-specific in `config/settings/`
- Stricter in production
- Relaxed in development for testing

### audit.py

Audit logging middleware for security monitoring.

**Responsibility:**

- Logs all requests and responses
- Tracks sensitive operations
- Records user actions for compliance
- Enables security incident investigation

**Logs:**

```
[INFO] Request: GET /admin/ from 192.168.1.1 user=admin
[INFO] Response: 200 OK from admin view
[WARNING] Failed login attempt from 192.168.1.100
[ERROR] Sensitive data access attempt by user=guest
```

**Configuration:**

- Logging level per environment
- Audit log rotation
- Sensitive endpoint tracking
- Performance impact monitoring

### ratelimit.py

Rate limiting middleware to prevent abuse.

**Responsibility:**

- Limits requests per IP address
- Protects endpoints from brute force
- Prevents denial-of-service attacks
- Throttles expensive operations

**Limits:**

```
Default: 100 requests per hour per IP
Strict endpoints: 10 requests per hour
API endpoints: 1000 requests per hour
```

**Returns on limit exceeded:**

```
HTTP 429 Too Many Requests
Retry-After: 300
X-RateLimit-Remaining: 0
```

---

## How Middleware Works

### Request Flow

```
Client Request
    ↓
[1] security.py (adds headers, validates request)
    ↓
[2] audit.py (logs request, tracks user)
    ↓
[3] ratelimit.py (checks rate limit, throttles if needed)
    ↓
[4] Other Django middleware
    ↓
Django View Processing
    ↓
[4] Other Django middleware (response)
    ↓
[3] ratelimit.py (cleanup, response headers)
    ↓
[2] audit.py (logs response, records completion)
    ↓
[1] security.py (final headers, cleanup)
    ↓
Client Response
```

### Middleware Order

Order matters! Middleware runs in the order specified in `settings.MIDDLEWARE`:

```python
# In config/settings/base.py
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    # ... Django middleware ...
    "config.middleware.security.SecurityHeadersMiddleware",
    "config.middleware.audit.AuditLoggingMiddleware",
    "config.middleware.ratelimit.RateLimitMiddleware",
]
```

---

## Creating New Middleware

### Step 1: Create Middleware Class

```python
# In config/middleware/my_middleware.py
"""Custom middleware for my_feature functionality."""

from django.http import HttpRequest, HttpResponse
from typing import Callable


class MyCustomMiddleware:
    """Description of what the middleware does.

    This middleware handles [specific responsibility] for requests.
    """

    def __init__(self, get_response: Callable) -> None:
        """Initialize middleware.

        Args:
            get_response: The next middleware or view callable.
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process request and response.

        Args:
            request: The incoming HTTP request.

        Returns:
            The HTTP response.
        """
        # Process request before view
        request.custom_attribute = "value"

        # Call next middleware/view
        response = self.get_response(request)

        # Process response after view
        response["X-Custom-Header"] = "value"

        return response
```

### Step 2: Register in Settings

```python
# In config/settings/base.py
MIDDLEWARE = [
    # ... existing middleware ...
    "config.middleware.my_middleware.MyCustomMiddleware",
]
```

### Step 3: Test Middleware

```python
# In tests/middleware/test_my_middleware.py
"""Tests for my_middleware."""

from django.test import TestCase, Client


class MyCustomMiddlewareTestCase(TestCase):
    """Test cases for MyCustomMiddleware."""

    def setUp(self) -> None:
        """Set up test client."""
        self.client = Client()

    def test_middleware_adds_header(self) -> None:
        """Test that middleware adds custom header."""
        response = self.client.get("/")
        self.assertIn("X-Custom-Header", response)
```

### Step 4: Documentation

Add docstring and update this README:

```markdown
### my_middleware.py

Description of what it does.

**Responsibility:**

- First responsibility
- Second responsibility

**Headers/Status Codes:**

- Header 1: description
- Status 429: description
```

---

## Advanced Patterns

### Conditional Middleware

Only run middleware for certain paths:

```python
class ConditionalMiddleware:
    """Only applies to certain URLs."""

    PROTECTED_PATHS = ["/admin/", "/api/"]

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process request conditionally."""
        if not any(request.path.startswith(p) for p in self.PROTECTED_PATHS):
            return self.get_response(request)

        # Apply middleware logic only for protected paths
        return self.apply_protection(request)
```

### Middleware with Database Access

```python
class DatabaseMiddleware:
    """Middleware that accesses the database."""

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process request with database access."""
        # Access database
        user_config = UserConfig.objects.filter(user=request.user).first()
        request.user_config = user_config

        return self.get_response(request)
```

### Middleware with Caching

```python
from django.views.decorators.cache import cache_page


class CachingMiddleware:
    """Middleware that caches responses."""

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Cache response if applicable."""
        if request.method == "GET" and not request.user.is_authenticated:
            # Cache public GET requests for 1 hour
            cache_key = f"response:{request.path}"
            # Check cache and return if found
            # Otherwise call view, cache response, return

        return self.get_response(request)
```

---

## Related Documentation

- [Configuration Overview](../README.md) - Config directory overview
- [Security Documentation](../../docs/SECURITY/SECURITY.md) - Security headers and protection
- [Audit Logging](../../docs/LOGGING/README.md) - Audit logging system
- [Django Middleware Docs](https://docs.djangoproject.com/en/5.2/topics/http/middleware/) - Official Django middleware guide

---

**Last Updated:** 2026-01-03
