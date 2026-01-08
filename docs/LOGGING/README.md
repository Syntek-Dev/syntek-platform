# Logging Implementation

**Last Updated**: 08/01/2026
**Version**: 0.4.1
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

**Current Status:** Phase 1 + 2 Complete (Database audit trail with IP encryption)
**Next Phase:** Phase 3 - GraphQL integration with audit logging
**Future Phase:** Phase 6 - Structured application logging with file rotation

---

## Available Documents

### US-001/LOGGING-REPORT-US-001.md

**Status**: ✅ Phase 1 + 2 Complete

Comprehensive logging and audit implementation report for US-001 User Authentication.

**Covers**:

- Phase 1: Database audit trail implementation
- Phase 2: Service layer with IP encryption and token security
- AuditService with encrypted IP storage
- IPEncryption utility with key rotation
- TokenHasher with HMAC-SHA256 and hash-then-store pattern
- Security best practices and GDPR compliance
- Testing status and gap analysis

**Key Achievements**:

- ✅ `AuditLog` model with encrypted IP addresses
- ✅ `AuditService` for centralised audit logging
- ✅ `IPEncryption` with Fernet encryption and key rotation
- ✅ `TokenHasher` with HMAC-SHA256 hashing
- ✅ Comprehensive unit tests (30+ test cases)

### IMPLEMENTATION-PLAN-2026-01-03.md

Complete implementation guide for structured application logging (Phase 6 - Deferred).

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

### Phase 1: Core Models and Database (✅ Complete)

- [x] `AuditLog` model with encrypted IP storage
- [x] Composite indexes for multi-tenant queries
- [x] Django Admin configuration (read-only)
- [x] `SecurityAuditMiddleware` for HTTP events
- [x] Unit tests (30+ test cases)

**Status:** ✅ Complete
**Branch:** `us001/user-authentication`

### Phase 2: Authentication Service Layer (✅ Complete)

- [x] `AuditService` - Centralised audit logging
- [x] `IPEncryption` - Fernet encryption with key rotation
- [x] `TokenHasher` - HMAC-SHA256 token hashing
- [x] `AuthService` - Authentication with race condition prevention
- [x] `TokenService` - Token management with replay detection
- [x] `PasswordResetService` - Hash-then-store pattern
- [x] Comprehensive unit tests for services and utilities

**Status:** ✅ Complete
**Branch:** `us001/user-authentication`

### Phase 3: GraphQL Integration (⚠️ In Progress)

- [ ] Integrate `AuditService` in GraphQL mutations
- [ ] Device fingerprinting utility
- [ ] GraphQL queries for viewing audit logs
- [ ] Organisation boundary enforcement
- [ ] Integration tests for audit flow

**Status:** Next phase
**Branch:** `us001/user-authentication`

### Phase 6: Production Logging (🔴 Deferred)

- [ ] File-based logging with rotation
- [ ] Audit log retention policy (90 days)
- [ ] Request ID tracking middleware
- [ ] Performance logging decorators
- [ ] Centralised log aggregation

**Status:** Deferred to Phase 6
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

1. Read [US-001/LOGGING-REPORT-US-001.md](US-001/LOGGING-REPORT-US-001.md) for current implementation
2. **Phase 3 (GraphQL):**
   - Integrate `AuditService` calls in GraphQL mutations
   - Implement device fingerprinting utility
   - Add GraphQL queries for audit logs
3. **Phase 6 (Production):**
   - Read [IMPLEMENTATION-PLAN-2026-01-03.md](IMPLEMENTATION-PLAN-2026-01-03.md) for file logging architecture
   - Implement file rotation and retention policies
   - Add request ID tracking

---

## Related Documents

**US-001 User Authentication**:

- [Logging Report - US-001](US-001/LOGGING-REPORT-US-001.md) - Phase 1 + 2 implementation
- [User Authentication Plan](../PLANS/US-001-USER-AUTHENTICATION.md) - Complete plan
- [QA Report - US-001](../QA/US-001/QA-US-001-REPORT.md) - Security requirements
- [Security Implementation - US-001](../SECURITY/US-001/SECURITY-US-001-IMPLEMENTATION.md)

**General Logging**:

- [Implementation Plan](IMPLEMENTATION-PLAN-2026-01-03.md) - File logging (Phase 6)
- [GDPR Compliance](../GDPR/COMPLIANCE-ASSESSMENT-2026-01-03.md)
- [Security Guidelines](../SECURITY/SECURITY.md)
