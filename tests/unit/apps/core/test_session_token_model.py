"""Unit tests for SessionToken model.

Tests cover:
- SessionToken creation with valid data
- Extends BaseToken (inherits is_expired, is_valid methods)
- User foreign key
- Token hash and refresh token hash fields
- IP address encryption (BinaryField)
- User agent storage
- Token family for replay detection (H9)
- is_refresh_token_used flag (H9)
- Device fingerprint field (H8)
- last_activity_at tracking (M8)
- Indexes for efficient querying
- Cascade deletion with User

These tests are in the RED phase of TDD - they WILL FAIL against the
barebones model skeleton until the model is fully implemented.
"""

import uuid
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

import pytest

from apps.core.models import Organisation, SessionToken, User


@pytest.mark.unit
@pytest.mark.django_db
class TestSessionTokenModel:
    """Unit tests for SessionToken model."""

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

    def test_session_token_creation_with_valid_data(self, user) -> None:
        """Test session token is created successfully with valid data.

        Given: Valid session token data
        When: SessionToken.objects.create() is called
        Then: SessionToken is created with correct attributes
        """
        expires_at = timezone.now() + timedelta(hours=24)
        token_family = uuid.uuid4()
        encrypted_ip = b"\x00\x01\x02encrypted_ip"

        token = SessionToken.objects.create(
            user=user,
            token_hash="unique_token_hash_123",
            refresh_token_hash="unique_refresh_hash_456",
            expires_at=expires_at,
            ip_address=encrypted_ip,
            user_agent="Mozilla/5.0 Test Browser",
            token_family=token_family,
            device_fingerprint="fp_abc123",
        )

        assert token.id is not None
        assert token.user == user
        assert token.token_hash == "unique_token_hash_123"
        assert token.refresh_token_hash == "unique_refresh_hash_456"
        assert token.expires_at == expires_at
        assert token.user_agent == "Mozilla/5.0 Test Browser"
        assert token.token_family == token_family
        assert token.device_fingerprint == "fp_abc123"

    def test_session_token_user_required(self, organisation) -> None:
        """Test session token requires a user.

        Given: Session token without user
        When: Token is created
        Then: IntegrityError is raised
        """
        with pytest.raises(IntegrityError):
            SessionToken.objects.create(
                user=None,
                token_hash="hash",
                refresh_token_hash="refresh_hash",
                expires_at=timezone.now() + timedelta(hours=1),
                ip_address=b"encrypted",
            )

    def test_session_token_hash_must_be_unique(self, user) -> None:
        """Test session token_hash must be unique.

        Given: Session token with specific token_hash
        When: Creating another token with same hash
        Then: IntegrityError is raised
        """
        SessionToken.objects.create(
            user=user,
            token_hash="duplicate_hash",
            refresh_token_hash="refresh_1",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
        )

        with pytest.raises(IntegrityError):
            SessionToken.objects.create(
                user=user,
                token_hash="duplicate_hash",
                refresh_token_hash="refresh_2",
                expires_at=timezone.now() + timedelta(hours=1),
                ip_address=b"encrypted",
            )

    def test_session_token_refresh_hash_must_be_unique(self, user) -> None:
        """Test session refresh_token_hash must be unique.

        Given: Session token with specific refresh_token_hash
        When: Creating another token with same refresh hash
        Then: IntegrityError is raised
        """
        SessionToken.objects.create(
            user=user,
            token_hash="token_1",
            refresh_token_hash="duplicate_refresh",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
        )

        with pytest.raises(IntegrityError):
            SessionToken.objects.create(
                user=user,
                token_hash="token_2",
                refresh_token_hash="duplicate_refresh",
                expires_at=timezone.now() + timedelta(hours=1),
                ip_address=b"encrypted",
            )

    def test_session_token_is_expired_when_past_expiry(self, user) -> None:
        """Test is_expired() returns True when expires_at is in the past.

        Given: Token with expires_at in the past
        When: is_expired() is called
        Then: True is returned
        """
        expired_time = timezone.now() - timedelta(hours=1)
        token = SessionToken.objects.create(
            user=user,
            token_hash="expired_token",
            refresh_token_hash="refresh",
            expires_at=expired_time,
            ip_address=b"encrypted",
        )

        assert token.is_expired() is True

    def test_session_token_is_not_expired_when_future_expiry(self, user) -> None:
        """Test is_expired() returns False when expires_at is in the future.

        Given: Token with expires_at in the future
        When: is_expired() is called
        Then: False is returned
        """
        future_time = timezone.now() + timedelta(hours=1)
        token = SessionToken.objects.create(
            user=user,
            token_hash="valid_token",
            refresh_token_hash="refresh",
            expires_at=future_time,
            ip_address=b"encrypted",
        )

        assert token.is_expired() is False

    def test_session_token_is_valid_when_not_expired_and_not_used(self, user) -> None:
        """Test is_valid() returns True when not expired and not used.

        Given: Token that is not expired and not used
        When: is_valid() is called
        Then: True is returned
        """
        future_time = timezone.now() + timedelta(hours=1)
        token = SessionToken.objects.create(
            user=user,
            token_hash="valid_token",
            refresh_token_hash="refresh",
            expires_at=future_time,
            ip_address=b"encrypted",
            used=False,
        )

        assert token.is_valid() is True

    def test_session_token_is_invalid_when_expired(self, user) -> None:
        """Test is_valid() returns False when expired.

        Given: Token that is expired but not used
        When: is_valid() is called
        Then: False is returned
        """
        expired_time = timezone.now() - timedelta(hours=1)
        token = SessionToken.objects.create(
            user=user,
            token_hash="expired_token",
            refresh_token_hash="refresh",
            expires_at=expired_time,
            ip_address=b"encrypted",
            used=False,
        )

        assert token.is_valid() is False

    def test_session_token_is_invalid_when_used(self, user) -> None:
        """Test is_valid() returns False when used.

        Given: Token that is not expired but has been used
        When: is_valid() is called
        Then: False is returned
        """
        future_time = timezone.now() + timedelta(hours=1)
        token = SessionToken.objects.create(
            user=user,
            token_hash="used_token",
            refresh_token_hash="refresh",
            expires_at=future_time,
            ip_address=b"encrypted",
            used=True,
        )

        assert token.is_valid() is False

    def test_session_token_ip_address_stored_as_binary(self, user) -> None:
        """Test session token IP address is stored as encrypted BinaryField.

        Given: Encrypted IP address data
        When: Token is saved
        Then: IP is stored as binary data
        """
        encrypted_ip = b"\x00\x01\x02\x03encrypted_ip_data"
        token = SessionToken.objects.create(
            user=user,
            token_hash="token",
            refresh_token_hash="refresh",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=encrypted_ip,
        )

        token.refresh_from_db()
        assert isinstance(token.ip_address, (bytes, memoryview))

    def test_session_token_user_agent_optional(self, user) -> None:
        """Test session token user_agent field is optional.

        Given: Token without user_agent
        When: Token is created
        Then: Token is created with blank user_agent
        """
        token = SessionToken.objects.create(
            user=user,
            token_hash="token",
            refresh_token_hash="refresh",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
        )

        assert token.user_agent == ""

    def test_session_token_token_family_for_replay_detection(self, user) -> None:
        """Test session token has token_family field for replay detection (H9).

        Given: Token family UUID
        When: Token is created
        Then: Token family is stored correctly
        """
        token_family = uuid.uuid4()
        token = SessionToken.objects.create(
            user=user,
            token_hash="token",
            refresh_token_hash="refresh",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
            token_family=token_family,
        )

        assert token.token_family == token_family
        assert isinstance(token.token_family, uuid.UUID)

    def test_session_token_is_refresh_token_used_defaults_to_false(self, user) -> None:
        """Test is_refresh_token_used defaults to False (H9).

        Given: Token created without specifying is_refresh_token_used
        When: Token is retrieved
        Then: is_refresh_token_used is False
        """
        token = SessionToken.objects.create(
            user=user,
            token_hash="token",
            refresh_token_hash="refresh",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
        )

        assert token.is_refresh_token_used is False

    def test_session_token_is_refresh_token_used_can_be_set(self, user) -> None:
        """Test is_refresh_token_used can be set to True (H9).

        Given: Token with unused refresh token
        When: is_refresh_token_used is set to True
        Then: Flag is updated correctly
        """
        token = SessionToken.objects.create(
            user=user,
            token_hash="token",
            refresh_token_hash="refresh",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
        )

        token.is_refresh_token_used = True
        token.save()

        token.refresh_from_db()
        assert token.is_refresh_token_used is True

    def test_session_token_device_fingerprint_field(self, user) -> None:
        """Test session token has device_fingerprint field (H8).

        Given: Device fingerprint string
        When: Token is created
        Then: Device fingerprint is stored correctly
        """
        token = SessionToken.objects.create(
            user=user,
            token_hash="token",
            refresh_token_hash="refresh",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
            device_fingerprint="fp_browser_hash_abc123",
        )

        assert token.device_fingerprint == "fp_browser_hash_abc123"

    def test_session_token_device_fingerprint_optional(self, user) -> None:
        """Test session token device_fingerprint is optional.

        Given: Token without device_fingerprint
        When: Token is created
        Then: Token is created with blank device_fingerprint
        """
        token = SessionToken.objects.create(
            user=user,
            token_hash="token",
            refresh_token_hash="refresh",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
        )

        assert token.device_fingerprint == ""

    def test_session_token_device_fingerprint_max_length(self, user) -> None:
        """Test session token device_fingerprint has max length of 255.

        Given: Device fingerprint longer than 255 characters
        When: full_clean() is called
        Then: ValidationError is raised
        """
        token = SessionToken(
            user=user,
            token_hash="token",
            refresh_token_hash="refresh",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
            device_fingerprint="A" * 256,
        )

        with pytest.raises(ValidationError) as exc_info:
            token.full_clean()

        assert "device_fingerprint" in exc_info.value.message_dict

    def test_session_token_last_activity_at_auto_updates(self, user) -> None:
        """Test session token last_activity_at is automatically updated (M8).

        Given: Session token exists
        When: Token is modified and saved
        Then: last_activity_at timestamp is updated
        """
        import time

        token = SessionToken.objects.create(
            user=user,
            token_hash="token",
            refresh_token_hash="refresh",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
        )
        original_activity = token.last_activity_at

        time.sleep(0.1)

        token.user_agent = "Updated Browser"
        token.save()

        assert token.last_activity_at > original_activity

    def test_session_token_uses_uuid_primary_key(self, user) -> None:
        """Test session token uses UUID as primary key.

        Given: Session token is created
        When: Token ID is checked
        Then: ID is a UUID instance
        """
        token = SessionToken.objects.create(
            user=user,
            token_hash="token",
            refresh_token_hash="refresh",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
        )

        assert isinstance(token.id, uuid.UUID)

    def test_session_token_created_at_auto_set(self, user) -> None:
        """Test session token created_at is automatically set on creation.

        Given: Session token is created
        When: created_at field is checked
        Then: created_at contains a timestamp close to now
        """
        before = timezone.now()
        token = SessionToken.objects.create(
            user=user,
            token_hash="token",
            refresh_token_hash="refresh",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
        )
        after = timezone.now()

        assert token.created_at is not None
        assert before <= token.created_at <= after

    def test_session_token_used_defaults_to_false(self, user) -> None:
        """Test session token used field defaults to False.

        Given: Token created without specifying used
        When: Token is retrieved
        Then: used is False by default
        """
        token = SessionToken.objects.create(
            user=user,
            token_hash="token",
            refresh_token_hash="refresh",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
        )

        assert token.used is False
        assert token.used_at is None

    def test_session_token_cascade_delete_with_user(self, user) -> None:
        """Test session token is deleted when user is deleted (CASCADE).

        Given: User with session tokens
        When: User is deleted
        Then: All associated tokens are deleted
        """
        token1 = SessionToken.objects.create(
            user=user,
            token_hash="token1",
            refresh_token_hash="refresh1",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
        )
        token2 = SessionToken.objects.create(
            user=user,
            token_hash="token2",
            refresh_token_hash="refresh2",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
        )
        token1_id = token1.id
        token2_id = token2.id

        user.delete()

        assert not SessionToken.objects.filter(id=token1_id).exists()
        assert not SessionToken.objects.filter(id=token2_id).exists()

    def test_session_token_ordering_by_created_at_descending(self, user) -> None:
        """Test session tokens are ordered by created_at descending.

        Given: Multiple session tokens
        When: Tokens are queried
        Then: Results are ordered newest first
        """
        import time

        token1 = SessionToken.objects.create(
            user=user,
            token_hash="token1",
            refresh_token_hash="refresh1",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
        )
        time.sleep(0.1)
        token2 = SessionToken.objects.create(
            user=user,
            token_hash="token2",
            refresh_token_hash="refresh2",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
        )

        tokens = list(SessionToken.objects.all())
        assert tokens[0] == token2
        assert tokens[1] == token1

    def test_session_token_has_user_created_at_index(self) -> None:
        """Test session token has index on (user, -created_at).

        Given: SessionToken model
        When: Model Meta indexes are checked
        Then: Index on user and created_at exists
        """
        index_fields = []
        for index in SessionToken._meta.indexes:
            index_fields.append(index.fields)

        assert ["user", "-created_at"] in index_fields

    def test_session_token_has_token_hash_index(self) -> None:
        """Test session token has index on token_hash.

        Given: SessionToken model
        When: Model Meta indexes are checked
        Then: Index on token_hash exists
        """
        index_fields = []
        for index in SessionToken._meta.indexes:
            index_fields.append(index.fields)

        assert ["token_hash"] in index_fields

    def test_session_token_db_table_name(self) -> None:
        """Test session token uses correct database table name.

        Given: SessionToken model
        When: Model Meta is checked
        Then: db_table is 'session_tokens'
        """
        assert SessionToken._meta.db_table == "session_tokens"

    def test_session_token_str_representation(self, user) -> None:
        """Test session token string representation.

        Given: Session token with user
        When: str(token) is called
        Then: String contains relevant info
        """
        token = SessionToken.objects.create(
            user=user,
            token_hash="token",
            refresh_token_hash="refresh",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
        )

        str_repr = str(token)
        # Should contain user email or "session" or similar meaningful text
        assert "test@example.com" in str_repr or "session" in str_repr.lower()

    def test_session_token_filter_by_user(self, user, organisation) -> None:
        """Test filtering session tokens by user.

        Given: Multiple tokens for different users
        When: Filtering by specific user
        Then: Only tokens for that user are returned
        """
        other_user = User.objects.create(email="other@example.com", organisation=organisation)

        token1 = SessionToken.objects.create(
            user=user,
            token_hash="token1",
            refresh_token_hash="refresh1",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
        )
        token2 = SessionToken.objects.create(
            user=other_user,
            token_hash="token2",
            refresh_token_hash="refresh2",
            expires_at=timezone.now() + timedelta(hours=1),
            ip_address=b"encrypted",
        )

        user_tokens = SessionToken.objects.filter(user=user)
        assert token1 in user_tokens
        assert token2 not in user_tokens
