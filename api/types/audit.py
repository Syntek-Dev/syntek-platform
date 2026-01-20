"""GraphQL types for audit logs and security monitoring.

This module provides GraphQL types for accessing audit logs and
session management with proper organisation boundary enforcement.
"""

from __future__ import annotations

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
    Uses DataLoaders for user and organisation relationships to prevent N+1 queries.
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

    # Private fields for DataLoader lookups
    _user_id_internal: strawberry.Private[int | None] = None
    _organisation_id_internal: strawberry.Private[int | None] = None
    _audit_log_instance: strawberry.Private[AuditLog | None] = None

    @staticmethod
    def from_model(audit_log: AuditLog) -> AuditLogType:
        """Convert AuditLog model to GraphQL type.

        Stores the audit log instance for potential DataLoader usage.
        If user/organisation are already loaded (via select_related),
        extracts their data immediately to avoid extra queries.

        Args:
            audit_log: AuditLog model instance.

        Returns:
            AuditLogType instance.
        """
        # Extract user data if available
        user_id = None
        user_email = None
        if audit_log.user_id:
            user_id = strawberry.ID(str(audit_log.user_id))
            # Try to get email from loaded user, otherwise will need DataLoader
            try:
                user_email = audit_log.user.email if audit_log.user else None
            except AttributeError:
                # User not loaded, will use DataLoader if needed
                pass

        # Extract organisation data if available
        organisation_id = None
        organisation_name = None
        if audit_log.organisation_id:
            organisation_id = strawberry.ID(str(audit_log.organisation_id))
            # Try to get name from loaded organisation
            try:
                organisation_name = audit_log.organisation.name if audit_log.organisation else None
            except AttributeError:
                # Organisation not loaded, will use DataLoader if needed
                pass

        return AuditLogType(
            id=strawberry.ID(str(audit_log.id)),
            action=audit_log.action,
            user_id=user_id,
            user_email=user_email,
            organisation_id=organisation_id,
            organisation_name=organisation_name,
            user_agent=audit_log.user_agent,
            device_fingerprint=audit_log.device_fingerprint,
            metadata=audit_log.metadata,
            created_at=audit_log.created_at,
            _user_id_internal=audit_log.user_id,
            _organisation_id_internal=audit_log.organisation_id,
            _audit_log_instance=audit_log,
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
