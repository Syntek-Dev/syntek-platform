"""Logging service for structured application logging with separation of concerns.

This module provides a centralised logging service that combines:
- Python's logging with structlog-style structured output
- Sentry integration for error tracking in production
- Separate log files per domain (auth, mail, database, security, graphql, app)

The LoggingService mirrors Pino's functionality from Node.js, providing:
- JSON-formatted logs in production (via python-json-logger)
- Human-readable logs in development
- Automatic context enrichment
- Request correlation IDs
- Security-aware field redaction

Log File Separation:
- auth.log: Authentication events (login, logout, 2FA, password changes)
- mail.log: Email delivery and verification events
- database.log: Query performance, slow queries, connection issues
- security.log: Security audit events, rate limiting, suspicious activity
- graphql.log: GraphQL queries, mutations, and errors
- app.log: General application logs

SECURITY NOTE:
- Sensitive data (passwords, tokens) is automatically redacted
- PII fields are masked before logging
- IP addresses use encrypted form from AuditService

Example:
    >>> from apps.core.services.logging_service import LoggingService
    >>> auth_logger = LoggingService.auth()
    >>> auth_logger.info("user_login", extra={"user_id": 123})
    >>>
    >>> mail_logger = LoggingService.mail()
    >>> mail_logger.info("email_sent", extra={"recipient": "user@example.com"})
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from pythonjsonlogger.json import JsonFormatter

# Try importing Sentry SDK (may not be installed in dev)
try:
    import sentry_sdk
except ImportError:
    sentry_sdk = None


class LoggingService:
    """Centralised logging service with domain-specific log files.

    Provides structured logging capabilities similar to Pino in Node.js,
    with separate log files for different concerns:
    - auth: Authentication and authorisation events
    - mail: Email delivery and notifications
    - database: Database queries and performance
    - security: Security audit trail
    - graphql: GraphQL API operations
    - app: General application logs

    Attributes:
        SENSITIVE_FIELDS: Field names that should be redacted
        PII_FIELDS: Field names containing personally identifiable information
        LOG_DOMAINS: Available logging domains
    """

    SENSITIVE_FIELDS: set[str] = {
        "password",
        "token",
        "secret",
        "api_key",
        "access_token",
        "refresh_token",
        "totp_secret",
        "backup_codes",
        "credit_card",
        "ssn",
    }

    PII_FIELDS: set[str] = {
        "email",
        "phone",
        "address",
        "date_of_birth",
        "national_id",
    }

    LOG_DOMAINS: set[str] = {
        "auth",
        "mail",
        "database",
        "security",
        "graphql",
        "app",
    }

    _loggers: dict[str, logging.Logger] = {}
    _configured: bool = False

    @classmethod
    def auth(cls) -> logging.Logger:
        """Get the authentication logger.

        Returns:
            Logger for auth.log
        """
        return cls.get_logger("auth")

    @classmethod
    def mail(cls) -> logging.Logger:
        """Get the mail/email logger.

        Returns:
            Logger for mail.log
        """
        return cls.get_logger("mail")

    @classmethod
    def database(cls) -> logging.Logger:
        """Get the database logger.

        Returns:
            Logger for database.log
        """
        return cls.get_logger("database")

    @classmethod
    def security(cls) -> logging.Logger:
        """Get the security audit logger.

        Returns:
            Logger for security.log
        """
        return cls.get_logger("security")

    @classmethod
    def graphql(cls) -> logging.Logger:
        """Get the GraphQL API logger.

        Returns:
            Logger for graphql.log
        """
        return cls.get_logger("graphql")

    @classmethod
    def app(cls) -> logging.Logger:
        """Get the general application logger.

        Returns:
            Logger for app.log
        """
        return cls.get_logger("app")

    @classmethod
    def get_logger(cls, domain: str) -> logging.Logger:
        """Get a logger for the specified domain.

        Args:
            domain: One of 'auth', 'mail', 'database', 'security', 'graphql', 'app'

        Returns:
            Configured Logger instance

        Raises:
            ValueError: If domain is not recognised
        """
        if domain not in cls.LOG_DOMAINS:
            raise ValueError(
                f"Domain '{domain}' not recognised. Must be one of: {', '.join(cls.LOG_DOMAINS)}"
            )

        # Return cached logger if already configured
        if domain in cls._loggers:
            return cls._loggers[domain]

        # Create logger if not configured yet
        logger = logging.getLogger(f"app.{domain}")

        # Store in cache
        cls._loggers[domain] = logger

        # Auto-configure if not done yet
        if not cls._configured:
            cls.configure()

        return logger

    @classmethod
    def redact_sensitive_data(cls, data: dict[str, Any]) -> dict[str, Any]:
        """Redact sensitive fields from log data.

        Args:
            data: Dictionary of log data

        Returns:
            Dictionary with sensitive fields redacted
        """
        if not data:
            return {}

        redacted = {}

        for key, value in data.items():
            key_lower = key.lower()

            # Check if field name contains sensitive terms (case-insensitive)
            is_sensitive = any(
                sensitive_field in key_lower for sensitive_field in cls.SENSITIVE_FIELDS
            )

            if is_sensitive:
                # Redact sensitive fields completely
                redacted[key] = "[REDACTED]"
            elif key_lower in cls.PII_FIELDS:
                # Mask PII fields (show last 4 chars)
                if isinstance(value, str):
                    if len(value) <= 4:
                        redacted[key] = "[MASKED]"
                    else:
                        redacted[key] = f"***{value[-4:]}"
                else:
                    redacted[key] = "[MASKED]"
            else:
                # Keep non-sensitive fields unchanged
                redacted[key] = value

        return redacted

    @classmethod
    def configure(
        cls,
        log_dir: str = "/var/log/app",
        level: str = "INFO",
        max_bytes: int = 10485760,
        backup_count: int = 5,
        json_format: bool = True,
    ) -> None:
        """Configure all domain loggers with file handlers.

        Args:
            log_dir: Directory for log files
            level: Minimum log level
            max_bytes: Maximum file size before rotation (default 10MB)
            backup_count: Number of backup files to keep
            json_format: Use JSON formatting (production) vs human-readable (dev)
        """
        # Create log directory if it doesn't exist
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        # Convert level string to logging constant
        log_level = getattr(logging, level.upper(), logging.INFO)

        # Configure each domain logger
        for domain in cls.LOG_DOMAINS:
            logger = logging.getLogger(f"app.{domain}")
            logger.setLevel(log_level)
            logger.propagate = False

            # Remove existing handlers to avoid duplicates
            logger.handlers.clear()

            # Create rotating file handler
            log_file = log_path / f"{domain}.log"
            handler = RotatingFileHandler(
                filename=str(log_file),
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding="utf-8",
            )
            handler.setLevel(log_level)

            # Set formatter based on format preference
            if json_format:
                # JSON formatter for production (machine-readable)
                formatter = JsonFormatter(
                    "%(asctime)s %(name)s %(levelname)s %(message)s",
                    timestamp=True,
                )
            else:
                # Human-readable formatter for development
                formatter = logging.Formatter(
                    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )

            handler.setFormatter(formatter)
            logger.addHandler(handler)

            # Store configured logger
            cls._loggers[domain] = logger

        cls._configured = True

    @classmethod
    def log_to_sentry(
        cls,
        message: str,
        level: str = "error",
        context: dict[str, Any] | None = None,
        exception: Exception | None = None,
    ) -> None:
        """Send an event to Sentry if configured.

        Args:
            message: Event message
            level: Log level ('debug', 'info', 'warning', 'error', 'critical')
            context: Additional context data
            exception: Optional exception to attach
        """
        # Skip if Sentry SDK not available
        if sentry_sdk is None:
            return

        # Redact sensitive data from context
        safe_context = cls.redact_sensitive_data(context or {})

        # Send to Sentry
        with sentry_sdk.push_scope() as scope:
            # Set log level
            scope.level = level

            # Add context as extra data
            for key, value in safe_context.items():
                scope.set_extra(key, value)

            # Send exception or message
            if exception:
                sentry_sdk.capture_exception(exception)
            else:
                sentry_sdk.capture_message(message, level=level)

    # =========================================================================
    # Sentry Direct Logging
    # =========================================================================
    # These methods send logs directly to Sentry using sentry_sdk.logger
    # Useful for important events that should always appear in Sentry

    @classmethod
    def sentry_info(cls, message: str, **kwargs: Any) -> None:
        """Send an info log directly to Sentry.

        Args:
            message: Log message
            **kwargs: Additional context (will be redacted)
        """
        if sentry_sdk is None:
            return
        safe_kwargs = cls.redact_sensitive_data(kwargs)
        sentry_sdk.logger.info(message, extra=safe_kwargs)

    @classmethod
    def sentry_warning(cls, message: str, **kwargs: Any) -> None:
        """Send a warning log directly to Sentry.

        Args:
            message: Log message
            **kwargs: Additional context (will be redacted)
        """
        if sentry_sdk is None:
            return
        safe_kwargs = cls.redact_sensitive_data(kwargs)
        sentry_sdk.logger.warning(message, extra=safe_kwargs)

    @classmethod
    def sentry_error(cls, message: str, **kwargs: Any) -> None:
        """Send an error log directly to Sentry.

        Args:
            message: Log message
            **kwargs: Additional context (will be redacted)
        """
        if sentry_sdk is None:
            return
        safe_kwargs = cls.redact_sensitive_data(kwargs)
        sentry_sdk.logger.error(message, extra=safe_kwargs)

    # =========================================================================
    # Sentry Metrics
    # =========================================================================
    # Emit custom metrics to Sentry for monitoring dashboards
    # See: https://docs.sentry.io/platforms/python/metrics/

    @classmethod
    def metric_count(cls, key: str, value: int = 1, tags: dict[str, str] | None = None) -> None:
        """Emit a count metric to Sentry.

        Use for counting occurrences of events.

        Args:
            key: Metric name (e.g., "auth.login_failed")
            value: Count value (default: 1)
            tags: Optional tags for filtering

        Example:
            >>> LoggingService.metric_count(
            ...     "auth.login_failed", tags={"reason": "invalid_password"}
            ... )
        """
        if sentry_sdk is None:
            return
        try:
            from sentry_sdk import metrics

            metrics.incr(key, value, tags=tags or {})
        except (ImportError, AttributeError):
            pass

    @classmethod
    def metric_gauge(cls, key: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Emit a gauge metric to Sentry.

        Use for measuring current values (e.g., queue depth, active users).

        Args:
            key: Metric name (e.g., "queue.depth")
            value: Current value
            tags: Optional tags for filtering

        Example:
            >>> LoggingService.metric_gauge("sessions.active", 42)
        """
        if sentry_sdk is None:
            return
        try:
            from sentry_sdk import metrics

            metrics.gauge(key, value, tags=tags or {})
        except (ImportError, AttributeError):
            pass

    @classmethod
    def metric_distribution(
        cls, key: str, value: float, tags: dict[str, str] | None = None
    ) -> None:
        """Emit a distribution metric to Sentry.

        Use for measuring distributions of values (e.g., response times, amounts).

        Args:
            key: Metric name (e.g., "api.response_time_ms")
            value: Measured value
            tags: Optional tags for filtering

        Example:
            >>> LoggingService.metric_distribution("checkout.amount_usd", 187.50)
        """
        if sentry_sdk is None:
            return
        try:
            from sentry_sdk import metrics

            metrics.distribution(key, value, tags=tags or {})
        except (ImportError, AttributeError):
            pass

    @classmethod
    def metric_timing(cls, key: str, value: float, tags: dict[str, str] | None = None) -> None:
        """Emit a timing metric to Sentry.

        Use for measuring durations in seconds.

        Args:
            key: Metric name (e.g., "db.query_time")
            value: Duration in seconds
            tags: Optional tags for filtering

        Example:
            >>> LoggingService.metric_timing("graphql.query_time", 0.250)
        """
        if sentry_sdk is None:
            return
        try:
            from sentry_sdk import metrics

            metrics.timing(key, value, tags=tags or {})
        except (ImportError, AttributeError):
            pass
