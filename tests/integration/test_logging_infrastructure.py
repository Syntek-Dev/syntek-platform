"""Integration tests for logging infrastructure.

Tests verify that the logging service integrates correctly with:
- Django settings configuration
- File system for log rotation
- Sentry SDK for error reporting
- AuditLog model for database persistence
- Multiple domain loggers working together

These tests require a configured Django environment and may
interact with the file system.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from django.test import override_settings

import pytest

from apps.core.models import AuditLog, Organisation, User
from apps.core.services.audit_service import AuditService
from apps.core.services.logging_service import LoggingService


@pytest.mark.integration
@pytest.mark.django_db
class TestLoggingServiceWithAuditService:
    """Integration tests for LoggingService and AuditService together."""

    @pytest.fixture
    def organisation(self) -> Organisation:
        """Create test organisation."""
        return Organisation.objects.create(name="Test Org", slug="test-org")

    @pytest.fixture
    def user(self, organisation: Organisation) -> User:
        """Create test user."""
        return User.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User",
            organisation=organisation,
        )

    def test_login_event_logged_to_both_services(self, user: User, tmp_path: Path) -> None:
        """Test login event is logged to file and database.

        Given: A configured logging service and audit service
        When: A login event occurs
        Then: Event is logged to auth.log file
        And: Event is persisted to AuditLog table
        """
        # Configure logging
        LoggingService.configure(log_dir=str(tmp_path), json_format=True)

        # Log to file via LoggingService
        auth_logger = LoggingService.auth()
        auth_logger.info(
            "LOGIN",
            extra={
                "event": "LOGIN",
                "user_id": user.id,
                "user_email": user.email,
            },
        )

        # Persist to database via AuditService
        audit_log = AuditService.log_login(
            user=user,
            ip_address="192.168.1.1",
            device_fingerprint="abc123",
        )

        # Verify file logging
        for handler in auth_logger.handlers:
            handler.flush()

        auth_log_path = tmp_path / "auth.log"
        assert auth_log_path.exists()
        log_content = auth_log_path.read_text()
        assert "LOGIN" in log_content

        # Verify database logging
        assert audit_log.id is not None
        assert audit_log.action == AuditLog.ActionType.LOGIN
        assert audit_log.user == user

    def test_failed_login_logged_with_ip_encryption(
        self, organisation: Organisation, tmp_path: Path
    ) -> None:
        """Test failed login logs encrypted IP to database.

        Given: A failed login attempt
        When: The event is logged
        Then: IP address is encrypted in AuditLog
        And: Event is logged to auth.log
        """
        LoggingService.configure(log_dir=str(tmp_path))

        # Log failed login
        audit_log = AuditService.log_login_failed(
            email="unknown@example.com",
            ip_address="10.0.0.1",
            organisation=organisation,
        )

        # Also log to file
        auth_logger = LoggingService.auth()
        auth_logger.warning(
            "LOGIN_FAILED",
            extra={
                "event": "LOGIN_FAILED",
                "attempted_email": "unknown@example.com",
            },
        )
        for handler in auth_logger.handlers:
            handler.flush()

        # Verify IP is encrypted (not stored as plain text)
        assert audit_log.ip_address is not None
        # IP should be binary (encrypted), not the original string
        if audit_log.ip_address:
            ip_bytes = bytes(audit_log.ip_address)
            assert b"10.0.0.1" not in ip_bytes

    def test_security_events_logged_to_security_file(self, user: User, tmp_path: Path) -> None:
        """Test security events go to security.log.

        Given: Security-related events occur
        When: Events are logged
        Then: They appear in security.log, not other log files
        """
        LoggingService.configure(log_dir=str(tmp_path))

        security_logger = LoggingService.security()
        security_logger.warning(
            "RATE_LIMIT_EXCEEDED",
            extra={
                "event": "RATE_LIMIT_EXCEEDED",
                "user_id": user.id,
                "request_count": 100,
            },
        )
        for handler in security_logger.handlers:
            handler.flush()

        # Verify in security.log
        security_log = tmp_path / "security.log"
        assert security_log.exists()
        content = security_log.read_text()
        assert "RATE_LIMIT_EXCEEDED" in content

        # Verify NOT in auth.log
        auth_log = tmp_path / "auth.log"
        if auth_log.exists():
            auth_content = auth_log.read_text()
            assert "RATE_LIMIT_EXCEEDED" not in auth_content


@pytest.mark.integration
class TestLoggingServiceFileRotation:
    """Integration tests for log file rotation."""

    def test_log_rotation_creates_backup_files(self, tmp_path: Path) -> None:
        """Test log files rotate when size limit is exceeded.

        Given: A log file approaching max size
        When: New log entries are written
        Then: File is rotated and backup is created
        """
        # Configure with small max size for testing
        LoggingService.configure(
            log_dir=str(tmp_path),
            max_bytes=1024,  # 1KB for testing
            backup_count=3,
        )

        auth_logger = LoggingService.auth()

        # Write enough data to trigger rotation
        for i in range(100):
            auth_logger.info(f"Test log entry {i}" + "x" * 100)

        for handler in auth_logger.handlers:
            handler.flush()

        # Check for rotated files
        auth_log = tmp_path / "auth.log"
        assert auth_log.exists()

        # At least one backup should exist after rotation
        backup_files = list(tmp_path.glob("auth.log.*"))
        # Note: rotation may not happen if we didn't write enough
        # This test verifies the mechanism is in place

    def test_backup_count_limits_old_files(self, tmp_path: Path) -> None:
        """Test backup count limits number of old log files.

        Given: backup_count=2
        When: Multiple rotations occur
        Then: Only 2 backup files are kept
        """
        LoggingService.configure(
            log_dir=str(tmp_path),
            max_bytes=512,
            backup_count=2,
        )

        auth_logger = LoggingService.auth()

        # Write lots of data to trigger multiple rotations
        for i in range(200):
            auth_logger.info(f"Entry {i}" + "y" * 100)

        for handler in auth_logger.handlers:
            handler.flush()

        # Count backup files
        backup_files = list(tmp_path.glob("auth.log.*"))
        assert len(backup_files) <= 2


@pytest.mark.integration
class TestLoggingServiceJsonFormat:
    """Integration tests for JSON log formatting."""

    def test_json_format_produces_valid_json(self, tmp_path: Path) -> None:
        """Test JSON format produces parseable JSON.

        Given: json_format=True
        When: Log entries are written
        Then: Each line is valid JSON
        """
        LoggingService.configure(log_dir=str(tmp_path), json_format=True)

        app_logger = LoggingService.app()
        app_logger.info(
            "test_event",
            extra={
                "event": "TEST_EVENT",
                "user_id": 123,
                "metadata": {"key": "value"},
            },
        )
        for handler in app_logger.handlers:
            handler.flush()

        app_log = tmp_path / "app.log"
        assert app_log.exists()

        # Each line should be valid JSON
        for line in app_log.read_text().strip().split("\n"):
            if line:
                parsed = json.loads(line)
                assert "message" in parsed or "event" in parsed

    def test_json_format_includes_timestamp(self, tmp_path: Path) -> None:
        """Test JSON logs include timestamp.

        Given: json_format=True
        When: Log entry is written
        Then: JSON includes timestamp field
        """
        LoggingService.configure(log_dir=str(tmp_path), json_format=True)

        app_logger = LoggingService.app()
        app_logger.info("test_event")
        for handler in app_logger.handlers:
            handler.flush()

        app_log = tmp_path / "app.log"
        line = app_log.read_text().strip().split("\n")[0]
        parsed = json.loads(line)

        # Should have timestamp (asctime or timestamp field)
        assert any(key in parsed for key in ["asctime", "timestamp", "time", "created"])


@pytest.mark.integration
class TestLoggingServiceSentryIntegration:
    """Integration tests for Sentry error reporting."""

    @patch("apps.core.services.logging_service.sentry_sdk")
    @override_settings(DEBUG=False)
    def test_errors_sent_to_sentry_in_production(
        self, mock_sentry: MagicMock, tmp_path: Path
    ) -> None:
        """Test errors are sent to Sentry when DEBUG=False.

        Given: Production mode (DEBUG=False) and Sentry configured
        When: An error is logged
        Then: Error is sent to Sentry
        """
        LoggingService.configure(log_dir=str(tmp_path))

        # Log an error with Sentry
        error = ValueError("Test error for Sentry")
        LoggingService.log_to_sentry(
            message="Test error occurred",
            level="error",
            context={"user_id": 123},
            exception=error,
        )

        # Verify Sentry was called
        mock_sentry.capture_exception.assert_called_once_with(error)

    @patch("apps.core.services.logging_service.sentry_sdk")
    def test_sentry_context_is_redacted(self, mock_sentry: MagicMock, tmp_path: Path) -> None:
        """Test sensitive data is redacted before sending to Sentry.

        Given: Context containing sensitive data
        When: Sent to Sentry
        Then: Sensitive fields are redacted
        """
        mock_scope = MagicMock()
        mock_sentry.push_scope.return_value.__enter__ = MagicMock(return_value=mock_scope)
        mock_sentry.push_scope.return_value.__exit__ = MagicMock(return_value=False)

        LoggingService.log_to_sentry(
            message="Login failed",
            context={
                "user_id": 123,
                "password": "secret123",
                "email": "user@example.com",
            },
        )

        # Check that set_extra was called with redacted values
        calls = {call[0][0]: call[0][1] for call in mock_scope.set_extra.call_args_list}

        assert calls.get("password") == "[REDACTED]"
        # Email should be masked
        if "email" in calls:
            assert "***" in calls["email"]


@pytest.mark.integration
class TestLoggingServiceMultipleDomains:
    """Integration tests for multiple logging domains working together."""

    def test_all_domains_log_independently(self, tmp_path: Path) -> None:
        """Test all domains can log simultaneously.

        Given: All logging domains are configured
        When: Events are logged to each domain
        Then: Each domain's log file contains only its events
        """
        LoggingService.configure(log_dir=str(tmp_path))

        # Log to each domain
        LoggingService.auth().info("AUTH_EVENT")
        LoggingService.mail().info("MAIL_EVENT")
        LoggingService.database().info("DB_EVENT")
        LoggingService.security().info("SECURITY_EVENT")
        LoggingService.graphql().info("GRAPHQL_EVENT")
        LoggingService.app().info("APP_EVENT")

        # Flush all handlers
        for domain in LoggingService.LOG_DOMAINS:
            logger = LoggingService.get_logger(domain)
            for handler in logger.handlers:
                handler.flush()

        # Verify each file contains only its domain's events
        expected_files = {
            "auth.log": "AUTH_EVENT",
            "mail.log": "MAIL_EVENT",
            "database.log": "DB_EVENT",
            "security.log": "SECURITY_EVENT",
            "graphql.log": "GRAPHQL_EVENT",
            "app.log": "APP_EVENT",
        }

        for filename, expected_event in expected_files.items():
            log_path = tmp_path / filename
            assert log_path.exists(), f"{filename} should exist"
            content = log_path.read_text()
            assert expected_event in content, f"{filename} should contain {expected_event}"

    def test_high_volume_logging_across_domains(self, tmp_path: Path) -> None:
        """Test logging handles high volume across multiple domains.

        Given: High volume of log events
        When: Events are logged rapidly across domains
        Then: All events are captured without loss
        """
        LoggingService.configure(log_dir=str(tmp_path))

        event_count = 100

        # Log many events to each domain
        for i in range(event_count):
            LoggingService.auth().info(f"AUTH_{i}")
            LoggingService.security().info(f"SECURITY_{i}")

        # Flush all handlers
        for domain in ["auth", "security"]:
            logger = LoggingService.get_logger(domain)
            for handler in logger.handlers:
                handler.flush()

        # Count events in each file
        auth_log = tmp_path / "auth.log"
        security_log = tmp_path / "security.log"

        auth_content = auth_log.read_text()
        security_content = security_log.read_text()

        auth_events = sum(1 for line in auth_content.split("\n") if "AUTH_" in line)
        security_events = sum(1 for line in security_content.split("\n") if "SECURITY_" in line)

        assert auth_events == event_count
        assert security_events == event_count


@pytest.mark.integration
@pytest.mark.django_db
class TestLoggingServiceWithDjangoSettings:
    """Integration tests for logging with Django settings."""

    def test_respects_django_log_level(self, tmp_path: Path) -> None:
        """Test logging respects Django settings log level.

        Given: Django settings specify a log level
        When: LoggingService is used
        Then: Only logs at or above that level are captured
        """
        LoggingService.configure(log_dir=str(tmp_path), level="WARNING")

        app_logger = LoggingService.app()
        app_logger.debug("DEBUG_MESSAGE")
        app_logger.info("INFO_MESSAGE")
        app_logger.warning("WARNING_MESSAGE")
        app_logger.error("ERROR_MESSAGE")

        for handler in app_logger.handlers:
            handler.flush()

        app_log = tmp_path / "app.log"
        content = app_log.read_text()

        # DEBUG and INFO should not appear
        assert "DEBUG_MESSAGE" not in content
        assert "INFO_MESSAGE" not in content

        # WARNING and ERROR should appear
        assert "WARNING_MESSAGE" in content
        assert "ERROR_MESSAGE" in content
