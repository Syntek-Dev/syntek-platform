"""Unit tests for LoggingService.

Tests cover:
- Domain-specific logger retrieval (auth, mail, database, security, graphql, app)
- Sensitive data redaction
- PII field masking
- Logger configuration with file handlers
- JSON vs human-readable formatting
- Log file rotation settings
- Sentry integration
- Invalid domain handling

These tests follow TDD - they WILL FAIL against the stub implementation
until LoggingService is fully implemented.

Test Categories:
- Logger retrieval tests
- Data redaction tests
- Configuration tests
- Sentry integration tests
"""

import logging
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from apps.core.services.logging_service import LoggingService


@pytest.mark.unit
class TestLoggingServiceDomainLoggers:
    """Unit tests for domain-specific logger retrieval."""

    def test_auth_returns_logger(self) -> None:
        """Test auth() returns a Logger instance.

        Given: LoggingService is available
        When: LoggingService.auth() is called
        Then: A logging.Logger instance is returned
        """
        logger = LoggingService.auth()

        assert isinstance(logger, logging.Logger)

    def test_mail_returns_logger(self) -> None:
        """Test mail() returns a Logger instance.

        Given: LoggingService is available
        When: LoggingService.mail() is called
        Then: A logging.Logger instance is returned
        """
        logger = LoggingService.mail()

        assert isinstance(logger, logging.Logger)

    def test_database_returns_logger(self) -> None:
        """Test database() returns a Logger instance.

        Given: LoggingService is available
        When: LoggingService.database() is called
        Then: A logging.Logger instance is returned
        """
        logger = LoggingService.database()

        assert isinstance(logger, logging.Logger)

    def test_security_returns_logger(self) -> None:
        """Test security() returns a Logger instance.

        Given: LoggingService is available
        When: LoggingService.security() is called
        Then: A logging.Logger instance is returned
        """
        logger = LoggingService.security()

        assert isinstance(logger, logging.Logger)

    def test_graphql_returns_logger(self) -> None:
        """Test graphql() returns a Logger instance.

        Given: LoggingService is available
        When: LoggingService.graphql() is called
        Then: A logging.Logger instance is returned
        """
        logger = LoggingService.graphql()

        assert isinstance(logger, logging.Logger)

    def test_app_returns_logger(self) -> None:
        """Test app() returns a Logger instance.

        Given: LoggingService is available
        When: LoggingService.app() is called
        Then: A logging.Logger instance is returned
        """
        logger = LoggingService.app()

        assert isinstance(logger, logging.Logger)

    def test_get_logger_with_valid_domain(self) -> None:
        """Test get_logger() returns logger for valid domain.

        Given: A valid domain name 'auth'
        When: LoggingService.get_logger('auth') is called
        Then: A logging.Logger instance is returned
        """
        logger = LoggingService.get_logger("auth")

        assert isinstance(logger, logging.Logger)

    def test_get_logger_with_invalid_domain_raises_error(self) -> None:
        """Test get_logger() raises ValueError for invalid domain.

        Given: An invalid domain name 'invalid'
        When: LoggingService.get_logger('invalid') is called
        Then: ValueError is raised
        """
        with pytest.raises(ValueError, match="not recognised"):
            LoggingService.get_logger("invalid")

    def test_auth_logger_has_correct_name(self) -> None:
        """Test auth logger has correct name for log file separation.

        Given: LoggingService is available
        When: LoggingService.auth() is called
        Then: Logger name contains 'auth'
        """
        logger = LoggingService.auth()

        assert "auth" in logger.name.lower()

    def test_mail_logger_has_correct_name(self) -> None:
        """Test mail logger has correct name for log file separation.

        Given: LoggingService is available
        When: LoggingService.mail() is called
        Then: Logger name contains 'mail'
        """
        logger = LoggingService.mail()

        assert "mail" in logger.name.lower()

    def test_database_logger_has_correct_name(self) -> None:
        """Test database logger has correct name for log file separation.

        Given: LoggingService is available
        When: LoggingService.database() is called
        Then: Logger name contains 'database'
        """
        logger = LoggingService.database()

        assert "database" in logger.name.lower()

    def test_security_logger_has_correct_name(self) -> None:
        """Test security logger has correct name for log file separation.

        Given: LoggingService is available
        When: LoggingService.security() is called
        Then: Logger name contains 'security'
        """
        logger = LoggingService.security()

        assert "security" in logger.name.lower()

    def test_graphql_logger_has_correct_name(self) -> None:
        """Test graphql logger has correct name for log file separation.

        Given: LoggingService is available
        When: LoggingService.graphql() is called
        Then: Logger name contains 'graphql'
        """
        logger = LoggingService.graphql()

        assert "graphql" in logger.name.lower()

    def test_same_domain_returns_same_logger(self) -> None:
        """Test calling same domain method returns cached logger.

        Given: LoggingService is available
        When: LoggingService.auth() is called twice
        Then: Same logger instance is returned
        """
        logger1 = LoggingService.auth()
        logger2 = LoggingService.auth()

        assert logger1 is logger2


