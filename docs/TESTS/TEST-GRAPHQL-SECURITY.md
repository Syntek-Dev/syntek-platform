# Test Specification: GraphQL Security Features

**Last Updated:** 10/01/2026
**Author:** Test Writer Agent
**Test Suites:** Permission Classes, CSRF Protection, Query Depth/Complexity Limiting

---

## Overview

This document specifies comprehensive test coverage for GraphQL security features including:

- **Permission Classes:** IsAuthenticated, HasPermission, IsOrganisationOwner
- **CSRF Protection:** GraphQL CSRF middleware for mutations (C4 requirement)
- **Query Security:** Depth limiting, complexity analysis, introspection control

All tests follow TDD (Test-Driven Development) principles and are written before full implementation.

---

## Test Files

| Test File                                     | Test Type   | Coverage                                      |
| --------------------------------------------- | ----------- | --------------------------------------------- |
| `tests/unit/api/test_permissions_comprehensive.py` | Unit        | Permission classes with edge cases            |
| `tests/unit/api/test_csrf_comprehensive.py`         | Unit        | CSRF middleware and token validation          |
| `tests/unit/api/test_graphql_security_extensions.py`| Unit        | Query depth, complexity, introspection limits |
| `docs/TESTS/MANUAL/MANUAL-GRAPHQL-SECURITY.md`      | Manual      | Manual testing guide for developers           |

---

## Test Coverage Summary

### Permission Classes (test_permissions_comprehensive.py)

**Classes Tested:**
- `IsAuthenticated`
- `HasPermission`
- `IsOrganisationOwner`

**Test Classes:**

#### TestIsAuthenticatedPermission
- ✅ Authenticated user passes permission check
- ✅ Unauthenticated user (AnonymousUser) fails check
- ✅ Inactive user fails check
- ✅ Error message is descriptive
- ✅ Permission handles additional kwargs

#### TestHasPermissionClass
- ✅ User with required permission is granted access
- ✅ User without required permission is denied
- ✅ Unauthenticated user always denied
- ✅ Error message includes specific permission name
- ✅ Superuser passes all permission checks
- ✅ Permission inherited via group membership
- ✅ Permission format validation (app.action_model)

#### TestIsOrganisationOwnerPermission
- ✅ Organisation owner passes check
- ✅ Admin user (non-owner) fails check
- ✅ Regular member fails check
- ✅ User with no group membership fails check
- ✅ Unauthenticated user fails check
- ✅ Error message clearly states owner requirement
- ✅ Owner from different organisation still passes

#### TestPermissionCombinations
- ✅ User with multiple permission types
- ✅ Permission checking order independence

#### TestPermissionEdgeCases
- ✅ Permission handles None user gracefully
- ✅ Permission handles missing request object
- ✅ HasPermission with empty permission string
- ✅ Permission source parameter unused

**Total Tests:** 28

---

### CSRF Protection (test_csrf_comprehensive.py)

**Classes Tested:**
- `GraphQLCSRFMiddleware`

**Test Classes:**

#### TestCSRFMiddlewareInitialization
- ✅ Middleware initializes with get_response callable
- ✅ Middleware creates CsrfViewMiddleware instance

#### TestCSRFMutationDetection
- ✅ Detects mutation keyword in GraphQL query
- ✅ Does not detect mutation in regular query
- ✅ Detects mutation case-insensitive (MUTATION)
- ✅ Detects mutation in mixed query+mutation
- ✅ Handles invalid JSON gracefully
- ✅ Handles missing 'query' field
- ✅ Handles non-JSON content type
- ✅ Handles empty request body

#### TestCSRFPathFiltering
- ✅ Only processes /graphql endpoint
- ✅ Processes /graphql endpoint correctly
- ✅ Processes /graphql without trailing slash

#### TestCSRFIntegrationWithDjango
- ✅ Query succeeds without CSRF token
- ✅ CSRF token can be retrieved from endpoint
- ✅ CSRF token is unique per session

#### TestCSRFErrorHandling
- ✅ Handles request without body
- ✅ Handles request with None body
- ✅ Handles very large request body
- ✅ Handles malformed GraphQL syntax

