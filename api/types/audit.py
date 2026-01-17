"""GraphQL types for audit logs and security monitoring.

This module provides GraphQL types for accessing audit logs and
session management with proper organisation boundary enforcement.
"""

from datetime import datetime
from typing import TYPE_CHECKING

import strawberry

if TYPE_CHECKING:
    from apps.core.models import AuditLog, SessionToken


@strawberry.type
class AuditLogType:
    """GraphQL type for audit log entries.

    Exposes audit log information with IP addresses remaining encrypted.
    Users can only view logs for their own organisation.
    """

    id: strawberry.ID
    action: str
    user_id: strawberry.ID | None
    user_email: str | None
    organisation_id: strawberry.ID | None
    organisation_name: str | None
    user_agent: str
    device_fingerprint: str
    metadata: strawberry.scalars.JSON
    created_at: datetime

    @staticmethod
    def from_model(audit_log: AuditLog) -> AuditLogType:
        """Convert AuditLog model to GraphQL type.

        Args:
            audit_log: AuditLog model instance.

        Returns:
            AuditLogType instance.
        """
        return AuditLogType(
            id=strawberry.ID(str(audit_log.id)),
            action=audit_log.action,
            user_id=strawberry.ID(str(audit_log.user.id)) if audit_log.user else None,
            user_email=audit_log.user.email if audit_log.user else None,
            organisation_id=(
                strawberry.ID(str(audit_log.organisation.id)) if audit_log.organisation else None
            ),
            organisation_name=audit_log.organisation.name if audit_log.organisation else None,
            user_agent=audit_log.user_agent,
            device_fingerprint=audit_log.device_fingerprint,
            metadata=audit_log.metadata,
            created_at=audit_log.created_at,
        )


@strawberry.type
class SessionTokenType:
    """GraphQL type for user session information.

    Provides session details for current user's active sessions.
    Sensitive information (token hashes) is not exposed.
    """

    id: strawberry.ID
    created_at: datetime
    last_activity_at: datetime
    expires_at: datetime
    device_fingerprint: str
    user_agent: str
    is_current: bool

    @staticmethod
    def from_model(session: SessionToken, is_current: bool = False) -> SessionTokenType:
        """Convert SessionToken model to GraphQL type.

        Args:
            session: SessionToken model instance.
            is_current: Whether this is the current session.

        Returns:
            SessionTokenType instance.
        """
        return SessionTokenType(
            id=strawberry.ID(str(session.id)),
            created_at=session.created_at,
            last_activity_at=session.last_activity_at,
            expires_at=session.expires_at,
            device_fingerprint=session.device_fingerprint,
            user_agent=session.user_agent,
            is_current=is_current,
        )


@strawberry.type
class AuditLogConnection:
    """Paginated connection for audit logs."""

    items: list[AuditLogType]
    total_count: int
    has_next_page: bool
    has_previous_page: bool


@strawberry.type
class SessionManagementInfo:
    """Information about user's session management status."""

    active_sessions: list[SessionTokenType]
    total_sessions: int
    max_sessions: int
    can_create_new_session: bool


@strawberry.input
class AuditLogFilterInput:
    """Filter options for audit log queries."""

    action: str | None = None
    user_id: strawberry.ID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None


@strawberry.input
class PaginationInput:
    """Pagination parameters."""

    limit: int = 20
    offset: int = 0
