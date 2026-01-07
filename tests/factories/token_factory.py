"""Token-related test factories.

This module contains factory-boy factories for creating token test data.
"""

import factory
from factory.django import DjangoModelFactory
from factory import SubFactory, Faker, LazyFunction
from django.utils import timezone
from datetime import timedelta
import uuid


# TODO: Import actual models once implemented
# from apps.core.models import (
#     SessionToken,
#     PasswordResetToken,
#     EmailVerificationToken,
#     TOTPDevice,
#     PasswordHistory,
# )

from tests.factories.user_factory import UserFactory


class SessionTokenFactory(DjangoModelFactory):
    """Factory for creating test SessionToken instances.

    Attributes:
        user: User who owns the session
        token_hash: HMAC-SHA256 hash of the session token
        refresh_token_hash: HMAC-SHA256 hash of the refresh token
        expires_at: Token expiration timestamp
        ip_address: Encrypted IP address
        user_agent: Browser user agent string
        token_family: UUID for token rotation tracking
        is_refresh_token_used: Whether refresh token was used
        device_fingerprint: Device identification string
    """

    class Meta:
        # model = SessionToken  # Uncomment when model exists
        model = "core.SessionToken"

    user = SubFactory(UserFactory)
    token_hash = Faker("sha256")
    refresh_token_hash = Faker("sha256")
    expires_at = LazyFunction(lambda: timezone.now() + timedelta(hours=1))
    used = False
    used_at = None
    ip_address = b"\\x00\\x01\\x02\\x03"  # Encrypted IP placeholder
    user_agent = Faker("user_agent")
    token_family = factory.LazyFunction(uuid.uuid4)
    is_refresh_token_used = False
    device_fingerprint = Faker("sha256")
    last_activity_at = LazyFunction(timezone.now)


class PasswordResetTokenFactory(DjangoModelFactory):
    """Factory for creating test PasswordResetToken instances.

    Attributes:
        user: User requesting password reset
        token_hash: HMAC-SHA256 hash of the reset token
        expires_at: Token expiration timestamp (15 minutes)
        used: Whether token has been used
        used_at: Timestamp when token was used
    """

    class Meta:
        # model = PasswordResetToken  # Uncomment when model exists
        model = "core.PasswordResetToken"

    user = SubFactory(UserFactory)
    token_hash = Faker("sha256")
    expires_at = LazyFunction(lambda: timezone.now() + timedelta(minutes=15))
    used = False
    used_at = None


class EmailVerificationTokenFactory(DjangoModelFactory):
    """Factory for creating test EmailVerificationToken instances.

    Attributes:
        user: User to verify email for
        token_hash: HMAC-SHA256 hash of the verification token
        expires_at: Token expiration timestamp (24 hours)
        used: Whether token has been used
        used_at: Timestamp when token was used
    """

    class Meta:
        # model = EmailVerificationToken  # Uncomment when model exists
        model = "core.EmailVerificationToken"

    user = SubFactory(UserFactory)
    token_hash = Faker("sha256")
    expires_at = LazyFunction(lambda: timezone.now() + timedelta(hours=24))
    used = False
    used_at = None


class TOTPDeviceFactory(DjangoModelFactory):
    """Factory for creating test TOTPDevice instances.

    Attributes:
        user: User who owns the TOTP device
        device_name: Human-readable device name
        secret: Fernet-encrypted TOTP secret
        confirmed: Whether device has been confirmed
        last_used_at: Last time device was used for 2FA
    """

    class Meta:
        # model = TOTPDevice  # Uncomment when model exists
        model = "core.TOTPDevice"

    user = SubFactory(UserFactory)
    device_name = Faker("random_element", elements=["iPhone", "Android", "Authenticator App"])
    secret = b"encrypted_secret_placeholder"  # Fernet encrypted
    confirmed = False
    last_used_at = None


class PasswordHistoryFactory(DjangoModelFactory):
    """Factory for creating test PasswordHistory instances.

    Attributes:
        user: User whose password history this records
        password_hash: Hashed password from history
        created_at: When this password was set
    """

    class Meta:
        # model = PasswordHistory  # Uncomment when model exists
        model = "core.PasswordHistory"

    user = SubFactory(UserFactory)
    password_hash = Faker("sha256")
    created_at = LazyFunction(timezone.now)
