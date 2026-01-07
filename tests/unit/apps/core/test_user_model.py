"""Unit tests for User model.

Tests cover:
- User creation with valid data
- Email field validation and uniqueness
- Password hashing and validation
- Organisation relationship (nullable for superusers)
- Email verification fields
- Two-factor authentication fields
- IP address encryption
- has_email_account and has_vault_access flags
- password_changed_at tracking
- User model methods (get_full_name, check_password, etc.)
- Timestamps

These tests are in the RED phase of TDD - they WILL FAIL against the
barebones model skeleton until the model is fully implemented.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
import time

from django.contrib.auth import get_user_model
from apps.core.models import Organisation

User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class TestUserModel:
    """Unit tests for User model."""

    @pytest.fixture
    def organisation(self, db) -> Organisation:
        """Create a test organisation.

        Returns:
            Organisation instance for testing.
        """
        return Organisation.objects.create(name="Test Org", slug="test-org")

    def test_user_creation_with_valid_data(self, organisation) -> None:
        """Test user is created successfully with valid data.

        Given: Valid user data (email, first_name, last_name)
        When: User.objects.create() is called
        Then: User is created with correct attributes
        """
        user = User.objects.create(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            organisation=organisation,
        )

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.first_name == "John"
        assert user.last_name == "Doe"
        assert user.organisation == organisation
        assert user.is_active is True
        assert user.is_staff is False
        assert user.is_superuser is False
        assert user.email_verified is False
        assert user.two_factor_enabled is False

    def test_user_email_must_be_unique(self, organisation) -> None:
        """Test user email must be unique.

        Given: A user with email "test@example.com" exists
        When: Creating another user with the same email
        Then: IntegrityError is raised
        """
        User.objects.create(
            email="test@example.com", first_name="First", organisation=organisation
        )

        with pytest.raises(IntegrityError):
            User.objects.create(
                email="test@example.com", first_name="Second", organisation=organisation
            )

    def test_user_email_validation_format(self, organisation) -> None:
        """Test user email must be a valid email address.

        Given: User with invalid email format
        When: full_clean() is called
        Then: ValidationError is raised
        """
        user = User(email="invalid-email", first_name="John", organisation=organisation)

        with pytest.raises(ValidationError) as exc_info:
            user.full_clean()

        assert "email" in exc_info.value.message_dict

    def test_user_email_required(self, organisation) -> None:
        """Test user email is required.

        Given: User data without email
        When: full_clean() is called
        Then: ValidationError is raised
        """
        user = User(first_name="John", organisation=organisation)

        with pytest.raises(ValidationError) as exc_info:
            user.full_clean()

        assert "email" in exc_info.value.message_dict

    def test_user_email_max_length(self, organisation) -> None:
        """Test user email has max length of 255 characters.

        Given: User with email longer than 255 characters
        When: full_clean() is called
        Then: ValidationError is raised
        """
        very_long_email = "a" * 250 + "@example.com"  # 263 chars
        user = User(email=very_long_email, first_name="John", organisation=organisation)

        with pytest.raises(ValidationError) as exc_info:
            user.full_clean()

        assert "email" in exc_info.value.message_dict

    def test_user_password_is_hashed(self, organisation) -> None:
        """Test user password is hashed on save.

        Given: A plain text password
        When: User is created with set_password()
        Then: Password is stored as a hash, not plain text
        """
        user = User.objects.create(email="test@example.com", organisation=organisation)
        user.set_password("TestPassword123!@")
        user.save()

        assert user.password != "TestPassword123!@"
        assert user.check_password("TestPassword123!@")

    def test_user_check_password_correct(self, organisation) -> None:
        """Test user check_password returns True for correct password.

        Given: User with password set
        When: check_password() is called with correct password
        Then: True is returned
        """
        user = User.objects.create(email="test@example.com", organisation=organisation)
        user.set_password("TestPassword123!@")
        user.save()

        assert user.check_password("TestPassword123!@") is True

    def test_user_check_password_incorrect(self, organisation) -> None:
        """Test user check_password returns False for incorrect password.

        Given: User with password set
        When: check_password() is called with incorrect password
        Then: False is returned
        """
        user = User.objects.create(email="test@example.com", organisation=organisation)
        user.set_password("TestPassword123!@")
        user.save()

        assert user.check_password("WrongPassword") is False

    def test_user_organisation_can_be_null_for_superuser(self, db) -> None:
        """Test user organisation can be null for platform superusers.

        Given: User created without organisation
        When: is_superuser is True
        Then: User is created successfully without organisation
        """
        user = User.objects.create(
            email="admin@example.com",
            first_name="Super",
            last_name="Admin",
            is_superuser=True,
            organisation=None,
        )

        assert user.organisation is None
        assert user.is_superuser is True

    def test_user_email_verified_defaults_to_false(self, organisation) -> None:
        """Test user email_verified defaults to False.

        Given: User created without specifying email_verified
        When: User is retrieved
        Then: email_verified is False by default
        """
        user = User.objects.create(email="test@example.com", organisation=organisation)

        assert user.email_verified is False
        assert user.email_verified_at is None

    def test_user_email_verified_at_set_on_verification(self, organisation) -> None:
        """Test user email_verified_at is set when email is verified.

        Given: User with unverified email
        When: email_verified is set to True
        Then: email_verified_at contains timestamp
        """
        user = User.objects.create(email="test@example.com", organisation=organisation)

        before = timezone.now()
        user.email_verified = True
        user.email_verified_at = timezone.now()
        user.save()
        after = timezone.now()

        assert user.email_verified is True
        assert user.email_verified_at is not None
        assert before <= user.email_verified_at <= after

    def test_user_two_factor_enabled_defaults_to_false(self, organisation) -> None:
        """Test user two_factor_enabled defaults to False.

        Given: User created without specifying two_factor_enabled
        When: User is retrieved
        Then: two_factor_enabled is False by default
        """
        user = User.objects.create(email="test@example.com", organisation=organisation)

        assert user.two_factor_enabled is False

    def test_user_two_factor_can_be_enabled(self, organisation) -> None:
        """Test user two-factor authentication can be enabled.

        Given: User with 2FA disabled
        When: two_factor_enabled is set to True
        Then: User has 2FA enabled
        """
        user = User.objects.create(email="test@example.com", organisation=organisation)
        user.two_factor_enabled = True
        user.save()

        user.refresh_from_db()
        assert user.two_factor_enabled is True

    def test_user_last_login_ip_is_encrypted(self, organisation) -> None:
        """Test user last_login_ip is stored as encrypted binary data.

        Given: User with last login IP set
        When: IP address is stored
        Then: IP is stored as encrypted BinaryField
        """
        user = User.objects.create(email="test@example.com", organisation=organisation)
        encrypted_ip = b"\x00\x01\x02\x03"  # Encrypted IP placeholder
        user.last_login_ip = encrypted_ip
        user.save()

        user.refresh_from_db()
        assert isinstance(user.last_login_ip, bytes)
        assert user.last_login_ip == encrypted_ip

    def test_user_has_email_account_defaults_to_false(self, organisation) -> None:
        """Test user has_email_account defaults to False.

        Given: User created without specifying has_email_account
        When: User is retrieved
        Then: has_email_account is False by default
        """
        user = User.objects.create(email="test@example.com", organisation=organisation)

        assert user.has_email_account is False

    def test_user_has_vault_access_defaults_to_false(self, organisation) -> None:
        """Test user has_vault_access defaults to False.

        Given: User created without specifying has_vault_access
        When: User is retrieved
        Then: has_vault_access is False by default
        """
        user = User.objects.create(email="test@example.com", organisation=organisation)

        assert user.has_vault_access is False

    def test_user_password_changed_at_tracking(self, organisation) -> None:
        """Test user password_changed_at is updated when password changes.

        Given: User with password set
        When: Password is changed
        Then: password_changed_at is updated to current timestamp
        """
        user = User.objects.create(email="test@example.com", organisation=organisation)
        user.set_password("OldPassword123!@")
        user.password_changed_at = timezone.now()
        user.save()

        original_changed_at = user.password_changed_at

        # Change password
        time.sleep(0.1)
        user.set_password("NewPassword456!@")
        user.password_changed_at = timezone.now()
        user.save()

        assert user.password_changed_at > original_changed_at

    def test_user_get_full_name_method(self, organisation) -> None:
        """Test user get_full_name() method returns first + last name.

        Given: User with first_name and last_name
        When: get_full_name() is called
        Then: Full name string is returned
        """
        user = User.objects.create(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            organisation=organisation,
        )

        assert user.get_full_name() == "John Doe"

    def test_user_get_short_name_method(self, organisation) -> None:
        """Test user get_short_name() method returns first name.

        Given: User with first_name
        When: get_short_name() is called
        Then: First name is returned
        """
        user = User.objects.create(
            email="test@example.com", first_name="John", organisation=organisation
        )

        assert user.get_short_name() == "John"

    def test_user_str_representation(self, organisation) -> None:
        """Test user string representation returns email.

        Given: User with email
        When: str(user) is called
        Then: Email address is returned
        """
        user = User.objects.create(email="test@example.com", organisation=organisation)

        assert str(user) == "test@example.com"

    def test_user_is_active_defaults_to_true(self, organisation) -> None:
        """Test user is_active defaults to True.

        Given: User created without specifying is_active
        When: User is retrieved
        Then: is_active is True by default
        """
        user = User.objects.create(email="test@example.com", organisation=organisation)

        assert user.is_active is True

    def test_user_can_be_deactivated(self, organisation) -> None:
        """Test user account can be deactivated.

        Given: Active user
        When: is_active is set to False
        Then: User account is deactivated
        """
        user = User.objects.create(email="test@example.com", organisation=organisation)
        user.is_active = False
        user.save()

        user.refresh_from_db()
        assert user.is_active is False

    def test_user_email_case_insensitive(self, organisation) -> None:
        """Test user email is case-insensitive for uniqueness.

        Given: User with email "test@example.com"
        When: Creating user with email "TEST@EXAMPLE.COM"
        Then: IntegrityError is raised (case-insensitive uniqueness)
        """
        User.objects.create(email="test@example.com", organisation=organisation)

        with pytest.raises(IntegrityError):
            User.objects.create(email="TEST@EXAMPLE.COM", organisation=organisation)

    def test_user_created_at_auto_set(self, organisation) -> None:
        """Test user created_at is automatically set on creation.

        Given: User is created
        When: created_at field is checked
        Then: created_at contains a timestamp close to now
        """
        before = timezone.now()
        user = User.objects.create(email="test@example.com", organisation=organisation)
        after = timezone.now()

        assert user.created_at is not None
        assert before <= user.created_at <= after

    def test_user_updated_at_auto_updates(self, organisation) -> None:
        """Test user updated_at is automatically updated on save.

        Given: User exists
        When: User is modified and saved
        Then: updated_at timestamp is updated
        """
        user = User.objects.create(email="test@example.com", organisation=organisation)
        original_updated = user.updated_at

        time.sleep(0.1)

        user.first_name = "Updated"
        user.save()

        assert user.updated_at > original_updated

    def test_user_uuid_primary_key(self, organisation) -> None:
        """Test user uses UUID as primary key.

        Given: User is created
        When: id field is checked
        Then: id is a valid UUID
        """
        import uuid

        user = User.objects.create(email="test@example.com", organisation=organisation)

        assert user.id is not None
        assert isinstance(user.id, uuid.UUID)

    def test_user_first_name_optional(self, organisation) -> None:
        """Test user first_name is optional.

        Given: User created without first_name
        When: User is saved
        Then: User is created with empty first_name
        """
        user = User.objects.create(
            email="test@example.com",
            organisation=organisation,
        )

        assert user.first_name == ""

    def test_user_last_name_optional(self, organisation) -> None:
        """Test user last_name is optional.

        Given: User created without last_name
        When: User is saved
        Then: User is created with empty last_name
        """
        user = User.objects.create(
            email="test@example.com",
            organisation=organisation,
        )

        assert user.last_name == ""

    def test_user_db_table_name(self, organisation) -> None:
        """Test user model uses correct database table name.

        Given: User model
        When: _meta.db_table is checked
        Then: Table name is core_user
        """
        assert User._meta.db_table == "core_user"

    def test_user_email_index_exists(self, organisation) -> None:
        """Test user email field has a database index.

        Given: User model
        When: _meta.indexes is checked
        Then: email field has an index
        """
        indexes = [idx.fields for idx in User._meta.indexes]
        # Check if email is indexed (either as standalone or in composite)
        has_email_index = any("email" in fields for fields in indexes)
        assert has_email_index or User._meta.get_field("email").db_index

    def test_user_organisation_on_delete_cascade(self, organisation) -> None:
        """Test user organisation FK uses SET_NULL on delete.

        Given: User linked to an organisation
        When: Organisation is deleted
        Then: User's organisation becomes NULL (not deleted)
        """
        user = User.objects.create(
            email="test@example.com",
            organisation=organisation,
        )

        # Delete organisation
        organisation.delete()

        # Refresh user from DB
        user.refresh_from_db()
        assert user.organisation is None
