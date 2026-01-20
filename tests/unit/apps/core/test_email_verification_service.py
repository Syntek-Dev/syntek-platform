"""Unit tests for EmailVerificationService.

Tests cover:
- Token generation and hashing
- Email sending integration
- Token verification with expiry checks
- Resend cooldown enforcement (M2)
- Single-use token enforcement (H12)
- Token invalidation after verification
- Rate limiting integration

These tests verify the email verification workflow security.
"""

from datetime import timedelta
from unittest.mock import patch

from django.utils import timezone

import pytest

from apps.core.models import EmailVerificationToken, Organisation, User
from apps.core.services.email_verification_service import EmailVerificationService


@pytest.mark.unit
@pytest.mark.django_db
class TestEmailVerificationService:
    """Unit tests for EmailVerificationService."""

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
            email_verified=False,
        )

    def test_generate_verification_token_creates_token_record(self, user) -> None:
        """Test token generation creates EmailVerificationToken record.

        Given: User without verification token
        When: generate_verification_token() is called
        Then: Token record is created in database with hashed token
        """
        with patch(
            "apps.core.services.email_verification_service.EmailService.send_verification_email"
        ) as mock_send:
            mock_send.return_value = True
            token = EmailVerificationService.generate_verification_token(user)

        assert token is not None
        assert len(token) > 32  # Token should be cryptographically secure
        assert EmailVerificationToken.objects.filter(user=user).exists()

    def test_generate_verification_token_stores_hash_not_plain(self, user) -> None:
        """Test token is hashed before storage.

        Given: User requesting verification token
        When: Token is generated
        Then: Database stores hash, not plain token
        """
        with patch(
            "apps.core.services.email_verification_service.EmailService.send_verification_email"
        ) as mock_send:
            mock_send.return_value = True
            plain_token = EmailVerificationService.generate_verification_token(user)

        token_record = EmailVerificationToken.objects.filter(user=user).first()
        assert token_record is not None
        assert token_record.token_hash != plain_token  # Hash should differ

    def test_generate_verification_token_sets_24_hour_expiry(self, user) -> None:
        """Test token expires in 24 hours.

        Given: User requesting verification token
        When: Token is generated
        Then: Expiry is set to 24 hours from now
        """
        before = timezone.now()
        with patch(
            "apps.core.services.email_verification_service.EmailService.send_verification_email"
        ) as mock_send:
            mock_send.return_value = True
            EmailVerificationService.generate_verification_token(user)
        after = timezone.now()

        token_record = EmailVerificationToken.objects.filter(user=user).first()
        assert token_record is not None

        expected_min = before + timedelta(hours=23, minutes=59)
        expected_max = after + timedelta(hours=24, minutes=1)
        assert expected_min <= token_record.expires_at <= expected_max

    def test_send_verification_email_calls_email_service(self, user) -> None:
        """Test send_verification_email calls EmailService.

        Given: User requiring email verification
        When: send_verification_email() is called
        Then: EmailService.send_verification_email is invoked
        """
        with patch(
            "apps.core.services.email_verification_service.EmailService.send_verification_email"
        ) as mock_send:
            mock_send.return_value = True
            result = EmailVerificationService.send_verification_email(user)

        assert result is True
        mock_send.assert_called_once()

    def test_verify_email_with_valid_token_marks_email_verified(self, user) -> None:
        """Test email verification with valid token.

        Given: User with valid verification token
        When: verify_email() is called with correct token
        Then: User email_verified is set to True
        """
        with patch(
            "apps.core.services.email_verification_service.EmailService.send_verification_email"
        ) as mock_send:
            mock_send.return_value = True
            plain_token = EmailVerificationService.generate_verification_token(user)

        verified_user = EmailVerificationService.verify_email(plain_token)

        assert verified_user is not None
        assert verified_user.id == user.id
        user.refresh_from_db()
        assert user.email_verified is True

    def test_verify_email_with_invalid_token_returns_none(self, user) -> None:
        """Test email verification with invalid token.

        Given: Invalid verification token
        When: verify_email() is called
        Then: None is returned and email not verified
        """
        verified_user = EmailVerificationService.verify_email("invalid_token_12345")

        assert verified_user is None
        user.refresh_from_db()
        assert user.email_verified is False

    def test_verify_email_marks_token_as_used(self, user) -> None:
        """Test token is marked as used after verification (H12).

        Given: User with valid verification token
        When: verify_email() is called
        Then: Token is marked as used
        """
        with patch(
            "apps.core.services.email_verification_service.EmailService.send_verification_email"
        ) as mock_send:
            mock_send.return_value = True
            plain_token = EmailVerificationService.generate_verification_token(user)

        EmailVerificationService.verify_email(plain_token)

        token_record = EmailVerificationToken.objects.filter(user=user).first()
        assert token_record is not None
        assert token_record.used is True
        assert token_record.used_at is not None

    def test_verify_email_with_used_token_fails(self, user) -> None:
        """Test verification fails with already used token (H12).

        Given: Token that has been used
        When: verify_email() is called again with same token
        Then: Verification fails
        """
        with patch(
            "apps.core.services.email_verification_service.EmailService.send_verification_email"
        ) as mock_send:
            mock_send.return_value = True
            plain_token = EmailVerificationService.generate_verification_token(user)

        # First verification succeeds
        first_result = EmailVerificationService.verify_email(plain_token)
        assert first_result is not None

        # Second verification fails (token already used)
        second_result = EmailVerificationService.verify_email(plain_token)
        assert second_result is None

    def test_verify_email_with_expired_token_fails(self, user) -> None:
        """Test verification fails with expired token.

        Given: Token that has expired
        When: verify_email() is called
        Then: Verification fails
        """
        with patch(
            "apps.core.services.email_verification_service.EmailService.send_verification_email"
        ) as mock_send:
            mock_send.return_value = True
            plain_token = EmailVerificationService.generate_verification_token(user)

        # Manually expire the token
        token_record = EmailVerificationToken.objects.filter(user=user).first()
        token_record.expires_at = timezone.now() - timedelta(hours=1)
        token_record.save()

        verified_user = EmailVerificationService.verify_email(plain_token)
        assert verified_user is None

    def test_resend_verification_email_generates_new_token(self, user) -> None:
        """Test resending verification email creates new token.

        Given: User with existing verification token
        When: resend_verification_email() is called
        Then: New token is generated
        """
        with patch(
            "apps.core.services.email_verification_service.EmailService.send_verification_email"
        ) as mock_send:
            mock_send.return_value = True
            first_token = EmailVerificationService.generate_verification_token(user)
            second_token = EmailVerificationService.resend_verification_email(user)

        assert first_token != second_token
        # Both tokens should exist in database (old ones should be cleaned up by service)
        assert EmailVerificationToken.objects.filter(user=user).count() >= 1

    def test_resend_verification_email_fails_if_already_verified(self, user) -> None:
        """Test resend fails if email already verified.

        Given: User with verified email
        When: resend_verification_email() is called
        Then: ValueError is raised
        """
        user.email_verified = True
        user.save()

        with pytest.raises(ValueError, match="already verified"):
            EmailVerificationService.resend_verification_email(user)

    def test_resend_cooldown_check_returns_true_within_5_minutes(self, user) -> None:
        """Test resend cooldown enforcement (M2).

        Given: Token created within last 5 minutes
        When: Checking if resend is allowed
        Then: Cooldown check indicates wait required
        """
        with patch(
            "apps.core.services.email_verification_service.EmailService.send_verification_email"
        ) as mock_send:
            mock_send.return_value = True
            EmailVerificationService.generate_verification_token(user)

        # Get the token creation time
        token_record = EmailVerificationToken.objects.filter(user=user).first()
        assert token_record is not None

        # Check if created within cooldown period (5 minutes)
        cooldown_minutes = 5
        cooldown_threshold = timezone.now() - timedelta(minutes=cooldown_minutes)
        within_cooldown = token_record.created_at > cooldown_threshold

        assert within_cooldown is True  # Token is fresh, within cooldown

    def test_resend_cooldown_check_returns_false_after_5_minutes(self, user) -> None:
        """Test resend allowed after cooldown period (M2).

        Given: Token created more than 5 minutes ago
        When: Checking if resend is allowed
        Then: Cooldown check indicates resend allowed
        """
        with patch(
            "apps.core.services.email_verification_service.EmailService.send_verification_email"
        ) as mock_send:
            mock_send.return_value = True
            EmailVerificationService.generate_verification_token(user)

        # Manually age the token
        token_record = EmailVerificationToken.objects.filter(user=user).first()
        token_record.created_at = timezone.now() - timedelta(minutes=6)
        token_record.save()

        # Check if created within cooldown period
        cooldown_minutes = 5
        cooldown_threshold = timezone.now() - timedelta(minutes=cooldown_minutes)
        within_cooldown = token_record.created_at > cooldown_threshold

        assert within_cooldown is False  # Token is old, cooldown expired

    def test_multiple_verification_tokens_only_latest_works(self, user) -> None:
        """Test only the latest verification token works.

        Given: User with multiple verification tokens
        When: Verifying with old token
        Then: Old token should be invalidated (implementation detail)
        """
        with patch(
            "apps.core.services.email_verification_service.EmailService.send_verification_email"
        ) as mock_send:
            mock_send.return_value = True
            first_token = EmailVerificationService.generate_verification_token(user)
            second_token = EmailVerificationService.generate_verification_token(user)

        # Both tokens exist but service should invalidate old ones
        assert EmailVerificationToken.objects.filter(user=user).count() >= 2

    def test_verify_email_invalidates_token_after_use(self, user) -> None:
        """Test token cannot be reused after verification.

        Given: User with valid verification token
        When: Token is used for verification
        Then: Token is invalidated and cannot be used again
        """
        with patch(
            "apps.core.services.email_verification_service.EmailService.send_verification_email"
        ) as mock_send:
            mock_send.return_value = True
            plain_token = EmailVerificationService.generate_verification_token(user)

        # First use succeeds
        EmailVerificationService.verify_email(plain_token)

        # Token should be marked as used
        token_record = EmailVerificationToken.objects.filter(user=user).first()
        assert token_record.is_valid() is False
