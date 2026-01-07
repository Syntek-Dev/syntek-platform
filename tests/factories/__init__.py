"""Test factories package.

Contains factory-boy factories for creating test data.

These factories use model string references ("core.Model") which will work
once the models are properly registered with Django. During TDD RED phase,
the factories may fail until models are fully implemented.
"""

from tests.factories.user_factory import (
    OrganisationFactory,
    UserFactory,
    UserProfileFactory,
    AuditLogFactory,
)
from tests.factories.token_factory import (
    SessionTokenFactory,
    PasswordResetTokenFactory,
    EmailVerificationTokenFactory,
    TOTPDeviceFactory,
    PasswordHistoryFactory,
)

__all__ = [
    "OrganisationFactory",
    "UserFactory",
    "UserProfileFactory",
    "AuditLogFactory",
    "SessionTokenFactory",
    "PasswordResetTokenFactory",
    "EmailVerificationTokenFactory",
    "TOTPDeviceFactory",
    "PasswordHistoryFactory",
]
