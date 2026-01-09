# Manual Testing Guide: US-001 Phase 3 - GraphQL API

**Last Updated:** 08/01/2026
**Author:** Test Writer Agent
**Phase:** Phase 3 - GraphQL API Implementation
**Prerequisites:** Phases 1 and 2 completed (database models and services)

---

## Table of Contents

- [Manual Testing Guide: US-001 Phase 3 - GraphQL API](#manual-testing-guide-us-001-phase-3---graphql-api)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Test Environment Setup](#test-environment-setup)
  - [GraphQL Playground Access](#graphql-playground-access)
  - [Test Scenarios](#test-scenarios)
    - [Scenario 1: User Registration (Happy Path)](#scenario-1-user-registration-happy-path)
    - [Scenario 2: User Login with Verified Email](#scenario-2-user-login-with-verified-email)
    - [Scenario 3: Email Verification Enforcement (C5 Requirement)](#scenario-3-email-verification-enforcement-c5-requirement)
    - [Scenario 4: Password Reset Flow](#scenario-4-password-reset-flow)
    - [Scenario 5: CSRF Protection for Mutations (C4 Requirement)](#scenario-5-csrf-protection-for-mutations-c4-requirement)
    - [Scenario 6: Query Without CSRF Token (Should Succeed)](#scenario-6-query-without-csrf-token-should-succeed)
    - [Scenario 7: Organisation Boundary Enforcement](#scenario-7-organisation-boundary-enforcement)
    - [Scenario 8: User Logout and Token Revocation](#scenario-8-user-logout-and-token-revocation)
    - [Scenario 9: Invalid Credentials Handling](#scenario-9-invalid-credentials-handling)
    - [Scenario 10: Weak Password Rejection](#scenario-10-weak-password-rejection)
  - [API Testing with cURL](#api-testing-with-curl)
    - [Register User](#register-user)
    - [Login User](#login-user)
    - [Query Current User](#query-current-user)
    - [Request Password Reset](#request-password-reset)
  - [Database Verification](#database-verification)
  - [Regression Checklist](#regression-checklist)
  - [Known Issues](#known-issues)
  - [Sign-Off](#sign-off)

---

## Prerequisites

- [ ] Phase 1 complete (database models migrated)
- [ ] Phase 2 complete (services implemented and tested)
- [ ] Development environment running: `./scripts/env/dev.sh start`
- [ ] GraphQL endpoint accessible at `http://localhost:8000/graphql/`
- [ ] Test organisation created with slug "test-org"
- [ ] Mailpit running at `http://localhost:8025` for email verification

---

## Test Environment Setup

```bash
# Start development environment
./scripts/env/dev.sh start

# Run migrations
./scripts/env/dev.sh migrate

# Create test organisation (if not exists)
./scripts/env/dev.sh shell
>>> from apps.core.models import Organisation
>>> Organisation.objects.get_or_create(
...     slug="test-org",
...     defaults={"name": "Test Organisation", "industry": "Technology"}
... )
>>> exit()

# Verify GraphQL endpoint
curl http://localhost:8000/graphql/
```

---

## GraphQL Playground Access

**Development GraphQL Playground:**
`http://localhost:8000/graphql/`

The playground provides:

- Interactive query editor with autocomplete
- Query/mutation history
- Documentation explorer (introspection)
- Variable editor for inputs

---

## Test Scenarios

### Scenario 1: User Registration (Happy Path)

**Purpose:** Verify users can successfully register

**Steps:**

1. Open GraphQL Playground at `http://localhost:8000/graphql/`
2. Enter the following mutation:

```graphql
mutation Register {
  register(
    input: {
      email: "testuser@example.com"
      password: "SecurePassword123!@"
      firstName: "Test"
      lastName: "User"
      organisationSlug: "test-org"
    }
  ) {
    token
    refreshToken
    user {
      id
      email
      firstName
      lastName
      emailVerified
      organisation {
        name
      }
    }
    requiresTwoFactor
  }
}
```

3. Click "Execute" (play button)

**Expected Result:**

- HTTP 200 response
- `token` and `refreshToken` are non-empty strings
- `user.email` is "<testuser@example.com>"
- `user.emailVerified` is `false` (email not verified yet)
- `user.organisation.name` is "Test Organisation"
- `requiresTwoFactor` is `false`

**Pass Criteria:** User created in database, tokens returned, email verification token created

---

### Scenario 2: User Login with Verified Email

**Purpose:** Verify users can login after email verification

**Steps:**

1. Manually verify user email in database:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import User
>>> user = User.objects.get(email="testuser@example.com")
>>> user.email_verified = True
>>> user.email_verified_at = timezone.now()
>>> user.save()
>>> exit()
```

2. Execute login mutation:

```graphql
mutation Login {
  login(input: { email: "testuser@example.com", password: "SecurePassword123!@" }) {
    token
    refreshToken
    user {
      email
      emailVerified
    }
  }
}
```

**Expected Result:**

- HTTP 200 response
- `token` and `refreshToken` returned
- `user.emailVerified` is `true`

**Pass Criteria:** Login succeeds, tokens generated, session created

---

### Scenario 3: Email Verification Enforcement (C5 Requirement)

**Purpose:** Verify unverified users cannot login (C5 security requirement)

**Steps:**

1. Create new user WITHOUT verified email:

```graphql
mutation RegisterUnverified {
  register(
    input: {
      email: "unverified@example.com"
      password: "SecurePassword123!@"
      firstName: "Unverified"
      lastName: "User"
      organisationSlug: "test-org"
    }
  ) {
    user {
      emailVerified
    }
  }
}
```

2. Attempt to login:

```graphql
mutation LoginUnverified {
  login(input: { email: "unverified@example.com", password: "SecurePassword123!@" }) {
    token
  }
}
```

**Expected Result:**

- Login FAILS with error
- Error code: `EMAIL_NOT_VERIFIED`
- Error message includes guidance: "Please verify your email address"
- No token is returned

**Pass Criteria:** Unverified users blocked from login (C5 requirement satisfied)

---

### Scenario 4: Password Reset Flow

**Purpose:** Verify complete password reset workflow

**Steps:**

1. Request password reset:

```graphql
mutation RequestPasswordReset {
  requestPasswordReset(input: { email: "testuser@example.com" })
}
```

2. Check Mailpit (`http://localhost:8025`) for reset email
3. Copy reset token from email link
4. Complete password reset:

```graphql
mutation ResetPassword {
  resetPassword(input: { token: "TOKEN_FROM_EMAIL", newPassword: "NewSecurePass456!@" })
}
```

5. Login with new password:

```graphql
mutation LoginNewPassword {
  login(input: { email: "testuser@example.com", password: "NewSecurePass456!@" }) {
    token
  }
}
```

**Expected Result:**

- Reset email received in Mailpit
- Password reset succeeds
- Login with new password succeeds
- Login with old password FAILS

**Pass Criteria:** Complete password reset flow works, old password invalidated

---

### Scenario 5: CSRF Protection for Mutations (C4 Requirement)

**Purpose:** Verify CSRF protection is enforced on mutations (C4 security requirement)

**Steps:**

1. Attempt logout mutation WITHOUT CSRF token:

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { logout }"}'
```

**Expected Result:**

- HTTP 403 Forbidden OR
- Error response with code `CSRF_TOKEN_MISSING`
- Mutation is NOT executed

**Pass Criteria:** Mutations require CSRF token (C4 requirement satisfied)

---

### Scenario 6: Query Without CSRF Token (Should Succeed)

**Purpose:** Verify queries do NOT require CSRF token

**Steps:**

1. Execute query WITHOUT CSRF token:

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{"query": "query { me { email } }"}'
```

**Expected Result:**

- HTTP 200 response
- Query executes (returns null if not authenticated, user data if authenticated)
- NO CSRF error

**Pass Criteria:** Queries work without CSRF token

---

### Scenario 7: Organisation Boundary Enforcement

**Purpose:** Verify users can only access data from their organisation

**Steps:**

1. Create second organisation and user:

```bash
./scripts/env/dev.sh shell
>>> from apps.core.models import Organisation, User
>>> org2 = Organisation.objects.create(name="Organisation 2", slug="org-2")
>>> user2 = User.objects.create_user(
...     email="user2@org2.com",
...     password="password",
...     organisation=org2,
...     email_verified=True
... )
>>> exit()
```

2. Login as user from Organisation 1
3. Attempt to query users:

```graphql
query GetUsers {
  users {
    id
    email
    organisation {
      name
    }
  }
}
```

**Expected Result:**

- Only users from Organisation 1 are returned
- Users from Organisation 2 are NOT visible
- All returned users have `organisation.name` = "Test Organisation"

**Pass Criteria:** Cross-organisation data is not accessible

---

### Scenario 8: User Logout and Token Revocation

**Purpose:** Verify logout revokes current session

**Steps:**

1. Login and save token:

```graphql
mutation Login {
  login(input: { email: "testuser@example.com", password: "SecurePassword123!@" }) {
    token
  }
}
```

2. Use token to query user data (should succeed)
3. Logout:

```graphql
mutation Logout {
  logout
}
```

4. Attempt to use same token again

**Expected Result:**

- Logout returns `true`
- Subsequent requests with old token FAIL authentication
- Token is revoked in database

**Pass Criteria:** Token revocation works correctly

---

### Scenario 9: Invalid Credentials Handling

**Purpose:** Verify invalid credentials are handled securely

**Steps:**

1. Attempt login with wrong password:

```graphql
mutation LoginWrongPassword {
  login(input: { email: "testuser@example.com", password: "WrongPassword" }) {
    token
  }
}
```

2. Attempt login with non-existent email:

```graphql
mutation LoginNonExistent {
  login(input: { email: "nonexistent@example.com", password: "anything" }) {
    token
  }
}
```

**Expected Result:**

- Both return SAME error message (prevent user enumeration - M7)
- Error code: `INVALID_CREDENTIALS`
- Error message: "Invalid email or password"
- Failed attempts logged in audit log

**Pass Criteria:** No user enumeration, consistent error messages

---

### Scenario 10: Weak Password Rejection

**Purpose:** Verify weak passwords are rejected

**Steps:**

1. Attempt registration with weak password:

```graphql
mutation RegisterWeakPassword {
  register(
    input: {
      email: "weak@example.com"
      password: "weak"
      firstName: "Test"
      lastName: "User"
      organisationSlug: "test-org"
    }
  ) {
    token
  }
}
```

**Expected Result:**

- Registration FAILS
- Error includes password requirements:
  - Minimum 12 characters
  - At least one uppercase letter
  - At least one lowercase letter
  - At least one digit
  - At least one special character

**Pass Criteria:** Weak passwords rejected with clear guidance

---

## API Testing with cURL

### Register User

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation Register($input: RegisterInput!) { register(input: $input) { token user { email } } }",
    "variables": {
      "input": {
        "email": "curl@example.com",
        "password": "SecurePass123!@",
        "firstName": "Curl",
        "lastName": "User",
        "organisationSlug": "test-org"
      }
    }
  }'
```

### Login User

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation Login($input: LoginInput!) { login(input: $input) { token } }",
    "variables": {
      "input": {
        "email": "curl@example.com",
        "password": "SecurePass123!@"
      }
    }
  }'
```

### Query Current User

```bash
# Replace YOUR_TOKEN with actual token from login
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"query": "query { me { email organisation { name } } }"}'
```

### Request Password Reset

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation RequestPasswordReset($input: PasswordResetRequestInput!) { requestPasswordReset(input: $input) }",
    "variables": {
      "input": {
        "email": "curl@example.com"
      }
    }
  }'
```

---

## Database Verification

After running tests, verify database state:

```bash
./scripts/env/dev.sh shell

# Check users created
>>> from apps.core.models import User
>>> User.objects.count()

# Check session tokens
>>> from apps.core.models import SessionToken
>>> SessionToken.objects.filter(user__email="testuser@example.com").count()

# Check audit logs
>>> from apps.core.models import AuditLog
>>> AuditLog.objects.filter(action="login_success").count()

# Check email verification tokens
>>> from apps.core.models import EmailVerificationToken
>>> EmailVerificationToken.objects.filter(verified=False).count()
```

---

## Regression Checklist

After implementing Phase 3, verify these still work:

- [ ] Phase 1: Database models queryable
- [ ] Phase 2: Service layer functions correctly
- [ ] User creation and retrieval
- [ ] Organisation relationships
- [ ] Token hashing (HMAC-SHA256 - C1)
- [ ] IP address encryption (C6)
- [ ] Audit logging
- [ ] Password validation

---

## Known Issues

**Phase 3 - Implementation Pending:**

- [ ] 2FA mutations not implemented (Phase 4)
- [ ] DataLoaders not implemented (H2 - will cause N+1 queries)
- [ ] CSRF middleware stub needs full implementation (C4)
- [ ] Account lockout not implemented (H13)
- [ ] Concurrent session limit not implemented (H12)

---

## Sign-Off

| Tester | Date | Status | Notes |
| ------ | ---- | ------ | ----- |
|        |      |        |       |
|        |      |        |       |
|        |      |        |       |

---

**Next Steps:**

1. Run automated tests: `./scripts/env/test.sh run -m graphql`
2. Implement missing stubs to make tests pass (GREEN phase)
3. Proceed to Phase 4: Two-Factor Authentication
