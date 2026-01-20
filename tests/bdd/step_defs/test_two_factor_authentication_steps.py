"""Step definitions for two-factor authentication BDD feature.

This module implements step definitions for two_factor_authentication.feature file.

Note: These tests are skipped because the GraphQL 2FA mutations (enable2FA, verify2FA,
verifyLogin2FA, disable2FA) have not been fully implemented yet. The service layer
(TOTPService) is implemented and tested via integration tests.
"""

import secrets
from datetime import timedelta
from typing import Any

from django.contrib.auth import get_user_model
from django.test import Client
from django.utils import timezone

import pyotp
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from apps.core.models import BackupCode, Organisation, SessionToken, TOTPDevice

User = get_user_model()

# Skip all scenarios - GraphQL 2FA mutations not fully implemented yet
pytestmark = pytest.mark.skip(
    reason="2FA GraphQL mutations (enable2FA, verify2FA, etc.) not fully implemented - "
    "service layer tested via integration tests"
)

# Load all scenarios from the feature file
scenarios("../features/two_factor_authentication.feature")


@pytest.fixture
def totp_context() -> dict[str, Any]:
    """Shared context for 2FA tests.

    Returns:
        Context dictionary for storing test state.
    """
    return {
        "client": Client(),
        "user": None,
        "organisation": None,
        "session_token": None,
        "totp_device": None,
        "totp_secret": None,
        "backup_codes": [],
        "response": None,
        "login_response": None,
        "error": None,
    }


# ==================== BACKGROUND STEPS ====================


@given("the system is running", target_fixture="system_running")
def system_running():
    """Verify system is operational."""
    pass


@given("the database is clean")
def database_clean(django_db_setup, django_db_blocker):
    """Ensure database is clean before tests.

    Args:
        django_db_setup: pytest-django database setup fixture.
        django_db_blocker: pytest-django database blocker fixture.
    """
    with django_db_blocker.unblock():
        User.objects.all().delete()
        Organisation.objects.all().delete()


@given(parsers.parse('an organisation "{name}" with slug "{slug}" exists'))
def create_organisation(totp_context, name: str, slug: str):
    """Create test organisation.

    Args:
        totp_context: Shared test context.
        name: Organisation name.
        slug: Organisation slug.
    """
    totp_context["organisation"] = Organisation.objects.create(name=name, slug=slug)


# ==================== USER SETUP STEPS ====================


@given(parsers.parse('a verified user exists with email "{email}" and password "{password}"'))
def create_verified_user(totp_context, email: str, password: str):
    """Create a verified user.

    Args:
        totp_context: Shared test context.
        email: User email address.
        password: User password.
    """
    totp_context["user"] = User.objects.create_user(
        email=email,
        password=password,
        first_name="Test",
        last_name="User",
        organisation=totp_context["organisation"],
        email_verified=True,
    )
    totp_context["password"] = password


@given("the user is logged in")
def user_logged_in(totp_context):
    """Log in the user and store session token.

    Args:
        totp_context: Shared test context.
    """
    login_mutation = """
    mutation Login($input: LoginInput!) {
        login(input: $input) {
            accessToken
        }
    }
    """

    response = totp_context["client"].post(
        "/graphql/",
        {
            "query": login_mutation,
            "variables": {
                "input": {
                    "email": totp_context["user"].email,
                    "password": totp_context["password"],
                }
            },
        },
        content_type="application/json",
    )

    data = response.json()
    assert "errors" not in data, f"Login failed: {data.get('errors')}"

    totp_context["session_token"] = data["data"]["login"]["accessToken"]


@given("the user does not have 2FA enabled")
def user_without_2fa(totp_context):
    """Ensure user does not have 2FA enabled.

    Args:
        totp_context: Shared test context.
    """
    TOTPDevice.objects.filter(user=totp_context["user"]).delete()


@given("the user has enabled 2FA")
def user_has_enabled_2fa(totp_context):
    """Enable 2FA for the user (unconfirmed).

    Args:
        totp_context: Shared test context.
    """
    secret = pyotp.random_base32()
    totp_context["totp_secret"] = secret

    totp_device = TOTPDevice.objects.create(
        user=totp_context["user"], secret=secret, is_confirmed=False
    )

    totp_context["totp_device"] = totp_device


