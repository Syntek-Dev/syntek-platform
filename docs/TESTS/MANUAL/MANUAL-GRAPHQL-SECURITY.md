# Manual Testing Guide: GraphQL Security Features

**Last Updated:** 10/01/2026
**Author:** Test Writer Agent

---

## Prerequisites

- [ ] Development environment running (`./scripts/env/dev.sh start`)
- [ ] Test database configured (`.env.test`)
- [ ] GraphQL endpoint accessible at `http://localhost:8000/graphql/`
- [ ] Test user accounts created with different permission levels
- [ ] HTTP client installed (curl, Postman, Insomnia, or GraphQL Playground)

## Test Environment Setup

```bash
# Start development environment
./scripts/env/dev.sh start

# Create test database
./scripts/env/dev.sh migrate

# Create test users with different roles
./scripts/env/dev.sh shell

# In Django shell:
from apps.core.models import User, Organisation
from django.contrib.auth.models import Group

# Create test organisation
org = Organisation.objects.create(name="Test Organisation", slug="test-org")

# Create organisation owner
owner_group = Group.objects.create(name="Organisation Owner")
owner = User.objects.create_user(
    email="owner@test.com",
    password="TestPassword123!@",
    organisation=org,
    email_verified=True
)
owner.groups.add(owner_group)

# Create regular member
member_group = Group.objects.create(name="Organisation Member")
member = User.objects.create_user(
    email="member@test.com",
    password="TestPassword123!@",
    organisation=org,
    email_verified=True
)
member.groups.add(member_group)

# Create user in different organisation
org2 = Organisation.objects.create(name="Other Organisation", slug="other-org")
other_user = User.objects.create_user(
    email="other@test.com",
    password="TestPassword123!@",
    organisation=org2,
    email_verified=True
)

exit()
```

---

## Test Scenarios

### Scenario 1: Permission Classes - Authenticated Access

**Purpose:** Verify IsAuthenticated permission blocks unauthenticated requests

**Steps:**

1. Open GraphQL client (Postman/Insomnia)
2. Configure endpoint: `POST http://localhost:8000/graphql/`
3. Send query WITHOUT authentication headers:

```graphql
query {
  me {
    id
    email
    firstName
  }
}
```

4. Observe response
5. Now login to get JWT token:

```graphql
mutation {
  login(input: {
    email: "owner@test.com"
    password: "TestPassword123!@"
  }) {
    token
    user {
      id
      email
    }
  }
}
```

6. Copy the token from response
7. Add authentication header: `Authorization: Bearer <token>`
8. Resend the `me` query from step 3

**Expected Result:**

- **Step 4:** Error response with "User is not authenticated" message
- **Step 8:** Successful response with user data

**Pass Criteria:** Unauthenticated requests are rejected, authenticated requests succeed

---

### Scenario 2: Permission Classes - Organisation Boundaries

**Purpose:** Verify users cannot access data from other organisations

**Steps:**

1. Login as `owner@test.com` and get token:

```graphql
mutation {
  login(input: {
    email: "owner@test.com"
    password: "TestPassword123!@"
  }) {
    token
  }
}
```

2. Get user ID of `other@test.com` (from different organisation):

```bash
./scripts/env/dev.sh shell

from apps.core.models import User
other_user = User.objects.get(email="other@test.com")
print(f"Other user ID: {other_user.id}")
exit()
```

3. Try to query the other user using owner's token:

```graphql
query {
  user(id: "<other_user_id>") {
    id
    email
    organisation {
      name
    }
  }
}
```

4. Query list of all users:

```graphql
query {
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

- **Step 3:** Returns `null` or error (cannot access user from different organisation)
- **Step 4:** Returns only users from owner's organisation (Test Organisation), excludes users from Other Organisation

**Pass Criteria:** Organisation boundaries are enforced, cross-organisation access is blocked

---

### Scenario 3: Permission Classes - Role-Based Access

**Purpose:** Verify IsOrganisationOwner permission restricts access to owners only

**Steps:**

1. Login as regular member (`member@test.com`):

```graphql
mutation {
  login(input: {
    email: "member@test.com"
    password: "TestPassword123!@"
  }) {
    token
  }
}
```

2. Try to perform owner-only operation (example - would need to implement):

```graphql
mutation {
  deleteOrganisation(id: "<org_id>") {
    success
  }
}
```

3. Observe error response
4. Login as owner (`owner@test.com`) and retry same operation

**Expected Result:**

- **Step 2:** Error: "User is not an organisation owner"
- **Step 4:** Operation succeeds (if mutation implemented)

**Pass Criteria:** Owner-only operations are restricted to users with Organisation Owner role

---

### Scenario 4: CSRF Protection - Mutation Requires Token

**Purpose:** Verify CSRF protection is enforced for GraphQL mutations

**Steps:**

1. First, get a CSRF token by making a GET request:

```bash
curl -X GET http://localhost:8000/graphql/ \
  -c cookies.txt \
  -v
