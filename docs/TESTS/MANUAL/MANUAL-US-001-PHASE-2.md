# Manual Testing Guide: US-001 Phase 2 (Authentication Service Layer)

**Last Updated:** 08/01/2026
**Author:** Test Writer Agent
**Phase:** Phase 2 - Service Layer Implementation
**Status:** ✅ Phase 2 Complete (Implementation Finished, Ready for Testing)

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Test Environment Setup](#test-environment-setup)
- [Test Scenarios](#test-scenarios)
  - [Scenario 1: IP Encryption and Decryption](#scenario-1-ip-encryption-and-decryption)
  - [Scenario 2: IP Encryption Key Rotation](#scenario-2-ip-encryption-key-rotation)
  - [Scenario 3: Token Hashing with HMAC-SHA256](#scenario-3-token-hashing-with-hmac-sha256)
  - [Scenario 4: Token Generation and Verification](#scenario-4-token-generation-and-verification)
  - [Scenario 5: JWT Token Creation and Verification](#scenario-5-jwt-token-creation-and-verification)
  - [Scenario 6: Refresh Token Rotation and Replay Detection](#scenario-6-refresh-token-rotation-and-replay-detection)
  - [Scenario 7: User Registration with Audit Logging](#scenario-7-user-registration-with-audit-logging)
  - [Scenario 8: User Login with Race Condition Prevention](#scenario-8-user-login-with-race-condition-prevention)
  - [Scenario 9: Account Lockout After Failed Attempts](#scenario-9-account-lockout-after-failed-attempts)
  - [Scenario 10: Password Reset with Hash-then-Store Pattern](#scenario-10-password-reset-with-hash-then-store-pattern)
  - [Scenario 11: Timezone Handling with DST](#scenario-11-timezone-handling-with-dst)
  - [Scenario 12: Audit Log Retrieval](#scenario-12-audit-log-retrieval)
- [API Testing (GraphQL)](#api-testing-graphql)
- [Database Verification](#database-verification)
- [Security Testing](#security-testing)
- [Performance Testing](#performance-testing)
- [Regression Checklist](#regression-checklist)
- [Known Issues](#known-issues)
- [Sign-Off](#sign-off)

---

## Prerequisites

- [x] Phase 1 (Models) completed and tested
- [x] Phase 2 (Service Layer) completed
- [x] Development environment running (`./scripts/env/dev.sh start`)
- [x] Test environment configured (`./scripts/env/test.sh start`)
- [x] Database migrations applied
- [x] Environment variables configured:
  - `TOKEN_SIGNING_KEY` set in `.env.dev`
  - `IP_ENCRYPTION_KEY` set in `.env.dev`
  - `TOTP_ENCRYPTION_KEY` set in `.env.dev`

## Test Environment Setup

```bash
# Start test environment
./scripts/env/test.sh start

# Run database migrations
./scripts/env/test.sh migrate

# Create test superuser
./scripts/env/test.sh shell
>>> from apps.core.models import User, Organisation
>>> org = Organisation.objects.create(name="Test Org", slug="test-org")
>>> user = User.objects.create_superuser(
...     email="admin@test.com",
...     password="AdminPass123!",
...     organisation=org
... )
>>> exit()

# Run all Phase 2 unit tests (should PASS - green phase)
./scripts/env/test.sh run tests/unit/apps/core/test_phase2_security.py
```

**Expected Result:** ✅ All tests should PASS now that Phase 2 services are implemented.

**Pass Criteria:** Tests run without errors, all assertions pass successfully.

---

## Test Scenarios

### Scenario 1: IP Encryption and Decryption

**Purpose:** Verify IP addresses are encrypted and decrypted correctly (C6)

**Steps:**

1. Open Django shell:

   ```bash
   ./scripts/env/dev.sh shell
   ```

2. Test IPv4 encryption:

   ```python
   from apps.core.utils.encryption import IPEncryption

   ip = "192.168.1.1"
   encrypted = IPEncryption.encrypt_ip(ip)
   print(f"Encrypted: {encrypted}")

   decrypted = IPEncryption.decrypt_ip(encrypted)
   print(f"Decrypted: {decrypted}")

   assert decrypted == ip, "IP mismatch!"
   ```

3. Test IPv6 encryption:

   ```python
   ipv6 = "2001:0db8:85a3::8a2e:0370:7334"
   encrypted_v6 = IPEncryption.encrypt_ip(ipv6)
   decrypted_v6 = IPEncryption.decrypt_ip(encrypted_v6)

   assert decrypted_v6 == ipv6, "IPv6 mismatch!"
   ```

4. Test invalid IP handling:
   ```python
   try:
       IPEncryption.encrypt_ip("not-an-ip")
       print("ERROR: Should have raised ValueError")
   except ValueError as e:
       print(f"Correctly rejected invalid IP: {e}")
   ```

**Expected Result:**

- IPv4 and IPv6 addresses encrypt/decrypt correctly
- Invalid IPs raise ValueError
- Encrypted data is bytes, not plain text

**Pass Criteria:** All assertions pass, invalid inputs rejected

---

### Scenario 2: IP Encryption Key Rotation

**Purpose:** Verify IP encryption keys can be rotated safely (C6)

**Steps:**

1. Create test audit logs with old key:

   ```python
   from apps.core.models import AuditLog, User
   from apps.core.utils.encryption import IPEncryption

   user = User.objects.first()
   old_key = IPEncryption.generate_key()

   # Create audit log with encrypted IP
   ip = "10.0.0.1"
   encrypted_ip = IPEncryption.encrypt_ip(ip, key=old_key)

   log = AuditLog.objects.create(
       user=user,
       action="LOGIN",
       ip_address=encrypted_ip
   )
   ```

2. Run key rotation command:

   ```bash
   ./scripts/env/dev.sh manage rotate_ip_keys --dry-run
   ```

3. Verify rotation statistics:

   ```python
   from apps.core.utils.encryption import IPEncryption

   old_key = b'old_key_here'
   new_key = IPEncryption.generate_key()

   result = IPEncryption.rotate_key(old_key, new_key)

   print(f"Audit logs updated: {result['audit_logs_updated']}")
   print(f"Session tokens updated: {result['session_tokens_updated']}")
   print(f"Errors: {result['errors']}")
   ```

**Expected Result:**

- Key rotation command runs without errors
- All IPs re-encrypted with new key
- No data loss during rotation
- Dry-run mode shows what would be changed

**Pass Criteria:** All IPs successfully re-encrypted, no errors reported

---

### Scenario 3: Token Hashing with HMAC-SHA256

**Purpose:** Verify tokens are hashed using HMAC-SHA256, not plain SHA-256 (C1)

**Steps:**

1. Test token hashing:

   ```python
   from apps.core.utils.token_hasher import TokenHasher

   token = "test_token_12345"
   token_hash = TokenHasher.hash_token(token)

   print(f"Token: {token}")
   print(f"Hash: {token_hash}")
   print(f"Hash length: {len(token_hash)}")
   ```

2. Verify HMAC properties:

   ```python
   # Same token should produce same hash
   hash1 = TokenHasher.hash_token("same_token")
   hash2 = TokenHasher.hash_token("same_token")
   assert hash1 == hash2, "Hashing not deterministic!"

   # Different tokens should produce different hashes
   hash_a = TokenHasher.hash_token("token_a")
   hash_b = TokenHasher.hash_token("token_b")
   assert hash_a != hash_b, "Different tokens have same hash!"
   ```

3. Test token verification:

   ```python
   token = "secret_token"
   token_hash = TokenHasher.hash_token(token)

   # Correct token should verify
   assert TokenHasher.verify_token(token, token_hash) is True

   # Wrong token should fail
   assert TokenHasher.verify_token("wrong_token", token_hash) is False
   ```

**Expected Result:**

- Tokens are hashed using HMAC-SHA256
- Hash is base64-encoded string
- Verification uses constant-time comparison
- Wrong tokens fail verification

**Pass Criteria:** Hashing is deterministic, verification works correctly

---

### Scenario 4: Token Generation and Verification

**Purpose:** Verify cryptographically secure token generation

**Steps:**

1. Generate tokens:

   ```python
   from apps.core.utils.token_hasher import TokenHasher

   # Default 32-byte token
   token1 = TokenHasher.generate_token()
   print(f"Token 1: {token1}")
   print(f"Length: {len(token1)}")

   # Custom length token
   token2 = TokenHasher.generate_token(length=16)
   print(f"Token 2: {token2}")

   # Tokens should be different
   assert token1 != token2
   ```

2. Test entropy requirements:

   ```python
   try:
       # Should reject low entropy
       TokenHasher.generate_token(length=8)
       print("ERROR: Should reject low entropy!")
   except ValueError as e:
       print(f"Correctly rejected: {e}")
   ```

3. Test constant-time comparison:
   ```python
   assert TokenHasher.constant_time_compare("same", "same") is True
   assert TokenHasher.constant_time_compare("different", "strings") is False
   ```

**Expected Result:**

- Tokens are hex-encoded random bytes
- Default token is 64 characters (32 bytes hex)
- Low entropy tokens are rejected
- Constant-time comparison works

**Pass Criteria:** All token generation and comparison tests pass

---

### Scenario 5: JWT Token Creation and Verification

**Purpose:** Verify JWT access and refresh token creation (H1)

**Steps:**

1. Create tokens for user:

   ```python
   from apps.core.services.token_service import TokenService
   from apps.core.models import User

   user = User.objects.first()

   tokens = TokenService.create_tokens(
       user,
       device_fingerprint="test_device_123"
   )

   print(f"Access Token: {tokens['access_token'][:50]}...")
   print(f"Refresh Token: {tokens['refresh_token'][:50]}...")
   print(f"Family ID: {tokens['family_id']}")
   ```

2. Verify access token:

   ```python
   verified_user = TokenService.verify_access_token(tokens['access_token'])

   assert verified_user is not None
   assert verified_user.id == user.id
   print("✅ Access token verified successfully")
   ```

3. Test expired token handling:

   ```python
   expired_token = "expired.jwt.token.here"
   result = TokenService.verify_access_token(expired_token)

   assert result is None
   print("✅ Expired token correctly rejected")
   ```

**Expected Result:**

- Token pair created with family ID
- Access token verifies and returns user
- Expired tokens return None
- Tokens use RS256 algorithm (not HS256)

**Pass Criteria:** Token creation and verification work correctly

---

### Scenario 6: Refresh Token Rotation and Replay Detection

**Purpose:** Verify refresh token rotation prevents replay attacks (H9)

**Steps:**

1. Create initial tokens:

   ```python
   from apps.core.services.token_service import TokenService
   from apps.core.models import User

   user = User.objects.first()
   tokens = TokenService.create_tokens(user)

   original_refresh = tokens['refresh_token']
   print(f"Original refresh token: {original_refresh[:50]}...")
   ```

2. Refresh tokens (first time - should succeed):

   ```python
   new_tokens = TokenService.refresh_tokens(original_refresh)

   assert new_tokens is not None
   assert new_tokens['refresh_token'] != original_refresh
   print("✅ First refresh succeeded, token rotated")
   ```

3. Attempt replay attack (should fail):

   ```python
   replay_attempt = TokenService.refresh_tokens(original_refresh)

   assert replay_attempt is None
   print("✅ Replay attack detected and blocked (H9)")
   ```

4. Verify token family revocation:

   ```python
   # After replay detection, entire family should be revoked
   # Try using the new token
   family_revoked = TokenService.refresh_tokens(new_tokens['refresh_token'])

   assert family_revoked is None
   print("✅ Entire token family revoked after replay")
   ```

**Expected Result:**

- First refresh succeeds and rotates token
- Second use of same refresh token detected as replay
- Entire token family revoked after replay detection
- New tokens cannot be used after family revocation

**Pass Criteria:** Replay detection works, token families revoked correctly

---

### Scenario 7: User Registration with Audit Logging

**Purpose:** Verify user registration creates audit logs

**Steps:**

1. Register new user:

   ```python
   from apps.core.services.auth_service import AuthService
   from apps.core.models import Organisation

   org = Organisation.objects.first()

   user = AuthService.register_user(
       email="newuser@test.com",
       password="SecurePass123!",
       first_name="Test",
       last_name="User",
       organisation=org
   )

   print(f"User created: {user.email}")
   print(f"User ID: {user.id}")
   ```

2. Verify audit log created:

   ```python
   from apps.core.services.audit_service import AuditService

   logs = AuditService.get_user_logs(user, limit=5)

   assert len(logs) > 0
   assert logs[0].action == "REGISTRATION"
   print(f"✅ Audit log created: {logs[0]}")
   ```

3. Test duplicate email prevention:
   ```python
   try:
       AuthService.register_user(
           email="newuser@test.com",  # Already exists
           password="AnotherPass123!",
           first_name="Duplicate",
           last_name="User",
           organisation=org
       )
       print("ERROR: Should have raised ValueError!")
   except ValueError as e:
       print(f"✅ Duplicate email rejected: {e}")
   ```

**Expected Result:**

- User created successfully
- Audit log entry created
- Duplicate email raises ValueError
- Password is hashed (not plain text)

**Pass Criteria:** Registration works, duplicate emails prevented

---

### Scenario 8: User Login with Race Condition Prevention

**Purpose:** Verify login uses SELECT FOR UPDATE to prevent race conditions (H3)

**Steps:**

1. Test successful login:

   ```python
   from apps.core.services.auth_service import AuthService

   result = AuthService.login(
       email="admin@test.com",
       password="AdminPass123!",
       ip_address="192.168.1.1",
       device_fingerprint="device_abc"
   )

   assert result is not None
   assert 'access_token' in result
   assert 'refresh_token' in result
   assert 'user' in result
   print("✅ Login successful")
   ```

2. Test failed login:

   ```python
   result = AuthService.login(
       email="admin@test.com",
       password="WrongPassword",
   )

   assert result is None
   print("✅ Failed login correctly rejected")
   ```

3. Verify audit logs for both attempts:

   ```python
   from apps.core.services.audit_service import AuditService
   from apps.core.models import User

   user = User.objects.get(email="admin@test.com")
   logs = AuditService.get_user_logs(user, limit=10)

   login_logs = [l for l in logs if l.action in ["LOGIN", "LOGIN_FAILED"]]
   print(f"✅ Found {len(login_logs)} login attempt logs")
   ```

**Expected Result:**

- Successful login returns tokens and user data
- Failed login returns None
- Both attempts logged in audit log
- IP addresses encrypted in logs

**Pass Criteria:** Login works, race conditions prevented with database locking

---

### Scenario 9: Account Lockout After Failed Attempts

**Purpose:** Verify account lockout after multiple failed login attempts

**Steps:**

1. Attempt multiple failed logins:

   ```python
   from apps.core.services.auth_service import AuthService

   email = "admin@test.com"

   for i in range(6):
       result = AuthService.login(
           email=email,
           password="WrongPassword",
           ip_address=f"192.168.1.{i}"
       )
       print(f"Attempt {i+1}: {'Success' if result else 'Failed'}")
   ```

2. Check if account is locked:

   ```python
   from apps.core.models import User

   user = User.objects.get(email=email)
   is_locked = AuthService.check_account_lockout(user)

   assert is_locked is True
   print("✅ Account locked after 5+ failed attempts")
   ```

3. Verify correct password also fails when locked:

   ```python
   result = AuthService.login(
       email=email,
       password="AdminPass123!",  # Correct password
   )

   assert result is None
   print("✅ Correct password rejected when account locked")
   ```

4. Unlock account:

   ```python
   AuthService.unlock_account(user)

   is_locked = AuthService.check_account_lockout(user)
   assert is_locked is False
   print("✅ Account unlocked successfully")
   ```

**Expected Result:**

- Account locked after 5 failed attempts
- Correct password rejected when locked
- Account can be unlocked by admin
- All attempts logged in audit log

**Pass Criteria:** Lockout mechanism works correctly

---

### Scenario 10: Password Reset with Hash-then-Store Pattern

**Purpose:** Verify password reset tokens use hash-then-store pattern (C3)

**Steps:**

1. Create password reset token:

   ```python
   from apps.core.services.password_reset_service import PasswordResetService
   from apps.core.models import User

   user = User.objects.get(email="admin@test.com")

   token = PasswordResetService.create_reset_token(
       user,
       ip_address="192.168.1.1"
   )

   print(f"Reset token (plain): {token[:20]}...")
   print(f"Token length: {len(token)}")
   ```

2. Verify database stores hash, not plain token:

   ```python
   from apps.core.models import PasswordResetToken

   reset_record = PasswordResetToken.objects.filter(user=user).latest('created_at')

   # Token hash should not match plain token
   assert reset_record.token_hash != token
   print("✅ Database stores hash, not plain token (C3)")
   ```

3. Verify token:

   ```python
   verified_user = PasswordResetService.verify_reset_token(token)

   assert verified_user is not None
   assert verified_user.id == user.id
   print("✅ Token verified successfully")
   ```

4. Reset password:

   ```python
   success = PasswordResetService.reset_password(
       user,
       token,
       new_password="NewSecure123!"
   )

   assert success is True
   print("✅ Password reset successfully")
   ```

5. Verify token is now single-use:

   ```python
   verified_again = PasswordResetService.verify_reset_token(token)

   assert verified_again is None
   print("✅ Token marked as used, cannot be reused")
   ```

**Expected Result:**

- Plain token returned once
- Only hash stored in database
- Token verifies correctly
- Password reset succeeds
- Token becomes invalid after use

**Pass Criteria:** Hash-then-store pattern implemented correctly (C3)

---

### Scenario 11: Timezone Handling with DST

**Purpose:** Verify timezone-aware datetime handling with DST transitions (M5)

**Steps:**

1. Test UTC conversion:

   ```python
   from apps.core.services.auth_service import AuthService
   from datetime import datetime

   naive_dt = datetime(2024, 6, 15, 12, 0, 0)

   utc_dt = AuthService.get_timezone_aware_datetime(naive_dt, "UTC")

   assert utc_dt.tzinfo is not None
   print(f"UTC datetime: {utc_dt}")
   ```

2. Test timezone conversion with DST:

   ```python
   # June (BST - UTC+1)
   summer_dt = datetime(2024, 6, 15, 12, 0, 0)
   london_summer = AuthService.get_timezone_aware_datetime(
       summer_dt,
       "Europe/London"
   )

   # December (GMT - UTC+0)
   winter_dt = datetime(2024, 12, 15, 12, 0, 0)
   london_winter = AuthService.get_timezone_aware_datetime(
       winter_dt,
       "Europe/London"
   )

   print(f"Summer: {london_summer} (offset: {london_summer.utcoffset()})")
   print(f"Winter: {london_winter} (offset: {london_winter.utcoffset()})")

   # Offsets should differ due to DST
   assert london_summer.utcoffset() != london_winter.utcoffset()
   print("✅ DST handled correctly (M5)")
   ```

3. Test DST transition edge case:

   ```python
   # March 31, 2024 01:00 - UK DST transition
   transition_dt = datetime(2024, 3, 31, 1, 0, 0)

   london_transition = AuthService.get_timezone_aware_datetime(
       transition_dt,
       "Europe/London"
   )

   assert london_transition.tzinfo is not None
   print(f"✅ DST transition handled: {london_transition}")
   ```

**Expected Result:**

- Naive datetimes converted to timezone-aware
- DST offsets calculated correctly
- Summer/winter times have different UTC offsets
- DST transition dates handled without errors

**Pass Criteria:** All timezone conversions correct, DST handled properly

---

### Scenario 12: Audit Log Retrieval

**Purpose:** Verify audit log retrieval and filtering

**Steps:**

1. Create various audit events:

   ```python
   from apps.core.services.audit_service import AuditService
   from apps.core.models import User

   user = User.objects.first()

   AuditService.log_login(user, ip_address="10.0.0.1")
   AuditService.log_logout(user, ip_address="10.0.0.1")
   AuditService.log_password_change(user, ip_address="10.0.0.2")
   ```

2. Retrieve user logs:

   ```python
   logs = AuditService.get_user_logs(user, limit=10)

   print(f"User has {len(logs)} audit log entries")

   for log in logs:
       print(f"- {log.action} at {log.created_at}")
   ```

3. Retrieve organisation logs:

   ```python
   org = user.organisation
   org_logs = AuditService.get_organisation_logs(org, limit=50)

   print(f"Organisation has {len(org_logs)} audit log entries")
   ```

4. Verify IP encryption in logs:

   ```python
   from apps.core.utils.encryption import IPEncryption

   log = logs[0]
   decrypted_ip = IPEncryption.decrypt_ip(log.ip_address)

   print(f"Encrypted IP in DB: {log.ip_address[:20]}...")
   print(f"Decrypted IP: {decrypted_ip}")
   ```

**Expected Result:**

- Audit logs created for all events
- Logs filterable by user and organisation
- IP addresses encrypted in database
- IP addresses decryptable with correct key

**Pass Criteria:** Audit log creation and retrieval work correctly

---

## API Testing (GraphQL)

**Note:** GraphQL API not yet implemented in Phase 2. These tests are for Phase 3.

Will include:

- Registration mutation
- Login mutation
- Logout mutation
- Password reset mutation
- Token refresh mutation

---

## Database Verification

Verify database schema and data integrity:

```bash
# Connect to database
./scripts/env/dev.sh shell

# Check SessionToken table
from apps.core.models import SessionToken
print(f"Active sessions: {SessionToken.objects.filter(is_revoked=False).count()}")

# Check AuditLog table
from apps.core.models import AuditLog
print(f"Total audit logs: {AuditLog.objects.count()}")

# Check PasswordResetToken table
from apps.core.models import PasswordResetToken
unexpired = PasswordResetToken.objects.filter(used=False, expires_at__gt=timezone.now())
print(f"Unexpired reset tokens: {unexpired.count()}")

# Verify IP encryption in logs
log = AuditLog.objects.first()
print(f"IP encrypted: {isinstance(log.ip_address, bytes)}")
print(f"IP length: {len(log.ip_address)}")
```

---

## Security Testing

### Test 1: Token Hash Collision

Verify two different tokens don't produce the same hash:

```python
from apps.core.utils.token_hasher import TokenHasher

hashes = set()
for i in range(10000):
    token = TokenHasher.generate_token()
    token_hash = TokenHasher.hash_token(token)

    if token_hash in hashes:
        print(f"ERROR: Hash collision at iteration {i}")
        break

    hashes.add(token_hash)

print(f"✅ Generated {len(hashes)} unique hashes without collision")
```

### Test 2: Timing Attack Resistance

Verify constant-time comparison prevents timing attacks:

```python
import time
from apps.core.utils.token_hasher import TokenHasher

correct = "secret_token_12345678"
wrong = "wrong_token_87654321"

# Time correct comparison
start = time.perf_counter()
for _ in range(10000):
    TokenHasher.constant_time_compare(correct, correct)
time_correct = time.perf_counter() - start

# Time incorrect comparison
start = time.perf_counter()
for _ in range(10000):
    TokenHasher.constant_time_compare(correct, wrong)
time_wrong = time.perf_counter() - start

print(f"Correct comparisons: {time_correct:.6f}s")
print(f"Wrong comparisons: {time_wrong:.6f}s")
print(f"Difference: {abs(time_correct - time_wrong):.6f}s")

# Timing should be nearly identical
assert abs(time_correct - time_wrong) < 0.001
print("✅ Constant-time comparison verified")
```

### Test 3: IP Encryption Strength

Verify encrypted IPs are not reversible without key:

```python
from apps.core.utils.encryption import IPEncryption

ip = "192.168.1.1"
key1 = IPEncryption.generate_key()
key2 = IPEncryption.generate_key()

encrypted = IPEncryption.encrypt_ip(ip, key=key1)

try:
    # Try decrypting with wrong key
    decrypted = IPEncryption.decrypt_ip(encrypted, key=key2)
    print("ERROR: Decrypted with wrong key!")
except Exception as e:
    print(f"✅ Wrong key rejected: {type(e).__name__}")
```

---

## Performance Testing

Test service layer performance:

```python
import time
from apps.core.services.token_service import TokenService
from apps.core.models import User

user = User.objects.first()

# Token creation performance
start = time.time()
for _ in range(100):
    TokenService.create_tokens(user)
elapsed = time.time() - start

print(f"Created 100 token pairs in {elapsed:.2f}s")
print(f"Average: {elapsed/100*1000:.2f}ms per token pair")

# Should be < 50ms per token pair
assert elapsed/100 < 0.050
print("✅ Token creation performance acceptable")
```

---

## Regression Checklist

After implementing Phase 2 services, verify Phase 1 still works:

- [ ] User model creation works
- [ ] Password hashing still using Argon2id
- [ ] Organisation relationships intact
- [ ] Existing unit tests still pass
- [ ] Database migrations apply cleanly

---

## Known Issues

**Phase 2 is in RED phase (TDD):**

- All service methods raise NotImplementedError
- Tests are expected to FAIL until implementations complete
- This is INTENTIONAL for TDD workflow

**Next Steps:**

- Run `/syntek-dev-suite:backend` to implement services (GREEN phase)
- Run `/syntek-dev-suite:refactor` to clean up code (REFACTOR phase)

---

## Sign-Off

| Tester | Date | Status | Notes |
| ------ | ---- | ------ | ----- |
|        |      |        |       |
|        |      |        |       |

**Testing Phase:** RED (Stubs Created, Tests Failing)
**Ready for GREEN Phase:** Yes - Implement services to make tests pass
**Approved By:** Test Writer Agent
**Date:** 08/01/2026
