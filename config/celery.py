"""Celery configuration for async task processing.

This module configures Celery for handling asynchronous tasks including
email sending with retry logic, background jobs, and scheduled tasks.

FEATURES:
- Async email delivery with exponential backoff (H6)
- Dead letter queue for failed tasks (H6)
- Task result storage in Redis
- Task monitoring and retry logic

Example:
    >>> from apps.core.tasks import send_verification_email_task
    >>> send_verification_email_task.delay(user_id)
"""

import os
from typing import TYPE_CHECKING

from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("backend_template")  # type: ignore[call-arg]

# Configure Celery using settings from Django settings.py.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks in all installed apps
# Import settings here to avoid circular imports during Celery initialisation
if TYPE_CHECKING:
    from django.conf import settings as django_settings

    _installed_apps: list[str] = django_settings.INSTALLED_APPS  # type: ignore[assignment]
else:
    from django.conf import settings

    _installed_apps = settings.INSTALLED_APPS

app.autodiscover_tasks(lambda: _installed_apps)


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery configuration.

    Args:
        self: Celery task instance.
    """
    import logging

    logger = logging.getLogger(__name__)
    logger.debug("Request: %r", self.request)
