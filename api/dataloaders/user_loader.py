"""DataLoader for User model.

Prevents N+1 query problems when loading users in GraphQL resolvers.
Batches user lookups within a single request.
"""

from collections.abc import Iterable
from typing import Any

from django.contrib.auth import get_user_model

from strawberry.dataloader import DataLoader

User = get_user_model()


async def load_users_batch(keys: Iterable[int]) -> list[Any]:
    """Batch load users by primary key.

    Args:
        keys: List of user IDs to load

    Returns:
        List of User instances in same order as keys (None for missing)
    """
    # Convert keys to list for indexing
    key_list = list(keys)

    # Fetch all users in a single query with related data
    users = User.objects.filter(id__in=key_list).select_related("organisation", "profile").in_bulk()

    # Return users in same order as requested keys
    return [users.get(key) for key in key_list]


# Create the DataLoader instance
UserLoader = DataLoader(load_fn=load_users_batch)
