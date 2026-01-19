"""Celery tasks for GDPR compliance operations.

This module implements async processing for GDPR operations including:
- Data export generation (Article 15)
- Account deletion processing (Article 17)
- Expired export cleanup (maintenance)

GDPR Requirements:
- Data exports must be processed within 30 days (we target <24 hours)
- Account deletions must be processed promptly after confirmation
- Expired exports must be cleaned up for storage management

Example:
    >>> from apps.core.tasks.gdpr_tasks import process_data_export_task
    >>> process_data_export_task.delay(str(export_request.id))
"""

import logging
from uuid import UUID

from celery import shared_task

from apps.core.services.account_deletion_service import AccountDeletionService
from apps.core.services.data_export_service import DataExportService

logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    retry_jitter=True,
)
def process_data_export_task(self, request_id: str) -> dict:
    """Process a data export request asynchronously.

    Generates the export file containing all user personal data in
    the requested format (JSON or CSV).

    Implements exponential backoff retry strategy:
    - Attempt 1: Immediate
    - Attempt 2: 1s delay
    - Attempt 3: 2s delay
    - Attempt 4: 4s delay (final)

    Args:
        self: Celery task instance (bound).
        request_id: UUID string of the DataExportRequest.

    Returns:
        Dictionary with task result:
            - processed: Boolean indicating success
            - request_id: Export request ID
            - file_size: Size of generated file in bytes
            - attempt: Retry attempt number
            - task_id: Celery task ID

    Raises:
        Exception: Any exception triggers automatic retry.
    """
    try:
        export_request = DataExportService.process_export(UUID(request_id))

        logger.info(f"Data export processed successfully: {request_id}")

        return {
            "processed": True,
            "request_id": request_id,
            "file_size": export_request.metadata.get("file_size"),
            "attempt": self.request.retries + 1,
            "task_id": self.request.id,
        }

    except Exception as e:
        logger.error(
            f"Data export processing error for {request_id}, "
            f"attempt {self.request.retries + 1}: {e}"
        )

        if self.request.retries >= self.max_retries:
            logger.critical(
                f"Data export FAILED after {self.max_retries + 1} attempts "
                f"for request {request_id}."
            )

        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,
    max_retries=3,
    retry_jitter=True,
)
def process_account_deletion_task(self, request_id: str) -> dict:
    """Process an account deletion request asynchronously.

    Executes the account deletion including data anonymisation
    and user account removal.

    Note: This task should only be called after the user has confirmed
    the deletion request via the confirmation token.

    Args:
        self: Celery task instance (bound).
        request_id: UUID string of the AccountDeletionRequest.

    Returns:
        Dictionary with task result:
            - processed: Boolean indicating success
            - request_id: Deletion request ID
            - attempt: Retry attempt number
            - task_id: Celery task ID

    Raises:
        Exception: Any exception triggers automatic retry.
    """
    try:
        deletion_request = AccountDeletionService.process_deletion(UUID(request_id))

        logger.info(f"Account deletion processed successfully: {request_id}")

        return {
            "processed": True,
            "request_id": request_id,
            "status": deletion_request.status,
            "attempt": self.request.retries + 1,
            "task_id": self.request.id,
        }

    except Exception as e:
        logger.error(
            f"Account deletion processing error for {request_id}, "
            f"attempt {self.request.retries + 1}: {e}"
        )

        if self.request.retries >= self.max_retries:
            logger.critical(
                f"Account deletion FAILED after {self.max_retries + 1} attempts "
                f"for request {request_id}. Manual intervention required."
            )

        raise


@shared_task
def cleanup_expired_exports_task() -> dict:
    """Clean up expired data exports.

    Removes expired export files from storage and updates
    request statuses. Should be scheduled to run daily.

    Celery Beat schedule example:
        'cleanup-expired-exports': {
            'task': 'apps.core.tasks.gdpr_tasks.cleanup_expired_exports_task',
            'schedule': crontab(hour=3, minute=0),  # Run at 3 AM daily
        }

    Returns:
        Dictionary with cleanup results:
            - cleaned: Number of exports cleaned up
            - task_id: Celery task ID
    """
    try:
        count = DataExportService.cleanup_expired_exports()

        logger.info(f"Cleaned up {count} expired data exports")

        return {
            "cleaned": count,
            "success": True,
        }

    except Exception as e:
        logger.error(f"Export cleanup failed: {e}")
        return {
            "cleaned": 0,
            "success": False,
            "error": str(e),
        }


@shared_task
def cleanup_expired_tokens_task() -> dict:
    """Clean up expired session tokens.

    Removes expired session tokens from the database.
    Should be scheduled to run daily.

    Returns:
        Dictionary with cleanup results:
            - cleaned: Number of tokens cleaned up
            - success: Boolean indicating success
    """
    try:
        from apps.core.services.token_service import TokenService

        count = TokenService.cleanup_expired_tokens()

        logger.info(f"Cleaned up {count} expired session tokens")

        return {
            "cleaned": count,
            "success": True,
        }

    except Exception as e:
        logger.error(f"Token cleanup failed: {e}")
        return {
            "cleaned": 0,
            "success": False,
            "error": str(e),
        }
