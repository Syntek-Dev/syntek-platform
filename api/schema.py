"""GraphQL schema definition for backend_template project.

This module defines the root Query and Mutation types for the GraphQL API
using Strawberry GraphQL with security extensions.

Phase 3 Implementation:
- Authentication mutations (register, login, logout, password reset)
- User queries with organisation boundary enforcement
- CSRF protection for mutations (C4)
- Email verification enforcement (C5)
- DataLoader integration for N+1 prevention (H2)
- Standardised error codes (H4)
- Token revocation on logout (H10)
"""

import strawberry

from api.mutations.auth import AuthMutations
from api.queries.user import UserQueries
from api.security import (
    IntrospectionControlExtension,
    QueryComplexityLimitExtension,
    QueryDepthLimitExtension,
)


@strawberry.type
class Query(UserQueries):
    """Root query type for the GraphQL API.

    Inherits from UserQueries to provide user-related queries.

    Security features:
    - Query depth limiting (max 10 levels by default)
    - Query complexity analysis (max 1000 by default)
    - Introspection disabled in production
    - Organisation boundary enforcement on all user queries
    """

    @strawberry.field
    def hello(self) -> str:
        """Simple hello world query for testing.

        Returns:
            A greeting message.
        """
        return "Hello from Backend Template GraphQL API!"


@strawberry.type
class Mutation(AuthMutations):
    """Root mutation type for the GraphQL API.

    Inherits from AuthMutations to provide authentication operations.

    Security features:
    - Rate limiting (30 mutations per minute by default)
    - Query complexity analysis
    - CSRF protection (C4 requirement)
    - Email verification enforcement (C5 requirement)
    - Token revocation on logout (H10 requirement)
    """

    pass


# Create schema with security extensions
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        QueryDepthLimitExtension,
        QueryComplexityLimitExtension,
        IntrospectionControlExtension,
    ],
)
