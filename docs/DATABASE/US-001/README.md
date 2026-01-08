# User Story 001 - Database Schema Documentation

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [User Story 001 - Database Schema Documentation](#user-story-001---database-schema-documentation)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [Schema Documentation](#schema-documentation)
    - [US-001-DATABASE-REVIEW.md](#us-001-database-reviewmd)
  - [Core Tables](#core-tables)
    - [Primary Authentication Tables](#primary-authentication-tables)
  - [Relationships](#relationships)
    - [User to Sessions](#user-to-sessions)
    - [User to 2FA Devices](#user-to-2fa-devices)
    - [User to Password Reset Tokens](#user-to-password-reset-tokens)
    - [User to Audit Log](#user-to-audit-log)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains comprehensive database schema documentation for User Story 001 (User
Authentication). It documents all tables, columns, constraints, indexes, and relationships
required for authentication, session management, and user account management.

**Phase**: Phase 1 & 2 - Core Authentication & Service Layer
**Database**: PostgreSQL 18.1+
**Phase 1 Status**: ✅ Complete
**Phase 2 Status**: ✅ Complete

---

## Directory Structure

```
US-001/
├── README.md                        # This file
└── US-001-DATABASE-REVIEW.md        # Complete schema design and documentation
```

---

## Schema Documentation

### US-001-DATABASE-REVIEW.md

Comprehensive database schema documentation covering:

**Phase 1 (Core Models):**

- Complete table definitions
- Column specifications with types and constraints
- Primary keys and unique constraints
- Foreign key relationships
- Index definitions and optimisation
- Constraint specifications
- Data integrity rules
- Trigger definitions (if any)
- Encryption strategies for sensitive fields
- Multi-tenancy isolation design
- Query performance optimisations
- Entity relationship diagrams
- Migration strategies

**Phase 2 (Service Layer & Security):**

- HMAC-SHA256 token hashing implementation (C1, C3)
- IP encryption with key rotation support (C6)
- Token family pattern for replay detection (H9)
- Single-use token validation (H12)
- Performance indexes for multi-tenant queries
- Query performance benchmarks
- Environment configuration requirements
- Token lifecycle management
- Migration 0006 documentation

**Use this when:**

- Understanding the authentication schema
- Designing related features
- Writing complex queries
- Optimising database performance
- Conducting database reviews
- Implementing security features
- Configuring environment variables

---

## Core Tables

### Primary Authentication Tables

**auth_user**

- Core user account information
- Email and password storage
- Account status and settings
- Timestamps for audit trail

**auth_session_token**

- API authentication tokens
- Token expiration and refresh
- Device and IP tracking
- Multi-device session management

**auth_totp_device**

- Two-factor authentication TOTP devices
- Secret key storage (encrypted)
- Backup codes
- Device status and verification

**auth_password_reset_token**

- Password reset flow tokens
- Token expiration for security
- Verification status

**auth_email_verification_token**

- Email verification tokens
- Token lifecycle management
- Verification status tracking

**auth_password_history**

- Password change audit trail
- Previous password hashes
- Prevention of password reuse

**auth_audit_log**

- Comprehensive audit trail
- Authentication events
- IP address tracking (encrypted)
- User agent tracking
- Event timestamps

---

## Relationships

### User to Sessions

- One user can have multiple active sessions
- Sessions are organisation-scoped
- Sessions track device and IP information

### User to 2FA Devices

- One user can have multiple TOTP devices
- Devices linked to specific authentication methods
- Primary device designation for backup codes

### User to Password Reset Tokens

- One-to-many relationship for password reset requests
- Tokens expire after 24 hours
- One active token per user

### User to Audit Log

- One-to-many comprehensive audit trail
- All authentication events logged
- Searchable by user, organisation, and time range

---

## Related Documentation

- [Parent Database Documentation](../README.md) - Database index
- [Architecture](../../ARCHITECTURE/US-001/README.md) - Design decisions
- [Implementation](../../AUTH/US-001/README.md) - Implementation details
- [Core Models](../../../apps/core/models/README.md) - Model definitions
- [User Story](../../STORIES/US-001-USER-AUTHENTICATION.md) - Requirements
- [Migrations](../../../apps/core/migrations/) - Migration files

---

**Project:** Backend Template
**Database**: PostgreSQL 18.1+
**Framework**: Django 5.2
**Last Updated:** 08/01/2026
