# Sprint 10: Content Branching Workflow

<!-- CLICKUP_LIST_ID: 901519464120 -->

**Sprint Duration:** 12/05/2026 - 26/05/2026 (2 weeks)
**Capacity:** 8/11 points (3 points buffer)
**Status:** Planned

---

## Sprint Goal

Implement git-like content branching workflow enabling content to flow through
feature → testing → dev → staging → production branches with version management
and promotion capabilities.

---

## MoSCoW Breakdown

### Must Have (8 points)

| Story ID                                         | Title             | Points | Status  |
| ------------------------------------------------ | ----------------- | ------ | ------- |
| [US-007](../STORIES/US-007-CONTENT-BRANCHING.md) | Content Branching | 8      | Pending |

### Should Have (0 points)

_None in this sprint_

### Could Have (0 points)

_None in this sprint_

---

## Dependencies

| Story  | Depends On | Notes                       |
| ------ | ---------- | --------------------------- |
| US-007 | US-006     | CMS page creation completed |

**Dependencies satisfied:** CMS page creation (Sprint 8) is complete.

---

## Implementation Order

### Week 1 (12/05 - 19/05)

1. **Branch Models and Backend (Priority 1)**
   - Backend: ContentBranch enum (feature, testing, dev, staging, production)
   - Backend: Modify PageVersion to include branch field
   - Backend: Branch-aware GraphQL queries
   - Backend: promotePage mutation for branch promotion
   - Backend: compareVersions query for cross-branch comparison
   - Backend: rollbackPage mutation
   - Backend: Branch-specific version numbering
   - Backend: Production branch write protection
   - Backend: Merge conflict detection
   - Backend: Audit logging for promotions

**Milestone:** Pages exist in multiple branches with promotion capability

### Week 2 (19/05 - 26/05)

2. **Branch UI and Workflow (Priority 2)**
   - Frontend Web: BranchSelector dropdown component
   - Frontend Web: PromoteDialog with confirmation
   - Frontend Web: ComparisonView for version diff
   - Frontend Web: RollbackDialog component
   - Frontend Web: VersionHistory browser per branch
   - Frontend Web: Branch indicator in page editor
   - Frontend Web: Production lock indicator
   - Frontend Web: Timeline view for promotions
   - Shared UI: BranchSelector component
   - Shared UI: VersionComparer component
   - Shared UI: ConfirmationDialog
   - Testing: Branch promotion workflow tests

**Milestone:** Content editors can promote content between branches and roll back if needed

---

## Repository Breakdown

| Story  | Backend | Frontend Web | Frontend Mobile | Shared UI |
| ------ | ------- | ------------ | --------------- | --------- |
| US-007 | ✅      | ✅           | ✅              | ✅        |

**All 4 repositories** will be active this sprint.

---

## Technical Focus

### Backend

- **Branch Management:** 5 branches (feature, testing, dev, staging, production)
- **Version Tracking:** Per-branch version history
- **Promotion Logic:** Copy content from one branch to next
- **Conflict Detection:** Detect if target branch has newer changes
- **Rollback:** Restore previous version with new version entry
- **Access Control:** Production branch is read-only (promote from staging only)

### Frontend Web

- **Branch Selector:** Dropdown showing current branch and allowing switch
- **Promotion Flow:** Guided promotion with confirmation
- **Visual Diff:** Side-by-side comparison of versions
- **Timeline View:** Visual history of promotions between branches
- **Rollback UI:** Select previous version to restore

### Frontend Mobile

- **Read-Only:** Mobile apps always query production branch
- **Branch Awareness:** Show content status (draft, published)

### Shared UI

- **Branch Components:** Reusable branch selector and indicator
- **Diff Components:** Visual comparison tools
- **Confirmation:** Standard confirmation dialogs

---

## Risks & Mitigations

| Risk                                       | Likelihood | Impact | Mitigation                                      |
| ------------------------------------------ | ---------- | ------ | ----------------------------------------------- |
| Merge conflicts with concurrent edits      | Medium     | High   | Implement conflict detection and resolution UI  |
| Data loss during promotion                 | Low        | High   | Transaction-based promotions, automatic backups |
| Complex promotion workflow confusing users | Medium     | Medium | Provide clear documentation and in-app guidance |
| Production branch accidental edits         | Low        | High   | Hard lock production, require staging promotion |
| Version history growth                     | Medium     | Low    | Archive versions older than 6 months            |

---

## Acceptance Criteria Summary

### US-007: Content Branching

- [ ] Pages exist in 5 branches (feature, testing, dev, staging, production)
- [ ] Branch selector shows current branch
- [ ] Switching branches loads that branch's version
- [ ] Promote button moves content to next branch in workflow
- [ ] Promotion creates new version in target branch
- [ ] Promotion confirmation shows what will change
- [ ] Version comparison shows side-by-side diff
- [ ] Rollback restores previous version
- [ ] Production branch is read-only (no direct edits)
- [ ] Only admins can promote to production
- [ ] Audit log tracks all promotions and rollbacks
- [ ] Conflict detection warns of newer changes in target branch
- [ ] Timeline view shows promotion history
- [ ] GraphQL queries accept branch parameter
- [ ] Default branch for public queries is production

---

## Definition of Done

- [ ] All acceptance criteria met for US-007
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass for promotion workflow
- [ ] Security tests pass for branch access control
- [ ] Code reviewed and merged to main
- [ ] Documentation updated (branching guide, promotion workflow)
- [ ] Deployed to development environment
- [ ] QA tested on dev environment
- [ ] Demo prepared for sprint review

---

## Sprint Metrics

| Metric            | Target | Actual |
| ----------------- | ------ | ------ |
| Points Committed  | 8      | -      |
| Points Completed  | -      | -      |
| Stories Completed | 1      | -      |
| Velocity          | -      | -      |
| Test Coverage     | >80%   | -      |

---

## Sprint Retrospective

_To be completed after sprint ends_

### What Went Well

- TBD

### What Could Improve

- TBD

### Action Items

- TBD

---

## Notes

- Branch workflow:
  1. **Feature:** Experimental work, draft content
  2. **Testing:** QA and content review
  3. **Dev:** Development environment testing
  4. **Staging:** Production-like environment for final review
  5. **Production:** Live public website
- Promotion flow:
  - Feature → Testing (content review)
  - Testing → Dev (development environment)
  - Dev → Staging (pre-production)
  - Staging → Production (go live)
- Rollback strategy:
  - Each rollback creates new version (not destructive)
  - Mark version as rollback with reference to original
  - Rollback notification sent to team
  - Rollback reason can be provided
- Conflict detection:
  - Compare version timestamps
  - Warn if target has newer version than source
  - Show diff of conflicting changes
  - Allow forced promotion with warning
- Access control:
  - Developers: Can edit feature, testing, dev branches
  - Content editors: Can edit feature, testing branches
  - Admins: Can promote to production
  - All: Can view any branch
- Version comparison:
  - Side-by-side block comparison
  - Highlight added/removed/changed blocks
  - Show metadata changes (title, slug, etc.)
  - Export diff as report

**Sprint 11 Preparation:**

- Publication workflow ready
- Pages can be marked as published
- Public URLs route to published pages only

---

_Last Updated: 06/01/2026_
_Sprint Owner: Development Team_
