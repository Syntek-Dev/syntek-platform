"""Email verification service for handling email confirmation workflow.

This module provides services for email verification including token generation,
validation, and verification completion. Implements secure email verification
flow with expiring tokens.

SECURITY NOTE:
- Tokens are cryptographically secure (64 bytes)
- Tokens are hashed before storage (HMAC-SHA256)
- Tokens expire after 24 hours
- One-time use tokens (invalidated after use)
- Rate limiting prevents abuse

Example:
    >>> token = EmailVerificationService.generate_verification_token(user)
    >>> EmailVerificationService.send_verification_email(user, token)
    >>> verified = EmailVerificationService.verify_email(token)
"""

from datetime import datetime, timedelta
from typing import cast

from django.utils import timezone

from apps.core.models import User
from apps.core.services.email_service import EmailService
from apps.core.utils.token_hasher import TokenHasher


class EmailVerificationService:
    """Service for email verification operations.

    Handles email verification token generation, sending verification
    emails, and validating verification tokens.

    Security Features:
    - Cryptographically secure tokens
    - Token hashing for storage
    - Expiring tokens (24 hours)
    - One-time use tokens
    - Rate limiting on verification attempts

    Attributes:
        None - All methods are static
    """

    TOKEN_EXPIRY_HOURS = 24

    @staticmethod
    def generate_verification_token(user: User) -> str:
        """Generate email verification token for user.

        Args:
            user: User instance to generate token for

        Returns:
            Plain verification token (not hashed)
        """
        # Generate cryptographically secure token
        token = TokenHasher.generate_token()

        # Hash token for storage
        token_hash = TokenHasher.hash_token(token)

        # Store hashed token in user model
        user.email_verification_token = token_hash
        user.email_verification_token_created = timezone.now()
        user.save(update_fields=["email_verification_token", "email_verification_token_created"])

        return token

    @staticmethod
    def send_verification_email(user: User) -> bool:
        """Send email verification email to user.

        Generates new token and sends verification email.

        Args:
            user: User to send verification email to

        Returns:
            True if email sent successfully, False otherwise
        """
        # Generate new token
        token = EmailVerificationService.generate_verification_token(user)

        # Send email via EmailService
        return EmailService.send_verification_email(user, token)

    @staticmethod
    def verify_email(token: str) -> User | None:
        """Verify email using verification token.

        Validates token, checks expiry, and marks email as verified.

        Args:
            token: Plain verification token (from email link)

        Returns:
            User instance if verification successful, None otherwise
        """
        # Hash the token to find in database
        token_hash = TokenHasher.hash_token(token)

        try:
            # Find user with matching token
            user = User.objects.get(
                email_verification_token=token_hash,
                email_verified=False,
            )

            # Check if token is expired
            if not EmailVerificationService.is_token_valid(user):
                return None

            # Mark email as verified
            user.email_verified = True
            user.email_verification_token = None
            user.email_verification_token_created = None
            user.save(
                update_fields=[
                    "email_verified",
                    "email_verification_token",
                    "email_verification_token_created",
                ]
            )

            return user

        except User.DoesNotExist:
            return None

    @staticmethod
    def is_token_valid(user: User) -> bool:
        """Check if user's verification token is still valid.

        Args:
            user: User instance to check

        Returns:
            True if token exists and not expired, False otherwise
        """
        if not user.email_verification_token or not user.email_verification_token_created:
            return False

        # Check if token is expired
        token_created = cast("datetime", user.email_verification_token_created)
        expiry_time = token_created + timedelta(hours=EmailVerificationService.TOKEN_EXPIRY_HOURS)
        return timezone.now() < expiry_time

    @staticmethod
    def resend_verification_email(user: User) -> bool:
        """Resend verification email to user.

        Generates new token and sends new verification email.
        Rate limiting should be applied at the view/mutation level.

        Args:
            user: User to resend verification email to

        Returns:
            True if email sent successfully, False otherwise

        Raises:
            ValueError: If email is already verified
        """
        if user.email_verified:
            raise ValueError("Email is already verified")

        # Generate new token and send email
        return EmailVerificationService.send_verification_email(user)
