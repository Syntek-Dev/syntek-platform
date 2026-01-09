"""DataLoader for AuditLog model.

Prevents N+1 query problems when loading audit logs in GraphQL resolvers.
Batches audit log lookups within a single request.
"""

from collections.abc import Iterable

from strawberry.dataloader import DataLoader

from apps.core.models import AuditLog


async def load_audit_logs_batch(keys: Iterable[int]) -> list[AuditLog | None]:
    """Batch load audit logs by primary key.

    Args:
        keys: List of audit log IDs to load

    Returns:
        List of AuditLog instances in same order as keys (None for missing)
    """
    # Convert keys to list for indexing
    key_list = list(keys)

    # Fetch all audit logs in a single query with related data
    logs = AuditLog.objects.filter(id__in=key_list).select_related("user", "organisation").in_bulk()

    # Return logs in same order as requested keys
    return [logs.get(key) for key in key_list]


# Create the DataLoader instance
AuditLogLoader = DataLoader(load_fn=load_audit_logs_batch)
