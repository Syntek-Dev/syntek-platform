"""URL configuration for GraphQL API.

This module defines the URL patterns for the GraphQL endpoint.
"""

from django.urls import path
from strawberry.django.views import GraphQLView

from .schema import schema

urlpatterns = [
    path("", GraphQLView.as_view(schema=schema), name="graphql"),
]
