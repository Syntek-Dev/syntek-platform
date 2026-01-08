# Test Factories

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team

---

## Overview

Factories create test data efficiently using the factory-boy library. This directory contains
factory classes for all major models.

---

## Directory Structure

```
factories/
├── __init__.py              # Factory imports
├── user_factory.py          # User model factories
├── token_factory.py         # Token model factories
└── ...                      # Other factories as needed
```

---

## Factory Files

### User Factory (`user_factory.py`)

Creates test users and organisations:

```python
from factory import Factory, SubFactory, Sequence
from factory.django import DjangoModelFactory
from apps.core.models import User, Organisation


class OrganisationFactory(DjangoModelFactory):
    """Factory for creating test organisations."""

    class Meta:
        model = Organisation

    name = Sequence(lambda n: f"Organisation {n}")
    slug = Sequence(lambda n: f"org-{n}")


class UserFactory(DjangoModelFactory):
    """Factory for creating test users."""

    class Meta:
        model = User

    email = Sequence(lambda n: f"user{n}@example.com")
    first_name = "Test"
    last_name = "User"
    organisation = SubFactory(OrganisationFactory)

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password after user creation."""
        if not create:
            return
        self.set_password(extracted or "default_password")
```

**Usage:**

```python
# Create single user
user = UserFactory()

# Create with custom data
user = UserFactory(email="custom@example.com", password="secret123")

# Create multiple users
users = UserFactory.create_batch(5)

# Create related objects
user = UserFactory(organisation=existing_org)
```

### Token Factory (`token_factory.py`)

Creates test tokens:

```python
from factory.django import DjangoModelFactory
from apps.core.models import SessionToken, PasswordResetToken


class SessionTokenFactory(DjangoModelFactory):
    """Factory for session tokens."""

    class Meta:
        model = SessionToken

    user = SubFactory(UserFactory)
    token = Sequence(lambda n: f"token-{n}")
```

---

## Using Factories in Tests

### In Unit Tests

```python
import pytest
from tests.factories import UserFactory, OrganisationFactory


@pytest.fixture
def user():
    """Fixture using factory."""
    return UserFactory()


def test_user_creation(user):
    """Test using factory-created user."""
    assert user.email is not None
    assert user.check_password("default_password")
```

### In Integration Tests

```python
def test_multiple_users(db):
    """Test with factory-created users."""
    # Create org
    org = OrganisationFactory()

    # Create multiple users in org
    users = [
        UserFactory(organisation=org)
        for _ in range(5)
    ]

    # Test interactions
    assert org.user_set.count() == 5
```

---

## Best Practices

### 1. Use Sequence for Unique Values

```python
# Good - creates unique emails
email = Sequence(lambda n: f"user{n}@example.com")

# Bad - might create duplicates
email = "test@example.com"
```

### 2. Use SubFactory for Relationships

```python
# Good - automatically creates related org
organisation = SubFactory(OrganisationFactory)

# Bad - requires manual creation
organisation_id = 1  # Hardcoded, fragile
```

### 3. Use post_generation for Complex Setup

```python
# Good - handles password hashing
@factory.post_generation
def password(self, create, extracted, **kwargs):
    if extracted:
        self.set_password(extracted)
    else:
        self.set_password("default")

# Usage
user = UserFactory(password="mypass")
```

### 4. Provide Sensible Defaults

```python
# Good - useful defaults
is_active = True
is_staff = False

# Bad - confusing defaults
is_active = False  # Why would test users be inactive?
```

---

**Last Updated:** 08/01/2026
