# BDD Feature Files

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team

---

## Overview

This directory contains Gherkin feature files that describe system behaviour in plain language.

**File Structure:**

```
features/
├── README.md              # This file
└── *.feature              # Feature specifications
```

---

## Feature Files

Feature files are written in Gherkin syntax. Each file describes a feature and its scenarios.

**Naming Convention:** `[feature-name].feature`

**Example Files:**

```
features/
├── authentication.feature      # User login/register
├── user_management.feature     # User administration
├── organisation.feature        # Organisation management
├── content_publishing.feature  # Content workflows
└── ...
```

---

## Feature File Format

```gherkin
Feature: User Authentication
  As a registered user
  I want to log in to the system
  So that I can access my account

  Background:
    Given the system is running

  Scenario: Successful login
    Given a user with email "user@example.com"
    When I submit login credentials
    Then I should be logged in
```

---

## Guidelines

### 1. Clear Feature Descriptions

```gherkin
# Good - explains value
Feature: User Authentication
  As a registered user
  I want to log in
  So that I can access my account

# Bad - vague
Feature: Login
```

### 2. Descriptive Scenario Names

```gherkin
# Good
Scenario: User can reset password with valid email
Scenario: System prevents duplicate organisation names
Scenario: Admin can view audit logs

# Bad
Scenario: Test password
Scenario: Check names
Scenario: View logs
```

### 3. Simple Gherkin Syntax

Keep scenarios readable and maintainable:

```gherkin
# Good - clear steps
Scenario: User registration
  When I fill in the registration form
  And I click sign up
  Then I should receive a confirmation email

# Bad - too technical
Scenario: User can POST to /api/auth/register with JSON payload
  When I POST {"email": "...", "password": "..."}
  Then the response contains JWT token
```

---

**Last Updated:** 08/01/2026
