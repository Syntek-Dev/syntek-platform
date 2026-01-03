# Logging Implementation Plan

**Date:** 3 January 2026
**Reviewer:** Syntek Logging Implementation Agent
**Scope:** Structured logging architecture
**Status:** Ready for implementation

## Table of Contents

- [Logging Implementation Plan](#logging-implementation-plan)
  - [Table of Contents](#table-of-contents)
  - [Executive Summary](#executive-summary)
  - [Current State](#current-state)
    - [What We Have](#what-we-have)
    - [Issues](#issues)
  - [Proposed Architecture](#proposed-architecture)
    - [Folder Structure](#folder-structure)
    - [Module Breakdown](#module-breakdown)
      - [1. formatters.py - Custom Formatters](#1-formatterspy---custom-formatters)
      - [2. filters.py - Custom Filters](#2-filterspy---custom-filters)
      - [3. handlers.py - Custom Handlers](#3-handlerspy---custom-handlers)
      - [4. context.py - Request Context Tracking](#4-contextpy---request-context-tracking)
      - [5. decorators.py - Logging Decorators](#5-decoratorspy---logging-decorators)
  - [Environment-Specific Configuration](#environment-specific-configuration)
    - [Development Environment](#development-environment)
    - [Production Environment](#production-environment)
  - [Implementation Phases](#implementation-phases)
    - [Phase 1: Core Logging Structure](#phase-1-core-logging-structure)
    - [Phase 2: Decorators and Utils](#phase-2-decorators-and-utils)
    - [Phase 3: Integration](#phase-3-integration)
  - [Code Examples](#code-examples)
    - [Using in Views](#using-in-views)
    - [GraphQL Query Logging](#graphql-query-logging)
    - [Accessing Logs](#accessing-logs)
  - [Testing Strategy](#testing-strategy)
    - [Unit Tests](#unit-tests)
    - [Integration Tests](#integration-tests)
  - [Deployment \& Monitoring](#deployment--monitoring)
    - [Log File Locations](#log-file-locations)
    - [Monitoring](#monitoring)
    - [Log Rotation](#log-rotation)
  - [Next Steps](#next-steps)
    - [Week 1 (Phase 1)](#week-1-phase-1)
    - [Week 2 (Phase 2)](#week-2-phase-2)
    - [Week 3 (Phase 3)](#week-3-phase-3)
    - [Ongoing](#ongoing)
  - [Related Documentation](#related-documentation)

---

## Executive Summary

**Current Status:** Basic logging configuration
**Proposed:** Structured, environment-aware logging with performance monitoring

**Improvements:**
- Centralised logging configuration
- JSON structured logging for production
- Colored console output for development
- Rotating file handlers
- Context-aware logging (request ID, user ID)
- GraphQL query logging
- Performance monitoring with Sentry

**Timeline:** 3-4 weeks
**Effort:** 60-80 hours

---

## Current State

### What We Have

```python
# config/settings/base.py - Basic logging configuration

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

### Issues

1. **All environments use same configuration** - No environment-specific tuning
2. **Only console output** - No persistent logs
3. **Plain text format** - Hard to parse and search in production
4. **No rotation** - Log files grow unbounded
5. **No request context** - Can't trace requests across logs
6. **No GraphQL logging** - API queries invisible
7. **Limited Sentry integration** - Missing performance monitoring

---

## Proposed Architecture

### Folder Structure

```
config/logging/
├── __init__.py                    # Package init, export public API
├── formatters.py                  # Custom formatters (JSON, colored)
├── filters.py                     # Custom filters (redact PII, environment)
├── handlers.py                    # Custom handlers (rotating files)
├── decorators.py                  # Logging decorators
├── context.py                     # Contextual logging (request tracking)
└── base.py                        # Base configuration (moved from settings)

config/settings/
├── base.py                        # Updated to import from config/logging
├── dev.py                         # Dev-specific logging
├── test.py                        # Test-specific logging
├── staging.py                     # Staging-specific logging
└── production.py                  # Production-specific logging

logs/                              # Log files directory (git-ignored)
├── app.log                        # General application logs
├── error.log                      # Error logs only
├── security.log                   # Security events
└── sql.log                        # Database queries
```

### Module Breakdown

#### 1. formatters.py - Custom Formatters

```python
# config/logging/formatters.py
"""Custom log formatters for different output styles."""

import json
import logging
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format logs as JSON for production parsing and searching."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON line."""
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': self.formatException(record.exc_info),
            }

        # Add request context if available
        if hasattr(record, 'request_id'):
            log_data['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'client_ip'):
            log_data['client_ip'] = record.client_ip

        # Add extra fields
        if hasattr(record, 'extra'):
            log_data.update(record.extra)

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """Format logs with ANSI colors for development console output."""

    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        levelname = record.levelname
        color = self.COLORS.get(levelname, '')

        # Create colored output
        record.levelname = f"{color}{levelname}{self.RESET}"

        # Use parent formatter
        result = super().format(record)

        # Restore original levelname
        record.levelname = levelname

        return result
```

#### 2. filters.py - Custom Filters

```python
# config/logging/filters.py
"""Custom filters for sensitive data redaction and context injection."""

import logging
import re
import os

class SensitiveDataFilter(logging.Filter):
    """Redact sensitive information from logs (passwords, tokens, SSNs)."""

    PATTERNS = [
        (r'password=\S+', 'password=[REDACTED]'),
        (r'token=\S+', 'token=[REDACTED]'),
        (r'"password":\s*"[^"]*"', '"password":"[REDACTED]"'),
        (r'"token":\s*"[^"]*"', '"token":"[REDACTED]"'),
        (r'\d{3}-\d{2}-\d{4}', '[SSN REDACTED]'),  # SSN pattern
        (r'(?:4[0-9]{12}(?:[0-9]{3})?)', '[CARD REDACTED]'),  # Credit card
    ]

    def filter(self, record: logging.LogRecord) -> bool:
        """Redact sensitive data from log message."""
        msg = record.getMessage()
        for pattern, replacement in self.PATTERNS:
            msg = re.sub(pattern, replacement, msg, flags=re.IGNORECASE)
        record.msg = msg
        return True


class EnvironmentFilter(logging.Filter):
    """Add environment information to logs."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add environment to log record."""
        record.environment = os.environ.get('ENVIRONMENT', 'development')
        record.version = os.environ.get('APP_VERSION', 'unknown')
        return True


class RequestContextFilter(logging.Filter):
    """Add request context to logs (request ID, user ID, IP)."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add request context from thread-local storage."""
        # This will be populated by middleware
        from config.logging.context import get_context

        context = get_context()
        if context:
            record.request_id = context.get('request_id')
            record.user_id = context.get('user_id')
            record.client_ip = context.get('client_ip')

        return True
```

#### 3. handlers.py - Custom Handlers

```python
# config/logging/handlers.py
"""Custom log handlers for file rotation and special handling."""

import logging
import logging.handlers
import os
from pathlib import Path

def get_rotating_handler(
    filename: str,
    formatter: logging.Formatter,
    level: int = logging.INFO,
    max_bytes: int = 10485760,  # 10 MB
    backup_count: int = 10
) -> logging.handlers.RotatingFileHandler:
    """Create a rotating file handler.

    Args:
        filename: Log file path.
        formatter: Formatter to use.
        level: Logging level.
        max_bytes: Maximum file size before rotation.
        backup_count: Number of backup files to keep.

    Returns:
        Configured RotatingFileHandler.
    """
    # Ensure log directory exists
    log_dir = Path(filename).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    handler = logging.handlers.RotatingFileHandler(
        filename,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    handler.setLevel(level)
    handler.setFormatter(formatter)

    return handler


def get_timed_rotating_handler(
    filename: str,
    formatter: logging.Formatter,
    when: str = 'midnight',
    interval: int = 1,
    backup_count: int = 30
) -> logging.handlers.TimedRotatingFileHandler:
    """Create a time-based rotating file handler.

    Args:
        filename: Log file path.
        formatter: Formatter to use.
        when: When to rotate ('midnight', 'hourly', etc).
        interval: Rotation interval.
        backup_count: Number of backup files to keep.

    Returns:
        Configured TimedRotatingFileHandler.
    """
    # Ensure log directory exists
    log_dir = Path(filename).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    handler = logging.handlers.TimedRotatingFileHandler(
        filename,
        when=when,
        interval=interval,
        backupCount=backup_count
    )
    handler.setFormatter(formatter)

    return handler
```

#### 4. context.py - Request Context Tracking

```python
# config/logging/context.py
"""Request context tracking for logging."""

import threading
import uuid
from typing import Optional, Dict, Any

# Thread-local storage for request context
_context = threading.local()


def set_context(request_id: str, user_id: Optional[int] = None,
                client_ip: Optional[str] = None) -> None:
    """Set logging context for current request.

    Args:
        request_id: Unique request identifier.
        user_id: ID of authenticated user (if any).
        client_ip: Client IP address.
    """
    _context.data = {
        'request_id': request_id,
        'user_id': user_id,
        'client_ip': client_ip,
    }


def get_context() -> Optional[Dict[str, Any]]:
    """Get current logging context."""
    return getattr(_context, 'data', None)


def clear_context() -> None:
    """Clear logging context."""
    if hasattr(_context, 'data'):
        del _context.data


def generate_request_id() -> str:
    """Generate unique request ID."""
    return str(uuid.uuid4())
```

#### 5. decorators.py - Logging Decorators

```python
# config/logging/decorators.py
"""Decorators for automatic function logging."""

import logging
import functools
import time
from typing import Any, Callable

logger = logging.getLogger(__name__)


def log_execution(level: int = logging.DEBUG) -> Callable:
    """Decorator to log function execution time and arguments.

    Args:
        level: Logging level to use.

    Example:
        @log_execution()
        def process_user_data(user_id: int) -> dict:
            # Function is logged with execution time
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            func_name = func.__qualname__
            start_time = time.time()

            logger.log(
                level,
                f"Executing {func_name}",
                extra={'function': func_name}
            )

            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.log(
                    level,
                    f"Completed {func_name} in {elapsed:.2f}s",
                    extra={
                        'function': func_name,
                        'elapsed_seconds': elapsed,
                        'status': 'success',
                    }
                )
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"Error in {func_name} after {elapsed:.2f}s: {e}",
                    extra={
                        'function': func_name,
                        'elapsed_seconds': elapsed,
                        'status': 'error',
                    },
                    exc_info=True
                )
                raise

        return wrapper
    return decorator


def log_graphql_query(func: Callable) -> Callable:
    """Decorator to log GraphQL query execution.

    Logs query, variables, and execution time.

    Example:
        @log_graphql_query
        def graphql_view(request):
            # GraphQL queries are logged
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()

        # Extract query from request if available
        if args and hasattr(args[0], 'POST'):
            query = args[0].POST.get('query', '')
        else:
            query = 'Unknown'

        logger.info(
            f"GraphQL query execution",
            extra={
                'query': query[:200],  # First 200 chars
                'type': 'graphql_query',
            }
        )

        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(
                f"GraphQL query completed in {elapsed:.2f}s",
                extra={
                    'elapsed_seconds': elapsed,
                    'type': 'graphql_query',
                    'status': 'success',
                }
            )
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"GraphQL query failed: {e}",
                extra={
                    'elapsed_seconds': elapsed,
                    'type': 'graphql_query',
                    'status': 'error',
                },
                exc_info=True
            )
            raise

    return wrapper
```

---

## Environment-Specific Configuration

### Development Environment

```python
# config/settings/dev.py
import logging
from config.logging.formatters import ColoredFormatter
from config.logging.handlers import get_rotating_handler
from config.logging.filters import SensitiveDataFilter, EnvironmentFilter

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'colored': {
            '()': ColoredFormatter,
            'format': '[{levelname}] {asctime} {name} - {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        },
        'detailed': {
            'format': '[{levelname}] {asctime} {name}:{funcName}:{lineno} - {message}',
            'datefmt': '%Y-%m-%d %H:%M:%S',
            'style': '{',
        },
    },

    'filters': {
        'sensitive_data': {
            '()': SensitiveDataFilter,
        },
        'environment': {
            '()': EnvironmentFilter,
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'colored',
            'filters': ['sensitive_data', 'environment'],
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/app.log',
            'maxBytes': 10485760,  # 10 MB
            'backupCount': 5,
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filters': ['sensitive_data'],
        },
    },

    'loggers': {
        'django': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
        },
        'apps': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
        },
        'api': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
        },
        'config': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
        },
    },

    'root': {
        'level': 'DEBUG',
        'handlers': ['console', 'file'],
    },
}
```

### Production Environment

```python
# config/settings/production.py
import logging
from config.logging.formatters import JSONFormatter
from config.logging.handlers import get_timed_rotating_handler
from config.logging.filters import SensitiveDataFilter, EnvironmentFilter, RequestContextFilter

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'json': {
            '()': JSONFormatter,
        },
    },

    'filters': {
        'sensitive_data': {
            '()': SensitiveDataFilter,
        },
        'environment': {
            '()': EnvironmentFilter,
        },
        'request_context': {
            '()': RequestContextFilter,
        },
    },

    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'json',
            'filters': ['sensitive_data', 'environment', 'request_context'],
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'logs/app.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'level': 'INFO',
            'formatter': 'json',
            'filters': ['sensitive_data', 'request_context'],
        },
        'error_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'logs/error.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'level': 'ERROR',
            'formatter': 'json',
            'filters': ['sensitive_data', 'request_context'],
        },
        'security_file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': 'logs/security.log',
            'when': 'midnight',
            'interval': 1,
            'backupCount': 30,
            'level': 'WARNING',
            'formatter': 'json',
            'filters': ['sensitive_data', 'request_context'],
        },
    },

    'loggers': {
        'django': {
            'level': 'WARNING',
            'handlers': ['console', 'file', 'error_file'],
        },
        'apps': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
        },
        'api': {
            'level': 'INFO',
            'handlers': ['console', 'file'],
        },
        'config.middleware.security': {
            'level': 'WARNING',
            'handlers': ['console', 'security_file'],
        },
        'config.middleware.audit': {
            'level': 'INFO',
            'handlers': ['console', 'security_file'],
        },
    },

    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file', 'error_file'],
    },
}

# Sentry configuration with performance monitoring
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn=SENTRY_DSN,
    integrations=[
        DjangoIntegration(),
        CeleryIntegration(),
    ],
    traces_sample_rate=0.1,  # 10% of transactions
    send_default_pii=False,  # Don't send PII
)
```

---

## Implementation Phases

### Phase 1: Core Logging Structure

**Effort:** 20-25 hours
**Timeline:** Week 1-2

**Tasks:**
1. Create `config/logging/` package structure
2. Implement formatters (JSON, colored)
3. Implement filters (sensitive data, environment)
4. Implement handlers (rotating files)
5. Implement context tracking
6. Move logging config from settings to new structure
7. Update settings files to import new logging config
8. Test all environments

**Deliverables:**
- Complete logging package
- Updated settings
- All tests passing
- Local development works

### Phase 2: Decorators and Utils

**Effort:** 15-20 hours
**Timeline:** Week 2-3

**Tasks:**
1. Implement logging decorators
2. Create GraphQL logging decorator
3. Add request ID generation middleware
4. Create logging utility functions
5. Add request context middleware
6. Document decorator usage
7. Add examples to codebase

**Deliverables:**
- Decorators ready for use
- Middleware for request context
- Examples and documentation
- Tests with 80%+ coverage

### Phase 3: Integration

**Effort:** 20-25 hours
**Timeline:** Week 3-4

**Tasks:**
1. Update existing code to use new logging
2. Add context to request handlers
3. Add request ID to responses (X-Request-ID header)
4. Update API views with logging decorators
5. Configure Sentry for production
6. Add performance monitoring
7. Deploy and verify in staging
8. Production deployment

**Deliverables:**
- All code using new logging
- Request IDs in responses
- Sentry integration working
- Production logs structured and searchable

---

## Code Examples

### Using in Views

```python
# apps/users/views.py
import logging
from config.logging.decorators import log_execution
from config.logging.context import set_context

logger = logging.getLogger(__name__)

@log_execution()
def get_user(request, user_id: int):
    """Get a user by ID with logging."""
    # Set request context for this request
    set_context(
        request_id=request.META.get('HTTP_X_REQUEST_ID'),
        user_id=request.user.id if request.user.is_authenticated else None,
        client_ip=request.META.get('REMOTE_ADDR'),
    )

    logger.info(
        f"Fetching user {user_id}",
        extra={'user_id': user_id}
    )

    user = get_object_or_404(User, id=user_id)

    logger.info(
        f"User {user_id} retrieved successfully",
        extra={'user_id': user_id, 'email': user.email}
    )

    return UserSerializer(user).data
```

### GraphQL Query Logging

```python
# api/schema.py
import logging
from config.logging.decorators import log_graphql_query

logger = logging.getLogger(__name__)

@log_graphql_query
def graphql_view(request):
    """GraphQL endpoint with query logging."""
    return execute_graphql_query(request)
```

### Accessing Logs

```bash
# Development (colored output)
tail -f logs/app.log

# Production (JSON lines, easily parsed)
tail -f logs/app.log | jq 'select(.level=="ERROR")'

# Search for specific user
tail -f logs/app.log | jq 'select(.user_id==123)'

# Search for specific request
tail -f logs/app.log | jq 'select(.request_id=="abc-123")'
```

---

## Testing Strategy

### Unit Tests

```python
# tests/test_logging.py
import logging
import pytest
from config.logging.formatters import JSONFormatter, ColoredFormatter
from config.logging.filters import SensitiveDataFilter

class TestJSONFormatter:
    def test_formats_as_valid_json(self):
        """Verify JSON formatter produces valid JSON."""
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='test.py',
            lineno=42,
            msg='Test message',
            args=(),
            exc_info=None,
        )
        formatter = JSONFormatter()
        output = formatter.format(record)
        # Should be valid JSON
        import json
        data = json.loads(output)
        assert data['message'] == 'Test message'
        assert data['level'] == 'INFO'

    def test_includes_request_context(self):
        """Verify request context is included in output."""
        record = logging.LogRecord(...)
        record.request_id = 'abc-123'
        record.user_id = 42
        formatter = JSONFormatter()
        output = formatter.format(record)
        data = json.loads(output)
        assert data['request_id'] == 'abc-123'
        assert data['user_id'] == 42


class TestSensitiveDataFilter:
    def test_redacts_passwords(self):
        """Verify passwords are redacted."""
        filter = SensitiveDataFilter()
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='test.py', lineno=42,
            msg='password=secret123', args=(), exc_info=None,
        )
        filter.filter(record)
        assert 'secret123' not in record.getMessage()
        assert '[REDACTED]' in record.getMessage()

    def test_redacts_tokens(self):
        """Verify tokens are redacted."""
        filter = SensitiveDataFilter()
        record = logging.LogRecord(
            name='test', level=logging.INFO, pathname='test.py', lineno=42,
            msg='token=supersecret', args=(), exc_info=None,
        )
        filter.filter(record)
        assert 'supersecret' not in record.getMessage()
```

### Integration Tests

```python
# tests/test_logging_integration.py
def test_request_logging_end_to_end(client):
    """Test logging flow for a complete request."""
    response = client.get('/api/users/123/')
    assert response.status_code == 200

    # Verify logs were created
    with open('logs/app.log') as f:
        logs = f.readlines()
        assert any('GET /api/users/123' in log for log in logs)
```

---

## Deployment & Monitoring

### Log File Locations

```bash
# Development
logs/
├── app.log         # General logs (rotates at 10MB)
└── app.log.1, .2   # Rotated backups

# Production
logs/
├── app.log         # General logs (daily rotation, 30 day retention)
├── error.log       # Error logs only (daily rotation)
├── security.log    # Security events (daily rotation)
└── sql.log         # Database queries (if DEBUG=True)
```

### Monitoring

```bash
# Check latest errors
tail -20 logs/error.log

# Count errors per hour
jq '.timestamp' logs/error.log | cut -d'T' -f1-13 | sort | uniq -c

# Find slow queries (>1s)
jq 'select(.elapsed_seconds > 1)' logs/sql.log

# Monitor security events
tail -f logs/security.log | jq '.message'
```

### Log Rotation

Logs automatically rotate based on size (dev) or time (prod).

```bash
# Check current log sizes
du -h logs/

# Archive old logs
tar -czf logs/archive/app-2025-12.tar.gz logs/app.log.*

# Delete logs older than 30 days (production)
find logs/ -name '*.log*' -mtime +30 -delete
```

---

## Next Steps

### Week 1 (Phase 1)

1. Create `config/logging/` package
2. Implement all modules (formatters, filters, handlers, context)
3. Update settings to use new logging
4. Test in development
5. Create unit tests

### Week 2 (Phase 2)

1. Implement decorators
2. Add request context middleware
3. Generate request IDs
4. Add examples to codebase
5. Create integration tests

### Week 3 (Phase 3)

1. Update existing code to use logging
2. Configure Sentry
3. Add performance monitoring
4. Deploy to staging
5. Verify in production

### Ongoing

- Monitor logs in production
- Adjust log levels based on noise
- Archive old logs
- Review logging patterns quarterly

---

## Related Documentation

- [Code Review - IP Extraction Duplication](../REVIEWS/CODE-REVIEW-2026-01-03.md#dry-violation-in-ip-extraction)
- [GDPR Compliance - Audit Logging](../GDPR/COMPLIANCE-ASSESSMENT-2026-01-03.md)
- [Syntax/Linting Report](../SYNTAX/LINTING-REPORT-2026-01-03.md)
- [Security Guidelines](../SECURITY/SECURITY.md)
