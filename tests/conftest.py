"""Global pytest configuration and fixtures.

This module contains shared fixtures and configuration for all tests.
It automatically imports all factories and fixtures to make them available
across all test modules.
"""

from typing import Any
from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.utils import timezone

import pytest

# Import all factories to make them available globally
# This allows tests to use factories without explicit imports
from tests.factories import (
    AuditLogFactory,
    EmailVerificationTokenFactory,
    OrganisationFactory,
    PasswordHistoryFactory,
    PasswordResetTokenFactory,
    SessionTokenFactory,
    TOTPDeviceFactory,
    UserFactory,
    UserProfileFactory,
)

# Make factories available via pytest namespace
pytest.OrganisationFactory = OrganisationFactory
pytest.UserFactory = UserFactory
pytest.UserProfileFactory = UserProfileFactory
pytest.AuditLogFactory = AuditLogFactory
pytest.SessionTokenFactory = SessionTokenFactory
pytest.PasswordResetTokenFactory = PasswordResetTokenFactory
pytest.EmailVerificationTokenFactory = EmailVerificationTokenFactory
pytest.TOTPDeviceFactory = TOTPDeviceFactory
pytest.PasswordHistoryFactory = PasswordHistoryFactory


@pytest.fixture
def db_setup(db):
    """Ensure database is set up correctly for tests.

    Args:
        db: pytest-django database fixture

    Returns:
        Database fixture instance
    """
    return db


@pytest.fixture
def clean_db(django_db_setup, django_db_blocker):
    """Clean database before each test.

    Args:
        django_db_setup: pytest-django database setup fixture
        django_db_blocker: pytest-django database blocker fixture
    """
    with django_db_blocker.unblock():
        User = get_user_model()
        User.objects.all().delete()


@pytest.fixture
def mock_fernet():
    """Mock Fernet encryption for TOTP secret testing.

    Returns:
        Mock Fernet instance with encrypt/decrypt methods
    """
    mock_fernet_instance = Mock()
    mock_fernet_instance.encrypt.return_value = b"encrypted_secret_data"
    mock_fernet_instance.decrypt.return_value = b"decrypted_secret_data"

    with patch("cryptography.fernet.Fernet") as mock_fernet_class:
        mock_fernet_class.return_value = mock_fernet_instance
        yield mock_fernet_instance


@pytest.fixture
def mock_hibp_api():
    """Mock HaveIBeenPwned API for password breach testing.

    Returns:
        Mock response from HIBP API
    """
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.text = ""  # Empty means password not breached

    with patch("requests.get") as mock_get:
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def test_password():
    """Provide a valid test password that meets all requirements.

    Returns:
        Valid password string
    """
    return "TestPassword123!@"


@pytest.fixture
def breached_password():
    """Provide a known breached password for testing.

    Returns:
        Breached password string
    """
    return "Password123"  # Common breached password


@pytest.fixture
def weak_passwords():
    """Provide list of passwords that should fail validation.

    Returns:
        List of weak password strings
    """
    return [
        "short",  # Too short
        "nocapitals123!",  # No uppercase
        "NOLOWERCASE123!",  # No lowercase
        "NoNumbers!",  # No digits
        "NoSpecialChar123",  # No special characters
        "a" * 129,  # Too long
    ]


@pytest.fixture
def mock_timezone():
    """Mock Django timezone for consistent test timing.

    Returns:
        Mocked timezone module
    """
    with patch("django.utils.timezone.now") as mock_now:
        fixed_time = timezone.datetime(2026, 1, 7, 12, 0, 0, tzinfo=timezone.get_current_timezone())
        mock_now.return_value = fixed_time
        yield mock_now


@pytest.fixture
def test_context() -> dict[str, Any]:
    """Provide shared test context dictionary.

    Returns:
        Empty context dictionary for storing test state
    """
    return {}
