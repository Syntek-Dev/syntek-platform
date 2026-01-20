"""DataLoader for Organisation model.

Prevents N+1 query problems when loading organisations in GraphQL resolvers.
Batches organisation lookups within a single request.

Uses synchronous batch loading compatible with Django ORM and pytest.
"""

from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async
from strawberry.dataloader import DataLoader

from apps.core.models import Organisation

if TYPE_CHECKING:
    from collections.abc import Sequence


def _load_organisations_sync(keys: list) -> list[Organisation | None]:
    """Synchronously batch load organisations by primary key.

    Args:
        keys: List of organisation IDs to load

    Returns:
        List of Organisation instances in same order as keys (None for missing)
    """
    # Fetch all organisations in a single query
    organisations = Organisation.objects.filter(id__in=keys).in_bulk()

    # Return organisations in same order as requested keys
    return [organisations.get(key) for key in keys]


async def load_organisations_batch(keys: Sequence) -> list[Organisation | None]:
    """Batch load organisations by primary key (async wrapper).

    Wraps synchronous Django ORM calls for async compatibility.

    Args:
        keys: Sequence of organisation IDs to load

    Returns:
        List of Organisation instances in same order as keys (None for missing)
    """
    key_list = list(keys)
    return await sync_to_async(_load_organisations_sync, thread_sensitive=True)(key_list)


def create_organisation_loader() -> DataLoader:
    """Create a new OrganisationLoader instance.

    DataLoaders must be created per-request to prevent cross-request caching
    and event loop issues.

    Returns:
        New DataLoader instance for organisations
    """
    return DataLoader(load_fn=load_organisations_batch)


# Export the factory function as OrganisationLoader for backwards compatibility
OrganisationLoader = create_organisation_loader
