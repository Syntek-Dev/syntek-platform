# Core Services

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team

---

## Overview

This directory contains business logic services for the core application. Services encapsulate
complex operations and permission checking to keep models and views lean.

**File Structure:**

```
services/
├── __init__.py                    # Service exports
└── permission_service.py          # Multi-tenancy permission checking
```

---

## Services

### Permission Service (`permission_service.py`)

Handles all permission checking and multi-tenancy boundary enforcement.

**Key Methods:**

| Method                           | Purpose                                        | Returns    |
| -------------------------------- | ---------------------------------------------- | ---------- |
| `has_organisation_access()`      | Check if user can access organisation          | `bool`     |
| `get_user_organisations()`       | List all organisations user belongs to         | `QuerySet` |
| `can_manage_user()`              | Check if user can modify target user           | `bool`     |
| `can_view_audit_logs()`          | Check if user can view organisation audit logs | `bool`     |
| `filter_by_organisation()`       | Filter queryset to user's tenant               | `QuerySet` |
| `get_user_permissions()`         | Get user's permissions in organisation         | `list`     |
| `validate_multi_tenancy_scope()` | Ensure request stays within tenant boundaries  | `bool`     |

**Usage Example:**

```python
from apps.core.services.permission_service import PermissionService

service = PermissionService()

# Check access
if not service.has_organisation_access(user, org):
    raise PermissionError("Access denied")

# Get scoped queryset
users = service.filter_by_organisation(User.objects.all(), user)
```

---

**Last Updated:** 08/01/2026
