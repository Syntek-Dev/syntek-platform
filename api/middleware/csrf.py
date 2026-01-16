"""CSRF protection middleware for GraphQL (C4 requirement).

Enforces CSRF token validation for GraphQL mutations while allowing
queries without CSRF protection.

Implementation stub for TDD.
"""

import json
from typing import TYPE_CHECKING, Any

from django.middleware.csrf import CsrfViewMiddleware

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.http import HttpRequest


class GraphQLCSRFMiddleware:
    """CSRF middleware for GraphQL that exempts queries.

    This middleware enforces CSRF protection on mutations but allows
    queries to proceed without CSRF tokens (C4 requirement).
    """

    def __init__(self, get_response: Callable) -> None:
        """Initialize middleware.

        Args:
            get_response: Next middleware/view in chain
        """
        self.get_response = get_response
        self.csrf_middleware = CsrfViewMiddleware(get_response)

    def __call__(self, request: HttpRequest) -> Any:
        """Process request through CSRF middleware.

        Validates CSRF token for mutations, allows queries without validation.

        Args:
            request: HTTP request

        Returns:
            HTTP response
        """
        # Check if request is to GraphQL endpoint
        if not request.path.startswith("/graphql"):
            return self.get_response(request)

        # Check if request contains mutations
        if self._is_mutation(request):
            # Enforce CSRF protection for mutations
            return self.csrf_middleware(request)

        # Allow queries without CSRF token
        return self.get_response(request)

    def _is_mutation(self, request: HttpRequest) -> bool:
        """Check if GraphQL request contains mutations.

        Args:
            request: HTTP request

        Returns:
            True if request contains mutation, False otherwise
        """
        try:
            if request.content_type == "application/json":
                body = json.loads(request.body)
                query = body.get("query", "")
                return "mutation" in query.lower()
        except (json.JSONDecodeError, AttributeError):
            pass
        return False
