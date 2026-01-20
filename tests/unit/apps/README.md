# Unit Tests - App Tests

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team

---

## Overview

This directory contains unit tests organised by Django app.

**File Structure:**

```
apps/
├── README.md              # This file
├── core/                  # Core app tests
│   ├── test_models.py
│   ├── test_services.py
│   └── ...
└── [other_apps]/          # Other app tests
```

---

## Organisation

Tests mirror the source code structure:

```
Source Code:                    Unit Tests:
apps/core/models/user.py        apps/core/test_user_model.py
apps/core/services/...          apps/core/test_permission_service.py
apps/core/views/health.py       apps/core/test_health_view.py
```

---

## Naming Convention

Test files are named `test_[component].py`:

- `test_models.py` - Model tests
- `test_services.py` - Service layer tests
- `test_views.py` - View/endpoint tests
- `test_serializers.py` - Serializer tests
- `test_utils.py` - Utility function tests

---

**Last Updated:** 08/01/2026
