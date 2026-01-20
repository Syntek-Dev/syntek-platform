# Test Fixtures

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team

---

## Overview

Fixtures provide reusable test data and setup/teardown logic using pytest fixtures.

---

## Directory Structure

```
fixtures/
├── __init__.py              # Fixture exports
└── (other fixture files as needed)
```

---

## Fixture Patterns

### Database Fixtures

```python
# conftest.py or fixtures/__init__.py

import pytest
from apps.core.models import User, Organisation


@pytest.fixture
def organisation(db):
    """Create a test organisation."""
    return Organisation.objects.create(
        name="Test Organisation",
        slug="test-org"
    )


@pytest.fixture
def user(db, organisation):
    """Create a test user."""
    return User.objects.create_user(
        email="test@example.com",
        password="test123",
        organisation=organisation
    )
```

**Usage in Tests:**

```python
def test_user_login(user):
    """Test using organisation and user fixtures."""
    assert user.email == "test@example.com"
    assert user.organisation.name == "Test Organisation"
```

### Client Fixtures

```python
@pytest.fixture
def authenticated_client(db, client, user):
    """Client logged in as test user."""
    client.force_login(user)
    return client


@pytest.fixture
def api_client(client):
    """REST API client."""
    from rest_framework.test import APIClient
    return APIClient()
```

### Scope Fixtures

Fixtures can have different scopes:

```python
# Function scope (default - created per test)
@pytest.fixture
def user(db):
    return User.objects.create_user(...)

# Session scope (created once per test session)
@pytest.fixture(scope="session")
def django_db_setup():
    """Set up test database once."""
    pass

# Module scope (created once per test module)
@pytest.fixture(scope="module")
def test_data(db):
    """Shared test data for all tests in module."""
    return create_shared_data()
```

---

## Best Practices

### 1. Use Parametrized Fixtures

```python
@pytest.fixture(params=["valid@example.com", "invalid", "another@test.com"])
def emails(request):
    """Provide multiple email values."""
    return request.param


def test_email_validation(emails):
    """Test with multiple email values."""
    result = validate_email(emails)
    # Test validates for each email
```

### 2. Create Dependent Fixtures

```python
@pytest.fixture
def organisation(db):
    return Organisation.objects.create(name="Test")


@pytest.fixture
def user(db, organisation):
    """Depends on organisation fixture."""
    return User.objects.create_user(
        email="user@example.com",
        organisation=organisation
    )
```

### 3. Return Resources, Not IDs

```python
# Good - returns model instance
@pytest.fixture
def user(db):
    return User.objects.create_user(...)

# Bad - returns just ID
@pytest.fixture
def user_id(db):
    user = User.objects.create_user(...)
    return user.id
```

### 4. Use Fixture Factories

```python
@pytest.fixture
def user_factory(db):
    """Factory-style fixture."""
    def create_user(**kwargs):
        defaults = {"email": "user@example.com"}
        defaults.update(kwargs)
        return User.objects.create_user(**defaults)
    return create_user


def test_multiple_users(user_factory):
    """Create multiple users with fixture."""
    user1 = user_factory(email="user1@example.com")
    user2 = user_factory(email="user2@example.com")
    # ...
```

---

**Last Updated:** 08/01/2026
