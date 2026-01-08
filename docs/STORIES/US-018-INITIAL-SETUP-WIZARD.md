# User Story: Initial Setup Wizard for Rapid Deployment

<!-- CLICKUP_ID: 86c7d2trz -->

## Overview

This story covers a comprehensive guided setup wizard that enables rapid deployment and configuration of Syntek instances. The wizard walks administrators through domain configuration, template selection, design token customisation, admin user creation, environment variable setup, and deployment verification. It includes health checks and a post-setup checklist to track remaining configuration tasks.

## Story

**As a** administrator deploying the Syntek platform
**I want** to follow a guided setup wizard that configures everything needed
**So that** new client instances can be deployed and configured quickly without manual steps

## MoSCoW Priority

- **Must Have:** Multi-step wizard, domain configuration, template selection, admin user setup, verification checks
- **Should Have:** Environment variable setup, integration suggestions, deployment verification
- **Could Have:** Video tutorials per step, AI-assisted setup
- **Won't Have:** One-click deployment in Phase 14

**Sprint:** Sprint 28

## Repository Coverage

| Repository      | Required | Notes                                                   |
| --------------- | -------- | ------------------------------------------------------- |
| Backend         | ✅       | Wizard state management, deployment checks, GraphQL API |
| Frontend Web    | ✅       | Wizard UI, step forms, progress tracking                |
| Frontend Mobile | ❌       | Not applicable in Phase 14                              |
| Shared UI       | ✅       | Wizard components, form components                      |

## Acceptance Criteria

### Scenario 1: Start Setup Wizard

**Given** a fresh Syntek instance is running
**When** an administrator accesses the system
**Then** they are directed to the setup wizard
**And** the wizard shows:

- Current step indicator (e.g., Step 1 of 7)
- Step name and description
- Form fields for this step
- Previous/Next buttons (Previous disabled on step 1)
- Progress bar showing completion

### Scenario 2: Configure Domain

**Given** the wizard is on the Domain step
**When** the administrator enters information
**Then** they can specify:

- Primary domain (e.g., companywebsite.com)
- Subdomain prefix (for SaaS apps like email.companywebsite.com)
- SSL certificate preferences
- DNS provider (for verification)
  **And** DNS configuration guide is shown
  **And** domain validation is performed

### Scenario 3: Select Template

**Given** the wizard is on the Template step
**When** the administrator selects a template
**Then** they can:

- View all 9 templates
- Preview each template
- Select the template
  **And** the selected template is noted for initialisation

### Scenario 4: Configure Design Tokens

**Given** the Template has been selected
**When** the wizard is on the Design Tokens step
**Then** the administrator can:

- Set primary brand colour
- Set secondary colours
- Select fonts (from system or Google Fonts)
- Preview token application
  **And** default tokens are shown for quick setup
  **And** advanced options are available for customisation

### Scenario 5: Create Admin User

**Given** the wizard is on the Admin User step
**When** the administrator enters information
**Then** they can:

- Enter first and last name
- Enter email address
- Set password (with requirements displayed)
- Enable 2FA setup
  **And** the user is created
  **And** they can log in with these credentials

### Scenario 6: Setup Environment Variables

**Given** the wizard is on the Secrets step
**When** the administrator enters secrets
**Then** they can:

- Add common secrets (STRIPE_KEY, SENDGRID_KEY, etc.)
- Use templates for guided setup
- Import from .env file
  **And** secrets are encrypted and stored
  **And** validation confirms required secrets are present

### Scenario 7: Verify Deployment

**Given** all steps are complete
**When** the wizard moves to verification
**Then** the system checks:

- Database connectivity
- Redis/Cache connectivity
- Email service connectivity
- Domain DNS configuration
- SSL certificate
- Storage access
  **And** green checkmarks show what's working
  **And** warnings show what needs attention
  **And** user can retry checks

### Scenario 8: Complete Setup

**Given** verification is complete
**When** the administrator clicks "Complete Setup"
**Then** the system:

- Initialises the selected template with default content
- Creates default design token set
- Creates initial pages
- Sends welcome email
- Redirects to the dashboard
- Marks setup as complete (wizard doesn't reappear)

### Scenario 9: Resume Incomplete Setup

**Given** a setup wizard was started but not completed
**When** an administrator logs in
**Then** they can:

- Resume from the step they left off
- View progress so far
- Continue or restart

### Scenario 10: Setup Checklist

**Given** setup is complete
**When** the administrator views the dashboard
**Then** a setup checklist shows:

- [ ] Domain configured and verified
- [ ] Template selected and initialised
- [ ] Design tokens customised
- [ ] First page published
- [ ] Team members invited
- [ ] Integrations connected
- [ ] Email service set up
- [ ] SSL certificate configured
      **And** each item can be clicked to configure it
      **And** completion percentage is shown

## Dependencies

- All previous systems (domain, template, secrets, etc.)
- Health check system
- Deployment verification scripts

## Tasks

### Backend Tasks

- [ ] Create SetupSession model to track wizard progress
- [ ] Create SetupStep model for step state
- [ ] Create SetupConfiguration model for storing setup data
- [ ] Implement wizard state machine
- [ ] Create step progress tracking
- [ ] Create health check service
- [ ] Create database connectivity check
- [ ] Create Redis connectivity check
- [ ] Create email service check
- [ ] Create DNS verification check
- [ ] Create SSL certificate check
- [ ] Create storage access check
- [ ] Create GraphQL mutation for saving step data
- [ ] Create GraphQL query for wizard status
- [ ] Create template initialisation trigger
- [ ] Implement wizard completion logic
- [ ] Add audit logging for setup events
- [ ] Create unit tests for wizard flow
- [ ] Create integration tests for full setup

### Frontend Web Tasks

- [ ] Create SetupWizard layout (main container)
- [ ] Create StepIndicator component (shows current step and progress)
- [ ] Create DomainStep form component
- [ ] Create TemplateSelectionStep component
- [ ] Create DesignTokenStep component
- [ ] Create AdminUserStep form component
- [ ] Create SecretsStep component (with .env import)
- [ ] Create VerificationStep component
- [ ] Create CompletionStep component
- [ ] Implement form validation per step
- [ ] Add Previous/Next button navigation
- [ ] Store wizard state in browser (localStorage or session)
- [ ] Create error handling and retry logic
- [ ] Add progress bar showing completion
- [ ] Create SetupChecklist component for post-setup
- [ ] Show helpful tips/documentation per step
- [ ] Implement step skipping (if optional)

### Shared UI Tasks

- [ ] Create Wizard component (step container)
- [ ] Create StepIndicator component
- [ ] Create FormStep component (base for all steps)
- [ ] Create DomainInput component
- [ ] Create TemplateSelector component
- [ ] Create ColourPicker component
- [ ] Create FontSelector component
- [ ] Create CheckBox component (for checklist)
- [ ] Create ProgressBar component
- [ ] Create HealthCheckItem component

## Story Points (Fibonacci)

**Estimate:** 13

**Complexity factors:**

- Complex multi-step form with state management
- Wizard state persistence and resume capability
- Multiple verification checks
- Template initialisation on completion
- Health check system implementation
- Integration with all previous systems
- Step-by-step form validation
- Progress tracking and UI updates

---

## Related Stories

- US-004: Organisation Creation and Setup
- US-008: Template System
- US-005: Design Token System
- US-016: Environment Secrets
- US-013: Caching System (health check)
