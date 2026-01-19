"""Celery tasks for the core application.

This module exports all Celery tasks for async processing.
Tasks are only available when Celery is installed.
"""

# Try to import Celery tasks - gracefully handle if Celery not installed
try:
    from apps.core.tasks.email_tasks import (
        send_password_reset_email_task,
        send_verification_email_task,
    )
    from apps.core.tasks.gdpr_tasks import (
        cleanup_expired_exports_task,
        cleanup_expired_tokens_task,
        process_account_deletion_task,
        process_data_export_task,
    )

    __all__ = [
        "cleanup_expired_exports_task",
        "cleanup_expired_tokens_task",
        "process_account_deletion_task",
        "process_data_export_task",
        "send_password_reset_email_task",
        "send_verification_email_task",
    ]
except ImportError:
    # Celery not installed - tasks not available
    cleanup_expired_exports_task = None
    cleanup_expired_tokens_task = None
    process_account_deletion_task = None
    process_data_export_task = None
    send_password_reset_email_task = None
    send_verification_email_task = None
    __all__ = []
