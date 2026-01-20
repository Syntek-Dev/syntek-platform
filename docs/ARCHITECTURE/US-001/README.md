# User Story 001 - Architecture Documentation

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [User Story 001 - Architecture Documentation](#user-story-001---architecture-documentation)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [Key Documents](#key-documents)
    - [ARCHITECTURE-REVIEW.md](#architecture-reviewmd)
  - [Architecture Decisions](#architecture-decisions)
    - [Key Design Decisions](#key-design-decisions)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains architecture-specific documentation for User Story 001 (User Authentication
Phase 1). It documents the system design decisions, technical specifications, and implementation
architecture for the core authentication system.

**Phase**: Phase 1 - Core Authentication
**Status**: In Progress
**Components**: User model, 2FA, Session management, Password reset, Audit logging

---

## Directory Structure

```
US-001/
├── README.md                         # This file
└── ARCHITECTURE-REVIEW.md            # Detailed architecture analysis and design decisions
```

---

## Key Documents

### ARCHITECTURE-REVIEW.md

Comprehensive architecture documentation covering:

- System design decisions and rationale
- User model structure and relationships
- Authentication flow architecture
- 2FA implementation design (TOTP)
- Session token management
- Password reset workflow
- Audit logging architecture
- Multi-tenancy isolation design
- Security considerations and mitigations
- Database schema decisions
- API endpoint architecture

**Use this when:**

- Understanding Phase 1 design decisions
- Reviewing authentication architecture
- Planning feature extensions
- Implementing related components
- Conducting security reviews

---

## Architecture Decisions

### Key Design Decisions

**User Authentication Model**

- Email/password authentication with secure hashing (Bcrypt)
- Session tokens instead of cookies for API-first design
- TOTP-based 2FA with backup codes for recovery
- Multi-organisation support with organisation-scoped tokens

**Security Architecture**

- Encrypted IP address tracking for audit logging
- Time-limited tokens with expiration
- Password history tracking to prevent reuse
- Email verification before account activation
- Rate limiting on sensitive operations

**Database Design**

- Custom user model extending Django AbstractUser
- Separate tables for TOTP devices, session tokens, and password history
- Audit logging for authentication events
- Index optimisation for performance-critical queries

**API Design**

- GraphQL-first API using Strawberry
- Mutation-based authentication operations
- Token in Authorization header
- Comprehensive error handling and validation

---

## Related Documentation

- [Parent Architecture](../README.md) - Architecture documentation index
- [User Story 001](../../STORIES/US-001-USER-AUTHENTICATION.md) - Requirements and acceptance
  criteria
- [Authentication Guide](../../AUTH/README.md) - Authentication documentation
- [Core App](../../../apps/core/README.md) - Implementation details
- [User Models](../../../apps/core/models/README.md) - Model documentation
- [Database Schema](../../DATABASE/) - Schema documentation

---

**Project:** Backend Template
**Framework:** Django 5.2
**Last Updated:** 08/01/2026
