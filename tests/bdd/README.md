# BDD Tests (Behaviour-Driven Development)

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team

---

## Table of Contents

- [BDD Tests (Behaviour-Driven Development)](#bdd-tests-behaviour-driven-development)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [Feature Files](#feature-files)
  - [Step Definitions](#step-definitions)
  - [Running Tests](#running-tests)
    - [Run All BDD Tests](#run-all-bdd-tests)
    - [Run Specific Feature](#run-specific-feature)
    - [Run with Verbose Output](#run-with-verbose-output)
    - [Run and Generate Report](#run-and-generate-report)
  - [Best Practices](#best-practices)
    - [1. Clear Scenario Names](#1-clear-scenario-names)
    - [2. Avoid Technical Details](#2-avoid-technical-details)
    - [3. Given-When-Then Structure](#3-given-when-then-structure)
    - [4. Reusable Steps](#4-reusable-steps)
    - [5. Scenario Outlines for Variations](#5-scenario-outlines-for-variations)

---

## Overview

BDD tests use Gherkin syntax to write human-readable test scenarios. Tests in this directory
validate behaviour from a user perspective using `pytest-bdd` framework.

---

## Directory Structure

```
bdd/
├── README.md              # This file
├── conftest.py            # BDD-specific pytest configuration
├── features/              # Gherkin feature files
│   └── *.feature          # Feature specifications
└── step_defs/             # Step definition implementations
    └── test_*_steps.py    # Step definitions for scenarios
```

---

## Feature Files

Feature files are written in Gherkin syntax and describe user-facing behaviour.

**Location:** `tests/bdd/features/`

**Naming Convention:** `[feature-name].feature`

**File Format:**

```gherkin
Feature: User Authentication
  As a registered user
  I want to log in to the system
  So that I can access my account

  Background:
    Given the system is running
    And the database is clean

  Scenario: Successful login with valid credentials
    Given a user with email "user@example.com" and password "secret123"
    When I submit login credentials:
      | email            | password  |
      | user@example.com | secret123 |
    Then I should be logged in
    And I should see the dashboard

  Scenario: Failed login with invalid password
    Given a user with email "user@example.com" and password "secret123"
    When I submit login credentials:
      | email            | password |
      | user@example.com | wrong    |
    Then I should not be logged in
    And I should see an error message "Invalid credentials"

  Scenario Outline: Login validation
    Given a user exists with email "<email>"
    When I attempt to login with password "<password>"
    Then the result should be "<result>"

    Examples:
      | email             | password  | result  |
      | user@example.com  | secret123 | success |
      | user@example.com  | wrong     | failure |
      | invalid@example.com | secret123 | failure |
```

---

## Step Definitions

Step definitions implement the Gherkin steps in Python.

**Location:** `tests/bdd/step_defs/`

**Naming Convention:** `test_[feature_name]_steps.py`

**Example:**

```python
# test_authentication_steps.py

import pytest
from pytest_bdd import given, when, then, scenarios, parsers
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

# Load scenarios from feature file
scenarios('../features/authentication.feature')


@given('the system is running')
def system_running():
    """Verify system is operational."""
    # System checks here
    pass


@given(parsers.parse('a user with email "{email}" and password "{password}"'))
def create_user(db, email: str, password: str):
    """Create a test user."""
    return User.objects.create_user(
        email=email,
        password=password
    )


@when('I submit login credentials:')
def submit_login(datatable):
    """Submit login form."""
    credentials = datatable[0]
    # Submit credentials
    return client.post('/api/auth/login/', credentials)


@then('I should be logged in')
def verify_logged_in(response):
    """Verify user is authenticated."""
    assert response.status_code == 200
    assert 'token' in response.json()
```

---

## Running Tests

### Run All BDD Tests

```bash
./scripts/env/test.sh run -m bdd
```

### Run Specific Feature

```bash
./scripts/env/test.sh run tests/bdd/step_defs/test_authentication_steps.py
```

### Run with Verbose Output

```bash
./scripts/env/test.sh run -vv tests/bdd/
```

### Run and Generate Report

```bash
./scripts/env/test.sh run --html=report.html tests/bdd/
```

---

## Best Practices

### 1. Clear Scenario Names

Use descriptive names that explain what is being tested:

```gherkin
# Good
Scenario: User can reset password with valid email
Scenario: System rejects duplicate organisation names
Scenario: Admin can view audit logs for organisation

# Bad
Scenario: Test password reset
Scenario: Check names
Scenario: View logs
```

### 2. Avoid Technical Details

Feature files are for non-technical stakeholders:

```gherkin
# Good - describes user action
When I enter my new password

# Bad - technical jargon
When I hash my password with bcrypt
```

### 3. Given-When-Then Structure

Follow the pattern consistently:

```gherkin
Given [precondition]      # Setup state
When [action]             # User performs action
Then [expected result]     # Verify outcome
```

### 4. Reusable Steps

Write generic steps that work across multiple scenarios:

```python
# Good - reusable step
@given(parsers.parse('a user with email "{email}"'))
def create_user(email):
    return User.objects.create_user(email=email)

# Bad - specific to one test
@given('a user admin@example.com exists')
def create_admin():
    return User.objects.create_user(email='admin@example.com')
```

### 5. Scenario Outlines for Variations

Use `Scenario Outline` when testing multiple similar cases:

```gherkin
# Good - tests multiple cases
Scenario Outline: User validation
  When I enter "<input>"
  Then the result should be "<result>"

  Examples:
    | input         | result |
    | user@test.com | valid  |
    | invalid       | error  |

# Bad - separate scenario for each case
Scenario: User validation 1
Scenario: User validation 2
```

---

**Last Updated:** 08/01/2026
