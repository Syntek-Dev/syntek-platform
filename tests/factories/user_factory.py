"""User-related test factories.

This module contains factory-boy factories for creating User and related test data.
"""

from django.utils import timezone

import factory
from factory import Faker, Sequence, SubFactory, post_generation
from factory.django import DjangoModelFactory

# TODO: Import actual models once implemented
# from apps.core.models import User, Organisation, UserProfile


class OrganisationFactory(DjangoModelFactory):
    """Factory for creating test Organisation instances.

    Attributes:
        name: Organisation name (auto-generated sequence)
        slug: URL-safe organisation identifier
        industry: Industry category
        is_active: Whether organisation is active
    """

    class Meta:
        # model = Organisation  # Uncomment when model exists
        model = "core.Organisation"

    name = Sequence(lambda n: f"Organisation {n}")
    slug = Sequence(lambda n: f"org-{n}")
    industry = Faker("random_element", elements=["technology", "finance", "retail", "healthcare"])
    is_active = True


class UserFactory(DjangoModelFactory):
    """Factory for creating test User instances.

    Attributes:
        email: Unique email address
        first_name: User's first name
        last_name: User's last name
        organisation: Foreign key to Organisation
        is_active: Whether user account is active
        is_staff: Whether user has staff permissions
        is_superuser: Whether user has all permissions
        email_verified: Whether email is verified
        two_factor_enabled: Whether 2FA is enabled
        has_email_account: Whether user has email service access
        has_vault_access: Whether user has vault access
    """

    class Meta:
        # model = User  # Uncomment when model exists
        model = "core.User"

    email = Faker("email")
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    organisation = SubFactory(OrganisationFactory)
    is_active = True
    is_staff = False
    is_superuser = False
    email_verified = False
    two_factor_enabled = False
    has_email_account = False
    has_vault_access = False
    password_changed_at = factory.LazyFunction(timezone.now)

    @post_generation
    def password(self, create, extracted, **kwargs):
        """Set password after user creation.

        Args:
            create: Whether to save the instance
            extracted: Password value if provided
            kwargs: Additional keyword arguments
        """
        if not create:
            return

        if extracted:
            self.set_password(extracted)
        else:
            self.set_password("TestPassword123!@")  # Default secure password


class UserProfileFactory(DjangoModelFactory):
    """Factory for creating test UserProfile instances.

    Attributes:
        user: OneToOne relationship to User
        phone: User's phone number (matches UserProfile model field name)
        avatar: Profile picture URL/path
    """

    class Meta:
        # model = UserProfile  # Uncomment when model exists
        model = "core.UserProfile"

    user = SubFactory(UserFactory)
    phone = Faker("phone_number")
    avatar = ""  # Empty string to match model default


class AuditLogFactory(DjangoModelFactory):
    """Factory for creating test AuditLog instances.

    Attributes:
        user: User who performed the action
        organisation: Organisation context for the action
        action: Action type (e.g., login, logout, password_change)
        ip_address: Encrypted IP address
        user_agent: Browser user agent string
        metadata: Additional action metadata as JSON
    """

    class Meta:
        # model = AuditLog  # Uncomment when model exists
        model = "core.AuditLog"

    user = SubFactory(UserFactory)
    organisation = factory.SelfAttribute("user.organisation")
    action = Faker("random_element", elements=["login", "logout", "password_change", "2fa_enabled"])
    ip_address = factory.LazyFunction(
        lambda: __import__(
            "apps.core.utils.encryption", fromlist=["IPEncryption"]
        ).IPEncryption.encrypt_ip("127.0.0.1")
    )
    user_agent = Faker("user_agent")
    metadata = factory.Dict({})