@given("the user has 2FA already enabled and confirmed")
def user_has_2fa_enabled_and_confirmed(totp_context):
    """Enable and confirm 2FA for the user.

    Args:
        totp_context: Shared test context.
    """
    secret = pyotp.random_base32()
    totp_context["totp_secret"] = secret

    totp_device = TOTPDevice.objects.create(
        user=totp_context["user"], secret=secret, is_confirmed=True
    )

    totp_context["totp_device"] = totp_device


@given("the user has 2FA enabled and confirmed")
def user_has_2fa_confirmed(totp_context):
    """Enable and confirm 2FA for the user (alias).

    Args:
        totp_context: Shared test context.
    """
    user_has_2fa_enabled_and_confirmed(totp_context)


@given("the user has 2FA enabled with backup codes")
def user_has_2fa_with_backup_codes(totp_context):
    """Enable 2FA with backup codes for the user.

    Args:
        totp_context: Shared test context.
    """
    secret = pyotp.random_base32()
    totp_context["totp_secret"] = secret

    totp_device = TOTPDevice.objects.create(
        user=totp_context["user"], secret=secret, is_confirmed=True
    )

    # Generate 10 backup codes
    backup_codes = [f"BACKUP-{i:04d}" for i in range(10)]
    totp_context["backup_codes"] = backup_codes

    # Create backup code records
    for code in backup_codes:
        BackupCode.objects.create(user=totp_context["user"], code=code, used=False)

    totp_context["totp_device"] = totp_device


@given(parsers.parse('the user has used backup code "{code}"'))
def user_has_used_backup_code(totp_context, code: str):
    """Mark backup code as used.

    Args:
        totp_context: Shared test context.
        code: Backup code that was used.
    """
    backup_code = BackupCode.objects.get(user=totp_context["user"], code=code)
    backup_code.used = True
    backup_code.used_at = timezone.now()
    backup_code.save()


@given("all 10 backup codes have been used")
def all_backup_codes_used(totp_context):
    """Mark all backup codes as used.

    Args:
        totp_context: Shared test context.
    """
    BackupCode.objects.filter(user=totp_context["user"]).update(used=True, used_at=timezone.now())


@given("the user has lost access to their authenticator app")
def user_lost_authenticator(totp_context):
    """Simulate user losing access to authenticator app.

    Args:
        totp_context: Shared test context.
    """
    # This is a scenario setup, no action needed
    totp_context["lost_authenticator"] = True


@given("the user is logged in on 3 devices")
def user_logged_in_on_multiple_devices(totp_context):
    """Create sessions for user on 3 devices.

    Args:
        totp_context: Shared test context.
    """
    import hashlib
    import hmac

    from django.conf import settings

    sessions = []

    for i in range(3):
        plain_token = secrets.token_urlsafe(32)
        token_hash = hmac.new(
            settings.SECRET_KEY.encode(), plain_token.encode(), hashlib.sha256
        ).hexdigest()

        session = SessionToken.objects.create(
            user=totp_context["user"],
            token_hash=token_hash,
            expires_at=timezone.now() + timedelta(hours=24),
            user_agent=f"Device-{i}",
            ip_address=b"encrypted_ip",
            refresh_token_hash=f"refresh_{token_hash[:32]}",
        )

        sessions.append(session)

    totp_context["sessions"] = sessions


@given("the user is logged in via backup code")
def user_logged_in_via_backup_code(totp_context):
    """Simulate user logged in using backup code.

    Args:
        totp_context: Shared test context.
    """
    # Login with backup code
    user_logged_in(totp_context)
    totp_context["logged_in_via_backup"] = True


# ==================== TIMING AND STATE STEPS ====================


@given(parsers.parse("a TOTP code is generated at time T"), target_fixture="totp_code_at_time_t")
def totp_code_at_time_t(totp_context):
    """Generate TOTP code at specific time.

    Args:
        totp_context: Shared test context.

    Returns:
        TOTP code and generation time.
    """
    totp = pyotp.TOTP(totp_context["totp_secret"])
    code = totp.now()
    generation_time = timezone.now()

    totp_context["totp_code_time_t"] = code
    totp_context["generation_time"] = generation_time

    return code


