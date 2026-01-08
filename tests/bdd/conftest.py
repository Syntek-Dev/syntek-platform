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
