# Core Utils

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team

---

## Overview

This directory contains utility functions and helper modules for the core application.

**File Structure:**

```
utils/
├── __init__.py                    # Utility exports
└── signed_urls.py                 # Token generation and verification
```

---

## Utilities

### Signed URLs (`signed_urls.py`)

Generates and validates secure, time-limited tokens for sensitive operations like email
verification and password resets.

**Key Functions:**

| Function                              | Purpose                                  | Returns        |
| ------------------------------------- | ---------------------------------------- | -------------- |
| `generate_email_verification_token()` | Create email verification token          | `str` (token)  |
| `verify_email_token()`                | Validate and consume email token         | `User \| None` |
| `generate_password_reset_token()`     | Create password reset token              | `str` (token)  |
| `verify_password_reset_token()`       | Validate and consume reset token         | `User \| None` |
| `is_token_valid()`                    | Check if token exists and is not expired | `bool`         |
| `get_token_expiry_minutes()`          | Get token expiry time in minutes         | `int`          |

**Security Features:**

- HMAC-SHA256 signatures
- Time-limited tokens (configurable expiry)
- Single-use tokens (consumed after verification)
- IP address binding (optional)
- User-specific tokens (cannot be reused for other users)

**Usage Examples:**

```python
from apps.core.utils.signed_urls import (
    generate_email_verification_token,
    verify_email_token,
    generate_password_reset_token,
    verify_password_reset_token,
)

# Email Verification
token = generate_email_verification_token(user)
verification_url = f"https://example.com/verify-email/{token}/"
# Send email to user

# User clicks link
verified_user = verify_email_token(token)
if verified_user:
    verified_user.email_verified = True
    verified_user.save()

# Password Reset
reset_token = generate_password_reset_token(user)
reset_url = f"https://example.com/reset-password/{reset_token}/"
# Send email to user

# User submits new password
reset_user = verify_password_reset_token(reset_token)
if reset_user:
    reset_user.set_password(new_password)
    reset_user.save()
```

**Configuration:**

Token expiry times are configured in Django settings:

```python
# settings.py
TOKEN_EXPIRY_MINUTES = {
    'email_verification': 24 * 60,  # 24 hours
    'password_reset': 1 * 60,       # 1 hour
}
```

---

**Last Updated:** 08/01/2026
