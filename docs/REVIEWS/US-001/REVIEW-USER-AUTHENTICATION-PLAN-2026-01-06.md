# Code Review: User Authentication Plan

**Last Updated**: 07/01/2026
**Reviewer**: Senior Code Reviewer
**Files Reviewed**:

- `docs/PLANS/US-001-USER-AUTHENTICATION.md`
- `docs/STORIES/US-001-USER-AUTHENTICATION.md`

---

## Summary

The User Authentication plan is comprehensive and well-structured. However, it requires significant
updates to properly integrate Django's Groups and permissions system for the CMS platform's
multi-tiered access control. The plan currently lacks proper role-based access control (RBAC)
design and doesn't account for the extensibility needed for future Customer and Seller models.

**Overall Assessment**: Request changes (critical issues found)

---

## Critical Issues

### 1. Missing Django Groups and Permissions System

**Issue**: The plan does not leverage Django's built-in Groups model for role-based access control.

**Why This Matters**:

- The CMS platform requires flexible, multi-tiered access control
- Future phases will add Customer, Seller, and other role models
- Django Groups provide a battle-tested RBAC foundation
- Custom permission management is reinventing the wheel

**Fix**:
Add Django Groups integration:

- Use `django.contrib.auth.models.Group` for role management
- Define platform-level, organisation-level, and website-level groups
- Implement custom permissions for CMS operations
- Design for extensibility (Customer, Seller roles in future phases)

---

### 2. Inconsistent Password Requirements

**File**: `US-001-USER-AUTHENTICATION.md`

**Lines**: 141-146 vs 899-904

**Issue**: Password requirements conflict between sections:

- Section "Security Requirements": Minimum **12 characters**
- Section "Password Requirements": Minimum **8 characters**

**Fix**: Standardise to **12 characters minimum** (more secure).

---

### 3. No Extensibility Design for Future Roles

**Issue**: The plan doesn't address how Customer, Seller, and other future role models will extend
the base User model.

**Why This Matters**:

- Phase 4+ introduces e-commerce templates requiring Customer/Seller roles
- Blog templates require Author/Contributor roles
- Corporate templates require Employee/Client roles
- No clear extension path from base User model

**Fix**: Add extensibility section:

- Document abstract base class patterns
- Show how future models extend User or link via OneToOne
- Design permissions to support role hierarchies
- Plan for role-specific GraphQL types

---

### 4. Missing Multi-Site Access Tier Design

**Issue**: The plan focuses on organisation-level multi-tenancy but doesn't address website-level
access tiers.

**Why This Matters**:

- One organisation may manage multiple websites (e.g., blog + e-commerce)
- Access needs to be scoped to specific websites, not just organisations
- Users may have different roles on different websites

**Fix**: Add website-level access tier:

- Introduce `Website` model linking to `Organisation`
- Add `UserWebsiteRole` model for website-specific permissions
- Document how roles cascade (Platform → Organisation → Website)
- Show permission checking flow in GraphQL resolvers

---

### 5. No Permission Checking Examples in GraphQL

**Issue**: GraphQL resolver examples don't show how to check permissions.

**Why This Matters**:

- Without permission checks, organisation boundaries alone aren't sufficient
- Role-based actions (e.g., "can publish content") require permission validation
- Security vulnerabilities if permission checks are inconsistent

**Fix**: Add permission checking examples:

```python
@strawberry.field
def publish_page(self, page_id: strawberry.ID) -> Page:
    """Publish a page (requires 'cms.publish_page' permission)."""
    if not self.user.has_perm('cms.publish_page'):
        raise PermissionError("You don't have permission to publish pages")
    # ... rest of resolver
```

---

## DRY Violations

### 1. Duplicate Token Models

**Issue**: `SessionToken`, `PasswordResetToken`, and `EmailVerificationToken` have similar structure.

**Existing Pattern**: All three models have:

- `token` field
- `expires_at` field
- `created_at` field
- Foreign key to User

**Action**: Consider abstract base class:

```python
class BaseToken(models.Model):
    """Abstract base for token models."""
    token = models.CharField(max_length=255, unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True
```

---

## Improvements

### 1. Add Django Admin Integration

**Suggestion**: Document Django admin configuration for user management.

**Why**:

- Admins need to view/manage users
- Audit logs should be viewable in admin
- Group management UI needed

**Recommendation**: Add Phase 1.5 for Django admin setup.

---

### 2. Add User Story Alignment Check

