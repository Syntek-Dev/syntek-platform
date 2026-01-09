"""DataLoaders for efficient batch loading of database objects.

This package provides DataLoader implementations to prevent N+1 query problems
in GraphQL resolvers. DataLoaders batch and cache database queries within
a single request context.

Security Requirement H2: N+1 Query Prevention
All relationship fields in GraphQL resolvers must use DataLoaders to batch
database queries and prevent performance issues.

Example:
    >>> loader = UserLoader(context)
    >>> user = await loader.load(user_id)
    >>> users = await loader.load_many([id1, id2, id3])
"""

from api.dataloaders.audit_log_loader import AuditLogLoader
from api.dataloaders.organisation_loader import OrganisationLoader
from api.dataloaders.user_loader import UserLoader

__all__ = [
    "UserLoader",
    "OrganisationLoader",
    "AuditLogLoader",
]
