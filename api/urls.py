"""URL configuration for GraphQL API.

This module defines the URL patterns for the GraphQL endpoint
with DataLoader context for N+1 query prevention.
"""

from typing import TYPE_CHECKING, Any

from django.urls import path

from strawberry.django.views import GraphQLView

from api.dataloaders.audit_log_loader import AuditLogLoader
from api.dataloaders.organisation_loader import OrganisationLoader
from api.dataloaders.user_loader import UserLoader

from .schema import schema

if TYPE_CHECKING:
    from django.http import HttpRequest


def get_graphql_context(request: HttpRequest) -> dict[str, Any]:
    """Create GraphQL context with DataLoaders.

    Instantiates DataLoaders per-request to prevent cross-request caching.
    DataLoaders batch database queries within a single request.

    Args:
        request: Django HTTP request

    Returns:
        Context dictionary with request and DataLoader instances
    """
    return {
        "request": request,
        "organisation_loader": OrganisationLoader(),
        "user_loader": UserLoader(),
        "audit_log_loader": AuditLogLoader(),
    }


class CustomGraphQLView(GraphQLView):
    """Custom GraphQL view with DataLoader context.

    Provides DataLoaders for N+1 query prevention through custom context.
    """

    def get_context(self, request: HttpRequest, response: Any = None) -> dict[str, Any]:
        """Override get_context to provide DataLoaders.

        Args:
            request: Django HTTP request
            response: HTTP response (unused)

        Returns:
            Context dictionary with request and DataLoader instances
        """
        return get_graphql_context(request)


urlpatterns = [
    path(
        "",
        CustomGraphQLView.as_view(schema=schema, graphql_ide="graphiql"),
        name="graphql",
    ),
]
