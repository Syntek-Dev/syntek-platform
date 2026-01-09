"""DataLoader for Organisation model.

Prevents N+1 query problems when loading organisations in GraphQL resolvers.
Batches organisation lookups within a single request.
"""

from collections.abc import Iterable

from strawberry.dataloader import DataLoader

from apps.core.models import Organisation


async def load_organisations_batch(keys: Iterable[int]) -> list[Organisation | None]:
    """Batch load organisations by primary key.

    Args:
        keys: List of organisation IDs to load

    Returns:
        List of Organisation instances in same order as keys (None for missing)
    """
    # Convert keys to list for indexing
    key_list = list(keys)

    # Fetch all organisations in a single query
    organisations = Organisation.objects.filter(id__in=key_list).in_bulk()

    # Return organisations in same order as requested keys
    return [organisations.get(key) for key in key_list]


# Create the DataLoader instance
OrganisationLoader = DataLoader(load_fn=load_organisations_batch)