#### TestCSRFMultipartRequests
- ✅ Handles multipart/form-data requests

#### TestCSRFBatchedRequests
- ✅ Handles batched queries (array of queries)
- ✅ Handles batched mutations

#### TestCSRFIntrospectionQueries
- ✅ Introspection query not treated as mutation (__schema)
- ✅ Type introspection not treated as mutation (__type)

**Total Tests:** 24

---

### GraphQL Security Extensions (test_graphql_security_extensions.py)

**Classes Tested:**
- `QueryDepthLimitExtension`
- `QueryComplexityLimitExtension`
- `IntrospectionControlExtension`

**Test Classes:**

#### TestQueryDepthLimitExtension
- ✅ Extension initializes with default max depth (10)
- ✅ Extension accepts custom max depth
- ✅ Extension uses GRAPHQL_MAX_QUERY_DEPTH from settings
- ✅ Simple query passes depth check
- ✅ Deeply nested query exceeds depth limit
- ✅ Query at exact max depth is allowed
- ✅ Calculate depth handles empty document
- ✅ Calculate depth handles document with no selections
- ✅ Depth calculation with multiple definitions (returns max)
- ✅ Depth limit error message includes details

#### TestQueryComplexityLimitExtension
- ✅ Extension initializes with default max complexity (1000)
- ✅ Extension accepts custom max complexity
- ✅ Extension uses GRAPHQL_MAX_QUERY_COMPLEXITY from settings
- ✅ Simple query passes complexity check
- ✅ Complex query exceeds complexity limit
- ✅ Query at exact max complexity is allowed
- ✅ Calculate complexity handles empty document
- ✅ List field increases complexity score
- ✅ Complexity error message includes details

#### TestIntrospectionControlExtension
- ✅ Introspection allowed in DEBUG mode
- ✅ Introspection allowed when explicitly enabled
- ✅ Introspection blocked in production (DEBUG=False)
- ✅ Type introspection (__type) blocked in production
- ✅ Regular queries allowed when introspection disabled
- ✅ _is_introspection_query detects __schema
- ✅ _is_introspection_query detects __type
- ✅ _is_introspection_query returns False for regular queries
- ✅ _is_introspection_query handles empty document

#### TestSecurityExtensionIntegration
- ✅ All extensions can be initialized together
- ✅ Extensions have independent configuration

**Total Tests:** 30

---

## Total Test Count

| Test Suite                  | Unit Tests | Integration Tests | E2E Tests | Total |
| --------------------------- | ---------- | ----------------- | --------- | ----- |
| Permission Classes          | 28         | 0                 | 0         | 28    |
| CSRF Protection             | 24         | 0                 | 0         | 24    |
| GraphQL Security Extensions | 30         | 0                 | 0         | 30    |
| **TOTAL**                   | **82**     | **0**             | **0**     | **82**|

---

## Test Markers

Tests are organised using pytest markers:

```python
@pytest.mark.unit           # Unit tests (fast, isolated)
@pytest.mark.integration    # Integration tests (multiple components)
@pytest.mark.graphql        # GraphQL-specific tests
@pytest.mark.security       # Security-related tests
@pytest.mark.django_db      # Tests requiring database access
```

---

## Running Tests

### Run All Security Tests

```bash
./scripts/env/test.sh run tests/unit/api/test_permissions_comprehensive.py
./scripts/env/test.sh run tests/unit/api/test_csrf_comprehensive.py
./scripts/env/test.sh run tests/unit/api/test_graphql_security_extensions.py
```

### Run by Marker

```bash
# Run all GraphQL tests
./scripts/env/test.sh run -m graphql

# Run all security tests
./scripts/env/test.sh run -m security

# Run only unit tests
./scripts/env/test.sh run -m unit
```

### Run with Coverage

```bash
./scripts/env/test.sh coverage tests/unit/api/
```

---

## Expected Behaviours

### Permission Classes

**IsAuthenticated:**
- Authenticated users: ✅ Allowed
- Unauthenticated users (AnonymousUser): ❌ Denied
- Inactive users: ❌ Denied

