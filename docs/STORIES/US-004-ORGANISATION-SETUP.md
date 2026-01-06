# User Story: Organisation Creation and Setup

<!-- CLICKUP_ID: 86c7d2mcd -->

## Story

**As a** new user
**I want** to create an organisation during registration or afterwards
**So that** I can manage my websites/apps under a single organisational entity with multi-user support

## MoSCoW Priority

- **Must Have:** Organisation model, multi-tenancy enforcement, domain assignment, basic setup
- **Should Have:** Organisation branding (logo, name), subscription plan selection, team member invitations
- **Could Have:** Sub-organisations, custom domain CNAMEs, white-label setup
- **Won't Have:** Organisation hierarchy in Phase 1

**Sprint:** Sprint 22

## Repository Coverage

| Repository      | Required | Notes                                                       |
| --------------- | -------- | ----------------------------------------------------------- |
| Backend         | ✅       | Organisation model, multi-tenancy isolation, database setup |
| Frontend Web    | ✅       | Organisation setup form, admin dashboard                    |
| Frontend Mobile | ❌       | Not applicable in Phase 1                                   |
| Shared UI       | ✅       | Form components for setup                                   |

## Acceptance Criteria

### Scenario 1: Create Organisation During Registration

**Given** a user is completing registration
**When** they enter organisation name and select a plan
**Then** the organisation is created in the database
**And** the user becomes the organisation owner
**And** a default subscription is created for the selected plan
**And** default design tokens are initialised
**And** the user is redirected to set up their template

### Scenario 2: Verify Unique Organisation Slug

**Given** the user is setting up an organisation
**When** they enter an organisation name
**Then** a slug is generated automatically
**And** the slug is checked for uniqueness
**And** if taken, a suffix is added or the user is prompted to choose
**And** the slug is used in the domain (e.g., orgslug.companywebsite.com)

### Scenario 3: Assign Domain

**Given** an organisation is created
**When** domain setup is initialised
**Then** the user can:

- Use a default subdomain (provided.companywebsite.com)
- Add a custom domain (custom-domain.com)
  **And** custom domains require DNS verification
  **And** the domain is stored in the database

### Scenario 4: Team Member Invitation

**Given** a user is the organisation owner
**When** they invite a team member by email
**Then** an invitation email is sent
**And** the invitation includes a setup link valid for 7 days
**And** the invited user can accept/decline
**And** upon acceptance, they are added to the organisation
**And** a role (Admin/Editor/Viewer) is assigned

### Scenario 5: Multi-Tenancy Enforcement

**Given** a user is querying organisation data
**When** they request data through GraphQL
**Then** the query is automatically filtered to their organisation
**And** cross-organisation data access returns an error
**And** audit logging tracks all cross-organisation access attempts

## Dependencies

- US-001: User Authentication with Email and Password
- Email service configured
- GraphQL API implemented
- Database migration system

## Tasks

### Backend Tasks

- [ ] Create Organisation model with fields: name, slug, domain, logo_url, is_active
- [ ] Create subscription tracking (plan: free/starter/professional/enterprise)
- [ ] Create Team model for members
- [ ] Create TeamInvitation model with expiry
- [ ] Implement organisation-based data filtering in GraphQL middleware
- [ ] Create multi-tenant cache isolation key structure
- [ ] Implement database signal to create default design tokens on org creation
- [ ] Create createOrganisation GraphQL mutation
- [ ] Create inviteTeamMember GraphQL mutation
- [ ] Create acceptTeamInvitation GraphQL mutation
- [ ] Implement custom domain DNS verification
- [ ] Create GraphQL queries for organisation data
- [ ] Add audit logging for all organisation operations
- [ ] Add unit tests for multi-tenancy isolation
- [ ] Add integration tests for team invitation flow

### Frontend Web Tasks

- [ ] Create organisation setup form in registration flow
- [ ] Create organisation dashboard
- [ ] Create team management interface
- [ ] Implement invitation email sending
- [ ] Display invitation acceptance/rejection flow
- [ ] Show organisation domain settings
- [ ] Create custom domain DNS setup guide
- [ ] Add organisation branding settings (logo, name)

### Shared UI Tasks

- [ ] Create FormInput for organisation name
- [ ] Create SlugGenerator component
- [ ] Create DomainInput component
- [ ] Create UserInvitationForm component
- [ ] Create AlertBox for validation messages

## Story Points (Fibonacci)

**Estimate:** 8

**Complexity factors:**

- Multi-tenancy architecture implementation
- Database isolation enforcement
- Domain and subdomain management
- Email invitation system
- DNS verification for custom domains
- Subscription plan tracking
- Team management features
- Data filtering middleware

---

## Related Stories

- US-001: User Authentication with Email and Password
- US-015: Design Token System Setup
- US-020: Template Selection and Initialization
