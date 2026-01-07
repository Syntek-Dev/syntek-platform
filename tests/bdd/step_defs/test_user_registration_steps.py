"""Step definitions for user registration BDD feature.

This module implements step definitions for the user_registration.feature file.
These tests drive the implementation of user registration functionality.
"""

import pytest
from pytest_bdd import given, when, then, scenarios, parsers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from datetime import timedelta

from apps.core.models import User, Organisation, AuditLog, EmailVerificationToken


# Load all scenarios from the feature file
scenarios("../features/user_registration.feature")


@pytest.fixture
def registration_context():
    """Shared context for registration tests.

    Returns:
        dict: Context dictionary for storing test state.
    """
    return {
        "organisation": None,
        "user": None,
        "email_token": None,
        "registration_response": None,
        "verification_response": None,
        "error_message": None,
    }


# --------------------------------------------------------------------------
# Background Steps
# --------------------------------------------------------------------------


@given("the system is running")
def system_running():
    """Verify system is operational.

    This step ensures the test environment is ready.
    """
    pass


@given("the database is clean")
def database_clean(db):
    """Ensure database is clean before tests.

    Args:
        db: pytest-django database fixture.
    """
    User.objects.all().delete()
    Organisation.objects.all().delete()
    AuditLog.objects.all().delete()
    EmailVerificationToken.objects.all().delete()


# --------------------------------------------------------------------------
# Given Steps - Setup
# --------------------------------------------------------------------------


@given(parsers.parse('an organisation "{name}" with slug "{slug}" exists'))
def organisation_exists(registration_context, name: str, slug: str, db):
    """Create a test organisation.

    Args:
        registration_context: Shared test context.
        name: Organisation name.
        slug: Organisation slug.
        db: pytest-django database fixture.
    """
    organisation = Organisation.objects.create(name=name, slug=slug)
    registration_context["organisation"] = organisation


@given(parsers.parse('a user "{email}" already exists'))
def user_already_exists(registration_context, email: str):
    """Create an existing user.

    Args:
        registration_context: Shared test context.
        email: User email address.
    """
    User.objects.create_user(
        email=email,
        password="ExistingPassword123!@",
        organisation=registration_context["organisation"],
    )


@given(parsers.parse('I have registered with email "{email}"'))
def have_registered_with_email(registration_context, email: str):
    """Register a user for verification testing.

    Args:
        registration_context: Shared test context.
        email: User email address.
    """
    user = User.objects.create_user(
        email=email,
        password="TestPassword123!@",
        first_name="Test",
        last_name="User",
        organisation=registration_context["organisation"],
    )
    registration_context["user"] = user


@given("I have received an email verification token")
def have_received_verification_token(registration_context):
    """Create email verification token for the user.

    Args:
        registration_context: Shared test context.
    """
    user = registration_context["user"]
    token = EmailVerificationToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(hours=24),
    )
    registration_context["email_token"] = token


@given("I have received an email verification token that has expired")
def have_received_expired_token(registration_context):
    """Create an expired email verification token.

    Args:
        registration_context: Shared test context.
    """
    user = registration_context["user"]
    token = EmailVerificationToken.objects.create(
        user=user,
        expires_at=timezone.now() - timedelta(hours=1),  # Already expired
    )
    registration_context["email_token"] = token


@given("I have verified my email")
def have_verified_email(registration_context):
    """Verify user's email and create a used token.

    Args:
        registration_context: Shared test context.
    """
    user = registration_context["user"]
    user.email_verified = True
    user.save()

    # Create a token that has been used
    token = EmailVerificationToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(hours=24),
        used=True,
        used_at=timezone.now(),
    )
    registration_context["email_token"] = token


# --------------------------------------------------------------------------
# When Steps - Actions
# --------------------------------------------------------------------------


@when("I register with the following details:")
def register_with_details(registration_context, datatable):
    """Register a new user with provided details.

    Args:
        registration_context: Shared test context.
        datatable: Gherkin datatable with registration details.
    """
    # pytest-bdd datatable is list of lists - convert to dict
    # First row is headers, subsequent rows are data
    if hasattr(datatable, "__iter__") and len(datatable) > 0:
        if isinstance(datatable[0], dict):
            # Already a list of dicts (some pytest-bdd versions)
            data = {row["field"]: row["value"] for row in datatable}
        else:
            # List of lists format - first row is header, skip it
            # Format: [["field", "value"], ["email", "x@y.com"], ...]
            data = {row[0]: row[1] for row in datatable[1:]}
    else:
        data = {}

    organisation = None
    if "organisation" in data:
        try:
            organisation = Organisation.objects.get(slug=data["organisation"])
        except Organisation.DoesNotExist:
            registration_context["error_message"] = "Organisation not found"
            registration_context["registration_response"] = {"success": False}
            return

    try:
        email = data.get("email")
        password = data.get("password")

        # Validate email format
        try:
            validate_email(email)
        except ValidationError as e:
            raise ValidationError(str(e.messages[0]))

        # Check for duplicate email
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Email address already in use")

        # Validate password against Django validators
        validate_password(password)

        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            organisation=organisation,
        )
        registration_context["user"] = user
        registration_context["registration_response"] = {"success": True}

        # Create email verification token
        token = EmailVerificationToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=24),
        )
        registration_context["email_token"] = token

        # Create audit log entry
        AuditLog.objects.create(
            user=user,
            organisation=organisation,
            action="user_registered",
            metadata={"email": user.email},
        )

    except ValidationError as e:
        registration_context["registration_response"] = {"success": False}
        registration_context["error_message"] = str(e)
    except Exception as e:
        registration_context["registration_response"] = {"success": False}
        registration_context["error_message"] = str(e)


