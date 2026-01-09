"""GraphQL queries for user data.

Implements organisation boundary enforcement and uses DataLoaders (H2).
All queries respect multi-tenancy isolation.
"""

from typing import Any

from django.contrib.auth import get_user_model

import strawberry
from strawberry.types import Info

from api.errors import AuthenticationError, ErrorCode, PermissionError
from api.types.user import AuditLogType, UserType
from apps.core.models import AuditLog
from apps.core.utils.encryption import IPEncryption

User = get_user_model()


def _user_to_graphql_type(user: Any) -> UserType:
    """Convert Django User to GraphQL UserType.

    Args:
        user: Django User instance

    Returns:
        UserType for GraphQL with organisation_id and user_instance for DataLoaders
    """
    return UserType(
        id=strawberry.ID(str(user.id)),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        email_verified=user.email_verified,
        two_factor_enabled=user.two_factor_enabled,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        _organisation_id=user.organisation_id,
        _user_instance=user,
    )


def _audit_log_to_graphql_type(log: AuditLog) -> AuditLogType:
    """Convert AuditLog to GraphQL AuditLogType.

    Decrypts IP address for display.

    Args:
        log: AuditLog instance

    Returns:
        AuditLogType for GraphQL
    """
    # Decrypt IP address if present
    ip_address = None
    if log.ip_address:
        ip_address = IPEncryption.decrypt_ip(log.ip_address)

    return AuditLogType(
        id=strawberry.ID(str(log.id)),
        action=log.action,
        ip_address=ip_address,
        user_agent=log.user_agent,
        created_at=log.created_at,
    )


@strawberry.type
class UserQueries:
    """GraphQL queries for user-related data with organisation boundaries."""

    @strawberry.field
    def me(self, info: Info) -> UserType | None:
        """Get current authenticated user.

        Returns:
            Current user or None if not authenticated
        """
        user = info.context.request.user

        if not user.is_authenticated:
            return None

        return _user_to_graphql_type(user)

    @strawberry.field
    def user(self, info: Info, id: strawberry.ID) -> UserType | None:
        """Get user by ID (organisation-scoped).

        Enforces organisation boundary - users can only query users from
        their own organisation.

        Args:
            info: GraphQL execution info
            id: User ID

        Returns:
            User if in same organisation, None otherwise
        """
        current_user = info.context.request.user

        if not current_user.is_authenticated:
            raise AuthenticationError(ErrorCode.NOT_AUTHENTICATED, "Authentication required")

        try:
            # Query with organisation boundary enforcement
            # User IDs are UUIDs, so use str(id) directly
            user = User.objects.select_related("organisation").get(
                id=str(id), organisation=current_user.organisation
            )
            return _user_to_graphql_type(user)

        except (User.DoesNotExist, ValueError):
            return None

    @strawberry.field
    def users(self, info: Info, limit: int = 10, offset: int = 0) -> list[UserType]:
        """Get all users in current user's organisation.

        Enforces organisation boundary - only returns users from the same
        organisation as the authenticated user.

        Args:
            info: GraphQL execution info
            limit: Maximum users to return (default: 10, max: 100)
            offset: Pagination offset

        Returns:
            List of users from same organisation

        Raises:
            AuthenticationError: If user not authenticated
        """
        current_user = info.context.request.user

        if not current_user.is_authenticated:
            raise AuthenticationError(ErrorCode.NOT_AUTHENTICATED, "Authentication required")

        # Limit maximum page size
        if limit > 100:
            limit = 100

        # Query users from same organisation only
        users = (
            User.objects.filter(organisation=current_user.organisation)
            .select_related("organisation")
            .order_by("email")[offset : offset + limit]
        )

        return [_user_to_graphql_type(u) for u in users]

    @strawberry.field
    def my_audit_logs(self, info: Info, limit: int = 50, offset: int = 0) -> list[AuditLogType]:
        """Get audit logs for current user.

        Returns audit logs for the authenticated user only.

        Args:
            info: GraphQL execution info
            limit: Maximum logs to return (default: 50, max: 100)
            offset: Pagination offset

        Returns:
            List of audit logs for authenticated user

        Raises:
            AuthenticationError: If user not authenticated
        """
        current_user = info.context.request.user

        if not current_user.is_authenticated:
            raise AuthenticationError(ErrorCode.NOT_AUTHENTICATED, "Authentication required")

        # Limit maximum page size
        if limit > 100:
            limit = 100

        # Query audit logs for current user
        logs = (
            AuditLog.objects.filter(user=current_user)
            .select_related("user", "organisation")
            .order_by("-created_at")[offset : offset + limit]
        )

        return [_audit_log_to_graphql_type(log) for log in logs]

    @strawberry.field
    def organisation_audit_logs(
        self, info: Info, limit: int = 100, offset: int = 0
    ) -> list[AuditLogType]:
        """Get audit logs for organisation (admin only).

        Requires 'core.view_auditlog' permission. Returns logs for the
        authenticated user's organisation only.

        Args:
            info: GraphQL execution info
            limit: Maximum logs to return (default: 100, max: 500)
            offset: Pagination offset

        Returns:
            List of audit logs for organisation

        Raises:
            AuthenticationError: If user not authenticated
            PermissionError: If user not organisation admin
        """
        current_user = info.context.request.user

        if not current_user.is_authenticated:
            raise AuthenticationError(ErrorCode.NOT_AUTHENTICATED, "Authentication required")

        # Check permission
        if not current_user.has_perm("core.view_auditlog"):
            raise PermissionError(
                ErrorCode.PERMISSION_DENIED,
                "You do not have permission to view organisation audit logs",
            )

        # Limit maximum page size
        if limit > 500:
            limit = 500

        # Query audit logs for organisation
        logs = (
            AuditLog.objects.filter(organisation=current_user.organisation)
            .select_related("user", "organisation")
            .order_by("-created_at")[offset : offset + limit]
        )

        return [_audit_log_to_graphql_type(log) for log in logs]