**Issue**: User story US-001 mentions minimum 12 characters for passwords, but plan says 8.

**Fix**: Ensure plan matches user story requirements exactly.

---

### 3. Document Permission Migration Path

**Suggestion**: Show how to migrate from simple `is_staff` checks to full permission system.

**Why**:

- Phase 1 may start simple
- Future phases need complex permissions
- Need clear upgrade path

---

### 4. Add GraphQL Permission Directives

**Suggestion**: Use GraphQL directives for permission checks:

```python
@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[IsAuthenticated, HasPermission("cms.publish_page")])
    def publish_page(self, page_id: strawberry.ID) -> Page:
        # Permission already checked by decorator
        ...
```

---

## Security Analysis

### Positive Notes

- **Password Hashing**: Argon2 is OWASP recommended
- **IP Encryption**: Good practice for PII protection
- **Rate Limiting**: Prevents brute force attacks
- **Audit Logging**: Comprehensive event tracking
- **2FA Support**: TOTP-based implementation

### Security Improvements Needed

#### 1. Permission Escalation Risk

**Risk**: Without proper permission checks, users could escalate privileges.

**Mitigation**:

- Add permission validation in all GraphQL resolvers
- Document permission hierarchies
- Test for privilege escalation in security tests

#### 2. Cross-Organisation Access Risk

**Risk**: GraphQL resolvers mention organisation boundary checks but don't show implementation.

**Mitigation**:

```python
def get_queryset(self):
    """Filter to current organisation only."""
    return User.objects.filter(organisation=self.request.user.organisation)
```

#### 3. Missing CSRF Protection

**Risk**: GraphQL mutations vulnerable to CSRF if not configured.

**Mitigation**: Document CSRF token handling for GraphQL mutations.

---

## Extensibility Gaps

### 1. No Role Hierarchy Design

**Missing**: How do roles inherit permissions?

**Example Needed**:

```
Platform Superuser (all permissions)
  ↓
Organisation Owner (all org permissions)
  ↓
Website Admin (all website permissions)
  ↓
Editor (content permissions)
  ↓
Viewer (read-only)
```

### 2. No Custom Permission Examples

**Missing**: How to define custom permissions for CMS operations.

**Example Needed**:

```python
class Page(models.Model):
    class Meta:
        permissions = [
            ("publish_page", "Can publish pages"),
            ("approve_page", "Can approve pages"),
            ("delete_page", "Can delete pages"),
        ]
```

### 3. No Multi-Website User Design

**Missing**: How does one user access multiple websites?

**Example Needed**:

```python
class UserWebsiteRole(models.Model):
    """Assigns a user to a website with a specific role."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    website = models.ForeignKey(Website, on_delete=models.CASCADE)
    groups = models.ManyToManyField(Group)
```

---

## Testing Gaps

### 1. No Permission Tests

**Missing**: Tests for permission checking in GraphQL resolvers.

**Add**:

```python
def test_user_without_permission_cannot_publish_page(self):
    """Test that users without 'publish_page' permission get denied."""
    user = UserFactory.create()  # No permissions
    response = graphql_client.execute(
        publish_page_mutation,
        user=user
    )
    assert 'PermissionDenied' in response['errors'][0]['message']
```

### 2. No Cross-Organisation Access Tests

**Missing**: Tests verifying organisation boundary enforcement.

**Add**:

```python
def test_user_cannot_access_other_organisation_users(self):
    """Test organisation isolation."""
    org1 = OrganisationFactory.create()
    org2 = OrganisationFactory.create()
    user1 = UserFactory.create(organisation=org1)
    user2 = UserFactory.create(organisation=org2)

    # user1 tries to query user2
    response = graphql_client.execute(user_query, user=user1, variables={'id': user2.id})
    assert response['data']['user'] is None
```

### 3. No Role Hierarchy Tests

**Missing**: Tests for role inheritance and permission cascading.

---

## Documentation Gaps

### 1. No Permission Documentation

**Missing**: How to define, assign, and check permissions.

**Add**: Section on "Permission System Design"

### 2. No Role Management Guide

**Missing**: How admins create and manage roles.

**Add**: Admin guide for role/group management

### 3. No Migration Guide

**Missing**: How to migrate from simple auth to role-based auth.

**Add**: Migration path for permission system evolution

---

## SaaS Products and Software Integration

This section addresses how the authentication system integrates with the platform's SaaS products and external services.

### Overview

