"""Unit tests for UserProfile model.

Tests cover:
- UserProfile creation with valid data
- One-to-one relationship with User
- Field validation (phone, avatar, timezone, language, bio)
- Default values for timezone and language
- Timestamps (created_at, updated_at)
- UUID primary key
- Cascade deletion with User

These tests are in the RED phase of TDD - they WILL FAIL against the
barebones model skeleton until the model is fully implemented.
"""

import uuid
import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from apps.core.models import UserProfile, User, Organisation


@pytest.mark.unit
@pytest.mark.django_db
class TestUserProfileModel:
    """Unit tests for UserProfile model."""

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

    def test_user_profile_creation_with_valid_data(self, user) -> None:
        """Test user profile is created successfully with valid data.

        Given: Valid user profile data (user, phone, timezone, language)
        When: UserProfile.objects.create() is called
        Then: UserProfile is created with correct attributes
        """
        profile = UserProfile.objects.create(
            user=user,
            phone="+44 1234 567890",
            timezone="Europe/London",
            language="en-GB",
            bio="Test biography",
        )

        assert profile.id is not None
        assert profile.user == user
        assert profile.phone == "+44 1234 567890"
        assert profile.timezone == "Europe/London"
        assert profile.language == "en-GB"
        assert profile.bio == "Test biography"

    def test_user_profile_one_to_one_relationship(self, user) -> None:
        """Test user profile has one-to-one relationship with user.

        Given: User with profile
        When: Accessing user.profile
        Then: Associated profile is returned
        """
        profile = UserProfile.objects.create(user=user, phone="+44 123")

        assert user.profile == profile
        assert profile.user == user

    def test_user_can_only_have_one_profile(self, user) -> None:
        """Test user can only have one profile (one-to-one constraint).

        Given: User with existing profile
        When: Creating another profile for same user
        Then: IntegrityError is raised
        """
        UserProfile.objects.create(user=user, phone="+44 123")

        with pytest.raises(IntegrityError):
            UserProfile.objects.create(user=user, phone="+44 456")

    def test_user_profile_phone_field_optional(self, user) -> None:
        """Test user profile phone field is optional.

        Given: User profile without phone
        When: Profile is created
        Then: Profile is created with blank phone
        """
        profile = UserProfile.objects.create(user=user)

        assert profile.phone == ""

    def test_user_profile_phone_max_length(self, user) -> None:
        """Test user profile phone has max length of 20 characters.

        Given: Phone number longer than 20 characters
        When: full_clean() is called
        Then: ValidationError is raised
        """
        profile = UserProfile(user=user, phone="1" * 21)

        with pytest.raises(ValidationError) as exc_info:
            profile.full_clean()

        assert "phone" in exc_info.value.message_dict

    def test_user_profile_avatar_field_optional(self, user) -> None:
        """Test user profile avatar field is optional.

        Given: User profile without avatar URL
        When: Profile is created
        Then: Profile is created with blank avatar
        """
        profile = UserProfile.objects.create(user=user)

        assert profile.avatar == ""

    def test_user_profile_avatar_must_be_valid_url(self, user) -> None:
        """Test user profile avatar must be a valid URL.

        Given: Invalid avatar URL
        When: full_clean() is called
        Then: ValidationError is raised
        """
        profile = UserProfile(user=user, avatar="not-a-valid-url")

        with pytest.raises(ValidationError) as exc_info:
            profile.full_clean()

        assert "avatar" in exc_info.value.message_dict

    def test_user_profile_timezone_defaults_to_utc(self, user) -> None:
        """Test user profile timezone defaults to UTC.

        Given: User profile without timezone specified
        When: Profile is created
        Then: Timezone is 'UTC' by default
        """
        profile = UserProfile.objects.create(user=user)

        assert profile.timezone == "UTC"

    def test_user_profile_timezone_max_length(self, user) -> None:
        """Test user profile timezone has max length of 50 characters.

        Given: Timezone string longer than 50 characters
        When: full_clean() is called
        Then: ValidationError is raised
        """
        profile = UserProfile(user=user, timezone="A" * 51)

        with pytest.raises(ValidationError) as exc_info:
            profile.full_clean()

        assert "timezone" in exc_info.value.message_dict

    def test_user_profile_language_defaults_to_en(self, user) -> None:
        """Test user profile language defaults to 'en'.

        Given: User profile without language specified
        When: Profile is created
        Then: Language is 'en' by default
        """
        profile = UserProfile.objects.create(user=user)

        assert profile.language == "en"

    def test_user_profile_language_max_length(self, user) -> None:
        """Test user profile language has max length of 10 characters.

        Given: Language code longer than 10 characters
        When: full_clean() is called
        Then: ValidationError is raised
        """
        profile = UserProfile(user=user, language="A" * 11)

        with pytest.raises(ValidationError) as exc_info:
            profile.full_clean()

        assert "language" in exc_info.value.message_dict

    def test_user_profile_bio_field_optional(self, user) -> None:
        """Test user profile bio field is optional.

        Given: User profile without bio
        When: Profile is created
        Then: Profile is created with blank bio
        """
        profile = UserProfile.objects.create(user=user)

        assert profile.bio == ""

    def test_user_profile_bio_can_store_long_text(self, user) -> None:
        """Test user profile bio can store long text (TextField).

        Given: Long biography text
        When: Profile is saved
        Then: Full text is stored
        """
        long_bio = "A" * 5000
        profile = UserProfile.objects.create(user=user, bio=long_bio)

        profile.refresh_from_db()
        assert profile.bio == long_bio
        assert len(profile.bio) == 5000

    def test_user_profile_uses_uuid_primary_key(self, user) -> None:
        """Test user profile uses UUID as primary key.

        Given: User profile is created
        When: Profile ID is checked
        Then: ID is a UUID instance
        """
        profile = UserProfile.objects.create(user=user)

        assert isinstance(profile.id, uuid.UUID)

    def test_user_profile_created_at_auto_set(self, user) -> None:
        """Test user profile created_at is automatically set on creation.

        Given: User profile is created
        When: created_at field is checked
        Then: created_at contains a timestamp close to now
        """
        before = timezone.now()
        profile = UserProfile.objects.create(user=user)
        after = timezone.now()

        assert profile.created_at is not None
        assert before <= profile.created_at <= after

    def test_user_profile_updated_at_auto_updates(self, user) -> None:
        """Test user profile updated_at is automatically updated on save.

        Given: User profile exists
        When: Profile is modified and saved
        Then: updated_at timestamp is updated
        """
        import time

        profile = UserProfile.objects.create(user=user)
        original_updated = profile.updated_at

        time.sleep(0.1)

        profile.bio = "Updated bio"
        profile.save()

        assert profile.updated_at > original_updated

    def test_user_profile_cascade_delete_with_user(self, user) -> None:
        """Test user profile is deleted when user is deleted (CASCADE).

        Given: User with profile
        When: User is deleted
        Then: Associated profile is also deleted
        """
        profile = UserProfile.objects.create(user=user)
        profile_id = profile.id

        user.delete()

        assert not UserProfile.objects.filter(id=profile_id).exists()

    def test_user_profile_deletion_does_not_delete_user(self, user) -> None:
        """Test deleting profile does not delete associated user.

        Given: User with profile
        When: Profile is deleted
        Then: User still exists
        """
        profile = UserProfile.objects.create(user=user)
        user_id = user.id

        profile.delete()

        assert User.objects.filter(id=user_id).exists()

    def test_user_profile_str_representation(self, user) -> None:
        """Test user profile string representation.

        Given: User profile with associated user
        When: str(profile) is called
        Then: String contains user email or relevant info
        """
        profile = UserProfile.objects.create(user=user)

        str_repr = str(profile)
        # Should contain user email or "Profile" or similar meaningful text
        assert "test@example.com" in str_repr or "Profile" in str_repr

    def test_user_profile_db_table_name(self) -> None:
        """Test user profile uses correct database table name.

        Given: UserProfile model
        When: Model Meta is checked
        Then: db_table is 'user_profiles'
        """
        assert UserProfile._meta.db_table == "user_profiles"
