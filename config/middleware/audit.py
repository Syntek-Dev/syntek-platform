"""Security audit logging middleware.

This module provides middleware to log security-relevant events such as:
- Successful and failed authentication attempts
- Authorization failures (403 errors)
- Suspicious request patterns
- CSRF validation failures

Audit logs are written to a separate logger channel for security analysis
and compliance requirements.
"""

import logging
from typing import Callable, Optional

from django.conf import settings
from django.contrib.auth.signals import (
    user_logged_in,
    user_logged_out,
    user_login_failed,
)
from django.core.exceptions import PermissionDenied
from django.dispatch import receiver
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

# Security audit logger (configured separately from application logs)
security_logger = logging.getLogger("security.audit")


class SecurityAuditMiddleware(MiddlewareMixin):
    """Log security-relevant events for audit and compliance purposes.

    This middleware logs the following events:
    - HTTP 403 (Forbidden) responses
    - HTTP 401 (Unauthorized) responses
    - CSRF validation failures
    - Authentication attempts (via Django signals)

    All logs include:
    - Timestamp (automatic via logger)
    - Client IP address
    - Request path
    - HTTP method
    - User agent
    - User (if authenticated)

    Security logs should be sent to a separate logging handler for:
    - Long-term retention
    - Security monitoring and alerting
    - Compliance audit trails
    """

    def process_response(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        """Log security events based on response status codes.

        Args:
            request: The HTTP request object.
            response: The HTTP response object.

        Returns:
            The unmodified HTTP response.
        """
        # Log authorization failures
        if response.status_code == 403:
            self._log_authorization_failure(request, response)

        # Log authentication failures
        if response.status_code == 401:
            self._log_authentication_required(request, response)

        return response

    def process_exception(
        self, request: HttpRequest, exception: Exception
    ) -> Optional[HttpResponse]:
        """Log security exceptions.

        Args:
            request: The HTTP request object.
            exception: The exception that was raised.

        Returns:
            None (allows normal exception handling to continue).
        """
        if isinstance(exception, PermissionDenied):
            self._log_authorization_failure(request, None)

        return None

    def _log_authorization_failure(
        self, request: HttpRequest, response: Optional[HttpResponse]
    ) -> None:
        """Log when a user is denied access to a resource.

        Args:
            request: The HTTP request object.
            response: The HTTP response object (may be None for exceptions).
        """
        security_logger.warning(
            "Authorization failure",
            extra={
                "event_type": "authorization_failure",
                "client_ip": self._get_client_ip(request),
                "path": request.path,
                "method": request.method,
                "user": str(request.user) if request.user.is_authenticated else "anonymous",
                "user_id": request.user.id if request.user.is_authenticated else None,
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                "referer": request.META.get("HTTP_REFERER", ""),
            },
        )

    def _log_authentication_required(
        self, request: HttpRequest, response: HttpResponse
    ) -> None:
        """Log when authentication is required but not provided.

        Args:
            request: The HTTP request object.
            response: The HTTP response object.
        """
        security_logger.info(
            "Authentication required",
            extra={
                "event_type": "authentication_required",
                "client_ip": self._get_client_ip(request),
                "path": request.path,
                "method": request.method,
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            },
        )

    def _get_client_ip(self, request: HttpRequest) -> str:
        """Extract the client IP address from the request.

        Args:
            request: The HTTP request object.

        Returns:
            The client's IP address.
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "unknown")
        return ip


# Signal handlers for authentication events


@receiver(user_logged_in)
def log_user_login(sender, request: HttpRequest, user, **kwargs) -> None:
    """Log successful user login events.

    Args:
        sender: The sender of the signal.
        request: The HTTP request object.
        user: The user who logged in.
        **kwargs: Additional keyword arguments from the signal.
    """
    client_ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
    if not client_ip:
        client_ip = request.META.get("REMOTE_ADDR", "unknown")

    security_logger.info(
        f"User login successful: {user.username}",
        extra={
            "event_type": "login_success",
            "user": str(user),
            "user_id": user.id,
            "username": user.username,
            "client_ip": client_ip,
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        },
    )


@receiver(user_logged_out)
def log_user_logout(sender, request: HttpRequest, user, **kwargs) -> None:
    """Log user logout events.

    Args:
        sender: The sender of the signal.
        request: The HTTP request object.
        user: The user who logged out.
        **kwargs: Additional keyword arguments from the signal.
    """
    if user is None:
        return

    client_ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
    if not client_ip:
        client_ip = request.META.get("REMOTE_ADDR", "unknown")

    security_logger.info(
        f"User logout: {user.username}",
        extra={
            "event_type": "logout",
            "user": str(user),
            "user_id": user.id,
            "username": user.username,
            "client_ip": client_ip,
        },
    )


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request: HttpRequest = None, **kwargs) -> None:
    """Log failed login attempts.

    Args:
        sender: The sender of the signal.
        credentials: The credentials that were attempted.
        request: The HTTP request object (may be None).
        **kwargs: Additional keyword arguments from the signal.
    """
    if request is None:
        return

    client_ip = request.META.get("HTTP_X_FORWARDED_FOR", "").split(",")[0].strip()
    if not client_ip:
        client_ip = request.META.get("REMOTE_ADDR", "unknown")

    username = credentials.get("username", "unknown")

    security_logger.warning(
        f"Failed login attempt for username: {username}",
        extra={
            "event_type": "login_failure",
            "username": username,
            "client_ip": client_ip,
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        },
    )
