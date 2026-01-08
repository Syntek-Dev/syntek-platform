# Test Suite

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

Automated tests for the Django backend application.

## Table of Contents

- [Test Suite](#test-suite)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Test Organization](#test-organization)
  - [Running Tests](#running-tests)
    - [All Tests](#all-tests)
    - [Specific Test File](#specific-test-file)
    - [Specific Test Class](#specific-test-class)
    - [Specific Test Method](#specific-test-method)
    - [With Coverage](#with-coverage)
    - [Parallel Execution](#parallel-execution)
  - [Writing Tests](#writing-tests)
    - [Test Structure](#test-structure)
    - [Model Tests](#model-tests)
    - [View Tests](#view-tests)
    - [API Tests](#api-tests)
  - [Coverage](#coverage)
    - [Generate Coverage Report](#generate-coverage-report)
    - [View HTML Report](#view-html-report)
    - [Coverage Goals](#coverage-goals)
  - [Best Practices](#best-practices)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains the test suite for the backend template project. Tests ensure code
quality, prevent regressions, and document expected behavior.

**Tool:** pytest with Django plugin
**Coverage Target:** 80% or higher

---

## Test Organization

Tests are organized by test type and module being tested:

```
tests/
├── README.md                # This file
├── conftest.py              # pytest configuration and global fixtures
├── bdd/                     # BDD behaviour tests (Gherkin)
│   ├── conftest.py         # BDD-specific fixtures
│   ├── features/           # Gherkin feature files
│   │   └── user_registration.feature
│   └── step_defs/          # Step definitions for features
│       └── test_user_registration_steps.py
├── e2e/                     # End-to-end tests (complete workflows)
│   └── __init__.py
├── factories/               # Test data factories
│   ├── token_factory.py    # Token factory for tests
│   └── user_factory.py     # User factory for tests
├── fixtures/                # Test fixtures and sample data
│   └── __init__.py
├── graphql/                 # GraphQL API tests
│   └── __init__.py
├── integration/             # Integration tests (multiple components)
│   └── __init__.py
└── unit/                    # Unit tests (TDD - fast, isolated)
    ├── apps/               # Tests for each Django app
    │   └── core/           # Core app tests
    │       ├── test_audit_log_model.py
    │       ├── test_base_token_model.py
    │       ├── test_email_verification_token_model.py
    │       ├── test_organisation_model.py
    │       ├── test_password_history_model.py
    │       ├── test_password_reset_token_model.py
    │       ├── test_session_token_model.py
    │       ├── test_totp_device_model.py
    │       ├── test_user_manager.py
    │       ├── test_user_model.py
    │       ├── test_user_profile_model.py
    │       └── test_validators.py
    └── __init__.py
```

---

## Running Tests

### All Tests

```bash
./scripts/env/test.sh run
```

### Specific Test File

```bash
./scripts/env/test.sh run tests/test_models.py
```

### Specific Test Class

```bash
./scripts/env/test.sh run tests/test_models.py::MyModelTestCase
```

### Specific Test Method

```bash
./scripts/env/test.sh run tests/test_models.py::MyModelTestCase::test_creation
```

### With Coverage

```bash
./scripts/env/test.sh coverage
```

### Parallel Execution

```bash
./scripts/env/test.sh run -n auto
```

---

## Writing Tests

### Test Structure

```python
"""Tests for models module."""

from django.test import TestCase
from apps.myapp.models import MyModel


class MyModelTestCase(TestCase):
    """Test cases for MyModel."""

    def setUp(self) -> None:
        """Create test data."""
        self.object = MyModel.objects.create(name="Test")

    def test_model_creation(self) -> None:
        """Test that model is created correctly."""
        self.assertIsNotNone(self.object.id)
        self.assertEqual(self.object.name, "Test")

    def test_string_representation(self) -> None:
        """Test __str__ method."""
        self.assertEqual(str(self.object), "Test")
```

### Model Tests

```python
from django.test import TestCase
from apps.myapp.models import MyModel


class MyModelTestCase(TestCase):
    """Test model functionality."""

    def test_valid_data(self) -> None:
        """Test with valid data."""
        obj = MyModel.objects.create(name="Test", email="test@example.com")
        self.assertTrue(obj.id)

    def test_invalid_email(self) -> None:
        """Test with invalid email."""
        with self.assertRaises(ValidationError):
            obj = MyModel(name="Test", email="invalid")
            obj.full_clean()
```

### View Tests

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User


class MyViewTestCase(TestCase):
    """Test view functionality."""

    def setUp(self) -> None:
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123"
        )

    def test_view_requires_authentication(self) -> None:
        """Test view requires login."""
        response = self.client.get("/myview/")
        self.assertEqual(response.status_code, 302)  # Redirect

    def test_authenticated_user_access(self) -> None:
        """Test authenticated user can access."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/myview/")
        self.assertEqual(response.status_code, 200)
```

### API Tests

```python
import json
from django.test import TestCase, Client


class MyAPITestCase(TestCase):
    """Test GraphQL API."""

    def setUp(self) -> None:
        """Set up test client."""
        self.client = Client()

    def test_query_execution(self) -> None:
        """Test GraphQL query."""
        query = """
        query {
            myField {
                id
                name
            }
        }
        """

        response = self.client.post(
            "/graphql/",
            json.dumps({"query": query}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIsNotNone(data.get("data"))
```

---

## Coverage

### Generate Coverage Report

```bash
./scripts/env/test.sh coverage
```

### View HTML Report

```bash
# After running coverage
open htmlcov/index.html
```

### Coverage Goals

| Module      | Target |
| ----------- | ------ |
| models      | 90%    |
| views       | 85%    |
| serializers | 85%    |
| services    | 90%    |
| Overall     | 80%    |

---

## Best Practices

1. **Test One Thing:** Each test should verify one behavior
2. **Clear Names:** Test names should describe what is being tested
3. **Arrange-Act-Assert:** Structure tests with setup, action, assertion
4. **Use Fixtures:** Reuse test data with setUp() methods
5. **Mock External:** Mock external APIs and services
6. **Keep Fast:** Unit tests should complete in seconds

---

## Related Documentation

- [Testing Guide](../docs/GUIDES/TESTING.md) - Detailed testing guide
- [Setup](../docs/DEVELOPER-SETUP.md) - Development setup
- [pytest Documentation](https://docs.pytest.org/) - pytest docs

---

**Last Updated:** 2026-01-03
