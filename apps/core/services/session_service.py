"""Session management service for concurrent session limits.

This module provides session tracking and management with configurable
concurrent session limits per user (Phase 7 - M7 requirement).

Security Features:
- Configurable max sessions per user
- Automatic termination of oldest sessions when limit exceeded
- Device fingerprinting for session identification
- Organisation-level session controls

Example:
    >>> SessionService.enforce_session_limit(user, request)
    >>> SessionService.get_active_sessions(user)
"""

from typing import TYPE_CHECKING

from django.conf import settings
from django.db import transaction
from django.utils import timezone

if TYPE_CHECKING:
    from apps.core.models import SessionToken, User


class SessionService:
    """Service for managing user sessions with concurrent session limits.

    Implements M7 requirement: configurable max sessions per user with
    automatic termination of oldest sessions when limit is exceeded.

    Configuration via settings:
    - MAX_CONCURRENT_SESSIONS: Maximum sessions per user (default: 5)
    - MAX_CONCURRENT_SESSIONS_PER_ORG: Organisation-level override

    Attributes:
        None - All methods are static
    """

    @staticmethod
    def get_max_sessions(user: User) -> int:
        """Get maximum concurrent sessions allowed for user.

        Checks organisation-level override first, then falls back to global setting.

        Args:
            user: User to check session limit for.

        Returns:
            Maximum number of concurrent sessions allowed.
        """
        # Check for organisation-level override
        if user.organisation:
            org_limit = getattr(user.organisation, "max_concurrent_sessions", None)
            if org_limit is not None:
                return org_limit

        # Fall back to global setting
        return getattr(settings, "MAX_CONCURRENT_SESSIONS", 5)

    @staticmethod
    def get_active_sessions(user: User) -> list[SessionToken]:
        """Get all active sessions for a user.

        Active sessions are non-revoked, non-expired sessions.

        Args:
            user: User to get sessions for.

        Returns:
            List of active SessionToken instances ordered by last activity.
        """
        from apps.core.models import SessionToken

        return list(
            SessionToken.objects.filter(user=user, is_revoked=False, expires_at__gt=timezone.now())
            .order_by("-last_activity_at")
            .select_related("user")
        )

    @staticmethod
    def get_session_count(user: User) -> int:
        """Get count of active sessions for a user.

        Args:
            user: User to count sessions for.

        Returns:
            Number of active sessions.
        """
        from apps.core.models import SessionToken

        return SessionToken.objects.filter(
            user=user, is_revoked=False, expires_at__gt=timezone.now()
        ).count()

    @staticmethod
    @transaction.atomic
    def enforce_session_limit(user: User, new_session: SessionToken) -> None:
        """Enforce concurrent session limit by revoking oldest sessions.

        Automatically terminates oldest sessions when the limit is exceeded.
        Uses database locking to prevent race conditions.

        Args:
            user: User who is creating a new session.
            new_session: Newly created session token.
        """
        from apps.core.models import SessionToken

        max_sessions = SessionService.get_max_sessions(user)

        # Get all active sessions (excluding the new one)
        active_sessions = (
            SessionToken.objects.filter(user=user, is_revoked=False, expires_at__gt=timezone.now())
            .exclude(id=new_session.id)
            .order_by("-last_activity_at")
            .select_for_update()
        )

        session_count = active_sessions.count()

        # If limit exceeded, revoke oldest sessions
        if session_count >= max_sessions:
            sessions_to_revoke = session_count - max_sessions + 1

            # Get oldest sessions (reverse order)
            oldest_sessions = list(
                active_sessions.order_by("last_activity_at")[:sessions_to_revoke]
            )

            # Revoke them
            for session in oldest_sessions:
                session.revoke()

    @staticmethod
    def revoke_session(session_id: str, user: User) -> bool:
        """Revoke a specific session for a user.

        Args:
            session_id: UUID of the session to revoke.
            user: User who owns the session.

        Returns:
            True if session was revoked, False if not found.
        """
        from apps.core.models import SessionToken

        try:
            session = SessionToken.objects.get(id=session_id, user=user)
            session.revoke()
            return True
        except SessionToken.DoesNotExist:
            return False

    @staticmethod
    def revoke_all_sessions_except_current(user: User, current_session: SessionToken) -> int:
        """Revoke all user sessions except the current one.

        Useful for "logout from all other devices" functionality.

        Args:
            user: User whose sessions to revoke.
            current_session: Session to keep active.

        Returns:
            Number of sessions revoked.
        """
        from apps.core.models import SessionToken

        sessions_to_revoke = SessionToken.objects.filter(
            user=user, is_revoked=False, expires_at__gt=timezone.now()
        ).exclude(id=current_session.id)

        count = sessions_to_revoke.count()

        for session in sessions_to_revoke:
            session.revoke()

        return count

    @staticmethod
    def revoke_all_sessions(user: User) -> int:
        """Revoke all active sessions for a user.

        Used when password is changed or account is disabled.

        Args:
            user: User whose sessions to revoke.

        Returns:
            Number of sessions revoked.
        """
        from apps.core.models import SessionToken

        sessions = SessionToken.objects.filter(
            user=user, is_revoked=False, expires_at__gt=timezone.now()
        )

        count = sessions.count()

        for session in sessions:
            session.revoke()

        return count

    @staticmethod
    def get_session_info(user: User) -> dict:
        """Get detailed session information for a user.

        Returns session statistics and device information.

        Args:
            user: User to get session info for.

        Returns:
            Dictionary with session statistics and device list.
        """
        from apps.core.utils.encryption import IPEncryption

        active_sessions = SessionService.get_active_sessions(user)
        max_sessions = SessionService.get_max_sessions(user)

        devices = []
        for session in active_sessions:
            # Decrypt IP address for display
            ip_address = "Unknown"
            if session.ip_address:
                try:
                    ip_address = IPEncryption.decrypt_ip(session.ip_address)
                except Exception:
                    ip_address = "[Encrypted]"

            devices.append(
                {
                    "session_id": str(session.id),
                    "device_fingerprint": session.device_fingerprint,
                    "ip_address": ip_address,
                    "user_agent": session.user_agent,
                    "last_activity": session.last_activity_at,
                    "created_at": session.created_at,
                }
            )

        return {
            "active_sessions": len(active_sessions),
            "max_sessions": max_sessions,
            "sessions_available": max(0, max_sessions - len(active_sessions)),
            "devices": devices,
        }