The CMS platform includes multiple integrated services:

- **Email Service** - Integrated email platform for organisation mailboxes
- **OnlyOffice** - Cloud document collaboration (word processing, spreadsheets, presentations)
- **Vaultwarden** - Password manager for secure credential storage
- **Third-Party Integrations** - External SaaS tools (Phase 11)
- **AI Service** - Anthropic Claude API integration (Phase 12)

All services must share authentication state and respect organisation boundaries.

---

### 1. Single Sign-On (SSO) Architecture

**Issue**: The plan does not address how users authenticate once and access all integrated services.

**Why This Matters**:

- Users expect seamless access across all platform services
- Re-authentication for each service creates poor UX
- Token sharing must be secure and scoped appropriately
- Session state must be synchronized across services

**Design Requirements**:

#### Token Sharing Strategy

```python
# apps/core/services/sso_service.py

class SSOService:
    """Service for Single Sign-On across platform services.

    Manages token issuance, verification, and revocation across all
    integrated SaaS products.
    """

    @staticmethod
    def generate_service_token(
        user: User,
        service: str,
        scopes: List[str]
    ) -> str:
        """Generate a service-specific token for SSO.

        Args:
            user: The authenticated user
            service: Service identifier (email, documents, vault, etc.)
            scopes: List of permission scopes for this service

        Returns:
            JWT token scoped to the service
        """
        pass

    @staticmethod
    def verify_service_token(token: str, service: str) -> User:
        """Verify a service-specific token."""
        pass
```

#### Service Token Structure

```json
{
  "user_id": "uuid",
  "organisation_id": "uuid",
  "service": "onlyoffice",
  "scopes": ["documents.read", "documents.write", "documents.share"],
  "exp": "timestamp",
  "iss": "backend_cms"
}
```

#### GraphQL Mutations for SSO

```graphql
type Mutation {
  """
  Generate a service-specific SSO token.
  Requires user to be authenticated with the main platform.
  """
  generateServiceToken(service: ServiceType!, scopes: [String!]!): ServiceTokenPayload!
}

enum ServiceType {
  EMAIL
  DOCUMENTS
  VAULT
  AI
}

type ServiceTokenPayload {
  token: String!
  expiresAt: DateTime!
  redirectUrl: String
}
```

**Recommendation for US-001**: **Defer to Phase 10 (SaaS Products)**. US-001 should focus on core
authentication. SSO infrastructure can be added when integrating first SaaS product.

---

### 2. OnlyOffice Integration

**Issue**: No design for how users access cloud documents and how permissions map from Django to
OnlyOffice.

**Why This Matters**:

- OnlyOffice has its own permission system
- Documents must be scoped to organisations
- User roles in Django must map to OnlyOffice roles
- Real-time collaboration requires session synchronization

**Design Requirements**:

#### Permission Mapping

| Django Group/Permission  | OnlyOffice Role | Capabilities                    |
| ------------------------ | --------------- | ------------------------------- |
| `documents.admin`        | Admin           | Manage all documents, settings  |
| `documents.editor`       | Editor          | Create, edit, delete own docs   |
| `documents.collaborator` | Collaborator    | Edit shared documents           |
| `documents.viewer`       | Viewer          | Read-only access to shared docs |
| Organisation Owner       | Admin           | Full access to org documents    |
| Platform Superuser       | SuperAdmin      | Access all organisations' docs  |

#### Document Access Control

```python
# apps/integrations/onlyoffice/models.py

class DocumentPermission(models.Model):
    """Permission model for OnlyOffice documents.

    Links Django users/groups to OnlyOffice document permissions
    scoped by organisation.
    """

    document_id = models.CharField(max_length=255)  # OnlyOffice doc ID
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=ONLYOFFICE_ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['document_id', 'user']),
            models.Index(fields=['organisation', 'role']),
        ]
```

#### OnlyOffice SSO Flow

```
1. User clicks "Open Document" in CMS
2. Backend generates service token for OnlyOffice
3. Backend calls OnlyOffice API to create session
4. Backend returns OnlyOffice URL with token
5. User redirected to OnlyOffice with auto-login
6. OnlyOffice verifies token with backend webhook
7. OnlyOffice loads document with appropriate permissions
```

**Recommendation for US-001**: **Out of scope**. OnlyOffice integration is Phase 9. US-001 should
only implement core User/Organisation models and authentication. Document permissions can extend
this later.

---

