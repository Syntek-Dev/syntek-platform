# Unit Tests

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team

---

## Overview

Unit tests verify individual components in isolation. These are fast, focused tests for models,
services, utilities, and other business logic.

---

## Table of Contents

- [Unit Tests](#unit-tests)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Directory Structure](#directory-structure)
  - [Test File Organization](#test-file-organization)
  - [Writing Unit Tests](#writing-unit-tests)
    - [Basic Test Structure](#basic-test-structure)
  - [Running Unit Tests](#running-unit-tests)
    - [Run All Unit Tests](#run-all-unit-tests)
    - [Run with Coverage](#run-with-coverage)
    - [Run Specific Test File](#run-specific-test-file)
    - [Run Specific Test Class](#run-specific-test-class)
    - [Run Specific Test Method](#run-specific-test-method)
    - [Run with Verbose Output](#run-with-verbose-output)
  - [Best Practices](#best-practices)
    - [1. Test One Thing](#1-test-one-thing)
    - [2. Use Descriptive Names](#2-use-descriptive-names)
    - [3. Use Fixtures](#3-use-fixtures)
    - [4. Test Both Success and Failure Cases](#4-test-both-success-and-failure-cases)
    - [5. Use pytest Markers](#5-use-pytest-markers)

---

## Directory Structure

```
unit/
├── README.md              # This file
├── __init__.py
└── apps/
    └── core/              # Tests for core app
        ├── test_models.py
        ├── test_services.py
        └── ...
```

---

## Test File Organization

Tests are organised to mirror the source code structure:

```
Source:                        Tests:
apps/core/models/user.py       tests/unit/apps/core/test_user_model.py
apps/core/services/...         tests/unit/apps/core/test_permission_service.py
apps/core/utils/...            tests/unit/apps/core/test_signed_urls.py
```

---

## Writing Unit Tests

### Basic Test Structure

```python
# test_user_model.py

import pytest
from django.contrib.auth import get_user_model
from apps.core.models import Organisation

User = get_user_model()


class TestUserModel:
    """Unit tests for User model."""

    @pytest.fixture
    def organisation(self, db):
        """Create a test organisation."""
        return Organisation.objects.create(
            name="Test Org",
            slug="test-org"
        )

    def test_user_creation(self, db, organisation):
        """Test user can be created with valid data."""
        user = User.objects.create_user(
            email="test@example.com",
            password="secret123",
            first_name="Test",
            last_name="User",
            organisation=organisation
        )

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.check_password("secret123")

    def test_user_email_must_be_unique(self, db, organisation):
        """Test user email must be unique."""
        User.objects.create_user(
            email="test@example.com",
            organisation=organisation
        )

        with pytest.raises(Exception):  # IntegrityError
            User.objects.create_user(
                email="test@example.com",
                organisation=organisation
            )

    def test_full_name_property(self, db, organisation):
        """Test get_full_name() method."""
        user = User.objects.create_user(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            organisation=organisation
        )

        assert user.get_full_name() == "John Doe"
```

---

## Running Unit Tests

### Run All Unit Tests

```bash
./scripts/env/test.sh run tests/unit/
```

### Run with Coverage

```bash
./scripts/env/test.sh coverage tests/unit/
```

### Run Specific Test File

```bash
./scripts/env/test.sh run tests/unit/apps/core/test_user_model.py
```

### Run Specific Test Class

```bash
./scripts/env/test.sh run tests/unit/apps/core/test_user_model.py::TestUserModel
```

### Run Specific Test Method

```bash
./scripts/env/test.sh run tests/unit/apps/core/test_user_model.py::TestUserModel::test_user_creation
```

### Run with Verbose Output

```bash
./scripts/env/test.sh run -vv tests/unit/
```

---

## Best Practices

### 1. Test One Thing

Each test should verify one behaviour:

```python
# Good - tests one thing
def test_user_password_is_hashed(self, db, organisation):
    """Test password is hashed, not stored as plain text."""
    user = User.objects.create_user(
        email="test@example.com",
        password="secret123",
        organisation=organisation
    )

    assert user.password != "secret123"
    assert user.check_password("secret123")

# Bad - tests multiple things
def test_user_creation_and_password(self, db, organisation):
    """Test user and password."""
    user = User.objects.create_user(
        email="test@example.com",
        password="secret123",
        organisation=organisation
    )

    assert user.id is not None
    assert user.email == "test@example.com"
    assert user.check_password("secret123")
    assert user.is_active
    # ... many more assertions
```

### 2. Use Descriptive Names

Test names should explain what is being tested:

```python
# Good
def test_user_email_must_be_unique(self)
def test_password_is_hashed_on_save(self)
def test_inactive_users_are_filtered(self)

# Bad
def test_user(self)
def test_password(self)
def test_filter(self)
```

### 3. Use Fixtures

Fixtures create test data and setup:

```python
@pytest.fixture
def user(db, organisation):
    """Create a test user."""
    return User.objects.create_user(
        email="test@example.com",
        organisation=organisation
    )

def test_user_with_fixture(self, user):
    """Use fixture for test setup."""
    assert user.email == "test@example.com"
```

### 4. Test Both Success and Failure Cases

```python
# Good - tests both cases
def test_valid_email(self):
    """Test valid email passes validation."""
    assert is_valid_email("test@example.com") is True

def test_invalid_email(self):
    """Test invalid email fails validation."""
    assert is_valid_email("not-an-email") is False

# Bad - only tests success
def test_email(self):
    """Test email."""
    assert is_valid_email("test@example.com") is True
```

### 5. Use pytest Markers

Mark tests with categories:

```python
@pytest.mark.unit
def test_user_model(self):
    """Fast, isolated unit test."""
    pass

@pytest.mark.slow
def test_complex_calculation(self):
    """Slow test that should run separately."""
    pass
```

---

**Last Updated:** 08/01/2026
