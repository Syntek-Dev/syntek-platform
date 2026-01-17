"""Email verification service for handling email confirmation workflow.

This module provides services for email verification including token generation,
validation, and verification completion. Implements secure email verification
flow with expiring tokens.

SECURITY NOTE:
- Tokens are cryptographically secure (64 bytes)
- Tokens are hashed before storage (HMAC-SHA256)
- Tokens expire after 24 hours
- One-time use tokens (invalidated after use) (H12)
- Rate limiting prevents abuse (M2)

Example:
    >>> token = EmailVerificationService.generate_verification_token(user)
    >>> EmailVerificationService.send_verification_email(user)
    >>> verified_user = EmailVerificationService.verify_email(token)
"""

from datetime import timedelta

from django.utils import timezone

from apps.core.models import EmailVerificationToken, User
from apps.core.services.email_service import EmailService
from apps.core.utils.token_hasher import TokenHasher


class EmailVerificationService:
    """Service for email verification operations.

    Handles email verification token generation, sending verification
    emails, and validating verification tokens.

    Security Features:
    - Cryptographically secure tokens
    - Token hashing for storage (C3 pattern)
    - Expiring tokens (24 hours)
    - One-time use tokens (H12)
    - Resend cooldown (5 minutes) (M2)

    Attributes:
        None - All methods are static
    """

    TOKEN_EXPIRY_HOURS = 24
    RESEND_COOLDOWN_MINUTES = 5

    @staticmethod
    def generate_verification_token(user: User) -> str:
        """Generate email verification token for user.

        Creates a new EmailVerificationToken record with a hashed token.
        Returns the plain token for sending via email.

        Args:
            user: User instance to generate token for.

        Returns:
            Plain verification token (not hashed) to send via email.
        """
        # Generate cryptographically secure token
        plain_token = TokenHasher.generate_token()

        # Hash token for storage
        token_hash = TokenHasher.hash_token(plain_token)

        # Calculate expiry time (24 hours)
        expires_at = timezone.now() + timedelta(hours=EmailVerificationService.TOKEN_EXPIRY_HOURS)

        # Create token record
        EmailVerificationToken.objects.create(
            user=user,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        # Return plain token (only returned once)
        return plain_token

    @staticmethod
    def send_verification_email(user: User) -> bool:
        """Send email verification email to user.

        Generates new token and sends verification email via EmailService.

        Args:
            user: User to send verification email to.

        Returns:
            True if email sent successfully, False otherwise.
        """
        # Generate new token
        plain_token = EmailVerificationService.generate_verification_token(user)

        # Send email via EmailService
        return EmailService.send_verification_email(user, plain_token)

    @staticmethod
    def verify_email(token: str) -> User | None:
        """Verify email using verification token.

        Validates token, checks expiry, checks single-use, and marks email as verified.

        Args:
            token: Plain verification token (from email link).

        Returns:
            User instance if verification successful, None otherwise.
        """
        # Hash the token to find in database
        token_hash = TokenHasher.hash_token(token)

        try:
            # Find token record with hash
            token_record = EmailVerificationToken.objects.select_related("user").get(
                token_hash=token_hash
            )

            # Check if token is valid (not expired, not used)
            if not token_record.is_valid():
                return None

            # Get user
            user = token_record.user

            # Mark email as verified
            user.email_verified = True
            user.save(update_fields=["email_verified"])

            # Mark token as used (H12)
            token_record.mark_used()

            return user

        except EmailVerificationToken.DoesNotExist:
            return None

    @staticmethod
    def resend_verification_email(user: User) -> str:
        """Resend verification email to user.

        Generates new token and sends new verification email.
        Should enforce cooldown at the API/mutation layer (M2).

        Args:
            user: User to resend verification email to.

        Returns:
            Plain token that was generated.

        Raises:
            ValueError: If email is already verified.
        """
        if user.email_verified:
            raise ValueError("Email is already verified")

        # Generate new token
        plain_token = EmailVerificationService.generate_verification_token(user)

        # Send email
        EmailService.send_verification_email(user, plain_token)

        return plain_token

    @staticmethod
    def check_resend_cooldown(user: User) -> bool:
        """Check if user is within resend cooldown period (M2).

        Args:
            user: User to check cooldown for.

        Returns:
            True if within cooldown (resend not allowed), False if cooldown expired.
        """
        # Get most recent token for user
        latest_token = (
            EmailVerificationToken.objects.filter(user=user).order_by("-created_at").first()
        )

        if not latest_token:
            return False  # No previous token, allow send

        # Check if created within cooldown period
        cooldown_threshold = timezone.now() - timedelta(
            minutes=EmailVerificationService.RESEND_COOLDOWN_MINUTES
        )

        return latest_token.created_at > cooldown_threshold

    @staticmethod
    def cleanup_expired_tokens() -> int:
        """Remove expired email verification tokens (maintenance task).

        Returns:
            Number of expired tokens removed.
        """
        now = timezone.now()
        expired_tokens = EmailVerificationToken.objects.filter(expires_at__lt=now)
        count = expired_tokens.count()
        expired_tokens.delete()
        return count
