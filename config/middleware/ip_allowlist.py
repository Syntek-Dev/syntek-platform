"""IP allowlist middleware for restricting admin area access.

This module provides middleware to restrict access to admin and sensitive areas
based on IP address allowlisting. This adds an additional layer of security
beyond authentication for high-security admin panels.

Security Features:
- IP-based access control for admin areas
- Support for IP ranges (CIDR notation)
- Configurable via environment variables
- Returns 404 (not 403) to avoid information disclosure
- Audit logging of blocked access attempts

Configuration via environment variables:
- ADMIN_ALLOWED_IPS: Comma-separated list of allowed IPs or CIDR ranges
  Example: "192.168.1.0/24,10.0.0.1,203.0.113.5"

Protected paths (configurable):
- /admin/ - Django admin panel
- /cms/admin/ - CMS admin panel
- /api/admin/ - Admin API endpoints

Implementation follows security best practices:
- Returns 404 instead of 403 to hide admin paths from attackers
- Supports both IPv4 and IPv6
- Handles X-Forwarded-For from reverse proxies
- Logs all blocked attempts for security monitoring

References:
- examples/security/SECURITY-HEADERS.md
"""

import ipaddress
import logging
from collections.abc import Callable

from django.conf import settings
from django.http import Http404, HttpRequest, HttpResponse

from config.utils.request import get_client_ip

logger = logging.getLogger("security.ip_allowlist")


class IPAllowlistMiddleware:
    """Restrict access to admin areas based on IP allowlist.

    This middleware checks if the client IP is in the allowlist before
    granting access to protected admin paths. If the IP is not allowlisted,
    a 404 response is returned to prevent information disclosure.

    Configuration:
    Set ADMIN_ALLOWED_IPS in environment variables:
        ADMIN_ALLOWED_IPS="192.168.1.0/24,10.0.0.1,203.0.113.5"

    Or in Django settings:
        ADMIN_ALLOWED_IPS = ["192.168.1.0/24", "10.0.0.1", "203.0.113.5"]

    Protected paths (default):
    - /admin/ - Django admin
    - /cms/admin/ - CMS admin
    - /api/admin/ - Admin API

    Attributes:
        get_response: The next middleware or view in the chain.
        allowed_ips: List of allowed IP addresses and ranges.
        protected_paths: List of URL prefixes to protect.
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialise the middleware.

        Args:
            get_response: The next middleware or view function in the request/response chain.
        """
        self.get_response = get_response

        # Load allowed IPs from settings
        self.allowed_ips = self._load_allowed_ips()

        # Define protected paths (can be customised via settings)
        self.protected_paths = getattr(
            settings,
            "IP_ALLOWLIST_PROTECTED_PATHS",
            ["/admin/", "/cms/admin/", "/api/admin/"],
        )

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process the request and check IP allowlist for protected paths.

        Args:
            request: The incoming HTTP request.

        Returns:
            The HTTP response (or raises Http404 if IP is blocked).

        Raises:
            Http404: If the IP is not allowlisted and trying to access a protected path.
        """
        # Check if the request path is protected
        if self._is_protected_path(request.path):
            # Get client IP (using centralised utility)
            client_ip = get_client_ip(request)

            # Check if IP is allowlisted
            if not self._is_ip_allowed(client_ip):
                # Log the blocked attempt
                logger.warning(
                    f"Blocked admin access attempt from {client_ip}",
                    extra={
                        "event_type": "ip_allowlist_blocked",
                        "client_ip": client_ip,
                        "path": request.path,
                        "method": request.method,
                        "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                    },
                )

                # Return 404 to avoid information disclosure
                # (don't reveal that an admin panel exists)
                raise Http404("Page not found")

        response = self.get_response(request)
        return response

    def _load_allowed_ips(self) -> list[ipaddress.IPv4Network | ipaddress.IPv6Network]:
        """Load and parse allowed IPs from settings.

        Supports both individual IPs and CIDR ranges for IPv4 and IPv6.

        Returns:
            List of IP network objects for allowlist checking.
        """
        allowed_ips = []

        # Get from settings (list or comma-separated string)
        ip_setting = getattr(settings, "ADMIN_ALLOWED_IPS", "")

        if isinstance(ip_setting, str):
            # Parse comma-separated string
            ip_list = [ip.strip() for ip in ip_setting.split(",") if ip.strip()]
        elif isinstance(ip_setting, (list, tuple)):
            ip_list = ip_setting
        else:
            logger.warning("ADMIN_ALLOWED_IPS is not configured or invalid format")
            return []

        # Parse each IP or CIDR range
        for ip_str in ip_list:
            try:
                # Try parsing as network (supports both single IPs and CIDR)
                network = ipaddress.ip_network(ip_str, strict=False)
                allowed_ips.append(network)
            except ValueError as e:
                logger.error(
                    f"Invalid IP address or CIDR range in ADMIN_ALLOWED_IPS: {ip_str}",
                    extra={"error": str(e)},
                )

        if allowed_ips:
            logger.info(
                f"IP allowlist configured with {len(allowed_ips)} entry/entries",
                extra={"count": len(allowed_ips)},
            )
        else:
            logger.warning("IP allowlist is empty - admin access is NOT IP-restricted")

        return allowed_ips

    def _is_protected_path(self, path: str) -> bool:
        """Check if the request path is protected by IP allowlist.

        Args:
            path: The request path.

        Returns:
            True if the path is protected, False otherwise.
        """
        return any(path.startswith(prefix) for prefix in self.protected_paths)

    def _is_ip_allowed(self, ip_str: str) -> bool:
        """Check if an IP address is in the allowlist.

        Supports both IPv4 and IPv6, and handles CIDR ranges.

        Args:
            ip_str: The IP address to check.

        Returns:
            True if the IP is allowlisted, False otherwise.
        """
        # If no IPs configured, allow all (IP restriction disabled)
        if not self.allowed_ips:
            return True

        try:
            client_ip = ipaddress.ip_address(ip_str)
        except ValueError:
            logger.error(
                f"Invalid IP address format: {ip_str}",
                extra={"ip": ip_str},
            )
            return False

        # Check if IP is in any of the allowed networks
        for network in self.allowed_ips:
            if client_ip in network:
                return True

        return False