@pytest.mark.unit
class TestLoggingServiceSensitiveDataRedaction:
    """Unit tests for sensitive data redaction."""

    def test_redact_password_field(self) -> None:
        """Test password field is redacted.

        Given: Data containing 'password' field
        When: redact_sensitive_data() is called
        Then: Password value is replaced with '[REDACTED]'
        """
        data = {"username": "john", "password": "secret123"}

        result = LoggingService.redact_sensitive_data(data)

        assert result["password"] == "[REDACTED]"
        assert result["username"] == "john"

    def test_redact_token_field(self) -> None:
        """Test token field is redacted.

        Given: Data containing 'token' field
        When: redact_sensitive_data() is called
        Then: Token value is replaced with '[REDACTED]'
        """
        data = {"user_id": 1, "token": "abc123xyz"}

        result = LoggingService.redact_sensitive_data(data)

        assert result["token"] == "[REDACTED]"

    def test_redact_access_token_field(self) -> None:
        """Test access_token field is redacted.

        Given: Data containing 'access_token' field
        When: redact_sensitive_data() is called
        Then: Access token value is replaced with '[REDACTED]'
        """
        data = {"access_token": "eyJhbGciOiJIUzI1NiIs..."}

        result = LoggingService.redact_sensitive_data(data)

        assert result["access_token"] == "[REDACTED]"

    def test_redact_refresh_token_field(self) -> None:
        """Test refresh_token field is redacted.

        Given: Data containing 'refresh_token' field
        When: redact_sensitive_data() is called
        Then: Refresh token value is replaced with '[REDACTED]'
        """
        data = {"refresh_token": "refresh_abc123"}

        result = LoggingService.redact_sensitive_data(data)

        assert result["refresh_token"] == "[REDACTED]"

    def test_redact_totp_secret_field(self) -> None:
        """Test totp_secret field is redacted.

        Given: Data containing 'totp_secret' field
        When: redact_sensitive_data() is called
        Then: TOTP secret value is replaced with '[REDACTED]'
        """
        data = {"totp_secret": "JBSWY3DPEHPK3PXP"}

        result = LoggingService.redact_sensitive_data(data)

        assert result["totp_secret"] == "[REDACTED]"

    def test_redact_api_key_field(self) -> None:
        """Test api_key field is redacted.

        Given: Data containing 'api_key' field
        When: redact_sensitive_data() is called
        Then: API key value is replaced with '[REDACTED]'
        """
        data = {"api_key": "sk-1234567890abcdef"}

        result = LoggingService.redact_sensitive_data(data)

        assert result["api_key"] == "[REDACTED]"

    def test_redact_backup_codes_field(self) -> None:
        """Test backup_codes field is redacted.

        Given: Data containing 'backup_codes' field
        When: redact_sensitive_data() is called
        Then: Backup codes value is replaced with '[REDACTED]'
        """
        data = {"backup_codes": ["code1", "code2", "code3"]}

        result = LoggingService.redact_sensitive_data(data)

        assert result["backup_codes"] == "[REDACTED]"

    def test_redact_secret_in_field_name(self) -> None:
        """Test field names containing 'secret' are redacted.

        Given: Data containing 'client_secret' field
        When: redact_sensitive_data() is called
        Then: Secret value is replaced with '[REDACTED]'
        """
        data = {"client_secret": "my_secret_value"}

        result = LoggingService.redact_sensitive_data(data)

        assert result["client_secret"] == "[REDACTED]"

    def test_redact_case_insensitive(self) -> None:
        """Test redaction is case insensitive.

        Given: Data with 'PASSWORD' (uppercase)
        When: redact_sensitive_data() is called
        Then: Password value is still redacted
        """
        data = {"PASSWORD": "secret123", "Token": "abc123"}

        result = LoggingService.redact_sensitive_data(data)

        assert result["PASSWORD"] == "[REDACTED]"
        assert result["Token"] == "[REDACTED]"


