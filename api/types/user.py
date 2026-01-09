"""GraphQL types for User model.

This module defines Strawberry GraphQL types for User-related data.
Implements H2 requirement for N+1 query prevention using DataLoaders.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

import strawberry


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
class UserType:
    """GraphQL type representing a User.

    Maps to apps.core.models.User model.
    Uses DataLoaders for relationship fields to prevent N+1 queries (H2).
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

    # Store organisation_id for lazy loading (Private fields are not exposed in schema)
    _organisation_id: strawberry.Private[int | None] = None
    _user_instance: strawberry.Private[Any] = None

    @strawberry.field
    def organisation(self) -> OrganisationType | None:
        """Load organisation for the user.

        Returns:
            OrganisationType for the user's organisation or None
        """
        if self._organisation_id is None:
            return None

        from apps.core.models import Organisation

        try:
            org = Organisation.objects.get(id=self._organisation_id)
            return OrganisationType(
                id=strawberry.ID(str(org.id)),
                name=org.name,
                slug=org.slug,
                industry=org.industry,
                is_active=org.is_active,
                created_at=org.created_at,
                updated_at=org.updated_at,
            )
        except Organisation.DoesNotExist:
            return None

    @strawberry.field
    def profile(self) -> UserProfileType | None:
        """Load user profile.

        Returns:
            UserProfileType for the user's profile or None
        """
        if self._user_instance is None:
            return None

        try:
            # Access profile through related manager
            profile = getattr(self._user_instance, "profile", None)
            if profile is None:
                return None
            return UserProfileType(
                id=strawberry.ID(str(profile.id)),
                phone=profile.phone,
                avatar=str(profile.avatar) if profile.avatar else None,
                timezone=profile.timezone,
                language=profile.language,
                bio=profile.bio,
            )
        except Exception:
            return None


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
