# User Authentication System (US-001) - Comprehensive Database Review

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Reviewed By**: Database Administrator (DBA) Agent, Database Specialist, Database Architecture Team
**Status**: Complete - Ready for Implementation with Critical Recommendations
**Language**: British English (en_GB)
**Timezone**: Europe/London
**Phase 1 Status**: ✅ Completed

---

## Table of Contents

- [User Authentication System (US-001) - Comprehensive Database Review](#user-authentication-system-us-001---comprehensive-database-review)
  - [Table of Contents](#table-of-contents)
  - [Executive Summary](#executive-summary)
  - [1. Overall Assessment](#1-overall-assessment)
  - [2. Schema Design Analysis](#2-schema-design-analysis)
    - [Normalisation Assessment](#normalisation-assessment)
    - [Table Structure Review](#table-structure-review)
    - [Primary Key Strategy](#primary-key-strategy)
  - [3. Foreign Key Relationships and Cascading](#3-foreign-key-relationships-and-cascading)
  - [4. Index Strategy Assessment](#4-index-strategy-assessment)
    - [Current Index Coverage](#current-index-coverage)
    - [Missing Indexes (Critical)](#missing-indexes-critical)
    - [Recommended Index Strategy](#recommended-index-strategy)
  - [5. Data Integrity and Constraints](#5-data-integrity-and-constraints)
  - [6. Query Performance Considerations](#6-query-performance-considerations)
    - [Hot-Path Queries](#hot-path-queries)
    - [N+1 Query Prevention](#n1-query-prevention)
    - [Query Optimisation Patterns](#query-optimisation-patterns)
  - [7. Multi-Tenancy and Isolation](#7-multi-tenancy-and-isolation)
  - [8. Migration Strategy](#8-migration-strategy)
  - [9. Scalability and Performance Targets](#9-scalability-and-performance-targets)
  - [10. Security Review](#10-security-review)
  - [11. PostgreSQL-Specific Optimisations](#11-postgresql-specific-optimisations)
  - [Critical Recommendations Summary](#critical-recommendations-summary)
  - [Implementation Roadmap](#implementation-roadmap)
  - [Conclusion](#conclusion)

---

## Executive Summary

The database schema for the User Authentication System (US-001) demonstrates a solid foundation with excellent security practices, proper normalisation, and thoughtful multi-tenancy design. The use of UUIDs for primary keys, encrypted storage for sensitive data (IP addresses), and comprehensive audit logging shows strong architectural awareness.

### Overall Grade: ✅ Approved for Implementation with Critical Improvements

**Strengths:**

- Proper 3NF normalisation with clear separation of concerns
- UUID primary keys for security and distributed systems
- Multi-tenancy via organisation foreign keys with proper isolation
- Encrypted storage for PII (IP addresses)
- Comprehensive audit logging with SET_NULL on user deletion
- Abstract BaseToken pattern for DRY principle
- Appropriate data types and field naming conventions

**Critical Issues Requiring Immediate Attention:**

1. Missing composite indexes for multi-tenant queries
2. Missing indexes on token expiry fields (expires_at)
3. Suboptimal audit log indexes for date-range queries
4. Missing database-level constraints for data integrity
5. AuditLog.organisation uses CASCADE (should be SET_NULL)
6. User.organisation not nullable (prevents platform superusers)
7. No Row-Level Security (RLS) for database-level multi-tenancy enforcement

**Impact if Recommendations Not Implemented:**

- Login queries will have poor performance as scale increases
- Token cleanup operations will cause full table scans
- Audit log queries for compliance reporting will be slow
- Data integrity issues could occur due to missing constraints
- Potential cross-organisation data leaks without RLS

---

## 1. Overall Assessment

| Category          | Rating     | Status                         |
| ----------------- | ---------- | ------------------------------ |
| Normalisation     | ⭐⭐⭐⭐⭐ | 3NF - Excellent                |
| Security          | ⭐⭐⭐⭐   | Strong with minor improvements |
| Multi-Tenancy     | ⭐⭐⭐⭐⭐ | Excellent isolation pattern    |
| Performance       | ⭐⭐⭐     | Good foundation, needs indexes |
| Audit Trail       | ⭐⭐⭐⭐   | Good design, fix CASCADE issue |
| Data Types        | ⭐⭐⭐⭐   | Appropriate choices            |
| Scalability       | ⭐⭐⭐⭐   | Supports 10K+ users/org        |
| Compliance (GDPR) | ⭐⭐⭐⭐   | Excellent with minor fixes     |
| **Overall**       | **4.1/5**  | **Approved with improvements** |

---

## 2. Schema Design Analysis

### Normalisation Assessment

**Target**: Third Normal Form (3NF)
**Achieved**: 3NF ✅

The schema demonstrates excellent normalisation:

| Table                       | NF Level | Assessment                             |
| --------------------------- | -------- | -------------------------------------- |
| `organisations`             | 3NF      | All columns depend on primary key only |
| `users`                     | 3NF      | All columns depend on user ID          |
| `user_profiles`             | 3NF      | Correctly separated from users         |
| `totp_devices`              | 3NF      | No transitive dependencies             |
| `session_tokens`            | 3NF      | Token data depends only on session     |
| `password_reset_tokens`     | 3NF      | Properly normalised                    |
| `email_verification_tokens` | 3NF      | Properly normalised                    |
| `audit_logs`                | 3NF      | Immutable event log, no anomalies      |

**Strengths:**

- All foreign keys properly defined with descriptive `related_name` attributes
- No redundant data duplication across tables
- Clear separation of concerns (authentication vs profile vs tokens vs audit)

### Table Structure Review

**User Model**

Strengths:

- UUID primary key for security
- Email as USERNAME_FIELD (modern best practice)
- Encrypted IP address storage (last_login_ip)
- Boolean flags for email verification and 2FA status
- Proper inheritance from AbstractBaseUser

Issues to address:

- `organisation` field should be nullable for platform superusers
- Missing indexes on `email_verified`, `two_factor_enabled`
- Missing composite indexes for multi-tenant queries

**Organisation Model**

Strengths:

- Simple, focused design with UUID primary key
- Unique slug for URL-safe identifiers
- is_active flag for soft deletion support

Issues to address:

- Missing index on `is_active` field
- No soft delete pattern implemented

**Token Models (BaseToken Abstract Pattern)**

Strengths:

- Excellent DRY principle with abstract base class
- Provides `is_expired()` and `is_valid()` helper methods
- Centralised token expiration logic
- Proper inheritance by SessionToken, PasswordResetToken, EmailVerificationToken

Issues to address:

- Missing index on `expires_at` for cleanup queries (CRITICAL)
- Missing composite indexes on `(user, expires_at)`
- No data retention/cleanup strategy documented

**AuditLog Model**

Strengths:

- Immutable design (read-only in admin)
- SET_NULL on user deletion preserves logs
- Encrypted IP addresses (GDPR compliant)
- JSON metadata for flexibility
- Comprehensive action choices

Issues to address:

- CASCADE on organisation (should be SET_NULL) - DATA LOSS RISK
- Missing composite indexes for filtered queries
- No partitioning strategy for long-term storage
- Missing index on `created_at` alone

### Primary Key Strategy

**Decision**: UUID v4 for all tables

**Assessment**: ✅ Excellent choice for this use case

**Advantages:**

- Security: Non-sequential IDs prevent enumeration attacks
- Distributed systems: No coordination required for ID generation
- Multi-tenancy: Clean separation across organisations
- Future scalability: Enables database sharding without ID conflicts

**Performance Considerations:**

- Storage overhead: 16 bytes vs 8 bytes (2x larger than BIGINT)
- Index size: ~25% larger than integer indexes
- Insert performance: ~15-20% slower due to random distribution
- Mitigation: Indexes and caching reduce real-world impact

**Recommendation**: Consider UUID v7 (time-ordered) in Phase 2 for better index locality

---

## 3. Foreign Key Relationships and Cascading

### Current CASCADE Behaviour

| Relationship                  | ON DELETE | Assessment        | Recommendation              |
| ----------------------------- | --------- | ----------------- | --------------------------- |
| User → Organisation           | CASCADE   | ✅ Appropriate    | Keep CASCADE (users belong) |
| UserProfile → User            | CASCADE   | ✅ Appropriate    | Keep CASCADE (extension)    |
| SessionToken → User           | CASCADE   | ⚠️ Review         | PROTECT or manual cleanup   |
| PasswordResetToken → User     | CASCADE   | ✅ Appropriate    | Keep CASCADE (temporary)    |
| EmailVerificationToken → User | CASCADE   | ✅ Appropriate    | Keep CASCADE (temporary)    |
| TOTPDevice → User             | CASCADE   | ✅ Appropriate    | Keep CASCADE (user-owned)   |
| AuditLog → User               | SET_NULL  | ✅ Excellent      | Preserves audit trail ✅    |
| AuditLog → Organisation       | CASCADE   | 🔴 CRITICAL ISSUE | MUST change to SET_NULL     |

### Critical Issues

**Issue 1: AuditLog.organisation CASCADE (DATA LOSS RISK)**

```python
# CURRENT (PROBLEMATIC):
organisation = models.ForeignKey(
    Organisation,
    on_delete=models.CASCADE,  # ❌ Deletes all audit logs when org deleted
    related_name='audit_logs'
)

# RECOMMENDED (SAFE):
organisation = models.ForeignKey(
    Organisation,
    on_delete=models.SET_NULL,  # ✅ Preserves audit logs
    null=True,
    blank=True,
    related_name='audit_logs'
)
```

**Impact**: Deleting an organisation would delete ALL audit logs (GDPR violation, compliance risk)

**Issue 2: User.organisation Not Nullable (Superuser Problem)**

```python
# CURRENT (RESTRICTIVE):
organisation = models.ForeignKey(
    'Organisation',
    on_delete=models.CASCADE,
    related_name='users'
    # ❌ All users must belong to an organisation
)

# RECOMMENDED (FLEXIBLE):
organisation = models.ForeignKey(
    'Organisation',
    on_delete=models.CASCADE,
    related_name='users',
    null=True,  # ✅ Allow platform superusers
    blank=True
)
```

**Impact**: Platform-level superusers cannot exist (they must be tied to an organisation)

---

## 4. Index Strategy Assessment

### Current Index Coverage

**User Table**

- `email` (unique) ✅
- `(organisation, created_at)` ✅

**Organisation Table**

- `slug` (unique) ✅

**AuditLog Table**

- `(user, created_at)` ✅
- `(organisation, created_at)` ✅
- `(action, created_at)` ✅

**SessionToken Table**

- `(user, created_at)` ✅
- `token_hash` (unique) ✅

### Missing Indexes (Critical)

| Table                  | Missing Index                           | Impact        | Priority |
| ---------------------- | --------------------------------------- | ------------- | -------- |
| User                   | `(organisation, email)`                 | Login queries | Critical |
| User                   | `(organisation, is_active, created_at)` | User listings | Critical |
| SessionToken           | `expires_at`                            | Token cleanup | Critical |
| SessionToken           | `(user, expires_at)`                    | User sessions | Critical |
| PasswordResetToken     | `expires_at`                            | Token cleanup | Critical |
| PasswordResetToken     | `(user, created_at)`                    | Recent tokens | High     |
| EmailVerificationToken | `expires_at`                            | Token cleanup | Critical |
| EmailVerificationToken | `(user, created_at)`                    | Recent tokens | High     |
| AuditLog               | `(organisation, action, created_at)`    | Audit reports | Critical |
| TOTPDevice             | `(user, confirmed)`                     | 2FA checks    | High     |

### Recommended Index Strategy

**1. Composite Indexes for Multi-Tenant Queries**

```python
# User model
models.Index(fields=['organisation', 'email'], name='users_org_email_idx'),
models.Index(
    fields=['organisation', 'is_active', '-created_at'],
    name='users_org_active_created_idx'
),
models.Index(
    fields=['organisation', 'email_verified', '-created_at'],
    name='users_org_verified_created_idx'
),
```

**2. Indexes for Token Expiry (CRITICAL)**

```python
# All token models must have expiry index
models.Index(fields=['expires_at'], name='%(class)s_expires_idx'),
```

**3. Composite Indexes for AuditLog Filtering**

```python
models.Index(
    fields=['organisation', 'action', '-created_at'],
    name='audit_org_action_created_idx'
),
models.Index(
    fields=['user', 'action', '-created_at'],
    name='audit_user_action_created_idx'
),
```

**4. Partial Indexes for Active Records (PostgreSQL 11+)**

```python
# Only index active users (smaller index, faster queries)
models.Index(
    fields=['organisation', '-created_at'],
    name='users_active_org_idx',
    condition=models.Q(is_active=True)
),

# Only index unexpired sessions
models.Index(
    fields=['user', '-last_activity'],
    name='session_active_idx',
    condition=models.Q(expires_at__gt=models.F('created_at'))
),
```

---

## 5. Data Integrity and Constraints

### Existing Constraints ✅

- `users.email` - UNIQUE constraint
- `organisations.slug` - UNIQUE constraint
- `session_tokens.token_hash` - UNIQUE constraint
- `password_reset_tokens.token` - UNIQUE constraint
- `email_verification_tokens.token` - UNIQUE constraint
- All ForeignKey relationships enforced

### Missing Constraints (Must Add)

**Email Format Validation**

```sql
ALTER TABLE users ADD CONSTRAINT users_email_format_check
    CHECK (email ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$');
```

**Password Hash Format (Argon2)**

```sql
ALTER TABLE users ADD CONSTRAINT users_password_hash_format_check
    CHECK (password LIKE 'argon2%');
```

**Token Expiry Must Be in Future**

```sql
ALTER TABLE session_tokens ADD CONSTRAINT session_expires_after_created_check
    CHECK (expires_at > created_at);
```

**Email Verification Timestamp Consistency**

```sql
ALTER TABLE users ADD CONSTRAINT users_email_verified_timestamp_check
    CHECK (email_verified = FALSE OR email_verified_at IS NOT NULL);
```

**TOTP Device Unique Constraint (user, name)**

```python
models.UniqueConstraint(fields=['user', 'name'], name='totp_user_name_unique')
```

---

## 6. Query Performance Considerations

### Hot-Path Queries

**Query 1: User Login (50+ req/sec expected)**

```python
User.objects.filter(organisation=org, email=email).select_related('organisation').first()
```

**Optimisation**: Composite index on `(organisation, email)` with INCLUDE `(id, password, is_active, email_verified, two_factor_enabled)`
**Expected**: 10-100x performance improvement

**Query 2: Session Token Validation (100+ req/sec expected)**

```python
SessionToken.objects.filter(
    token_hash=token,
    expires_at__gt=now
).select_related('user').first()
```

**Optimisation**: Composite index on `(token_hash, expires_at)` with partial index `WHERE expires_at > NOW()`
**Expected**: 5-50x performance improvement

**Query 3: Organisation User Listing (10+ req/sec expected)**

```python
User.objects.filter(
    organisation=org,
    is_active=True
).order_by('-created_at')[:20]
```

**Optimisation**: Composite index on `(organisation, is_active, created_at)` with INCLUDE columns
**Expected**: 10-50x performance improvement

**Query 4: Audit Log Range Query (5+ req/sec expected)**

```python
AuditLog.objects.filter(
    organisation=org,
    action='login_success',
    created_at__gte=start_date
).order_by('-created_at')
```

**Optimisation**: Composite index on `(organisation, action, created_at)`
**Expected**: 5-50x performance improvement

### N+1 Query Prevention

**ALL GraphQL resolvers MUST use `select_related()` and `prefetch_related()`**

```python
# Bad (N+1 query):
@strawberry.field
def users(self, info: Info) -> List[User]:
    return User.objects.filter(organisation=info.context.user.organisation)

# Good (single query):
@strawberry.field
def users(self, info: Info) -> List[User]:
    return User.objects.filter(
        organisation=info.context.user.organisation
    ).select_related('organisation', 'profile').prefetch_related('totp_devices')
```

### Query Optimisation Patterns

**For Large Result Sets**

```python
# Use iterator() to stream results instead of loading all into memory
for user in User.objects.iterator(chunk_size=1000):
    process_user(user)
```

**For Limited Columns**

```python
# Use only() to fetch only needed columns
users = User.objects.only('id', 'email', 'first_name')
```

**For Cached Results**

```python
# Implement query result caching for expensive operations
cache_key = f'org_stats:{organisation_id}'
stats = cache.get(cache_key)
if stats is None:
    stats = User.objects.filter(organisation_id=organisation_id).aggregate(
        total_users=Count('id'),
        active_users=Count('id', filter=Q(is_active=True))
    )
    cache.set(cache_key, stats, timeout=300)
```

---

## 7. Multi-Tenancy and Isolation

### Current Isolation Pattern ✅

**Row-level tenancy via organisation foreign keys**

- Every user belongs to an organisation (tenant)
- All queries enforce organisation boundaries
- Foreign key constraints prevent cross-organisation relationships

### Critical: Implement Row-Level Security (RLS) 🔴

PostgreSQL Row-Level Security provides database-level enforcement of multi-tenancy:

```sql
-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see users in their organisation
CREATE POLICY users_organisation_isolation ON users
    FOR ALL
    USING (
        organisation_id = current_setting('app.current_organisation_id')::uuid
        OR current_setting('app.is_superuser')::boolean = true
    );
```

**Benefits:**

- Database-level enforcement of multi-tenancy boundaries
- Protection against SQL injection and misconfigured queries
- Prevents accidental cross-organisation data leaks

**Implementation**: Add Django middleware to set PostgreSQL session variables

```python
class OrganisationMiddleware:
    def __call__(self, request):
        if request.user.is_authenticated and request.user.organisation:
            with connection.cursor() as cursor:
                cursor.execute(
                    "SET app.current_organisation_id = %s",
                    [str(request.user.organisation.id)]
                )
        response = self.get_response(request)
        return response
```

---

## 8. Migration Strategy

### Approach

**Phase-Based Implementation with Zero-Downtime Deployment**

**Phase 1: Core Tables**

- Create Organisation, User, UserProfile models
- Run migrations: `./scripts/env/dev.sh makemigrations core`

**Phase 2: Authentication Tables**

- Create SessionToken, PasswordResetToken, EmailVerificationToken
- Create TOTPDevice model

**Phase 3: Security and Audit**

- Create AuditLog model
- Test immutability in admin interface

**Phase 4: Performance Optimisation**

- Add indexes using `CREATE INDEX CONCURRENTLY` (no table locks)
- Add CHECK constraints using `NOT VALID` + `VALIDATE` pattern
- Add Row-Level Security policies

### Zero-Downtime Index Creation

```python
class Migration(migrations.Migration):
    atomic = False  # Required for CONCURRENTLY

    operations = [
        migrations.RunSQL(
            sql="""
            CREATE INDEX CONCURRENTLY IF NOT EXISTS users_org_email_idx
            ON users (organisation_id, email);
            """,
            reverse_sql="DROP INDEX CONCURRENTLY IF EXISTS users_org_email_idx;",
        ),
    ]
```

### Zero-Downtime Constraint Addition

```python
# Step 1: Add constraint without validating existing rows (fast)
migrations.RunSQL(
    sql="""
    ALTER TABLE users
    ADD CONSTRAINT users_email_format_check
    CHECK (email ~ '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    NOT VALID;
    """
),
# Step 2: Validate constraint in background (can run during traffic)
migrations.RunSQL(
    sql="ALTER TABLE users VALIDATE CONSTRAINT users_email_format_check;"
),
```

---

## 9. Scalability and Performance Targets

### Expected Load (Production)

| Metric                     | Target        | Scaling Trigger |
| -------------------------- | ------------- | --------------- |
| Concurrent users           | 10,000        | 5,000 users     |
| Login requests/sec         | 50            | 30 req/sec      |
| Session validation req/sec | 100           | 60 req/sec      |
| GraphQL queries/sec        | 200           | 120 req/sec     |
| Database size (1 year)     | 100GB         | 50GB            |
| Audit log rows             | 36M+ (1 year) | 10M rows        |

### Scaling Strategy

**Stage 1: Single PostgreSQL Instance (0-10K users)**

- PostgreSQL 18 on AWS RDS or Digital Ocean
- Instance: db.t3.medium (2 vCPU, 4GB RAM)
- Storage: 100GB SSD with auto-scaling

**Stage 2: Primary with Read Replicas (10K-50K users)**

- Primary: db.m5.large
- Read replicas: 2x db.m5.large
- Connection pooling: PgBouncer

**Stage 3: Multi-Region (50K+ users)**

- Primary: db.m5.xlarge
- Read replicas: 3x db.m5.xlarge (multi-region)
- Redis caching layer
- Aurora PostgreSQL for automatic failover

### Connection Pooling (CRITICAL for Production)

**PgBouncer Configuration**

```ini
[databases]
backend_template = host=db.example.com dbname=backend_template

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 25
reserve_pool_size = 5
```

**Django Configuration**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': env('PGBOUNCER_HOST'),  # PgBouncer, not direct DB
        'PORT': env('PGBOUNCER_PORT', default='6432'),
        'CONN_MAX_AGE': 0,  # Disable persistent connections
    },
}
```

---

## 10. Security Review

### Encryption Strategy ✅

| Field                   | Encryption Method | Storage Type | Assessment    |
| ----------------------- | ----------------- | ------------ | ------------- |
| User.password           | Argon2id          | CharField    | ✓ Excellent   |
| User.last_login_ip      | Fernet            | BinaryField  | ✓ Good        |
| AuditLog.ip_address     | Fernet            | BinaryField  | ✓ Good        |
| SessionToken.ip_address | Fernet            | BinaryField  | ✓ Good        |
| TOTPDevice.secret       | Fernet (\*)       | BinaryField  | ⚠️ Clarify    |
| UserProfile.phone       | None              | CharField    | ✗ Encrypt PII |

**Recommendations:**

- Encrypt UserProfile.phone field
- Clarify TOTPDevice.secret encryption method
- Consider PostgreSQL's native encryption in Phase 2

### GDPR Compliance

**Strengths:**

- Audit logs preserve user deletion (SET_NULL on user FK)
- IP addresses encrypted (PII protection)
- Timestamps for compliance reporting

**Issues to Fix:**

- Change AuditLog.organisation to SET_NULL (prevents audit log deletion)
- Add soft delete pattern for organisations

---

## 11. PostgreSQL-Specific Optimisations

### Extensions to Enable

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";     -- UUID generation
CREATE EXTENSION IF NOT EXISTS "btree_gin";     -- GIN indexes with B-tree
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements"; -- Query monitoring
```

### Advanced Index Types

**GIN Index for JSON Metadata**

```sql
CREATE INDEX audit_logs_metadata_gin_idx
ON audit_logs USING gin (metadata jsonb_path_ops);
```

**Partial Index for Recent Logs**

```sql
CREATE INDEX audit_logs_recent_idx
ON audit_logs (created_at DESC)
WHERE created_at > NOW() - INTERVAL '90 days';
```

**BRIN Index for Time-Series Data**

```sql
CREATE INDEX audit_logs_created_at_brin_idx
ON audit_logs USING BRIN (created_at);
```

---

## Critical Recommendations Summary

### 🔴 Critical (Implement Before Production)

1. **Fix AuditLog.organisation CASCADE to SET_NULL** - Prevents data loss
2. **Make User.organisation nullable** - Allows platform superusers
3. **Add composite indexes** for multi-tenant queries - Performance critical
4. **Add indexes on expires_at** - Prevents token cleanup full table scans
5. **Add database-level CHECK constraints** - Data integrity

### 🟠 High Priority (Implement During Phase 1)

1. **Implement Row-Level Security (RLS)** - Database-level multi-tenancy
2. **Add unique constraint (user, name) for TOTPDevice** - Data quality
3. **Fix token hash field sizes** (255 → 64 for SHA-256)
4. **Add organisation deletion safeguards** - Prevent accidental deletion

### 🟡 Medium Priority (Phase 2)

1. **Add covering indexes** - Query optimisation (20-50% improvement)
2. **Add partial indexes** - Smaller, faster indexes
3. **Implement query result caching** - Redis layer
4. **Database connection pooling** - PgBouncer

### 🟢 Low Priority (Phase 3+)

1. **Audit log partitioning** - When table exceeds 10M rows
2. **UUID v7 migration** - Better index locality
3. **PostgreSQL 18 encrypted columns** - Simplify encryption logic

---

## Implementation Roadmap

### Sprint 1: Critical Fixes (Week 1-2)

```python
# Migration 0001: Fix foreign key cascading
- Change AuditLog.organisation to SET_NULL
- Make User.organisation nullable with validation
- Add db_index=True to foreign keys

# Migration 0002: Add critical indexes
- Composite indexes for User (organisation, email)
- Composite indexes for User (organisation, is_active, created_at)
- Indexes on all token expires_at fields
- Composite indexes for AuditLog filtering

# Migration 0003: Add data integrity constraints
- CHECK constraint for email format
- CHECK constraint for password hash format
- CHECK constraint for token expiry
- UNIQUE constraint for TOTP (user, name)
```

### Sprint 2: Performance Optimisation (Week 3-4)

```python
# Migration 0004: Add covering indexes
- Users login covering index
- Session validation covering index
- Audit log query covering index

# Migration 0005: Add partial indexes
- Active users partial index
- Unexpired sessions partial index
- Recent audit logs partial index

# Migration 0006: Row-Level Security
- Enable RLS on all multi-tenant tables
- Create organisation isolation policies
```

### Sprint 3: Scaling Foundation (Week 5-6)

```python
# Implementation:
- PgBouncer connection pooling setup
- Read replica configuration
- Redis caching layer
- Query monitoring setup (pg_stat_statements)
```

---

## Conclusion

The User Authentication System database design is **well-architected and ready for implementation** with the recommended critical improvements. The foundation is solid, but addressing the issues outlined above is essential for production deployment.

### Key Takeaways

✅ **Excellent Design Elements:**

- Proper normalisation and data separation
- Security-first approach with encryption
- Multi-tenancy architectural pattern
- Comprehensive audit logging
- Abstract base classes for DRY principle

⚠️ **Critical Issues to Fix:**

- Foreign key cascading (AuditLog.organisation)
- User.organisation nullability
- Missing indexes for performance
- Missing database constraints

📈 **Expected Performance Gains:**

- 10-100x improvement in user login queries
- 5-50x improvement in audit log queries
- Elimination of full table scans for token cleanup
- 20-50% reduction in hot-path query times

🔒 **Security Enhancements:**

- Row-Level Security for database-level enforcement
- Enhanced data integrity constraints
- Encrypted storage for all PII

### Approval Status

**Status**: ✅ **APPROVED FOR IMPLEMENTATION** with Critical Recommendations

**Conditions:**

1. Apply critical fixes from Sprint 1 before production launch
2. Implement high-priority recommendations during Phase 1
3. Plan medium-priority optimisations for Phase 2
4. Monitor performance metrics and adjust as needed

---

**Document Status**: Complete
**Review Date**: 07/01/2026
**Next Review**: After Phase 1 implementation
**Approved By**: Database Architecture Team
**Maintained By**: DBA Agent, Database Specialists
