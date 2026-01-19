"""CSRF protection middleware for GraphQL (C4 requirement).

Enforces CSRF token validation for GraphQL mutations while allowing
queries without CSRF protection.

Uses proper GraphQL parsing (graphql.parse) to detect mutations accurately,
avoiding false positives from string matching.
"""

import json
import logging
from typing import TYPE_CHECKING, Any

from django.middleware.csrf import CsrfViewMiddleware

from graphql import OperationDefinitionNode, OperationType, parse
from graphql.error import GraphQLError

if TYPE_CHECKING:
    from collections.abc import Callable

    from django.http import HttpRequest


logger = logging.getLogger(__name__)


class GraphQLCSRFMiddleware:
    """CSRF middleware for GraphQL that exempts queries.

    This middleware enforces CSRF protection on mutations but allows
    queries to proceed without CSRF tokens (C4 requirement).

    Uses proper GraphQL query parsing to accurately detect mutation operations,
    preventing bypass attempts via string manipulation.
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

        Uses proper GraphQL parsing via graphql.parse() to detect mutations.
        Handles batched queries, introspection queries, and malformed requests.

        Security considerations:
        - If query cannot be parsed, assumes mutation for safety
        - Handles batched queries (array of operations)
        - Detects mutations in any position within batch
        - Uses AST parsing to prevent string-matching bypasses

        Args:
            request: HTTP request

        Returns:
            True if request contains mutation, False otherwise
        """
        try:
            if request.content_type != "application/json":
                # Non-JSON requests treated as mutations for safety
                return True

            body = json.loads(request.body)

            # Handle batched queries (array of operations)
            if isinstance(body, list):
                return any(self._contains_mutation(item.get("query", "")) for item in body)

            # Handle single query
            query = body.get("query", "")
            return self._contains_mutation(query)

        except json.JSONDecodeError:
            # Malformed JSON treated as mutation for safety
            logger.warning("GraphQL CSRF middleware: malformed JSON in request")
            return True
        except Exception as e:
            # Any parsing error treated as mutation for safety
            logger.warning(f"GraphQL CSRF middleware: error parsing request: {e!s}")
            return True

    def _contains_mutation(self, query: str) -> bool:
        """Check if GraphQL query string contains mutation operation.

        Uses graphql.parse() to build AST and inspect operation types.
        This prevents false positives from comments or string content.

        Args:
            query: GraphQL query string

        Returns:
            True if query contains mutation operation, False otherwise
        """
        if not query or not query.strip():
            # Empty query treated as mutation for safety
            return True

        try:
            # Parse GraphQL query into AST
            document = parse(query)

            # Inspect all operation definitions
            for definition in document.definitions:
                if isinstance(definition, OperationDefinitionNode):
                    # Check if operation is a mutation
                    if definition.operation == OperationType.MUTATION:
                        return True

            # No mutation operations found
            return False

        except GraphQLError as e:
            # Invalid GraphQL syntax treated as mutation for safety
            logger.warning(f"GraphQL CSRF middleware: GraphQL parse error: {e!s}")
            return True
        except Exception as e:
            # Any other error treated as mutation for safety
            logger.warning(f"GraphQL CSRF middleware: unexpected error: {e!s}")
            return True
