"""Unit tests for EmailVerificationToken model.

Tests cover:
- EmailVerificationToken creation with valid data
- Extends BaseToken (inherits is_expired, is_valid methods)
- User foreign key
- Token hash storage
- Single-use enforcement (H12)
- Resend cooldown tracking (M2)
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

from apps.core.models import EmailVerificationToken, Organisation, User


@pytest.mark.unit
@pytest.mark.django_db
class TestEmailVerificationTokenModel:
    """Unit tests for EmailVerificationToken model."""

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

    def test_email_verification_token_creation_with_valid_data(self, user) -> None:
        """Test email verification token is created successfully with valid data.

        Given: Valid token data
        When: EmailVerificationToken.objects.create() is called
        Then: Token is created with correct attributes
        """
        expires_at = timezone.now() + timedelta(hours=24)
        token = EmailVerificationToken.objects.create(
            user=user,
            token_hash="hashed_verification_token",
            expires_at=expires_at,
        )

        assert token.id is not None
        assert token.user == user
        assert token.token_hash == "hashed_verification_token"
        assert token.expires_at == expires_at
        assert token.used is False

    def test_email_verification_token_user_required(self) -> None:
        """Test email verification token requires a user.

        Given: Token without user
        When: Token is created
        Then: IntegrityError is raised
        """
        with pytest.raises(IntegrityError):
            EmailVerificationToken.objects.create(
                user=None,
                token_hash="hash",
                expires_at=timezone.now() + timedelta(hours=24),
            )

    def test_email_verification_token_hash_must_be_unique(self, user) -> None:
        """Test email verification token_hash must be unique.

        Given: Token with specific token_hash
        When: Creating another token with same hash
        Then: IntegrityError is raised
        """
        EmailVerificationToken.objects.create(
            user=user,
            token_hash="duplicate_hash",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        with pytest.raises(IntegrityError):
            EmailVerificationToken.objects.create(
                user=user,
                token_hash="duplicate_hash",
                expires_at=timezone.now() + timedelta(hours=24),
            )

    def test_email_verification_token_is_expired_when_past_expiry(self, user) -> None:
        """Test token is_expired() returns True when expires_at is in the past.

        Given: Token with expires_at in the past
        When: is_expired() is called
        Then: True is returned
        """
        expired_time = timezone.now() - timedelta(hours=1)
        token = EmailVerificationToken.objects.create(
            user=user,
            token_hash="expired_token",
            expires_at=expired_time,
        )

        assert token.is_expired() is True

    def test_email_verification_token_is_not_expired_within_validity(self, user) -> None:
        """Test token is_expired() returns False within validity period.

        Given: Token with expires_at in the future
        When: is_expired() is called
        Then: False is returned
        """
        future_time = timezone.now() + timedelta(hours=12)
        token = EmailVerificationToken.objects.create(
            user=user,
            token_hash="valid_token",
            expires_at=future_time,
        )

        assert token.is_expired() is False

    def test_email_verification_token_is_valid_when_not_expired_and_not_used(self, user) -> None:
        """Test is_valid() returns True when not expired and not used.

        Given: Token that is not expired and not used
        When: is_valid() is called
        Then: True is returned
        """
        future_time = timezone.now() + timedelta(hours=12)
        token = EmailVerificationToken.objects.create(
            user=user,
            token_hash="valid_token",
            expires_at=future_time,
            used=False,
        )

        assert token.is_valid() is True

    def test_email_verification_token_is_invalid_when_used(self, user) -> None:
        """Test is_valid() returns False when token has been used (H12).

        Given: Token that has been used
        When: is_valid() is called
        Then: False is returned
        """
        future_time = timezone.now() + timedelta(hours=12)
        token = EmailVerificationToken.objects.create(
            user=user,
            token_hash="used_token",
            expires_at=future_time,
            used=True,
        )

        assert token.is_valid() is False

    def test_email_verification_token_used_defaults_to_false(self, user) -> None:
        """Test token used field defaults to False.

        Given: Token created without specifying used
        When: Token is retrieved
        Then: used is False by default
        """
        token = EmailVerificationToken.objects.create(
            user=user,
            token_hash="token",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        assert token.used is False
        assert token.used_at is None

    def test_email_verification_token_used_at_set_when_used(self, user) -> None:
        """Test used_at is set when token is marked as used.

        Given: Unused token
        When: Token is marked as used
        Then: used_at timestamp is set
        """
        token = EmailVerificationToken.objects.create(
            user=user,
            token_hash="token",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        before = timezone.now()
        token.used = True
        token.used_at = timezone.now()
        token.save()
        after = timezone.now()

        assert token.used is True
        assert token.used_at is not None
        assert before <= token.used_at <= after

    def test_email_verification_token_uses_uuid_primary_key(self, user) -> None:
        """Test email verification token uses UUID as primary key.

        Given: Token is created
        When: Token ID is checked
        Then: ID is a UUID instance
        """
        token = EmailVerificationToken.objects.create(
            user=user,
            token_hash="token",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        assert isinstance(token.id, uuid.UUID)

    def test_email_verification_token_created_at_auto_set(self, user) -> None:
        """Test token created_at is automatically set on creation.

        Given: Token is created
        When: created_at field is checked
        Then: created_at contains a timestamp close to now
        """
        before = timezone.now()
        token = EmailVerificationToken.objects.create(
            user=user,
            token_hash="token",
            expires_at=timezone.now() + timedelta(hours=24),
        )
        after = timezone.now()

        assert token.created_at is not None
        assert before <= token.created_at <= after

    def test_email_verification_token_cascade_delete_with_user(self, user) -> None:
        """Test email verification token is deleted when user is deleted.

        Given: User with email verification tokens
        When: User is deleted
        Then: All associated tokens are deleted
        """
        token = EmailVerificationToken.objects.create(
            user=user,
            token_hash="token",
            expires_at=timezone.now() + timedelta(hours=24),
        )
        token_id = token.id

        user.delete()

        assert not EmailVerificationToken.objects.filter(id=token_id).exists()

    def test_email_verification_token_db_table_name(self) -> None:
        """Test email verification token uses correct database table name.

        Given: EmailVerificationToken model
        When: Model Meta is checked
        Then: db_table is 'email_verification_tokens'
        """
        assert EmailVerificationToken._meta.db_table == "email_verification_tokens"

    def test_email_verification_token_str_representation(self, user) -> None:
        """Test email verification token string representation.

        Given: Email verification token
        When: str(token) is called
        Then: String contains relevant info
        """
        token = EmailVerificationToken.objects.create(
            user=user,
            token_hash="token",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        str_repr = str(token)
        # Should contain user email or "verification" or similar text
        assert (
            "test@example.com" in str_repr
            or "verification" in str_repr.lower()
            or "email" in str_repr.lower()
        )

    def test_email_verification_token_filter_by_user(self, user, organisation) -> None:
        """Test filtering email verification tokens by user.

        Given: Multiple tokens for different users
        When: Filtering by specific user
        Then: Only tokens for that user are returned
        """
        other_user = User.objects.create(email="other@example.com", organisation=organisation)

        token1 = EmailVerificationToken.objects.create(
            user=user,
            token_hash="token1",
            expires_at=timezone.now() + timedelta(hours=24),
        )
        token2 = EmailVerificationToken.objects.create(
            user=other_user,
            token_hash="token2",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        user_tokens = EmailVerificationToken.objects.filter(user=user)
        assert token1 in user_tokens
        assert token2 not in user_tokens

    def test_email_verification_token_resend_cooldown_check(self, user) -> None:
        """Test ability to check token creation time for resend cooldown (M2).

        Given: Token created within the last 5 minutes
        When: Checking if resend is allowed
        Then: created_at can be used to enforce cooldown
        """
        token = EmailVerificationToken.objects.create(
            user=user,
            token_hash="token",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        # Verify created_at can be used for cooldown calculation
        cooldown_minutes = 5
        cooldown_threshold = timezone.now() - timedelta(minutes=cooldown_minutes)

        # Token was just created, so it should be within cooldown
        assert token.created_at > cooldown_threshold

    def test_email_verification_token_multiple_tokens_same_user(self, user) -> None:
        """Test user can have multiple verification tokens (for resend).

        Given: User with existing verification token
        When: Creating another token (with different hash)
        Then: Both tokens exist (old should be invalidated by service)
        """
        token1 = EmailVerificationToken.objects.create(
            user=user,
            token_hash="token1",
            expires_at=timezone.now() + timedelta(hours=24),
        )
        token2 = EmailVerificationToken.objects.create(
            user=user,
            token_hash="token2",
            expires_at=timezone.now() + timedelta(hours=24),
        )

        assert EmailVerificationToken.objects.filter(user=user).count() == 2
        assert token1.id != token2.id
