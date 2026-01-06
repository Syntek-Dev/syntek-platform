# Logging Implementation

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [Logging Implementation](#logging-implementation)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Available Documents](#available-documents)
    - [IMPLEMENTATION-PLAN-2026-01-03.md](#implementation-plan-2026-01-03md)
  - [Quick Start](#quick-start)
    - [1. Understanding Current Logging](#1-understanding-current-logging)
    - [2. Proposed Structure](#2-proposed-structure)
    - [3. Key Benefits](#3-key-benefits)
  - [Architecture](#architecture)
    - [Development Environment](#development-environment)
    - [Production Environment](#production-environment)
    - [Request Context Tracking](#request-context-tracking)
  - [Implementation Status](#implementation-status)
    - [Phase 1: Core Structure (Not Started)](#phase-1-core-structure-not-started)
    - [Phase 2: Decorators \& Utils (Not Started)](#phase-2-decorators--utils-not-started)
    - [Phase 3: Integration (Not Started)](#phase-3-integration-not-started)
  - [Using the Logging System](#using-the-logging-system)
    - [Basic Usage](#basic-usage)
    - [Using Decorators](#using-decorators)
    - [Request Context](#request-context)
  - [Querying Logs](#querying-logs)
    - [Development (Colored Console)](#development-colored-console)
    - [Production (JSON)](#production-json)
  - [Performance Monitoring](#performance-monitoring)
    - [With Sentry](#with-sentry)
    - [Metrics to Monitor](#metrics-to-monitor)
  - [Troubleshooting](#troubleshooting)
    - [Logs Not Appearing](#logs-not-appearing)
    - [Logs Growing Too Large](#logs-growing-too-large)
    - [Missing Context](#missing-context)
  - [Next Steps](#next-steps)
  - [Related Documents](#related-documents)

---

## Overview

This folder contains the logging system design and implementation plan for the Django backend.

**Current Status:** Basic logging configuration
**Proposed Status:** Structured JSON logging with request context tracking
**Timeline:** 3-4 weeks to implement

---

## Available Documents

### IMPLEMENTATION-PLAN-2026-01-03.md

Complete implementation guide for structured logging.

**Includes:**

- Current state analysis
- Proposed architecture
- Module breakdown
- Environment-specific configuration
- Implementation phases with detailed tasks
- Code examples
- Testing strategy
- Deployment guide

**Key Features:**

- Colored console output for development
- JSON structured logging for production
- Request ID tracking across logs
- Automatic sensitive data redaction
- Performance monitoring with decorators
- Rotating file handlers
- Sentry integration with performance tracking

---

## Quick Start

### 1. Understanding Current Logging

```python
# Current (simple)
LOGGING = {
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {'django': {'handlers': ['console']}},
}
```

### 2. Proposed Structure

```
config/logging/
├── __init__.py        # Public API
├── formatters.py      # JSON and colored formatting
├── filters.py         # Sensitive data redaction
├── handlers.py        # Rotating file handlers
├── decorators.py      # Function logging decorators
└── context.py         # Request context tracking
```

### 3. Key Benefits

| Benefit                | Use Case                                  |
| ---------------------- | ----------------------------------------- |
| JSON formatting        | Production - easily parsed and searchable |
| Colored output         | Development - human readable              |
| Request IDs            | Track requests across multiple logs       |
| Context tracking       | Correlate logs with user ID and client IP |
| Automatic redaction    | Prevent PII leakage to logs               |
| Performance monitoring | Identify slow operations                  |
| Rotating logs          | Manage disk space automatically           |

---

## Architecture

### Development Environment

**Console Output (Colored):**

```
[INFO] 2026-01-03 14:30:42 config.middleware.audit - User 123 logged in
[WARNING] 2026-01-03 14:30:43 apps.api.views - Slow query (1.2s)
[ERROR] 2026-01-03 14:30:44 apps.users.models - User update failed
```

**File Output (Rotating):**

- `logs/app.log` - All logs (rotates at 10MB)

### Production Environment

**Console Output (JSON):**

<!-- prettier-ignore -->
```json
{"timestamp":"2026-01-03T14:30:42Z","level":"INFO","logger":"config.middleware.audit","message":"User 123 logged in","request_id":"abc-123","user_id":123}
{"timestamp":"2026-01-03T14:30:43Z","level":"WARNING","logger":"apps.api.views","message":"Slow query (1.2s)","elapsed_seconds":1.2}
{"timestamp":"2026-01-03T14:30:44Z","level":"ERROR","logger":"apps.users.models","message":"User update failed","exception":{"type":"IntegrityError","message":"Duplicate entry"}}
```

**File Output (Daily Rotation, 30-day retention):**

- `logs/app.log` - All INFO+ logs
- `logs/error.log` - ERROR+ logs only
- `logs/security.log` - Security events (authentication, authorization)
- `logs/sql.log` - Database queries (dev only)

### Request Context Tracking

Every request gets a unique ID that flows through all logs:

```
Request: GET /api/users/123/
├─ Middleware generates request_id: "req-abc-123-def"
├─ Set in thread-local context
├─ All logs in this request include request_id
├─ Response includes X-Request-ID header
└─ Can search logs by request_id
```

---

## Implementation Status

### Phase 1: Core Structure (Not Started)

- [ ] Create `config/logging/` package
- [ ] Implement formatters (JSON, colored)
- [ ] Implement filters (sensitive data, environment)
- [ ] Implement handlers (rotating files)
- [ ] Implement context tracking
- [ ] Update settings

**Timeline:** Week 1-2
**Effort:** 20-25 hours

### Phase 2: Decorators & Utils (Not Started)

- [ ] Implement logging decorators
- [ ] Create GraphQL logging decorator
- [ ] Add request ID middleware
- [ ] Create utility functions
- [ ] Add context middleware
- [ ] Document usage

**Timeline:** Week 2-3
**Effort:** 15-20 hours

### Phase 3: Integration (Not Started)

- [ ] Update existing code
- [ ] Add context to views
- [ ] Add request IDs to responses
- [ ] Configure Sentry
- [ ] Deploy to staging
- [ ] Production verification

**Timeline:** Week 3-4
**Effort:** 20-25 hours

---

## Using the Logging System

### Basic Usage

```python
import logging

logger = logging.getLogger(__name__)

# Simple logging
logger.info("User logged in")
logger.warning("Slow operation")
logger.error("Database error")

# With context
logger.info(
    "User action",
    extra={'user_id': 123, 'action': 'update_profile'}
)
```

### Using Decorators

```python
from config.logging.decorators import log_execution

@log_execution()  # Logs execution time automatically
def process_user_data(user_id: int):
    # Function is logged with timing
    pass
```

### Request Context

```python
from config.logging.context import set_context

def my_view(request):
    # Set context for this request
    set_context(
        request_id=request.META.get('HTTP_X_REQUEST_ID'),
        user_id=request.user.id,
        client_ip=request.META.get('REMOTE_ADDR'),
    )

    # All logs now include request_id, user_id, client_ip
    logger.info("Processing request")
```

---

## Querying Logs

### Development (Colored Console)

```bash
# Watch logs in real-time
tail -f logs/app.log

# Filter by level
grep ERROR logs/app.log
grep WARNING logs/app.log

# Search for specific text
grep "user_id" logs/app.log
```

### Production (JSON)

```bash
# Watch error logs
tail -f logs/error.log | jq '.message'

# Find errors
jq 'select(.level=="ERROR")' logs/app.log

# Find specific user
jq 'select(.user_id==123)' logs/app.log

# Find specific request
jq 'select(.request_id=="abc-123")' logs/app.log

# Count errors by type
jq '.exception.type' logs/error.log | sort | uniq -c

# Find slow operations (>1 second)
jq 'select(.elapsed_seconds > 1)' logs/app.log
```

---

## Performance Monitoring

### With Sentry

Logs are automatically sent to Sentry for:

- Error tracking
- Performance monitoring
- Release tracking
- User feedback

### Metrics to Monitor

| Metric        | Target     | Alert      |
| ------------- | ---------- | ---------- |
| Slow requests | <200ms p95 | >500ms     |
| Error rate    | <0.1%      | >1%        |
| Log volume    | <10MB/hour | >50MB/hour |

---

## Troubleshooting

### Logs Not Appearing

1. Check log level: `logger.setLevel(logging.DEBUG)`
2. Verify logger is configured: Check `LOGGING` in settings
3. Check file permissions: `ls -la logs/`

### Logs Growing Too Large

1. Check rotation settings (maxBytes, backupCount)
2. Increase backup count or max size
3. Archive old logs: `tar -czf logs/archive/logs-2025-12.tar.gz logs/`

### Missing Context

1. Verify context is set in middleware
2. Check `RequestContextFilter` is enabled
3. Verify thread-local storage is working

---

## Next Steps

1. Read [IMPLEMENTATION-PLAN-2026-01-03.md](IMPLEMENTATION-PLAN-2026-01-03.md)
2. Review proposed architecture
3. Schedule implementation sprints
4. Create tasks in ClickUp
5. Start Phase 1

---

## Related Documents

- [Code Review - IP Extraction](../REVIEWS/CODE-REVIEW-2026-01-03.md)
- [GDPR Compliance - Audit Logging](../GDPR/COMPLIANCE-ASSESSMENT-2026-01-03.md)
- [Syntax/Linting Report](../SYNTAX/LINTING-REPORT-2026-01-03.md)
- [Security Guidelines](../SECURITY/SECURITY.md)
