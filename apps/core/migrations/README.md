# Core App Migrations

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [Core App Migrations](#core-app-migrations)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [Migration Files](#migration-files)
  - [Creating Migrations](#creating-migrations)
    - [Automatic Migration Generation](#automatic-migration-generation)
    - [Manual Migration Creation](#manual-migration-creation)
  - [Applying Migrations](#applying-migrations)
    - [Running Migrations](#running-migrations)
    - [Reversing Migrations (Development Only)](#reversing-migrations-development-only)
  - [Migration Best Practices](#migration-best-practices)
    - [For New Migrations](#for-new-migrations)
    - [For Data Migrations](#for-data-migrations)
    - [For Production](#for-production)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains all Django database migrations for the core application. Migrations are
automatically generated Python files that describe the changes made to the database schema over
time.

**Framework**: Django 5.2
**Database**: PostgreSQL 18.1+
**ORM**: Django ORM with migrations

---

## Directory Structure

```
migrations/
├── README.md                                           # This file
├── __init__.py                                         # Python package marker
├── 0001_initial.py                                     # Initial schema creation
├── 0002_alter_sessiontoken_options_*.py                # Session token model updates
├── 0003_create_default_groups.py                       # Default permission groups
├── 0004_alter_organisation_options_and_more.py         # Organisation updates
├── 0005_remove_sessiontoken_session_tok_*.py           # Index optimisations
└── 0006_auditlog_audit_logs_user_id_*.py               # Audit log indexes
```

---

## Migration Files

| Migration File                                | Description                                                        | Tables Affected                                                                                                                  | Status    |
| --------------------------------------------- | ------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------- | --------- |
| `0001_initial.py`                             | Initial schema with User, Organisation, tokens, 2FA, audit logging | User, UserProfile, Organisation, SessionToken, EmailVerificationToken, PasswordResetToken, TOTPDevice, PasswordHistory, AuditLog | Completed |
| `0002_alter_sessiontoken_options_*`           | Metadata and options updates for token models                      | SessionToken, TOTPDevice                                                                                                         | Completed |
| `0003_create_default_groups.py`               | Creates default permission groups (Admin, Manager, User, Guest)    | Group                                                                                                                            | Completed |
| `0004_alter_organisation_options_and_more.py` | Organisation model updates and optimisations                       | Organisation, related models                                                                                                     | Completed |
| `0005_remove_sessiontoken_session_tok_*`      | Removes duplicate indexes, optimises indexing                      | SessionToken, AuditLog                                                                                                           | Completed |
| `0006_auditlog_audit_logs_user_id_*`          | Adds performance indexes to AuditLog table                         | AuditLog                                                                                                                         | Completed |

---

## Creating Migrations

### Automatic Migration Generation

When you modify Django models in `apps/core/models/`, Django automatically detects changes and
creates migration files:

```bash
# Generate migration files for all changes
./scripts/env/dev.sh makemigrations

# Generate migrations for a specific app
./scripts/env/dev.sh makemigrations core

# See what migrations would be created (dry run)
./scripts/env/dev.sh makemigrations --dry-run --verbosity 3
```

### Manual Migration Creation

For complex operations or data migrations:

```bash
# Create an empty migration for manual coding
./scripts/env/dev.sh makemigrations core --empty --name="custom_migration_name"
```

---

## Applying Migrations

### Running Migrations

Apply pending migrations to the database:

```bash
# Apply all pending migrations
./scripts/env/dev.sh migrate

# Apply migrations for a specific app
./scripts/env/dev.sh migrate core

# Apply up to a specific migration
./scripts/env/dev.sh migrate core 0004

# Show migration status
./scripts/env/dev.sh showmigrations
```

### Reversing Migrations (Development Only)

Undo migrations in development environments:

```bash
# Reverse all migrations for an app
./scripts/env/dev.sh migrate core zero

# Reverse to a specific migration
./scripts/env/dev.sh migrate core 0003
```

---

## Migration Best Practices

### For New Migrations

1. **Run makemigrations** before making any commits

   ```bash
   ./scripts/env/dev.sh makemigrations
   ```

2. **Review generated migrations** to ensure they're correct

   ```bash
   # Check the SQL that will be executed
   ./scripts/env/dev.sh sqlmigrate core 0001
   ```

3. **Test migrations locally** before pushing to remote

   ```bash
   ./scripts/env/dev.sh migrate
   ```

4. **Never edit migrations** after they've been created and committed
   - If you need to fix a migration, create a new one

5. **Keep migrations small and focused**
   - One logical change per migration
   - Easier to debug and reverse if needed

6. **Write descriptive migration names**
   - Use clear names: `0007_add_email_to_user.py` (good)
   - Avoid generic names: `0007_auto.py` (bad)

### For Data Migrations

When creating data migrations (moving data, complex transformations):

```python
# Example data migration
from django.db import migrations

def forward(apps, schema_editor):
    """Forward migration logic."""
    User = apps.get_model('core', 'User')
    for user in User.objects.all():
        user.full_name = f"{user.first_name} {user.last_name}"
        user.save()

def backward(apps, schema_editor):
    """Backward/rollback logic."""
    User = apps.get_model('core', 'User')
    for user in User.objects.all():
        user.full_name = ""
        user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auditlog_audit_logs_user_id_d685f3_idx_and_more'),
    ]

    operations = [
        migrations.RunPython(forward, backward),
    ]
```

### For Production

1. **Create database backups** before applying migrations

   ```bash
   ./scripts/env/production.sh backup
   ```

2. **Test migrations in staging first**

   ```bash
   ./scripts/env/staging.sh migrate
   ```

3. **Review migration SQL** before applying to production

   ```bash
   ./scripts/env/production.sh sqlmigrate core [migration_number]
   ```

4. **Apply migrations during low-traffic periods**

5. **Monitor the application** after migration completion

6. **Have rollback plan** in case of issues

---

## Related Documentation

- [Core App Overview](../README.md) - Core app structure and purpose
- [Core Models](../models/README.md) - Model definitions and schema
- [Database Documentation](../../docs/DATABASE/) - Overall database architecture
- [Development Setup](../../docs/SETUP/) - Setting up development environment
- [User Authentication Phase 1](../../docs/ARCHITECTURE/US-001/) - Auth schema details

---

**Project:** Backend Template
**Framework:** Django 5.2
**Database**: PostgreSQL 18.1+
**Last Updated:** 08/01/2026
