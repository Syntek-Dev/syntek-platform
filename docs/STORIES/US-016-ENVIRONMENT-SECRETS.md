# User Story: Environment Variable and Secrets Management

<!-- CLICKUP_ID: 86c7d2rvw -->

## Overview

This story covers secure management of encrypted environment variables and secrets across development, staging, and production environments. Features include encrypted storage with environment-specific values, secret versioning with rollback capability, granular access controls, audit logging of all operations, and integration with the deployment pipeline for automatic secret injection.

## Story

**As a** system administrator
**I want** to securely manage encrypted environment variables and secrets
**So that** sensitive configuration can be safely stored, versioned, and deployed across environments

## MoSCoW Priority

- **Must Have:** Encrypted secret storage, environment-specific secrets (dev/staging/prod), access control, audit logging
- **Should Have:** Secret versioning, secret templates for common integrations, bulk import/export, key rotation
- **Could Have:** Secret validation schema, secret complexity requirements
- **Won't Have:** Hardware security module (HSM) in Phase 13

**Sprint:** Sprint 26

## Repository Coverage

| Repository      | Required | Notes                                                   |
| --------------- | -------- | ------------------------------------------------------- |
| Backend         | ✅       | Secret storage, encryption, GraphQL API, access control |
| Frontend Web    | ✅       | Secret management UI, audit logs                        |
| Frontend Mobile | ❌       | Not applicable in Phase 13                              |
| Shared UI       | ✅       | Secret editor components                                |

## Acceptance Criteria

### Scenario 1: Create Encrypted Secret

**Given** an administrator is in the Secrets section
**When** they create a new secret
**Then** they can:

- Enter secret name (e.g., STRIPE_API_KEY)
- Select environment (dev, staging, production, all)
- Enter secret value
- Add description
  **And** the secret is encrypted before storage
  **And** the secret is not logged or displayed after creation

### Scenario 2: Environment-Specific Secrets

**Given** secrets are managed
**When** they are stored
**Then** each secret can have different values per environment:

- Development environment
- Staging environment
- Production environment
  **And** the correct secret is injected into each deployment
  **And** environment isolation is enforced

### Scenario 3: View Secret (Masked)

**Given** a secret exists
**When** an administrator views the secrets list
**Then** the secret value is:

- Masked in the list view (shows only last 4 characters)
- Only visible in full if "Show Secret" is clicked
- Requires additional confirmation to reveal
- Logged as a security audit event

### Scenario 4: Secret Versioning

**Given** a secret is updated
**When** the new value is saved
**Then** the previous value is:

- Retained in version history
- Viewable with timestamp and who changed it
- Rollback-able to any previous version
- All versions are retained indefinitely

### Scenario 5: Access Control

**Given** secrets are stored
**When** team members request access
**Then** access is controlled by role:

- Only admins and security role can access secrets
- Developers can see secret names but not values
- Access to view secrets is audited
- Sensitive secrets can be marked with higher access requirements

### Scenario 6: Secret Templates

**Given** an administrator sets up common integrations
**When** they select a template
**Then** a template provides:

- Required secret names for the integration
- Input validation rules
- Documentation links
- Example values (for demo purposes)
  **And** templates exist for:
