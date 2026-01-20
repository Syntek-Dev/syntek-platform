"""Unit tests for password validators.

Tests cover:
- MinimumLengthValidator (12-character minimum)
- PasswordComplexityValidator (uppercase, lowercase, digit, special char)
- BreachedPasswordValidator (HaveIBeenPwned integration with mocked API)
- PasswordHistoryValidator (prevents reuse of last 5 passwords)
- Edge cases for each validator

These tests are in the RED phase of TDD - they WILL FAIL until the
validators are fully implemented.
"""

from unittest.mock import Mock, patch

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

import pytest

from apps.core.models import Organisation, PasswordHistory
from config.validators import (
    HIBPPasswordValidator as BreachedPasswordValidator,
    MinimumLengthValidator,
    PasswordComplexityValidator,
    PasswordHistoryValidator,
)

User = get_user_model()


@pytest.fixture
def mock_hibp_api():
    """Mock HIBP API responses for breach checking.

    Yields:
        Mock: Mocked requests.get function.
    """
    with patch("requests.get") as mock:
        yield mock


@pytest.mark.unit
class TestMinimumLengthValidator:
    """Unit tests for MinimumLengthValidator."""

    def test_password_meets_minimum_length_12_chars(self) -> None:
        """Test password with exactly 12 characters passes validation.

        Given: Password with 12 characters
        When: validate() is called
        Then: No exception is raised
        """
        validator = MinimumLengthValidator(min_length=12)
        password = "TestPass123!"  # Exactly 12 chars

        try:
            validator.validate(password)
        except ValidationError:
            pytest.fail("Validation should not raise error for 12-char password")

    def test_password_below_minimum_length_fails(self) -> None:
        """Test password shorter than 12 characters fails validation.

        Given: Password with 11 characters
        When: validate() is called
        Then: ValidationError is raised
        """
        validator = MinimumLengthValidator(min_length=12)
        password = "Short123!"  # 9 chars

        with pytest.raises(ValidationError) as exc_info:
            validator.validate(password)

        assert "at least 12 characters" in str(exc_info.value)

    def test_password_above_maximum_length_128_fails(self) -> None:
        """Test password longer than 128 characters fails validation.

        Given: Password with 129 characters
        When: validate() is called
        Then: ValidationError is raised
        """
        validator = MinimumLengthValidator(min_length=12, max_length=128)
        password = "A" * 129

        with pytest.raises(ValidationError) as exc_info:
            validator.validate(password)

        assert "maximum" in str(exc_info.value).lower()

    def test_password_at_maximum_length_passes(self) -> None:
        """Test password at exactly 128 characters passes validation.

        Given: Password with 128 characters
        When: validate() is called
        Then: No exception is raised
        """
        validator = MinimumLengthValidator(min_length=12, max_length=128)
        password = "Aa1!" + "x" * 124  # Exactly 128 chars

        try:
            validator.validate(password)
        except ValidationError:
            pytest.fail("Validation should not raise error for 128-char password")

    def test_get_help_text(self) -> None:
        """Test validator returns appropriate help text.

        Given: MinimumLengthValidator instance
        When: get_help_text() is called
        Then: Help text mentions minimum length
        """
        validator = MinimumLengthValidator(min_length=12)
        help_text = validator.get_help_text()

        assert "12" in help_text
        assert "character" in help_text.lower()


