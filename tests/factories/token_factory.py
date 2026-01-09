"""Token-related test factories.

This module contains factory-boy factories for creating token test data.
"""

import secrets
import uuid
from datetime import timedelta

from django.utils import timezone

import factory
from factory import Faker, LazyFunction, SubFactory
from factory.django import DjangoModelFactory

from apps.core.utils.token_hasher import TokenHasher
from tests.factories.user_factory import UserFactory


# Default plain token for testing - allows tests to use this known token
DEFAULT_TEST_TOKEN = "test_token_for_verification_12345678901234567890"


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

    The factory generates a plain token and stores its hash. Tests can access
    the plain token via the `plain_token` attribute after creation.

    Attributes:
        user: User requesting password reset
        token_hash: HMAC-SHA256 hash of the reset token
        expires_at: Token expiration timestamp (15 minutes)
        used: Whether token has been used
        used_at: Timestamp when token was used

    Example:
        token_obj = PasswordResetTokenFactory.create(user=user)
        plain_token = token_obj.plain_token  # Use this in reset mutation
    """

    class Meta:
        model = "core.PasswordResetToken"

    user = SubFactory(UserFactory)
    expires_at = LazyFunction(lambda: timezone.now() + timedelta(minutes=15))
    used = False
    used_at = None
    # Token fields are set in _create to ensure hash matches plain token

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create instance and store plain token for test access."""
        plain_token = kwargs.pop("plain_token", None) or secrets.token_urlsafe(48)
        kwargs["token"] = plain_token
        kwargs["token_hash"] = TokenHasher.hash_token(plain_token)
        obj = super()._create(model_class, *args, **kwargs)
        obj.plain_token = plain_token  # Store for test access
        return obj


class EmailVerificationTokenFactory(DjangoModelFactory):
    """Factory for creating test EmailVerificationToken instances.

    The factory generates a plain token and stores its hash. Tests can access
    the plain token via the `plain_token` attribute after creation.

    Attributes:
        user: User to verify email for
        token_hash: HMAC-SHA256 hash of the verification token
        expires_at: Token expiration timestamp (24 hours)
        used: Whether token has been used
        used_at: Timestamp when token was used

    Example:
        token_obj = EmailVerificationTokenFactory.create(user=user)
        plain_token = token_obj.plain_token  # Use this in verify mutation
    """

    class Meta:
        model = "core.EmailVerificationToken"

    user = SubFactory(UserFactory)
    expires_at = LazyFunction(lambda: timezone.now() + timedelta(hours=24))
    used = False
    used_at = None
    # Token fields are set in _create to ensure hash matches plain token

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create instance and store plain token for test access."""
        plain_token = kwargs.pop("plain_token", None) or secrets.token_urlsafe(48)
        kwargs["token"] = plain_token
        kwargs["token_hash"] = TokenHasher.hash_token(plain_token)
        obj = super()._create(model_class, *args, **kwargs)
        obj.plain_token = plain_token  # Store for test access
        return obj


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