### 3. Vaultwarden Integration

**Issue**: No design for how the password manager authenticates users and syncs credentials.

**Why This Matters**:

- Vaultwarden stores sensitive credentials
- Organisation vaults must be isolated
- User passwords for the CMS should not be stored in the vault
- Vault access must support 2FA

**Design Requirements**:

#### Vault Access Model

```python
# apps/integrations/vaultwarden/models.py

class VaultAccess(models.Model):
    """Tracks which users have access to organisation vaults.

    Vaultwarden has its own user database, but we sync permissions
    from Django to maintain organisation isolation.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    vault_id = models.CharField(max_length=255)  # Vaultwarden vault ID
    role = models.CharField(max_length=50, choices=VAULT_ROLE_CHOICES)
    last_synced_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('user', 'organisation', 'vault_id')]
```

#### Permission Mapping

| Django Group/Permission | Vaultwarden Role | Capabilities               |
| ----------------------- | ---------------- | -------------------------- |
| `vault.admin`           | Owner            | Manage vault, invite users |
| `vault.manager`         | Admin            | Add/edit vault items       |
| `vault.user`            | User             | Access shared vault items  |
| Organisation Owner      | Owner            | Full vault access          |

#### Vaultwarden SSO Flow

```
1. User clicks "Password Manager" in CMS
2. Backend checks if user has vault access
3. Backend creates/updates Vaultwarden user via API
4. Backend syncs organisation vault permissions
5. Backend generates Vaultwarden session token
6. User redirected to Vaultwarden with auto-login
7. Vaultwarden displays organisation vault
```

**Recommendation for US-001**: **Out of scope**. Vaultwarden is Phase 10. The User model in US-001
provides the foundation, but vault-specific fields and permissions should be added in Phase 10.

---

### 4. Email Service Integration

**Issue**: No design for how users get mailboxes provisioned or access email.

**Why This Matters**:

- Each organisation may have custom email domains
- User mailboxes must be created automatically on registration
- Email authentication separate from CMS authentication
- Organisation admins need to manage email accounts

**Design Requirements**:

#### Email Account Model

```python
# apps/integrations/email/models.py

class EmailAccount(models.Model):
    """Email account linked to a CMS user.

    Represents a mailbox on the integrated email service
    (e.g., Roundcube, Mailcow, custom IMAP/SMTP).
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='email_account')
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    email_address = models.EmailField(unique=True)
    mailbox_id = models.CharField(max_length=255)  # Email service mailbox ID
    quota_mb = models.IntegerField(default=1024)  # Mailbox size limit
    password_hash = models.CharField(max_length=255)  # Separate from CMS password
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['organisation', 'email_address']),
        ]
```

#### Mailbox Provisioning on User Registration

```python
# apps/core/services/auth_service.py

class AuthService:
    @staticmethod
    def register_user(email, password, organisation, **kwargs) -> User:
        """Register a new user.

        Creates user account and provisions integrated services:
        - Email mailbox (if organisation has email service)
        - Vault access (if organisation has vault)
        - Document workspace (if organisation has OnlyOffice)
        """
        user = User.objects.create_user(...)

        # Provision email mailbox
        if organisation.has_email_service:
            EmailService.provision_mailbox(user)

        # Provision vault access
        if organisation.has_vault:
            VaultService.provision_vault_access(user)

        # Provision document workspace
        if organisation.has_documents:
            DocumentService.provision_workspace(user)

        return user
```

#### Email SSO Flow

```
1. User clicks "Email" in CMS
2. Backend generates email service token
3. Backend returns webmail URL with token
4. User redirected to webmail with auto-login
5. Webmail verifies token with backend API
6. Webmail loads user's mailbox
```

**Recommendation for US-001**: **Partially in scope**. The User model should include an
`email_verified` field (already present), but mailbox provisioning is Phase 8. Add a placeholder
field `has_email_account` (Boolean) to track provisioning status.

---

### 5. Third-Party OAuth/OIDC

**Issue**: No support for external identity providers (Google, Microsoft, GitHub, etc.).

**Why This Matters**:

- Enterprise customers expect SSO with their existing identity providers
- Social login reduces friction for new users
- SAML/OIDC required for enterprise sales
- Multi-factor authentication may be delegated to IdP

**Design Requirements**:

#### OAuth Provider Model