@pytest.mark.unit
class TestLoggingServicePIIMasking:
    """Unit tests for PII field masking."""

    def test_mask_email_field(self) -> None:
        """Test email field is masked showing last 4 chars.

        Given: Data containing 'email' field with value 'user@example.com'
        When: redact_sensitive_data() is called
        Then: Email is masked as '***.com'
        """
        data = {"email": "user@example.com"}

        result = LoggingService.redact_sensitive_data(data)

        assert result["email"] == "***.com"

    def test_mask_phone_field(self) -> None:
        """Test phone field is masked showing last 4 digits.

        Given: Data containing 'phone' field
        When: redact_sensitive_data() is called
        Then: Phone is masked showing last 4 digits
        """
        data = {"phone": "+44 7700 900123"}

        result = LoggingService.redact_sensitive_data(data)

        assert result["phone"] == "***0123"

    def test_mask_short_pii_value(self) -> None:
        """Test short PII values are fully masked.

        Given: Data containing short PII value (4 chars or less)
        When: redact_sensitive_data() is called
        Then: Value is replaced with '[MASKED]'
        """
        data = {"phone": "1234"}

        result = LoggingService.redact_sensitive_data(data)

        assert result["phone"] == "[MASKED]"

    def test_preserve_non_sensitive_fields(self) -> None:
        """Test non-sensitive fields are preserved unchanged.

        Given: Data with mix of sensitive and non-sensitive fields
        When: redact_sensitive_data() is called
        Then: Non-sensitive fields are unchanged
        """
        data = {
            "user_id": 123,
            "action": "login",
            "timestamp": "2026-01-17T10:00:00Z",
            "password": "secret",
        }

        result = LoggingService.redact_sensitive_data(data)

        assert result["user_id"] == 123
        assert result["action"] == "login"
        assert result["timestamp"] == "2026-01-17T10:00:00Z"
        assert result["password"] == "[REDACTED]"

    def test_empty_data_returns_empty_dict(self) -> None:
        """Test empty dict input returns empty dict.

        Given: Empty dictionary
        When: redact_sensitive_data() is called
        Then: Empty dictionary is returned
        """
        result = LoggingService.redact_sensitive_data({})

        assert result == {}