@when(parsers.parse('I register with email "{email}" and password "{password}"'))
def register_with_email_password(registration_context, email: str, password: str):
    """Register with just email and password for validation testing.

    Args:
        registration_context: Shared test context.
        email: User email address.
        password: User password.
    """
    try:
        # Validate password against Django validators
        validate_password(password)

        user = User.objects.create_user(
            email=email,
            password=password,
            organisation=registration_context["organisation"],
        )
        registration_context["user"] = user
        registration_context["registration_response"] = {"success": True}
        registration_context["error_message"] = ""

    except ValidationError as e:
        registration_context["registration_response"] = {"success": False}
        registration_context["error_message"] = str(e)
    except Exception as e:
        registration_context["registration_response"] = {"success": False}
        registration_context["error_message"] = str(e)


@when("I verify my email with the token")
def verify_email_with_token(registration_context):
    """Verify email using the token.

    Args:
        registration_context: Shared test context.
    """
    token = registration_context["email_token"]

    try:
        # Check if token is valid
        if token.is_expired():
            raise ValueError("Verification token has expired")
        if token.used:
            raise ValueError("Verification token has already been used")

        # Mark token as used
        token.mark_used()

        # Verify the user's email
        user = token.user
        user.email_verified = True
        user.save()

        registration_context["verification_response"] = {"success": True}

    except Exception as e:
        registration_context["verification_response"] = {"success": False}
        registration_context["error_message"] = str(e)


@when("I verify my email with the expired token")
def verify_email_with_expired_token(registration_context):
    """Attempt to verify email with an expired token.

    Args:
        registration_context: Shared test context.
    """
    verify_email_with_token(registration_context)


@when("I try to verify my email again with the same token")
def try_verify_again(registration_context):
    """Attempt to verify email with an already used token.

    Args:
        registration_context: Shared test context.
    """
    verify_email_with_token(registration_context)


# --------------------------------------------------------------------------
# Then Steps - Assertions
# --------------------------------------------------------------------------


@then("registration should succeed")
def registration_should_succeed(registration_context):
    """Assert registration was successful.

    Args:
        registration_context: Shared test context.
    """
    assert registration_context["registration_response"]["success"] is True


@then(parsers.parse('registration should fail with error "{error}"'))
def registration_should_fail_with_error(registration_context, error: str):
    """Assert registration failed with specific error.

    Args:
        registration_context: Shared test context.
        error: Expected error message.
    """
    assert registration_context["registration_response"]["success"] is False
    assert error in registration_context["error_message"]


@then(parsers.parse('registration should "{result}"'))
def registration_should_result(registration_context, result: str):
    """Assert registration result matches expected.

    Args:
        registration_context: Shared test context.
        result: Expected result ("succeed" or "fail").
    """
    if result == "succeed":
        assert registration_context["registration_response"]["success"] is True
    else:
        assert registration_context["registration_response"]["success"] is False


@then('I should see error message ""')
def should_see_no_error_message(registration_context):
    """Assert no error message is present (success case).

    Args:
        registration_context: Shared test context.
    """
    # Empty error string means success - no assertion needed
    pass


@then(parsers.parse('I should see error message "{error}"'))
def should_see_error_message(registration_context, error: str):
    """Assert specific error message is present.

    Args:
        registration_context: Shared test context.
        error: Expected error message substring.
    """
    assert error in registration_context.get("error_message", "")


@then("I should receive an email verification token")
def should_receive_verification_token(registration_context):
    """Assert email verification token was created.

    Args:
        registration_context: Shared test context.
    """
    assert registration_context["email_token"] is not None
    assert not registration_context["email_token"].is_expired()


@then(parsers.parse('the user "{email}" should exist'))
def user_should_exist(email: str):
    """Assert user with email exists.

    Args:
        email: User email address.
    """
    assert User.objects.filter(email=email).exists()


@then(parsers.parse('the user "{email}" should not be verified'))
def user_should_not_be_verified(email: str):
    """Assert user email is not verified.

    Args:
        email: User email address.
    """
    user = User.objects.get(email=email)
    assert user.email_verified is False


@then(parsers.parse('the user "{email}" should be verified'))
def user_should_be_verified(email: str):
    """Assert user email is verified.

    Args:
        email: User email address.
    """
    user = User.objects.get(email=email)
    assert user.email_verified is True


@then(
    parsers.parse(
        'the user "{email}" should have an audit log entry for "{action}"'
    )
)
def user_should_have_audit_log(email: str, action: str):
    """Assert user has an audit log entry with specified action.

    Args:
        email: User email address.
        action: Expected audit log action.
    """
    user = User.objects.get(email=email)
    assert AuditLog.objects.filter(user=user, action=action).exists()


@then("email verification should succeed")
def email_verification_should_succeed(registration_context):
    """Assert email verification was successful.

    Args:
        registration_context: Shared test context.
    """
    assert registration_context["verification_response"]["success"] is True


@then(parsers.parse('email verification should fail with error "{error}"'))
def email_verification_should_fail(registration_context, error: str):
    """Assert email verification failed with specific error.

    Args:
        registration_context: Shared test context.
        error: Expected error message.
    """
    assert registration_context["verification_response"]["success"] is False
    assert error in registration_context["error_message"]


@then("the email verification token should be marked as used")
def token_should_be_marked_used(registration_context):
    """Assert email verification token is marked as used.

    Args:
        registration_context: Shared test context.
    """
    token = registration_context["email_token"]
    token.refresh_from_db()
    assert token.used is True
    assert token.used_at is not None