```python
# apps/core/models/oauth_provider.py

class OAuthProvider(models.Model):
    """Configuration for external OAuth/OIDC providers.

    Allows organisations to configure SSO with Google, Microsoft,
    GitHub, Okta, Auth0, etc.
    """

    PROVIDER_CHOICES = [
        ('google', 'Google'),
        ('microsoft', 'Microsoft'),
        ('github', 'GitHub'),
        ('okta', 'Okta'),
        ('auth0', 'Auth0'),
        ('custom_oidc', 'Custom OIDC'),
        ('custom_saml', 'Custom SAML'),
    ]

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    provider_type = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)  # Encrypted
    redirect_uri = models.URLField()
    scopes = models.JSONField(default=list)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('organisation', 'provider_type')]
```

#### GraphQL Mutations for OAuth

```graphql
type Mutation {
  """
  Initiate OAuth login flow.
  Returns authorization URL for user to visit.
  """
  initiateOAuthLogin(provider: String!): OAuthURLPayload!

  """
  Complete OAuth login after callback.
  Exchanges authorization code for access token and user info.
  """
  completeOAuthLogin(provider: String!, code: String!): AuthPayload!
}

type OAuthURLPayload {
  authorizationUrl: String!
  state: String!
}
```

**Recommendation for US-001**: **Out of scope**. OAuth/OIDC is Phase 11 (Third-Party
Integrations). US-001 should focus on email/password authentication. OAuth can be added later
without changing the User model structure.

---

### 6. API Authentication for Integrations

**Issue**: No design for how external services authenticate when calling the backend API.

**Why This Matters**:

- OnlyOffice needs to verify user permissions via webhook
- Email service needs to validate SSO tokens
- Third-party integrations need API keys
- Webhooks must be authenticated

**Design Requirements**:

#### API Key Model

```python
# apps/core/models/api_key.py

class APIKey(models.Model):
    """API keys for service-to-service authentication.

    Allows external services and integrations to authenticate
    without user credentials.
    """

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  # e.g., "OnlyOffice Webhook"
    key_hash = models.CharField(max_length=255, unique=True)
    permissions = models.JSONField(default=list)  # List of permission scopes
    last_used_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['key_hash']),
            models.Index(fields=['organisation', 'is_active']),
        ]
```

#### GraphQL Mutations for API Keys

```graphql
type Mutation {
  """
  Create API key for service integration.
  Requires 'api_key.create' permission.
  """
  createAPIKey(input: CreateAPIKeyInput!): APIKeyPayload!

  """
  Revoke an API key.
  """
  revokeAPIKey(keyId: ID!): Boolean!
}

input CreateAPIKeyInput {
  name: String!
  permissions: [String!]!
  expiresAt: DateTime
}

type APIKeyPayload {
  id: ID!
  name: String!
  key: String! # Only returned once on creation
  expiresAt: DateTime
}
```

**Recommendation for US-001**: **Out of scope**. API key infrastructure is Phase 11. US-001 should
focus on user authentication. Service-to-service auth can be added later.

---

### 7. AI Service Authentication

**Issue**: No design for how Claude API access is managed and tracked.

**Why This Matters**:

- Anthropic API keys are sensitive credentials
- API usage must be tracked per organisation for billing
- Rate limits must be enforced per organisation
- Audit logs must track AI usage for compliance

**Design Requirements**:

#### AI Usage Tracking Model

```python
# apps/ai/models.py

class AIUsageLog(models.Model):
    """Track AI API usage per organisation.

    Records all Claude API calls for billing and audit purposes.
    """

    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    service = models.CharField(max_length=50)  # e.g., "content_generation", "seo"
    model = models.CharField(max_length=50)  # e.g., "claude-opus-4"
    input_tokens = models.IntegerField()
    output_tokens = models.IntegerField()
    cost_usd = models.DecimalField(max_digits=10, decimal_places=4)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['organisation', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
```

#### AI Service Permissions

```python
class Meta:
    permissions = [
        ("use_ai_content", "Can use AI for content generation"),
        ("use_ai_seo", "Can use AI for SEO optimization"),
        ("use_ai_code", "Can use AI for code assistance"),
        ("view_ai_usage", "Can view AI usage statistics"),
    ]
```

**Recommendation for US-001**: **Out of scope**. AI integration is Phase 12. The User/Organisation
models provide the foundation, but AI-specific tracking should be added in Phase 12.

---

### 8. Security Considerations for Multi-Service Auth

**Critical Security Issues**:

#### 8.1 Token Scope Leakage

