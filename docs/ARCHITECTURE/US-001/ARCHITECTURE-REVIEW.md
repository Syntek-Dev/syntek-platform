# User Authentication Architecture Review

**Review Date**: 07/01/2026
**Plan Version**: 1.1.0
**Reviewer**: System Architect
**Review Type**: Architecture and Technical Design Review
**User Story**: US-001
**Plan Document**: docs/PLANS/US-001-USER-AUTHENTICATION.md

---

## Table of Contents

- [User Authentication Architecture Review](#user-authentication-architecture-review)
  - [Table of Contents](#table-of-contents)
  - [Executive Summary](#executive-summary)
  - [Review Scope](#review-scope)
  - [Architecture Areas Reviewed](#architecture-areas-reviewed)
    - [1. Overall System Architecture](#1-overall-system-architecture)
    - [2. Authentication Flow Design](#2-authentication-flow-design)
    - [3. Multi-Tenancy Approach](#3-multi-tenancy-approach)
    - [4. Session/Token Strategy](#4-sessiontoken-strategy)
    - [5. Extensibility Patterns (OneToOne for Roles)](#5-extensibility-patterns-onetoone-for-roles)
    - [6. Permission System Design](#6-permission-system-design)
    - [7. Scalability Architecture](#7-scalability-architecture)
    - [8. Service Layer Boundaries](#8-service-layer-boundaries)
    - [9. Integration Points with Other Phases](#9-integration-points-with-other-phases)
    - [10. Technical Debt Considerations](#10-technical-debt-considerations)
  - [Architecture Diagrams and Suggestions](#architecture-diagrams-and-suggestions)
    - [System Context Diagram](#system-context-diagram)
    - [Authentication Flow Diagram](#authentication-flow-diagram)
    - [Multi-Tenancy Data Model](#multi-tenancy-data-model)
    - [Service Layer Architecture](#service-layer-architecture)
  - [Critical Recommendations](#critical-recommendations)
    - [High Priority (Address Before Implementation)](#high-priority-address-before-implementation)
    - [Medium Priority (Address During Implementation)](#medium-priority-address-during-implementation)
    - [Low Priority (Address in Future Phases)](#low-priority-address-in-future-phases)
  - [Risk Assessment](#risk-assessment)
  - [Overall Assessment](#overall-assessment)
  - [Approval Status](#approval-status)

---

## Executive Summary

This architectural review evaluates the technical design for the User Authentication system (US-001).
The plan demonstrates a solid foundation with enterprise-grade security considerations, appropriate
multi-tenancy patterns, and good extensibility for future phases.

**Overall Rating**: ✅ **Good** (8.5/10)

**Strengths:**

- Comprehensive security approach with IP encryption, Argon2 hashing, and 2FA
- Well-designed multi-tenancy with organisation boundaries
- Excellent extensibility pattern using OneToOne relationships
- Proper separation of concerns with service layer architecture
- Thorough testing strategy with TDD, BDD, and E2E approaches
- Good integration planning with future phases

**Areas for Improvement:**

- Token storage strategy needs clarification on Redis vs Database trade-offs
- Missing GraphQL query complexity and depth limiting implementation details
- Rate limiting implementation needs more architectural detail
- Service layer could benefit from more explicit dependency injection patterns
- Missing discussion of horizontal scaling strategies for stateful components

**Recommendation**: Proceed with implementation with specific improvements outlined in this review.

---

## Review Scope

This review covers the following aspects of the User Authentication architecture:

1. Overall system architecture and component design
2. Authentication flow patterns and security measures
3. Multi-tenancy implementation and data isolation
4. Session management and token strategy
5. Extensibility patterns for future role models
6. Permission system and RBAC design
7. Scalability and performance architecture
8. Service layer boundaries and responsibilities
9. Integration points with other platform phases
10. Potential technical debt and mitigation strategies

---

## Architecture Areas Reviewed

### 1. Overall System Architecture

**Rating**: ✅ **Good**

**Analysis:**

The plan follows a layered architecture with clear separation between data, business logic, and API
layers:

```
┌─────────────────────────────────────────┐
│         GraphQL API Layer               │
│   (Strawberry, Queries, Mutations)      │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│        Service Layer                    │
│  (AuthService, TokenService, etc.)      │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│        Data Layer                       │
│  (Django Models, Custom Manager)        │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│    Infrastructure Layer                 │
│  (PostgreSQL, Redis, Email)             │
└─────────────────────────────────────────┘
```

**Strengths:**

- Clear separation of concerns between layers
- Service layer provides good abstraction over Django ORM
- GraphQL API provides type-safe, versioned interface
- Infrastructure dependencies properly abstracted

**Weaknesses:**

- Missing explicit dependency injection patterns
- No discussion of how services will be instantiated/managed
- Circular dependency risks between services not addressed
- Missing API versioning strategy for GraphQL schema evolution

**Recommendations:**

1. **Add Dependency Injection Container** - Consider using `django-injector` or `dependency-injector`
   to manage service instantiation and dependencies.

2. **Define Service Lifecycle** - Document whether services are singletons, request-scoped, or
   stateless utilities.

3. **Add GraphQL Schema Versioning** - Plan for schema evolution using deprecation decorators and
   field versioning.

```python
# Suggested dependency injection approach
from dependency_injector import containers, providers

class ServiceContainer(containers.DeclarativeContainer):
    """Container for service dependencies."""

    # Infrastructure
    redis_client = providers.Singleton(RedisClient)

    # Services
    token_service = providers.Factory(
        TokenService,
        redis_client=redis_client
    )

    auth_service = providers.Factory(
        AuthService,
        token_service=token_service
    )
```

---

### 2. Authentication Flow Design

**Rating**: ✅ **Good**

**Analysis:**

The authentication flows are well-designed with clear state transitions and security checkpoints.
The plan covers registration, login (with/without 2FA), password reset, and email verification
flows comprehensively.

**Strengths:**

- Clear flow diagrams for each authentication scenario
- Proper handling of 2FA as optional additional step
- Email verification separate from login (allows graceful degradation)
- Audit logging integrated into all flows
- Token expiration and refresh handled correctly

**Weaknesses:**

- Missing account lockout mechanism after multiple failed login attempts
- No discussion of CAPTCHA integration for preventing automated attacks
- Concurrent login handling not specified (can user login from multiple devices?)
- Missing "magic link" authentication option (passwordless flow)
- No mention of session invalidation on password change

**Recommendations:**

1. **Add Account Lockout Policy** - After 5 failed login attempts, temporarily lock account for
   15 minutes.

```python
# apps/core/services/auth_service.py

def check_account_lockout(self, user: User) -> bool:
    """Check if account is locked due to failed login attempts.

    Args:
        user: User to check

    Returns:
        True if account is locked, False otherwise
    """
    failed_attempts = AuditLog.objects.filter(
        user=user,
        action='login_failed',
        created_at__gte=timezone.now() - timedelta(minutes=15)
    ).count()

    if failed_attempts >= 5:
        return True
    return False
```

2. **Invalidate Sessions on Password Change** - When user changes password, revoke all existing
   sessions except current one.

3. **Add Concurrent Session Management** - Allow maximum 5 concurrent sessions, revoke oldest when
   limit exceeded.

4. **Consider CAPTCHA Integration** - Add CAPTCHA after 3 failed login attempts to prevent brute
   force attacks.

---

### 3. Multi-Tenancy Approach

**Rating**: ✅ **Good**

**Analysis:**

The multi-tenancy design uses organisation-based isolation with foreign key relationships. This is
a solid approach for logical data separation.

**Strengths:**

- Organisation foreign key on User model enforces tenancy
- GraphQL resolvers enforce organisation boundaries at query level
- Audit logs scoped to organisations
- Clear organisation ownership model

**Weaknesses:**

- No database-level row security policies (PostgreSQL RLS)
- Missing middleware to automatically filter queries by organisation
- No discussion of organisation switching for multi-org users (future)
- Superuser bypass behaviour needs clearer specification
- Missing organisation soft-delete strategy

**Recommendations:**

1. **Add PostgreSQL Row-Level Security (RLS)** - Provide defence-in-depth for multi-tenancy:

```sql
-- Enable RLS on users table
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policy to enforce organisation boundaries
CREATE POLICY user_organisation_isolation ON users
    USING (organisation_id = current_setting('app.current_organisation_id')::uuid)
    WITH CHECK (organisation_id = current_setting('app.current_organisation_id')::uuid);
```

2. **Create Organisation Context Middleware** - Automatically set organisation context from
   authenticated user:

```python
# apps/core/middleware/organisation_context.py

class OrganisationContextMiddleware:
    """Middleware to set organisation context for request."""

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            # Set organisation context for RLS
            with connection.cursor() as cursor:
                cursor.execute(
                    "SET LOCAL app.current_organisation_id = %s",
                    [str(request.user.organisation_id)]
                )

        response = self.get_response(request)
        return response
```

3. **Define Superuser Organisation Access Policy** - Document clear rules:
   - Superusers can access all organisations
   - Superusers must explicitly switch organisation context
   - All superuser actions logged with organisation context

---

### 4. Session/Token Strategy

**Rating**: ⚠️ **Needs Improvement**

**Analysis:**

The token strategy combines JWT tokens with database storage and Redis caching. While this provides
good flexibility, there are some architectural concerns about consistency and performance.

**Strengths:**

- JWT provides stateless authentication capability
- Database storage allows token revocation
- Redis caching improves performance
- Token rotation on refresh is secure

**Weaknesses:**

- Dual storage (Database + Redis) creates synchronisation challenges
- No clear strategy for Redis cache invalidation on token revocation
- Missing discussion of token blacklisting strategy
- JWT claims not specified (what goes in payload?)
- No mention of JWT asymmetric signing for microservices future
- Token expiration strategy (24 hours) not justified with use case

**Recommendations:**

1. **Clarify Token Storage Strategy** - Choose one of the following approaches:

   **Option A: Redis as Primary Store**

   ```python
   # Store token in Redis only, use database for audit trail
   # Pros: Fast lookups, automatic expiration
   # Cons: Data loss if Redis fails (mitigated by persistence)

   class TokenService:
       def create_token(self, user: User) -> str:
           token = jwt.encode(payload, settings.SECRET_KEY)
           redis_client.setex(
               f"token:{token_hash}",
               settings.TOKEN_EXPIRY,
               user.id
           )
           # Log in database for audit only
           SessionToken.objects.create(
               user=user,
               token_hash=token_hash,
               expires_at=expiry
           )
           return token
   ```

   **Option B: Database as Primary, Redis as Cache**

   ```python
   # Store token in database, cache lookups in Redis
   # Pros: Durable, survives Redis failures
   # Cons: Slower, requires cache invalidation logic

   class TokenService:
       def verify_token(self, token: str) -> User:
           # Try cache first
           user_id = redis_client.get(f"token:{token_hash}")
           if user_id:
               return User.objects.get(id=user_id)

           # Fallback to database
           session = SessionToken.objects.get(token_hash=token_hash)
           # Populate cache
           redis_client.setex(
               f"token:{token_hash}",
               ttl,
               session.user_id
           )
           return session.user
   ```

2. **Define JWT Payload Structure**:

```python
payload = {
    'user_id': str(user.id),
    'organisation_id': str(user.organisation_id),
    'email': user.email,
    'exp': datetime.utcnow() + timedelta(hours=24),
    'iat': datetime.utcnow(),
    'jti': str(uuid.uuid4()),  # JWT ID for blacklisting
    'type': 'access',  # vs 'refresh'
}
```

3. **Implement Token Blacklist** - For revoked tokens before expiry:

```python
# apps/core/services/token_service.py

def revoke_token(self, token: str) -> None:
    """Revoke a token before expiry."""
    decoded = jwt.decode(token, settings.SECRET_KEY)
    ttl = decoded['exp'] - time.time()

    # Add to blacklist in Redis
    redis_client.setex(
        f"blacklist:{decoded['jti']}",
        int(ttl),
        '1'
    )

    # Mark as revoked in database
    SessionToken.objects.filter(
        token_hash=hashlib.sha256(token.encode()).hexdigest()
    ).update(revoked=True)
```

4. **Plan for Asymmetric JWT Signing** - For future microservices architecture:

```python
# Generate RS256 key pair for JWT signing
# Private key: Signs tokens (backend only)
# Public key: Verifies tokens (can be shared with microservices)

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
public_key = private_key.public_key()

# In settings:
JWT_ALGORITHM = 'RS256'
JWT_PRIVATE_KEY = private_key
JWT_PUBLIC_KEY = public_key
```

---

### 5. Extensibility Patterns (OneToOne for Roles)

**Rating**: ✅ **Good**

**Analysis:**

The OneToOne relationship pattern for role-specific profiles is an excellent architectural decision.
This provides flexibility for future role models without modifying the core User model.

**Strengths:**

- Clean separation between core authentication and role-specific data
- Allows users to have multiple roles simultaneously
- No multi-table inheritance complexity
- Easy to add/remove role profiles
- GraphQL schema naturally supports optional role profiles

**Weaknesses:**

- No discussion of role profile lifecycle management
- Missing migration strategy for converting users to new roles
- No mention of role profile validation (e.g., can user be both Customer and Seller?)
- Lazy loading vs eager loading of profiles not addressed

**Recommendations:**

1. **Add Role Profile Manager** - Centralise role assignment logic:

```python
# apps/core/services/role_service.py

class RoleService:
    """Service for managing user role profiles."""

    @staticmethod
    def assign_customer_role(user: User, initial_data: dict = None) -> Customer:
        """Assign customer role to user.

        Args:
            user: User to assign role to
            initial_data: Initial customer profile data

        Returns:
            Created or existing Customer profile
        """
        customer, created = Customer.objects.get_or_create(
            user=user,
            defaults=initial_data or {}
        )

        # Assign to Customer group
        customer_group = Group.objects.get(name="Customer")
        user.groups.add(customer_group)

        # Audit log
        AuditService.log_event(
            action='role_assigned',
            user=user,
            metadata={'role': 'customer'}
        )

        return customer

    @staticmethod
    def get_user_roles(user: User) -> List[str]:
        """Get all roles assigned to user.

        Args:
            user: User to check

        Returns:
            List of role names (e.g., ['customer', 'seller'])
        """
        roles = []
        if hasattr(user, 'customer_profile'):
            roles.append('customer')
        if hasattr(user, 'seller_profile'):
            roles.append('seller')
        if hasattr(user, 'author_profile'):
            roles.append('author')
        return roles
```

2. **Optimise GraphQL Queries with Prefetch** - Avoid N+1 queries:

```python
# api/queries/user.py

@strawberry.field
def users(self, info: Info) -> List[User]:
    """Get users with role profiles prefetched."""
    return User.objects.filter(
        organisation=info.context.user.organisation
    ).prefetch_related(
        'customer_profile',
        'seller_profile',
        'author_profile'
    )
```

3. **Add Role Validation Rules** - Define which role combinations are allowed:

```python
# apps/core/validators.py

class RoleValidator:
    """Validator for role assignment rules."""

    INCOMPATIBLE_ROLES = {
        ('customer', 'admin'),  # Customers cannot be admins
    }

    @classmethod
    def validate_role_assignment(cls, user: User, new_role: str) -> None:
        """Validate if role can be assigned to user.

        Args:
            user: User to validate
            new_role: Role to assign

        Raises:
            ValidationError: If role assignment is invalid
        """
        current_roles = RoleService.get_user_roles(user)

        for existing_role in current_roles:
            if (existing_role, new_role) in cls.INCOMPATIBLE_ROLES:
                raise ValidationError(
                    f"Cannot assign {new_role} role to user with {existing_role} role"
                )
```

---

### 6. Permission System Design

**Rating**: ✅ **Good**

**Analysis:**

The permission system leverages Django's built-in Groups and permissions framework, which is a
battle-tested approach. The three-tier hierarchy (Platform → Organisation → Website) is well-suited
for the CMS platform.

**Strengths:**

- Uses Django's proven permission system
- Clear hierarchy with three levels
- Good examples of custom permissions
- Permission checking examples for GraphQL resolvers
- Strawberry permission classes for declarative access control

**Weaknesses:**

- Missing object-level permissions (e.g., "can edit THIS page")
- No discussion of permission caching strategy
- Organisation boundary checks separate from permission checks (could be unified)
- Missing permission inheritance rules between levels
- No mention of permission auditing

**Recommendations:**

1. **Add Object-Level Permissions** - Use `django-guardian` for granular permissions:

```python
# Install django-guardian
# pip install django-guardian

from guardian.shortcuts import assign_perm, get_objects_for_user

# Assign permission to specific object
assign_perm('cms.change_page', user, page_obj)

# Query objects user has permission for
pages = get_objects_for_user(
    user,
    'cms.change_page',
    klass=Page,
    accept_global_perms=True
)
```

2. **Implement Permission Caching** - Cache permission checks in Redis:

```python
# apps/core/services/permission_service.py

class PermissionService:
    """Service for checking permissions with caching."""

    @staticmethod
    def has_permission(user: User, permission: str, obj=None) -> bool:
        """Check if user has permission (with caching).

        Args:
            user: User to check
            permission: Permission string (e.g., 'cms.change_page')
            obj: Optional object for object-level permissions

        Returns:
            True if user has permission, False otherwise
        """
        cache_key = f"perm:{user.id}:{permission}"
        if obj:
            cache_key += f":{obj.pk}"

        # Check cache
        cached = redis_client.get(cache_key)
        if cached is not None:
            return cached == '1'

        # Check permission
        if obj:
            has_perm = user.has_perm(permission, obj)
        else:
            has_perm = user.has_perm(permission)

        # Cache for 5 minutes
        redis_client.setex(cache_key, 300, '1' if has_perm else '0')

        return has_perm
```

3. **Unify Organisation Boundary and Permission Checks** - Create decorator:

```python
# api/decorators.py

def require_organisation_permission(permission: str):
    """Decorator to check permission and organisation boundary.

    Args:
        permission: Django permission to check

    Returns:
        Decorator function
    """
    def decorator(resolver):
        @wraps(resolver)
        def wrapper(root, info: Info, **kwargs):
            user = info.context.request.user

            # Check authentication
            if not user.is_authenticated:
                raise PermissionError("Authentication required")

            # Check permission
            if not user.has_perm(permission):
                raise PermissionError(f"Permission denied: {permission}")

            # Check organisation boundary if object has organisation
            obj_id = kwargs.get('id') or kwargs.get('page_id')
            if obj_id:
                # Resolver will verify organisation boundary
                pass

            return resolver(root, info, **kwargs)

        return wrapper
    return decorator

# Usage:
@require_organisation_permission('cms.publish_page')
@strawberry.mutation
def publish_page(self, info: Info, page_id: strawberry.ID) -> Page:
    """Publish a page."""
    # Permission and auth already checked by decorator
    pass
```

---

### 7. Scalability Architecture

**Rating**: ⚠️ **Needs Improvement**

**Analysis:**

The plan mentions scalability requirements (10,000+ users per organisation, horizontal scaling via
Redis) but lacks architectural detail on how this will be achieved.

**Strengths:**

- Redis used for session storage enables horizontal scaling
- Database indexing strategy defined
- Performance requirements specified (< 200ms response times)
- Query optimisation mentioned (select_related, prefetch_related)

**Weaknesses:**

- No discussion of database connection pooling
- Missing Celery/background task architecture for async operations
- No mention of API rate limiting at infrastructure level
- GraphQL query complexity analysis not implemented
- Missing caching strategy beyond sessions (query results, user objects)
- No discussion of database read replicas
- WebSocket scaling not addressed (for future real-time features)

**Recommendations:**

1. **Add Database Connection Pooling** - Use PgBouncer for connection management:

```yaml
# docker/production/docker-compose.yml

pgbouncer:
  image: pgbouncer/pgbouncer:latest
  environment:
    DATABASES_HOST: postgres
    DATABASES_PORT: 5432
    DATABASES_DBNAME: backend_template
    PGBOUNCER_POOL_MODE: transaction
    PGBOUNCER_MAX_CLIENT_CONN: 1000
    PGBOUNCER_DEFAULT_POOL_SIZE: 25
```

2. **Implement GraphQL Query Complexity Analysis**:

```python
# api/complexity.py

from strawberry.extensions import QueryDepthLimiter, ParserCache

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        QueryDepthLimiter(max_depth=10),
        ParserCache(maxsize=100),
    ]
)

# Add custom complexity calculator
from strawberry.extensions import Extension

class QueryComplexityLimiter(Extension):
    """Limit query complexity based on field weights."""

    def on_execute(self):
        complexity = self.calculate_complexity()
        if complexity > 1000:
            raise GraphQLError(
                f"Query too complex: {complexity}. Maximum allowed: 1000"
            )

    def calculate_complexity(self):
        # Calculate based on field types and depth
        # Lists have higher cost than scalar fields
        pass
```

3. **Add Celery for Background Tasks**:

```python
# config/celery.py

from celery import Celery

app = Celery('backend_template')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# apps/core/tasks.py

@app.task
def send_verification_email(user_id: uuid.UUID):
    """Send email verification email asynchronously."""
    user = User.objects.get(id=user_id)
    EmailService.send_verification_email(user)

# Usage in AuthService:
def register_user(self, email: str, password: str, **kwargs):
    user = User.objects.create_user(email=email, password=password, **kwargs)
    send_verification_email.delay(user.id)  # Async
    return user
```

4. **Implement Multi-Layer Caching Strategy**:

```python
# apps/core/cache.py

from django.core.cache import cache
from functools import wraps

def cache_user(timeout=300):
    """Decorator to cache user objects.

    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(user_id, *args, **kwargs):
            cache_key = f"user:{user_id}"
            user = cache.get(cache_key)

            if user is None:
                user = func(user_id, *args, **kwargs)
                cache.set(cache_key, user, timeout)

            return user
        return wrapper
    return decorator

@cache_user()
def get_user_by_id(user_id: uuid.UUID) -> User:
    """Get user by ID with caching."""
    return User.objects.select_related('organisation', 'profile').get(id=user_id)
```

5. **Plan for Database Read Replicas**:

```python
# config/settings/production.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'postgres-primary.rds.amazonaws.com',
        # ... other settings
    },
    'read_replica': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'postgres-replica.rds.amazonaws.com',
        # ... other settings
    }
}

# Use read replica for queries
class ReadReplicaRouter:
    """Router to use read replica for read operations."""

    def db_for_read(self, model, **hints):
        """Send reads to replica."""
        return 'read_replica'

    def db_for_write(self, model, **hints):
        """Send writes to primary."""
        return 'default'
```

---

### 8. Service Layer Boundaries

**Rating**: ✅ **Good**

**Analysis:**

The service layer design provides good separation between business logic and data access. Each
service has a clear responsibility.

**Strengths:**

- Clear service responsibilities (AuthService, TokenService, AuditService, etc.)
- Services encapsulate business logic away from models
- Services provide testable units
- Service methods have clear input/output contracts

**Weaknesses:**

- No discussion of transaction management across services
- Missing error handling strategy (where do exceptions get caught?)
- Service interdependencies not mapped
- No mention of service interfaces/protocols for dependency injection
- Missing validation layer (where does input validation happen?)

**Recommendations:**

1. **Define Service Transaction Boundaries**:

```python
# apps/core/services/auth_service.py

from django.db import transaction

class AuthService:
    """Service for authentication operations."""

    @transaction.atomic
    def register_user(
        self,
        email: str,
        password: str,
        organisation: Organisation,
        **kwargs
    ) -> User:
        """Register a new user (transactional).

        All operations (create user, create profile, send email) happen
        in a single transaction. If any step fails, everything rolls back.

        Args:
            email: User email
            password: User password
            organisation: Organisation to join
            **kwargs: Additional user fields

        Returns:
            Created User instance

        Raises:
            ValidationError: If user data is invalid
            IntegrityError: If email already exists
        """
        # Validate input
        self._validate_registration_data(email, password, organisation)

        # Create user
        user = User.objects.create_user(
            email=email,
            password=password,
            organisation=organisation,
            **kwargs
        )

        # Create profile
        UserProfile.objects.create(user=user)

        # Create verification token
        token = EmailVerificationToken.objects.create(
            user=user,
            token=self._generate_token(),
            expires_at=timezone.now() + timedelta(days=1)
        )

        # Send email (use select_for_update to prevent race conditions)
        EmailService.send_verification_email(user, token)

        # Log audit event
        AuditService.log_event('register', user, request=None)

        return user
```

2. **Implement Service Error Handling Strategy**:

```python
# apps/core/exceptions.py

class ServiceException(Exception):
    """Base exception for service layer errors."""
    pass

class AuthenticationError(ServiceException):
    """Raised when authentication fails."""
    pass

class PermissionDeniedError(ServiceException):
    """Raised when user lacks permission."""
    pass

class RateLimitExceededError(ServiceException):
    """Raised when rate limit is exceeded."""
    pass

# In GraphQL resolvers, convert service exceptions to GraphQL errors
from strawberry.types import Info
import strawberry

@strawberry.type
class Mutation:
    @strawberry.mutation
    def login(self, info: Info, input: LoginInput) -> AuthPayload:
        try:
            return AuthService.login(input.email, input.password)
        except AuthenticationError as e:
            raise GraphQLError(str(e), extensions={"code": "AUTHENTICATION_ERROR"})
        except RateLimitExceededError as e:
            raise GraphQLError(str(e), extensions={"code": "RATE_LIMIT_EXCEEDED"})
```

3. **Map Service Dependencies**:

```
AuthService
  ├── depends on: TokenService
  ├── depends on: AuditService
  ├── depends on: EmailService
  └── depends on: RateLimitService

TokenService
  ├── depends on: RedisClient
  └── depends on: AuditService

EmailService
  ├── depends on: SMTPClient
  └── depends on: TemplateEngine

AuditService
  ├── depends on: IPEncryption
  └── no circular dependencies
```

---

### 9. Integration Points with Other Phases

**Rating**: ✅ **Good**

**Analysis:**

The plan demonstrates good awareness of future phases and includes forward-thinking design decisions
(e.g., `has_email_account`, `has_vault_access` fields on User model).

**Strengths:**

- User model includes SaaS product integration flags
- Organisation model designed for future CMS features
- Permission system designed for future website-level permissions
- Role profiles pattern supports future template-specific roles

**Weaknesses:**

- Missing integration points documentation
- No API versioning strategy for breaking changes
- GraphQL schema evolution not addressed
- Missing data migration strategy for adding new features
- No discussion of feature flags for gradual rollout

**Recommendations:**

1. **Document Integration Points**:

```markdown
## Phase Integration Points

### Phase 1 (US-001): User Authentication

**Provides:**

- User model with authentication
- Organisation model for multi-tenancy
- GraphQL API for user management
- Permission system (Groups)

**Consumes:**

- None (foundation phase)

### Phase 2: Design Tokens

**Provides:**

- DesignToken model per organisation
- GraphQL API for design token management

**Consumes from Phase 1:**

- User model (creator, updater)
- Organisation model (design tokens belong to org)
- Permission system (who can edit design tokens)

**Integration Points:**

- User.last_updated_by on DesignToken
- Organisation.design_tokens relationship
- Permission: 'design.change_designtoken'

### Phase 3: CMS Content

**Provides:**

- Page, Block, Media models
- Content branching system

**Consumes from Phase 1:**

- User model (author, publisher)
- Organisation model (pages belong to org)
- Permission system (publish, approve permissions)

**Integration Points:**

- Page.author = ForeignKey(User)
- Page.organisation = ForeignKey(Organisation)
- Permission: 'cms.publish_page', 'cms.approve_page'
```

2. **Implement Feature Flags**:

```python
# apps/core/utils/feature_flags.py

class FeatureFlags:
    """Feature flag management for gradual rollout."""

    @staticmethod
    def is_enabled(flag_name: str, user: User = None, org: Organisation = None) -> bool:
        """Check if feature is enabled.

        Args:
            flag_name: Name of feature flag
            user: Optional user for user-specific flags
            org: Optional organisation for org-specific flags

        Returns:
            True if feature is enabled, False otherwise
        """
        # Check in Redis cache
        cache_key = f"feature:{flag_name}"
        if org:
            cache_key += f":org:{org.id}"
        if user:
            cache_key += f":user:{user.id}"

        cached = redis_client.get(cache_key)
        if cached is not None:
            return cached == '1'

        # Check in database
        enabled = FeatureFlag.objects.filter(
            name=flag_name,
            enabled=True
        ).exists()

        # Cache for 1 minute
        redis_client.setex(cache_key, 60, '1' if enabled else '0')

        return enabled

# Usage in code:
if FeatureFlags.is_enabled('2fa_required', user=user):
    # Require 2FA for this user
    pass
```

3. **Add GraphQL Schema Deprecation Strategy**:

```python
# api/types/user.py

import strawberry
from typing import Optional

@strawberry.type
class User:
    id: strawberry.ID
    email: str
    first_name: str
    last_name: str

    # Deprecated field (will be removed in v2)
    full_name: Optional[str] = strawberry.field(
        deprecation_reason="Use firstName and lastName instead. Will be removed in v2."
    )

    # New field added in v1.1
    display_name: str = strawberry.field(
        description="User's display name (firstName + lastName)"
    )
```

---

### 10. Technical Debt Considerations

**Rating**: ✅ **Good**

**Analysis:**

The plan is generally well-designed with minimal technical debt. However, there are some areas
where shortcuts might accumulate debt over time.

**Identified Technical Debt:**

1. **IP Encryption Key Rotation** - Manual rotation quarterly is technical debt; should be automated.

2. **Dual Token Storage** - Storing tokens in both Redis and Database creates synchronisation debt.

3. **No Soft Delete** - Hard deletes for users/organisations could cause data integrity issues.

4. **GraphQL N+1 Queries** - Without DataLoader, role profiles could cause N+1 query issues.

5. **Email Service Dependency** - Synchronous email sending could block requests.

**Recommendations:**

1. **Implement Automated Key Rotation**:

```python
# apps/core/management/commands/rotate_encryption_keys.py

from django.core.management.base import BaseCommand
from apps.core.utils.encryption import IPEncryption
from cryptography.fernet import Fernet

class Command(BaseCommand):
    """Rotate IP encryption keys and re-encrypt data."""

    def handle(self, *args, **options):
        # Generate new key
        new_key = Fernet.generate_key()

        # Re-encrypt all IP addresses
        audit_logs = AuditLog.objects.all()

        for log in audit_logs.iterator(chunk_size=1000):
            # Decrypt with old key
            old_ip = IPEncryption.decrypt_ip(log.ip_address)

            # Encrypt with new key
            new_encrypted = IPEncryption.encrypt_ip(old_ip, key=new_key)

            # Update
            log.ip_address = new_encrypted
            log.save(update_fields=['ip_address'])

        # Update key in settings
        self.stdout.write("New key: " + new_key.decode())
        self.stdout.write("Update IP_ENCRYPTION_KEY in environment variables")
```

2. **Add Soft Delete Support**:

```python
# apps/core/models/base.py

class SoftDeleteManager(models.Manager):
    """Manager that excludes soft-deleted objects."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class SoftDeleteModel(models.Model):
    """Abstract model with soft delete support."""

    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # Include deleted objects

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        """Soft delete by setting deleted_at."""
        self.deleted_at = timezone.now()
        self.save(update_fields=['deleted_at'])

    def hard_delete(self):
        """Permanently delete from database."""
        super().delete()

# Usage:
class User(AbstractBaseUser, SoftDeleteModel):
    """User model with soft delete."""
    pass
```

3. **Implement GraphQL DataLoader**:

```python
# api/dataloaders.py

from strawberry.dataloader import DataLoader
from typing import List
import strawberry

async def load_user_profiles(user_ids: List[int]) -> List[UserProfile]:
    """Batch load user profiles to prevent N+1 queries."""
    profiles = UserProfile.objects.filter(user_id__in=user_ids)

    # Create map of user_id -> profile
    profile_map = {p.user_id: p for p in profiles}

    # Return in same order as user_ids
    return [profile_map.get(uid) for uid in user_ids]

# Usage in context:
@strawberry.type
class User:
    @strawberry.field
    async def profile(self, info: Info) -> Optional[UserProfile]:
        loader = info.context.dataloaders['user_profiles']
        return await loader.load(self.id)
```

---

## Architecture Diagrams and Suggestions

### System Context Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     External Systems                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │  Email   │   │  SMS     │   │  TOTP    │   │  Redis   │    │
│  │  (SMTP)  │   │  (Twilio)│   │  Apps    │   │  Cache   │    │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘    │
└───────┬────────────┬────────────────┬──────────────┬───────────┘
        │            │                │              │
        ▼            ▼                ▼              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Backend Template API                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐     │
│  │             GraphQL API (Strawberry)                  │     │
│  ├───────────────────────────────────────────────────────┤     │
│  │  Queries:                  │  Mutations:              │     │
│  │  - me                      │  - register              │     │
│  │  - user(id)                │  - login                 │     │
│  │  - users                   │  - logout                │     │
│  │  - myAuditLogs            │  - refreshToken          │     │
│  │  - organisationAuditLogs   │  - requestPasswordReset  │     │
│  │                            │  - resetPassword         │     │
│  │                            │  - changePassword        │     │
│  │                            │  - verifyEmail           │     │
│  │                            │  - enableTwoFactor       │     │
│  │                            │  - disableTwoFactor      │     │
│  └───────────────────────────────────────────────────────┘     │
│                            ↓                                    │
│  ┌───────────────────────────────────────────────────────┐     │
│  │               Service Layer                           │     │
│  ├───────────────────────────────────────────────────────┤     │
│  │  AuthService    │  TokenService   │  AuditService    │     │
│  │  EmailService   │  TOTPService    │  RateLimitService│     │
│  └───────────────────────────────────────────────────────┘     │
│                            ↓                                    │
│  ┌───────────────────────────────────────────────────────┐     │
│  │               Data Layer (Django ORM)                 │     │
│  ├───────────────────────────────────────────────────────┤     │
│  │  User  │  Organisation  │  UserProfile  │  AuditLog  │     │
│  │  SessionToken  │  PasswordResetToken  │  TOTPDevice │     │
│  └───────────────────────────────────────────────────────┘     │
└───────────────────────────────┬─────────────────────────────────┘
                                ▼
                    ┌───────────────────────┐
                    │    PostgreSQL 18      │
                    │   (Multi-Tenant DB)   │
                    └───────────────────────┘
```

### Authentication Flow Diagram

```
┌──────┐                                                    ┌──────────┐
│Client│                                                    │ Backend  │
└──┬───┘                                                    └────┬─────┘
   │                                                             │
   │  1. POST /graphql (register mutation)                      │
   │  { email, password, firstName, lastName, orgSlug }         │
   │ ─────────────────────────────────────────────────────────> │
   │                                                             │
   │                                      2. Validate input      │
   │                                      3. Hash password       │
   │                                      4. Create User         │
   │                                      5. Create UserProfile  │
   │                                      6. Generate token      │
   │                                      7. Send verify email   │
   │                                      8. Log audit event     │
   │                                                             │
   │  9. Response: { token, refreshToken, user }                │
   │ <───────────────────────────────────────────────────────── │
   │                                                             │
   │  10. Store tokens in localStorage                          │
   │                                                             │
   │  11. POST /graphql (me query)                              │
   │  Authorization: Bearer {token}                             │
   │ ─────────────────────────────────────────────────────────> │
   │                                                             │
   │                                      12. Verify JWT         │
   │                                      13. Check Redis cache  │
   │                                      14. Load user          │
   │                                      15. Check org boundary │
   │                                                             │
   │  16. Response: { user data }                               │
   │ <───────────────────────────────────────────────────────── │
   │                                                             │
   │  17. Click email verification link                         │
   │  GET /verify-email?token={token}                           │
   │ ─────────────────────────────────────────────────────────> │
   │                                                             │
   │                                      18. Validate token     │
   │                                      19. Check expiration   │
   │                                      20. Mark email verified│
   │                                      21. Log audit event    │
   │                                                             │
   │  22. Response: { success: true }                           │
   │ <───────────────────────────────────────────────────────── │
   │                                                             │
```

### Multi-Tenancy Data Model

```
┌────────────────────────────────────────────────────────────────┐
│                        Organisation                            │
├────────────────────────────────────────────────────────────────┤
│  id: UUID (PK)                                                 │
│  name: String                                                  │
│  slug: String (UNIQUE)                                         │
│  industry: String                                              │
│  is_active: Boolean                                            │
│  created_at: DateTime                                          │
│  updated_at: DateTime                                          │
└────────────────┬───────────────────────────────────────────────┘
                 │
                 │ 1:N
                 ▼
┌────────────────────────────────────────────────────────────────┐
│                           User                                 │
├────────────────────────────────────────────────────────────────┤
│  id: UUID (PK)                                                 │
│  email: String (UNIQUE)                                        │
│  password: String (hashed)                                     │
│  first_name: String                                            │
│  last_name: String                                             │
│  organisation_id: UUID (FK) ──────────────────────┐            │
│  is_active: Boolean                               │            │
│  is_staff: Boolean                                │            │
│  email_verified: Boolean                          │            │
│  two_factor_enabled: Boolean                      │            │
│  last_login_ip: Binary (encrypted)                │            │
│  created_at: DateTime                             │            │
│  updated_at: DateTime                             │            │
└───────┬──────────────────┬────────────────────────┼────────────┘
        │                  │                        │
        │ 1:1              │ 1:N                    │ 1:N
        ▼                  ▼                        ▼
┌───────────────┐  ┌──────────────┐   ┌────────────────────────┐
│  UserProfile  │  │ SessionToken │   │     AuditLog           │
├───────────────┤  ├──────────────┤   ├────────────────────────┤
│  user_id (FK) │  │  user_id (FK)│   │  user_id (FK, null)    │
│  phone        │  │  token_hash  │   │  organisation_id (FK)  │
│  avatar       │  │  expires_at  │   │  action: String        │
│  timezone     │  │  ip_address  │   │  ip_address: Binary    │
│  language     │  └──────────────┘   │  user_agent: String    │
│  bio          │                     │  metadata: JSON        │
└───────────────┘                     │  created_at: DateTime  │
                                      └────────────────────────┘

Organisation Boundary Enforcement:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. Database Level: Foreign key constraints
2. Application Level: GraphQL resolver filters
3. Query Level: WHERE organisation_id = current_user.organisation_id
4. (Recommended) PostgreSQL RLS: Row-level security policies
```

### Service Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    GraphQL Resolvers                            │
│         (Thin layer - delegates to services)                    │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Service Layer                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────────────────┐         ┌────────────────────┐         │
│  │   AuthService      │◄────────┤  TokenService      │         │
│  ├────────────────────┤         ├────────────────────┤         │
│  │ + register()       │         │ + create_token()   │         │
│  │ + login()          │         │ + verify_token()   │         │
│  │ + logout()         │         │ + refresh_token()  │         │
│  │ + change_password()│         │ + revoke_token()   │         │
│  └────────┬───────────┘         └──────────┬─────────┘         │
│           │                                │                   │
│           │ uses                           │ uses              │
│           ▼                                ▼                   │
│  ┌────────────────────┐         ┌────────────────────┐         │
│  │  AuditService      │         │  EmailService      │         │
│  ├────────────────────┤         ├────────────────────┤         │
│  │ + log_event()      │         │ + send_verification│         │
│  │ + get_user_logs()  │         │ + send_reset()     │         │
│  │ + get_org_logs()   │         │ + send_welcome()   │         │
│  └────────────────────┘         └────────────────────┘         │
│           │                                │                   │
│           │ uses                           │ uses              │
│           ▼                                ▼                   │
│  ┌────────────────────┐         ┌────────────────────┐         │
│  │  IPEncryption      │         │  TemplateEngine    │         │
│  ├────────────────────┤         ├────────────────────┤         │
│  │ + encrypt_ip()     │         │ + render()         │         │
│  │ + decrypt_ip()     │         └────────────────────┘         │
│  └────────────────────┘                                        │
│                                                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Access Layer                            │
│                    (Django ORM Models)                          │
└─────────────────────────────────────────────────────────────────┘

Key Principles:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Services encapsulate business logic
• Services are stateless (can be singletons)
• Services use dependency injection
• Services handle transactions
• Services validate inputs
• GraphQL resolvers are thin (no business logic)
• Models are data containers (minimal logic)
```

---

## Critical Recommendations

### High Priority (Address Before Implementation)

1. **Clarify Token Storage Strategy** ⚠️
   - Choose between Redis-primary or Database-primary approach
   - Document synchronisation strategy
   - Implement cache invalidation logic

2. **Add Account Lockout Mechanism** ⚠️
   - Prevent brute force attacks
   - Temporary lockout after 5 failed attempts
   - Email notification on lockout

3. **Implement PostgreSQL Row-Level Security** ⚠️
   - Defence-in-depth for multi-tenancy
   - Automatic enforcement of organisation boundaries
   - Protection against application-level bugs

4. **Add Dependency Injection Container** ⚠️
   - Manage service lifecycle
   - Prevent circular dependencies
   - Improve testability

5. **Implement GraphQL Query Complexity Analysis** ⚠️
   - Prevent expensive queries
   - Limit query depth to 10
   - Calculate complexity based on field costs

### Medium Priority (Address During Implementation)

6. **Add Object-Level Permissions** ⚠️
   - Use django-guardian for granular access control
   - Implement permission caching

7. **Implement Celery for Background Tasks** ⚠️
   - Move email sending to async tasks
   - Prevent request blocking

8. **Add Database Connection Pooling** ⚠️
   - Use PgBouncer for production
   - Configure appropriate pool sizes

9. **Implement Multi-Layer Caching** ⚠️
   - Cache user objects (5 minutes)
   - Cache permission checks (5 minutes)
   - Cache GraphQL query results (configurable)

10. **Add Soft Delete Support** ⚠️
    - Prevent accidental data loss
    - Support GDPR right to deletion
    - Implement hard delete for compliance

### Low Priority (Address in Future Phases)

11. **Automate IP Encryption Key Rotation** ⚠️
    - Quarterly rotation scheduled task
    - Re-encrypt existing data

12. **Implement GraphQL DataLoader** ⚠️
    - Prevent N+1 queries for role profiles
    - Batch database queries

13. **Add Feature Flag System** ⚠️
    - Gradual rollout of new features
    - A/B testing capability

14. **Plan for Asymmetric JWT Signing** ⚠️
    - RS256 for future microservices
    - Share public key for verification

15. **Add Database Read Replicas** ⚠️
    - Scale read operations
    - Reduce load on primary database

---

## Risk Assessment

| Risk                           | Likelihood | Impact | Mitigation Status  | Notes                                |
| ------------------------------ | ---------- | ------ | ------------------ | ------------------------------------ |
| Token synchronisation issues   | Medium     | High   | ⚠️ Needs Plan      | Clarify storage strategy             |
| Brute force login attacks      | High       | Medium | ⚠️ Needs Addition  | Add account lockout                  |
| Organisation boundary bypass   | Low        | High   | ⚠️ Add RLS         | Implement PostgreSQL RLS             |
| GraphQL query abuse            | Medium     | Medium | ⚠️ Needs Addition  | Add complexity analysis              |
| Service circular dependencies  | Medium     | Medium | ⚠️ Needs DI        | Add dependency injection             |
| N+1 queries in GraphQL         | Medium     | Medium | ✅ Monitored       | Use select_related, add DataLoader   |
| Redis cache unavailable        | Low        | Medium | ✅ Handled         | Graceful degradation to DB           |
| Email service failure          | Medium     | Low    | ✅ Planned         | Queue with Celery, retry logic       |
| Database connection exhaustion | Medium     | High   | ⚠️ Add Pooling     | Implement PgBouncer                  |
| Password database breach       | Low        | High   | ✅ Good            | Argon2, 2FA, encryption              |
| Concurrent session conflicts   | Low        | Low    | ✅ Good            | Session limit (5), oldest revoked    |
| IP encryption key compromise   | Low        | High   | ✅ Good            | Environment vars, quarterly rotation |
| GDPR compliance violations     | Low        | High   | ⚠️ Add Soft Delete | User export, soft delete, audit      |
| Horizontal scaling challenges  | Low        | Medium | ✅ Good            | Redis sessions enable scaling        |

---

## Overall Assessment

**Architecture Quality**: ✅ **Good** (8.5/10)

The User Authentication architecture is well-designed with strong security foundations, proper
multi-tenancy isolation, and good extensibility for future phases. The use of Django's built-in
authentication framework combined with GraphQL provides a modern, type-safe API.

**Key Strengths:**

1. **Security-First Design** - Comprehensive security measures including Argon2 hashing, IP
   encryption, 2FA, and audit logging demonstrate a mature security posture.

2. **Multi-Tenancy Foundation** - Organisation-based isolation provides clean separation for
   future CMS features.

3. **Extensibility Pattern** - OneToOne relationships for role profiles is an excellent
   architectural decision that will prevent technical debt as new features are added.

4. **Service Layer Separation** - Clear separation between business logic (services) and API
   layer (GraphQL resolvers) improves testability and maintainability.

5. **Testing Strategy** - Comprehensive testing approach with TDD, BDD, and E2E tests ensures
   quality and prevents regressions.

**Areas Requiring Improvement:**

1. **Token Management** - Needs clearer strategy for Redis/Database synchronisation and cache
   invalidation.

2. **Scalability Details** - While scalability is mentioned, specific implementation details
   (connection pooling, query complexity, caching strategy) need elaboration.

3. **Defence-in-Depth** - Adding PostgreSQL RLS would provide additional security layer for
   multi-tenancy.

4. **Dependency Management** - Explicit dependency injection pattern would improve service
   lifecycle management and testability.

**Critical Recommendations:**

Before proceeding with implementation, address the following:

1. Clarify and document token storage strategy (Redis vs Database trade-offs)
2. Implement account lockout mechanism
3. Add PostgreSQL Row-Level Security for multi-tenancy
4. Implement GraphQL query complexity analysis
5. Add dependency injection container for services

**Implementation Readiness**: ✅ **Ready with Improvements**

The architecture is solid enough to begin implementation, but the critical recommendations should
be addressed in Phase 1 to avoid accumulating technical debt. The medium and low priority
recommendations can be addressed during or after initial implementation.

---

## Approval Status

**Review Status**: ✅ **Approved with Conditions**

**Conditions:**

1. Address all **High Priority** recommendations before Phase 1 implementation begins
2. Document token storage strategy decision in plan
3. Add PostgreSQL RLS implementation to Phase 1 tasks
4. Include GraphQL complexity analysis in Phase 3 (GraphQL API Implementation)

**Next Steps:**

1. Update implementation plan with high priority recommendations
2. Create technical specifications for:
   - Token storage strategy
   - Account lockout mechanism
   - PostgreSQL RLS policies
   - GraphQL complexity analysis
3. Review updated plan with security team
4. Proceed with Phase 1 implementation

**Reviewer Signature**: System Architect
**Date**: 07/01/2026
**Review Version**: 1.0

---

**End of Architecture Review**
