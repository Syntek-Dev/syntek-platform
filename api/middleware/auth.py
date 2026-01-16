"""Authentication middleware for GraphQL API.

Extracts JWT tokens from Authorization header and authenticates users
for GraphQL requests. Uses TokenService for token verification.
"""

from typing import TYPE_CHECKING, Any

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from apps.core.services.token_service import TokenService

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.http import HttpRequest

User = get_user_model()


class GraphQLAuthenticationMiddleware:
    """JWT authentication middleware for GraphQL.

    Extracts Bearer token from Authorization header and authenticates
    the user using TokenService. Sets request.user to authenticated
    user or AnonymousUser.

    Example Authorization header:
        Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...
    """

    def __init__(self, get_response: Callable) -> None:
        """Initialize middleware.

        Args:
            get_response: Next middleware/view in chain
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> Any:
        """Process request to authenticate user.

        Extracts JWT token from Authorization header, verifies it,
        and sets request.user to the authenticated user.

        Args:
            request: HTTP request

        Returns:
            HTTP response from next middleware/view
        """
        # Only process GraphQL requests
        if not request.path.startswith("/graphql"):
            return self.get_response(request)

        # Extract token from Authorization header
        auth_header = request.headers.get("authorization", "")

        if auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix

            # Verify token and get user
            user = TokenService.verify_access_token(token)

            if user:
                request.user = user  # type: ignore[assignment]
            else:
                request.user = AnonymousUser()
        else:
            # No token provided, user is anonymous
            request.user = AnonymousUser()

        return self.get_response(request)
