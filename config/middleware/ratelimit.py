"""Rate limiting middleware for API and authentication endpoints.

This module provides rate limiting functionality to protect against brute force
attacks and API abuse. Different rate limits apply to different types of endpoints.

Rate limits are implemented using Redis for distributed caching and are configurable
via environment variables.
"""

import hashlib
import logging

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.utils.deprecation import MiddlewareMixin

from config.utils.request import get_client_ip

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

    def process_request(self, request: HttpRequest) -> HttpResponse | None:
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

        # Get client IP address (using centralised utility)
        client_ip = get_client_ip(request)

        # Determine rate limit based on request path
        rate_limit, period = self._get_rate_limit(request)

        # Get current request count and calculate headers
        current_count, reset_time = self._get_request_count(client_ip, request.path, period)

        # Store rate limit info in request for process_response
        request._ratelimit_info = {  # type: ignore[attr-defined]
            "limit": rate_limit,
            "remaining": max(0, rate_limit - current_count - 1),
            "reset": reset_time,
        }

        # Check if rate limit is exceeded
        if current_count >= rate_limit:
            logger.warning(
                f"Rate limit exceeded for IP {client_ip} on path {request.path}",
                extra={
                    "client_ip": client_ip,
                    "path": request.path,
                    "method": request.method,
                },
            )
            response = JsonResponse(
                {
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please try again in {period} seconds.",
                },
                status=429,
            )
            # Add rate limit headers to error response
            response["X-RateLimit-Limit"] = str(rate_limit)
            response["X-RateLimit-Remaining"] = "0"
            response["X-RateLimit-Reset"] = str(reset_time)
            response["Retry-After"] = str(period)
            return response

        return None

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Add rate limit headers to successful responses.

        Args:
            request: The HTTP request object.
            response: The HTTP response object.

        Returns:
            The response with added rate limit headers.
        """
        # Add rate limit headers if available
        if hasattr(request, "_ratelimit_info"):
            info = request._ratelimit_info  # type: ignore[attr-defined]
            response["X-RateLimit-Limit"] = str(info["limit"])
            response["X-RateLimit-Remaining"] = str(info["remaining"])
            response["X-RateLimit-Reset"] = str(info["reset"])

        return response

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

    def _get_request_count(self, client_ip: str, path: str, period: int) -> tuple[int, int]:
        """Get current request count and calculate reset time.

        Uses a sliding window approach with Redis cache. Each request increments
        a counter that expires after the period duration.

        Args:
            client_ip: The client's IP address.
            path: The request path (for separate rate limits per endpoint type).
            period: Time period in seconds.

        Returns:
            Tuple of (current_count, reset_timestamp).
        """
        import time

        # Create a unique cache key based on IP and path prefix
        path_prefix = self._get_path_prefix(path)
        cache_key_base = f"ratelimit:{client_ip}:{path_prefix}"

        # Use a hash to keep cache keys short
        cache_key = hashlib.md5(cache_key_base.encode()).hexdigest()
        reset_key = f"{cache_key}:reset"

        try:
            # Get current request count
            current_count = cache.get(cache_key, 0)

            # Get or set reset time
            reset_time = cache.get(reset_key)
            if reset_time is None:
                reset_time = int(time.time()) + period
                cache.set(reset_key, reset_time, period)

            # Increment the counter
            cache.set(cache_key, current_count + 1, period)

            return current_count, reset_time

        except (ConnectionError, TimeoutError, OSError) as e:
            # If cache is unavailable, log the error but don't block the request
            # Fail open - allow requests through if cache is down
            logger.error(f"Rate limiting cache error: {e}")
            return 0, int(time.time()) + period

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
