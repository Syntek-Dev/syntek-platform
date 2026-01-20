# GraphQL Tests

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team

---

## Overview

GraphQL tests verify queries, mutations, and subscriptions using the Strawberry GraphQL framework.

---

## Directory Structure

```
graphql/
├── README.md              # This file
└── __init__.py
```

---

## Test Structure

GraphQL tests verify API schema operations:

```python
# test_user_queries.py

import pytest
from django.contrib.auth import get_user_model
from apps.core.models import Organisation

User = get_user_model()


@pytest.mark.graphql
class TestUserQueries:
    """Test GraphQL queries for users."""

    @pytest.fixture
    def organisation(self, db):
        """Create test organisation."""
        return Organisation.objects.create(
            name="Test Org",
            slug="test-org"
        )

    @pytest.fixture
    def user(self, db, organisation):
        """Create test user."""
        return User.objects.create_user(
            email="user@example.com",
            password="test123",
            organisation=organisation
        )

    def test_user_query(self, graphql_client, user):
        """Test user query returns correct data.

        Query:
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                email
                firstName
                lastName
            }
        }
        """
        query = """
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                email
                firstName
                lastName
            }
        }
        """

        response = graphql_client.execute(
            query,
            variables={"id": str(user.id)}
        )

        assert response["data"]["user"]["id"] == str(user.id)
        assert response["data"]["user"]["email"] == "user@example.com"

    def test_users_query_respects_organisation(self, graphql_client, user):
        """Test users query filters by organisation."""
        query = """
        query GetUsers {
            users {
                id
                email
            }
        }
        """

        # Authenticate as user
        graphql_client.force_login(user)

        response = graphql_client.execute(query)

        # Should only see users in their organisation
        user_ids = [u["id"] for u in response["data"]["users"]]
        assert str(user.id) in user_ids

    def test_user_mutation(self, graphql_client, user):
        """Test updating user via mutation."""
        mutation = """
        mutation UpdateUser($id: ID!, $firstName: String!) {
            updateUser(id: $id, firstName: $firstName) {
                user {
                    id
                    firstName
                }
            }
        }
        """

        graphql_client.force_login(user)

        response = graphql_client.execute(
            mutation,
            variables={
                "id": str(user.id),
                "firstName": "Updated"
            }
        )

        assert response["data"]["updateUser"]["user"]["firstName"] == "Updated"
```

---

## Best Practices

### 1. Test Permissions

```python
def test_user_cannot_view_other_users(self, graphql_client, user1, user2):
    """Test user cannot view users from different org."""
    query = """
    query GetUser($id: ID!) {
        user(id: $id) { id email }
    }
    """

    graphql_client.force_login(user1)

    # Try to access user2 from different org
    response = graphql_client.execute(
        query,
        variables={"id": str(user2.id)}
    )

    # Should return null or error
    assert response["data"]["user"] is None
```

### 2. Test Filtering and Pagination

```python
def test_users_pagination(self, graphql_client, user):
    """Test pagination works correctly."""
    query = """
    query GetUsers($first: Int!, $offset: Int!) {
        users(first: $first, offset: $offset) {
            edges {
                node { id }
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }
    """

    graphql_client.force_login(user)

    response = graphql_client.execute(
        query,
        variables={"first": 10, "offset": 0}
    )

    assert len(response["data"]["users"]["edges"]) <= 10
```

### 3. Test Errors

```python
def test_invalid_user_id(self, graphql_client, user):
    """Test error handling for invalid ID."""
    query = """
    query GetUser($id: ID!) {
        user(id: $id) { id }
    }
    """

    graphql_client.force_login(user)

    response = graphql_client.execute(
        query,
        variables={"id": "invalid"}
    )

    assert "errors" in response
```

### 4. Test Mutations

```python
def test_create_user_mutation(self, graphql_client, user):
    """Test creating new user via mutation."""
    mutation = """
    mutation CreateUser(
        $email: String!,
        $firstName: String!,
        $lastName: String!
    ) {
        createUser(email: $email, firstName: $firstName, lastName: $lastName) {
            user {
                id
                email
                firstName
            }
        }
    }
    """

    graphql_client.force_login(user)

    response = graphql_client.execute(
        mutation,
        variables={
            "email": "new@example.com",
            "firstName": "New",
            "lastName": "User"
        }
    )

    assert response["data"]["createUser"]["user"]["email"] == "new@example.com"
```

---

**Last Updated:** 08/01/2026
