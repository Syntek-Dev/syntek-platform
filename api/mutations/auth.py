"""GraphQL mutations for authentication operations.

This module defines all authentication-related mutations with full implementation
for Phase 3 including security requirements C4, C5, H2, H4, H10, M1.
"""

from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone as tz

import strawberry
from strawberry.types import Info

from api.errors import AuthenticationError, ErrorCode, ValidationError
from api.types.auth import (
    AuthPayload,
    EnableTwoFactorInput,
    LoginInput,
    PasswordChangeInput,
    PasswordResetInput,
    PasswordResetRequestInput,
    RegisterInput,
    TwoFactorSetupPayload,
)
from api.types.user import UserType
from apps.core.models import EmailVerificationToken, Organisation
from apps.core.services.audit_service import AuditService
from apps.core.services.auth_service import AuthService
from apps.core.services.email_service import EmailService
from apps.core.services.password_reset_service import PasswordResetService
from apps.core.services.token_service import TokenService
from apps.core.utils.token_hasher import TokenHasher

User = get_user_model()


def _user_to_graphql(user: Any) -> UserType:
    """Convert Django User instance to GraphQL UserType.

    Args:
        user: Django User instance

    Returns:
        UserType for GraphQL response
    """
    return UserType(
        id=strawberry.ID(str(user.id)),
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        email_verified=user.email_verified,
        two_factor_enabled=user.two_factor_enabled,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@strawberry.type
class AuthMutations:
    """GraphQL mutations for authentication."""

    @strawberry.mutation
    def register(self, info: Info, input: RegisterInput) -> AuthPayload:
        """Register a new user account.

        Creates user, sends verification email, and returns auth tokens.
        Implements error code standardisation (H4).

        Args:
            info: GraphQL execution info
            input: Registration input data

        Returns:
            AuthPayload with token and user data

        Raises:
            ValidationError: If email exists or organisation not found (H4)
        """
        # Get client IP for audit logging
        ip_address = info.context.request.META.get("REMOTE_ADDR", "")

        # Find organisation by slug
        try:
            organisation = Organisation.objects.get(slug=input.organisation_slug)
        except Organisation.DoesNotExist as err:
            raise ValidationError(
                ErrorCode.ORGANISATION_NOT_FOUND,
                f"Organisation with slug '{input.organisation_slug}' not found",
            ) from err

        # Register user (raises ValueError if email exists)
        try:
            with transaction.atomic():
                user = AuthService.register_user(
                    email=input.email,
                    password=input.password,
                    first_name=input.first_name,
                    last_name=input.last_name,
                    organisation=organisation,
                )

                # Create email verification token (expires in 24 hours)
                from django.utils import timezone as tz

                token = TokenHasher.generate_token()
                token_hash = TokenHasher.hash_token(token)
                EmailVerificationToken.objects.create(
                    user=user,
                    token_hash=token_hash,
                    expires_at=tz.now() + tz.timedelta(hours=24),
                )

                # Send verification email
                EmailService.send_verification_email(user, token)

                # Create session tokens
                tokens = TokenService.create_tokens(user)

                # Log registration
                AuditService.log_event(
                    action="user_registered",
                    user=user,
                    organisation=organisation,
                    ip_address=ip_address,
                )

                return AuthPayload(
                    token=tokens["access_token"],
                    refresh_token=tokens["refresh_token"],
                    user=_user_to_graphql(user),
                    requires_two_factor=False,
                )

        except ValueError as e:
            # Convert to standardised error (H4)
            if "already registered" in str(e):
                raise ValidationError(ErrorCode.EMAIL_ALREADY_EXISTS, str(e)) from e
            raise ValidationError(ErrorCode.INVALID_INPUT, str(e)) from e

    @strawberry.mutation
    def login(self, info: Info, input: LoginInput) -> AuthPayload:
        """Login with email and password.

        Enforces email verification (C5) and implements standardised errors (H4).

        Args:
            info: GraphQL execution info
            input: Login credentials

        Returns:
            AuthPayload with token and user data

        Raises:
            AuthenticationError: If credentials invalid or email not verified (H4)
        """
        # Get client IP and device fingerprint
        ip_address = info.context.request.META.get("REMOTE_ADDR", "")
        user_agent = info.context.request.META.get("HTTP_USER_AGENT", "")

        # Authenticate user
        result = AuthService.login(
            email=input.email,
            password=input.password,
            device_fingerprint=user_agent[:200],  # Truncate user agent
            ip_address=ip_address,
        )

        if not result:
            # Log failed attempt
            AuditService.log_event(
                action="login_failed",
                user=None,
                organisation=None,
                ip_address=ip_address,
                metadata={"email": input.email, "reason": "invalid_credentials"},
            )
            raise AuthenticationError(ErrorCode.INVALID_CREDENTIALS, "Invalid email or password")

        user = result["user"]

        # Enforce email verification (C5 requirement)
        if not user.email_verified:
            AuditService.log_event(
                action="login_blocked_unverified",
                user=user,
                organisation=user.organisation,
                ip_address=ip_address,
            )
            raise AuthenticationError(
                ErrorCode.EMAIL_NOT_VERIFIED,
                "Please verify your email address before logging in",
            )

        # Check if account is locked
        if not user.is_active:
            raise AuthenticationError(ErrorCode.ACCOUNT_DISABLED, "Your account has been disabled")

        # Check if 2FA is required (Phase 4 implementation)
        requires_two_factor = user.two_factor_enabled and not input.totp_code
        if requires_two_factor and not input.totp_code:
            return AuthPayload(
                token="",  # No token until 2FA verified
                refresh_token="",
                user=_user_to_graphql(user),
                requires_two_factor=True,
            )

        # Log successful login
        AuditService.log_event(
            action="login_success",
            user=user,
            organisation=user.organisation,
            ip_address=ip_address,
        )

        return AuthPayload(
            token=result["access_token"],
            refresh_token=result["refresh_token"],
            user=_user_to_graphql(user),
            requires_two_factor=False,
        )

    @strawberry.mutation
    def logout(self, info: Info) -> bool:
        """Logout and revoke current session.

        Implements proper token revocation (H10 requirement).

        Args:
            info: GraphQL execution info with authenticated user

        Returns:
            True if logout successful

        Raises:
            AuthenticationError: If user not authenticated
        """
        user = info.context.request.user

        if not user.is_authenticated:
            raise AuthenticationError(ErrorCode.NOT_AUTHENTICATED, "Authentication required")

        # Get access token from request headers
        auth_header = info.context.request.META.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]  # Remove "Bearer " prefix
        else:
            token = ""

        # Revoke current session token (H10 requirement)
        if token:
            AuthService.logout(user, token)

        # Log logout
        ip_address = info.context.request.META.get("REMOTE_ADDR", "")
        AuditService.log_event(
            action="logout",
            user=user,
            organisation=user.organisation,
            ip_address=ip_address,
        )

        return True

    @strawberry.mutation
    def refresh_token(self, info: Info, refresh_token: str) -> AuthPayload:
        """Refresh access token using refresh token.

        Implements replay detection (H9) and standardised errors (H4).

        Args:
            info: GraphQL execution info
            refresh_token: Valid refresh token

        Returns:
            AuthPayload with new tokens

        Raises:
            AuthenticationError: If refresh token invalid, expired, or replayed
        """
        user_agent = info.context.request.META.get("HTTP_USER_AGENT", "")

        # Get session token to find user
        token_hash = TokenHasher.hash_token(refresh_token)
        try:
            from apps.core.models import SessionToken

            session = SessionToken.objects.select_related("user").get(refresh_token_hash=token_hash)
            user = session.user
        except SessionToken.DoesNotExist as err:
            raise AuthenticationError(
                ErrorCode.TOKEN_INVALID, "Invalid or expired refresh token"
            ) from err

        # Refresh tokens with replay detection (H9)
        tokens = TokenService.refresh_tokens(
            refresh_token=refresh_token,
            device_fingerprint=user_agent[:200],
        )

        if not tokens:
            raise AuthenticationError(ErrorCode.TOKEN_INVALID, "Invalid or expired refresh token")

        return AuthPayload(
            token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
            user=_user_to_graphql(user),
            requires_two_factor=False,
        )

    @strawberry.mutation
    def request_password_reset(self, info: Info, input: PasswordResetRequestInput) -> bool:
        """Request password reset email.

        Always returns True to prevent user enumeration (M7).

        Args:
            info: GraphQL execution info
            input: Email to send reset link

        Returns:
            True (always, to prevent user enumeration - M7)
        """
        ip_address = info.context.request.META.get("REMOTE_ADDR", "")

        try:
            user = User.objects.get(email=input.email)

            # Create password reset token (hashed - C3)
            token = PasswordResetService.create_reset_token(user, ip_address)

            # Send reset email
            EmailService.send_password_reset_email(user, token)

            # Log reset request
            AuditService.log_event(
                action="password_reset_requested",
                user=user,
                organisation=user.organisation,
                ip_address=ip_address,
            )

        except User.DoesNotExist:
            # Return True anyway to prevent user enumeration (M7)
            pass

        return True

    @strawberry.mutation
    def reset_password(self, info: Info, input: PasswordResetInput) -> bool:
        """Complete password reset with token.

        Revokes all sessions after reset (H8) and uses hash comparison (C3).

        Args:
            info: GraphQL execution info
            input: Reset token and new password

        Returns:
            True if reset successful

        Raises:
            AuthenticationError: If token invalid or expired
            ValidationError: If password weak
        """
        ip_address = info.context.request.META.get("REMOTE_ADDR", "")

        # Verify reset token (C3 - hash comparison)
        user = PasswordResetService.verify_reset_token(input.token)
        if not user:
            raise AuthenticationError(ErrorCode.TOKEN_INVALID, "Invalid or expired reset token")

        try:
            # Reset password and revoke all sessions (H8)
            PasswordResetService.reset_password(user, input.token, input.new_password)

            # Log password reset
            AuditService.log_event(
                action="password_reset_completed",
                user=user,
                organisation=user.organisation,
                ip_address=ip_address,
            )

            return True

        except ValueError as e:
            raise ValidationError(ErrorCode.PASSWORD_TOO_WEAK, str(e)) from e

    @strawberry.mutation
    def change_password(self, info: Info, input: PasswordChangeInput) -> bool:
        """Change password for authenticated user.

        Revokes all other sessions (H8) and validates password strength.

        Args:
            info: GraphQL execution info with authenticated user
            input: Current and new password

        Returns:
            True if change successful

        Raises:
            AuthenticationError: If user not authenticated or current password wrong
            ValidationError: If new password weak or in history
        """
        user = info.context.request.user

        if not user.is_authenticated:
            raise AuthenticationError(ErrorCode.NOT_AUTHENTICATED, "Authentication required")

        ip_address = info.context.request.META.get("REMOTE_ADDR", "")

        # Change password (validates and revokes sessions)
        success = AuthService.change_password(user, input.current_password, input.new_password)

        if not success:
            raise AuthenticationError(
                ErrorCode.INVALID_CREDENTIALS, "Current password is incorrect"
            )

        # Log password change
        AuditService.log_event(
            action="password_changed",
            user=user,
            organisation=user.organisation,
            ip_address=ip_address,
        )

        return True

    @strawberry.mutation
    def verify_email(self, info: Info, token: str) -> bool:
        """Verify email address with token.

        Uses hash comparison for token validation (C3).

        Args:
            info: GraphQL execution info
            token: Email verification token from email

        Returns:
            True if verification successful

        Raises:
            AuthenticationError: If token invalid or expired
        """
        ip_address = info.context.request.META.get("REMOTE_ADDR", "")

        # Hash token for lookup (C3)
        token_hash = TokenHasher.hash_token(token)

        try:
            verification_token = EmailVerificationToken.objects.select_related("user").get(
                token_hash=token_hash
            )

            # Check if token is valid
            if not verification_token.is_valid():
                raise AuthenticationError(ErrorCode.TOKEN_EXPIRED, "Verification token has expired")

            # Mark email as verified
            user = verification_token.user
            user.email_verified = True
            user.save(update_fields=["email_verified"])

            # Mark token as used
            verification_token.mark_used()

            # Log verification
            AuditService.log_event(
                action="email_verified",
                user=user,
                organisation=user.organisation,
                ip_address=ip_address,
            )

            return True

        except EmailVerificationToken.DoesNotExist as err:
            raise AuthenticationError(
                ErrorCode.TOKEN_INVALID, "Invalid verification token"
            ) from err

    @strawberry.mutation
    def resend_verification_email(self, info: Info) -> bool:
        """Resend email verification for current user.

        Invalidates old tokens before creating new one.

        Args:
            info: GraphQL execution info with authenticated user

        Returns:
            True if email sent

        Raises:
            AuthenticationError: If user not authenticated
            ValidationError: If email already verified
        """
        user = info.context.request.user

        if not user.is_authenticated:
            raise AuthenticationError(ErrorCode.NOT_AUTHENTICATED, "Authentication required")

        if user.email_verified:
            raise ValidationError(ErrorCode.INVALID_INPUT, "Email address is already verified")

        # Invalidate old verification tokens
        EmailVerificationToken.objects.filter(user=user, used=False).update(used=True)

        # Create new verification token (expires in 24 hours)
        token = TokenHasher.generate_token()
        token_hash = TokenHasher.hash_token(token)
        EmailVerificationToken.objects.create(
            user=user,
            token_hash=token_hash,
            expires_at=tz.now() + tz.timedelta(hours=24),
        )

        # Send verification email
        EmailService.send_verification_email(user, token)

        return True

    @strawberry.mutation
    def enable_two_factor(self, info: Info, input: EnableTwoFactorInput) -> bool:
        """Enable two-factor authentication (Phase 4).

        Args:
            info: GraphQL execution info with authenticated user
            input: TOTP code to verify setup

        Returns:
            True if 2FA enabled

        Raises:
            PermissionError: If user not authenticated
            ValueError: If TOTP code invalid
        """
        # TODO: Implement 2FA enable (Phase 4)
        raise NotImplementedError("Enable 2FA not implemented yet - Phase 4")

    @strawberry.mutation
    def disable_two_factor(self, info: Info, password: str) -> bool:
        """Disable two-factor authentication (Phase 4).

        Args:
            info: GraphQL execution info with authenticated user
            password: User password to confirm

        Returns:
            True if 2FA disabled

        Raises:
            PermissionError: If user not authenticated
            ValueError: If password invalid
        """
        # TODO: Implement 2FA disable (Phase 4)
        raise NotImplementedError("Disable 2FA not implemented yet - Phase 4")

    @strawberry.mutation
    def generate_two_factor_setup(self, info: Info) -> TwoFactorSetupPayload:
        """Generate 2FA setup data (QR code, secret, backup codes) - Phase 4.

        Args:
            info: GraphQL execution info with authenticated user

        Returns:
            TwoFactorSetupPayload with secret and QR code

        Raises:
            PermissionError: If user not authenticated
        """
        # TODO: Implement 2FA setup generation (Phase 4)
        raise NotImplementedError("Generate 2FA setup not implemented yet - Phase 4")
