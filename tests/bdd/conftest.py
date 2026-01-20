"""pytest-bdd configuration and fixtures.

This module provides BDD-specific fixtures and configuration for pytest-bdd tests.
"""

import pytest


@pytest.fixture
def bdd_context():
    """Shared context dictionary for BDD tests.

    Returns:
        dict: Empty context dictionary for storing test state.
    """
    return {}


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Ensure database access is enabled for all BDD tests.

    This fixture automatically requests the pytest-django `db` fixture
    for all tests in the BDD test directory, ensuring the test database
    is created and migrations are applied.

    Args:
        db: pytest-django database fixture that sets up the test database.
    """
    pass
