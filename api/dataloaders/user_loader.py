"""DataLoader for User model.

Prevents N+1 query problems when loading users in GraphQL resolvers.
Batches user lookups within a single request.

Uses synchronous batch loading compatible with Django ORM and pytest.
"""

from typing import TYPE_CHECKING, Any

from django.contrib.auth import get_user_model

from asgiref.sync import sync_to_async
from strawberry.dataloader import DataLoader

if TYPE_CHECKING:
    from collections.abc import Sequence

User = get_user_model()


def _load_users_sync(keys: list) -> list[Any]:
    """Synchronously batch load users by primary key.

    Args:
        keys: List of user IDs to load

    Returns:
        List of User instances in same order as keys (None for missing)
    """
    # Fetch all users in a single query with related data
    users = User.objects.filter(id__in=keys).select_related("organisation").in_bulk()

    # Return users in same order as requested keys
    return [users.get(key) for key in keys]


async def load_users_batch(keys: Sequence) -> list[Any]:
    """Batch load users by primary key (async wrapper).

    Wraps synchronous Django ORM calls for async compatibility.

    Args:
        keys: Sequence of user IDs to load

    Returns:
        List of User instances in same order as keys (None for missing)
    """
    key_list = list(keys)
    return await sync_to_async(_load_users_sync, thread_sensitive=True)(key_list)


def create_user_loader() -> DataLoader:
    """Create a new UserLoader instance.

    DataLoaders must be created per-request to prevent cross-request caching
    and event loop issues.

    Returns:
        New DataLoader instance for users
    """
    return DataLoader(load_fn=load_users_batch)


# Export the factory function as UserLoader for backwards compatibility
UserLoader = create_user_loader