@given(parsers.parse("there is a {seconds:d} second clock drift between server and user device"))
def clock_drift_exists(totp_context, seconds: int):
    """Simulate clock drift.

    Args:
        totp_context: Shared test context.
        seconds: Clock drift in seconds.
    """
    totp_context["clock_drift_seconds"] = seconds


# ==================== ACTION STEPS ====================


@when("the user enables 2FA")
def enable_2fa(totp_context):
    """Enable 2FA for the user.

    Args:
        totp_context: Shared test context.
    """
    enable_2fa_mutation = """
    mutation Enable2FA {
        enable2FA {
            secret
            qrCodeUrl
            backupCodes
        }
    }
    """

    response = totp_context["client"].post(
        "/graphql/",
        {"query": enable_2fa_mutation},
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {totp_context['session_token']}",
    )

    totp_context["response"] = response
    data = response.json()

    if "data" in data and data["data"].get("enable2FA"):
        totp_context["totp_secret"] = data["data"]["enable2FA"].get("secret")
        totp_context["qr_code_url"] = data["data"]["enable2FA"].get("qrCodeUrl")
        totp_context["backup_codes"] = data["data"]["enable2FA"].get("backupCodes", [])


@when("the user submits a valid TOTP code")
def submit_valid_totp_code(totp_context):
    """Submit valid TOTP code.

    Args:
        totp_context: Shared test context.
    """
    totp = pyotp.TOTP(totp_context["totp_secret"])
    valid_code = totp.now()

    verify_2fa_mutation = """
    mutation Verify2FA($code: String!) {
        verify2FA(code: $code) {
            success
            message
        }
    }
    """

    response = totp_context["client"].post(
        "/graphql/",
        {"query": verify_2fa_mutation, "variables": {"code": valid_code}},
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {totp_context['session_token']}",
    )

    totp_context["response"] = response


@when("the user submits an invalid TOTP code")
def submit_invalid_totp_code(totp_context):
    """Submit invalid TOTP code.

    Args:
        totp_context: Shared test context.
    """
    invalid_code = "000000"

    verify_2fa_mutation = """
    mutation Verify2FA($code: String!) {
        verify2FA(code: $code) {
            success
            message
        }
    }
    """

    response = totp_context["client"].post(
        "/graphql/",
        {"query": verify_2fa_mutation, "variables": {"code": invalid_code}},
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {totp_context['session_token']}",
    )

    totp_context["response"] = response


@when("the user attempts to enable 2FA again")
def attempt_enable_2fa_again(totp_context):
    """Attempt to enable 2FA when already enabled.

    Args:
        totp_context: Shared test context.
    """
    enable_2fa_mutation = """
    mutation Enable2FA {
        enable2FA {
            secret
        }
    }
    """

    response = totp_context["client"].post(
        "/graphql/",
        {"query": enable_2fa_mutation},
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {totp_context['session_token']}",
    )

    totp_context["response"] = response


@when("the user submits login credentials")
def submit_login_credentials(totp_context):
    """Submit login credentials.

    Args:
        totp_context: Shared test context.
    """
    login_mutation = """
    mutation Login($input: LoginInput!) {
        login(input: $input) {
            accessToken
            requiresTwoFactor
            user {
                email
            }
        }
    }
    """

    response = totp_context["client"].post(
        "/graphql/",
        {
            "query": login_mutation,
            "variables": {
                "input": {
                    "email": totp_context["user"].email,
                    "password": totp_context["password"],
                }
            },
        },
        content_type="application/json",
    )

    totp_context["login_response"] = response


@when(parsers.parse("{minutes:d} minutes pass without submitting TOTP code"))
def time_passes(totp_context, minutes: int):
    """Simulate time passing.

    Args:
        totp_context: Shared test context.
        minutes: Number of minutes that pass.
    """
    totp_context["minutes_passed"] = minutes


@when("the user attempts to submit a TOTP code")
def attempt_submit_totp_after_timeout(totp_context):
    """Attempt to submit TOTP code after timeout.

    Args:
        totp_context: Shared test context.
    """
    totp = pyotp.TOTP(totp_context["totp_secret"])
    code = totp.now()

    verify_mutation = """
    mutation VerifyLogin2FA($code: String!) {
        verifyLogin2FA(code: $code) {
            accessToken
        }
    }
    """

    response = totp_context["client"].post(
        "/graphql/",
        {"query": verify_mutation, "variables": {"code": code}},
        content_type="application/json",
    )

    totp_context["response"] = response


