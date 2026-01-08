# BDD Step Definitions

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team

---

## Overview

Step definitions implement Gherkin steps from feature files in Python code using pytest-bdd.

**File Structure:**

```
step_defs/
├── README.md              # This file
└── test_*.py              # Step definition modules
```

---

## Step Definition Files

Step definitions are Python files that implement Gherkin steps.

**Naming Convention:** `test_[feature_name]_steps.py`

**Example Files:**

```
step_defs/
├── test_authentication_steps.py      # Authentication steps
├── test_user_management_steps.py     # User steps
├── test_organisation_steps.py         # Organisation steps
└── ...
```

---

## Step Definition Pattern

```python
# test_authentication_steps.py

import pytest
from pytest_bdd import given, when, then, scenarios, parsers
from django.contrib.auth import get_user_model

User = get_user_model()

# Load all scenarios from feature file
scenarios('../features/authentication.feature')


# Given steps
@given('the system is running')
def system_running():
    """Verify system is operational."""
    pass


@given(parsers.parse('a user with email "{email}"'))
def create_user(db, email: str):
    """Create a test user."""
    return User.objects.create_user(email=email, password="test123")


# When steps
@when('I submit login credentials:')
def submit_login(datatable):
    """Submit login form."""
    credentials = datatable[0]
    # Submit credentials
    pass


# Then steps
@then('I should be logged in')
def verify_logged_in():
    """Verify user is authenticated."""
    # Assertion here
    pass
```

---

## Best Practices

### 1. Reusable Steps

Write steps that can be used in multiple scenarios:

```python
# Good - reusable
@given(parsers.parse('a user with email "{email}"'))
def create_user(db, email: str):
    return User.objects.create_user(email=email)

# Bad - specific to one test
@given('a user admin@example.com exists')
def create_admin():
    return User.objects.create_user(email='admin@example.com')
```

### 2. Clear Step Names

Step names should be readable:

```python
# Good - what the step does is clear
@when('I submit login credentials')
def submit_login():
    pass

# Bad - ambiguous
@when('I do the thing')
def do_thing():
    pass
```

### 3. Use Parametrised Steps

Use `parsers` for flexible steps:

```python
# Good - works for any email
@given(parsers.parse('a user with email "{email}"'))
def create_user(email):
    return User.objects.create_user(email=email)

# Bad - hardcoded
@given('a user with email "test@example.com"')
def create_user():
    return User.objects.create_user(email="test@example.com")
```

### 4. Share Fixtures

Use pytest fixtures for common test data:

```python
# conftest.py
@pytest.fixture
def authenticated_user(db):
    return User.objects.create_user(
        email="user@example.com",
        password="test123"
    )

# In step definitions
def my_step(authenticated_user):
    # Use the user
    pass
```

---

**Last Updated:** 08/01/2026