- Stripe (STRIPE_API_KEY, STRIPE_SECRET_KEY)
- SendGrid (SENDGRID_API_KEY)
- AWS (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
- Mailchimp (MAILCHIMP_API_KEY)
- Etc.

### Scenario 7: Bulk Import Secrets

**Given** an administrator has secrets in an .env file
**When** they import the file
**Then** the system:

- Parses the .env file
- Displays preview of secrets to be imported
- Requires confirmation
- Encrypts and stores all secrets
- Shows success/failure for each secret
- Does not import duplicate secret names (shows warning)

### Scenario 8: Deployment Secret Injection

**Given** an application is being deployed
**When** the deployment process runs
**Then** the system:

- Retrieves encrypted secrets for the environment
- Decrypts them (with appropriate permissions)
- Injects them into the deployment container/process
- Ensures secrets are not logged
- Cleans up after deployment

### Scenario 9: Rotation and Cleanup

**Given** a secret is no longer needed
**When** it is deleted
**Then** the system:

- Marks it as deleted (soft delete)
- Retains history for 90 days
- Permanently removes after 90 days
- Logs the deletion as a security event

## Dependencies

- Encryption library (Fernet)
- Django model for secret storage
- Access control system
- Deployment system integration

## Tasks

### Backend Tasks

- [ ] Create SecretCategory model
- [ ] Create EncryptedSecret model with encrypted field
- [ ] Create SecretVersion model for versioning
- [ ] Create SecretAccessLog model
- [ ] Create SecretTemplate model
- [ ] Implement secret encryption/decryption service
- [ ] Create GraphQL query for secrets (with access control)
- [ ] Create GraphQL mutation for creating/updating secrets
- [ ] Create GraphQL mutation for deleting secrets
- [ ] Create GraphQL query for secret history
- [ ] Implement access control checks
- [ ] Create .env file parser
- [ ] Create bulk import mutation
- [ ] Create secret template library
- [ ] Implement secret masking in logs
- [ ] Create GraphQL query for deployment secret injection
- [ ] Add audit logging for all secret operations
- [ ] Add unit tests for encryption/decryption
- [ ] Add integration tests for secret operations

### Security Gap Remediation Tasks (from Security Review)

- [ ] **H001**: Implement comprehensive key management strategy:
  - [ ] Integrate with AWS Secrets Manager or HashiCorp Vault for production
  - [ ] Create key inventory documentation (all encryption keys used in system)
  - [ ] Define key hierarchy (master keys, data encryption keys, signing keys)
  - [ ] Implement automated key rotation schedule:
    - [ ] Quarterly rotation for encryption keys
    - [ ] Annual rotation for master keys
    - [ ] Immediate rotation capability for compromised keys
  - [ ] Create key backup and recovery procedures
  - [ ] Document key access controls and audit requirements
  - [ ] Implement key escrow for disaster recovery
  - [ ] Create key rotation management command
  - [ ] Add alerting for key expiry (30 days before rotation due)
- [ ] Add unit tests for key rotation
- [ ] Add integration tests for Secrets Manager/Vault integration
- [ ] Add documentation for key management procedures

### Frontend Web Tasks

- [ ] Create Secrets management page
- [ ] Create SecretList component
- [ ] Create SecretCreate form
- [ ] Create SecretEdit form (with confirmation)
- [ ] Create SecretViewToggle (show/hide with confirmation)
- [ ] Create SecretHistory browser
- [ ] Create EnvironmentSelector (dev/staging/prod)
- [ ] Create BulkImportDialog
- [ ] Create TemplateSelector for new secrets
- [ ] Create AccessLog viewer
- [ ] Add validation for secret format/length
- [ ] Show warning when viewing secrets (audit logged)
- [ ] Create copy-to-clipboard button (with confirmation)
- [ ] Show version rollback option

### Shared UI Tasks

- [ ] Create SecureInput component (masked text)
- [ ] Create SecretViewer component
- [ ] Create EnvironmentSelector component
- [ ] Create TemplateSelector component
- [ ] Create ConfirmationDialog for sensitive operations
- [ ] Create AlertBox for warnings

## Story Points (Fibonacci)

**Estimate:** 8

**Complexity factors:**

- Encryption/decryption implementation
- Access control and permission checking
- Version tracking and rollback
- Multi-environment management
- .env file parsing
- Deployment integration
- Audit logging for all operations
- Template creation system

---

## Security Gaps Addressed

This story addresses the following security gaps from the US-001 Security Implementation Review:

| Gap ID | Description | Implementation |
|--------|-------------|----------------|
| **H001** | Key management strategy incomplete | AWS Secrets Manager/HashiCorp Vault integration, key hierarchy, automated rotation |

---

## Related Stories

- US-012: Audit Logging System (logging secret access)
- US-014: Third-Party Integration Adapter System (storing integration credentials)
- US-020: Deployment Pipeline (secret injection during deployment)
