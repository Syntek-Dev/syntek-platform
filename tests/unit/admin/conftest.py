"""Shared fixtures for admin tests."""

from django.contrib.auth import get_user_model
from django.test import Client

import pytest

from apps.core.models import Organisation

User = get_user_model()


@pytest.fixture
def admin_client(db, admin_user):
    """Create authenticated admin client.

    Returns:
        Django test client authenticated as admin user
    """
    client = Client()
    client.force_login(admin_user)
    return client


@pytest.fixture
def admin_user(db):
    """Create superuser for admin tests.

    Returns:
        Superuser instance
    """
    org = Organisation.objects.create(
        name="Admin Organisation",
        slug="admin-org",
    )

    admin = User.objects.create_superuser(
        email="admin@example.com",
        password="adminpass123",
        first_name="Admin",
        last_name="User",
        organisation=org,
    )
    return admin
