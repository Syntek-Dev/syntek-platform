"""Security middleware for additional HTTP security headers.

This module provides middleware to add security-related HTTP headers that are
not provided by Django's built-in SecurityMiddleware. These headers help protect
against various web vulnerabilities and comply with modern security best practices.
"""

from typing import Callable

from django.http import HttpRequest, HttpResponse


class SecurityHeadersMiddleware:
    """Add additional security headers to all HTTP responses.

    This middleware adds the following security headers:
    - X-Content-Type-Options: Prevents MIME type sniffing
    - Referrer-Policy: Controls referrer information sent with requests
    - Permissions-Policy: Controls browser features and APIs

    Django's SecurityMiddleware already handles:
    - X-Frame-Options
    - Strict-Transport-Security (HSTS)
    - X-XSS-Protection (deprecated but still set)
    - Content-Security-Policy (via django-csp)

    Attributes:
        get_response: The next middleware or view in the chain.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize the middleware.

        Args:
            get_response: The next middleware or view function in the request/response chain.
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request and add security headers to the response.

        Args:
            request: The incoming HTTP request.

        Returns:
            The HTTP response with additional security headers.
        """
        response = self.get_response(request)

        # Prevent MIME type sniffing
        response["X-Content-Type-Options"] = "nosniff"

        # Control referrer information (strict-origin-when-cross-origin is recommended)
        # Sends full URL for same-origin, only origin for cross-origin HTTPS, nothing for HTTP
        response["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy (formerly Feature Policy)
        # Disable potentially dangerous browser features by default
        permissions_policy_directives = [
            "geolocation=()",  # Disable geolocation API
            "microphone=()",  # Disable microphone access
            "camera=()",  # Disable camera access
            "payment=()",  # Disable payment request API
            "usb=()",  # Disable USB access
            "magnetometer=()",  # Disable magnetometer
            "gyroscope=()",  # Disable gyroscope
            "accelerometer=()",  # Disable accelerometer
        ]
        response["Permissions-Policy"] = ", ".join(permissions_policy_directives)

        return response
