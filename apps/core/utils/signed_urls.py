"""Signed URL utility for secure time-limited access to resources.

This module provides functionality for generating and verifying signed URLs for sensitive actions
such as password reset, email verification, file downloads, and admin access.

Security Features:
- HMAC-SHA256 signatures prevent tampering
- Time-based expiration
- Optional IP binding for additional security
- Single-use token support (requires database tracking)
- Protection against signature stripping attacks

Implementation follows OWASP guidelines for secure URL design and prevents:
- URL tampering
- Signature forgery
- Replay attacks (with single-use tokens)
- Parameter manipulation

References:
- examples/security/SIGNED-URLS.md
- OWASP Cheat Sheet: Authentication
"""

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class SignedURLService:
    """Service for creating and verifying signed URLs.

    Provides methods for generating time-limited, tamper-proof URLs for sensitive actions.
    All signatures are generated using HMAC-SHA256 with a secret key.

    Security Notes:
    - Always use HTTPS in production to prevent signature interception
    - Set appropriate expiration times based on action sensitivity
    - Consider IP binding for high-security actions
    - Use single-use tokens for critical actions (password reset, email verification)
    """

    def __init__(self, secret_key: str | None = None):
        """Initialise the signed URL service.

        Args:
            secret_key: Secret key for HMAC signing. Defaults to Django SECRET_KEY.

        Raises:
            ImproperlyConfigured: If no secret key is provided and Django SECRET_KEY is not set.
        """
        self.secret_key = secret_key or getattr(settings, "SECRET_KEY", None)

        if not self.secret_key:
            raise ImproperlyConfigured(
                "SECRET_KEY must be set in Django settings or provided to SignedURLService"
            )

    def generate_signed_url(
        self,
        base_url: str,
        params: dict[str, Any] | None = None,
        expires_in_seconds: int = 3600,
        ip_address: str | None = None,
    ) -> str:
        """Generate a signed URL with expiration and optional IP binding.

        Args:
            base_url: The base URL to sign (e.g., '/admin/special-action/').
            params: Additional query parameters to include.
            expires_in_seconds: Time until URL expires (default: 1 hour).
            ip_address: Optional IP address to bind the URL to.

        Returns:
            The signed URL with signature and expiration parameters.

        Example:
            >>> service = SignedURLService()
            >>> url = service.generate_signed_url(
            ...     '/download/file/',
            ...     params={'file_id': '123'},
            ...     expires_in_seconds=900,  # 15 minutes
            ...     ip_address='192.168.1.1'
            ... )
            >>> print(url)
            '/download/file/?file_id=123&expires=1234567890&signature=abc123...'
        """
        params = params or {}

        # Add expiration timestamp
        expiration_time = int(time.time()) + expires_in_seconds
        params["expires"] = str(expiration_time)

        # Add IP binding if provided
        if ip_address:
            params["ip"] = ip_address

        # Parse the base URL
        parsed_url = urlparse(base_url)
        query_params = parse_qs(parsed_url.query)

        # Merge with existing query parameters
        for key, value in params.items():
            query_params[key] = [str(value)]

        # Generate signature
        signature = self._generate_signature(parsed_url.path, query_params, ip_address)
        query_params["signature"] = [signature]

        # Reconstruct URL with signature
        new_query = urlencode(query_params, doseq=True)
        signed_url = urlunparse(
            (
                parsed_url.scheme,
                parsed_url.netloc,
                parsed_url.path,
                parsed_url.params,
                new_query,
                parsed_url.fragment,
            )
        )

        return signed_url

    def verify_signed_url(
        self,
        url: str,
        current_ip: str | None = None,
    ) -> tuple[bool, str | None]:
        """Verify a signed URL's authenticity and expiration.

        Args:
            url: The signed URL to verify.
            current_ip: The current request IP address (required if URL is IP-bound).

        Returns:
            A tuple of (is_valid, error_message).
            - is_valid: True if the URL is valid, False otherwise.
            - error_message: None if valid, otherwise a description of the error.

        Example:
            >>> service = SignedURLService()
            >>> is_valid, error = service.verify_signed_url(
            ...     '/download/file/?file_id=123&expires=1234567890&signature=abc123...',
            ...     current_ip='192.168.1.1'
            ... )
            >>> if is_valid:
            ...     # Proceed with action
            ...     pass
            ... else:
            ...     # Handle error
            ...     print(error)
        """
        # Parse the URL
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)

        # Check if signature exists
        if "signature" not in query_params:
            return False, "Missing signature"

        provided_signature = query_params["signature"][0]

        # Check if expiration exists
        if "expires" not in query_params:
            return False, "Missing expiration"

        try:
            expiration_time = int(query_params["expires"][0])
        except (ValueError, IndexError):
            return False, "Invalid expiration format"

        # Check if URL has expired
        current_time = int(time.time())
        if current_time > expiration_time:
            return False, "URL has expired"

        # Check IP binding if present
        if "ip" in query_params:
            bound_ip = query_params["ip"][0]
            if not current_ip:
                return False, "IP address required for verification"
            if bound_ip != current_ip:
                return False, "IP address mismatch"

        # Remove signature from params for verification
        verification_params = {k: v for k, v in query_params.items() if k != "signature"}

        # Generate expected signature
        expected_signature = self._generate_signature(
            parsed_url.path,
            verification_params,
            query_params.get("ip", [None])[0],
        )

        # Compare signatures using constant-time comparison
        if not hmac.compare_digest(provided_signature, expected_signature):
            return False, "Invalid signature"

        return True, None

    def _generate_signature(
        self,
        path: str,
        params: dict[str, list[str]],
        ip_address: str | None = None,
    ) -> str:
        """Generate HMAC-SHA256 signature for URL components.

        Args:
            path: The URL path.
            params: Query parameters (excluding signature).
            ip_address: Optional IP address to include in signature.

        Returns:
            Hex-encoded HMAC-SHA256 signature.
        """
        # Sort parameters for consistent signature generation
        sorted_params = sorted(params.items())

        # Create message to sign: path + sorted params + IP (if present)
        message_parts = [path]

        for key, values in sorted_params:
            for value in sorted(values):
                message_parts.append(f"{key}={value}")

        if ip_address:
            message_parts.append(f"ip={ip_address}")

        message = "&".join(message_parts)

        # Generate HMAC-SHA256 signature
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return signature