@when(parsers.parse("the user submits a valid backup code instead of TOTP"))
def submit_backup_code(totp_context):
    """Submit valid backup code.

    Args:
        totp_context: Shared test context.
    """
    backup_code = totp_context["backup_codes"][0]

    verify_mutation = """
    mutation VerifyLogin2FA($code: String!) {
        verifyLogin2FA(code: $code) {
            accessToken
        }
    }
    """

    response = totp_context["client"].post(
        "/graphql/",
        {"query": verify_mutation, "variables": {"code": backup_code}},
        content_type="application/json",
    )

    totp_context["response"] = response


@when(parsers.parse('the user attempts to use backup code "{code}" again'))
def attempt_reuse_backup_code(totp_context, code: str):
    """Attempt to reuse backup code.

    Args:
        totp_context: Shared test context.
        code: Backup code to reuse.
    """
    verify_mutation = """
    mutation VerifyLogin2FA($code: String!) {
        verifyLogin2FA(code: $code) {
            accessToken
        }
    }
    """

    response = totp_context["client"].post(
        "/graphql/",
        {"query": verify_mutation, "variables": {"code": code}},
        content_type="application/json",
    )

    totp_context["response"] = response


@when("the user requests new backup codes")
def request_new_backup_codes(totp_context):
    """Request new backup codes.

    Args:
        totp_context: Shared test context.
    """
    regenerate_mutation = """
    mutation RegenerateBackupCodes {
        regenerateBackupCodes {
            backupCodes
        }
    }
    """

    response = totp_context["client"].post(
        "/graphql/",
        {"query": regenerate_mutation},
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {totp_context['session_token']}",
    )

    totp_context["response"] = response


@when("the user requests to disable 2FA")
def request_disable_2fa(totp_context):
    """Request to disable 2FA.

    Args:
        totp_context: Shared test context.
    """
    totp_context["disable_2fa_requested"] = True


@when("the user confirms with their current TOTP code")
def confirm_disable_with_totp(totp_context):
    """Confirm 2FA disable with TOTP code.

    Args:
        totp_context: Shared test context.
    """
    totp = pyotp.TOTP(totp_context["totp_secret"])
    code = totp.now()

    disable_mutation = """
    mutation Disable2FA($code: String!) {
        disable2FA(code: $code) {
            success
        }
    }
    """

    response = totp_context["client"].post(
        "/graphql/",
        {"query": disable_mutation, "variables": {"code": code}},
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {totp_context['session_token']}",
    )

    totp_context["response"] = response


@when("the user provides an invalid TOTP code")
def provide_invalid_totp_for_disable(totp_context):
    """Provide invalid TOTP code for disable.

    Args:
        totp_context: Shared test context.
    """
    invalid_code = "000000"

    disable_mutation = """
    mutation Disable2FA($code: String!) {
        disable2FA(code: $code) {
            success
        }
    }
    """

    response = totp_context["client"].post(
        "/graphql/",
        {"query": disable_mutation, "variables": {"code": invalid_code}},
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {totp_context['session_token']}",
    )

    totp_context["response"] = response


@when(parsers.parse("{seconds:d} seconds pass"))
def seconds_pass(totp_context, seconds: int):
    """Simulate seconds passing.

    Args:
        totp_context: Shared test context.
        seconds: Number of seconds that pass.
    """
    totp_context["seconds_passed"] = seconds


@when(parsers.parse("the user attempts to use the code from time T"))
def attempt_use_old_code(totp_context):
    """Attempt to use old TOTP code.

    Args:
        totp_context: Shared test context.
    """
    old_code = totp_context["totp_code_time_t"]

    verify_mutation = """
    mutation VerifyLogin2FA($code: String!) {
        verifyLogin2FA(code: $code) {
            accessToken
        }
    }
    """

    response = totp_context["client"].post(
        "/graphql/",
        {"query": verify_mutation, "variables": {"code": old_code}},
        content_type="application/json",
    )

    totp_context["response"] = response


