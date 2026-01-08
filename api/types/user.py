"""GraphQL types for User model.

This module defines Strawberry GraphQL types for User-related data.
Implementation stub for TDD - tests will fail until fully implemented.
"""

from datetime import datetime

import strawberry


@strawberry.type
class UserType:
    """GraphQL type representing a User.

    Maps to apps.core.models.User model.
    """

    id: strawberry.ID
    email: str
    first_name: str
    last_name: str
    email_verified: bool
    two_factor_enabled: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Relationships (will use DataLoaders)
    # organisation: "OrganisationType"
    # profile: Optional["UserProfileType"]


@strawberry.type
class UserProfileType:
    """GraphQL type representing a UserProfile.

    Maps to apps.core.models.UserProfile model.
    """

    id: strawberry.ID
    phone: str | None
    avatar: str | None
    timezone: str
    language: str
    bio: str | None


@strawberry.type
class OrganisationType:
    """GraphQL type representing an Organisation.

    Maps to apps.core.models.Organisation model.
    """

    id: strawberry.ID
    name: str
    slug: str
    industry: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


@strawberry.type
class AuditLogType:
    """GraphQL type representing an AuditLog entry.

    Maps to apps.core.models.AuditLog model.
    IP address is decrypted for display.
    """

    id: strawberry.ID
    action: str
    ip_address: str | None  # Decrypted
    user_agent: str | None
    created_at: datetime

    # Relationships
    # user: Optional[UserType]
    # organisation: Optional[OrganisationType]