@pytest.mark.unit
class TestLoggingServiceConfiguration:
    """Unit tests for logging configuration."""

    def test_configure_creates_log_directory(self, tmp_path: Path) -> None:
        """Test configure() creates log directory if it doesn't exist.

        Given: A non-existent log directory path
        When: LoggingService.configure() is called
        Then: Directory is created
        """
        log_dir = tmp_path / "logs"

        LoggingService.configure(log_dir=str(log_dir))

        assert log_dir.exists()

    def test_configure_sets_log_level(self, tmp_path: Path) -> None:
        """Test configure() sets the specified log level.

        Given: Log level 'DEBUG'
        When: LoggingService.configure(level='DEBUG') is called
        Then: Loggers have DEBUG level
        """
        LoggingService.configure(log_dir=str(tmp_path), level="DEBUG")

        auth_logger = LoggingService.auth()
        assert auth_logger.level <= logging.DEBUG

    def test_configure_with_json_format(self, tmp_path: Path) -> None:
        """Test configure() uses JSON formatter when json_format=True.

        Given: json_format=True
        When: LoggingService.configure() is called
        Then: Handlers use JSON formatter
        """
        LoggingService.configure(log_dir=str(tmp_path), json_format=True)

        auth_logger = LoggingService.auth()
        # Check that at least one handler has JSON formatter
        has_json = any(
            "json" in type(h.formatter).__name__.lower()
            for h in auth_logger.handlers
            if h.formatter
        )
        assert has_json

    def test_configure_with_human_readable_format(self, tmp_path: Path) -> None:
        """Test configure() uses human-readable formatter when json_format=False.

        Given: json_format=False
        When: LoggingService.configure() is called
        Then: Handlers use standard formatter (not JSON)
        """
        LoggingService.configure(log_dir=str(tmp_path), json_format=False)

        auth_logger = LoggingService.auth()
        # Check that handlers don't use JSON formatter
        has_json = any(
            "json" in type(h.formatter).__name__.lower()
            for h in auth_logger.handlers
            if h.formatter
        )
        assert not has_json

    def test_configure_sets_max_bytes(self, tmp_path: Path) -> None:
        """Test configure() sets max file size for rotation.

        Given: max_bytes=5242880 (5MB)
        When: LoggingService.configure() is called
        Then: File handlers have correct maxBytes setting
        """
        LoggingService.configure(log_dir=str(tmp_path), max_bytes=5242880)

        auth_logger = LoggingService.auth()
        for handler in auth_logger.handlers:
            if hasattr(handler, "maxBytes"):
                assert handler.maxBytes == 5242880

    def test_configure_sets_backup_count(self, tmp_path: Path) -> None:
        """Test configure() sets backup count for rotation.

        Given: backup_count=3
        When: LoggingService.configure() is called
        Then: File handlers have correct backupCount setting
        """
        LoggingService.configure(log_dir=str(tmp_path), backup_count=3)

        auth_logger = LoggingService.auth()
        for handler in auth_logger.handlers:
            if hasattr(handler, "backupCount"):
                assert handler.backupCount == 3

    def test_configure_creates_separate_log_files(self, tmp_path: Path) -> None:
        """Test configure() creates separate log files for each domain.

        Given: A log directory
        When: LoggingService.configure() is called and logs are written
        Then: Separate log files exist for each domain
        """
        LoggingService.configure(log_dir=str(tmp_path))

        # Write a log to each domain
        LoggingService.auth().info("test auth")
        LoggingService.mail().info("test mail")
        LoggingService.database().info("test database")
        LoggingService.security().info("test security")
        LoggingService.graphql().info("test graphql")
        LoggingService.app().info("test app")

        # Force flush
        for domain in LoggingService.LOG_DOMAINS:
            logger = LoggingService.get_logger(domain)
            for handler in logger.handlers:
                handler.flush()

        # Check log files exist
        assert (tmp_path / "auth.log").exists()
        assert (tmp_path / "mail.log").exists()
        assert (tmp_path / "database.log").exists()
        assert (tmp_path / "security.log").exists()
        assert (tmp_path / "graphql.log").exists()
        assert (tmp_path / "app.log").exists()


@pytest.mark.unit
class TestLoggingServiceSentryIntegration:
    """Unit tests for Sentry integration."""

    @patch("apps.core.services.logging_service.sentry_sdk")
    def test_log_to_sentry_captures_message(self, mock_sentry: MagicMock) -> None:
        """Test log_to_sentry() sends message to Sentry.

        Given: Sentry SDK is available
        When: LoggingService.log_to_sentry() is called
        Then: sentry_sdk.capture_message is called
        """
        LoggingService.log_to_sentry("Test error message", level="error")

        mock_sentry.capture_message.assert_called()

    @patch("apps.core.services.logging_service.sentry_sdk")
    def test_log_to_sentry_captures_exception(self, mock_sentry: MagicMock) -> None:
        """Test log_to_sentry() sends exception to Sentry.

        Given: An exception is provided
        When: LoggingService.log_to_sentry() is called with exception
        Then: sentry_sdk.capture_exception is called
        """
        error = ValueError("Test exception")

        LoggingService.log_to_sentry("Error occurred", exception=error)

        mock_sentry.capture_exception.assert_called_with(error)

    @patch("apps.core.services.logging_service.sentry_sdk")
    def test_log_to_sentry_includes_context(self, mock_sentry: MagicMock) -> None:
        """Test log_to_sentry() includes context data.

        Given: Context data is provided
        When: LoggingService.log_to_sentry() is called
        Then: Context is added to Sentry scope
        """
        context = {"user_id": 123, "action": "login"}
        mock_scope = MagicMock()
        mock_sentry.push_scope.return_value.__enter__ = MagicMock(return_value=mock_scope)
        mock_sentry.push_scope.return_value.__exit__ = MagicMock(return_value=False)

        LoggingService.log_to_sentry("Test message", context=context)

        # Verify set_extra was called for each context item
        calls = mock_scope.set_extra.call_args_list
        assert any(call[0] == ("user_id", 123) for call in calls)

    @patch("apps.core.services.logging_service.sentry_sdk", None)
    def test_log_to_sentry_handles_missing_sdk(self) -> None:
        """Test log_to_sentry() handles missing Sentry SDK gracefully.

        Given: Sentry SDK is not installed
        When: LoggingService.log_to_sentry() is called
        Then: No exception is raised
        """
        # Should not raise
        LoggingService.log_to_sentry("Test message")

    @patch("apps.core.services.logging_service.sentry_sdk")
    def test_log_to_sentry_redacts_sensitive_context(self, mock_sentry: MagicMock) -> None:
        """Test log_to_sentry() redacts sensitive data in context.

        Given: Context containing sensitive data
        When: LoggingService.log_to_sentry() is called
        Then: Sensitive data is redacted before sending to Sentry
        """
        context = {"user_id": 123, "password": "secret123"}
        mock_scope = MagicMock()
        mock_sentry.push_scope.return_value.__enter__ = MagicMock(return_value=mock_scope)
        mock_sentry.push_scope.return_value.__exit__ = MagicMock(return_value=False)

        LoggingService.log_to_sentry("Test message", context=context)

        # Verify password was redacted
        calls = mock_scope.set_extra.call_args_list
        password_calls = [c for c in calls if c[0][0] == "password"]
        if password_calls:
            assert password_calls[0][0][1] == "[REDACTED]"


