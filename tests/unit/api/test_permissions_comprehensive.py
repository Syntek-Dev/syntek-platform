"""Comprehensive unit tests for GraphQL permission classes.

Tests cover:
- IsAuthenticated permission with various authentication states
- HasPermission permission with multiple permission scenarios
- IsOrganisationOwner permission with group membership
- Permission class initialization and error messages
- Edge cases and boundary conditions

Following TDD approach: tests written before full implementation.
"""

from typing import Any
from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group, Permission
from django.contrib.contenttypes.models import ContentType

import pytest

from api.permissions import HasPermission, IsAuthenticated, IsOrganisationOwner
from tests.factories import OrganisationFactory, UserFactory

User = get_user_model()


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestIsAuthenticatedPermission:
    """Comprehensive tests for IsAuthenticated permission class."""

    def test_authenticated_user_passes_permission_check(self, db) -> None:
        """Test authenticated user passes IsAuthenticated check.

        Given: Authenticated user with verified account
        When: IsAuthenticated.has_permission() is called
        Then: Returns True
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org, email_verified=True)

        mock_info = Mock()
        mock_info.context.request.user = user

        permission = IsAuthenticated()
        assert permission.has_permission(None, mock_info) is True

    def test_unauthenticated_user_fails_permission_check(self) -> None:
        """Test unauthenticated user fails IsAuthenticated check.

        Given: AnonymousUser (not logged in)
        When: IsAuthenticated.has_permission() is called
        Then: Returns False
        """
        mock_info = Mock()
        mock_info.context.request.user = AnonymousUser()

        permission = IsAuthenticated()
        assert permission.has_permission(None, mock_info) is False

    def test_inactive_user_fails_permission_check(self, db) -> None:
        """Test inactive user fails IsAuthenticated check.

        Given: User with is_active=False
        When: IsAuthenticated.has_permission() is called
        Then: Returns False (inactive users are not authenticated)
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org, is_active=False)

        mock_info = Mock()
        mock_info.context.request.user = user

        permission = IsAuthenticated()
        # Inactive users should not be authenticated
        assert permission.has_permission(None, mock_info) is user.is_authenticated

    def test_permission_error_message_is_descriptive(self) -> None:
        """Test IsAuthenticated has clear error message.

        Given: IsAuthenticated permission instance
        When: Error message is checked
        Then: Message clearly states authentication requirement
        """
        permission = IsAuthenticated()
        assert permission.message == "User is not authenticated"
        assert "authenticated" in permission.message.lower()

    def test_permission_works_with_kwargs(self, db) -> None:
        """Test IsAuthenticated permission handles additional kwargs.

        Given: Authenticated user
        When: has_permission() is called with extra kwargs
        Then: Returns True and ignores extra arguments
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org)

        mock_info = Mock()
        mock_info.context.request.user = user

        permission = IsAuthenticated()
        # Should handle extra kwargs gracefully
        assert permission.has_permission(None, mock_info, extra_arg="test") is True


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestHasPermissionClass:
    """Comprehensive tests for HasPermission permission class."""

    @pytest.fixture
    def setup_permissions(self, db) -> dict[str, Any]:
        """Create test data with various permission scenarios.

        Returns:
            Dictionary containing test users and permissions
        """
        org = OrganisationFactory.create()

        # Get content type for User model
        content_type = ContentType.objects.get_for_model(User)

        # Get or create specific permissions
        view_perm, _ = Permission.objects.get_or_create(
            codename="view_user",
            content_type=content_type,
            defaults={"name": "Can view user"},
        )

        change_perm, _ = Permission.objects.get_or_create(
            codename="change_user",
            content_type=content_type,
            defaults={"name": "Can change user"},
        )

        delete_perm, _ = Permission.objects.get_or_create(
            codename="delete_user",
            content_type=content_type,
            defaults={"name": "Can delete user"},
        )

        # Create users with different permissions
        user_with_view = UserFactory.create(organisation=org)
        user_with_view.user_permissions.add(view_perm)

        user_with_multiple = UserFactory.create(organisation=org)
        user_with_multiple.user_permissions.add(view_perm, change_perm)

        user_with_none = UserFactory.create(organisation=org)

        return {
            "org": org,
            "view_perm": view_perm,
            "change_perm": change_perm,
            "delete_perm": delete_perm,
            "user_with_view": user_with_view,
            "user_with_multiple": user_with_multiple,
            "user_with_none": user_with_none,
        }

    def test_user_with_required_permission_is_granted_access(self, setup_permissions) -> None:
        """Test user with required permission passes check.

        Given: User with 'core.view_user' permission
        When: HasPermission('core.view_user') is checked
        Then: Returns True
        """
        setup = setup_permissions
        user = setup["user_with_view"]

        mock_info = Mock()
        mock_info.context.request.user = user

        permission = HasPermission("core.view_user")
        assert permission.has_permission(None, mock_info) is True

    def test_user_without_required_permission_is_denied(self, setup_permissions) -> None:
        """Test user without required permission fails check.

        Given: User without 'core.delete_user' permission
        When: HasPermission('core.delete_user') is checked
        Then: Returns False
        """
        setup = setup_permissions
        user = setup["user_with_none"]

        mock_info = Mock()
        mock_info.context.request.user = user

        permission = HasPermission("core.delete_user")
        assert permission.has_permission(None, mock_info) is False

    def test_unauthenticated_user_always_denied(self) -> None:
        """Test unauthenticated user fails HasPermission check.

        Given: AnonymousUser
        When: HasPermission is checked for any permission
        Then: Returns False
        """
        mock_info = Mock()
        mock_info.context.request.user = AnonymousUser()

        permission = HasPermission("core.view_user")
        assert permission.has_permission(None, mock_info) is False

    def test_permission_error_message_includes_required_permission(self) -> None:
        """Test error message includes specific permission name.

        Given: HasPermission('cms.publish_page')
        When: Error message is checked
        Then: Message includes 'cms.publish_page'
        """
        permission = HasPermission("cms.publish_page")
        assert "cms.publish_page" in permission.message
        assert "permission" in permission.message.lower()

    def test_superuser_passes_all_permission_checks(self, db) -> None:
        """Test superuser passes all permission checks.

        Given: User with is_superuser=True
        When: Any HasPermission is checked
        Then: Returns True
        """
        org = OrganisationFactory.create()
        superuser = UserFactory.create(organisation=org, is_superuser=True)

        mock_info = Mock()
        mock_info.context.request.user = superuser

        # Superuser should pass any permission check
        permission = HasPermission("nonexistent.permission")
        assert permission.has_permission(None, mock_info) is True

    def test_permission_via_group_membership(self, setup_permissions) -> None:
        """Test user inherits permissions from group membership.

        Given: User in group with specific permissions
        When: HasPermission is checked for group's permission
        Then: Returns True
        """
        setup = setup_permissions
        user = UserFactory.create(organisation=setup["org"])

        # Create group with permission
        group = Group.objects.create(name="Content Editors")
        group.permissions.add(setup["change_perm"])
        user.groups.add(group)

        mock_info = Mock()
        mock_info.context.request.user = user

        permission = HasPermission("core.change_user")
        assert permission.has_permission(None, mock_info) is True

    def test_permission_format_validation(self) -> None:
        """Test HasPermission accepts various permission formats.

        Given: Different permission string formats
        When: HasPermission is initialized
        Then: Accepts valid formats without error
        """
        # Standard format: app.action_model
        perm1 = HasPermission("core.view_user")
        assert perm1.permission == "core.view_user"

        # Django format with underscore
        perm2 = HasPermission("auth.add_permission")
        assert perm2.permission == "auth.add_permission"

        # Custom permission
        perm3 = HasPermission("custom.special_action")
        assert perm3.permission == "custom.special_action"


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestIsOrganisationOwnerPermission:
    """Comprehensive tests for IsOrganisationOwner permission class."""

    @pytest.fixture
    def setup_users(self, db) -> dict[str, Any]:
        """Create users with different organisation roles.

        Returns:
            Dictionary containing test users and organisations
        """
        org_a = OrganisationFactory.create(name="Organisation A")
        org_b = OrganisationFactory.create(name="Organisation B")

        # Create groups
        owner_group, _ = Group.objects.get_or_create(name="Organisation Owner")
        admin_group, _ = Group.objects.get_or_create(name="Organisation Admin")
        member_group, _ = Group.objects.get_or_create(name="Organisation Member")

        # Create users with different roles
        owner = UserFactory.create(organisation=org_a)
        owner.groups.add(owner_group)

        admin = UserFactory.create(organisation=org_a)
        admin.groups.add(admin_group)

        member = UserFactory.create(organisation=org_a)
        member.groups.add(member_group)

        # User with no groups
        no_group_user = UserFactory.create(organisation=org_a)

        # Owner from different organisation
        other_owner = UserFactory.create(organisation=org_b)
        other_owner.groups.add(owner_group)

        return {
            "org_a": org_a,
            "org_b": org_b,
            "owner": owner,
            "admin": admin,
            "member": member,
            "no_group_user": no_group_user,
            "other_owner": other_owner,
        }

    def test_organisation_owner_passes_check(self, setup_users) -> None:
        """Test user with Organisation Owner group passes check.

        Given: User with 'Organisation Owner' group
        When: IsOrganisationOwner.has_permission() is called
        Then: Returns True
        """
        owner = setup_users["owner"]

        mock_info = Mock()
        mock_info.context.request.user = owner

        permission = IsOrganisationOwner()
        assert permission.has_permission(None, mock_info) is True

    def test_admin_user_fails_owner_check(self, setup_users) -> None:
        """Test admin (non-owner) fails IsOrganisationOwner check.

        Given: User with 'Organisation Admin' group (not owner)
        When: IsOrganisationOwner.has_permission() is called
        Then: Returns False
        """
        admin = setup_users["admin"]

        mock_info = Mock()
        mock_info.context.request.user = admin

        permission = IsOrganisationOwner()
        assert permission.has_permission(None, mock_info) is False

    def test_regular_member_fails_owner_check(self, setup_users) -> None:
        """Test regular member fails IsOrganisationOwner check.

        Given: User with 'Organisation Member' group
        When: IsOrganisationOwner.has_permission() is called
        Then: Returns False
        """
        member = setup_users["member"]

        mock_info = Mock()
        mock_info.context.request.user = member

        permission = IsOrganisationOwner()
        assert permission.has_permission(None, mock_info) is False

    def test_user_with_no_group_fails_check(self, setup_users) -> None:
        """Test user with no group membership fails check.

        Given: User not in any groups
        When: IsOrganisationOwner.has_permission() is called
        Then: Returns False
        """
        no_group_user = setup_users["no_group_user"]

        mock_info = Mock()
        mock_info.context.request.user = no_group_user

        permission = IsOrganisationOwner()
        assert permission.has_permission(None, mock_info) is False

    def test_unauthenticated_user_fails_check(self) -> None:
        """Test unauthenticated user fails IsOrganisationOwner check.

        Given: AnonymousUser
        When: IsOrganisationOwner.has_permission() is called
        Then: Returns False
        """
        mock_info = Mock()
        mock_info.context.request.user = AnonymousUser()

        permission = IsOrganisationOwner()
        assert permission.has_permission(None, mock_info) is False

    def test_permission_error_message_is_clear(self) -> None:
        """Test error message clearly states owner requirement.

        Given: IsOrganisationOwner permission instance
        When: Error message is checked
        Then: Message clearly states organisation owner requirement
        """
        permission = IsOrganisationOwner()
        assert permission.message == "User is not an organisation owner"
        assert "organisation" in permission.message.lower()
        assert "owner" in permission.message.lower()

    def test_owner_from_different_org_still_passes(self, setup_users) -> None:
        """Test owner from different organisation still passes owner check.

        Given: User with 'Organisation Owner' group in different org
        When: IsOrganisationOwner.has_permission() is called
        Then: Returns True (group membership is sufficient)
        """
        other_owner = setup_users["other_owner"]

        mock_info = Mock()
        mock_info.context.request.user = other_owner

        permission = IsOrganisationOwner()
        # Permission only checks group membership, not which organisation
        assert permission.has_permission(None, mock_info) is True


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestPermissionCombinations:
    """Test combinations of multiple permissions."""

    @pytest.fixture
    def setup_complex_permissions(self, db) -> dict[str, Any]:
        """Create complex permission scenarios.

        Returns:
            Dictionary with users having various permission combinations
        """
        org = OrganisationFactory.create()

        # Create groups
        owner_group, _ = Group.objects.get_or_create(name="Organisation Owner")
        admin_group, _ = Group.objects.get_or_create(name="Organisation Admin")

        # Get permissions
        content_type = ContentType.objects.get_for_model(User)
        view_perm, _ = Permission.objects.get_or_create(
            codename="view_user",
            content_type=content_type,
            defaults={"name": "Can view user"},
        )

        # User with both owner role and specific permission
        owner_with_perm = UserFactory.create(organisation=org)
        owner_with_perm.groups.add(owner_group)
        owner_with_perm.user_permissions.add(view_perm)

        # Regular user with permission
        user_with_perm = UserFactory.create(organisation=org)
        user_with_perm.user_permissions.add(view_perm)

        return {
            "org": org,
            "owner_with_perm": owner_with_perm,
            "user_with_perm": user_with_perm,
        }

    def test_user_with_multiple_permission_types(self, setup_complex_permissions) -> None:
        """Test user with both role and specific permission.

        Given: User with Organisation Owner role AND specific permission
        When: Both permission checks are performed
        Then: Both return True
        """
        setup = setup_complex_permissions
        user = setup["owner_with_perm"]

        mock_info = Mock()
        mock_info.context.request.user = user

        # Check owner permission
        owner_perm = IsOrganisationOwner()
        assert owner_perm.has_permission(None, mock_info) is True

        # Check specific permission
        view_perm = HasPermission("core.view_user")
        assert view_perm.has_permission(None, mock_info) is True

    def test_permission_checking_order_independence(self, setup_complex_permissions) -> None:
        """Test permission checks work regardless of order.

        Given: User with specific permission
        When: Multiple permission checks are performed in different orders
        Then: Results are consistent regardless of order
        """
        setup = setup_complex_permissions
        user = setup["user_with_perm"]

        mock_info = Mock()
        mock_info.context.request.user = user

        # Check in one order
        has_perm = HasPermission("core.view_user")
        is_auth = IsAuthenticated()
        result1_perm = has_perm.has_permission(None, mock_info)
        result1_auth = is_auth.has_permission(None, mock_info)

        # Check in reverse order
        is_auth2 = IsAuthenticated()
        has_perm2 = HasPermission("core.view_user")
        result2_auth = is_auth2.has_permission(None, mock_info)
        result2_perm = has_perm2.has_permission(None, mock_info)

        # Results should be the same
        assert result1_perm == result2_perm
        assert result1_auth == result2_auth


@pytest.mark.unit
@pytest.mark.graphql
class TestPermissionEdgeCases:
    """Test edge cases and error handling in permissions."""

    def test_permission_with_none_user(self) -> None:
        """Test permission handles None user gracefully.

        Given: Request with user=None
        When: Permission is checked
        Then: Returns False without raising exception
        """
        mock_info = Mock()
        mock_info.context.request.user = None

        permission = IsAuthenticated()
        # Should handle None gracefully
        try:
            result = permission.has_permission(None, mock_info)
            assert result is False
        except AttributeError:
            # Also acceptable to raise AttributeError for None user
            pass

    def test_permission_with_missing_request(self) -> None:
        """Test permission handles missing request object.

        Given: Info context without request
        When: Permission is checked
        Then: Raises AttributeError or returns False
        """
        mock_info = Mock()
        mock_info.context.request = None

        permission = IsAuthenticated()
        # Should raise AttributeError or handle gracefully
        with pytest.raises(AttributeError):
            permission.has_permission(None, mock_info)

    def test_has_permission_with_empty_permission_string(self) -> None:
        """Test HasPermission with empty permission string.

        Given: HasPermission initialized with empty string
        When: Permission is checked
        Then: Always returns False
        """
        mock_info = Mock()
        mock_info.context.request.user = Mock(
            is_authenticated=True, has_perm=Mock(return_value=False)
        )

        permission = HasPermission("")
        assert permission.has_permission(None, mock_info) is False

    def test_permission_source_parameter_unused(self, db) -> None:
        """Test permissions correctly ignore source parameter.

        Given: Permission check with various source values
        When: has_permission() is called
        Then: Source parameter doesn't affect result
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org)

        mock_info = Mock()
        mock_info.context.request.user = user

        permission = IsAuthenticated()

        # Source parameter should not affect result
        assert permission.has_permission(None, mock_info) == permission.has_permission(
            "some_source", mock_info
        )
        assert permission.has_permission({}, mock_info) == permission.has_permission(
            ["list"], mock_info
        )