**Risk**: A service token for OnlyOffice could be used to access Vaultwarden.

**Mitigation**:

```python
def verify_service_token(token: str, required_service: str) -> User:
    """Verify token is scoped to the correct service."""
    payload = jwt.decode(token, settings.SECRET_KEY)

    if payload.get('service') != required_service:
        raise PermissionError("Token not valid for this service")

    return User.objects.get(id=payload['user_id'])
```

#### 8.2 Organisation Boundary Bypass

**Risk**: User from Org A accesses documents/vault of Org B.

**Mitigation**:

```python
def check_organisation_access(user: User, resource_org_id: str) -> None:
    """Verify user belongs to the resource's organisation."""
    if str(user.organisation_id) != resource_org_id:
        raise PermissionError("Access denied: organisation boundary violation")
```

#### 8.3 Session Fixation Attacks

**Risk**: Attacker steals SSO token and impersonates user across services.

**Mitigation**:

- Service tokens expire after 5 minutes (short-lived)
- Token rotation on each service access
- Bind tokens to IP address (encrypted)
- Revoke all service tokens on main session logout

#### 8.4 API Key Compromise

**Risk**: API key leaked, allowing unauthorized service access.

**Mitigation**:

- API keys have expiration dates
- API keys scoped to specific permissions
- API key usage logged with IP address
- Automatic revocation on suspicious activity

---

### 9. Recommendations

#### What Should Be in Scope for US-001

**Include in US-001**:

1. Core User and Organisation models (already designed)
2. Email/password authentication (already designed)
3. 2FA with TOTP (already designed)
4. Session token management (already designed)
5. Audit logging for authentication events (already designed)
6. IP address encryption (already designed)

**Add to US-001**:

1. `has_email_account` Boolean field on User model (tracks if mailbox provisioned)
2. `has_vault_access` Boolean field on User model (tracks if vault provisioned)
3. Basic permission checking in GraphQL resolvers (examples needed)

#### What Should Be Deferred to Later Phases

**Defer to Phase 8 (Email Service)**:

- EmailAccount model
- Mailbox provisioning service
- Email SSO flow

**Defer to Phase 9 (OnlyOffice)**:

- DocumentPermission model
- OnlyOffice SSO flow
- Permission mapping to OnlyOffice roles

**Defer to Phase 10 (Vaultwarden)**:

- VaultAccess model
- Vaultwarden SSO flow
- Vault permission syncing

**Defer to Phase 11 (Third-Party Integrations)**:

- OAuthProvider model
- OAuth/OIDC login flows
- APIKey model
- Webhook authentication

**Defer to Phase 12 (AI Integration)**:

- AIUsageLog model
- Claude API authentication
- AI usage quotas and billing

#### Security Considerations Summary

**Critical for US-001**:

- Implement strong password hashing (Argon2) ✅ Already in plan
- Encrypt IP addresses ✅ Already in plan
- Audit all authentication events ✅ Already in plan
- Rate limit authentication endpoints ✅ Already in plan
- Enforce organisation boundaries in GraphQL ❌ Examples missing

**Critical for SSO (Later Phases)**:

- Service tokens scoped to specific services
- Short token expiration (5 minutes for SSO)
- Bind tokens to IP addresses
- Revoke service tokens on main logout

**Critical for API Keys (Phase 11)**:

- API keys scoped to minimal permissions
- API key expiration dates
- Log all API key usage
- Automatic revocation on suspicious activity

---

### 10. Updated Next Steps for US-001

**Before Implementation Starts**:

1. ✅ User/Organisation models already well-designed
2. ✅ Authentication flows already documented
3. ❌ Add permission checking examples to GraphQL resolvers
4. ❌ Add `has_email_account` and `has_vault_access` Boolean fields to User model
5. ❌ Document that SSO/API keys are out of scope for US-001

**Future Phases Will Add**:

- Phase 8: Email service integration and mailbox provisioning
- Phase 9: OnlyOffice SSO and document permissions
- Phase 10: Vaultwarden SSO and vault permissions
- Phase 11: OAuth/OIDC providers and API keys
- Phase 12: AI service authentication and usage tracking

**Verdict for SaaS Integration in US-001**: The current plan correctly focuses on core
authentication. SaaS product integration should be deferred to later phases. Only minor additions
needed: permission checking examples and Boolean flags for service provisioning status.

---

## Organisation Invitation Analysis

### The Question

**Should "Organisation Invitation" functionality be included in US-001 or deferred?**

