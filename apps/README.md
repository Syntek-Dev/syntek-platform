# Django Applications

Container directory for all Django application modules.

## Table of Contents

- [Django Applications](#django-applications)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Structure](#structure)
  - [Creating New Apps](#creating-new-apps)
    - [Step 1: Create App Structure](#step-1-create-app-structure)
    - [Step 2: Create README](#step-2-create-readme)
    - [Step 3: Register App](#step-3-register-app)
    - [Step 4: Create Models](#step-4-create-models)
    - [Step 5: Create Serializers](#step-5-create-serializers)
    - [Step 6: Create Migrations](#step-6-create-migrations)
    - [Step 7: Create Tests](#step-7-create-tests)
  - [App Organization](#app-organization)
    - [Optional: Separate Test File](#optional-separate-test-file)
    - [Services Layer](#services-layer)
    - [Custom Managers](#custom-managers)
  - [Best Practices](#best-practices)
    - [1. Module Docstrings](#1-module-docstrings)
    - [2. Type Hints](#2-type-hints)
    - [3. Google-Style Docstrings](#3-google-style-docstrings)
    - [4. Model Metadata](#4-model-metadata)
    - [5. App Configuration](#5-app-configuration)
    - [6. Admin Registration](#6-admin-registration)
    - [7. Testing](#7-testing)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains all Django applications (apps) for the project. Each app is a self-contained module with its own models, views, serializers, and tests.

**Key Principle:** Each app should be reusable and not tightly coupled to other apps.

---

## Structure

The `apps/` directory is organized by feature or domain:

```
apps/
├── __init__.py              # Package initialization
├── [app_name]/              # Django application directory
│   ├── migrations/          # Database migrations
│   ├── __init__.py
│   ├── admin.py             # Django admin configuration
│   ├── apps.py              # App configuration
│   ├── models.py            # Data models
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # Class-based views
│   ├── forms.py             # Django forms (if needed)
│   ├── urls.py              # URL routing (if needed)
│   ├── filters.py           # Query filters
│   ├── managers.py          # Custom model managers
│   ├── services.py          # Business logic
│   └── tests.py             # Unit tests
└── [app_name]/
    └── ...
```

---

## Creating New Apps

### Step 1: Create App Structure

```bash
# Use Django's startapp command inside Docker
./scripts/env/dev.sh startapp [app_name]

# This creates the basic structure
```

### Step 2: Create README

Create a `README.md` in the app directory describing:

```markdown
# [App Name]

## Overview

Brief description of what the app does.

## Models

List of models and their relationships.

## API Endpoints

List of exposed endpoints or GraphQL queries.

## Configuration

Any special setup or configuration needed.
```

### Step 3: Register App

Edit `config/settings/base.py` to add the app:

```python
INSTALLED_APPS = [
    # ...
    "apps.[app_name]",
    # ...
]
```

### Step 4: Create Models

Edit `apps/[app_name]/models.py`:

```python
"""Models for [app_name] app.

This module defines the data models for the [app_name] functionality.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class MyModel(models.Model):
    """Description of the model.

    Attributes:
        name: Name of the model.
        created_at: Timestamp when created.
        updated_at: Timestamp when updated.
    """

    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("My Model")
        verbose_name_plural = _("My Models")

    def __str__(self) -> str:
        """Return the model's name."""
        return self.name
```

### Step 5: Create Serializers

Edit `apps/[app_name]/serializers.py`:

```python
"""Serializers for [app_name] app."""

from rest_framework import serializers
from apps.[app_name].models import MyModel


class MyModelSerializer(serializers.ModelSerializer):
    """Serialize MyModel for API responses.

    Fields:
        id: Model ID
        name: Model name
        created_at: Creation timestamp
    """

    class Meta:
        model = MyModel
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "created_at"]
```

### Step 6: Create Migrations

```bash
# Create migration files
./scripts/env/dev.sh makemigrations

# Run migrations
./scripts/env/dev.sh migrate
```

### Step 7: Create Tests

Edit `apps/[app_name]/tests.py`:

```python
"""Tests for [app_name] app."""

from django.test import TestCase
from apps.[app_name].models import MyModel


class MyModelTestCase(TestCase):
    """Test cases for MyModel."""

    def setUp(self) -> None:
        """Create test data."""
        self.model = MyModel.objects.create(name="Test")

    def test_model_creation(self) -> None:
        """Test that model is created correctly."""
        self.assertEqual(self.model.name, "Test")
        self.assertIsNotNone(self.model.created_at)
```

---

## App Organization

### Optional: Separate Test File

For large apps, create a `tests/` directory:

```
apps/[app_name]/
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_serializers.py
│   └── test_services.py
└── ...
```

### Services Layer

For complex business logic, create `services.py`:

```python
"""Business logic services for [app_name] app."""

from apps.[app_name].models import MyModel


class MyModelService:
    """Service class for MyModel business operations."""

    @staticmethod
    def create_with_validation(name: str) -> MyModel:
        """Create a model with custom validation.

        Args:
            name: The model name.

        Returns:
            The created MyModel instance.

        Raises:
            ValueError: If name is invalid.
        """
        if not name or len(name) < 3:
            raise ValueError("Name must be at least 3 characters")

        return MyModel.objects.create(name=name)
```

### Custom Managers

For complex queries, create `managers.py`:

```python
"""Custom model managers for [app_name] app."""

from django.db import models


class MyModelManager(models.Manager):
    """Custom manager for MyModel with helper methods."""

    def active(self):
        """Return only active models."""
        return self.filter(is_active=True)

    def recent(self, days: int = 7):
        """Return models from the last N days."""
        from datetime import timedelta
        from django.utils import timezone

        since = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=since)
```

---

## Best Practices

### 1. Module Docstrings

Always include module docstrings:

```python
"""Models for the [app_name] app.

This module contains data models for [brief description].
"""
```

### 2. Type Hints

Use type hints on all functions:

```python
def get_models(count: int = 10) -> List[MyModel]:
    """Get models."""
    return list(MyModel.objects.all()[:count])
```

### 3. Google-Style Docstrings

Follow Google-style docstring format:

```python
def process_data(data: dict) -> bool:
    """Process incoming data.

    Args:
        data: Dictionary containing data to process.

    Returns:
        True if processing succeeded, False otherwise.

    Raises:
        ValueError: If data validation fails.
    """
    pass
```

### 4. Model Metadata

Always define Meta class:

```python
class Meta:
    ordering = ["-created_at"]
    indexes = [
        models.Index(fields=["status", "-created_at"]),
    ]
    verbose_name = _("My Model")
    verbose_name_plural = _("My Models")
```

### 5. App Configuration

Update `apps.py`:

```python
"""Configuration for [app_name] app."""

from django.apps import AppConfig


class [AppName]Config(AppConfig):
    """App configuration for [app_name]."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.[app_name]"
    verbose_name = "[App Name]"
```

### 6. Admin Registration

Register models in `admin.py`:

```python
"""Django admin configuration for [app_name] app."""

from django.contrib import admin
from apps.[app_name].models import MyModel


@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    """Admin interface for MyModel."""

    list_display = ["name", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["created_at", "updated_at"]
```

### 7. Testing

Write tests for all business logic:

```python
"""Tests for [app_name] app."""

from django.test import TestCase, Client
from apps.[app_name].models import MyModel


class MyModelTestCase(TestCase):
    """Test cases for MyModel model."""

    def setUp(self) -> None:
        """Set up test data."""
        self.model = MyModel.objects.create(name="Test Model")

    def test_model_creation(self) -> None:
        """Test model creation."""
        self.assertIsNotNone(self.model.id)
        self.assertEqual(self.model.name, "Test Model")

    def test_string_representation(self) -> None:
        """Test __str__ method."""
        self.assertEqual(str(self.model), "Test Model")
```

---

## Related Documentation

- [Django Models](https://docs.djangoproject.com/en/5.2/topics/db/models/) - Official Django models documentation
- [Documentation Standards](../.claude/CLAUDE.md) - Project docstring and code standards
- [Testing Guide](../docs/GUIDES/TESTING.md) - Testing guidelines
- [Code Review](../docs/REVIEWS/README.md) - Code quality expectations

---

**Last Updated:** 2026-01-03
