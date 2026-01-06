"""Security audit logging middleware.

This module provides middleware to log security-relevant events such as:
- Successful and failed authentication attempts
- Authorization failures (403 errors)
- Suspicious request patterns
- CSRF validation failures

Audit logs are written to a separate logger channel for security analysis
and compliance requirements.

GDPR Compliance:
- Security audit logs retain full IP addresses (legitimate interest for security)
- Non-security logs should use anonymised IPs via anonymise_ip()
- Recommended retention: 90 days for security logs, 30 days for general logs
"""

import ipaddress
import logging

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


def anonymise_ip(ip_address: str) -> str:
    """Anonymise an IP address for GDPR-compliant non-security logging.

    For IPv4: Zeros the last octet (e.g., 192.168.1.45 -> 192.168.1.0)
    For IPv6: Zeros the last 80 bits (keeps /48 prefix)

    This follows Google Analytics' IP anonymisation approach and is
    accepted as GDPR-compliant by most EU DPAs.

    Args:
        ip_address: The IP address to anonymise.

    Returns:
        The anonymised IP address, or 'unknown' if parsing fails.

    Example:
        >>> anonymise_ip('192.168.1.45')
        '192.168.1.0'
        >>> anonymise_ip('2001:db8:85a3::8a2e:370:7334')
        '2001:db8:85a3::'
    """
    if not ip_address or ip_address == "unknown":
        return "unknown"

    try:
        ip = ipaddress.ip_address(ip_address)
        if isinstance(ip, ipaddress.IPv4Address):
            # Zero the last octet for IPv4
            ipv4_network = ipaddress.IPv4Network(f"{ip_address}/24", strict=False)
            return str(ipv4_network.network_address)
        else:
            # Zero the last 80 bits for IPv6 (keep /48 prefix)
            ipv6_network = ipaddress.IPv6Network(f"{ip_address}/48", strict=False)
            return str(ipv6_network.network_address)
    except ValueError:
        # Invalid IP address format
        return "unknown"


def get_client_ip(request: HttpRequest, anonymise: bool = False) -> str:
    """Extract the client IP address from the request.

    Handles X-Forwarded-For header from reverse proxies (nginx, load balancers).

    Args:
        request: The HTTP request object.
        anonymise: If True, return GDPR-compliant anonymised IP.

    Returns:
        The client's IP address (full or anonymised based on parameter).
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # Take the first IP in the chain (client's real IP)
        ip = str(x_forwarded_for).split(",")[0].strip()
    else:
        ip = str(request.META.get("REMOTE_ADDR", "unknown"))

    if anonymise:
        return anonymise_ip(ip)
    return ip


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

    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
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

    def process_exception(self, request: HttpRequest, exception: Exception) -> HttpResponse | None:
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
        self, request: HttpRequest, response: HttpResponse | None
    ) -> None:
        """Log when a user is denied access to a resource.

        Uses full IP for security logging (legitimate interest under GDPR).

        Args:
            request: The HTTP request object.
            response: The HTTP response object (may be None for exceptions).
        """
        security_logger.warning(
            "Authorization failure",
            extra={
                "event_type": "authorization_failure",
                "client_ip": get_client_ip(request),  # Full IP for security
                "path": request.path,
                "method": request.method,
                "user": str(request.user) if request.user.is_authenticated else "anonymous",
                "user_id": request.user.id if request.user.is_authenticated else None,
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                "referer": request.META.get("HTTP_REFERER", ""),
            },
        )

    def _log_authentication_required(self, request: HttpRequest, response: HttpResponse) -> None:
        """Log when authentication is required but not provided.

        Uses full IP for security logging (legitimate interest under GDPR).

        Args:
            request: The HTTP request object.
            response: The HTTP response object.
        """
        security_logger.info(
            "Authentication required",
            extra={
                "event_type": "authentication_required",
                "client_ip": get_client_ip(request),  # Full IP for security
                "path": request.path,
                "method": request.method,
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
            },
        )


# Signal handlers for authentication events


@receiver(user_logged_in)
def log_user_login(sender, request: HttpRequest, user, **kwargs) -> None:
    """Log successful user login events.

    Uses full IP for security logging (legitimate interest under GDPR).

    Args:
        sender: The sender of the signal.
        request: The HTTP request object.
        user: The user who logged in.
        **kwargs: Additional keyword arguments from the signal.
    """
    security_logger.info(
        f"User login successful: {user.username}",
        extra={
            "event_type": "login_success",
            "user": str(user),
            "user_id": user.id,
            "username": user.username,
            "client_ip": get_client_ip(request),  # Full IP for security
            "user_agent": request.META.get("HTTP_USER_AGENT", ""),
        },
    )


@receiver(user_logged_out)
def log_user_logout(sender, request: HttpRequest, user, **kwargs) -> None:
    """Log user logout events.

    Uses full IP for security logging (legitimate interest under GDPR).

    Args:
        sender: The sender of the signal.
        request: The HTTP request object.
        user: The user who logged out.
        **kwargs: Additional keyword arguments from the signal.
    """
    if user is None:
        return

    security_logger.info(
        f"User logout: {user.username}",
        extra={
            "event_type": "logout",
            "user": str(user),
            "user_id": user.id,
            "username": user.username,
            "client_ip": get_client_ip(request),  # Full IP for security
        },
    )


@receiver(user_login_failed)
def log_user_login_failed(
    sender, credentials, request: HttpRequest | None = None, **kwargs
) -> None:
    """Log failed login attempts.

    Uses full IP for security logging (legitimate interest under GDPR).

    Args:
        sender: The sender of the signal.
        credentials: The credentials that were attempted.
        request: The HTTP request object (may be None).
        **kwargs: Additional keyword arguments from the signal.
    """
    if request is None:
        return

    client_ip = get_client_ip(request)  # Full IP for security

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