### What Organisation Invitation Involves

1. **Invite Users via Email**
   - Organisation admin sends invitation email
   - Email contains unique, expiring token
   - Track invitation status (pending, accepted, declined, expired)

2. **Accept/Decline Workflow**
   - User receives invitation email with link
   - User can accept (creates account or links existing)
   - User can decline (invitation marked as declined)
   - Invitation expires after set period (e.g., 7 days)

3. **Role Assignment on Invitation**
   - Specify role/group when inviting
   - User automatically assigned to specified groups on acceptance
   - Option to assign to specific websites (future)

4. **Invitation Management**
   - View pending invitations
   - Resend invitation
   - Revoke invitation before acceptance
   - Audit log of invitation events

### Dependencies and Complexity

**Required Models:**

```python
class OrganisationInvitation(models.Model):
    """Invitation to join an organisation."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    email = models.EmailField()
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    groups = models.ManyToManyField(Group, blank=True)
    status = models.CharField(choices=[
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
        ('revoked', 'Revoked'),
    ])
    expires_at = models.DateTimeField()
    accepted_at = models.DateTimeField(null=True)
    accepted_by = models.ForeignKey(User, null=True, related_name='accepted_invitations')
    created_at = models.DateTimeField(auto_now_add=True)
```

**Required GraphQL Mutations:**

```graphql
type Mutation {
  inviteToOrganisation(input: InviteInput!): Invitation!
  acceptInvitation(token: String!): AuthPayload!
  declineInvitation(token: String!): Boolean!
  revokeInvitation(invitationId: ID!): Boolean!
  resendInvitation(invitationId: ID!): Boolean!
}

type Query {
  pendingInvitations: [Invitation!]!
  myInvitations: [Invitation!]!
}
```

**Email Templates Needed:**

- `invitation_email.html` - Invitation to join organisation
- `invitation_accepted.html` - Notification to inviter
- `invitation_reminder.html` - Reminder before expiry

### Analysis: In Scope vs Deferred

| Consideration        | In US-001                                  | Deferred                         |
| -------------------- | ------------------------------------------ | -------------------------------- |
| **Complexity**       | Adds ~2-3 days                             | Separate story                   |
| **MVP Essential?**   | No - manual user creation works            | Later story                      |
| **Email Dependency** | Requires email service working             | Same dependency                  |
| **User Flow**        | Required for self-service onboarding       | Manual admin creation OK for MVP |
| **Security**         | Token management similar to password reset | Already have token patterns      |
| **Testing**          | Additional BDD scenarios                   | Separate test suite              |
| **Sprint Fit**       | US-001 already 5 points                    | Would add 3+ points              |

### Recommendation: **DEFER to US-004 (Organisation Setup)**

**Rationale:**

1. **US-001 Scope is Already Defined**
   - US-001 (5 points) is focused on core authentication
   - Adding invitations would expand scope by ~60%
   - Current plan and sprint allocation already set

2. **US-004 is the Natural Home**
   - US-004 "Organisation Setup" (8 points) covers team management
   - Invitation is an organisation-level feature, not auth-level
   - US-004 already includes "Organisation owners can manage users"

3. **MVP Can Work Without Invitations**
   - Phase 1: Superusers/admins manually create users via Django Admin
   - Phase 2: Add invitation system for self-service onboarding
   - This is a common SaaS pattern (admin-only initially)

4. **Email Service is Not Complete in Sprint 1**
   - Mailpit works for dev/test
   - Production email needs proper SMTP configuration
   - Invitation emails need reliable delivery

5. **Dependencies Are Satisfied by US-004**
   - US-004 depends on US-001 (auth complete)
   - Invitation can use email verification patterns from US-001
   - Group/role assignment needs organisation context

### Action Items

**For US-001 (No Changes):**

- Keep scope focused on core authentication
- Manual user creation via Django Admin sufficient for MVP
- Document that invitations are out of scope

**For US-004 (Add to Plan):**

- Add "Organisation Invitation System" as sub-feature
- Reuse token patterns from password reset
- Add BDD scenarios for invitation workflow
- Add GraphQL mutations for invitation management

**Update US-004 Story:**

