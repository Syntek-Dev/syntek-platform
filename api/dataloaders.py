"""GraphQL DataLoaders for batching and caching database queries.

DataLoaders prevent N+1 query problems by batching multiple lookups into
single database queries. This is critical for GraphQL performance when
resolving nested relationships.

Usage:
    from api.dataloaders import get_dataloaders

    # In a resolver
    def resolve_organisation(self, info):
        loaders = get_dataloaders(info.context)
        return await loaders.organisation.load(self.organisation_id)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model

from strawberry.dataloader import DataLoader

if TYPE_CHECKING:
    from uuid import UUID

    from apps.core.models import Organisation

User = get_user_model()


async def load_organisations(keys: list[UUID]) -> list[Organisation | None]:
    """Batch load organisations by ID.

    Fetches multiple organisations in a single database query to prevent
    N+1 query problems when accessing user.organisation across multiple users.

    Args:
        keys: List of organisation UUIDs to load

    Returns:
        List of Organisation instances in the same order as keys,
        with None for IDs that don't exist
    """
    from apps.core.models import Organisation

    # Fetch all organisations in a single query
    organisations = Organisation.objects.filter(id__in=keys)

    # Create a lookup map by ID
    org_map = {org.id: org for org in organisations}

    # Return results in the same order as keys (None if not found)
    return [org_map.get(key) for key in keys]


async def load_users(keys: list[UUID]) -> list[User | None]:
    """Batch load users by ID.

    Fetches multiple users in a single database query to prevent
    N+1 query problems when accessing relationships like audit_log.user.

    Args:
        keys: List of user UUIDs to load

    Returns:
        List of User instances in the same order as keys,
        with None for IDs that don't exist
    """
    # Fetch all users in a single query with their organisations
    users = User.objects.filter(id__in=keys).select_related("organisation")

    # Create a lookup map by ID
    user_map = {user.id: user for user in users}

    # Return results in the same order as keys (None if not found)
    return [user_map.get(key) for key in keys]


async def load_user_profiles(keys: list[UUID]) -> list:
    """Batch load user profiles by user ID.

    Fetches multiple user profiles in a single database query.

    Args:
        keys: List of user UUIDs

    Returns:
        List of UserProfile instances in the same order as keys,
        with None for users without profiles
    """
    from apps.core.models import UserProfile

    # Fetch all profiles in a single query
    profiles = UserProfile.objects.filter(user_id__in=keys).select_related("user")

    # Create a lookup map by user_id
    profile_map = {profile.user_id: profile for profile in profiles}

    # Return results in the same order as keys (None if not found)
    return [profile_map.get(key) for key in keys]


class DataLoaders:
    """Container for all DataLoader instances.

    Each DataLoader batches and caches database queries for a specific model.
    Create one instance per GraphQL request to ensure proper caching scope.
    """

    def __init__(self) -> None:
        """Initialize all DataLoader instances."""
        self.organisation = DataLoader(load_fn=load_organisations)
        self.user = DataLoader(load_fn=load_users)
        self.user_profile = DataLoader(load_fn=load_user_profiles)


def get_dataloaders(context) -> DataLoaders:
    """Get or create DataLoaders for the current request.

    DataLoaders are stored in the request context to ensure they're scoped
    to a single GraphQL request (important for caching consistency).

    Args:
        context: GraphQL context (usually info.context)

    Returns:
        DataLoaders instance for the current request
    """
    # Check if DataLoaders already exist in context
    if not hasattr(context, "dataloaders"):
        context.dataloaders = DataLoaders()

    return context.dataloaders
