"""GraphQL schema definition for backend_template project.

This module defines the root Query and Mutation types for the GraphQL API
using Strawberry GraphQL with security extensions.
"""

import strawberry

from api.security import (
    IntrospectionControlExtension,
    QueryComplexityLimitExtension,
    QueryDepthLimitExtension,
)


@strawberry.type
class Query:
    """Root query type for the GraphQL API.

    Provides access to all publicly available data through GraphQL queries.
    Security features:
    - Query depth limiting (max 10 levels by default)
    - Query complexity analysis (max 1000 by default)
    - Introspection disabled in production
    """

    @strawberry.field
    def hello(self) -> str:
        """Simple hello world query for testing.

        Returns:
            A greeting message.
        """
        return "Hello from Backend Template GraphQL API!"


@strawberry.type
class Mutation:
    """Root mutation type for the GraphQL API.

    Provides access to all data modification operations.
    Security features:
    - Rate limiting (30 mutations per minute by default)
    - Query complexity analysis
    """

    @strawberry.field
    def placeholder(self) -> str:
        """Placeholder mutation.

        Returns:
            A placeholder message.
        """
        return "Mutations will be added here"


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