```markdown
## Additional Acceptance Criteria (to be added)

### Scenario 5: Invite User to Organisation

Given I am an organisation admin
When I send an invitation to "newuser@example.com" with role "Editor"
Then the invitation is created with status "pending"
And an invitation email is sent
And the invitation expires in 7 days

### Scenario 6: Accept Organisation Invitation

Given I received an invitation to "Acme Corp"
When I click the invitation link
And I complete registration (or link existing account)
Then I am added to the organisation with assigned role
And the invitation status is "accepted"
And an audit log entry is created
```

---

## Final Review Summary

### Document Consistency Check

| Document                                                                | Status        | Notes                                    |
| ----------------------------------------------------------------------- | ------------- | ---------------------------------------- |
| [US-001-USER-AUTHENTICATION.md](../PLANS/US-001-USER-AUTHENTICATION.md) | ✅ Reviewed   | Comprehensive plan, minor updates needed |
| [DEVELOPMENT-ROADMAP.md](../STORIES/DEVELOPMENT-ROADMAP.md)             | ✅ Consistent | US-001 at 5 points, Week 1-2             |
| [STORIES/QUICK-REFERENCE.md](../STORIES/QUICK-REFERENCE.md)             | ✅ Consistent | US-001 listed as "Small" (5 points)      |
| [SPRINTS/QUICK-REFERENCE.md](../SPRINTS/QUICK-REFERENCE.md)             | ✅ Consistent | Sprint 1 includes US-001 (10 pts total)  |
| [SPRINT-SUMMARY.md](../SPRINTS/SPRINT-SUMMARY.md)                       | ✅ Consistent | Sprint 1: US-001, US-003                 |

### Outstanding Issues

**Critical (Must Fix Before Implementation):**

1. ❌ **Password Requirements Inconsistency**
   - Plan Section "Security Requirements" says 12 characters
   - Plan Section "Password Requirements" says 8 characters
   - **Action:** Standardise to 12 characters minimum

2. ❌ **Missing Django Groups Integration**
   - Plan does not leverage Django's built-in Groups model
   - **Action:** Add section on Groups/Permissions system

3. ❌ **Missing Permission Checking Examples**
   - GraphQL resolvers don't show permission validation
   - **Action:** Add permission decorator examples

**Important (Should Fix):**

4. ⚠️ **Add `has_email_account` and `has_vault_access` Fields**
   - Needed for future SaaS integrations
   - **Action:** Add Boolean fields to User model

5. ⚠️ **Document Extensibility Path**
   - No guidance on future Customer/Seller models
   - **Action:** Add section on role extension patterns

6. ⚠️ **Abstract Token Base Class**
   - DRY violation with duplicate token models
   - **Action:** Create `BaseToken` abstract model

**Minor (Nice to Have):**

7. ℹ️ **Add Django Admin Configuration**
   - User management via admin interface
   - **Action:** Document admin setup

8. ℹ️ **Document Permission Migration Path**
   - How to evolve from simple to complex permissions
   - **Action:** Add migration guide section

### Overall Readiness Assessment

| Criterion                 | Status                 | Score    |
| ------------------------- | ---------------------- | -------- |
| Requirements Clear        | ✅                     | 9/10     |
| Technical Design Complete | ⚠️                     | 7/10     |
| Security Addressed        | ✅                     | 8/10     |
| Testing Strategy Defined  | ✅                     | 8/10     |
| Documentation Complete    | ⚠️                     | 7/10     |
| Sprint Alignment          | ✅                     | 9/10     |
| Dependencies Identified   | ✅                     | 9/10     |
| **Overall**               | **Ready with Changes** | **8/10** |

### Verdict

**Status:** ✅ **APPROVED WITH REQUIRED CHANGES**

The US-001 User Authentication plan is comprehensive and well-structured. It can proceed to
implementation after addressing the critical issues:

1. Fix password requirement inconsistency (12 characters minimum)
2. Add Django Groups and permissions integration
3. Add permission checking examples to GraphQL resolvers

**Organisation Invitation:** **DEFERRED to US-004**

The invitation system should be implemented as part of US-004 (Organisation Setup), not US-001.
This maintains US-001's focused scope and follows the natural feature grouping.

### Next Steps

1. ✅ Plan reviewed and approved with required changes
2. ⏳ Update plan with password requirements fix
3. ⏳ Add Django Groups section to plan
4. ⏳ Add permission checking examples
5. ⏳ Update US-004 story to include invitation system
6. ⏳ Run `/syntek-dev-suite:backend` to begin implementation

---

**Reviewed By:** Senior Code Reviewer
**Review Date:** 07/01/2026
**Review Status:** Approved with Required Changes
