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

Phase 5 Implementation:
- TOTP-based two-factor authentication (2FA)
- Multiple TOTP devices per user (H13)
- Backup codes with hashing (H14) and improved format (M3)
- TOTP secret encryption (C2)
- Time window tolerance (M6)

Phase 8 Implementation (GDPR):
- Data export (Article 15 - Right of Access)
- Account deletion (Article 17 - Right to Erasure)
- Processing restriction (Article 18)
- Consent management

Phase 8b Implementation (Legal Documents):
- Terms & Conditions version management
- Privacy Policy version management
- Cookie Policy management
- DPA (Data Processing Agreement) management
- Legal acceptance tracking
"""

import strawberry

from api.mutations.auth import AuthMutations
from api.mutations.gdpr import GDPRMutations
from api.mutations.legal import LegalMutations
from api.mutations.session import SessionMutation
from api.mutations.totp import TOTPMutations, TOTPQueries
from api.queries.audit import AuditQuery
from api.queries.gdpr import GDPRQuery
from api.queries.legal import LegalQuery
from api.queries.user import UserQueries
from api.security import (
    IntrospectionControlExtension,
    QueryComplexityLimitExtension,
    QueryDepthLimitExtension,
)


@strawberry.type
class Query(UserQueries, TOTPQueries, AuditQuery, GDPRQuery, LegalQuery):
    """Root query type for the GraphQL API.

    Inherits from:
    - UserQueries: user-related queries
    - TOTPQueries: 2FA status and device queries (H13)
    - AuditQuery: audit log queries with organisation boundaries (Phase 7)
    - GDPRQuery: GDPR compliance queries (Phase 8)
    - LegalQuery: legal document queries (Phase 8b)

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
class Mutation(AuthMutations, TOTPMutations, SessionMutation, GDPRMutations, LegalMutations):
    """Root mutation type for the GraphQL API.

    Inherits from:
    - AuthMutations: authentication operations
    - TOTPMutations: 2FA setup, verification, and management (Phase 5)
    - SessionMutation: session management operations (Phase 7)
    - GDPRMutations: GDPR compliance operations (Phase 8)
    - LegalMutations: legal document acceptance operations (Phase 8b)

    Security features:
    - Rate limiting (30 mutations per minute by default)
    - Query complexity analysis
    - CSRF protection (C4 requirement)
    - Email verification enforcement (C5 requirement)
    - Token revocation on logout (H10 requirement)
    - TOTP secret encryption (C2 requirement)
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
