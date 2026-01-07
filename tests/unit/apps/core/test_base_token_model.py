"""Unit tests for BaseToken abstract model.

Tests cover:
- BaseToken cannot be instantiated directly (abstract model)
- is_expired() method logic
- is_valid() method logic (not expired AND not used)
- Token hash storage and validation
- expires_at field behavior
- used and used_at field tracking
- UUID primary key generation

These tests are in the RED phase of TDD - they WILL FAIL against the
barebones model skeleton until the model is fully implemented.
"""

import pytest
import uuid
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from apps.core.models import BaseToken, SessionToken, Organisation

User = get_user_model()


@pytest.mark.unit
@pytest.mark.django_db
class TestBaseTokenModel:
    """Unit tests for BaseToken abstract model."""

    @pytest.fixture
    def organisation(self, db) -> Organisation:
        """Create a test organisation.

        Returns:
            Organisation instance for testing.
        """
        return Organisation.objects.create(name="Test Org", slug="test-org")

    @pytest.fixture
    def user(self, organisation) -> User:
        """Create a test user.

        Args:
            organisation: Organisation fixture.

        Returns:
            User instance for testing.
        """
        return User.objects.create_user(
            email="test@example.com",
            password="TestPassword123!@",
            organisation=organisation,
        )

    def test_base_token_cannot_be_instantiated(self, db) -> None:
        """Test BaseToken cannot be instantiated directly (abstract model).

        Given: BaseToken is an abstract model
        When: Attempting to create a BaseToken instance
        Then: TypeError or AttributeError is raised
        """
        with pytest.raises((TypeError, AttributeError)):
            BaseToken.objects.create(
                token_hash="test_hash", expires_at=timezone.now()
            )

    def test_token_is_expired_when_expires_at_in_past(self, user) -> None:
        """Test token is_expired() returns True when expires_at is in the past.

        Given: Token with expires_at in the past
        When: is_expired() is called
        Then: True is returned
        """
        expired_time = timezone.now() - timedelta(hours=1)
        token = SessionToken.objects.create(
            user=user,
            token="test_hash_expired",
            expires_at=expired_time,
        )

        assert token.is_expired() is True

    def test_token_is_not_expired_when_expires_at_in_future(self, user) -> None:
        """Test token is_expired() returns False when expires_at is in the future.

        Given: Token with expires_at in the future
        When: is_expired() is called
        Then: False is returned
        """
        future_time = timezone.now() + timedelta(hours=1)
        token = SessionToken.objects.create(
            user=user,
            token="test_hash_future",
            expires_at=future_time,
        )

        assert token.is_expired() is False

    def test_token_is_valid_when_not_expired_and_not_used(self, user) -> None:
        """Test token is_valid() returns True when not expired and not used.

        Given: Token that is not expired and not used
        When: is_valid() is called
        Then: True is returned
        """
        future_time = timezone.now() + timedelta(hours=1)
        token = SessionToken.objects.create(
            user=user,
            token="test_hash_valid",
            expires_at=future_time,
            is_used=False,
        )

        assert token.is_valid() is True

    def test_token_is_not_valid_when_expired(self, user) -> None:
        """Test token is_valid() returns False when expired.

        Given: Token that is expired but not used
        When: is_valid() is called
        Then: False is returned
        """
        expired_time = timezone.now() - timedelta(hours=1)
        token = SessionToken.objects.create(
            user=user,
            token="test_hash_expired_invalid",
            expires_at=expired_time,
            is_used=False,
        )

        assert token.is_valid() is False

    def test_token_is_not_valid_when_used(self, user) -> None:
        """Test token is_valid() returns False when used.

        Given: Token that is not expired but has been used
        When: is_valid() is called
        Then: False is returned
        """
        future_time = timezone.now() + timedelta(hours=1)
        token = SessionToken.objects.create(
            user=user,
            token="test_hash_used",
            expires_at=future_time,
            is_used=True,
        )

        assert token.is_valid() is False

    def test_token_used_at_is_set_when_marked_as_used(self, user) -> None:
        """Test token used_at is set when token is marked as used.

        Given: Unused token
        When: Token is marked as used
        Then: used_at timestamp is set
        """
        future_time = timezone.now() + timedelta(hours=1)
        token = SessionToken.objects.create(
            user=user,
            token="test_hash_mark_used",
            expires_at=future_time,
        )

        assert token.used_at is None

        before = timezone.now()
        token.mark_used()
        after = timezone.now()

        assert token.is_used is True
        assert token.used_at is not None
        assert before <= token.used_at <= after

    def test_token_hash_is_unique(self, user) -> None:
        """Test token must be unique across all tokens.

        Given: Token with specific token value
        When: Creating another token with same value
        Then: IntegrityError is raised
        """
        future_time = timezone.now() + timedelta(hours=1)
        SessionToken.objects.create(
            user=user,
            token="unique_hash_test",
            expires_at=future_time,
        )

        with pytest.raises(IntegrityError):
            SessionToken.objects.create(
                user=user,
                token="unique_hash_test",
                expires_at=future_time,
            )

    def test_token_uses_uuid_primary_key(self, user) -> None:
        """Test token uses UUID as primary key.

        Given: Token is created
        When: Token ID is checked
        Then: ID is a UUID instance
        """
        future_time = timezone.now() + timedelta(hours=1)
        token = SessionToken.objects.create(
            user=user,
            token="test_hash_uuid",
            expires_at=future_time,
        )

        assert isinstance(token.id, uuid.UUID)

    def test_token_created_at_auto_set(self, user) -> None:
        """Test token created_at is automatically set on creation.

        Given: Token is created
        When: created_at field is checked
        Then: created_at contains a timestamp close to now
        """
        before = timezone.now()
        token = SessionToken.objects.create(
            user=user,
            token="test_hash_created_at",
            expires_at=timezone.now() + timedelta(hours=1),
        )
        after = timezone.now()

        assert token.created_at is not None
        assert before <= token.created_at <= after

    def test_token_used_defaults_to_false(self, user) -> None:
        """Test token is_used field defaults to False.

        Given: Token is created without specifying is_used
        When: Token is retrieved
        Then: is_used is False by default
        """
        token = SessionToken.objects.create(
            user=user,
            token="test_hash_used_default",
            expires_at=timezone.now() + timedelta(hours=1),
        )

        assert token.is_used is False
        assert token.used_at is None

    def test_token_user_foreign_key(self, user) -> None:
        """Test token has foreign key to User.

        Given: Token is created with user
        When: Token is retrieved
        Then: Token's user matches the creating user
        """
        token = SessionToken.objects.create(
            user=user,
            token="test_hash_user_fk",
            expires_at=timezone.now() + timedelta(hours=1),
        )

        assert token.user == user
        assert token.user.email == "test@example.com"

    def test_token_user_cascade_delete(self, user) -> None:
        """Test token is deleted when user is deleted (CASCADE).

        Given: Token linked to a user
        When: User is deleted
        Then: Token is also deleted
        """
        token = SessionToken.objects.create(
            user=user,
            token="test_hash_cascade",
            expires_at=timezone.now() + timedelta(hours=1),
        )
        token_id = token.id

        user.delete()

        assert not SessionToken.objects.filter(id=token_id).exists()
