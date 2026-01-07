"""Unit tests for PasswordHistory model.

Tests cover:
- PasswordHistory creation with valid data
- User foreign key
- Password hash storage (Argon2 hashed)
- Timestamps (created_at)
- UUID primary key
- Ordering by created_at descending
- Cascade deletion with User
- Querying for password history check (H11)

These tests are in the RED phase of TDD - they WILL FAIL against the
barebones model skeleton until the model is fully implemented.
"""

import uuid
import pytest
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

from apps.core.models import PasswordHistory, User, Organisation


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordHistoryModel:
    """Unit tests for PasswordHistory model."""

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

    def test_password_history_creation_with_valid_data(self, user) -> None:
        """Test password history is created successfully with valid data.

        Given: Valid password history data
        When: PasswordHistory.objects.create() is called
        Then: Password history entry is created with correct attributes
        """
        password_hash = make_password("TestPassword123!@")
        history = PasswordHistory.objects.create(
            user=user,
            password_hash=password_hash,
        )

        assert history.id is not None
        assert history.user == user
        assert history.password_hash == password_hash
        assert history.created_at is not None

    def test_password_history_user_required(self) -> None:
        """Test password history requires a user.

        Given: Password history without user
        When: Entry is created
        Then: IntegrityError is raised
        """
        with pytest.raises(IntegrityError):
            PasswordHistory.objects.create(
                user=None,
                password_hash="hash",
            )

    def test_password_history_stores_hashed_password(self, user) -> None:
        """Test password history stores hashed passwords.

        Given: Plain text password
        When: Hash is created and stored
        Then: Hash is stored (not plain text) and can verify password
        """
        password = "TestPassword123!@"
        password_hash = make_password(password)
        history = PasswordHistory.objects.create(
            user=user,
            password_hash=password_hash,
        )

        # Verify hash is stored and can verify the password
        assert history.password_hash != password
        assert check_password(password, history.password_hash)

    def test_password_history_can_verify_password(self, user) -> None:
        """Test stored password hash can verify passwords.

        Given: Password history entry with hashed password
        When: check_password is called with correct password
        Then: True is returned
        """
        password = "TestPassword123!@"
        password_hash = make_password(password)
        history = PasswordHistory.objects.create(
            user=user,
            password_hash=password_hash,
        )

        assert check_password(password, history.password_hash) is True
        assert check_password("WrongPassword", history.password_hash) is False

    def test_password_history_uses_uuid_primary_key(self, user) -> None:
        """Test password history uses UUID as primary key.

        Given: Password history is created
        When: History ID is checked
        Then: ID is a UUID instance
        """
        history = PasswordHistory.objects.create(
            user=user,
            password_hash=make_password("TestPassword123!@"),
        )

        assert isinstance(history.id, uuid.UUID)

    def test_password_history_created_at_auto_set(self, user) -> None:
        """Test password history created_at is automatically set on creation.

        Given: Password history is created
        When: created_at field is checked
        Then: created_at contains a timestamp close to now
        """
        before = timezone.now()
        history = PasswordHistory.objects.create(
            user=user,
            password_hash=make_password("TestPassword123!@"),
        )
        after = timezone.now()

        assert history.created_at is not None
        assert before <= history.created_at <= after

    def test_password_history_ordering_by_created_at_descending(self, user) -> None:
        """Test password history is ordered by created_at descending.

        Given: Multiple password history entries
        When: Entries are queried
        Then: Results are ordered newest first
        """
        import time

        history1 = PasswordHistory.objects.create(
            user=user,
            password_hash=make_password("Password1!@#"),
        )
        time.sleep(0.1)
        history2 = PasswordHistory.objects.create(
            user=user,
            password_hash=make_password("Password2!@#"),
        )
        time.sleep(0.1)
        history3 = PasswordHistory.objects.create(
            user=user,
            password_hash=make_password("Password3!@#"),
        )

        histories = list(PasswordHistory.objects.filter(user=user))
        assert histories[0] == history3
        assert histories[1] == history2
        assert histories[2] == history1

    def test_password_history_cascade_delete_with_user(self, user) -> None:
        """Test password history is deleted when user is deleted (CASCADE).

        Given: User with password history entries
        When: User is deleted
        Then: All associated history entries are deleted
        """
        history1 = PasswordHistory.objects.create(
            user=user,
            password_hash=make_password("Password1!@#"),
        )
        history2 = PasswordHistory.objects.create(
            user=user,
            password_hash=make_password("Password2!@#"),
        )
        history1_id = history1.id
        history2_id = history2.id

        user.delete()

        assert not PasswordHistory.objects.filter(id=history1_id).exists()
        assert not PasswordHistory.objects.filter(id=history2_id).exists()

    def test_password_history_db_table_name(self) -> None:
        """Test password history uses correct database table name.

        Given: PasswordHistory model
        When: Model Meta is checked
        Then: db_table is 'password_history'
        """
        assert PasswordHistory._meta.db_table == "password_history"

    def test_password_history_str_representation(self, user) -> None:
        """Test password history string representation.

        Given: Password history entry
        When: str(history) is called
        Then: String contains relevant info
        """
        history = PasswordHistory.objects.create(
            user=user,
            password_hash=make_password("TestPassword123!@"),
        )

        str_repr = str(history)
        # Should contain user email or "password" or "history"
        assert (
            "test@example.com" in str_repr
            or "password" in str_repr.lower()
            or "history" in str_repr.lower()
        )

    def test_password_history_filter_by_user(self, user, organisation) -> None:
        """Test filtering password history by user.

        Given: Multiple history entries for different users
        When: Filtering by specific user
        Then: Only entries for that user are returned
        """
        other_user = User.objects.create(
            email="other@example.com", organisation=organisation
        )

        history1 = PasswordHistory.objects.create(
            user=user,
            password_hash=make_password("Password1!@#"),
        )
        history2 = PasswordHistory.objects.create(
            user=other_user,
            password_hash=make_password("Password2!@#"),
        )

        user_history = PasswordHistory.objects.filter(user=user)
        assert history1 in user_history
        assert history2 not in user_history

    def test_password_history_query_last_five_passwords(self, user) -> None:
        """Test querying for last 5 passwords (H11 requirement).

        Given: User with 6 password history entries
        When: Querying for last 5
        Then: Only 5 most recent entries are returned
        """
        import time

        # Create 6 password history entries
        for i in range(6):
            PasswordHistory.objects.create(
                user=user,
                password_hash=make_password(f"Password{i}!@#"),
            )
            time.sleep(0.05)

        last_five = PasswordHistory.objects.filter(user=user)[:5]
        assert last_five.count() == 5

    def test_password_history_check_password_reuse(self, user) -> None:
        """Test checking if password was recently used (H11 requirement).

        Given: User with password history
        When: Checking if a password matches any in history
        Then: Match is found if password was used
        """
        password = "ReusedPassword123!@"
        password_hash = make_password(password)

        PasswordHistory.objects.create(
            user=user,
            password_hash=password_hash,
        )

        # Check if password is in history
        history_entries = PasswordHistory.objects.filter(user=user)
        password_was_used = any(
            check_password(password, entry.password_hash)
            for entry in history_entries
        )

        assert password_was_used is True

    def test_password_history_new_password_not_in_history(self, user) -> None:
        """Test new password is not found in history.

        Given: User with password history
        When: Checking if new password matches any in history
        Then: No match is found
        """
        # Add some passwords to history
        for i in range(3):
            PasswordHistory.objects.create(
                user=user,
                password_hash=make_password(f"OldPassword{i}!@#"),
            )

        # Check if new password is in history
        new_password = "CompletelyNewPassword123!@"
        history_entries = PasswordHistory.objects.filter(user=user)
        password_was_used = any(
            check_password(new_password, entry.password_hash)
            for entry in history_entries
        )

        assert password_was_used is False

    def test_password_history_max_length_255(self, user) -> None:
        """Test password_hash field has max length of 255 characters.

        Given: PasswordHistory model
        When: password_hash field max_length is checked
        Then: max_length is 255
        """
        password_hash_field = PasswordHistory._meta.get_field("password_hash")
        assert password_hash_field.max_length == 255
