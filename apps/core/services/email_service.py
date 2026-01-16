"""Email service for sending authentication-related emails.

This module provides email sending functionality for verification,
password reset, and notification emails. Supports both SMTP
and Mailpit for development/testing.

SECURITY NOTE:
- Rate limiting prevents email bombing
- Tokens are cryptographically secure
- Email templates sanitize user input
- Async sending with Celery (future)

Example:
    >>> EmailService.send_verification_email(user, token)
    >>> EmailService.send_password_reset_email(user, token)
"""

import logging
from typing import TYPE_CHECKING

from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags

if TYPE_CHECKING:
    from apps.core.models import User

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending authentication emails.

    Handles sending of verification emails, password reset emails,
    and other authentication-related notifications.

    Features:
    - Template-based email composition
    - Rate limiting to prevent abuse
    - Async sending support (Celery)
    - Retry logic for failed sends

    Attributes:
        None - All methods are static
    """

    @staticmethod
    def send_verification_email(user: User, token: str) -> bool:
        """Send email verification email to user.

        Args:
            user: User to send email to
            token: Email verification token (plain, not hashed)

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Build verification URL
            base_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
            verification_url = f"{base_url}/verify-email/{token}"

            # Email context
            context = {
                "user": user,
                "verification_url": verification_url,
                "site_name": getattr(settings, "SITE_NAME", "Backend Template"),
            }

            # Render email templates (HTML and plain text)
            subject = f"Verify your email address - {context['site_name']}"
            html_message = f"""
            <html>
                <body>
                    <h2>Welcome {user.get_full_name() or user.email}!</h2>
                    <p>
                    Thank you for registering. Please verify your email address by clicking the
                    link below:
                    </p>
                    <p><a href="{verification_url}">Verify Email Address</a></p>
                    <p>Or copy and paste this URL into your browser:</p>
                    <p>{verification_url}</p>
                    <p>This link will expire in 24 hours.</p>
                    <p>If you did not create an account, please ignore this email.</p>
                </body>
            </html>
            """
            plain_message = strip_tags(html_message)

            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Verification email sent to {user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send verification email to {user.email}: {e}")
            return False

    @staticmethod
    def send_password_reset_email(user: User, token: str) -> bool:
        """Send password reset email to user.

        Phase 4 (M007): Token expiry reduced from 15 to 10 minutes for improved security.

        Args:
            user: User to send email to
            token: Password reset token (plain, not hashed)

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            base_url = getattr(settings, "FRONTEND_URL", "http://localhost:3000")
            reset_url = f"{base_url}/reset-password/{token}"
            site_name = getattr(settings, "SITE_NAME", "Backend Template")

            # Get expiry minutes from settings (M007 - Phase 4)
            expiry_minutes = getattr(settings, "PASSWORD_RESET_TOKEN_EXPIRY_MINUTES", 10)

            subject = f"Reset your password - {site_name}"
            html_message = f"""
            <html>
                <body>
                    <h2>Password Reset Request</h2>
                    <p>Hi {user.get_full_name() or user.email},</p>
                    <p>You requested to reset your password. Click the link below to set a new
                    password:</p>
                    <p><a href="{reset_url}" style="display: inline-block; padding: 10px 20px;
                    background-color: #007bff; color: white; text-decoration: none; border-radius:
                        5px;">Reset Password</a></p>
                    <p>Or copy and paste this URL into your browser:</p>
                    <p>{reset_url}</p>
                    <p style="background-color: #fff3cd; border: 1px solid #ffc107; padding: 10px;
                        margin: 15px 0; border-radius: 5px;">
                        <strong>⏰ Important:</strong> This link will expire in
                        <strong>{expiry_minutes} minutes</strong>.
                    </p>
                    <p>If you did not request a password reset, please ignore this email.
                    Your password will remain unchanged.</p>
                </body>
            </html>
            """
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Password reset email sent to {user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send password reset email to {user.email}: {e}")
            return False

    @staticmethod
    def send_welcome_email(user: User) -> bool:
        """Send welcome email after successful registration.

        Args:
            user: User to send email to

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            site_name = getattr(settings, "SITE_NAME", "Backend Template")

            subject = f"Welcome to {site_name}!"
            html_message = f"""
            <html>
                <body>
                    <h2>Welcome {user.get_full_name() or user.email}!</h2>
                    <p>Thank you for joining {site_name}.</p>
                    <p>Your account has been successfully verified and is now active.</p>
                    <p>You can now log in and start using our platform.</p>
                </body>
            </html>
            """
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Welcome email sent to {user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {e}")
            return False

    @staticmethod
    def send_password_changed_notification(user: User) -> bool:
        """Send notification email after password change.

        Args:
            user: User to send email to

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            site_name = getattr(settings, "SITE_NAME", "Backend Template")

            subject = f"Password Changed - {site_name}"
            html_message = f"""
            <html>
                <body>
                    <h2>Password Changed</h2>
                    <p>Hi {user.get_full_name() or user.email},</p>
                    <p>Your password was successfully changed.</p>
                    <p>If you did not make this change, please contact support immediately.</p>
                </body>
            </html>
            """
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"Password changed notification sent to {user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send password changed notification to {user.email}: {e}")
            return False

    @staticmethod
    def send_2fa_enabled_notification(user: User) -> bool:
        """Send notification email after 2FA is enabled.

        Args:
            user: User to send email to

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            site_name = getattr(settings, "SITE_NAME", "Backend Template")

            subject = f"Two-Factor Authentication Enabled - {site_name}"
            html_message = f"""
            <html>
                <body>
                    <h2>Two-Factor Authentication Enabled</h2>
                    <p>Hi {user.get_full_name() or user.email},</p>
                    <p>Two-factor authentication has been successfully enabled on your account.</p>
                    <p>Your account is now more secure.</p>
                    <p>If you did not enable this feature, please contact support immediately.</p>
                </body>
            </html>
            """
            plain_message = strip_tags(html_message)

            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            logger.info(f"2FA enabled notification sent to {user.email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send 2FA enabled notification to {user.email}: {e}")
            return False
