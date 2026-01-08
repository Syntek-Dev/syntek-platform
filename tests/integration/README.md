# Integration Tests

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team

---

## Overview

Integration tests verify that multiple components work together correctly. These tests
exercise real database interactions and service-to-service communication.

---

## Directory Structure

```
integration/
├── README.md              # This file
└── __init__.py
```

---

## Test Examples

Integration tests follow the same structure as unit tests but exercise multiple systems:

```python
# test_user_registration_flow.py

import pytest
from django.contrib.auth import get_user_model
from apps.core.models import Organisation

User = get_user_model()


@pytest.mark.integration
class TestUserRegistrationFlow:
    """Integration tests for user registration workflow."""

    def test_complete_registration_flow(self, db, client):
        """Test registration, email verification, and login.

        This integration test verifies:
        1. User can register with email
        2. Email verification token is created
        3. User can verify email
        4. User can login
        """
        # Step 1: Register user
        response = client.post('/api/auth/register/', {
            'email': 'newuser@example.com',
            'password': 'secret123',
            'first_name': 'New',
            'last_name': 'User',
        })

        assert response.status_code == 201
        user = User.objects.get(email='newuser@example.com')
        assert not user.email_verified

        # Step 2: Verify email (simulating link click)
        from apps.core.utils.signed_urls import verify_email_token
        token = user.email_verification_tokens.first().token
        verified = verify_email_token(token)

        assert verified is not None
        user.refresh_from_db()
        assert user.email_verified

        # Step 3: Login
        response = client.post('/api/auth/login/', {
            'email': 'newuser@example.com',
            'password': 'secret123',
        })

        assert response.status_code == 200
        assert 'token' in response.json()
```

---

## Best Practices

### 1. Test Complete Workflows

Integration tests should verify complete user flows:

```python
# Good - complete workflow
def test_organisation_setup_complete(self):
    """Test full org setup: create, configure, deploy."""
    # Create org
    # Add members
    # Configure settings
    # Deploy
    # Verify live
    pass

# Bad - isolated component
def test_organisation_model(self):
    """Test creating organisation."""
    pass
```

### 2. Use Realistic Data

Use realistic test data that mimics production scenarios:

```python
# Good
org = Organisation.objects.create(
    name="Acme Corporation",
    slug="acme-corp",
    domain="acme.example.com"
)

# Bad
org = Organisation.objects.create(
    name="Test",
    slug="t"
)
```

### 3. Clean Up After Tests

Ensure tests clean up their data:

```python
# Good - pytest handles cleanup
@pytest.fixture
def organisation(db):
    """Create test organisation (auto-cleaned)."""
    return Organisation.objects.create(name="Test")

def test_something(self, organisation):
    """Test using organisation (cleaned up after)."""
    pass

# Bad - manual cleanup needed
def test_something(self):
    org = Organisation.objects.create(name="Test")
    # ... test code ...
    # No cleanup!
```

---

**Last Updated:** 08/01/2026
