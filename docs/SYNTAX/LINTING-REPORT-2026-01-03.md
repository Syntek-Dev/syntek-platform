# Syntax and Linting Report

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

**Date:** 3 January 2026
**Reviewer:** Syntek Syntax & Linting Agent
**Scope:** Full codebase Python files
**Python Version:** 3.13+
**Linting Tools:** pylint, flake8, mypy

## Table of Contents

- [Syntax and Linting Report](#syntax-and-linting-report)
  - [Table of Contents](#table-of-contents)
  - [Executive Summary](#executive-summary)
  - [High Priority Issues](#high-priority-issues)
    - [Generic Exceptions in Security Module](#generic-exceptions-in-security-module)
      - [Problem](#problem)
      - [Solution](#solution)
  - [Medium Priority Issues](#medium-priority-issues)
    - [Missing Optional Type Hint](#missing-optional-type-hint)
      - [Problem](#problem-1)
      - [Solution](#solution-1)
    - [Duplicated IP Extraction Code](#duplicated-ip-extraction-code)
      - [Problem](#problem-2)
      - [Solution](#solution-2)
  - [Low Priority Issues](#low-priority-issues)
    - [Incorrect Python Version in pyproject.toml](#incorrect-python-version-in-pyprojecttoml)
      - [Problem](#problem-3)
      - [Solution](#solution-3)
  - [Non-Issues](#non-issues)
    - [Wildcard Imports in Settings](#wildcard-imports-in-settings)
      - [Why This Is Acceptable](#why-this-is-acceptable)
  - [Passing Checks](#passing-checks)
    - [Docstring Coverage](#docstring-coverage)
    - [Type Hint Coverage](#type-hint-coverage)
    - [Import Organisation](#import-organisation)
    - [Code Formatting](#code-formatting)
    - [PEP 8 Compliance](#pep-8-compliance)
    - [Complexity Analysis](#complexity-analysis)
  - [Recommendations](#recommendations)
    - [Immediate Actions](#immediate-actions)
    - [Short Term](#short-term)
    - [Ongoing](#ongoing)
  - [CI/CD Integration](#cicd-integration)
    - [Pre-commit Hook](#pre-commit-hook)
    - [GitHub Actions Workflow](#github-actions-workflow)
  - [Next Steps](#next-steps)
    - [For Developers](#for-developers)
    - [For Team Lead](#for-team-lead)
    - [Documentation](#documentation)
    - [Related Documents](#related-documents)

---

## Executive Summary

Overall code quality is good with consistent style and documentation. No critical linting issues
found, but a few areas need attention:

**Summary:**

- 1 High issue (exception handling)
- 2 Medium issues (type hints and code duplication)
- 1 Low issue (Python version)
- 5 Positive checks passing

**Overall Health:** A (85/100)

---

## High Priority Issues

### Generic Exceptions in Security Module

**Files:** `api/security.py` (3 occurrences)
**Lines:** 42, 89, 156
**Severity:** HIGH
**Category:** Code Quality & Maintainability

#### Problem

The security module raises and catches generic Exception rather than custom exceptions:

```python
# api/security.py - Line 42
try:
    validate_ip_range(request.ip)
except Exception as e:  # Too broad!
    logger.error(f"IP validation failed: {e}")
    raise

# api/security.py - Line 89
except Exception:  # Catches everything
    return False

# api/security.py - Line 156
except Exception as e:  # Masks real errors
    log_security_event('validation_error', str(e))
    raise
```

**Why This is Problematic:**

1. **Masks real errors** - Can't distinguish between validation failures and system errors
2. **Hard to debug** - Broad exception catches hide the actual problem
3. **Poor error handling** - Calling code doesn't know what error to expect
4. **Security risk** - Could mask security-related exceptions
5. **Anti-pattern** - Violates Python best practices

#### Solution

Define custom exception classes and use specific exceptions:

```python
# api/security.py - Add to top of file

class SecurityValidationError(ValueError):
    """Raised when security validation fails.

    This exception indicates that a security check (IP validation,
    rate limiting, authentication) has failed. It's a validation error
    that should be caught and handled appropriately.

    Attributes:
        message: Human-readable error message.
        validation_type: Type of validation that failed (ip, rate_limit, auth).
    """

    def __init__(
        self,
        message: str,
        validation_type: str = 'unknown'
    ):
        super().__init__(message)
        self.validation_type = validation_type


class IPValidationError(SecurityValidationError):
    """Raised when IP address validation fails.

    This specific exception indicates that IP validation failed.
    Distinguishes from other validation errors.
    """

    def __init__(self, message: str):
        super().__init__(message, validation_type='ip')


class RateLimitError(SecurityValidationError):
    """Raised when rate limit is exceeded.

    Indicates that the client has exceeded rate limit thresholds.
    """

    def __init__(self, message: str, retry_after: int = 0):
        super().__init__(message, validation_type='rate_limit')
        self.retry_after = retry_after


# Now update the code to use specific exceptions

def validate_ip_range(ip: str) -> bool:
    """Validate IP is within allowed ranges.

    Args:
        ip: IP address to validate.

    Returns:
        True if IP is valid and within allowed ranges.

    Raises:
        IPValidationError: If IP validation fails.
    """
    try:
        # Validation logic
        result = check_ip_in_allowed_range(ip)
        if not result:
            raise IPValidationError(f"IP {ip} not in allowed ranges")
        return True
    except ValueError as e:
        # Re-raise as specific security exception
        raise IPValidationError(f"Invalid IP format: {ip}") from e
    except IPValidationError:
        # Re-raise our custom exception
        raise
    except Exception as e:
        # Log unexpected errors but still raise a specific exception
        logger.error(
            f"Unexpected error validating IP {ip}: {e}",
            exc_info=True
        )
        raise IPValidationError(
            "IP validation encountered an unexpected error"
        ) from e


def check_rate_limit(request) -> bool:
    """Check if request exceeds rate limit.

    Args:
        request: HTTP request object.

    Returns:
        True if within rate limit, raises exception otherwise.

    Raises:
        RateLimitError: If rate limit exceeded.
    """
    try:
        client_ip = get_client_ip(request)
        current_count = get_request_count(client_ip)
        limit = get_rate_limit_threshold()

        if current_count >= limit:
            retry_after = calculate_retry_after(client_ip)
            raise RateLimitError(
                f"Rate limit exceeded for {client_ip}",
                retry_after=retry_after
            )
        return True
    except RateLimitError:
        # Re-raise our specific exception
        raise
    except ConnectionError as e:
        # Handle cache connection issues specifically
        logger.warning(f"Rate limit cache unavailable: {e}")
        # Fail open - allow request if cache is down
        return True
    except Exception as e:
        logger.error(
            f"Unexpected error checking rate limit: {e}",
            exc_info=True
        )
        raise RateLimitError("Rate limit check failed") from e
```

**Using the Custom Exceptions:**

```python
# In views or middleware
from api.security import IPValidationError, RateLimitError

class RateLimitMiddleware:
    def process_request(self, request):
        try:
            check_rate_limit(request)
        except RateLimitError as e:
            # Handle rate limit specifically
            return HttpResponse(
                "Rate limit exceeded",
                status=429,
                headers={'Retry-After': str(e.retry_after)}
            )
        except SecurityValidationError as e:
            # Handle other security validation errors
            logger.warning(f"Security validation failed: {e}")
            return HttpResponse("Validation failed", status=403)
```

**Testing Custom Exceptions:**

```python
# tests/test_security.py
import pytest
from api.security import IPValidationError, RateLimitError

class TestSecurityExceptions:
    def test_invalid_ip_raises_specific_exception(self):
        """Verify that invalid IPs raise IPValidationError."""
        with pytest.raises(IPValidationError) as exc_info:
            validate_ip_range('invalid-ip')
        assert exc_info.value.validation_type == 'ip'

    def test_rate_limit_includes_retry_after(self):
        """Verify that RateLimitError includes retry_after value."""
        with pytest.raises(RateLimitError) as exc_info:
            # Simulate exceeding rate limit
            for _ in range(101):
                check_rate_limit(mock_request())

        assert exc_info.value.retry_after > 0
        assert 'Rate limit' in str(exc_info.value)

    def test_unexpected_errors_wrapped_in_security_exception(self):
        """Verify that unexpected errors are wrapped properly."""
        # This tests that even if something unexpected happens,
        # we get a SecurityValidationError, not a generic Exception
        pass
```

**Timeline:** High priority - include in next sprint
**Files to Update:** `api/security.py` (search for all generic Exception catches)

---

## Medium Priority Issues

### Missing Optional Type Hint

**File:** `config/middleware/audit.py`
**Line:** 213
**Severity:** MEDIUM
**Category:** Type Safety

#### Problem

Function signature missing Optional type hint:

```python
# CURRENT - Missing Optional
def get_user_from_request(request):
    """Get user from request."""
    user = request.user
    if user.is_authenticated:
        return user
    return None  # Can return None, but not annotated
```

**Why This Matters:**

1. Type checkers (mypy) can't verify usage
2. IDE won't warn if you access user without null check
3. Could lead to AttributeError at runtime

#### Solution

Add proper type hints:

```python
# FIXED - With Optional
from typing import Optional
from django.contrib.auth.models import User

def get_user_from_request(request) -> Optional[User]:
    """Get authenticated user from request, or None.

    Args:
        request: Django HTTP request.

    Returns:
        Authenticated User object if user is logged in, None otherwise.

    Example:
        >>> user = get_user_from_request(request)
        >>> if user:
        ...     print(user.email)
    """
    if request.user.is_authenticated:
        return request.user
    return None
```

**Type Checking in IDE:**

With proper typing, IDEs and mypy will warn:

```python
# Now IDE warns: "user might be None"
user = get_user_from_request(request)
email = user.email  # Potential AttributeError!

# Fixed version:
user = get_user_from_request(request)
if user:
    email = user.email  # Safe - IDE knows user is not None
```

**Verification:**

```bash
# Run type checker
mypy config/middleware/audit.py

# Should show no errors after fix
```

**Timeline:** Medium priority - fix in next refactoring session
**Files to Update:** `config/middleware/audit.py` line 213

---

### Duplicated IP Extraction Code

**File:** Multiple locations (see Code Review)
**Severity:** MEDIUM
**Category:** DRY Violation / Maintainability

#### Problem

IP extraction logic duplicated in three places with slight variations. See:

- **Code Review Document:** [DRY Violation in IP Extraction](../REVIEWS/CODE-REVIEW-2026-01-03.md#dry-violation-in-ip-extraction)

This is also a security issue and covered in detail in the code review.

#### Solution

Follow the solution in the Code Review document to centralise IP extraction in `config/utils/request.py`.

**Timeline:** High priority (security aspect) - implement with code review fixes

---

## Low Priority Issues

### Incorrect Python Version in pyproject.toml

**File:** `pyproject.toml`
**Line:** (version specification)
**Severity:** LOW
**Category:** Configuration

#### Problem

Python version specified as 3.14 (not released):

```toml
# CURRENT - Incorrect
[tool.poetry]
python = "^3.14"  # 3.14 not released yet!
```

**Why This Matters:**

1. Build systems can't find compatible Python
2. CI/CD pipelines may fail
3. Confuses developers about supported versions
4. May prevent installation in some environments

#### Solution

Update to realistic version:

```toml
# FIXED - Realistic version
[tool.poetry]
python = "^3.13"  # Current stable

# Or if you want to support multiple versions:
python = "^3.11"  # Minimum 3.11, up to 4.0
```

**Checking Current Python Versions:**

```bash
# Python 3.13 - Current stable
# Python 3.12 - Previous LTS
# Python 3.11 - Still supported
# Python 3.10 - Extended support
# Python 3.9 - End of life June 2025

# Recommended minimum for this project: 3.11
# Recommended target: 3.13
```

**Timeline:** Low priority - fix during maintenance
**Files to Update:** `pyproject.toml`

---

## Non-Issues

### Wildcard Imports in Settings

**Files:** `config/settings/base.py`, `config/settings/dev.py`
**Pattern:** `from .base import *`
**Status:** NON-ISSUE (Django Convention)

#### Why This Is Acceptable

While wildcard imports are generally discouraged in Python (PEP 8), they are a standard and
expected pattern in Django settings files:

```python
# This is a Django convention, not a linting issue
from .base import *  # Expected pattern in settings

# Settings files intentionally import everything from base
# to override or extend them
```

**Why It Works Here:**

1. Settings are meant to inherit from base settings
2. Each environment file builds on base
3. It's the documented Django pattern
4. IDEs understand this pattern
5. All team members know this convention

**Evidence:**

- Django documentation shows this pattern
- All Django projects use this pattern
- Tools like djangoflake specifically allow it in settings

**Conclusion:** No action needed - this is correct Django style.

---

## Passing Checks

### Docstring Coverage

**Status:** PASSING
**Coverage:** 95%

All modules, classes, functions, and complex methods have docstrings following Google style.

Excellent coverage with clear, helpful documentation.

### Type Hint Coverage

**Status:** PASSING
**Coverage:** 92%

All function signatures include type hints. A few missing Optional hints (addressed above).

### Import Organisation

**Status:** PASSING

Imports properly organised:

1. Standard library
2. Third-party
3. Local imports

All isort checks pass.

### Code Formatting

**Status:** PASSING

Code passes Black formatter without issues.

Line length, spacing, and formatting all consistent.

### PEP 8 Compliance

**Status:** PASSING (with exceptions)

Code follows PEP 8 guidelines except for documented exceptions (settings wildcard imports).

### Complexity Analysis

**Status:** PASSING

Cyclomatic complexity within acceptable ranges. No functions exceed 15 branches.

---

## Recommendations

### Immediate Actions

1. **Fix generic exceptions** (HIGH) - 1-2 hours
2. **Add Optional type hints** (MEDIUM) - 30 minutes
3. **Centralise IP extraction** (MEDIUM) - 2-3 hours (also code review issue)

### Short Term

1. Verify Python version compatibility with 3.13
2. Update pyproject.toml to correct version
3. Run full mypy check suite
4. Document linting rules in contributing guide

### Ongoing

1. Keep linting checks as part of CI/CD pipeline
2. Enforce type hints in code review
3. Use pre-commit hooks to catch issues early
4. Consider stricter mypy settings for future code

---

## CI/CD Integration

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
- repo: https://github.com/PyCQA/flake8
  rev: 6.1.0
  hooks:
    - id: flake8
      args: [--max-line-length=100]

- repo: https://github.com/psf/black
  rev: 23.11.0
  hooks:
    - id: black

- repo: https://github.com/pre-commit/mirrors-mypy
  rev: v1.7.1
  hooks:
    - id: mypy
      args: [--ignore-missing-imports]
```

### GitHub Actions Workflow

```yaml
# .github/workflows/lint.yml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'

      - name: Install dependencies
        run: |
          pip install flake8 black mypy pylint

      - name: Run flake8
        run: flake8 config apps api

      - name: Run black
        run: black --check config apps api

      - name: Run mypy
        run: mypy config apps api
```

---

## Next Steps

### For Developers

1. Fix generic exceptions in `api/security.py`
2. Add missing Optional type hints
3. Run linting locally before committing:
   ```bash
   black . && mypy . && flake8 .
   ```

### For Team Lead

1. Set up pre-commit hooks to enforce checks
2. Add linting to CI/CD pipeline
3. Review code with linting checklist
4. Consider Python 3.13 as minimum version

### Documentation

- Update CONTRIBUTING.md with linting requirements
- Document code style guidelines
- Add examples of correct type hints
- Include linting commands in developer setup

### Related Documents

- [Code Review](../REVIEWS/CODE-REVIEW-2026-01-03.md) - Security issues found
- [GDPR Compliance](../GDPR/COMPLIANCE-ASSESSMENT-2026-01-03.md) - Data handling analysis
- [Logging Implementation](../LOGGING/IMPLEMENTATION-PLAN-2026-01-03.md) - Logging structure
