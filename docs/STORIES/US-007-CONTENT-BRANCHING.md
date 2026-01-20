# User Story: Content Branching Workflow (feature → testing → dev → staging → production)

<!-- CLICKUP_ID: 86c7d2ngn -->

## Overview

This user story implements a Git-like branching system for content that enables safe content development and testing. Content moves through five branches (feature → testing → dev → staging → production) with separate version history per branch. The system supports branch promotion, version comparison, rollback capability, and enforces read-only protection on the production branch.

## Story

**As a** content team lead
**I want** to manage content through a branching workflow
**So that** we can develop content safely, test changes, and promote them to production without downtime

## MoSCoW Priority

- **Must Have:** Branch structure, page versioning per branch, branch-specific queries, promotion workflow
- **Should Have:** Version comparison, branch merge conflict detection, rollback capability
- **Could Have:** Scheduled promotions, branch locking, approval workflows
- **Won't Have:** Advanced merge strategies in Phase 3

**Sprint:** Sprint 10

## Repository Coverage

| Repository      | Required | Notes                                                          |
| --------------- | -------- | -------------------------------------------------------------- |
| Backend         | ✅       | Branch model, content versioning, promotion logic, GraphQL API |
| Frontend Web    | ✅       | Branch selector, promotion UI, version comparison              |
| Frontend Mobile | ✅       | Read-only access to production branch                          |
| Shared UI       | ✅       | Branch selector component                                      |

## Acceptance Criteria

### Scenario 1: Page Exists in Multiple Branches

**Given** a page exists in the system
**When** content is created or edited
**Then** each page version belongs to a specific branch:

- **feature**: Development/experimental work
- **testing**: QA and testing
- **dev**: Development environment
- **staging**: Staging environment (production-like)
- **production**: Live website
  **And** each branch maintains separate version history
  **And** changes in one branch do not affect others

### Scenario 2: Promote Content Between Branches

**Given** content has been edited in the feature branch
**When** the editor clicks "Promote to Testing"
**Then** the current version is copied to the testing branch
**And** the version number increments in testing
**And** created_by and created_at are updated
**And** an audit log entry is created
**And** the content is now available in testing for QA

### Scenario 3: View Specific Branch Content

**Given** the branch selector shows available branches
**When** the editor selects a branch
**Then** the page editor displays the version from that branch
**And** the editor can make changes to that branch version
**And** changes only affect the selected branch

### Scenario 4: Compare Versions Across Branches

**Given** a page exists in multiple branches with different content
**When** the editor selects "Compare Branches"
**Then** a side-by-side view shows:

- Feature branch version on the left
- Testing branch version on the right
- Highlights of differences
  **And** the editor can choose to accept changes from either branch

### Scenario 5: Rollback to Previous Version

**Given** a page has been promoted and issues are discovered
**When** the editor clicks "Rollback"
**Then** they can select a previous version from the version history
**And** the current version is reverted to the selected version
**And** a new version entry is created marking this as a rollback
**And** a notification is sent to team members

### Scenario 6: Production Branch Read-Only

**Given** the production branch is active
**When** content is being viewed
**Then** production branch versions cannot be directly edited
**And** changes must come from promotion from staging branch
**And** all production changes are audit-logged
**And** only users with admin role can access production branch settings

### Scenario 7: Branch-Specific Queries

**Given** the frontend is querying content
**When** a page is requested with branch parameter (or defaulting to production)
**Then** the GraphQL query returns the version from the specified branch
**And** if the page doesn't exist in that branch, an error is returned
**And** the default branch for public websites is always production

## Dependencies

- US-006: Create and Edit CMS Pages with Block-Based Content
- Page versioning system
- Audit logging system

## Tasks

### Backend Tasks

- [ ] Create ContentBranch model with enum (feature, testing, dev, staging, production)
- [ ] Modify PageVersion to include branch field
- [ ] Create branch-aware queries in GraphQL
- [ ] Create promotePage mutation for branch promotion
- [ ] Create compareVersions query for cross-branch comparison
- [ ] Create rollbackPage mutation
- [ ] Implement branch-specific version numbering
- [ ] Add branch filtering to all page queries
- [ ] Implement production branch write protection
- [ ] Create merge conflict detection logic
- [ ] Add audit logging for all promotions and rollbacks
- [ ] Add branch parameter to GraphQL page queries
- [ ] Create unit tests for promotion logic
- [ ] Create integration tests for branch workflow
- [ ] Add constraints to prevent invalid promotions

### Frontend Web Tasks

- [ ] Create BranchSelector component (dropdown)
- [ ] Create PromoteDialog component
- [ ] Create ComparisonView for side-by-side version comparison
- [ ] Add RollbackDialog component
- [ ] Create VersionHistory browser per branch
- [ ] Show current branch indicator in editor
- [ ] Add warning when editing feature branch
- [ ] Add lock indicator for production branch
- [ ] Show promotion status/history in page editor
- [ ] Create promotion confirmation dialog
- [ ] Add timeline view showing promotions between branches

### Shared UI Tasks

- [ ] Create BranchSelector component
- [ ] Create VersionComparer component
- [ ] Create ConfirmationDialog for promotions
- [ ] Create StatusBadge for branch indicators
- [ ] Create TimelineComponent for branch promotions

## Story Points (Fibonacci)

**Estimate:** 8

**Complexity factors:**

- Multiple branch states to track
- Version management across branches
- Conflict detection logic
- Promotion workflow implementation
- Read-only enforcement for production
- Complex query filtering logic
- Audit logging for all operations

---

## Related Stories

- US-006: Create and Edit CMS Pages with Block-Based Content
- US-025: Audit Logging System
