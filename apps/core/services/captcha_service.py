"""reCAPTCHA v3 verification service for bot protection.

This module provides CAPTCHA validation functionality to prevent automated attacks
on authentication endpoints. It uses Google's reCAPTCHA v3 which returns a score
from 0.0 (likely bot) to 1.0 (likely human).

Security Review Recommendation M001:
"Implement CAPTCHA for bot protection on registration and login endpoints."

Usage:
    from apps.core.services.captcha_service import captcha_service

    is_valid, score, error = captcha_service.verify_token(
        token=request.POST.get('captcha_token'),
        action='register',
        remote_ip=get_client_ip(request)
    )
"""

import logging

from django.conf import settings

import requests

logger = logging.getLogger(__name__)


class CaptchaService:
    """Service for validating reCAPTCHA v3 tokens.

    reCAPTCHA v3 returns a score from 0.0 to 1.0:
    - 1.0 is very likely a good interaction
    - 0.0 is very likely a bot

    Different thresholds are used for different actions:
    - Registration: 0.5 (moderate protection)
    - Login: 0.3 (lower threshold to avoid blocking legitimate users)
    - Password Reset: 0.5 (moderate protection)
    - Email Verification: 0.3 (lower threshold)
    """

    VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"

    SCORE_THRESHOLDS = {
        "register": 0.5,
        "login": 0.3,
        "password_reset": 0.5,
        "email_verification": 0.3,
    }

    def __init__(self) -> None:
        """Initialise CaptchaService with configuration from Django settings."""
        self.secret_key = getattr(settings, "RECAPTCHA_SECRET_KEY", "")
        self.enabled = getattr(settings, "RECAPTCHA_ENABLED", False)

    def verify_token(
        self, token: str | None, action: str, remote_ip: str | None = None
    ) -> tuple[bool, float, str | None]:
        """Verify a reCAPTCHA token.

        Validates the token against Google's reCAPTCHA API and checks if the score
        meets the threshold for the specified action.

        Args:
            token: The reCAPTCHA response token from the client (None if not provided).
            action: The expected action name (register, login, etc.).
            remote_ip: Optional client IP address for additional validation.

        Returns:
            Tuple of (is_valid, score, error_message):
            - is_valid: True if CAPTCHA passed, False otherwise
            - score: Float between 0.0 and 1.0 (bot to human likelihood)
            - error_message: Error description if validation failed, None otherwise
        """
        # If CAPTCHA is disabled in settings, always pass
        if not self.enabled:
            logger.debug("CAPTCHA validation skipped (disabled in settings)")
            return True, 1.0, None

        # Token is required when CAPTCHA is enabled
        if not token:
            logger.warning("CAPTCHA token missing in request")
            return False, 0.0, "CAPTCHA token is required"

        try:
            # Send verification request to Google
            response = requests.post(
                self.VERIFY_URL,
                data={
                    "secret": self.secret_key,
                    "response": token,
                    "remoteip": remote_ip,
                },
                timeout=5,
            )
            result = response.json()

            # Check if verification succeeded
            if not result.get("success"):
                error_codes = result.get("error-codes", [])
                logger.warning(f"CAPTCHA verification failed: {error_codes}")
                return False, 0.0, f"CAPTCHA validation failed: {error_codes}"

            # Verify action matches (prevents token reuse across different forms)
            result_action = result.get("action", "")
            if result_action != action:
                logger.warning(
                    f"CAPTCHA action mismatch: expected '{action}', got '{result_action}'"
                )
                return False, 0.0, "CAPTCHA action mismatch"

            # Get score and threshold
            score = result.get("score", 0.0)
            threshold = self.SCORE_THRESHOLDS.get(action, 0.5)

            # Check if score meets threshold
            if score < threshold:
                logger.info(
                    f"CAPTCHA score too low for action '{action}': {score:.2f} < {threshold:.2f}"
                )
                return (
                    False,
                    score,
                    f"CAPTCHA score too low ({score:.2f} < {threshold:.2f})",
                )

            # Validation passed
            logger.debug(f"CAPTCHA validation passed for action '{action}' with score {score:.2f}")
            return True, score, None

        except requests.RequestException as e:
            # Fail open: if CAPTCHA service is unavailable, allow the request
            # This prevents legitimate users from being blocked due to service issues
            logger.warning(f"CAPTCHA service unavailable: {e}. Failing open.")
            return True, 1.0, None

    def get_threshold(self, action: str) -> float:
        """Get the score threshold for a specific action.

        Args:
            action: The action name (register, login, etc.).

        Returns:
            The score threshold as a float (default: 0.5 if action not found).
        """
        return self.SCORE_THRESHOLDS.get(action, 0.5)


# Singleton instance for convenience
captcha_service = CaptchaService()
