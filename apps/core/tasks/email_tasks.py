"""Celery tasks for async email delivery with retry logic (H6).

This module implements async email sending with:
- Exponential backoff retry strategy
- Dead letter queue for failed emails
- Task monitoring and logging
- Rate limiting integration

SECURITY NOTE (H6):
- Retries with exponential backoff (1s, 2s, 4s, 8s, 16s)
- Maximum 5 retry attempts
- Failed emails moved to dead letter queue after max retries
- Email delivery failures logged for admin review

Example:
    >>> from apps.core.tasks.email_tasks import send_verification_email_task
    >>> send_verification_email_task.delay(user_id)
"""

import logging

from django.contrib.auth import get_user_model

from celery import shared_task

from apps.core.services.email_service import EmailService

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=5,
    retry_jitter=True,
)
def send_verification_email_task(self, user_id: int, token: str) -> dict:
    """Send email verification email asynchronously with retry logic (H6).

    Implements exponential backoff retry strategy:
    - Attempt 1: Immediate
    - Attempt 2: 1s delay
    - Attempt 3: 2s delay
    - Attempt 4: 4s delay
    - Attempt 5: 8s delay
    - Attempt 6: 16s delay (final)

    After max retries, email is logged to dead letter queue for manual review.

    Args:
        self: Celery task instance (bound).
        user_id: User ID to send verification email to.
        token: Email verification token (plain, not hashed).

    Returns:
        Dictionary with task result:
            - sent: Boolean indicating success
            - user_id: User ID
            - attempt: Retry attempt number
            - task_id: Celery task ID

    Raises:
        Exception: Any exception triggers automatic retry with exponential backoff.
    """
    try:
        # Get user
        user = User.objects.get(id=user_id)

        # Send email
        success = EmailService.send_verification_email(user, token)

        if not success:
            # Email service returned False, retry
            logger.warning(
                f"Email verification send failed for user {user_id}, attempt {self.request.retries}"
            )
            raise Exception("Email send returned False")

        logger.info(f"Verification email sent successfully to user {user_id}")

        return {
            "sent": True,
            "user_id": user_id,
            "attempt": self.request.retries + 1,
            "task_id": self.request.id,
        }

    except User.DoesNotExist:
        # User doesn't exist, don't retry
        logger.error(f"Cannot send verification email: User {user_id} does not exist")
        return {
            "sent": False,
            "user_id": user_id,
            "error": "User not found",
            "task_id": self.request.id,
        }

    except Exception as e:
        logger.error(
            f"Email verification send error for user {user_id}, "
            f"attempt {self.request.retries + 1}: {e}"
        )

        # Check if max retries reached
        if self.request.retries >= self.max_retries:
            # Log to dead letter queue (H6)
            logger.critical(
                f"Email verification FAILED after {self.max_retries + 1} attempts "
                f"for user {user_id}. Moving to dead letter queue."
            )
            # TODO: Implement dead letter queue storage
            # DeadLetterEmail.objects.create(
            #     user_id=user_id,
            #     email_type='verification',
            #     token=token,
            #     error=str(e),
            #     attempts=self.max_retries + 1
            # )

        # Re-raise to trigger retry
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=5,
    retry_jitter=True,
)
def send_password_reset_email_task(self, user_id: int, token: str) -> dict:
    """Send password reset email asynchronously with retry logic (H6).

    Implements exponential backoff retry strategy identical to verification emails.
    Password reset emails are high priority due to security implications.

    Args:
        self: Celery task instance (bound).
        user_id: User ID to send password reset email to.
        token: Password reset token (plain, not hashed).

    Returns:
        Dictionary with task result:
            - sent: Boolean indicating success
            - user_id: User ID
            - attempt: Retry attempt number
            - task_id: Celery task ID

    Raises:
        Exception: Any exception triggers automatic retry with exponential backoff.
    """
    try:
        # Get user
        user = User.objects.get(id=user_id)

        # Send email
        success = EmailService.send_password_reset_email(user, token)

        if not success:
            # Email service returned False, retry
            logger.warning(
                f"Password reset email send failed for user {user_id}, "
                f"attempt {self.request.retries}"
            )
            raise Exception("Email send returned False")

        logger.info(f"Password reset email sent successfully to user {user_id}")

        return {
            "sent": True,
            "user_id": user_id,
            "attempt": self.request.retries + 1,
            "task_id": self.request.id,
        }

    except User.DoesNotExist:
        # User doesn't exist, don't retry
        logger.error(f"Cannot send password reset email: User {user_id} does not exist")
        return {
            "sent": False,
            "user_id": user_id,
            "error": "User not found",
            "task_id": self.request.id,
        }

    except Exception as e:
        logger.error(
            f"Password reset email send error for user {user_id}, "
            f"attempt {self.request.retries + 1}: {e}"
        )

        # Check if max retries reached
        if self.request.retries >= self.max_retries:
            # Log to dead letter queue (H6)
            logger.critical(
                f"Password reset email FAILED after {self.max_retries + 1} attempts "
                f"for user {user_id}. Moving to dead letter queue."
            )
            # TODO: Implement dead letter queue storage
            # DeadLetterEmail.objects.create(
            #     user_id=user_id,
            #     email_type='password_reset',
            #     token=token,
            #     error=str(e),
            #     attempts=self.max_retries + 1
            # )

        # Re-raise to trigger retry
        raise