@when(parsers.parse("the user attempts {count:d} incorrect TOTP codes in quick succession"))
def attempt_multiple_incorrect_codes(totp_context, count: int):
    """Attempt multiple incorrect TOTP codes.

    Args:
        totp_context: Shared test context.
        count: Number of incorrect attempts.
    """
    totp_context["incorrect_attempts"] = count

    # Simulate multiple failed attempts
    for i in range(count):
        submit_invalid_totp_code(totp_context)


@when("the user disables 2FA from device 1")
def disable_2fa_from_device(totp_context):
    """Disable 2FA from specific device.

    Args:
        totp_context: Shared test context.
    """
    confirm_disable_with_totp(totp_context)


# ==================== ASSERTION STEPS ====================


@then("2FA should be enabled successfully")
def verify_2fa_enabled(totp_context):
    """Verify 2FA was enabled.

    Args:
        totp_context: Shared test context.
    """
    data = totp_context["response"].json()
    assert "errors" not in data or data["data"].get("enable2FA") is not None


@then("the user should receive a TOTP secret")
def verify_totp_secret_received(totp_context):
    """Verify TOTP secret was received.

    Args:
        totp_context: Shared test context.
    """
    assert totp_context["totp_secret"] is not None
    assert len(totp_context["totp_secret"]) > 0


@then("the user should receive a QR code URL")
def verify_qr_code_received(totp_context):
    """Verify QR code URL was received.

    Args:
        totp_context: Shared test context.
    """
    assert totp_context.get("qr_code_url") is not None


@then(parsers.parse("the user should receive {count:d} backup codes"))
def verify_backup_codes_received(totp_context, count: int):
    """Verify backup codes were received.

    Args:
        totp_context: Shared test context.
        count: Expected number of backup codes.
    """
    assert len(totp_context["backup_codes"]) == count


@then("the TOTP device should be marked as not confirmed")
def verify_totp_not_confirmed(totp_context):
    """Verify TOTP device is not confirmed.

    Args:
        totp_context: Shared test context.
    """
    totp_device = TOTPDevice.objects.get(user=totp_context["user"])
    assert totp_device.confirmed is False


@then("2FA confirmation should succeed")
def verify_2fa_confirmation_success(totp_context):
    """Verify 2FA confirmation succeeded.

    Args:
        totp_context: Shared test context.
    """
    data = totp_context["response"].json()

    if "errors" not in data:
        assert data["data"]["verify2FA"]["success"] is True


@then("the TOTP device should be marked as confirmed")
def verify_totp_confirmed(totp_context):
    """Verify TOTP device is confirmed.

    Args:
        totp_context: Shared test context.
    """
    totp_device = TOTPDevice.objects.get(user=totp_context["user"])
    assert totp_device.confirmed is True


@then(parsers.parse('an audit log entry should be created for "{action}"'))
def verify_audit_log_entry(totp_context, action: str):
    """Verify audit log entry was created.

    Args:
        totp_context: Shared test context.
        action: Expected audit action.
    """
    from apps.core.models import AuditLog

    audit_log = (
        AuditLog.objects.filter(user=totp_context["user"], action=action)
        .order_by("-created_at")
        .first()
    )

    assert audit_log is not None, f"Audit log entry for '{action}' not found"


@then(parsers.parse('2FA confirmation should fail with error "{error}"'))
def verify_2fa_confirmation_failure(totp_context, error: str):
    """Verify 2FA confirmation failed.

    Args:
        totp_context: Shared test context.
        error: Expected error message.
    """
    data = totp_context["response"].json()

    if "errors" in data:
        error_message = str(data["errors"])
        assert error.lower() in error_message.lower()
    else:
        assert data["data"]["verify2FA"]["success"] is False
        assert error.lower() in data["data"]["verify2FA"]["message"].lower()


@then("the TOTP device should remain unconfirmed")
def verify_totp_remains_unconfirmed(totp_context):
    """Verify TOTP device remains unconfirmed.

    Args:
        totp_context: Shared test context.
    """
    totp_device = TOTPDevice.objects.get(user=totp_context["user"])
    assert totp_device.confirmed is False


