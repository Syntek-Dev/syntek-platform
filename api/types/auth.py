"""GraphQL types for authentication operations.

This module defines input and output types for authentication mutations.
Implementation stub for TDD - tests will fail until fully implemented.
"""

import strawberry

from api.types.user import UserType


@strawberry.input
class RegisterInput:
    """Input for user registration mutation."""

    email: str
    password: str
    first_name: str
    last_name: str
    organisation_slug: str


@strawberry.input
class LoginInput:
    """Input for user login mutation."""

    email: str
    password: str
    totp_code: str | None = None  # For 2FA (Phase 4)


@strawberry.input
class PasswordResetRequestInput:
    """Input for password reset request mutation."""

    email: str


@strawberry.input
class PasswordResetInput:
    """Input for password reset completion mutation."""

    token: str
    new_password: str


@strawberry.input
class PasswordChangeInput:
    """Input for password change mutation."""

    current_password: str
    new_password: str


@strawberry.input
class EnableTwoFactorInput:
    """Input for enabling 2FA mutation."""

    totp_code: str  # Verify setup worked


@strawberry.type
class AuthPayload:
    """Response payload for authentication mutations."""

    token: str
    refresh_token: str
    user: UserType
    requires_two_factor: bool = False


@strawberry.type
class TwoFactorSetupPayload:
    """Response payload for 2FA setup mutation."""

    secret: str
    qr_code_url: str
    backup_codes: list[str]
