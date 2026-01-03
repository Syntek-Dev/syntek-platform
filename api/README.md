# GraphQL API

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

GraphQL API definition using Strawberry GraphQL with security extensions and customizations.

## Table of Contents

- [GraphQL API](#graphql-api)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Files](#files)
  - [Schema Structure](#schema-structure)
    - [schema.py](#schemapy)
    - [Type Definition Pattern](#type-definition-pattern)
  - [Security Features](#security-features)
    - [Query Depth Limit](#query-depth-limit)
    - [Query Complexity Limit](#query-complexity-limit)
    - [Introspection Control](#introspection-control)
  - [Usage](#usage)
    - [Accessing the GraphQL Endpoint](#accessing-the-graphql-endpoint)
    - [Example Query](#example-query)
    - [Example Mutation](#example-mutation)
    - [Using the API from Python](#using-the-api-from-python)
    - [Using the API from Frontend](#using-the-api-from-frontend)
  - [Development](#development)
    - [Adding a New Query](#adding-a-new-query)
    - [Adding a New Mutation](#adding-a-new-mutation)
    - [Testing Queries](#testing-queries)
    - [Modifying Security Settings](#modifying-security-settings)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains the GraphQL API implementation for the backend template project.

**Framework:** Strawberry GraphQL
**Security:** Query depth limit, query complexity limit, introspection control
**Features:** Type-safe schema, authentication support, audit logging

The API provides a single endpoint that can be queried from frontend applications, mobile apps, and third-party integrations.

---

## Files

| File | Purpose |
|------|---------|
| `schema.py` | Root GraphQL schema definition (Query, Mutation, Subscription types) |
| `security.py` | Security extensions and request validation |
| `urls.py` | URL routing configuration for the GraphQL endpoint |
| `__init__.py` | Package initialization |

---

## Schema Structure

### schema.py

Contains the root GraphQL types:

```python
@strawberry.type
class Query:
    """Root query type for accessing data."""
    # Define query resolvers here

@strawberry.type
class Mutation:
    """Root mutation type for modifying data."""
    # Define mutation resolvers here
```

All types should include docstrings explaining their purpose and return values.

### Type Definition Pattern

Types should follow this pattern:

```python
@strawberry.type
class MyType:
    """Description of the type."""

    field_name: str
    count: int

    @strawberry.field
    def computed_field(self) -> str:
        """Description of computed field."""
        return f"{self.field_name} computed"
```

---

## Security Features

### Query Depth Limit

Prevents deeply nested queries that could impact performance:

```python
# Extension: QueryDepthLimitExtension
# Max depth: 10 levels
# Configurable in security.py
```

**Example blocked query:**
```graphql
query {
  article {
    author {
      profile {
        settings {
          # ... beyond max depth
        }
      }
    }
  }
}
```

### Query Complexity Limit

Limits the total "cost" of a query based on field complexity:

```python
# Extension: QueryComplexityLimitExtension
# Max complexity: 1000
# Configurable per field
```

**How it works:**
- Each field has a complexity score
- Nested fields multiply complexity
- Queries exceeding limit are rejected

### Introspection Control

Controls whether clients can introspect the schema:

```python
# Extension: IntrospectionControlExtension
# Production: Disabled (introspection off)
# Development: Enabled (introspection on)
# Staging: Configurable
```

**What is introspection?**
Introspection allows clients to query the schema itself (`__schema`, `__type`).

**Security implications:**
- Disabled in production to hide API structure
- Enabled in development for tooling support
- Can leak sensitive information

---

## Usage

### Accessing the GraphQL Endpoint

**Development:** `http://localhost:8000/graphql/`
**GraphQL Playground:** Interactive IDE included in development

### Example Query

```graphql
query GetArticles {
  articles(limit: 5) {
    id
    title
    author {
      name
      email
    }
    commentCount
  }
}
```

### Example Mutation

```graphql
mutation CreateArticle {
  createArticle(
    title: "My Article"
    content: "Article content"
  ) {
    article {
      id
      title
      createdAt
    }
    success
    errors
  }
}
```

### Using the API from Python

```python
from strawberry.django.views import GraphQLView
from api.schema import schema

# Already configured in Django URLs
# No additional setup needed
```

### Using the API from Frontend

```javascript
// JavaScript/TypeScript example
const query = `
  query {
    articles(limit: 5) {
      id
      title
    }
  }
`;

const response = await fetch('/graphql/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ query }),
});

const data = await response.json();
```

---

## Development

### Adding a New Query

1. Define the return type:

```python
@strawberry.type
class MyData:
    """Return type for my_data query."""
    value: str
    count: int
```

2. Add the query resolver to Query class:

```python
@strawberry.type
class Query:
    @strawberry.field
    def my_data(self) -> MyData:
        """Retrieve my data.

        Returns the computed data for the client.
        """
        return MyData(value="test", count=42)
```

3. Test the query:

```graphql
query {
  myData {
    value
    count
  }
}
```

### Adding a New Mutation

1. Define input and return types:

```python
@strawberry.input
class CreateMyDataInput:
    """Input for creating new data."""
    name: str
    value: str

@strawberry.type
class CreateMyDataPayload:
    """Return type for create_my_data mutation."""
    success: bool
    data: Optional[MyData] = None
    errors: List[str] = strawberry.field(default_factory=list)
```

2. Add the mutation resolver:

```python
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_my_data(self, input: CreateMyDataInput) -> CreateMyDataPayload:
        """Create new data.

        Args:
            input: The input data for creating new data.

        Returns:
            Payload with created data or errors.
        """
        try:
            # Create the data
            data = MyData(value=input.value, count=0)
            return CreateMyDataPayload(success=True, data=data)
        except Exception as e:
            return CreateMyDataPayload(
                success=False,
                errors=[str(e)]
            )
```

### Testing Queries

```python
# tests/api/test_queries.py
from strawberry.django.testing import GraphQLTestClient
from config.wsgi import application

def test_my_query():
    client = GraphQLTestClient(application)

    query = """
    query {
      myData {
        value
        count
      }
    }
    """

    result = client.query(query)

    assert result.errors is None
    assert result.data["myData"]["value"] == "test"
```

### Modifying Security Settings

Edit `security.py` to adjust limits:

```python
# QueryDepthLimitExtension
# Change: max_depth = 10
# to:     max_depth = 15

# QueryComplexityLimitExtension
# Change: max_complexity = 1000
# to:     max_complexity = 2000

# IntrospectionControlExtension
# Change: allowed = DEBUG
# to:     allowed = True  # Always allow
```

---

## Related Documentation

- [API Security](../docs/SECURITY/SECURITY.md) - Comprehensive security guide
- [Setup Guide](../docs/DEVELOPER-SETUP.md) - Development environment setup
- [Strawberry GraphQL Docs](https://strawberry.rocks/) - Official Strawberry documentation

---

**Last Updated:** 2026-01-03
