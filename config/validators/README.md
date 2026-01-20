# Custom Validators

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

Custom form and field validators for data validation.

## Table of Contents

- [Custom Validators](#custom-validators)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Validator Files](#validator-files)
    - [password.py](#passwordpy)
  - [How Validators Work](#how-validators-work)
    - [Validator Pattern](#validator-pattern)
    - [Using Validators](#using-validators)
  - [Creating New Validators](#creating-new-validators)
    - [Step 1: Create Validator Function](#step-1-create-validator-function)
    - [Step 2: Import in validators/**init**.py](#step-2-import-in-validatorsinitpy)
    - [Step 3: Use in Models/Forms](#step-3-use-in-modelsforms)
    - [Step 4: Add Tests](#step-4-add-tests)
  - [Best Practices](#best-practices)
    - [1. Clear Error Messages](#1-clear-error-messages)
    - [2. Error Codes for i18n](#2-error-codes-for-i18n)
    - [3. Handle Edge Cases](#3-handle-edge-cases)
    - [4. Document Requirements](#4-document-requirements)
    - [5. Reuse Existing Validators](#5-reuse-existing-validators)
  - [Common Validators](#common-validators)
    - [Email Domain Validator](#email-domain-validator)
    - [Phone Number Validator](#phone-number-validator)
    - [File Size Validator](#file-size-validator)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains custom validators for Django forms and model fields.

**Purpose:** Validate incoming data and provide user-friendly error messages.

---

## Directory Tree

```
config/validators/
├── README.md                  # This file - Validators overview and guide
├── __init__.py                # Package initialisation and exports
└── password.py                # Password validation rules and strength checking
```

---

## Validator Files

### password.py

Password validation rules and strength checking.

**Validator Functions:**

```python
def validate_password_strength(password: str) -> None:
    """Validate password meets strength requirements.

    Requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character

    Raises:
        ValidationError: If password does not meet requirements
    """
```

**Usage in Models:**

```python
from django.contrib.auth.models import User
from config.validators import validate_password_strength


class UserProfile(models.Model):
    """User profile with strong password requirement."""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    password_hash = models.CharField(
        max_length=255,
        validators=[validate_password_strength]
    )
```

**Usage in Forms:**

```python
from django import forms
from config.validators import validate_password_strength


class PasswordChangeForm(forms.Form):
    """Form for changing password."""

    new_password = forms.CharField(
        widget=forms.PasswordInput,
        validators=[validate_password_strength]
    )
```

**Error Messages:**

```
"Password must be at least 12 characters long."
"Password must contain at least one uppercase letter."
"Password must contain at least one lowercase letter."
"Password must contain at least one digit."
"Password must contain at least one special character."
```

---

## How Validators Work

### Validator Pattern

```python
def validate_something(value):
    """Validate value.

    Args:
        value: The value to validate.

    Raises:
        ValidationError: If validation fails.
    """
    if not condition_met(value):
        raise ValidationError(
            "Error message for user",
            code="error_code"
        )
```

### Using Validators

```python
# In models
from django.db import models
from config.validators import validate_something


class MyModel(models.Model):
    field = models.CharField(validators=[validate_something])


# In forms
from django import forms
from config.validators import validate_something


class MyForm(forms.Form):
    field = forms.CharField(validators=[validate_something])


# Standalone validation
from config.validators import validate_something
from django.core.exceptions import ValidationError

try:
    validate_something(user_input)
except ValidationError as e:
    print(f"Validation failed: {e.message}")
```

---

## Creating New Validators

### Step 1: Create Validator Function

```python
# In config/validators/my_validator.py
"""Custom validators for my_field."""

from django.core.exceptions import ValidationError
from typing import Any


def validate_my_field(value: Any) -> None:
    """Validate my_field value.

    Args:
        value: The value to validate.

    Raises:
        ValidationError: If validation fails.
    """
    if not is_valid(value):
        raise ValidationError(
            "Error message displayed to user",
            code="my_error_code"
        )
```

### Step 2: Import in validators/**init**.py

```python
# In config/validators/__init__.py
from .password import validate_password_strength
from .my_validator import validate_my_field

__all__ = [
    "validate_password_strength",
    "validate_my_field",
]
```

### Step 3: Use in Models/Forms

```python
# In a model
from config.validators import validate_my_field


class MyModel(models.Model):
    my_field = models.CharField(validators=[validate_my_field])


# In a form
from config.validators import validate_my_field


class MyForm(forms.Form):
    my_field = forms.CharField(validators=[validate_my_field])
```

### Step 4: Add Tests

```python
# In tests/validators/test_my_validator.py
"""Tests for my_validator."""

from django.test import TestCase
from django.core.exceptions import ValidationError
from config.validators import validate_my_field


class ValidateMyFieldTestCase(TestCase):
    """Test cases for validate_my_field validator."""

    def test_valid_value(self) -> None:
        """Test validation passes for valid value."""
        try:
            validate_my_field("valid_value")
        except ValidationError:
            self.fail("Valid value raised ValidationError")

    def test_invalid_value(self) -> None:
        """Test validation fails for invalid value."""
        with self.assertRaises(ValidationError):
            validate_my_field("invalid_value")

    def test_error_message(self) -> None:
        """Test validation error message."""
        try:
            validate_my_field("invalid")
        except ValidationError as e:
            self.assertIn("Error message", str(e))
```

---

## Best Practices

### 1. Clear Error Messages

```python
# Good: Clear, actionable error message
raise ValidationError(
    "Email address must be from company domain (@example.com)",
    code="invalid_email_domain"
)

# Bad: Vague error message
raise ValidationError("Invalid email")
```

### 2. Error Codes for i18n

```python
# Use error codes for internationalization
raise ValidationError(
    _("Value must be positive"),  # Translatable message
    code="not_positive"  # Error code for programmatic handling
)
```

### 3. Handle Edge Cases

```python
def validate_positive_number(value: Any) -> None:
    """Validate positive number."""
    if value is None:
        raise ValidationError("Value cannot be empty")

    try:
        num = float(value)
    except (TypeError, ValueError):
        raise ValidationError("Value must be a number")

    if num <= 0:
        raise ValidationError("Value must be positive")
```

### 4. Document Requirements

```python
def validate_username(value: str) -> None:
    """Validate username format.

    Requirements:
    - 3-20 characters long
    - Alphanumeric and underscore only
    - Must start with letter
    - Must end with alphanumeric

    Args:
        value: Username to validate.

    Raises:
        ValidationError: If username doesn't meet requirements.
    """
    pass
```

### 5. Reuse Existing Validators

```python
from django.core.validators import (
    EmailValidator,
    URLValidator,
    MinLengthValidator,
    MaxLengthValidator,
    RegexValidator,
)

# Use built-in validators when possible
email_field = models.EmailField(
    validators=[EmailValidator(message="Invalid email format")]
)

# Combine multiple validators
username_field = models.CharField(
    max_length=20,
    validators=[
        MinLengthValidator(3),
        RegexValidator(r"^[a-zA-Z][a-zA-Z0-9_]*$")
    ]
)
```

---

## Common Validators

### Email Domain Validator

```python
import re
from django.core.exceptions import ValidationError


def validate_company_email(value: str) -> None:
    """Validate email is from company domain."""
    allowed_domains = ["company.com", "subsidiary.com"]

    domain = value.split("@")[1] if "@" in value else ""

    if domain not in allowed_domains:
        raise ValidationError(
            f"Email must be from {', '.join(allowed_domains)}",
            code="invalid_domain"
        )
```

### Phone Number Validator

```python
import re
from django.core.exceptions import ValidationError


def validate_phone_number(value: str) -> None:
    """Validate phone number format."""
    # Remove common separators
    clean = re.sub(r"[\s\-\(\)]", "", value)

    if not re.match(r"^\+?1?\d{10,14}$", clean):
        raise ValidationError(
            "Invalid phone number format",
            code="invalid_phone"
        )
```

### File Size Validator

```python
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile


def validate_file_size(file: UploadedFile, max_size_mb: int = 10) -> None:
    """Validate uploaded file size.

    Args:
        file: The uploaded file.
        max_size_mb: Maximum allowed size in MB.

    Raises:
        ValidationError: If file exceeds size limit.
    """
    max_bytes = max_size_mb * 1024 * 1024

    if file.size > max_bytes:
        raise ValidationError(
            f"File size must not exceed {max_size_mb}MB",
            code="file_too_large"
        )
```

---

## Related Documentation

- [Configuration Overview](../README.md) - Config directory overview
- [Django Validators Docs](https://docs.djangoproject.com/en/5.2/ref/validators/) - Official Django validators
- [Form Validation](https://docs.djangoproject.com/en/5.2/ref/forms/validation/) - Django form validation

---

**Last Updated:** 2026-01-03
