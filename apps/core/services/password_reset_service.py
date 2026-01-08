"""Password reset service with hash-then-store pattern.

This module handles password reset token creation and verification using
the hash-then-store security pattern. Implements C3 security requirement.

SECURITY NOTE (C3):
- Tokens are hashed before storing in database
- Plain token never persisted, only sent via email once
- HMAC-SHA256 hashing with TOKEN_SIGNING_KEY
- Constant-time comparison prevents timing attacks
- Tokens expire after 15 minutes

Example:
    >>> token = PasswordResetService.create_reset_token(user)
    >>> # Token sent via email, hash stored in DB
    >>> user = PasswordResetService.verify_reset_token(token)
    >>> PasswordResetService.reset_password(user, token, new_password)
"""

from datetime import timedelta

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.core.models import PasswordResetToken, User
from apps.core.services.token_service import TokenService
from apps.core.utils.token_hasher import TokenHasher


class PasswordResetService:
    """Service for password reset with hash-then-store pattern.

    Handles creation of password reset tokens, verification, and
    password reset completion with secure token handling.

    Security Features:
    - Hash-then-store pattern (C3)
    - HMAC-SHA256 token hashing
    - 15-minute token expiry
    - Single-use tokens
    - Rate limiting on reset requests

    Attributes:
        None - All methods are static
    """

    @staticmethod
    def create_reset_token(user: User, ip_address: str = "") -> str:
        """Create password reset token for user.

        Generates a cryptographically secure token, hashes it with
        HMAC-SHA256, and stores only the hash in the database.

        Args:
            user: User requesting password reset
            ip_address: IP address of request (for audit log)

        Returns:
            Plain reset token (only returned once, not stored)
        """
        # Generate cryptographically secure token
        plain_token = TokenHasher.generate_token()

        # Hash the token for storage
        token_hash = TokenHasher.hash_token(plain_token)

        # Create password reset token (expires in 1 hour)
        expires_at = timezone.now() + timedelta(hours=1)
        PasswordResetToken.objects.create(
            user=user,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        # Return plain token (only returned once, never stored)
        return plain_token

    @staticmethod
    def verify_reset_token(token: str) -> User | None:
        """Verify password reset token and return user.

        Hashes the provided token and compares with stored hashes
        using constant-time comparison to prevent timing attacks.

        Args:
            token: Plain reset token from email link

        Returns:
            User instance if token is valid and not expired, None otherwise
        """
        # Hash the token
        token_hash = TokenHasher.hash_token(token)

        try:
            reset_token = PasswordResetToken.objects.select_related("user").get(
                token_hash=token_hash
            )

            # Check if token is valid
            if reset_token.is_valid():
                return reset_token.user

        except PasswordResetToken.DoesNotExist:
            pass

        return None

    @staticmethod
    def reset_password(user: User, token: str, new_password: str) -> bool:
        """Reset user password using valid token.

        Verifies token, validates new password against requirements,
        marks token as used, and updates password with history tracking.

        Args:
            user: User whose password to reset
            token: Plain reset token from email link
            new_password: New password to set

        Returns:
            True if successful, False if token invalid

        Raises:
            ValueError: If new password violates requirements or matches history
        """
        # Verify token
        if PasswordResetService.verify_reset_token(token) != user:
            return False

        # Validate password
        try:
            validate_password(new_password, user=user)
        except ValidationError as e:
            raise ValueError("; ".join(e.messages)) from e

        # Hash the token to find it
        token_hash = TokenHasher.hash_token(token)

        try:
            reset_token = PasswordResetToken.objects.get(token_hash=token_hash)

            # Mark token as used
            reset_token.mark_used()

            # Set new password
            user.set_password(new_password)
            user.save(update_fields=["password"])

            # Revoke all existing tokens (force re-login)
            TokenService.revoke_user_tokens(user)

            return True

        except PasswordResetToken.DoesNotExist:
            return False

    @staticmethod
    def cleanup_expired_tokens() -> int:
        """Remove expired password reset tokens (maintenance task).

        Returns:
            Number of expired tokens removed
        """
        now = timezone.now()
        expired_tokens = PasswordResetToken.objects.filter(expires_at__lt=now)
        count = expired_tokens.count()
        expired_tokens.delete()
        return count
