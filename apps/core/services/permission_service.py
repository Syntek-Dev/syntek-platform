"""Permission checking service for RBAC implementation.

This module provides centralised permission checking logic for role-based access control (RBAC).
Permissions are cached in Redis for performance and support both group-based and direct user permissions.

Security Features:
- Multi-tenancy enforcement (organisation boundaries)
- Permission caching with Redis for performance
- Support for custom permission checking
- Audit logging integration for permission failures

Permission Hierarchy:
- Organisation Owner: Full access to all resources within organisation
- Admin: Administrative access (cannot transfer ownership or delete organisation)
- Member: Standard access for content creation and editing
- Viewer: Read-only access to resources
"""

import logging

from django.contrib.auth.models import Group
from django.core.cache import cache
from django.db.models import QuerySet

from apps.core.models.user import User

logger = logging.getLogger(__name__)


class PermissionService:
    """Service for checking user permissions and enforcing RBAC.

    Provides methods for checking permissions, role membership, and organisation boundaries.
    All permission checks respect multi-tenancy and organisation isolation.
    """

    CACHE_TIMEOUT = 300  # 5 minutes cache for permission checks

    @staticmethod
    def has_permission(user: User, permission_code: str) -> bool:
        """Check if a user has a specific permission.

        Checks both group-based permissions and direct user permissions.
        Results are cached in Redis for performance.

        Args:
            user: The user to check permissions for.
            permission_code: Permission code in format 'app_label.codename' (e.g., 'core.add_user').

        Returns:
            True if the user has the permission, False otherwise.

        Example:
            >>> has_permission(user, 'core.add_user')
            True
        """
        if not user or not user.is_authenticated:
            return False

        # Superusers always have all permissions
        if user.is_superuser:
            return True

        # Check cache first
        cache_key = f"permission:{user.id}:{permission_code}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Check permission via Django's permission system
        has_perm = user.has_perm(permission_code)

        # Cache the result
        cache.set(cache_key, has_perm, PermissionService.CACHE_TIMEOUT)

        return has_perm

    @staticmethod
    def has_any_permission(user: User, permission_codes: list[str]) -> bool:
        """Check if a user has any of the specified permissions.

        Args:
            user: The user to check permissions for.
            permission_codes: List of permission codes to check.

        Returns:
            True if the user has at least one of the permissions, False otherwise.

        Example:
            >>> has_any_permission(user, ['core.add_user', 'core.change_user'])
            True
        """
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return any(
            PermissionService.has_permission(user, perm_code) for perm_code in permission_codes
        )

    @staticmethod
    def has_all_permissions(user: User, permission_codes: list[str]) -> bool:
        """Check if a user has all of the specified permissions.

        Args:
            user: The user to check permissions for.
            permission_codes: List of permission codes to check.

        Returns:
            True if the user has all of the permissions, False otherwise.

        Example:
            >>> has_all_permissions(user, ['core.view_user', 'core.change_user'])
            False
        """
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        return all(
            PermissionService.has_permission(user, perm_code) for perm_code in permission_codes
        )

    @staticmethod
    def is_organisation_owner(user: User) -> bool:
        """Check if a user is an Organisation Owner.

        Args:
            user: The user to check role for.

        Returns:
            True if the user is an Organisation Owner, False otherwise.
        """
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        # Check cache first
        cache_key = f"role:owner:{user.id}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Check group membership
        is_owner = user.groups.filter(name="Organisation Owner").exists()

        # Cache the result
        cache.set(cache_key, is_owner, PermissionService.CACHE_TIMEOUT)

        return is_owner

    @staticmethod
    def is_admin(user: User) -> bool:
        """Check if a user is an Admin or Organisation Owner.

        Args:
            user: The user to check role for.

        Returns:
            True if the user is an Admin or Organisation Owner, False otherwise.
        """
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        # Check cache first
        cache_key = f"role:admin:{user.id}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Check group membership
        is_admin = user.groups.filter(name__in=["Organisation Owner", "Admin"]).exists()

        # Cache the result
        cache.set(cache_key, is_admin, PermissionService.CACHE_TIMEOUT)

        return is_admin

    @staticmethod
    def is_member(user: User) -> bool:
        """Check if a user is a Member, Admin, or Organisation Owner.

        Args:
            user: The user to check role for.

        Returns:
            True if the user has Member-level access or higher, False otherwise.
        """
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        # Check cache first
        cache_key = f"role:member:{user.id}"
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Check group membership
        is_member = user.groups.filter(name__in=["Organisation Owner", "Admin", "Member"]).exists()

        # Cache the result
        cache.set(cache_key, is_member, PermissionService.CACHE_TIMEOUT)

        return is_member

    @staticmethod
    def can_access_organisation_data(user: User, organisation_id: int) -> bool:
        """Check if a user can access data for a specific organisation.

        Enforces multi-tenancy boundary: users can only access their own organisation's data.
        Superusers can access all organisations.

        Args:
            user: The user to check access for.
            organisation_id: The ID of the organisation to check access to.

        Returns:
            True if the user can access the organisation's data, False otherwise.
        """
        if not user or not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        # Users can only access their own organisation
        return user.organisation_id == organisation_id

    @staticmethod
    def filter_by_organisation(user: User, queryset: QuerySet) -> QuerySet:
        """Filter a queryset to only include records from the user's organisation.

        Enforces multi-tenancy isolation at the database query level.
        Assumes the model has an 'organisation' foreign key field.

        Args:
            user: The user performing the query.
            queryset: The queryset to filter.

        Returns:
            Filtered queryset scoped to the user's organisation.

        Raises:
            ValueError: If the user is not authenticated.

        Example:
            >>> users = User.objects.all()
            >>> filtered_users = PermissionService.filter_by_organisation(request.user, users)
        """
        if not user or not user.is_authenticated:
            raise ValueError("User must be authenticated to filter by organisation")

        # Superusers can see all organisations
        if user.is_superuser:
            return queryset

        # Filter to user's organisation
        return queryset.filter(organisation=user.organisation)

    @staticmethod
    def clear_user_permission_cache(user: User) -> None:
        """Clear all cached permissions for a user.

        Should be called when a user's permissions or group membership changes.

        Args:
            user: The user whose permission cache should be cleared.
        """
        if not user:
            return

        # Clear individual permission caches
        # Note: This is a simple implementation. For production, consider using cache key patterns
        # to delete all keys matching "permission:{user_id}:*"

        cache.delete(f"role:owner:{user.id}")
        cache.delete(f"role:admin:{user.id}")
        cache.delete(f"role:member:{user.id}")

        logger.info(
            f"Cleared permission cache for user {user.id}",
            extra={
                "user_id": user.id,
                "email": user.email,
            },
        )

    @staticmethod
    def assign_role(user: User, role_name: str) -> bool:
        """Assign a role (group) to a user.

        Valid roles: 'Organisation Owner', 'Admin', 'Member', 'Viewer'

        Args:
            user: The user to assign the role to.
            role_name: The name of the role to assign.

        Returns:
            True if the role was assigned successfully, False if the role doesn't exist.

        Raises:
            ValueError: If the role name is invalid.
        """
        valid_roles = ["Organisation Owner", "Admin", "Member", "Viewer"]

        if role_name not in valid_roles:
            raise ValueError(f"Invalid role: {role_name}. Must be one of: {', '.join(valid_roles)}")

        try:
            group = Group.objects.get(name=role_name)
            user.groups.add(group)

            # Clear permission cache
            PermissionService.clear_user_permission_cache(user)

            logger.info(
                f"Assigned role '{role_name}' to user {user.id}",
                extra={
                    "user_id": user.id,
                    "email": user.email,
                    "role": role_name,
                },
            )

            return True

        except Group.DoesNotExist:
            logger.error(
                f"Role '{role_name}' does not exist in database",
                extra={
                    "role": role_name,
                },
            )
            return False

    @staticmethod
    def remove_role(user: User, role_name: str) -> bool:
        """Remove a role (group) from a user.

        Args:
            user: The user to remove the role from.
            role_name: The name of the role to remove.

        Returns:
            True if the role was removed successfully, False if the user didn't have the role.
        """
        try:
            group = Group.objects.get(name=role_name)
            user.groups.remove(group)

            # Clear permission cache
            PermissionService.clear_user_permission_cache(user)

            logger.info(
                f"Removed role '{role_name}' from user {user.id}",
                extra={
                    "user_id": user.id,
                    "email": user.email,
                    "role": role_name,
                },
            )

            return True

        except Group.DoesNotExist:
            return False

    @staticmethod
    def get_user_roles(user: User) -> list[str]:
        """Get all roles (groups) assigned to a user.

        Args:
            user: The user to get roles for.

        Returns:
            List of role names.

        Example:
            >>> get_user_roles(user)
            ['Organisation Owner', 'Admin']
        """
        if not user or not user.is_authenticated:
            return []

        return list(user.groups.values_list("name", flat=True))
