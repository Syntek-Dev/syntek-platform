# End-to-End Tests

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team

---

## Overview

End-to-end (E2E) tests verify complete user workflows across the entire system. These tests
exercise the full stack from API endpoints through database operations.

---

## Directory Structure

```
e2e/
├── README.md              # This file
└── __init__.py
```

---

## Test Structure

E2E tests simulate real user scenarios:

```python
# test_user_onboarding_e2e.py

import pytest
from django.test import Client
from django.contrib.auth import get_user_model
from apps.core.models import Organisation, SessionToken

User = get_user_model()


@pytest.mark.e2e
class TestUserOnboardingE2E:
    """E2E tests for complete user onboarding flow."""

    @pytest.fixture
    def api_client(self):
        """Create test API client."""
        return Client()

    def test_complete_user_onboarding(self, db, api_client):
        """Test complete onboarding: register, verify, 2FA, login.

        This E2E test verifies the complete user journey:
        1. User registers with email
        2. System sends verification email
        3. User verifies email
        4. System prompts for 2FA setup
        5. User enables 2FA
        6. User logs in with 2FA
        7. User accesses protected resource
        """
        # Step 1: Register
        response = api_client.post('/api/auth/register/', {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
            'first_name': 'John',
            'last_name': 'Doe',
        })
        assert response.status_code == 201

        # Step 2: Verify email
        user = User.objects.get(email='newuser@example.com')
        from apps.core.utils.signed_urls import verify_email_token
        token = user.email_verification_tokens.first().token
        verify_email_token(token)

        # Step 3: Enable 2FA
        response = api_client.post('/api/auth/2fa/setup/', {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
        })
        assert response.status_code == 200
        qr_code = response.json()['qr_code']
        secret = response.json()['secret']

        # Simulate user scanning QR and confirming
        import pyotp
        totp = pyotp.TOTP(secret)
        response = api_client.post('/api/auth/2fa/confirm/', {
            'code': totp.now(),
        })
        assert response.status_code == 200

        # Step 4: Login with 2FA
        response = api_client.post('/api/auth/login/', {
            'email': 'newuser@example.com',
            'password': 'SecurePass123!',
        })
        assert response.status_code == 200
        data = response.json()
        assert 'requires_2fa' in data

        # Provide 2FA code
        totp_code = totp.now()
        response = api_client.post('/api/auth/login/2fa/', {
            'code': totp_code,
        })
        assert response.status_code == 200
        assert 'token' in response.json()
        token = response.json()['token']

        # Step 5: Access protected resource
        response = api_client.get(
            '/api/users/me/',
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert response.status_code == 200
        assert response.json()['email'] == 'newuser@example.com'
```

---

## Best Practices

### 1. Test Real User Journeys

Focus on how real users interact with the system:

```python
# Good - real user flow
def test_user_creates_and_publishes_content(self):
    """Test: user creates page, configures, publishes"""
    pass

# Bad - artificial test
def test_model_creation(self):
    """Test model"""
    pass
```

### 2. Use Multiple Clients

Test interactions between different users:

```python
def test_organisation_member_collaboration(self, db):
    """Test two users collaborating in organisation."""
    admin_client = Client()
    member_client = Client()

    # Admin creates organisation
    # Admin invites member
    # Member joins
    # Both see organisation
```

### 3. Test Error Scenarios

Include negative test cases:

```python
def test_user_cannot_access_other_org(self, db, api_client):
    """Test user cannot access organisations they don't belong to."""
    org1 = Organisation.objects.create(name="Org 1", slug="org-1")
    org2 = Organisation.objects.create(name="Org 2", slug="org-2")

    user = User.objects.create_user(email="user@example.com")
    user.organisations.add(org1)

    # Login
    response = api_client.post('/api/auth/login/', {...})
    token = response.json()['token']

    # Try to access org2 (should fail)
    response = api_client.get(
        f'/api/organisations/{org2.id}/',
        HTTP_AUTHORIZATION=f'Bearer {token}'
    )
    assert response.status_code == 403
```

---

**Last Updated:** 08/01/2026
