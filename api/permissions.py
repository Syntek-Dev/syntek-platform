"""GraphQL permission classes for access control.

Implementation stub for TDD - permissions return placeholder values.
"""

from typing import Any

from strawberry.permission import BasePermission
from strawberry.types import Info


class IsAuthenticated(BasePermission):
    """Permission class requiring user to be authenticated."""

    message = "User is not authenticated"

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check if user is authenticated.

        Args:
            source: Source object
            info: GraphQL execution info
            **kwargs: Additional arguments

        Returns:
            True if authenticated, False otherwise
        """
        return info.context.request.user.is_authenticated


class HasPermission(BasePermission):
    """Permission class requiring specific Django permission."""

    def __init__(self, permission: str) -> None:
        """Initialize with required permission.

        Args:
            permission: Django permission string (e.g., 'core.view_user')
        """
        self.permission = permission
        self.message = f"User lacks required permission: {permission}"

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check if user has required permission.

        Args:
            source: Source object
            info: GraphQL execution info
            **kwargs: Additional arguments

        Returns:
            True if user has permission, False otherwise
        """
        user = info.context.request.user
        return user.is_authenticated and user.has_perm(self.permission)


class IsOrganisationOwner(BasePermission):
    """Permission class requiring organisation owner role."""

    message = "User is not an organisation owner"

    def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        """Check if user is organisation owner.

        Args:
            source: Source object
            info: GraphQL execution info
            **kwargs: Additional arguments

        Returns:
            True if organisation owner, False otherwise
        """
        user = info.context.request.user
        if not user.is_authenticated:
            return False
        return user.groups.filter(name="Organisation Owner").exists()