# Convenience functions for common use cases


def generate_password_reset_url(
    user_id: int,
    token: str,
    expires_in_seconds: int = 900,  # 15 minutes
) -> str:
    """Generate a signed password reset URL.

    Args:
        user_id: The user ID.
        token: The password reset token (already hashed in database).
        expires_in_seconds: Time until URL expires (default: 15 minutes).

    Returns:
        The signed password reset URL.

    Example:
        >>> url = generate_password_reset_url(user_id=123, token='abc123')
    """
    service = SignedURLService()
    return service.generate_signed_url(
        "/api/auth/reset-password/",
        params={"user_id": user_id, "token": token},
        expires_in_seconds=expires_in_seconds,
    )


def generate_email_verification_url(
    user_id: int,
    token: str,
    expires_in_seconds: int = 86400,  # 24 hours
) -> str:
    """Generate a signed email verification URL.

    Args:
        user_id: The user ID.
        token: The email verification token.
        expires_in_seconds: Time until URL expires (default: 24 hours).

    Returns:
        The signed email verification URL.

    Example:
        >>> url = generate_email_verification_url(user_id=123, token='xyz789')
    """
    service = SignedURLService()
    return service.generate_signed_url(
        "/api/auth/verify-email/",
        params={"user_id": user_id, "token": token},
        expires_in_seconds=expires_in_seconds,
    )


def generate_file_download_url(
    file_id: str,
    expires_in_seconds: int = 3600,  # 1 hour
    ip_address: str | None = None,
) -> str:
    """Generate a signed file download URL.

    Args:
        file_id: The file ID.
        expires_in_seconds: Time until URL expires (default: 1 hour).
        ip_address: Optional IP address to bind the URL to.

    Returns:
        The signed file download URL.

    Example:
        >>> url = generate_file_download_url(
        ...     file_id='document-123',
        ...     ip_address='192.168.1.1'
        ... )
    """
    service = SignedURLService()
    return service.generate_signed_url(
        "/api/files/download/",
        params={"file_id": file_id},
        expires_in_seconds=expires_in_seconds,
        ip_address=ip_address,
    )


def verify_url(url: str, current_ip: str | None = None) -> tuple[bool, str | None]:
    """Verify a signed URL.

    Args:
        url: The signed URL to verify.
        current_ip: The current request IP address.

    Returns:
        A tuple of (is_valid, error_message).

    Example:
        >>> is_valid, error = verify_url('/api/auth/reset-password/?...')
        >>> if not is_valid:
        ...     print(f"Invalid URL: {error}")
    """
    service = SignedURLService()
    return service.verify_signed_url(url, current_ip)
