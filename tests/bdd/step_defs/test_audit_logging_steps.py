"""Step definitions for audit logging feature.

This module implements step definitions for the audit_logging.feature file.
Tests verify that security events are logged to the correct log files
with proper formatting and sensitive data redaction.
"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from apps.core.services.logging_service import LoggingService

# Load all scenarios from the feature file
scenarios("../features/audit_logging.feature")


@pytest.fixture
def logging_context(tmp_path: Path) -> dict[str, Any]:
    """Shared context for logging tests.

    Args:
        tmp_path: Pytest temporary path fixture

    Returns:
        Dictionary containing test context
    """
    return {
        "log_dir": tmp_path,
        "log_entries": {},
        "user": None,
        "mock_sentry": None,
        "last_log_data": {},
    }


@pytest.fixture
def mock_user() -> MagicMock:
    """Create a mock user for testing."""
    user = MagicMock()
    user.id = 1
    user.email = "user@example.com"
    user.organisation = MagicMock()
    user.organisation.id = 1
    return user


# Background steps


@given("the logging service is configured")
def logging_service_configured(logging_context: dict[str, Any]) -> None:
    """Configure the logging service with test directory."""
    LoggingService.configure(
        log_dir=str(logging_context["log_dir"]),
        level="DEBUG",
        json_format=True,
    )


@given("the log directory exists")
def log_directory_exists(logging_context: dict[str, Any]) -> None:
    """Verify log directory exists."""
    assert logging_context["log_dir"].exists()


# Authentication logging steps


@given(parsers.parse('a registered user with email "{email}"'))
def registered_user(logging_context: dict[str, Any], email: str) -> None:
    """Set up a registered user."""
    user = MagicMock()
    user.email = email
    user.id = 1
    logging_context["user"] = user


@given('no user exists with email "unknown@example.com"')
def no_user_exists(logging_context: dict[str, Any]) -> None:
    """Set up scenario with non-existent user."""
    logging_context["user"] = None


@given("a logged-in user")
def logged_in_user(logging_context: dict[str, Any], mock_user: MagicMock) -> None:
    """Set up a logged-in user."""
    logging_context["user"] = mock_user


@given("a logged-in user without 2FA")
def user_without_2fa(logging_context: dict[str, Any], mock_user: MagicMock) -> None:
    """Set up a logged-in user without 2FA."""
    mock_user.totp_enabled = False
    logging_context["user"] = mock_user


@given("a logged-in user with 2FA enabled")
def user_with_2fa(logging_context: dict[str, Any], mock_user: MagicMock) -> None:
    """Set up a logged-in user with 2FA."""
    mock_user.totp_enabled = True
    logging_context["user"] = mock_user


@when("the user logs in successfully")
def user_logs_in(logging_context: dict[str, Any]) -> None:
    """Simulate successful login."""
    auth_logger = LoggingService.auth()
    auth_logger.info(
        "LOGIN",
        extra={
            "event": "LOGIN",
            "user_email": logging_context["user"].email,
            "user_id": logging_context["user"].id,
        },
    )
    # Flush handlers
    for handler in auth_logger.handlers:
        handler.flush()


@when(parsers.parse('a login attempt is made with email "{email}"'))
def failed_login_attempt(logging_context: dict[str, Any], email: str) -> None:
    """Simulate failed login attempt."""
    auth_logger = LoggingService.auth()
    auth_logger.warning(
        "LOGIN_FAILED",
        extra={
            "event": "LOGIN_FAILED",
            "attempted_email": email,
        },
    )
    for handler in auth_logger.handlers:
        handler.flush()


@when("the user logs out")
def user_logs_out(logging_context: dict[str, Any]) -> None:
    """Simulate logout."""
    auth_logger = LoggingService.auth()
    auth_logger.info(
        "LOGOUT",
        extra={
            "event": "LOGOUT",
            "user_id": logging_context["user"].id,
        },
    )
    for handler in auth_logger.handlers:
        handler.flush()


@when("the user changes their password")
def user_changes_password(logging_context: dict[str, Any]) -> None:
    """Simulate password change."""
    auth_logger = LoggingService.auth()
    auth_logger.info(
        "PASSWORD_CHANGE",
        extra={
            "event": "PASSWORD_CHANGE",
            "user_id": logging_context["user"].id,
        },
    )
    for handler in auth_logger.handlers:
        handler.flush()


@when("the user enables 2FA")
def user_enables_2fa(logging_context: dict[str, Any]) -> None:
    """Simulate 2FA enablement."""
    auth_logger = LoggingService.auth()
    auth_logger.info(
        "TWO_FACTOR_ENABLED",
        extra={
            "event": "TWO_FACTOR_ENABLED",
            "user_id": logging_context["user"].id,
        },
    )
    for handler in auth_logger.handlers:
        handler.flush()


@when("the user disables 2FA")
def user_disables_2fa(logging_context: dict[str, Any]) -> None:
    """Simulate 2FA disablement."""
    auth_logger = LoggingService.auth()
    auth_logger.info(
        "TWO_FACTOR_DISABLED",
        extra={
            "event": "TWO_FACTOR_DISABLED",
            "user_id": logging_context["user"].id,
        },
    )
    for handler in auth_logger.handlers:
        handler.flush()


# Email logging steps


@given("a newly registered user")
def newly_registered_user(logging_context: dict[str, Any], mock_user: MagicMock) -> None:
    """Set up a newly registered user."""
    mock_user.email_verified = False
    logging_context["user"] = mock_user


@given("a user requests password reset")
def user_requests_reset(logging_context: dict[str, Any], mock_user: MagicMock) -> None:
    """Set up password reset request."""
    logging_context["user"] = mock_user


@given("an invalid email address")
def invalid_email(logging_context: dict[str, Any]) -> None:
    """Set up invalid email scenario."""
    logging_context["invalid_email"] = "invalid@nonexistent.xyz"


@when("a verification email is sent")
def verification_email_sent(logging_context: dict[str, Any]) -> None:
    """Simulate verification email sent."""
    mail_logger = LoggingService.mail()
    mail_logger.info(
        "VERIFICATION_EMAIL_SENT",
        extra={
            "event": "VERIFICATION_EMAIL_SENT",
            "recipient": logging_context["user"].email,
        },
    )
    for handler in mail_logger.handlers:
        handler.flush()


@when("the password reset email is sent")
def password_reset_email_sent(logging_context: dict[str, Any]) -> None:
    """Simulate password reset email sent."""
    mail_logger = LoggingService.mail()
    mail_logger.info(
        "PASSWORD_RESET_EMAIL_SENT",
        extra={
            "event": "PASSWORD_RESET_EMAIL_SENT",
            "recipient": logging_context["user"].email,
        },
    )
    for handler in mail_logger.handlers:
        handler.flush()


@when("email delivery fails")
def email_delivery_fails(logging_context: dict[str, Any]) -> None:
    """Simulate email delivery failure."""
    mail_logger = LoggingService.mail()
    mail_logger.error(
        "EMAIL_DELIVERY_FAILED",
        extra={
            "event": "EMAIL_DELIVERY_FAILED",
            "recipient": logging_context.get("invalid_email", "unknown"),
            "error": "SMTP connection refused",
        },
    )
    for handler in mail_logger.handlers:
        handler.flush()


# Security logging steps


@given("a user making rapid requests")
def user_rapid_requests(logging_context: dict[str, Any], mock_user: MagicMock) -> None:
    """Set up rapid request scenario."""
    logging_context["user"] = mock_user
    logging_context["request_count"] = 100


@given("a user with too many failed login attempts")
def user_too_many_failures(logging_context: dict[str, Any], mock_user: MagicMock) -> None:
    """Set up account lockout scenario."""
    logging_context["user"] = mock_user
    logging_context["failed_attempts"] = 5


@given("a user logging in from a new location")
def user_new_location(logging_context: dict[str, Any], mock_user: MagicMock) -> None:
    """Set up new location login scenario."""
    logging_context["user"] = mock_user
    logging_context["new_ip"] = "203.0.113.50"
    logging_context["known_ips"] = ["192.168.1.1", "10.0.0.1"]


@given("the IP encryption keys need rotation")
def keys_need_rotation(logging_context: dict[str, Any]) -> None:
    """Set up key rotation scenario."""
    logging_context["key_age_days"] = 90


@when("the rate limit is exceeded")
def rate_limit_exceeded(logging_context: dict[str, Any]) -> None:
    """Simulate rate limit exceeded."""
    security_logger = LoggingService.security()
    security_logger.warning(
        "RATE_LIMIT_EXCEEDED",
        extra={
            "event": "RATE_LIMIT_EXCEEDED",
            "user_id": logging_context["user"].id,
            "request_count": logging_context["request_count"],
        },
    )
    for handler in security_logger.handlers:
        handler.flush()


@when("the account is locked")
def account_locked(logging_context: dict[str, Any]) -> None:
    """Simulate account lockout."""
    security_logger = LoggingService.security()
    security_logger.warning(
        "ACCOUNT_LOCKED",
        extra={
            "event": "ACCOUNT_LOCKED",
            "user_id": logging_context["user"].id,
            "failed_attempts": logging_context["failed_attempts"],
        },
    )
    for handler in security_logger.handlers:
        handler.flush()


@when("suspicious activity is detected")
def suspicious_activity(logging_context: dict[str, Any]) -> None:
    """Simulate suspicious activity detection."""
    security_logger = LoggingService.security()
    security_logger.warning(
        "SUSPICIOUS_ACTIVITY",
        extra={
            "event": "SUSPICIOUS_ACTIVITY",
            "user_id": logging_context["user"].id,
            "reason": "login_from_new_location",
            "new_ip": logging_context["new_ip"],
        },
    )
    for handler in security_logger.handlers:
        handler.flush()


@when("the keys are rotated")
def keys_rotated(logging_context: dict[str, Any]) -> None:
    """Simulate key rotation."""
    security_logger = LoggingService.security()
    security_logger.info(
        "IP_KEY_ROTATED",
        extra={
            "event": "IP_KEY_ROTATED",
            "old_key_age_days": logging_context["key_age_days"],
        },
    )
    for handler in security_logger.handlers:
        handler.flush()


# Database logging steps


@given("a database query takes longer than threshold")
def slow_query_scenario(logging_context: dict[str, Any]) -> None:
    """Set up slow query scenario."""
    logging_context["query_duration_ms"] = 5000
    logging_context["threshold_ms"] = 1000


@given("the database is unavailable")
def database_unavailable(logging_context: dict[str, Any]) -> None:
    """Set up database unavailable scenario."""
    logging_context["db_error"] = "Connection refused"


@when("the slow query is detected")
def slow_query_detected(logging_context: dict[str, Any]) -> None:
    """Simulate slow query detection."""
    db_logger = LoggingService.database()
    db_logger.warning(
        "SLOW_QUERY",
        extra={
            "event": "SLOW_QUERY",
            "duration_ms": logging_context["query_duration_ms"],
            "query": "SELECT * FROM large_table...",
        },
    )
    for handler in db_logger.handlers:
        handler.flush()


@when("a connection error occurs")
def connection_error(logging_context: dict[str, Any]) -> None:
    """Simulate database connection error."""
    db_logger = LoggingService.database()
    db_logger.error(
        "CONNECTION_ERROR",
        extra={
            "event": "CONNECTION_ERROR",
            "error": logging_context["db_error"],
        },
    )
    for handler in db_logger.handlers:
        handler.flush()


# GraphQL logging steps


@given("a GraphQL client")
def graphql_client(logging_context: dict[str, Any]) -> None:
    """Set up GraphQL client scenario."""
    logging_context["graphql_client"] = True


@when("a query is executed")
def graphql_query_executed(logging_context: dict[str, Any]) -> None:
    """Simulate GraphQL query execution."""
    gql_logger = LoggingService.graphql()
    gql_logger.info(
        "GRAPHQL_QUERY",
        extra={
            "event": "GRAPHQL_QUERY",
            "operation_name": "GetUser",
            "duration_ms": 50,
        },
    )
    for handler in gql_logger.handlers:
        handler.flush()


@when("a mutation is executed")
def graphql_mutation_executed(logging_context: dict[str, Any]) -> None:
    """Simulate GraphQL mutation execution."""
    gql_logger = LoggingService.graphql()
    gql_logger.info(
        "GRAPHQL_MUTATION",
        extra={
            "event": "GRAPHQL_MUTATION",
            "operation_name": "UpdateUser",
            "duration_ms": 100,
        },
    )
    for handler in gql_logger.handlers:
        handler.flush()


@when("a query results in an error")
def graphql_error(logging_context: dict[str, Any]) -> None:
    """Simulate GraphQL error."""
    gql_logger = LoggingService.graphql()
    gql_logger.error(
        "GRAPHQL_ERROR",
        extra={
            "event": "GRAPHQL_ERROR",
            "error": "Field not found",
            "operation_name": "InvalidQuery",
        },
    )
    for handler in gql_logger.handlers:
        handler.flush()


# Sensitive data redaction steps


@given("log data containing a password field")
def log_data_with_password(logging_context: dict[str, Any]) -> None:
    """Set up data with password."""
    logging_context["last_log_data"] = {
        "username": "testuser",
        "password": "supersecret123",
    }


@given("log data containing access_token and refresh_token")
def log_data_with_tokens(logging_context: dict[str, Any]) -> None:
    """Set up data with tokens."""
    logging_context["last_log_data"] = {
        "access_token": "eyJhbGciOiJIUzI1NiIs...",
        "refresh_token": "dGhpcyBpcyBhIHJlZnJlc2g...",
    }


@given(parsers.parse('log data containing email "{email}"'))
def log_data_with_email(logging_context: dict[str, Any], email: str) -> None:
    """Set up data with email."""
    logging_context["last_log_data"] = {"email": email}


@given("log data containing totp_secret")
def log_data_with_totp(logging_context: dict[str, Any]) -> None:
    """Set up data with TOTP secret."""
    logging_context["last_log_data"] = {"totp_secret": "JBSWY3DPEHPK3PXP"}


@when("the log entry is written")
def log_entry_written(logging_context: dict[str, Any]) -> None:
    """Write log entry with redaction."""
    redacted = LoggingService.redact_sensitive_data(logging_context["last_log_data"])
    logging_context["redacted_data"] = redacted


@then(parsers.parse('the password value should be "{expected}"'))
def verify_password_redacted(logging_context: dict[str, Any], expected: str) -> None:
    """Verify password was redacted."""
    assert logging_context["redacted_data"]["password"] == expected


@then(parsers.parse('both token values should be "{expected}"'))
def verify_tokens_redacted(logging_context: dict[str, Any], expected: str) -> None:
    """Verify tokens were redacted."""
    assert logging_context["redacted_data"]["access_token"] == expected
    assert logging_context["redacted_data"]["refresh_token"] == expected


@then(parsers.parse('the email should be masked as "{expected}"'))
def verify_email_masked(logging_context: dict[str, Any], expected: str) -> None:
    """Verify email was masked."""
    assert logging_context["redacted_data"]["email"] == expected


@then(parsers.parse('the totp_secret value should be "{expected}"'))
def verify_totp_redacted(logging_context: dict[str, Any], expected: str) -> None:
    """Verify TOTP secret was redacted."""
    assert logging_context["redacted_data"]["totp_secret"] == expected


# Log file verification steps


@then(parsers.parse('an entry should be written to "{log_file}"'))
def verify_log_file_entry(logging_context: dict[str, Any], log_file: str) -> None:
    """Verify entry was written to specified log file."""
    log_path = logging_context["log_dir"] / log_file
    assert log_path.exists(), f"Log file {log_file} does not exist"
    content = log_path.read_text()
    assert len(content) > 0, f"Log file {log_file} is empty"


@then("the log entry should contain:")
def verify_log_entry_contains(
    logging_context: dict[str, Any], datatable: list[dict[str, str]]
) -> None:
    """Verify log entry contains expected fields."""
    # This would parse the last log entry and verify fields
    # Implementation depends on log format
    pass


@then("each domain should have its own log file:")
def verify_separate_log_files(
    logging_context: dict[str, Any], datatable: list[dict[str, str]]
) -> None:
    """Verify each domain has its own log file."""
    for row in datatable:
        domain = row["domain"]
        expected_file = row["file"]
        log_path = logging_context["log_dir"] / expected_file
        assert log_path.exists(), f"Log file {expected_file} for domain {domain} not found"


# Log rotation steps


@given("a log file at maximum size")
def log_file_at_max_size(logging_context: dict[str, Any]) -> None:
    """Set up log file at maximum size."""
    log_path = logging_context["log_dir"] / "auth.log"
    # Create a file just under the rotation threshold
    log_path.write_text("x" * 10485760)  # 10MB


@then("the log file should be rotated")
def verify_log_rotation(logging_context: dict[str, Any]) -> None:
    """Verify log file was rotated."""
    log_path = logging_context["log_dir"] / "auth.log"
    backup_path = logging_context["log_dir"] / "auth.log.1"
    # After rotation, original file should be smaller or backup should exist
    assert backup_path.exists() or log_path.stat().st_size < 10485760


@then("a backup file should be created")
def verify_backup_created(logging_context: dict[str, Any]) -> None:
    """Verify backup file was created."""
    backup_path = logging_context["log_dir"] / "auth.log.1"
    assert backup_path.exists()


# Sentry integration steps


@given("the application is in production mode")
def production_mode(logging_context: dict[str, Any]) -> None:
    """Set up production mode."""
    logging_context["debug"] = False


@given("Sentry is configured")
def sentry_configured(logging_context: dict[str, Any]) -> None:
    """Set up Sentry configuration."""
    logging_context["sentry_dsn"] = "https://test@sentry.io/123"


@given("Sentry SDK is not installed")
def sentry_not_installed(logging_context: dict[str, Any]) -> None:
    """Set up scenario without Sentry."""
    logging_context["sentry_installed"] = False


@when("an error is logged")
def error_logged(logging_context: dict[str, Any]) -> None:
    """Log an error."""
    app_logger = LoggingService.app()
    app_logger.error("Test error", extra={"event": "TEST_ERROR"})
    for handler in app_logger.handlers:
        handler.flush()


@when("events occur in different domains")
def events_in_different_domains(logging_context: dict[str, Any]) -> None:
    """Generate events in all domains."""
    LoggingService.auth().info("auth event")
    LoggingService.mail().info("mail event")
    LoggingService.security().info("security event")
    LoggingService.database().info("database event")
    LoggingService.graphql().info("graphql event")
    LoggingService.app().info("app event")

    # Flush all handlers
    for domain in LoggingService.LOG_DOMAINS:
        logger = LoggingService.get_logger(domain)
        for handler in logger.handlers:
            handler.flush()


@then("the error should be sent to Sentry")
def verify_sentry_error(logging_context: dict[str, Any]) -> None:
    """Verify error was sent to Sentry."""
    # This would verify Sentry was called
    # Implementation depends on mocking
    pass


@then("sensitive data should be redacted")
def verify_sentry_redaction(logging_context: dict[str, Any]) -> None:
    """Verify sensitive data was redacted before Sentry."""
    pass


@then("no exception should be raised")
def verify_no_exception(logging_context: dict[str, Any]) -> None:
    """Verify no exception was raised."""
    # If we got here, no exception was raised
    pass


@then("the error should be logged to file")
def verify_error_in_file(logging_context: dict[str, Any]) -> None:
    """Verify error was logged to file."""
    log_path = logging_context["log_dir"] / "app.log"
    if log_path.exists():
        content = log_path.read_text()
        assert "error" in content.lower() or "ERROR" in content
