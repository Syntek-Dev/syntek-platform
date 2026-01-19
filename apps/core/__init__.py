"""Core application package.

Contains user authentication, organisations, and audit logging.
"""

# Export commonly used exceptions for convenience
from apps.core.exceptions import (
    AccountLockedError,
    AuthenticationError,
    CoreServiceError,
    EmailAlreadyExistsError,
    EmailNotVerifiedError,
    Invalid2FACodeError,
    InvalidCredentialsError,
    InvalidTokenError,
    PasswordBreachedError,
    PasswordReusedError,
    TwoFactorRequiredError,
    ValidationError,
    WeakPasswordError,
)

__all__ = [
    "AccountLockedError",
    "AuthenticationError",
    "CoreServiceError",
    "EmailAlreadyExistsError",
    "EmailNotVerifiedError",
    "Invalid2FACodeError",
    "InvalidCredentialsError",
    "InvalidTokenError",
    "PasswordBreachedError",
    "PasswordReusedError",
    "TwoFactorRequiredError",
    "ValidationError",
    "WeakPasswordError",
]
