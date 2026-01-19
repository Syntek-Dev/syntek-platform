"""Custom exception hierarchy for core application services.

This module defines domain-specific exceptions for authentication, validation,
and other core service operations. Using custom exceptions instead of generic
ValueError provides better error handling, clearer code intent, and easier
debugging.

Example:
    >>> from apps.core.exceptions import EmailAlreadyExistsError
    >>> if User.objects.filter(email=email).exists():
    ...     raise EmailAlreadyExistsError(email)
"""


# Base exceptions


class CoreServiceError(Exception):
    """Base exception for all core service errors.

    All custom exceptions in the core app should inherit from this base.
    This allows catching all core-related errors with a single except clause.
    """

    pass


# Authentication exceptions


class AuthenticationError(CoreServiceError):
    """Base exception for authentication-related errors."""

    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid.

    This exception provides a generic message to prevent user enumeration
    attacks (security requirement SV2).
    """

    def __init__(self, message: str = "Invalid credentials"):
        """Initialise with generic error message.

        Args:
            message: Error message (default: "Invalid credentials")
        """
        self.message = message
        super().__init__(self.message)


class AccountLockedError(AuthenticationError):
    """Raised when user account is temporarily locked due to failed login attempts.

    Attributes:
        unlock_time: When the account will be automatically unlocked
    """

    def __init__(self, unlock_time) -> None:
        """Initialise with unlock time.

        Args:
            unlock_time: Datetime when account will be unlocked
        """
        from django.utils import timezone

        self.unlock_time = unlock_time

        # Calculate time remaining
        time_remaining = unlock_time - timezone.now()
        minutes = int(time_remaining.total_seconds() / 60)

        if minutes > 0:
            message = f"Account locked. Try again in {minutes} minutes."
        else:
            message = "Account locked. Try again shortly."

        super().__init__(message)


class EmailNotVerifiedError(AuthenticationError):
    """Raised when attempting to login with unverified email address."""

    def __init__(self, email: str) -> None:
        """Initialise with user email.

        Args:
            email: The unverified email address
        """
        self.email = email
        super().__init__(f"Email address {email} has not been verified")


class TwoFactorRequiredError(AuthenticationError):
    """Raised when 2FA is required but not provided."""

    def __init__(self, message: str = "Two-factor authentication required") -> None:
        """Initialise with error message.

        Args:
            message: Error message (default: "Two-factor authentication required")
        """
        super().__init__(message)


class Invalid2FACodeError(AuthenticationError):
    """Raised when 2FA code is invalid or expired."""

    def __init__(self, message: str = "Invalid or expired 2FA code") -> None:
        """Initialise with error message.

        Args:
            message: Error message
        """
        super().__init__(message)


# Registration/validation exceptions


class ValidationError(CoreServiceError):
    """Base exception for validation errors."""

    pass


class EmailAlreadyExistsError(ValidationError):
    """Raised when attempting to register with an email that already exists.

    Note: Error message is generic to prevent user enumeration (SV2).
    """

    def __init__(self, email: str = "") -> None:
        """Initialise with email address.

        Args:
            email: The duplicate email address (not exposed in message)
        """
        self.email = email
        # Generic message to prevent enumeration
        super().__init__("Registration failed due to invalid data")


class InvalidEmailError(ValidationError):
    """Raised when email format is invalid."""

    def __init__(self, email: str) -> None:
        """Initialise with invalid email.

        Args:
            email: The invalid email address
        """
        self.email = email
        super().__init__(f"Invalid email format: {email}")


class WeakPasswordError(ValidationError):
    """Raised when password doesn't meet security requirements."""

    def __init__(self, errors: list[str]) -> None:
        """Initialise with validation errors.

        Args:
            errors: List of password validation error messages
        """
        self.errors = errors
        message = "Password does not meet requirements: " + "; ".join(errors)
        super().__init__(message)


class PasswordReusedError(ValidationError):
    """Raised when attempting to reuse a previous password."""

    def __init__(self, history_count: int = 5) -> None:
        """Initialise with password history count.

        Args:
            history_count: Number of previous passwords checked
        """
        self.history_count = history_count
        super().__init__(f"Cannot reuse any of your last {history_count} passwords")


class PasswordBreachedError(ValidationError):
    """Raised when password found in breach database (HaveIBeenPwned)."""

    def __init__(self, occurrences: int = 0) -> None:
        """Initialise with breach occurrence count.

        Args:
            occurrences: Number of times password appeared in breaches
        """
        self.occurrences = occurrences
        super().__init__(
            "This password has been found in data breaches and cannot be used. "
            "Please choose a different password."
        )


