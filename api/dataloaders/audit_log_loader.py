"""DataLoader for AuditLog model.

Prevents N+1 query problems when loading audit logs in GraphQL resolvers.
Batches audit log lookups within a single request.

Uses synchronous batch loading compatible with Django ORM and pytest.
"""

from typing import TYPE_CHECKING

from asgiref.sync import sync_to_async
from strawberry.dataloader import DataLoader

from apps.core.models import AuditLog

if TYPE_CHECKING:
    from collections.abc import Sequence


def _load_audit_logs_sync(keys: list) -> list[AuditLog | None]:
    """Synchronously batch load audit logs by primary key.

    Args:
        keys: List of audit log IDs to load

    Returns:
        List of AuditLog instances in same order as keys (None for missing)
    """
    # Fetch all audit logs in a single query with related data
    logs = AuditLog.objects.filter(id__in=keys).select_related("user", "organisation").in_bulk()

    # Return logs in same order as requested keys
    return [logs.get(key) for key in keys]


async def load_audit_logs_batch(keys: Sequence) -> list[AuditLog | None]:
    """Batch load audit logs by primary key (async wrapper).

    Wraps synchronous Django ORM calls for async compatibility.

    Args:
        keys: Sequence of audit log IDs to load

    Returns:
        List of AuditLog instances in same order as keys (None for missing)
    """
    key_list = list(keys)
    return await sync_to_async(_load_audit_logs_sync, thread_sensitive=True)(key_list)


def create_audit_log_loader() -> DataLoader:
    """Create a new AuditLogLoader instance.

    DataLoaders must be created per-request to prevent cross-request caching
    and event loop issues.

    Returns:
        New DataLoader instance for audit logs
    """
    return DataLoader(load_fn=load_audit_logs_batch)


# Export the factory function as AuditLogLoader for backwards compatibility
AuditLogLoader = create_audit_log_loader
