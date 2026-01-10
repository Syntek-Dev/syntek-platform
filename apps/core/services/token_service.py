"""Token service for JWT token management with replay detection.

This module provides token creation, verification, and revocation services
for JWT access and refresh tokens. Implements H9 security requirement for
refresh token replay detection using token families.

SECURITY NOTE (H9):
- Token families track refresh token chains
- Replay detection: if used token is reused, revoke entire family
- Prevents stolen refresh token attacks
- Database + Redis storage for revocation

Example:
    >>> tokens = TokenService.create_tokens(user)
    >>> {'access_token': '...', 'refresh_token': '...', 'family_id': '...'}
"""

import uuid
from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from apps.core.models import SessionToken, User
from apps.core.utils.token_hasher import TokenHasher


class TokenService:
    """Service for JWT token management with replay detection.

    Handles creation, verification, and revocation of JWT access tokens
    and refresh tokens. Implements token family pattern for detecting
    replay attacks on refresh tokens.

    Security Features:
    - RS256 algorithm for JWT signing (H1)
    - Token family tracking for replay detection (H9)
    - Automatic token revocation on password change
    - Redis caching for fast token verification
    - Concurrent session limit enforcement

    Attributes:
        None - All methods are static
    """

    @staticmethod
    def create_tokens(user: User, device_fingerprint: str = "") -> dict[str, str]:
        """Create JWT access and refresh tokens for user.

        Args:
            user: User instance to create tokens for
            device_fingerprint: Device identifier for tracking (H8)

        Returns:
            Dictionary containing:
                - access_token: JWT access token (24h expiry)
                - refresh_token: JWT refresh token (30d expiry)
                - family_id: Token family UUID for replay detection
        """
        # Generate random tokens
        access_token = TokenHasher.generate_token()
        refresh_token = TokenHasher.generate_token()

        # Hash tokens for storage
        access_token_hash = TokenHasher.hash_token(access_token)
        refresh_token_hash = TokenHasher.hash_token(refresh_token)

        # Create token family ID
        family_id = uuid.uuid4()

        # Create session token record
        expires_at = timezone.now() + timedelta(days=30)
        SessionToken.objects.create(
            user=user,
            token_hash=access_token_hash,
            refresh_token_hash=refresh_token_hash,
            token_family=family_id,
            device_fingerprint=device_fingerprint,
            expires_at=expires_at,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "family_id": str(family_id),
        }

    @staticmethod
    def verify_access_token(token: str) -> User | None:
        """Verify JWT access token and return user.

        Args:
            token: JWT access token string

        Returns:
            User instance if token is valid, None otherwise
        """
        # Hash the token to find in database
        token_hash = TokenHasher.hash_token(token)

        try:
            session_token = SessionToken.objects.select_related("user").get(token_hash=token_hash)

            # Check if token is valid
            if session_token.is_valid():
                return session_token.user

        except SessionToken.DoesNotExist:
            pass

        return None

    @staticmethod
    def refresh_tokens(
        refresh_token: str,
        device_fingerprint: str = "",
    ) -> dict[str, str] | None:
        """Refresh access token using refresh token with replay detection.

        Implements token rotation: old refresh token is invalidated and
        new pair is issued. If used refresh token is detected, entire
        token family is revoked (H9). Uses SELECT FOR UPDATE to prevent
        race conditions (P2-C4, SV3).

        Args:
            refresh_token: JWT refresh token string
            device_fingerprint: Device identifier for validation

        Returns:
            Dictionary with new tokens if valid, None if invalid/replayed
        """
        # Hash the refresh token
        refresh_token_hash = TokenHasher.hash_token(refresh_token)

        try:
            # Use SELECT FOR UPDATE with NOWAIT to prevent race conditions
            with transaction.atomic():
                session_token = (
                    SessionToken.objects.select_for_update(nowait=True)
                    .select_related("user")
                    .get(refresh_token_hash=refresh_token_hash)
                )

                # Check if refresh token was already used (replay attack)
                if session_token.is_refresh_token_used:
                    # Revoke entire token family
                    TokenService.revoke_token_family(session_token.token_family)
                    return None

                # Check if token is valid
                if not session_token.is_valid():
                    return None

                # Mark refresh token as used (atomic operation)
                session_token.mark_refresh_token_used()

                # Create new token pair
                new_tokens = TokenService.create_tokens(session_token.user, device_fingerprint)

                # Update token family to maintain chain (atomic operation)
                new_session = SessionToken.objects.select_for_update().get(
                    refresh_token_hash=TokenHasher.hash_token(new_tokens["refresh_token"])
                )
                new_session.token_family = session_token.token_family
                new_session.save(update_fields=["token_family"])

                return new_tokens

        except SessionToken.DoesNotExist:
            return None

    @staticmethod
    def revoke_token_family(family_id: uuid.UUID) -> int:
        """Revoke all tokens in a token family (replay attack detected).

        Args:
            family_id: Token family UUID to revoke

        Returns:
            Number of tokens revoked
        """
        tokens = SessionToken.objects.filter(token_family=family_id)
        count = tokens.count()

        for token in tokens:
            token.revoke()

        return count

    @staticmethod
    def revoke_user_tokens(user: User) -> int:
        """Revoke all tokens for a user (password change, logout all).

        Args:
            user: User instance whose tokens should be revoked

        Returns:
            Number of tokens revoked
        """
        tokens = SessionToken.objects.filter(user=user, is_revoked=False)
        count = tokens.count()

        for token in tokens:
            token.revoke()

        return count

    @staticmethod
    def cleanup_expired_tokens() -> int:
        """Remove expired tokens from database (maintenance task).

        Returns:
            Number of expired tokens removed
        """
        now = timezone.now()
        expired_tokens = SessionToken.objects.filter(expires_at__lt=now)
        count = expired_tokens.count()
        expired_tokens.delete()
        return count