# Token/session exceptions


class TokenError(CoreServiceError):
    """Base exception for token-related errors."""

    pass


class InvalidTokenError(TokenError):
    """Raised when token is invalid, expired, or already used."""

    def __init__(self, token_type: str = "Token") -> None:
        """Initialise with token type.

        Args:
            token_type: Type of token (e.g., "Password reset", "Email verification")
        """
        self.token_type = token_type
        super().__init__(f"{token_type} is invalid, expired, or already used")


class TokenExpiredError(TokenError):
    """Raised when token has expired."""

    def __init__(self, token_type: str = "Token") -> None:
        """Initialise with token type.

        Args:
            token_type: Type of token
        """
        self.token_type = token_type
        super().__init__(f"{token_type} has expired")


class TokenAlreadyUsedError(TokenError):
    """Raised when attempting to reuse a single-use token."""

    def __init__(self, token_type: str = "Token") -> None:
        """Initialise with token type.

        Args:
            token_type: Type of token
        """
        self.token_type = token_type
        super().__init__(f"{token_type} has already been used")


class RefreshTokenReplayError(TokenError):
    """Raised when refresh token replay attack is detected.

    This indicates a security incident where a previously used refresh token
    is being reused, potentially by an attacker. All tokens in the family
    should be revoked.
    """

    def __init__(self, family_id: str) -> None:
        """Initialise with token family ID.

        Args:
            family_id: UUID of the compromised token family
        """
        self.family_id = family_id
        super().__init__(f"Token replay detected for family {family_id}")


class SessionLimitExceededError(TokenError):
    """Raised when user exceeds maximum concurrent sessions."""

    def __init__(self, max_sessions: int) -> None:
        """Initialise with session limit.

        Args:
            max_sessions: Maximum number of concurrent sessions allowed
        """
        self.max_sessions = max_sessions
        super().__init__(f"Maximum {max_sessions} concurrent sessions allowed")


# Permission exceptions


class PermissionError(CoreServiceError):
    """Base exception for permission-related errors."""

    pass


class InsufficientPermissionsError(PermissionError):
    """Raised when user lacks required permissions."""

    def __init__(self, required_permission: str) -> None:
        """Initialise with required permission.

        Args:
            required_permission: The permission that was required
        """
        self.required_permission = required_permission
        super().__init__(f"Insufficient permissions. Required: {required_permission}")


class OrganisationAccessDeniedError(PermissionError):
    """Raised when attempting to access resource outside user's organisation."""

    def __init__(self, resource_type: str = "Resource") -> None:
        """Initialise with resource type.

        Args:
            resource_type: Type of resource being accessed
        """
        self.resource_type = resource_type
        super().__init__(f"Access denied. {resource_type} belongs to different organisation")


# Service-specific exceptions


class EmailServiceError(CoreServiceError):
    """Base exception for email service errors."""

    pass


class EmailDeliveryError(EmailServiceError):
    """Raised when email fails to send."""

    def __init__(self, recipient: str, reason: str = "") -> None:
        """Initialise with recipient and failure reason.

        Args:
            recipient: Email address that failed to receive
            reason: Reason for failure
        """
        self.recipient = recipient
        self.reason = reason
        message = f"Failed to send email to {recipient}"
        if reason:
            message += f": {reason}"
        super().__init__(message)


class CaptchaValidationError(ValidationError):
    """Raised when CAPTCHA validation fails."""

    def __init__(self, message: str = "CAPTCHA validation failed") -> None:
        """Initialise with error message.

        Args:
            message: Error message
        """
        super().__init__(message)


class RateLimitExceededError(CoreServiceError):
    """Raised when rate limit is exceeded."""

    def __init__(self, resource: str, retry_after: int = 0) -> None:
        """Initialise with resource and retry time.

        Args:
            resource: The rate-limited resource
            retry_after: Seconds to wait before retrying
        """
        self.resource = resource
        self.retry_after = retry_after
        message = f"Rate limit exceeded for {resource}"
        if retry_after > 0:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message)


# External service exceptions


class ExternalServiceError(CoreServiceError):
    """Base exception for external service integration errors."""

    pass


class HaveIBeenPwnedError(ExternalServiceError):
    """Raised when HaveIBeenPwned API fails."""

    def __init__(self, reason: str = "") -> None:
        """Initialise with failure reason.

        Args:
            reason: Reason for API failure
        """
        self.reason = reason
        message = "Password breach check unavailable"
        if reason:
            message += f": {reason}"
        super().__init__(message)
