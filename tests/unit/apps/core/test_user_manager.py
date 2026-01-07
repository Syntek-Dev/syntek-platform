"""Unit tests for UserManager.

Tests cover:
- create_user method
- create_superuser method
- Email normalisation
- Password hashing
- Required field validation
- Organisation assignment
- Default field values
- get_by_natural_key method

These tests are in the RED phase of TDD - they WILL FAIL against the
barebones model skeleton until the manager is fully implemented.
"""

import uuid
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.core.models import User, Organisation


@pytest.mark.unit
@pytest.mark.django_db
class TestUserManager:
    """Unit tests for UserManager."""

    @pytest.fixture
    def organisation(self, db) -> Organisation:
        """Create a test organisation.

        Returns:
            Organisation instance for testing.
        """
        return Organisation.objects.create(name="Test Org", slug="test-org")

    def test_create_user_with_valid_data(self, organisation) -> None:
        """Test create_user creates user with valid data.

        Given: Valid user data
        When: User.objects.create_user() is called
        Then: User is created with correct attributes
        """
        user = User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!@",
            first_name="Test",
            last_name="User",
            organisation=organisation,
        )

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.first_name == "Test"
        assert user.last_name == "User"
        assert user.organisation == organisation
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False

    def test_create_user_hashes_password(self, organisation) -> None:
        """Test create_user hashes the password.

        Given: Plain text password
        When: User is created
        Then: Password is hashed (not stored as plain text)
        """
        password = "TestPassword123!@"
        user = User.objects.create_user(
            email="test@example.com",
            password=password,
            organisation=organisation,
        )

        assert user.password != password
        assert user.check_password(password) is True

    def test_create_user_normalises_email(self, organisation) -> None:
        """Test create_user normalises email address.

        Given: Email with uppercase characters
        When: User is created
        Then: Email is lowercased for case-insensitive uniqueness
        """
        user = User.objects.create_user(
            email="Test@EXAMPLE.COM",
            password="TestPassword123!@",
            organisation=organisation,
        )

        # Email should be fully lowercased for case-insensitive uniqueness
        assert user.email == "test@example.com"

    def test_create_user_requires_email(self, organisation) -> None:
        """Test create_user raises error without email.

        Given: No email provided
        When: User.objects.create_user() is called
        Then: ValueError is raised
        """
        with pytest.raises(ValueError) as exc_info:
            User.objects.create_user(
                email=None,
                password="TestPassword123!@",
                organisation=organisation,
            )

        assert "email" in str(exc_info.value).lower()

    def test_create_user_requires_email_not_empty(self, organisation) -> None:
        """Test create_user raises error with empty email.

        Given: Empty string email
        When: User.objects.create_user() is called
        Then: ValueError is raised
        """
        with pytest.raises(ValueError) as exc_info:
            User.objects.create_user(
                email="",
                password="TestPassword123!@",
                organisation=organisation,
            )

        assert "email" in str(exc_info.value).lower()

    def test_create_user_sets_is_active_true_by_default(self, organisation) -> None:
        """Test create_user sets is_active to True by default.

        Given: User created without is_active specified
        When: User is retrieved
        Then: is_active is True
        """
        user = User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!@",
            organisation=organisation,
        )

        assert user.is_active is True

    def test_create_user_sets_is_staff_false_by_default(self, organisation) -> None:
        """Test create_user sets is_staff to False by default.

        Given: User created without is_staff specified
        When: User is retrieved
        Then: is_staff is False
        """
        user = User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!@",
            organisation=organisation,
        )

        assert user.is_staff is False

    def test_create_user_sets_is_superuser_false_by_default(
        self, organisation
    ) -> None:
        """Test create_user sets is_superuser to False by default.

        Given: User created without is_superuser specified
        When: User is retrieved
        Then: is_superuser is False
        """
        user = User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!@",
            organisation=organisation,
        )

        assert user.is_superuser is False

    def test_create_user_sets_email_verified_false_by_default(
        self, organisation
    ) -> None:
        """Test create_user sets email_verified to False by default.

        Given: User created without email_verified specified
        When: User is retrieved
        Then: email_verified is False
        """
        user = User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!@",
            organisation=organisation,
        )

        assert user.email_verified is False

    def test_create_user_allows_no_password(self, organisation) -> None:
        """Test create_user allows creating user without password.

        Given: No password provided
        When: User is created
        Then: User is created with unusable password
        """
        user = User.objects.create_user(
            email="test@example.com",
            password=None,
            organisation=organisation,
        )

        assert user.has_usable_password() is False

    def test_create_superuser_with_valid_data(self) -> None:
        """Test create_superuser creates superuser with valid data.

        Given: Valid superuser data
        When: User.objects.create_superuser() is called
        Then: Superuser is created with correct attributes
        """
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="AdminPassword123!@",
            first_name="Admin",
            last_name="User",
        )

        assert user.id is not None
        assert user.email == "admin@example.com"
        assert user.is_active is True
        assert user.is_staff is True
        assert user.is_superuser is True

    def test_create_superuser_without_organisation(self) -> None:
        """Test create_superuser allows null organisation for platform admins.

        Given: No organisation specified
        When: Superuser is created
        Then: Superuser is created with null organisation
        """
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="AdminPassword123!@",
        )

        assert user.organisation is None
        assert user.is_superuser is True

    def test_create_superuser_forces_is_staff_true(self) -> None:
        """Test create_superuser forces is_staff to True.

        Given: is_staff=False passed
        When: Superuser is created
        Then: is_staff is still True
        """
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                email="admin@example.com",
                password="AdminPassword123!@",
                is_staff=False,
            )

    def test_create_superuser_forces_is_superuser_true(self) -> None:
        """Test create_superuser forces is_superuser to True.

        Given: is_superuser=False passed
        When: Superuser is created
        Then: ValueError is raised
        """
        with pytest.raises(ValueError):
            User.objects.create_superuser(
                email="admin@example.com",
                password="AdminPassword123!@",
                is_superuser=False,
            )

    def test_create_superuser_hashes_password(self) -> None:
        """Test create_superuser hashes the password.

        Given: Plain text password
        When: Superuser is created
        Then: Password is hashed
        """
        password = "AdminPassword123!@"
        user = User.objects.create_superuser(
            email="admin@example.com",
            password=password,
        )

        assert user.password != password
        assert user.check_password(password) is True

    def test_get_by_natural_key(self, organisation) -> None:
        """Test get_by_natural_key retrieves user by email.

        Given: User exists with specific email
        When: get_by_natural_key(email) is called
        Then: User is retrieved
        """
        user = User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!@",
            organisation=organisation,
        )

        retrieved_user = User.objects.get_by_natural_key("test@example.com")
        assert retrieved_user == user

    def test_get_by_natural_key_case_insensitive(self, organisation) -> None:
        """Test get_by_natural_key is case-insensitive for email.

        Given: User exists with lowercase email
        When: get_by_natural_key with uppercase email is called
        Then: User is retrieved
        """
        user = User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!@",
            organisation=organisation,
        )

        retrieved_user = User.objects.get_by_natural_key("TEST@EXAMPLE.COM")
        assert retrieved_user == user

    def test_create_user_with_extra_fields(self, organisation) -> None:
        """Test create_user accepts extra fields.

        Given: Extra fields like first_name, last_name
        When: User is created
        Then: Extra fields are stored
        """
        user = User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!@",
            organisation=organisation,
            first_name="John",
            last_name="Doe",
        )

        assert user.first_name == "John"
        assert user.last_name == "Doe"

    def test_create_user_strips_email_whitespace(self, organisation) -> None:
        """Test create_user strips whitespace from email.

        Given: Email with leading/trailing whitespace
        When: User is created
        Then: Whitespace is stripped
        """
        user = User.objects.create_user(
            email="  test@example.com  ",
            password="TestPassword123!@",
            organisation=organisation,
        )

        assert user.email == "test@example.com"

    def test_create_user_lowercases_email(self, organisation) -> None:
        """Test create_user lowercases entire email.

        Given: Email with mixed case
        When: User is created
        Then: Email is stored in lowercase
        """
        user = User.objects.create_user(
            email="TEST@EXAMPLE.COM",
            password="TestPassword123!@",
            organisation=organisation,
        )

        # Full email should be lowercased for uniqueness
        assert user.email.lower() == "test@example.com"

    def test_user_manager_active_users_queryset(self, organisation) -> None:
        """Test manager can filter active users.

        Given: Mix of active and inactive users
        When: Filtering by is_active
        Then: Only active users are returned
        """
        active_user = User.objects.create_user(
            email="active@example.com",
            password="TestPassword123!@",
            organisation=organisation,
            is_active=True,
        )
        inactive_user = User.objects.create_user(
            email="inactive@example.com",
            password="TestPassword123!@",
            organisation=organisation,
            is_active=False,
        )

        active_users = User.objects.filter(is_active=True)
        assert active_user in active_users
        assert inactive_user not in active_users
