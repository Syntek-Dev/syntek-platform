# User Story: Organisation Creation and Setup

<!-- CLICKUP_ID: 86c7d2mcd -->

**Last Updated**: 07/01/2026
**Version**: 1.1

## Overview

This user story implements the organisation creation and multi-tenancy foundation. Users can create organisations during registration, set up custom domains, and manage team members through an email-based invitation system with role-based access control. Multi-tenancy is enforced at the database and GraphQL levels to ensure data isolation between organisations.

## Story

**As a** new user or organisation admin
**I want** to create an organisation and manage team members through invitations
**So that** I can manage websites/apps with multi-user support and self-service team onboarding

## MoSCoW Priority

- **Must Have:** Organisation model, multi-tenancy enforcement, domain assignment, team member
  invitations (email, accept/decline, role assignment)
- **Should Have:** Organisation branding (logo, name), subscription plan selection, invitation
  management (resend, revoke)
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

### Scenario 4: Verify Multi-Tenancy Enforcement

**Given** a user is querying organisation data
**When** they request data through GraphQL
**Then** the query is automatically filtered to their organisation
**And** cross-organisation data access returns an error
**And** audit logging tracks all cross-organisation access attempts

### Scenario 5: Invite User to Organisation

**Given** I am an organisation admin
**When** I send an invitation to a new team member with role "Editor"
**Then** the invitation is created with status "pending"
**And** an invitation email is sent to the team member's email address
**And** the invitation expires in 7 days
**And** an audit log entry is created for the invitation

### Scenario 6: Accept Organisation Invitation

**Given** I received an invitation to join an organisation
**When** I click the invitation link in the email
**And** I complete registration or link an existing account
**Then** I am added to the organisation
**And** I am assigned the specified role from the invitation
**And** the invitation status changes to "accepted"
**And** an audit log entry records the acceptance

### Scenario 7: Decline Organisation Invitation

**Given** I received an invitation to join an organisation
**When** I click the decline link in the email
**Then** the invitation status is marked as "declined"
**And** the user who sent the invitation receives a notification
**And** an audit log entry records the decline

### Scenario 8: Manage Pending Invitations

**Given** I am an organisation admin
**When** I view the pending invitations list
**Then** I can see all pending invitations with status and recipient email
**And** I can resend an invitation (if still valid)
**And** I can revoke an invitation (before acceptance)
**And** I can view the user who created each invitation

## Dependencies

- US-001: User Authentication with Email and Password
- Email service configured
- GraphQL API implemented
- Database migration system

## Tasks

### Backend Tasks

**Organisation Models:**

- [ ] Create Organisation model with fields: name, slug, domain, logo_url, is_active
- [ ] Create subscription tracking (plan: free/starter/professional/enterprise)
- [ ] Implement organisation-based data filtering in GraphQL middleware
- [ ] Create multi-tenant cache isolation key structure
- [ ] Implement database signal to create default design tokens on org creation

**Invitation System:**

- [ ] Create OrganisationInvitation model with fields: id, organisation, email, invited_by,
      token, groups, status, expires_at, accepted_at, accepted_by, created_at
- [ ] Implement invitation token generation and validation
- [ ] Create invitation email templates (invitation, reminder, notification)
- [ ] Implement invitation expiry checking (7 day window)
- [ ] Create GraphQL mutation: inviteToOrganisation (requires admin role)
- [ ] Create GraphQL mutation: acceptInvitation (with token)
- [ ] Create GraphQL mutation: declineInvitation (with token)
- [ ] Create GraphQL mutation: revokeInvitation (requires admin)
- [ ] Create GraphQL mutation: resendInvitation (requires admin)
- [ ] Create GraphQL query: pendingInvitations (organisation admins only)
- [ ] Create GraphQL query: myInvitations (current user)
- [ ] Add audit logging for all invitation events
- [ ] Implement role/group assignment from invitation on acceptance

**Domain and DNS:**

- [ ] Implement custom domain DNS verification
- [ ] Create GraphQL queries for organisation data

**Testing:**

- [ ] Add unit tests for multi-tenancy isolation
- [ ] Add unit tests for invitation token validation
- [ ] Add integration tests for invitation workflow
- [ ] Add integration tests for role assignment on acceptance
- [ ] Add BDD tests for all invitation scenarios (5-8)

### Frontend Web Tasks

**Organisation Setup:**

- [ ] Create organisation setup form in registration flow
- [ ] Create organisation dashboard
- [ ] Show organisation domain settings
- [ ] Create custom domain DNS setup guide
- [ ] Add organisation branding settings (logo, name)

**Invitation Management:**

- [ ] Create "Invite Team Member" form
- [ ] Implement team member invitation sending via GraphQL
- [ ] Create pending invitations management interface
- [ ] Implement resend invitation functionality
- [ ] Implement revoke invitation functionality
- [ ] Create invitation email preview (for admins)

**Invitation Acceptance:**

- [ ] Create invitation acceptance page (accessible via email token)
- [ ] Implement registration flow for new users accepting invitations
- [ ] Implement account linking flow for existing users accepting invitations
- [ ] Create invitation decline flow
- [ ] Add success confirmation after acceptance

### Shared UI Tasks

- [ ] Create FormInput for organisation name
- [ ] Create SlugGenerator component
- [ ] Create DomainInput component
- [ ] Create UserInvitationForm component (email, role selection)
- [ ] Create InvitationStatusBadge component
- [ ] Create AlertBox for validation messages

## Story Points (Fibonacci)

**Estimate:** 13

**Complexity factors:**

- Multi-tenancy architecture implementation
- Database isolation enforcement
- Domain and subdomain management
- Invitation token generation and validation
- Email invitation system with expiry handling
- Accept/decline workflow for invitations
- Role assignment from invitations
- Invitation management (resend, revoke)
- DNS verification for custom domains
- Subscription plan tracking
- Team management features
- Data filtering middleware
- Audit logging for invitations
- BDD test scenarios (5-8)

---

## Related Stories

- US-001: User Authentication with Email and Password
- US-015: Design Token System Setup
- US-020: Template Selection and Initialization
