"""GraphQL context utilities.

This module provides helper functions for accessing request data from
GraphQL Info context in a consistent way.
"""

from typing import TYPE_CHECKING

from strawberry.types import Info

if TYPE_CHECKING:
    from django.http import HttpRequest


def get_request(info: Info) -> "HttpRequest":
    """Extract Django request from GraphQL Info context.

    Handles both dict-based context (from CustomGraphQLView) and
    object-based context for compatibility.

    Args:
        info: Strawberry GraphQL Info object

    Returns:
        Django HttpRequest object

    Raises:
        AttributeError: If request not found in context

    Example:
        >>> request = get_request(info)
        >>> ip_address = request.META.get("REMOTE_ADDR", "")
    """
    if isinstance(info.context, dict):
        return info.context["request"]
    return info.context.request


def get_ip_address(info: Info) -> str:
    """Get client IP address from GraphQL Info context.

    Args:
        info: Strawberry GraphQL Info object

    Returns:
        Client IP address or empty string if not available

    Example:
        >>> ip = get_ip_address(info)
        '192.168.1.1'
    """
    request = get_request(info)
    return request.META.get("REMOTE_ADDR", "")


def get_user_agent(info: Info) -> str:
    """Get user agent string from GraphQL Info context.

    Args:
        info: Strawberry GraphQL Info object

    Returns:
        User agent string or empty string if not available

    Example:
        >>> user_agent = get_user_agent(info)
        'Mozilla/5.0...'
    """
    request = get_request(info)
    return request.META.get("HTTP_USER_AGENT", "")


def get_authorization_header(info: Info) -> str:
    """Get Authorization header from GraphQL Info context.

    Args:
        info: Strawberry GraphQL Info object

    Returns:
        Authorization header value or empty string if not available

    Example:
        >>> auth = get_authorization_header(info)
        'Bearer eyJ0eXAi...'
    """
    request = get_request(info)
    return request.META.get("HTTP_AUTHORIZATION", "")


def get_bearer_token(info: Info) -> str:
    """Extract Bearer token from Authorization header.

    Args:
        info: Strawberry GraphQL Info object

    Returns:
        Bearer token value (without "Bearer " prefix) or empty string

    Example:
        >>> token = get_bearer_token(info)
        'eyJ0eXAi...'
    """
    auth_header = get_authorization_header(info)
    if auth_header.startswith("Bearer "):
        return auth_header[7:]  # Remove "Bearer " prefix
    return ""
