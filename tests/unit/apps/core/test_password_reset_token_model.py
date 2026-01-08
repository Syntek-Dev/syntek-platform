"""Unit tests for PasswordResetToken model.

Tests cover:
- PasswordResetToken creation with valid data
- Extends BaseToken (inherits is_expired, is_valid methods)
- User foreign key
- Token hash storage (HMAC-SHA256 hashed, per C3)
- 15-minute expiration (as per security requirements)
- Single-use enforcement (H12)
- Timestamps
- UUID primary key
- Cascade deletion with User

These tests are in the RED phase of TDD - they WILL FAIL against the
barebones model skeleton until the model is fully implemented.
"""

import uuid
from datetime import timedelta

from django.db import IntegrityError
from django.utils import timezone

import pytest

from apps.core.models import Organisation, PasswordResetToken, User


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordResetTokenModel:
    """Unit tests for PasswordResetToken model."""

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
        return User.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            organisation=organisation,
        )

    def test_password_reset_token_creation_with_valid_data(self, user) -> None:
        """Test password reset token is created successfully with valid data.

        Given: Valid token data
        When: PasswordResetToken.objects.create() is called
        Then: Token is created with correct attributes
        """
        expires_at = timezone.now() + timedelta(minutes=15)
        token = PasswordResetToken.objects.create(
            user=user,
            token_hash="hmac_sha256_hashed_token_value",
            expires_at=expires_at,
        )

        assert token.id is not None
        assert token.user == user
        assert token.token_hash == "hmac_sha256_hashed_token_value"
        assert token.expires_at == expires_at
        assert token.used is False

    def test_password_reset_token_user_required(self) -> None:
        """Test password reset token requires a user.

        Given: Token without user
        When: Token is created
        Then: IntegrityError is raised
        """
        with pytest.raises(IntegrityError):
            PasswordResetToken.objects.create(
                user=None,
                token_hash="hash",
                expires_at=timezone.now() + timedelta(minutes=15),
            )

    def test_password_reset_token_hash_must_be_unique(self, user) -> None:
        """Test password reset token_hash must be unique.

        Given: Token with specific token_hash
        When: Creating another token with same hash
        Then: IntegrityError is raised
        """
        PasswordResetToken.objects.create(
            user=user,
            token_hash="duplicate_hash",
            expires_at=timezone.now() + timedelta(minutes=15),
        )

        with pytest.raises(IntegrityError):
            PasswordResetToken.objects.create(
                user=user,
                token_hash="duplicate_hash",
                expires_at=timezone.now() + timedelta(minutes=15),
            )

    def test_password_reset_token_is_expired_after_15_minutes(self, user) -> None:
        """Test token is_expired() returns True after 15 minutes.

        Given: Token created 16 minutes ago with 15-minute expiry
        When: is_expired() is called
        Then: True is returned
        """
        expired_time = timezone.now() - timedelta(minutes=1)
        token = PasswordResetToken.objects.create(
            user=user,
            token_hash="expired_token",
            expires_at=expired_time,
        )

        assert token.is_expired() is True

    def test_password_reset_token_is_not_expired_within_15_minutes(self, user) -> None:
        """Test token is_expired() returns False within 15 minutes.

        Given: Token with expires_at in 10 minutes
        When: is_expired() is called
        Then: False is returned
        """
        future_time = timezone.now() + timedelta(minutes=10)
        token = PasswordResetToken.objects.create(
            user=user,
            token_hash="valid_token",
            expires_at=future_time,
        )

        assert token.is_expired() is False

    def test_password_reset_token_is_valid_when_not_expired_and_not_used(self, user) -> None:
        """Test is_valid() returns True when not expired and not used.

        Given: Token that is not expired and not used
        When: is_valid() is called
        Then: True is returned
        """
        future_time = timezone.now() + timedelta(minutes=10)
        token = PasswordResetToken.objects.create(
            user=user,
            token_hash="valid_token",
            expires_at=future_time,
            used=False,
        )

        assert token.is_valid() is True

    def test_password_reset_token_is_invalid_when_used(self, user) -> None:
        """Test is_valid() returns False when token has been used (H12).

        Given: Token that has been used
        When: is_valid() is called
        Then: False is returned
        """
        future_time = timezone.now() + timedelta(minutes=10)
        token = PasswordResetToken.objects.create(
            user=user,
            token_hash="used_token",
            expires_at=future_time,
            used=True,
        )

        assert token.is_valid() is False

    def test_password_reset_token_used_defaults_to_false(self, user) -> None:
        """Test token used field defaults to False.

        Given: Token created without specifying used
        When: Token is retrieved
        Then: used is False by default
        """
        token = PasswordResetToken.objects.create(
            user=user,
            token_hash="token",
            expires_at=timezone.now() + timedelta(minutes=15),
        )

        assert token.used is False
        assert token.used_at is None

    def test_password_reset_token_used_at_set_when_used(self, user) -> None:
        """Test used_at is set when token is marked as used.

        Given: Unused token
        When: Token is marked as used
        Then: used_at timestamp is set
        """
        token = PasswordResetToken.objects.create(
            user=user,
            token_hash="token",
            expires_at=timezone.now() + timedelta(minutes=15),
        )

        before = timezone.now()
        token.used = True
        token.used_at = timezone.now()
        token.save()
        after = timezone.now()

        assert token.used is True
        assert token.used_at is not None
        assert before <= token.used_at <= after

    def test_password_reset_token_uses_uuid_primary_key(self, user) -> None:
        """Test password reset token uses UUID as primary key.

        Given: Token is created
        When: Token ID is checked
        Then: ID is a UUID instance
        """
        token = PasswordResetToken.objects.create(
            user=user,
            token_hash="token",
            expires_at=timezone.now() + timedelta(minutes=15),
        )

        assert isinstance(token.id, uuid.UUID)

    def test_password_reset_token_created_at_auto_set(self, user) -> None:
        """Test token created_at is automatically set on creation.

        Given: Token is created
        When: created_at field is checked
        Then: created_at contains a timestamp close to now
        """
        before = timezone.now()
        token = PasswordResetToken.objects.create(
            user=user,
            token_hash="token",
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        after = timezone.now()

        assert token.created_at is not None
        assert before <= token.created_at <= after

    def test_password_reset_token_cascade_delete_with_user(self, user) -> None:
        """Test password reset token is deleted when user is deleted (CASCADE).

        Given: User with password reset tokens
        When: User is deleted
        Then: All associated tokens are deleted
        """
        token = PasswordResetToken.objects.create(
            user=user,
            token_hash="token",
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        token_id = token.id

        user.delete()

        assert not PasswordResetToken.objects.filter(id=token_id).exists()

    def test_password_reset_token_db_table_name(self) -> None:
        """Test password reset token uses correct database table name.

        Given: PasswordResetToken model
        When: Model Meta is checked
        Then: db_table is 'password_reset_tokens'
        """
        assert PasswordResetToken._meta.db_table == "password_reset_tokens"

    def test_password_reset_token_str_representation(self, user) -> None:
        """Test password reset token string representation.

        Given: Password reset token
        When: str(token) is called
        Then: String contains relevant info
        """
        token = PasswordResetToken.objects.create(
            user=user,
            token_hash="token",
            expires_at=timezone.now() + timedelta(minutes=15),
        )

        str_repr = str(token)
        # Should contain user email or "reset" or similar meaningful text
        assert (
            "test@example.com" in str_repr
            or "reset" in str_repr.lower()
            or "password" in str_repr.lower()
        )

    def test_password_reset_token_multiple_tokens_per_user(self, user) -> None:
        """Test user can have multiple password reset tokens.

        Given: User with existing reset token
        When: Creating another reset token (with different hash)
        Then: Both tokens exist (old tokens should be invalidated by service layer)
        """
        token1 = PasswordResetToken.objects.create(
            user=user,
            token_hash="token1",
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        token2 = PasswordResetToken.objects.create(
            user=user,
            token_hash="token2",
            expires_at=timezone.now() + timedelta(minutes=15),
        )

        assert PasswordResetToken.objects.filter(user=user).count() == 2
        assert token1.id != token2.id

    def test_password_reset_token_filter_by_user(self, user, organisation) -> None:
        """Test filtering password reset tokens by user.

        Given: Multiple tokens for different users
        When: Filtering by specific user
        Then: Only tokens for that user are returned
        """
        other_user = User.objects.create(email="other@example.com", organisation=organisation)

        token1 = PasswordResetToken.objects.create(
            user=user,
            token_hash="token1",
            expires_at=timezone.now() + timedelta(minutes=15),
        )
        token2 = PasswordResetToken.objects.create(
            user=other_user,
            token_hash="token2",
            expires_at=timezone.now() + timedelta(minutes=15),
        )

        user_tokens = PasswordResetToken.objects.filter(user=user)
        assert token1 in user_tokens
        assert token2 not in user_tokens

    def test_password_reset_token_filter_unused(self, user) -> None:
        """Test filtering for unused password reset tokens.

        Given: Mix of used and unused tokens
        When: Filtering by used=False
        Then: Only unused tokens are returned
        """
        unused_token = PasswordResetToken.objects.create(
            user=user,
            token_hash="unused",
            expires_at=timezone.now() + timedelta(minutes=15),
            used=False,
        )
        used_token = PasswordResetToken.objects.create(
            user=user,
            token_hash="used",
            expires_at=timezone.now() + timedelta(minutes=15),
            used=True,
        )

        unused_tokens = PasswordResetToken.objects.filter(used=False)
        assert unused_token in unused_tokens
        assert used_token not in unused_tokens
