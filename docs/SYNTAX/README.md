# Syntax and Code Quality

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [Syntax and Code Quality](#syntax-and-code-quality)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Available Reports](#available-reports)
    - [LINTING-REPORT-2026-01-03.md](#linting-report-2026-01-03md)
  - [Quick Reference](#quick-reference)
    - [Most Common Issues](#most-common-issues)
  - [How to Use](#how-to-use)
    - [1. Read the Report](#1-read-the-report)
    - [2. Identify Priority](#2-identify-priority)
    - [3. Create Issues](#3-create-issues)
    - [4. Run Local Checks](#4-run-local-checks)
    - [5. Fix Issues](#5-fix-issues)
    - [6. Verify Fix](#6-verify-fix)
  - [Linting Tools](#linting-tools)
    - [Running Locally](#running-locally)
  - [CI/CD Integration](#cicd-integration)
  - [Common Patterns](#common-patterns)
    - [Type Hints](#type-hints)
    - [Exception Handling](#exception-handling)
    - [Docstrings](#docstrings)
  - [Next Steps](#next-steps)
  - [Related Documents](#related-documents)

---

## Overview

This folder contains syntax analysis, code quality assessments, and linting reports for the codebase.

**Current Status:** A (85/100) - Good code quality with minor improvements needed

---

## Available Reports

### LINTING-REPORT-2026-01-03.md

Comprehensive analysis of Python code syntax, type hints, and style compliance.

**Key Findings:**
- 1 High priority issue (generic exception handling)
- 2 Medium priority issues (type hints, code duplication)
- 1 Low priority issue (Python version)
- 5 Positive checks passing

**Focus Areas:**
- Exception handling best practices
- Type hint coverage
- Code duplication detection
- Python version compatibility
- PEP 8 compliance
- Docstring coverage

---

## Quick Reference

### Most Common Issues

| Issue | File | Fix |
|-------|------|-----|
| Generic Exception | `api/security.py` | Create specific exception classes |
| Missing Optional | `config/middleware/audit.py:213` | Add Optional type hint |
| Code Duplication | IP extraction (3 locations) | Centralise in `config/utils/request.py` |
| Python Version | `pyproject.toml` | Update to `^3.13` |

---

## How to Use

### 1. Read the Report

Start with [LINTING-REPORT-2026-01-03.md](LINTING-REPORT-2026-01-03.md) for complete analysis.

### 2. Identify Priority

**High Priority (fix soon):**
- Generic exception handling in security code

**Medium Priority (next sprint):**
- Missing Optional type hints
- Code duplication

**Low Priority (maintenance):**
- Python version in config

### 3. Create Issues

Convert findings to tasks in ClickUp or GitHub Issues.

### 4. Run Local Checks

```bash
# Check syntax
python -m py_compile config/settings/base.py

# Run linters
flake8 config/ apps/ api/
black --check config/ apps/ api/
mypy config/ apps/ api/
pylint config/ apps/ api/
```

### 5. Fix Issues

Follow the detailed solutions in the report.

### 6. Verify Fix

Re-run linters to confirm issues resolved.

---

## Linting Tools

The project uses these tools for code quality:

| Tool | Purpose | Config |
|------|---------|--------|
| flake8 | Style compliance | `.flake8` |
| black | Code formatting | `pyproject.toml` |
| mypy | Type checking | `pyproject.toml` |
| pylint | Code analysis | `.pylintrc` |
| isort | Import sorting | `.isort.cfg` |

### Running Locally

```bash
# Format code
black config/ apps/ api/

# Check formatting
black --check config/ apps/ api/

# Sort imports
isort config/ apps/ api/

# Run all linters
flake8 && black --check . && mypy . && pylint config apps api
```

---

## CI/CD Integration

These checks run automatically:

1. **On every commit:** Pre-commit hooks (if configured)
2. **On every push:** GitHub Actions workflow
3. **Before merge:** Required checks must pass

See `.pre-commit-config.yaml` and `.github/workflows/` for details.

---

## Common Patterns

### Type Hints

```python
# Good
from typing import Optional, List, Dict

def get_user(user_id: int) -> Optional[User]:
    """Get user or None if not found."""
    pass

def process_items(items: List[str]) -> Dict[str, int]:
    """Process items and return counts."""
    pass

# Bad
def get_user(user_id):  # Missing type hints
    pass
```

### Exception Handling

```python
# Good - Specific exceptions
class ValidationError(Exception):
    pass

try:
    validate_data(data)
except ValidationError as e:
    logger.warning(f"Validation failed: {e}")

# Bad - Generic exception
try:
    validate_data(data)
except Exception:  # Too broad!
    pass
```

### Docstrings

```python
# Good - Google style
def process_user(user_id: int) -> dict:
    """Process user data and return results.

    Args:
        user_id: The ID of the user to process.

    Returns:
        Dictionary with processed user information.

    Raises:
        User.DoesNotExist: If user not found.
    """
    pass

# Bad - Incomplete
def process_user(user_id):
    pass  # No documentation
```

---

## Next Steps

1. Review [LINTING-REPORT-2026-01-03.md](LINTING-REPORT-2026-01-03.md)
2. Fix High priority issues this sprint
3. Address Medium priority issues next sprint
4. Set up pre-commit hooks for local development
5. Review code with linting checklist

---

## Related Documents

- [Code Review Report](../REVIEWS/CODE-REVIEW-2026-01-03.md)
- [GDPR Compliance](../GDPR/COMPLIANCE-ASSESSMENT-2026-01-03.md)
- [Logging Implementation](../LOGGING/IMPLEMENTATION-PLAN-2026-01-03.md)