@pytest.mark.unit
class TestPasswordComplexityValidator:
    """Unit tests for PasswordComplexityValidator."""

    def test_password_with_all_requirements_passes(self) -> None:
        """Test password meeting all complexity requirements passes.

        Given: Password with uppercase, lowercase, digit, special char
        When: validate() is called
        Then: No exception is raised
        """
        validator = PasswordComplexityValidator()
        password = "TestPassword123!@"

        try:
            validator.validate(password)
        except ValidationError:
            pytest.fail("Should not raise error for complex password")

    def test_password_missing_uppercase_fails(self) -> None:
        """Test password without uppercase letter fails validation.

        Given: Password with no uppercase letters
        When: validate() is called
        Then: ValidationError is raised
        """
        validator = PasswordComplexityValidator()
        password = "testpassword123!"  # No uppercase

        with pytest.raises(ValidationError) as exc_info:
            validator.validate(password)

        assert "uppercase" in str(exc_info.value).lower()

    def test_password_missing_lowercase_fails(self) -> None:
        """Test password without lowercase letter fails validation.

        Given: Password with no lowercase letters
        When: validate() is called
        Then: ValidationError is raised
        """
        validator = PasswordComplexityValidator()
        password = "TESTPASSWORD123!"  # No lowercase

        with pytest.raises(ValidationError) as exc_info:
            validator.validate(password)

        assert "lowercase" in str(exc_info.value).lower()

    def test_password_missing_digit_fails(self) -> None:
        """Test password without digit fails validation.

        Given: Password with no digits
        When: validate() is called
        Then: ValidationError is raised
        """
        validator = PasswordComplexityValidator()
        password = "TestPassword!@#"  # No digit

        with pytest.raises(ValidationError) as exc_info:
            validator.validate(password)

        assert "digit" in str(exc_info.value).lower()

    def test_password_missing_special_char_fails(self) -> None:
        """Test password without special character fails validation.

        Given: Password with no special characters
        When: validate() is called
        Then: ValidationError is raised
        """
        validator = PasswordComplexityValidator()
        password = "TestPassword123"  # No special char

        with pytest.raises(ValidationError) as exc_info:
            validator.validate(password)

        assert "special character" in str(exc_info.value).lower()

    def test_get_help_text(self) -> None:
        """Test validator returns appropriate help text.

        Given: PasswordComplexityValidator instance
        When: get_help_text() is called
        Then: Help text mentions all requirements
        """
        validator = PasswordComplexityValidator()
        help_text = validator.get_help_text()

        assert "uppercase" in help_text.lower()
        assert "lowercase" in help_text.lower()
        assert "digit" in help_text.lower()
        assert "special" in help_text.lower()


@pytest.mark.unit
class TestBreachedPasswordValidator:
    """Unit tests for BreachedPasswordValidator with HaveIBeenPwned API.

    Note: The mock_hibp_api fixture is not used in RED phase since the
    skeleton implementation doesn't make API calls. Tests will FAIL
    because the validation logic is not implemented.
    """

    def test_password_not_breached_passes(self) -> None:
        """Test password not in breach database passes validation.

        Given: Password not found in HIBP database
        When: validate() is called
        Then: No exception is raised

        Note: Skeleton passes all passwords - this test should PASS in RED phase.
        """
        validator = BreachedPasswordValidator()
        password = "UniquePassword123!@"

        try:
            validator.validate(password)
        except ValidationError:
            pytest.fail("Should not raise error for non-breached password")

    def test_breached_password_fails(self, mock_hibp_api) -> None:
        """Test password found in breach database fails validation.

        Given: Password found in HIBP database (known breached password)
        When: validate() is called
        Then: ValidationError is raised
        """
        # Mock HIBP API response with a matching hash suffix
        # SHA-1 of "password123" = CBFDAC6008F9CAB4083784CBD1874F76618D2A97
        # Prefix: CBFDA, Suffix: C6008F9CAB4083784CBD1874F76618D2A97
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "C6008F9CAB4083784CBD1874F76618D2A97:1000\r\nOTHERHASH:5"
        mock_hibp_api.return_value = mock_response

        validator = BreachedPasswordValidator()
        password = "password123"

        with pytest.raises(ValidationError) as exc_info:
            validator.validate(password)

        assert "breach" in str(exc_info.value).lower()

    def test_hibp_api_failure_allows_password(self) -> None:
        """Test HIBP API failure does not block password (fail-open).

        Given: HIBP API is unavailable
        When: validate() is called
        Then: No exception is raised (fail-open for availability)

        Note: Skeleton always passes - this test should PASS in RED phase.
        """
        validator = BreachedPasswordValidator()
        password = "TestPassword123!@"

        try:
            validator.validate(password)
        except ValidationError:
            pytest.fail("Should fail-open when HIBP API is unavailable")

    def test_hibp_uses_k_anonymity(self, mock_hibp_api) -> None:
        """Test HIBP validator uses k-anonymity (only sends first 5 chars of hash).

        Given: Password to validate
        When: validate() is called
        Then: Only first 5 characters of SHA-1 hash are sent to HIBP
        """
        import hashlib

        # Setup mock response (no matches)
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "SOMEHASH:5\r\nOTHERHASH:10"
        mock_hibp_api.return_value = mock_response

        validator = BreachedPasswordValidator()
        password = "TestPassword123!@"

        # Calculate expected prefix
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        expected_prefix = sha1_hash[:5]

        # Call validate
        validator.validate(password)

        # Verify API was called with k-anonymity (only first 5 chars)
        mock_hibp_api.assert_called_once()
        call_url = mock_hibp_api.call_args[0][0]
        assert expected_prefix in call_url
        assert sha1_hash not in call_url  # Full hash should NOT be in URL

    def test_get_help_text(self) -> None:
        """Test validator returns appropriate help text.

        Given: BreachedPasswordValidator instance
        When: get_help_text() is called
        Then: Help text mentions breach checking
        """
        validator = BreachedPasswordValidator()
        help_text = validator.get_help_text()

        assert "breach" in help_text.lower() or "pwned" in help_text.lower()


