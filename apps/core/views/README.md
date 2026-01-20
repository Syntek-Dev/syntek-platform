# Core Views

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team

---

## Overview

This directory contains view endpoints for the core application. Views handle HTTP requests
and return responses.

**File Structure:**

```
views/
├── __init__.py                    # View exports
└── health.py                      # Health check endpoints
```

---

## Views

### Health Check View (`health.py`)

Provides system health status endpoint for monitoring and diagnostics.

**Endpoint:** `GET /api/health/`

**Request:**

```bash
curl https://example.com/api/health/
```

**Response (200 OK):**

```json
{
  "status": "healthy",
  "database": "ok",
  "cache": "ok",
  "timestamp": "2026-01-08T12:34:56.123456Z",
  "version": "0.4.1"
}
```

**Error Response (503 Service Unavailable):**

```json
{
  "status": "unhealthy",
  "database": "error: connection refused",
  "cache": "ok",
  "timestamp": "2026-01-08T12:34:56.123456Z"
}
```

**Checks Performed:**

- Database connectivity
- Cache connectivity
- Essential services status

**Use Cases:**

- Kubernetes/Docker health probes
- Load balancer health checks
- Uptime monitoring
- Dependency verification

---

**Last Updated:** 08/01/2026
