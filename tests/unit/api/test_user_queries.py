"""Unit tests for GraphQL user queries.

Tests cover:
- Current user (me) query
- User by ID query with organisation scoping
- Users list query with organisation boundaries
- Organisation query
- Audit log queries (user and organisation level)
- Permission enforcement for queries

These tests follow TDD - they test against minimal implementation stubs.
"""

from django.contrib.auth import get_user_model

import pytest

from apps.core.models import AuditLog, Organisation
from tests.factories import AuditLogFactory, OrganisationFactory, UserFactory

User = get_user_model()


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestMeQuery:
    """Test GraphQL me query for current authenticated user."""

    @pytest.fixture
    def authenticated_user(self, db) -> User:
        """Create authenticated user for testing.

        Returns:
            User instance with email verified
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(
            organisation=org,
            email_verified=True,
            first_name="Test",
            last_name="User",
        )
        return user

    def test_me_query_returns_current_user(self, client, authenticated_user) -> None:
        """Test me query returns authenticated user data.

        Given: Authenticated user
        When: me query is executed
        Then: User data is returned with all fields
        And: Organisation data is included
        """
        client.force_login(authenticated_user)

        query = """
        query {
            me {
                id
                email
                firstName
                lastName
                emailVerified
                twoFactorEnabled
                organisation {
                    id
                    name
                    slug
                }
                createdAt
            }
        }
        """

        response = client.post(
            "/graphql/",
            {"query": query},
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert data["data"]["me"]["email"] == authenticated_user.email
        assert data["data"]["me"]["firstName"] == "Test"
        assert data["data"]["me"]["lastName"] == "User"
        assert data["data"]["me"]["emailVerified"] is True
        assert data["data"]["me"]["organisation"]["name"] is not None

    def test_me_query_without_authentication(self, client) -> None:
        """Test me query returns null when not authenticated.

        Given: Unauthenticated request
        When: me query is executed
        Then: null is returned (not an error)
        """
        query = """
        query {
            me {
                id
                email
            }
        }
        """

        response = client.post(
            "/graphql/",
            {"query": query},
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert data["data"]["me"] is None

    def test_me_query_includes_profile_data(self, client, db) -> None:
        """Test me query includes user profile data.

        Given: Authenticated user with profile
        When: me query requests profile fields
        Then: Profile data is included in response
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org)
        client.force_login(user)

        query = """
        query {
            me {
                id
                email
                profile {
                    phone
                    timezone
                    language
                }
            }
        }
        """

        response = client.post(
            "/graphql/",
            {"query": query},
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert data["data"]["me"] is not None
        # Profile may be null if not created yet
        if data["data"]["me"]["profile"]:
            assert "timezone" in data["data"]["me"]["profile"]


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestUserQuery:
    """Test GraphQL query for single user by ID."""

    @pytest.fixture
    def organisation_with_users(self, db) -> tuple[Organisation, list[User]]:
        """Create organisation with multiple users.

        Returns:
            Tuple of (organisation, [users])
        """
        org = OrganisationFactory.create(name="Test Organisation")
        users = [UserFactory.create(organisation=org, first_name=f"User{i}") for i in range(3)]
        return org, users

    def test_user_query_returns_user_in_same_organisation(
        self, client, organisation_with_users
    ) -> None:
        """Test user query returns user from same organisation.

        Given: Authenticated user in organisation A
        When: user query is executed for another user in organisation A
        Then: User data is returned
        """
        org, users = organisation_with_users
        requester = users[0]
        target = users[1]
        client.force_login(requester)

        query = """
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                email
                firstName
                organisation {
                    id
                }
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": query,
                "variables": {"id": str(target.id)},
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert data["data"]["user"]["id"] == str(target.id)
        assert data["data"]["user"]["email"] == target.email

    def test_user_query_blocks_cross_organisation_access(self, client, db) -> None:
        """Test user query blocks access to users from different organisation.

        Given: Authenticated user in organisation A
        When: user query is executed for user in organisation B
        Then: null is returned (organisation boundary enforcement)
        """
        org_a = OrganisationFactory.create(name="Organisation A")
        org_b = OrganisationFactory.create(name="Organisation B")

        user_a = UserFactory.create(organisation=org_a)
        user_b = UserFactory.create(organisation=org_b)

        client.force_login(user_a)

        query = """
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                email
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": query,
                "variables": {"id": str(user_b.id)},
            },
            content_type="application/json",
        )

        data = response.json()
        # Should return null or error - cannot access cross-org user
        assert data["data"]["user"] is None or "errors" in data

    def test_user_query_requires_authentication(self, client, db) -> None:
        """Test user query requires authentication.

        Given: Unauthenticated request
        When: user query is executed
        Then: null or error is returned
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org)

        query = """
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                email
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": query,
                "variables": {"id": str(user.id)},
            },
            content_type="application/json",
        )

        data = response.json()
        assert data["data"]["user"] is None or "errors" in data


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestUsersQuery:
    """Test GraphQL query for users list."""

    @pytest.fixture
    def organisation_with_users(self, db) -> tuple[Organisation, list[User]]:
        """Create organisation with multiple users.

        Returns:
            Tuple of (organisation, [users])
        """
        org = OrganisationFactory.create(name="Test Organisation")
        users = [
            UserFactory.create(
                organisation=org,
                first_name=f"User{i}",
                email=f"user{i}@example.com",
            )
            for i in range(5)
        ]
        return org, users

    def test_users_query_returns_organisation_users(self, client, organisation_with_users) -> None:
        """Test users query returns only users from same organisation.

        Given: Organisation with 5 users
        When: users query is executed by a user in that organisation
        Then: All 5 users are returned
        And: No users from other organisations are included
        """
        org, users = organisation_with_users
        requester = users[0]
        client.force_login(requester)

        query = """
        query {
            users {
                id
                email
                firstName
            }
        }
        """

        response = client.post(
            "/graphql/",
            {"query": query},
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert len(data["data"]["users"]) == 5

    def test_users_query_respects_pagination(self, client, organisation_with_users) -> None:
        """Test users query supports limit and offset pagination.

        Given: Organisation with 5 users
        When: users query is executed with limit=2, offset=1
        Then: 2 users are returned starting from offset 1
        """
        org, users = organisation_with_users
        requester = users[0]
        client.force_login(requester)

        query = """
        query GetUsers($limit: Int, $offset: Int) {
            users(limit: $limit, offset: $offset) {
                id
                email
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": query,
                "variables": {"limit": 2, "offset": 1},
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert len(data["data"]["users"]) == 2

    def test_users_query_excludes_other_organisations(self, client, db) -> None:
        """Test users query excludes users from other organisations.

        Given: Two organisations with users
        When: users query is executed by user in organisation A
        Then: Only users from organisation A are returned
        """
        org_a = OrganisationFactory.create(name="Organisation A")
        org_b = OrganisationFactory.create(name="Organisation B")

        users_a = [UserFactory.create(organisation=org_a) for _ in range(3)]
        _users_b = [UserFactory.create(organisation=org_b) for _ in range(2)]

        client.force_login(users_a[0])

        query = """
        query {
            users {
                id
                organisation {
                    name
                }
            }
        }
        """

        response = client.post(
            "/graphql/",
            {"query": query},
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert len(data["data"]["users"]) == 3
        # All users should be from Organisation A
        for user_data in data["data"]["users"]:
            assert user_data["organisation"]["name"] == "Organisation A"

    def test_users_query_requires_authentication(self, client, db) -> None:
        """Test users query requires authentication.

        Given: Unauthenticated request
        When: users query is executed
        Then: Error or empty list is returned
        """
        org = OrganisationFactory.create()
        UserFactory.create_batch(3, organisation=org)

        query = """
        query {
            users {
                id
            }
        }
        """

        response = client.post(
            "/graphql/",
            {"query": query},
            content_type="application/json",
        )

        data = response.json()
        # Should require authentication
        assert "errors" in data or data["data"]["users"] == []


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestAuditLogQueries:
    """Test GraphQL audit log queries."""

    @pytest.fixture
    def user_with_audit_logs(self, db) -> tuple[User, list[AuditLog]]:
        """Create user with audit logs.

        Returns:
            Tuple of (user, [audit_logs])
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org)

        logs = [
            AuditLogFactory.create(
                user=user,
                organisation=org,
                action=action,
            )
            for action in ["login_success", "logout", "password_change"]
        ]
        return user, logs

    def test_my_audit_logs_query_returns_user_logs(self, client, user_with_audit_logs) -> None:
        """Test myAuditLogs query returns logs for current user.

        Given: Authenticated user with audit logs
        When: myAuditLogs query is executed
        Then: All audit logs for that user are returned
        And: Logs are ordered by most recent first
        """
        user, logs = user_with_audit_logs
        client.force_login(user)

        query = """
        query {
            myAuditLogs {
                id
                action
                createdAt
            }
        }
        """

        response = client.post(
            "/graphql/",
            {"query": query},
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert len(data["data"]["myAuditLogs"]) == 3

    def test_my_audit_logs_query_supports_pagination(self, client, user_with_audit_logs) -> None:
        """Test myAuditLogs query supports limit and offset.

        Given: User with multiple audit logs
        When: myAuditLogs query is executed with limit=1
        Then: Only 1 log is returned
        """
        user, logs = user_with_audit_logs
        client.force_login(user)

        query = """
        query GetAuditLogs($limit: Int) {
            myAuditLogs(limit: $limit) {
                id
                action
            }
        }
        """

        response = client.post(
            "/graphql/",
            {
                "query": query,
                "variables": {"limit": 1},
            },
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        assert len(data["data"]["myAuditLogs"]) == 1

    def test_organisation_audit_logs_query_requires_admin(self, client, db) -> None:
        """Test organisationAuditLogs query requires admin permission.

        Given: Regular user (not admin)
        When: organisationAuditLogs query is executed
        Then: Permission error is returned
        """
        org = OrganisationFactory.create()
        user = UserFactory.create(organisation=org)  # Regular user
        AuditLogFactory.create_batch(5, organisation=org)

        client.force_login(user)

        query = """
        query {
            organisationAuditLogs {
                id
                action
            }
        }
        """

        response = client.post(
            "/graphql/",
            {"query": query},
            content_type="application/json",
        )

        data = response.json()
        # Should require admin permission
        assert "errors" in data or data["data"]["organisationAuditLogs"] is None

    @pytest.mark.skip(reason="Admin permissions not implemented yet")
    def test_organisation_audit_logs_query_for_admin(self, client, db) -> None:
        """Test organisationAuditLogs query works for organisation admin.

        Given: Organisation admin user
        When: organisationAuditLogs query is executed
        Then: All organisation audit logs are returned
        """
        pass


@pytest.mark.unit
@pytest.mark.graphql
@pytest.mark.django_db
class TestOrganisationQuery:
    """Test GraphQL organisation query."""

    def test_organisation_query_returns_current_organisation(self, client, db) -> None:
        """Test organisation query returns user's organisation.

        Given: Authenticated user in an organisation
        When: Organisation data is queried through user.organisation
        Then: Organisation details are returned
        """
        org = OrganisationFactory.create(
            name="Test Organisation",
            slug="test-org",
            industry="Technology",
        )
        user = UserFactory.create(organisation=org)
        client.force_login(user)

        query = """
        query {
            me {
                organisation {
                    id
                    name
                    slug
                    industry
                    isActive
                }
            }
        }
        """

        response = client.post(
            "/graphql/",
            {"query": query},
            content_type="application/json",
        )

        data = response.json()
        assert "errors" not in data or data["errors"] is None
        org_data = data["data"]["me"]["organisation"]
        assert org_data["name"] == "Test Organisation"
        assert org_data["slug"] == "test-org"
        assert org_data["industry"] == "Technology"
        assert org_data["isActive"] is True