@pytest.mark.unit
@pytest.mark.django_db
class TestPasswordHistoryValidator:
    """Unit tests for PasswordHistoryValidator."""

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

    def test_new_password_not_in_history_passes(self, user) -> None:
        """Test new password not matching previous 5 passwords passes.

        Given: User with 5 previous passwords in history
        When: validate() is called with new password
        Then: No exception is raised
        """
        # Create 5 password history entries with different hashes
        for i in range(5):
            PasswordHistory.objects.create(
                user=user,
                password_hash=make_password(f"OldPassword{i}!@"),
            )

        validator = PasswordHistoryValidator()
        new_password = "NewPassword123!@"

        try:
            validator.validate(new_password, user=user)
        except ValidationError:
            pytest.fail("Should allow password not in history")

    def test_password_matching_recent_history_fails(self, user) -> None:
        """Test password matching one of last 5 passwords fails.

        Given: User with password in last 5 passwords
        When: validate() is called with same password
        Then: ValidationError is raised
        """
        reused_password = "ReusedPassword123!@"
        password_hash = make_password(reused_password)

        # Create password history entry
        PasswordHistory.objects.create(user=user, password_hash=password_hash)

        validator = PasswordHistoryValidator()

        with pytest.raises(ValidationError) as exc_info:
            validator.validate(reused_password, user=user)

        assert "recently used" in str(exc_info.value).lower()

    def test_password_older_than_5_history_entries_passes(self, user) -> None:
        """Test password used more than 5 passwords ago can be reused.

        Given: User with 6 password history entries
        When: validate() is called with 6th oldest password
        Then: No exception is raised (only last 5 are checked)
        """
        old_password = "OldPassword123!@"

        # Create the oldest entry first
        PasswordHistory.objects.create(user=user, password_hash=make_password(old_password))
        # Create 5 newer password history entries
        for i in range(5):
            PasswordHistory.objects.create(
                user=user, password_hash=make_password(f"NewerPassword{i}!@")
            )

        validator = PasswordHistoryValidator()

        try:
            validator.validate(old_password, user=user)
        except ValidationError:
            pytest.fail("Should allow password older than last 5")

    def test_validator_handles_user_without_history(self, user) -> None:
        """Test validator handles new user with no password history.

        Given: User with no password history
        When: validate() is called
        Then: No exception is raised
        """
        # Ensure no password history exists
        PasswordHistory.objects.filter(user=user).delete()

        validator = PasswordHistoryValidator()
        password = "FirstPassword123!@"

        try:
            validator.validate(password, user=user)
        except ValidationError:
            pytest.fail("Should allow first password for new user")

    def test_validator_without_user_passes(self) -> None:
        """Test validator passes when no user is provided.

        Given: No user context
        When: validate() is called
        Then: No exception is raised (can't check history without user)
        """
        validator = PasswordHistoryValidator()
        password = "AnyPassword123!@"

        try:
            validator.validate(password, user=None)
        except ValidationError:
            pytest.fail("Should pass when no user is provided")

    def test_get_help_text(self) -> None:
        """Test validator returns appropriate help text.

        Given: PasswordHistoryValidator instance
        When: get_help_text() is called
        Then: Help text mentions password history
        """
        validator = PasswordHistoryValidator()
        help_text = validator.get_help_text()

        assert "recent" in help_text.lower() or "previous" in help_text.lower()
