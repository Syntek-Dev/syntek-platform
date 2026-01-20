# Security Penetration Tests

**Last Updated**: 17/01/2026
**Purpose**: Security penetration testing for US-001 User Authentication
**Test Type**: Security, Penetration Testing
**Markers**: `@pytest.mark.security`, `@pytest.mark.penetration`

---

## Overview

This directory contains security penetration tests that verify the authentication system's
resistance to common attacks and vulnerabilities.

## Test Categories

### 1. Token Security Tests

- **File**: `test_token_security.py`
- **Coverage**: Token brute-force resistance (C1), TOTP secret extraction (C2)

### 2. CSRF and XSS Tests

- **File**: `test_csrf_xss_protection.py`
- **Coverage**: CSRF bypass attempts (C4), XSS injection prevention

### 3. Email Verification Bypass Tests

- **File**: `test_email_verification_bypass.py`
- **Coverage**: Email verification bypass attempts (C5)

### 4. SQL Injection and Input Validation

- **File**: `test_sql_injection_prevention.py`
- **Coverage**: SQL injection attempts, input validation

## Running Security Tests

```bash
# Run all security tests
./scripts/env/test.sh run -m security

# Run penetration tests only
./scripts/env/test.sh run -m penetration

# Run specific security test file
./scripts/env/test.sh run tests/security/test_token_security.py
```

## Security Test Markers

| Marker                     | Purpose                                 |
| -------------------------- | --------------------------------------- |
| `@pytest.mark.security`    | General security test                   |
| `@pytest.mark.penetration` | Penetration testing (attack simulation) |
| `@pytest.mark.slow`        | Long-running security tests             |

## Test Coverage Map

| Critical Fix | Test File                                         | Test Method                                 |
| ------------ | ------------------------------------------------- | ------------------------------------------- |
| C1           | `test_token_security.py`                          | `test_session_token_brute_force_resistance` |
| C2           | `test_token_security.py`                          | `test_totp_secret_extraction_prevented`     |
| C3           | `../e2e/test_password_reset_hash_verification.py` | (Covered in E2E)                            |
| C4           | `test_csrf_xss_protection.py`                     | `test_csrf_bypass_attempts_blocked`         |
| C5           | `test_email_verification_bypass.py`               | `test_email_verification_bypass_blocked`    |
| C6           | `test_token_security.py`                          | `test_ip_encryption_key_rotation_secure`    |

## Security Testing Best Practices

1. **Isolation**: Security tests run in isolated environments
2. **Cleanup**: Always clean up after attack simulations
3. **Documentation**: Document attack vectors and expected defences
4. **No Real Attacks**: Tests simulate attacks, never perform real attacks
5. **Rate Limiting**: Be mindful of rate limits during tests

---

**Last Updated**: 2026-01-17
