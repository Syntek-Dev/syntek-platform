# Core Managers

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team

---

## Overview

This directory is reserved for custom Django model managers for the core application.

**File Structure:**

```
managers/
└── (currently empty)
```

---

## Purpose

Custom managers encapsulate complex query logic and provide convenient methods on Django models.

**Future Managers:**

When custom managers are needed, they would be created here following this pattern:

```
managers/
├── __init__.py
├── user_manager.py           # User-related queries
├── organisation_manager.py   # Organisation-related queries
├── audit_log_manager.py      # Audit log queries
└── ...
```

**Example Manager:**

```python
# managers/user_manager.py

from django.db import models
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    """Custom manager for User model."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a user."""
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def active(self):
        """Return only active users."""
        return self.filter(is_active=True)

    def by_organisation(self, organisation):
        """Return users in specific organisation."""
        return self.filter(organisation=organisation)
```

---

## Usage in Models

```python
class User(AbstractBaseUser):
    """User model with custom manager."""

    objects = UserManager()  # Use custom manager
```

---

**Last Updated:** 08/01/2026