```

2. Extract `csrftoken` from cookies.txt
3. Attempt mutation WITHOUT CSRF token:

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "query": "mutation { logout }"
  }'
```

4. Observe 403 Forbidden response
5. Retry mutation WITH CSRF token:

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <csrf_token_from_step_2>" \
  -b cookies.txt \
  -d '{
    "query": "mutation { logout }"
  }'
```

**Expected Result:**

- **Step 4:** 403 Forbidden or CSRF error message
- **Step 5:** 200 OK, mutation executes successfully

**Pass Criteria:** Mutations require valid CSRF token, rejected without token

---

### Scenario 5: CSRF Protection - Query Allowed Without Token

**Purpose:** Verify CSRF protection is NOT enforced for queries

**Steps:**

1. Send GraphQL query WITHOUT CSRF token:

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -d '{
    "query": "query { hello }"
  }'
```

2. Observe successful response
3. Send more complex query:

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "query": "query { me { id email } }"
  }'
```

**Expected Result:**

- **Step 1:** 200 OK, query executes successfully
- **Step 3:** 200 OK, query returns user data

**Pass Criteria:** Queries work without CSRF token (no 403 errors)

---

### Scenario 6: Query Depth Limiting

**Purpose:** Verify deeply nested queries are rejected

**Steps:**

1. Configure max query depth in settings (`.env.dev`):

```bash
GRAPHQL_MAX_QUERY_DEPTH=5
```

2. Restart development server
3. Send shallow query (depth 2):

```graphql
query {
  me {
    id
    organisation {
      name
    }
  }
}
```

4. Send deeply nested query (depth 10):

```graphql
query {
  me {
    organisation {
      users {
        organisation {
          users {
            organisation {
              users {
                organisation {
                  users {
                    organisation {
                      name
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
}
```

**Expected Result:**

- **Step 3:** 200 OK, query executes successfully
- **Step 4:** 400 Bad Request with error: "Query depth of 10 exceeds maximum allowed depth of 5"

**Pass Criteria:** Queries within depth limit succeed, queries exceeding limit are rejected with clear error message

---

### Scenario 7: Query Complexity Limiting

**Purpose:** Verify expensive queries are rejected based on complexity score

**Steps:**

1. Configure max query complexity in settings (`.env.dev`):

```bash
GRAPHQL_MAX_QUERY_COMPLEXITY=100
```

2. Restart development server
3. Send simple query (low complexity):

```graphql
query {
  me {
    id
    email
  }
}
```

4. Send expensive query with multiple list fields (high complexity):

```graphql
query {
  users {
    id
    posts {
      id
      comments {
        id
        author {
          posts {
            id
            comments {
              id
            }
          }
        }
      }
    }
  }
}
```

**Expected Result:**

- **Step 3:** 200 OK, query executes
- **Step 4:** 400 Bad Request with error: "Query complexity of [high_number] exceeds maximum allowed complexity of 100"

**Pass Criteria:** Simple queries succeed, complex queries with multiple nested lists are rejected

---

### Scenario 8: Introspection Control in Production

**Purpose:** Verify introspection is disabled in production mode

**Steps:**

1. Set DEBUG=False and disable introspection (`.env.dev`):

```bash
DEBUG=False
GRAPHQL_ENABLE_INTROSPECTION=False
```

2. Restart server
3. Send introspection query for schema:

```graphql
query {
  __schema {
    types {
      name
    }
  }
}
```

4. Send introspection query for type:

```graphql
query {
  __type(name: "User") {
    name
    fields {
      name
      type {
        name
      }
    }
  }
}
```

5. Send regular query:

```graphql
query {
  hello
}
```

6. Re-enable introspection:

```bash
GRAPHQL_ENABLE_INTROSPECTION=True
```

7. Restart server and retry introspection query from step 3

**Expected Result:**

- **Step 3:** Error: "GraphQL introspection is disabled in production"
- **Step 4:** Error: "GraphQL introspection is disabled in production"
- **Step 5:** 200 OK, regular query works
- **Step 7:** 200 OK, introspection query succeeds

**Pass Criteria:** Introspection blocked when disabled, regular queries unaffected, introspection works when enabled

---

### Scenario 9: Introspection Allowed in Development

**Purpose:** Verify introspection is allowed in development mode

**Steps:**

1. Set DEBUG=True (`.env.dev`):

```bash
DEBUG=True
```

2. Restart server
3. Send introspection query:

```graphql
query {
  __schema {
    queryType {
      name
    }
    mutationType {
      name
    }
    types {
      name
      kind
    }
  }
}
```

**Expected Result:**

- **Step 3:** 200 OK, returns complete schema information

**Pass Criteria:** Introspection works in development mode (DEBUG=True)

---

### Scenario 10: Combined Security Features

**Purpose:** Verify all security features work together without conflicts

**Steps:**

1. Configure all security settings (`.env.dev`):

```bash
GRAPHQL_MAX_QUERY_DEPTH=5
GRAPHQL_MAX_QUERY_COMPLEXITY=100
DEBUG=False
GRAPHQL_ENABLE_INTROSPECTION=False
```

2. Restart server
3. Get CSRF token:

```bash
curl -X GET http://localhost:8000/graphql/ -c cookies.txt
```

4. Login with CSRF token:

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <csrf_token>" \
  -b cookies.txt \
  -d '{
    "query": "mutation { login(input: { email: \"owner@test.com\", password: \"TestPassword123!@\" }) { token } }"
  }'
```

5. Send authenticated query with valid depth and complexity:

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "query": "query { me { id email organisation { name } } }"
  }'
```

6. Send deeply nested query (exceeds depth):

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "query": "query { me { organisation { users { organisation { users { organisation { name } } } } } } }"
  }'
```

7. Send introspection query:

```bash
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "query": "query { __schema { types { name } } }"
  }'
```

**Expected Result:**

- **Step 4:** 200 OK, login succeeds with CSRF token
- **Step 5:** 200 OK, valid query succeeds
- **Step 6:** 400 Bad Request, depth limit error
- **Step 7:** Error, introspection disabled

**Pass Criteria:** All security features work together, no conflicts or unexpected behaviours

---

## API Testing

### Endpoint: POST /graphql/

#### Test CSRF Token Retrieval

```bash
# Get CSRF token
curl -X GET http://localhost:8000/graphql/ -v 2>&1 | grep -i csrf
```

**Expected Response:**
CSRF token in `Set-Cookie` header: `csrftoken=<token_value>`

#### Test Authenticated Query

```bash
# Login and get token
TOKEN=$(curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: <csrf_token>" \
  -b cookies.txt \
  -d '{
    "query": "mutation { login(input: { email: \"owner@test.com\", password: \"TestPassword123!@\" }) { token } }"
  }' | jq -r '.data.login.token')

# Use token for authenticated query
curl -X POST http://localhost:8000/graphql/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "query { me { id email firstName lastName } }"
  }' | jq
```

**Expected Response:**

```json
{
  "data": {
    "me": {
      "id": "1",
      "email": "owner@test.com",
      "firstName": "Test",
      "lastName": "Owner"
    }
  }
}
```

---

## Regression Checklist

After making changes to security features, verify these still work:

- [ ] User authentication with JWT tokens
- [ ] User registration and email verification
- [ ] Password reset flow
- [ ] 2FA authentication (TOTP)
- [ ] GraphQL queries without CSRF token
- [ ] GraphQL mutations with CSRF token
- [ ] Organisation boundary enforcement
- [ ] Permission-based access control
- [ ] Query depth limiting
- [ ] Query complexity limiting
- [ ] Introspection control
- [ ] Audit logging of security events

---

## Known Issues

- CSRF middleware enforcement requires Django CSRF middleware to be enabled
- Query depth/complexity limits are approximations, not exact calculations
- Introspection control requires DEBUG and GRAPHQL_ENABLE_INTROSPECTION settings
- Some GraphQL clients (Apollo, Relay) may cache introspection results

---

## Sign-Off

| Tester | Date | Status | Notes |
| ------ | ---- | ------ | ----- |
|        |      |        |       |
