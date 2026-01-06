"""Rate limiting middleware for API and authentication endpoints.

This module provides rate limiting functionality to protect against brute force
attacks and API abuse. Different rate limits apply to different types of endpoints.

Rate limits are implemented using Redis for distributed caching and are configurable
via environment variables.
"""

import hashlib
import logging
from typing import Callable, Optional

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RateLimitMiddleware(MiddlewareMixin):
    """Apply rate limiting to requests based on IP address and endpoint type.

    Rate limits (requests per minute):
    - Authentication endpoints (/admin/, /cms/, login): 5 requests/minute
    - GraphQL mutations: 30 requests/minute
    - GraphQL queries: 100 requests/minute
    - General API: 60 requests/minute
    - All other requests: 120 requests/minute

    Rate limits can be overridden via environment variables:
    - RATELIMIT_AUTH_REQUESTS_PER_MINUTE
    - RATELIMIT_GRAPHQL_MUTATION_REQUESTS_PER_MINUTE
    - RATELIMIT_GRAPHQL_QUERY_REQUESTS_PER_MINUTE
    - RATELIMIT_API_REQUESTS_PER_MINUTE
    - RATELIMIT_DEFAULT_REQUESTS_PER_MINUTE

    The middleware uses Redis cache for distributed rate limiting. Each client
    IP address is tracked separately with a sliding window approach.

    Attributes:
        get_response: The next middleware or view in the chain.
    """

    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """Check rate limits before processing the request.

        Args:
            request: The incoming HTTP request.

        Returns:
            None if the request is allowed, or a 429 Too Many Requests response
            if the rate limit has been exceeded.
        """
        # Skip rate limiting in DEBUG mode if configured
        if getattr(settings, "DEBUG", False) and not getattr(
            settings, "RATELIMIT_ENABLE_IN_DEBUG", False
        ):
            return None

        # Get client IP address
        client_ip = self._get_client_ip(request)

        # Determine rate limit based on request path
        rate_limit, period = self._get_rate_limit(request)

        # Check if rate limit is exceeded
        if self._is_rate_limited(client_ip, request.path, rate_limit, period):
            logger.warning(
                f"Rate limit exceeded for IP {client_ip} on path {request.path}",
                extra={
                    "client_ip": client_ip,
                    "path": request.path,
                    "method": request.method,
                },
            )
            return JsonResponse(
                {
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please try again in {period} seconds.",
                },
                status=429,
            )

        return None

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Extract the client IP address from the request.

        Checks X-Forwarded-For header first (for reverse proxy setups),
        then falls back to REMOTE_ADDR.

        Args:
            request: The HTTP request object.

        Returns:
            The client's IP address as a string.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            # Take the first IP in the chain (client's real IP)
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "unknown")
        return ip

    def _get_rate_limit(self, request: HttpRequest) -> tuple[int, int]:
        """Determine the appropriate rate limit for the request.

        Args:
            request: The HTTP request object.

        Returns:
            A tuple of (requests_allowed, period_in_seconds).
        """
        path = request.path
        method = request.method

        # Authentication endpoints (strictest limits)
        if any(
            path.startswith(prefix)
            for prefix in ["/admin/", "/cms/", "/accounts/login/", "/api/auth/"]
        ):
            return (
                getattr(settings, "RATELIMIT_AUTH_REQUESTS_PER_MINUTE", 5),
                60,
            )

        # GraphQL mutations (medium-strict limits)
        if path.startswith("/graphql/") and method == "POST":
            # Check if it's a mutation by inspecting the request body
            # For simplicity, apply mutation limits to all POST requests
            return (
                getattr(settings, "RATELIMIT_GRAPHQL_MUTATION_REQUESTS_PER_MINUTE", 30),
                60,
            )

        # GraphQL queries (more permissive)
        if path.startswith("/graphql/"):
            return (
                getattr(settings, "RATELIMIT_GRAPHQL_QUERY_REQUESTS_PER_MINUTE", 100),
                60,
            )

        # General API endpoints
        if path.startswith("/api/"):
            return (
                getattr(settings, "RATELIMIT_API_REQUESTS_PER_MINUTE", 60),
                60,
            )

        # Default rate limit for all other requests
        return (
            getattr(settings, "RATELIMIT_DEFAULT_REQUESTS_PER_MINUTE", 120),
            60,
        )

    def _is_rate_limited(self, client_ip: str, path: str, limit: int, period: int) -> bool:
        """Check if the client has exceeded the rate limit.

        Uses a sliding window approach with Redis cache. Each request increments
        a counter that expires after the period duration.

        Args:
            client_ip: The client's IP address.
            path: The request path (for separate rate limits per endpoint type).
            limit: Maximum number of requests allowed.
            period: Time period in seconds.

        Returns:
            True if the rate limit has been exceeded, False otherwise.
        """
        # Create a unique cache key based on IP and path prefix
        path_prefix = self._get_path_prefix(path)
        cache_key_base = f"ratelimit:{client_ip}:{path_prefix}"

        # Use a hash to keep cache keys short
        cache_key = hashlib.md5(cache_key_base.encode()).hexdigest()

        try:
            # Get current request count
            current_count = cache.get(cache_key, 0)

            if current_count >= limit:
                return True

            # Increment the counter
            cache.set(cache_key, current_count + 1, period)
            return False

        except Exception as e:
            # If cache is unavailable, log the error but don't block the request
            logger.error(f"Rate limiting cache error: {e}")
            return False

    def _get_path_prefix(self, path: str) -> str:
        """Extract a path prefix for rate limiting grouping.

        Groups similar paths together for rate limiting purposes.

        Args:
            path: The full request path.

        Returns:
            A normalized path prefix for rate limiting.
        """
        if path.startswith("/admin/"):
            return "/admin/"
        if path.startswith("/cms/"):
            return "/cms/"
        if path.startswith("/graphql/"):
            return "/graphql/"
        if path.startswith("/api/"):
            return "/api/"
        return "/"