**HasPermission:**
- Users with specific permission: ✅ Allowed
- Users without permission: ❌ Denied
- Superusers: ✅ Always allowed
- Permission via groups: ✅ Allowed

**IsOrganisationOwner:**
- Users in "Organisation Owner" group: ✅ Allowed
- Users in other groups: ❌ Denied
- Unauthenticated users: ❌ Denied

### CSRF Protection

**Mutations:**
- With valid CSRF token: ✅ Allowed
- Without CSRF token: ❌ 403 Forbidden
- With invalid CSRF token: ❌ 403 Forbidden

**Queries:**
- With CSRF token: ✅ Allowed
- Without CSRF token: ✅ Allowed (CSRF not required)

### Query Security

**Depth Limiting:**
- Queries within max depth: ✅ Allowed
- Queries exceeding max depth: ❌ Rejected with error

**Complexity Limiting:**
- Queries within max complexity: ✅ Allowed
- Queries exceeding max complexity: ❌ Rejected with error

**Introspection:**
- DEBUG=True: ✅ Introspection allowed
- DEBUG=False + GRAPHQL_ENABLE_INTROSPECTION=True: ✅ Allowed
- DEBUG=False + GRAPHQL_ENABLE_INTROSPECTION=False: ❌ Blocked

---

## Edge Cases Tested

### Permission Classes
- None user object
- Missing request object
- Empty permission string
- Source parameter variations
- Permission checking order
- Multiple permission types

### CSRF Middleware
- Invalid JSON in request body
- Missing 'query' field
- Non-JSON content types
- Empty request body
- Very large request bodies
- Malformed GraphQL syntax
- Multipart/form-data requests
- Batched GraphQL requests
- Introspection queries

### Security Extensions
- Empty/None documents
- Documents with no selections
- Multiple query definitions
- Queries at exact limits
- Settings configuration
- Extension combinations

---

## Security Requirements Mapping

| Requirement | Feature                  | Test Coverage |
| ----------- | ------------------------ | ------------- |
| C4          | CSRF protection          | ✅ 24 tests    |
| C5          | Email verification       | (Separate)    |
| H2          | DataLoader integration   | (Separate)    |
| H4          | Standardised errors      | (Separate)    |
| H10         | Token revocation         | (Separate)    |
| NEW         | Query depth limiting     | ✅ 10 tests    |
| NEW         | Query complexity         | ✅ 9 tests     |
| NEW         | Introspection control    | ✅ 9 tests     |
| NEW         | Permission classes       | ✅ 28 tests    |

---

## Test Data Setup

Tests use factory-boy factories for consistent test data:

```python
from tests.factories import (
    OrganisationFactory,
    UserFactory,
    AuditLogFactory,
)

# Create test organisation
org = OrganisationFactory.create(name="Test Org", slug="test-org")

# Create test user
user = UserFactory.create(
    organisation=org,
    email="test@example.com",
    email_verified=True
)

# Create user with specific permissions
from django.contrib.auth.models import Group
owner_group = Group.objects.create(name="Organisation Owner")
owner = UserFactory.create(organisation=org)
owner.groups.add(owner_group)
```

---

## Manual Testing

Refer to `docs/TESTS/MANUAL/MANUAL-GRAPHQL-SECURITY.md` for comprehensive manual testing guide including:

- 10 detailed test scenarios
- Step-by-step instructions
- Expected results and pass criteria
- API testing examples with curl
- Regression checklist
- Known issues

---

## Next Steps

1. **Run Tests:** Execute all tests to verify skeleton implementation
2. **Implement Features:** Use `/syntek-dev-suite:backend` to implement functionality
3. **Verify Tests Pass:** Ensure all tests turn green
4. **Integration Testing:** Test features together in integration environment
5. **Manual Testing:** Follow manual testing guide for end-to-end verification

---

## Notes

- All tests follow TDD principles (written before implementation)
- Tests use type hints and Google-style docstrings
- Tests include Given/When/Then structure in docstrings
- Edge cases and error handling are comprehensively tested
- Tests are independent and can run in any order
- Factories ensure consistent, isolated test data
