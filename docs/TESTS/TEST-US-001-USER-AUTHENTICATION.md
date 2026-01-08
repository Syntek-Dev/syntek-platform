# Test Specification: US-001 User Authentication - Phase 1

**Last Updated**: 07/01/2026
**User Story**: US-001
**Phase**: Phase 1 - Core Models and Database
**Test Status**: Ready for Implementation
**Test Writer**: Test Writer Agent

---

## Overview

This document specifies all tests for Phase 1 of US-001 User Authentication, which focuses on database models, migrations, and core validation logic. It includes comprehensive unit tests, BDD feature tests, and security-focused test specifications.

The test specification covers:

- Core model tests for User, Organisation, and authentication-related models
- Token model tests including BaseToken, SessionToken, and verification tokens
- Security model tests for TOTP devices and password history
- Password validator tests with edge case coverage
- BDD feature tests for user registration workflows
- Test coverage analysis and targets
- Expected test results and execution commands

---

## Table of Contents

- [Test Specification: US-001 User Authentication - Phase 1](#test-specification-us-001-user-authentication---phase-1)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Test Coverage Summary](#test-coverage-summary)
  - [Models Under Test](#models-under-test)
    - [Critical Security Fields](#critical-security-fields)
  - [Unit Tests (TDD)](#unit-tests-tdd)
    - [Organisation Model Tests](#organisation-model-tests)
    - [User Model Tests](#user-model-tests)
    - [BaseToken Abstract Model Tests](#basetoken-abstract-model-tests)
    - [SessionToken Model Tests](#sessiontoken-model-tests)
    - [PasswordResetToken Model Tests](#passwordresettoken-model-tests)
    - [EmailVerificationToken Model Tests](#emailverificationtoken-model-tests)
    - [TOTPDevice Model Tests](#totpdevice-model-tests)
    - [UserProfile Model Tests](#userprofile-model-tests)
    - [AuditLog Model Tests](#auditlog-model-tests)
    - [PasswordHistory Model Tests](#passwordhistory-model-tests)
  - [Validator Tests](#validator-tests)
    - [MinimumLengthValidator Tests](#minimumlengthvalidator-tests)
    - [PasswordComplexityValidator Tests](#passwordcomplexityvalidator-tests)
    - [BreachedPasswordValidator Tests](#breachedpasswordvalidator-tests)
    - [PasswordHistoryValidator Tests](#passwordhistoryvalidator-tests)
  - [BDD Feature Tests](#bdd-feature-tests)
  - [Test Execution](#test-execution)
    - [Run All Phase 1 Tests](#run-all-phase-1-tests)
    - [Run Specific Model Tests](#run-specific-model-tests)
  - [Expected Test Results](#expected-test-results)

---

## Test Coverage Summary

| Component              | Test File                              | Test Count  | Status |
| ---------------------- | -------------------------------------- | ----------- | ------ |
| Organisation Model     | test_organisation_model.py             | 17          | Ready  |
| User Model             | test_user_model.py                     | 25          | Ready  |
| BaseToken Model        | test_base_token_model.py               | 10          | Ready  |
| SessionToken Model     | test_session_token_model.py            | TBD         | Ready  |
| PasswordResetToken     | test_password_reset_token_model.py     | TBD         | Ready  |
| EmailVerificationToken | test_email_verification_token_model.py | TBD         | Ready  |
| TOTPDevice Model       | test_totp_device_model.py              | 15          | Ready  |
| UserProfile Model      | test_user_profile_model.py             | TBD         | Ready  |
| AuditLog Model         | test_audit_log_model.py                | TBD         | Ready  |
| PasswordHistory Model  | test_password_history_model.py         | TBD         | Ready  |
| Password Validators    | test_validators.py                     | 18          | Ready  |
| UserManager            | test_user_manager.py                   | TBD         | Ready  |
| **Total Unit Tests**   | -                                      | **85+**     | Ready  |
| BDD Feature Tests      | user_registration.feature              | 8 scenarios | Ready  |

## Models Under Test

### Critical Security Fields

| Model           | Security Field     | Test Focus                               |
| --------------- | ------------------ | ---------------------------------------- |
| User            | password           | Argon2 hashing, complexity validation    |
| User            | last_login_ip      | IP address encryption (BinaryField)      |
| TOTPDevice      | secret             | Fernet encryption with separate key (C2) |
| AuditLog        | ip_address         | IP address encryption                    |
| SessionToken    | token_hash         | HMAC-SHA256 hashing (not plain SHA-256)  |
| SessionToken    | device_fingerprint | Device tracking (H8)                     |
| SessionToken    | token_family       | Replay detection (H9)                    |
| PasswordHistory | password_hash      | Password reuse prevention (H11)          |

## Unit Tests (TDD)

### Organisation Model Tests

**File**: `tests/unit/apps/core/test_organisation_model.py`

| Test Name                                    | Purpose                           |
| -------------------------------------------- | --------------------------------- |
| test_organisation_creation_with_valid_data   | Verify creation with valid data   |
| test_organisation_slug_must_be_unique        | Ensure slug uniqueness constraint |
| test_organisation_name_required              | Verify name is required           |
| test_organisation_slug_required              | Verify slug is required           |
| test_organisation_slug_max_length            | Verify slug max length (255)      |
| test_organisation_name_max_length            | Verify name max length (255)      |
| test_organisation_industry_optional          | Industry field is optional        |
| test_organisation_is_active_defaults_to_true | Verify default is_active value    |
| test_organisation_can_be_deactivated         | Test deactivation workflow        |
| test_organisation_str_representation         | Verify **str** method             |
| test_organisation_created_at_auto_set        | Verify auto_now_add timestamp     |
| test_organisation_updated_at_auto_updates    | Verify auto_now timestamp updates |
| test_organisation_slug_allows_hyphens        | Hyphenated slugs allowed          |
| test_organisation_slug_validation_format     | Invalid characters rejected       |
| test_organisation_industry_max_length        | Industry max length (100)         |
| test_organisation_ordering_by_name           | Default ordering by name          |
| test_organisation_queryset_active_filter     | Filter active organisations       |

### User Model Tests

**File**: `tests/unit/apps/core/test_user_model.py`

| Test Name                                        | Purpose                                 |
| ------------------------------------------------ | --------------------------------------- |
| test_user_creation_with_valid_data               | Create user with valid data             |
| test_user_email_must_be_unique                   | Email uniqueness constraint             |
| test_user_email_validation_format                | Invalid email format rejected           |
| test_user_email_required                         | Email is required                       |
| test_user_email_max_length                       | Email max length (255)                  |
| test_user_password_is_hashed                     | Password hashed with Argon2             |
| test_user_check_password_correct                 | check_password() works                  |
| test_user_check_password_incorrect               | check_password() rejects wrong password |
| test_user_organisation_can_be_null_for_superuser | Superusers can have null organisation   |
| test_user_email_verified_defaults_to_false       | email_verified defaults to False        |
| test_user_email_verified_at_set_on_verification  | email_verified_at timestamp set         |
| test_user_two_factor_enabled_defaults_to_false   | 2FA disabled by default                 |
| test_user_two_factor_can_be_enabled              | 2FA can be enabled                      |
| test_user_last_login_ip_is_encrypted             | IP stored as encrypted binary           |
| test_user_has_email_account_defaults_to_false    | has_email_account defaults False        |
| test_user_has_vault_access_defaults_to_false     | has_vault_access defaults False         |
| test_user_password_changed_at_tracking           | password_changed_at updated             |
| test_user_get_full_name_method                   | get_full_name() returns full name       |
| test_user_get_short_name_method                  | get_short_name() returns first name     |
| test_user_str_representation                     | **str** returns email                   |
| test_user_is_active_defaults_to_true             | is_active defaults True                 |
| test_user_can_be_deactivated                     | User can be deactivated                 |
| test_user_email_case_insensitive                 | Email uniqueness is case-insensitive    |
| test_user_created_at_auto_set                    | created_at auto-set on creation         |
| test_user_updated_at_auto_updates                | updated_at auto-updates on save         |

### BaseToken Abstract Model Tests

**File**: `tests/unit/apps/core/test_base_token_model.py`

| Test Name                                           | Purpose                                   |
| --------------------------------------------------- | ----------------------------------------- |
| test_base_token_cannot_be_instantiated              | Abstract model cannot be created directly |
| test_token_is_expired_when_expires_at_in_past       | is_expired() returns True when expired    |
| test_token_is_not_expired_when_expires_at_in_future | is_expired() returns False when valid     |
| test_token_is_valid_when_not_expired_and_not_used   | is_valid() returns True when usable       |
| test_token_is_not_valid_when_expired                | is_valid() returns False when expired     |
| test_token_is_not_valid_when_used                   | is_valid() returns False when used        |
| test_token_used_at_is_set_when_marked_as_used       | used_at timestamp set when used           |
| test_token_hash_is_unique                           | token_hash must be unique                 |
| test_token_uses_uuid_primary_key                    | Tokens use UUID as PK                     |
| test_token_created_at_auto_set                      | created_at auto-set on creation           |
| test_token_used_defaults_to_false                   | used defaults to False                    |

### SessionToken Model Tests

**File**: `tests/unit/apps/core/test_session_token_model.py`

Extends BaseToken tests with additional fields:

- token_family for replay detection (H9)
- is_refresh_token_used tracking
- device_fingerprint for device tracking (H8)
- last_activity_at for session timeout (M8)

### PasswordResetToken Model Tests

**File**: `tests/unit/apps/core/test_password_reset_token_model.py`

Tests specific to password reset workflow:

- 15-minute expiration window
- Single-use enforcement
- User association

### EmailVerificationToken Model Tests

**File**: `tests/unit/apps/core/test_email_verification_token_model.py`

Tests specific to email verification:

- 24-hour expiration window
- Single-use enforcement
- User association

### TOTPDevice Model Tests

**File**: `tests/unit/apps/core/test_totp_device_model.py`

| Test Name                                      | Purpose                                  |
| ---------------------------------------------- | ---------------------------------------- |
| test_totp_device_creation_with_valid_data      | Create device with valid data            |
| test_totp_secret_is_stored_as_encrypted_binary | Secret stored as encrypted BinaryField   |
| test_totp_set_secret_encrypts_plain_secret     | set_secret() uses Fernet encryption (C2) |
| test_totp_get_secret_decrypts_encrypted_secret | get_secret() decrypts secret             |
| test_totp_device_name_allows_multiple_devices  | Multiple devices per user (H13)          |
| test_totp_device_name_max_length               | device_name max length (100)             |
| test_totp_device_name_defaults_to_default      | Default device name is 'Default'         |
| test_totp_confirmed_defaults_to_false          | confirmed defaults False                 |
| test_totp_can_be_confirmed                     | Device can be confirmed                  |
| test_totp_last_used_at_initially_null          | last_used_at starts null                 |
| test_totp_last_used_at_updated_on_use          | last_used_at updated on use              |
| test_totp_user_can_have_multiple_devices       | User can have 3+ devices                 |
| test_totp_device_deletion_does_not_delete_user | Deleting device keeps user               |
| test_totp_user_deletion_cascades_to_devices    | Deleting user cascades to devices        |
| test_totp_str_representation                   | **str** shows user and device name       |
| test_totp_encryption_uses_separate_fernet_key  | Uses separate key (not SECRET_KEY)       |

### UserProfile Model Tests

**File**: `tests/unit/apps/core/test_user_profile_model.py`

Tests for OneToOne relationship with User:

- phone_number validation
- avatar field handling
- User cascade behavior

### AuditLog Model Tests

**File**: `tests/unit/apps/core/test_audit_log_model.py`

Tests for audit trail:

- User and organisation association
- IP address encryption
- Action tracking
- Metadata JSON field

### PasswordHistory Model Tests

**File**: `tests/unit/apps/core/test_password_history_model.py`

Tests for password reuse prevention (H11):

- Password hash storage
- Last 5 passwords tracked
- User cascade behavior

## Validator Tests

### MinimumLengthValidator Tests

| Test Name                                    | Purpose                 |
| -------------------------------------------- | ----------------------- |
| test_password_meets_minimum_length_12_chars  | 12-char password passes |
| test_password_below_minimum_length_fails     | <12 chars fails         |
| test_password_above_maximum_length_128_fails | >128 chars fails        |

### PasswordComplexityValidator Tests

| Test Name                                  | Purpose                    |
| ------------------------------------------ | -------------------------- |
| test_password_with_all_requirements_passes | All complexity rules met   |
| test_password_missing_uppercase_fails      | Missing uppercase fails    |
| test_password_missing_lowercase_fails      | Missing lowercase fails    |
| test_password_missing_digit_fails          | Missing digit fails        |
| test_password_missing_special_char_fails   | Missing special char fails |

### BreachedPasswordValidator Tests

| Test Name                             | Purpose                               |
| ------------------------------------- | ------------------------------------- |
| test_password_not_breached_passes     | Non-breached password passes (mocked) |
| test_breached_password_fails          | Breached password fails (mocked)      |
| test_hibp_api_failure_allows_password | Fail-open when HIBP unavailable       |
| test_hibp_uses_k_anonymity            | Only first 5 chars of hash sent (H5)  |

### PasswordHistoryValidator Tests

| Test Name                                         | Purpose                         |
| ------------------------------------------------- | ------------------------------- |
| test_new_password_not_in_history_passes           | New password passes             |
| test_password_matching_recent_history_fails       | Reused password fails (H11)     |
| test_password_older_than_5_history_entries_passes | >5 passwords ago can be reused  |
| test_validator_handles_user_without_history       | New user with no history passes |

## BDD Feature Tests

**File**: `tests/bdd/features/user_registration.feature`

| Scenario                                         | Purpose                      |
| ------------------------------------------------ | ---------------------------- |
| Successful user registration with valid data     | Happy path registration      |
| Registration fails with weak password            | Password validation enforced |
| Registration fails with duplicate email          | Email uniqueness enforced    |
| Registration fails with invalid email format     | Email format validation      |
| Password validation rules (scenario outline)     | All password rules tested    |
| Email verification after registration            | Email verification workflow  |
| Email verification fails with expired token      | Expired token rejected       |
| Email verification fails with already used token | Used token rejected          |

## Test Execution

### Run All Phase 1 Tests

```bash
# Run all unit tests for Phase 1
./scripts/env/test.sh run tests/unit/apps/core/ -m unit

# Run BDD feature tests
./scripts/env/test.sh run tests/bdd/ -m bdd

# Run with coverage
./scripts/env/test.sh coverage --cov=apps/core
```

### Run Specific Model Tests

```bash
# Test Organisation model only
./scripts/env/test.sh run tests/unit/apps/core/test_organisation_model.py

# Test password validators only
./scripts/env/test.sh run tests/unit/apps/core/test_validators.py

# Test TOTP device security
./scripts/env/test.sh run tests/unit/apps/core/test_totp_device_model.py
```

## Expected Test Results

**All tests should FAIL initially (TDD Red phase)** because models have not been implemented yet.

**Expected failure types:**

- `ImportError`: Models not yet defined
- `AttributeError`: Model methods not implemented
- Placeholder `assert True` statements will pass until replaced with real model code

**After model implementation, tests should:**

1. **Pass all unit tests** with 90%+ coverage on models
2. **Pass all BDD feature tests** for registration workflow
3. **Pass all validator tests** including mocked HIBP API calls

---

**Next Steps:**

1. Implement model skeletons in `apps/core/models/`
2. Run tests to verify they fail correctly (Red phase)
3. Implement models fully to make tests pass (Green phase)
4. Refactor while keeping tests green
