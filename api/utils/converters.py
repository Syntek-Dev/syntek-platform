"""Type conversion utilities for GraphQL API.

This module provides functions to convert Django models to GraphQL types.
Consolidates conversion logic to maintain DRY principle (addresses DRY-2).
"""

from typing import Any

import strawberry

from api.types.user import UserType


def user_to_graphql_type(user: Any) -> UserType:
    """Convert Django User instance to GraphQL UserType.

    This is the canonical conversion function used by both mutations and queries.
    Includes private fields (_organisation_id, _user_instance) for DataLoader support.

    Args:
        user: Django User instance

    Returns:
        UserType for GraphQL response with all fields populated
    """
    return UserType(
        id=strawberry.ID(str(user.id)),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        email_verified=user.email_verified,
        two_factor_enabled=user.two_factor_enabled,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        _organisation_id=user.organisation_id,
        _user_instance=user,
    )
