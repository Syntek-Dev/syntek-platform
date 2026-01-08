# Backend API Documentation

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [Backend API Documentation](#backend-api-documentation)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [API Technology](#api-technology)
    - [GraphQL with Strawberry](#graphql-with-strawberry)
    - [Security Features](#security-features)
  - [Documentation by Phase](#documentation-by-phase)
    - [Phase 1: Core Authentication API](#phase-1-core-authentication-api)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains comprehensive backend API documentation, including GraphQL schema
definitions, endpoint specifications, and implementation details for each development phase.

**API Type**: GraphQL with Strawberry
**Authentication**: Token-based
**Format**: JSON
**Base URL**: `/graphql/`

---

## Directory Structure

```
BACKEND/
├── README.md            # This file
└── US-001/              # User Story 001 - Authentication API
    └── [API documentation for authentication endpoints]
```

---

## API Technology

### GraphQL with Strawberry

**Framework**: Strawberry GraphQL
**Python Version**: 3.14+
**Django Version**: 5.2+

**Features:**

- Type-safe schema with Python type hints
- Query depth limiting to prevent expensive queries
- Query complexity analysis for protection
- Introspection control (disabled in production)
- Built-in error handling and validation
- Support for mutations and subscriptions
- Authentication middleware integration

### Security Features

- **Authentication**: Token-based using Authorization header
- **Authorization**: Organisation-based scope checking
- **Rate Limiting**: IP-based rate limits on sensitive operations
- **Query Protection**: Depth and complexity limits
- **Error Handling**: Generic error messages in production
- **Logging**: Comprehensive audit logging of all operations

---

## Documentation by Phase

### Phase 1: Core Authentication API

**Location**: `US-001/`

Documents the GraphQL schema and operations for user authentication including:

- User registration mutations
- Login and logout operations
- Two-factor authentication (2FA) setup
- Password reset flow
- Session management queries
- Profile management
- Email verification

**Status**: In Progress

---

## Related Documentation

- [API Overview](../../README.md) - Project overview
- [Core App](../../apps/core/README.md) - Django app implementation
- [GraphQL API](../../api/README.md) - GraphQL configuration
- [Security](../SECURITY/README.md) - Security implementation
- [Architecture](../ARCHITECTURE/README.md) - System architecture
- [User Stories](../STORIES/) - Feature specifications
- [Testing](../TESTS/) - Test documentation

---

**Project:** Backend Template
**Framework:** Django 5.2
**API Type:** GraphQL (Strawberry)
**Last Updated:** 08/01/2026
