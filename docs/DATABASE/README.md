# Database Documentation

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [Database Documentation](#database-documentation)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [Database Technology](#database-technology)
    - [PostgreSQL](#postgresql)
    - [Django ORM](#django-orm)
    - [Database Environments](#database-environments)
  - [Schema Management](#schema-management)
    - [Migrations](#migrations)
    - [Creating Migrations](#creating-migrations)
    - [Migration Naming Convention](#migration-naming-convention)
  - [Documentation by Phase](#documentation-by-phase)
    - [Phase 1: Core Authentication Schema](#phase-1-core-authentication-schema)
  - [Migration Management](#migration-management)
    - [Commands](#commands)
    - [Best Practices](#best-practices)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains comprehensive database documentation, including schema definitions,
migration histories, database design decisions, and entity relationship diagrams for each
development phase.

**Database**: PostgreSQL 18.1+
**ORM**: Django ORM
**Migration Tool**: Django Migrations

---

## Directory Structure

```
DATABASE/
├── README.md                # This file
└── US-001/                  # User Story 001 - Authentication Database Schema
    └── [Schema and migration documentation]
```

---

## Database Technology

### PostgreSQL

**Version**: 18.1+
**Features Used:**

- JSONB for flexible content storage
- UUID for distributed identifiers
- Full-text search capabilities
- Encryption for sensitive fields
- Transaction support for data integrity
- Index optimisation for query performance

### Django ORM

**Features:**

- Object-relational mapping for Python models
- Migration system for schema versioning
- Query optimisation with select_related/prefetch_related
- Transaction management with atomic operations
- Signal system for event-driven operations

### Database Environments

| Environment | Database             | Cache           | Backup              |
| ----------- | -------------------- | --------------- | ------------------- |
| Development | PostgreSQL Container | Redis Container | Local snapshots     |
| Testing     | PostgreSQL Container | Redis Container | Ephemeral (cleaned) |
| Staging     | PostgreSQL (AWS/DO)  | Redis (managed) | Daily snapshots     |
| Production  | PostgreSQL (AWS/DO)  | Redis (managed) | Hourly snapshots    |

---

## Schema Management

### Migrations

All database schema changes are managed through Django migrations located in:

```
apps/[app_name]/migrations/
```

### Creating Migrations

```bash
# Generate migration files
./scripts/env/dev.sh makemigrations

# Apply migrations
./scripts/env/dev.sh migrate

# Show migration status
./scripts/env/dev.sh showmigrations
```

### Migration Naming Convention

Migrations follow Django's auto-generated naming:

```
0001_initial.py
0002_add_field_to_model.py
0003_alter_model_field.py
```

---

## Documentation by Phase

### Phase 1: Core Authentication Schema

**Location**: `US-001/`

Documents the database schema for user authentication including:

- User model and related tables
- Authentication token tables
- Session management tables
- Password management tables
- Two-factor authentication tables
- Audit logging tables
- Multi-tenancy schema design
- Index definitions
- Constraint specifications
- Relationship diagrams

**Status**: In Progress

---

## Migration Management

### Commands

```bash
# Create migrations for changes
./scripts/env/dev.sh makemigrations

# Apply pending migrations
./scripts/env/dev.sh migrate

# Check migration status
./scripts/env/dev.sh showmigrations

# Reverse migrations (development only)
./scripts/env/dev.sh migrate [app] [migration_number]
```

### Best Practices

1. Create migrations for all schema changes
2. Never edit migration files after they're created
3. Always test migrations locally first
4. Review migration SQL before applying to production
5. Keep migrations small and focused
6. Write descriptive migration names
7. Document complex migrations with comments

---

## Related Documentation

- [Database Design](US-001/README.md) - Phase 1 schema documentation
- [Project Overview](../../README.md) - Project overview
- [Core App Models](../../apps/core/models/README.md) - Model definitions
- [Architecture](../ARCHITECTURE/) - System architecture
- [Development Setup](../DEVELOPER-SETUP.md) - Database setup guide
- [Testing](../TESTS/) - Testing with test databases

---

**Project:** Backend Template
**Database**: PostgreSQL 18.1+
**ORM**: Django 5.2
**Last Updated:** 08/01/2026
