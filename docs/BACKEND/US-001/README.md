# User Story 001 - Authentication API Documentation

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [User Story 001 - Authentication API Documentation](#user-story-001---authentication-api-documentation)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [API Documentation](#api-documentation)
    - [BACKEND-REVIEW-US-001.md](#backend-review-us-001md)
  - [GraphQL Operations](#graphql-operations)
    - [User Registration](#user-registration)
    - [User Login](#user-login)
    - [Enable 2FA](#enable-2fa)
    - [Verify Email](#verify-email)
  - [Authentication Endpoints](#authentication-endpoints)
    - [POST /graphql/](#post-graphql)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains comprehensive API documentation for User Story 001 (User Authentication).
It documents all GraphQL mutations, queries, and types related to user authentication, two-factor
authentication, session management, and password reset flows.

**Phase**: Phase 1 - Core Authentication
**API Type**: GraphQL (Strawberry)
**Status**: In Progress

---

## Directory Structure

```
US-001/
├── README.md                    # This file
└── BACKEND-REVIEW-US-001.md     # Complete API specification and implementation review
```

---

## API Documentation

### BACKEND-REVIEW-US-001.md

Comprehensive API documentation covering:

- GraphQL schema for authentication types
- User type definition
- Authentication token type
- 2FA device type
- Session type
- Mutation specifications
  - Register user mutation
  - Login mutation
  - Logout mutation
  - Enable 2FA mutation
  - Disable 2FA mutation
  - Request password reset mutation
  - Confirm password reset mutation
  - Verify email mutation
- Query specifications
  - Current user query
  - Session list query
  - 2FA devices query
- Error codes and handling
- Request/response examples
- Authentication headers
- Rate limiting information
- Validation rules

**Use this when:**

- Understanding authentication API endpoints
- Implementing frontend authentication flows
- Testing GraphQL mutations
- Debugging authentication issues
- Writing API integration tests

---

## GraphQL Operations

### User Registration

```graphql
mutation RegisterUser {
  registerUser(
    email: "user@example.com"
    password: "secure_password"
    firstName: "John"
    lastName: "Doe"
  ) {
    user {
      id
      email
      firstName
      lastName
    }
    token
    errors
  }
}
```

### User Login

```graphql
mutation LoginUser {
  loginUser(email: "user@example.com", password: "secure_password") {
    user {
      id
      email
    }
    token
    requiresTwoFactor
    errors
  }
}
```

### Enable 2FA

```graphql
mutation EnableTwoFactor {
  enableTwoFactor {
    secret
    qrCodeUrl
    backupCodes
    errors
  }
}
```

### Verify Email

```graphql
mutation VerifyEmail {
  verifyEmail(token: "email_verification_token") {
    success
    errors
  }
}
```

---

## Authentication Endpoints

### POST /graphql/

Single GraphQL endpoint for all API operations.

**Headers:**

```
Content-Type: application/json
Authorization: Bearer <token>  # For authenticated requests
```

**Request Body:**

```json
{
  "query": "mutation { loginUser(...) { ... } }",
  "variables": {},
  "operationName": "LoginUser"
}
```

**Response:**

```json
{
  "data": {
    "loginUser": {
      "user": { "id": "123", "email": "user@example.com" },
      "token": "eyJhbGc...",
      "errors": []
    }
  }
}
```

---

## Related Documentation

- [Parent Backend Documentation](../README.md) - Backend API index
- [Architecture](../../ARCHITECTURE/US-001/README.md) - System design
- [Implementation](../../AUTH/US-001/README.md) - Implementation details
- [User Story](../../STORIES/US-001-USER-AUTHENTICATION.md) - Requirements
- [GraphQL API](../../../api/README.md) - GraphQL configuration
- [Core App Services](../../../apps/core/services/README.md) - Service implementations

---

**Project:** Backend Template
**Framework:** Django 5.2
**API Type:** GraphQL (Strawberry)
**Last Updated:** 08/01/2026