@pytest.mark.unit
class TestLoggingServiceLogDomains:
    """Unit tests for LOG_DOMAINS constant."""

    def test_log_domains_contains_auth(self) -> None:
        """Test LOG_DOMAINS includes 'auth'."""
        assert "auth" in LoggingService.LOG_DOMAINS

    def test_log_domains_contains_mail(self) -> None:
        """Test LOG_DOMAINS includes 'mail'."""
        assert "mail" in LoggingService.LOG_DOMAINS

    def test_log_domains_contains_database(self) -> None:
        """Test LOG_DOMAINS includes 'database'."""
        assert "database" in LoggingService.LOG_DOMAINS

    def test_log_domains_contains_security(self) -> None:
        """Test LOG_DOMAINS includes 'security'."""
        assert "security" in LoggingService.LOG_DOMAINS

    def test_log_domains_contains_graphql(self) -> None:
        """Test LOG_DOMAINS includes 'graphql'."""
        assert "graphql" in LoggingService.LOG_DOMAINS

    def test_log_domains_contains_app(self) -> None:
        """Test LOG_DOMAINS includes 'app'."""
        assert "app" in LoggingService.LOG_DOMAINS

    def test_log_domains_has_six_domains(self) -> None:
        """Test LOG_DOMAINS contains exactly 6 domains."""
        assert len(LoggingService.LOG_DOMAINS) == 6


@pytest.mark.unit
class TestLoggingServiceSensitiveFields:
    """Unit tests for SENSITIVE_FIELDS constant."""

    def test_sensitive_fields_contains_password(self) -> None:
        """Test SENSITIVE_FIELDS includes 'password'."""
        assert "password" in LoggingService.SENSITIVE_FIELDS

    def test_sensitive_fields_contains_token(self) -> None:
        """Test SENSITIVE_FIELDS includes 'token'."""
        assert "token" in LoggingService.SENSITIVE_FIELDS

    def test_sensitive_fields_contains_secret(self) -> None:
        """Test SENSITIVE_FIELDS includes 'secret'."""
        assert "secret" in LoggingService.SENSITIVE_FIELDS

    def test_sensitive_fields_contains_api_key(self) -> None:
        """Test SENSITIVE_FIELDS includes 'api_key'."""
        assert "api_key" in LoggingService.SENSITIVE_FIELDS

    def test_sensitive_fields_contains_totp_secret(self) -> None:
        """Test SENSITIVE_FIELDS includes 'totp_secret'."""
        assert "totp_secret" in LoggingService.SENSITIVE_FIELDS

    def test_sensitive_fields_contains_backup_codes(self) -> None:
        """Test SENSITIVE_FIELDS includes 'backup_codes'."""
        assert "backup_codes" in LoggingService.SENSITIVE_FIELDS


@pytest.mark.unit
class TestLoggingServicePIIFields:
    """Unit tests for PII_FIELDS constant."""

    def test_pii_fields_contains_email(self) -> None:
        """Test PII_FIELDS includes 'email'."""
        assert "email" in LoggingService.PII_FIELDS

    def test_pii_fields_contains_phone(self) -> None:
        """Test PII_FIELDS includes 'phone'."""
        assert "phone" in LoggingService.PII_FIELDS

    def test_pii_fields_contains_address(self) -> None:
        """Test PII_FIELDS includes 'address'."""
        assert "address" in LoggingService.PII_FIELDS