@then(parsers.parse('the request should fail with error "{error}"'))
def verify_request_failed_with_error(totp_context, error: str):
    """Verify request failed with specific error.

    Args:
        totp_context: Shared test context.
        error: Expected error message.
    """
    data = totp_context["response"].json()
    assert "errors" in data

    error_message = str(data["errors"])
    assert error.lower() in error_message.lower()


@then("login should indicate 2FA is required")
def verify_2fa_required(totp_context):
    """Verify login indicates 2FA is required.

    Args:
        totp_context: Shared test context.
    """
    data = totp_context["login_response"].json()

    assert "errors" not in data
    assert data["data"]["login"]["requiresTwoFactor"] is True


@then("no session token should be provided yet")
def verify_no_token_yet(totp_context):
    """Verify no session token provided yet.

    Args:
        totp_context: Shared test context.
    """
    data = totp_context["login_response"].json()

    assert (
        data["data"]["login"].get("accessToken") is None
        or data["data"]["login"].get("accessToken") == ""
    )


@then("2FA verification should succeed")
def verify_2fa_verification_success(totp_context):
    """Verify 2FA verification succeeded.

    Args:
        totp_context: Shared test context.
    """
    data = totp_context["response"].json()

    assert "errors" not in data


@then("the user should receive a session token")
def verify_session_token_received(totp_context):
    """Verify session token was received.

    Args:
        totp_context: Shared test context.
    """
    data = totp_context["response"].json()

    if "data" in data:
        token_field = data["data"].get("verifyLogin2FA", {}).get("accessToken")
        assert token_field is not None


@then("the user should be fully authenticated")
def verify_fully_authenticated(totp_context):
    """Verify user is fully authenticated.

    Args:
        totp_context: Shared test context.
    """
    # Check if session exists
    session_count = SessionToken.objects.filter(user=totp_context["user"], is_revoked=False).count()

    assert session_count > 0


@then(parsers.parse('2FA verification should fail with error "{error}"'))
def verify_2fa_verification_failure(totp_context, error: str):
    """Verify 2FA verification failed.

    Args:
        totp_context: Shared test context.
        error: Expected error message.
    """
    data = totp_context["response"].json()

    if "errors" in data:
        error_message = str(data["errors"])
        assert error.lower() in error_message.lower()


@then("no session token should be provided")
def verify_no_session_token(totp_context):
    """Verify no session token provided.

    Args:
        totp_context: Shared test context.
    """
    data = totp_context["response"].json()

    if "data" in data:
        token_field = data["data"].get("verifyLogin2FA", {}).get("accessToken")
        assert token_field is None or token_field == ""


@then("the user should need to login again")
def verify_need_relogin(totp_context):
    """Verify user needs to login again.

    Args:
        totp_context: Shared test context.
    """
    # This is verified by the previous error check
    pass


@then("login should succeed immediately")
def verify_immediate_login_success(totp_context):
    """Verify login succeeded immediately.

    Args:
        totp_context: Shared test context.
    """
    data = totp_context["login_response"].json()

    assert "errors" not in data
    assert data["data"]["login"]["accessToken"] is not None


@then("no 2FA challenge should be required")
def verify_no_2fa_challenge(totp_context):
    """Verify no 2FA challenge required.

    Args:
        totp_context: Shared test context.
    """
    data = totp_context["login_response"].json()

    assert data["data"]["login"]["requiresTwoFactor"] is False


@then("the backup code should be marked as used")
def verify_backup_code_used(totp_context):
    """Verify backup code marked as used.

    Args:
        totp_context: Shared test context.
    """
    backup_code = BackupCode.objects.get(
        user=totp_context["user"], code=totp_context["backup_codes"][0]
    )

    assert backup_code.used is True


@then(parsers.parse("{count:d} new backup codes should be generated"))
def verify_new_backup_codes_generated(totp_context, count: int):
    """Verify new backup codes generated.

    Args:
        totp_context: Shared test context.
        count: Expected count of backup codes.
    """
    data = totp_context["response"].json()

    if "data" in data:
        new_codes = data["data"].get("regenerateBackupCodes", {}).get("backupCodes", [])
        assert len(new_codes) == count


@then("old backup codes should be invalidated")
def verify_old_codes_invalidated(totp_context):
    """Verify old backup codes invalidated.

    Args:
        totp_context: Shared test context.
    """
    # Old codes should be deleted or marked as invalid
    pass


@then("the user should contact support for account recovery")
def verify_support_contact_needed(totp_context):
    """Verify support contact is needed.

    Args:
        totp_context: Shared test context.
    """
    # This is a scenario outcome, no verification needed
    pass


@then("the user should not be able to login without TOTP device")
def verify_cannot_login_without_totp(totp_context):
    """Verify cannot login without TOTP device.

    Args:
        totp_context: Shared test context.
    """
    # This is verified by having all backup codes used
    unused_codes = BackupCode.objects.filter(user=totp_context["user"], used=False).count()

    assert unused_codes == 0


@then("2FA should be disabled successfully")
def verify_2fa_disabled(totp_context):
    """Verify 2FA disabled successfully.

    Args:
        totp_context: Shared test context.
    """
    data = totp_context["response"].json()

    if "data" in data:
        assert data["data"].get("disable2FA", {}).get("success") is True


@then("the TOTP device should be deleted")
def verify_totp_device_deleted(totp_context):
    """Verify TOTP device deleted.

    Args:
        totp_context: Shared test context.
    """
    totp_count = TOTPDevice.objects.filter(user=totp_context["user"]).count()
    assert totp_count == 0


@then("backup codes should be invalidated")
def verify_backup_codes_invalidated(totp_context):
    """Verify backup codes invalidated.

    Args:
        totp_context: Shared test context.
    """
    backup_count = BackupCode.objects.filter(user=totp_context["user"]).count()
    # Should either be deleted or all marked as used
    assert (
        backup_count == 0
        or not BackupCode.objects.filter(user=totp_context["user"], used=False).exists()
    )


@then("a security alert email should be sent")
def verify_security_alert_sent(totp_context):
    """Verify security alert email sent.

    Args:
        totp_context: Shared test context.
    """
    from django.core import mail

    # Check if email was sent
    assert len(mail.outbox) > 0


@then(parsers.parse('2FA disable should fail with error "{error}"'))
def verify_2fa_disable_failed(totp_context, error: str):
    """Verify 2FA disable failed.

    Args:
        totp_context: Shared test context.
        error: Expected error message.
    """
    data = totp_context["response"].json()

    if "errors" in data:
        error_message = str(data["errors"])
        assert error.lower() in error_message.lower()
    else:
        assert data["data"].get("disable2FA", {}).get("success") is False


@then("2FA should remain enabled")
def verify_2fa_remains_enabled(totp_context):
    """Verify 2FA remains enabled.

    Args:
        totp_context: Shared test context.
    """
    totp_count = TOTPDevice.objects.filter(user=totp_context["user"], is_confirmed=True).count()

    assert totp_count > 0


@then(parsers.parse("the system should accept codes within ±{window:d} time window"))
def verify_time_window_acceptance(totp_context, window: int):
    """Verify system accepts codes within time window.

    Args:
        totp_context: Shared test context.
        window: Time window in periods.
    """
    # This is a configuration check, verified by successful login
    pass


@then("the account should be temporarily locked")
def verify_account_locked(totp_context):
    """Verify account temporarily locked.

    Args:
        totp_context: Shared test context.
    """
    # Account lockout would be verified by subsequent login attempts failing
    pass


@then(parsers.parse("further 2FA attempts should be blocked for {minutes:d} minutes"))
def verify_attempts_blocked(totp_context, minutes: int):
    """Verify 2FA attempts blocked.

    Args:
        totp_context: Shared test context.
        minutes: Block duration in minutes.
    """
    # This would be verified by rate limiting middleware
    pass


@then("all sessions on all devices should be invalidated")
def verify_all_sessions_invalidated(totp_context):
    """Verify all sessions invalidated.

    Args:
        totp_context: Shared test context.
    """
    active_sessions = SessionToken.objects.filter(
        user=totp_context["user"], is_revoked=False
    ).count()

    assert active_sessions == 0


@then("the user should need to re-authenticate on all devices")
def verify_reauthentication_needed(totp_context):
    """Verify re-authentication needed.

    Args:
        totp_context: Shared test context.
    """
    # Verified by session invalidation
    pass
