# Quick Reference Guide - Syntek User Stories

## Overview

Quick lookup tables and story selection guide for the Syntek CMS Platform user stories. Organises 22 stories by effort level, repository, phase, and team role. Use this guide for sprint planning, resource allocation, and understanding story dependencies.

---

## Stories by Effort Level

### Small Stories (5 points) - 2-3 days per person

- US-001: User Authentication
- US-003: Password Reset

### Medium Stories (8 points) - 4-5 days per person

- US-002: Login with 2FA
- US-004: Organisation Setup
- US-007: Content Branching
- US-009: Media Library
- US-010: Page Publication
- US-012: Audit Logging
- US-013: Caching System
- US-016: Environment Secrets

### Large Stories (13 points) - 1-2 weeks per person

- US-005: Design Tokens
- US-006: Page Creation
- US-008: Templates
- US-011: GraphQL API
- US-014: Integrations
- US-015: AI Integration
- US-018: Setup Wizard
- US-021: Cloud Documents
- US-022: Password Manager

### Epic Stories (21 points) - 3-4 weeks per person

- US-017: Email SaaS Service
- US-019: Shared UI Library
- US-020: Deployment Pipeline

## Stories by Repository

### Backend (20 stories)

- US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010
- US-011, US-012, US-013, US-014, US-015, US-016, US-017, US-018, US-021, US-022

### Frontend Web (21 stories)

- US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010
- US-011, US-012, US-014, US-015, US-016, US-017, US-018, US-019, US-020, US-021, US-022

### Frontend Mobile (13 stories)

- US-001, US-002, US-004, US-005, US-007, US-010, US-011, US-013, US-015
- US-017, US-019, US-020, US-021, US-022

### Shared UI (18 stories)

- US-001, US-002, US-003, US-004, US-005, US-006, US-007, US-008, US-009, US-010
- US-012, US-014, US-015, US-016, US-018, US-019, US-021, US-022

## Stories by Phase

| Phase                | Stories                        |
| -------------------- | ------------------------------ |
| 1: Core Foundation   | US-001, US-002, US-003, US-004 |
| 2: Design Tokens     | US-005                         |
| 3: CMS Engine        | US-006, US-007, US-009, US-010 |
| 4: Templates         | US-008                         |
| 5: UI Library        | US-019                         |
| 6-7: Frontend        | (Web/Mobile consume API)       |
| 8: Email SaaS        | US-017                         |
| 9: Cloud Documents   | US-021                         |
| 10: Password Manager | US-022                         |
| 11: Integrations     | US-014                         |
| 12: AI               | US-015                         |
| 13: Secrets          | US-016                         |
| 14: Setup Wizard     | US-018                         |
| 15: Deployment       | US-020                         |
| Cross-cutting        | US-011, US-012, US-013         |

## Critical Path (Dependencies)

```
Start → US-001 (Auth) → US-004 (Org) → US-011 (API) → US-006 (CMS)
                                             ↓
                                        US-005 (Tokens)
                                             ↓
                                        US-008 (Templates)

US-006 → US-007 (Branching)
US-006 → US-009 (Media)
US-006 → US-010 (Publish)

→ US-013 (Cache) [early]
→ US-012 (Audit) [early]
→ US-019 (UI Lib) [parallel]

→ US-014 (Integrations) → US-015 (AI)
                       → US-017 (Email)
                       → US-021 (Cloud Docs)
                       → US-022 (Password Vault)

→ US-016 (Secrets)
→ US-018 (Setup Wizard) [late]
→ US-020 (Deployment) [end]
```

## Story Selection by Team Role

### For Backend Engineers

Priority order: US-001 → US-002 → US-003 → US-004 → US-011 → US-013 → US-012
→ US-005 → US-006 → US-007 → US-009 → US-010 → US-008 → US-014 → US-015 → US-021
→ US-022 → US-016 → US-017 → US-018

### For Frontend Web Engineers

Priority order: US-001 → US-002 → US-003 → US-004 → US-019 → US-005 → US-006
→ US-007 → US-009 → US-010 → US-008 → US-011 → US-012 → US-014 → US-015 → US-021
→ US-022 → US-016 → US-017 → US-018 → US-020

### For Mobile Engineers

Priority order: US-001 → US-002 → US-003 → US-004 → US-005 → US-007 → US-010
→ US-011 → US-015 → US-021 → US-022 → US-019 → US-020

### For DevOps/Infra

Priority order: US-013 → US-012 → US-016 → US-020 → (then others for
integration testing)

## Story Relationships

### Authentication Stories

- US-001: Basic auth (unblocks everything)
- US-002: 2FA (security enhancement)
- US-003: Password reset (account recovery)

### Content Management

- US-005: Styling system
- US-006: Page editing
- US-007: Workflow
- US-008: Quick start templates
- US-009: Asset management
- US-010: Publishing

### Technical Infrastructure

- US-011: API layer (foundation)
- US-012: Observability (monitoring)
- US-013: Performance (caching)
- US-016: Configuration (secrets)
- US-020: Operations (deployment)

### Business Integration

- US-014: Extension system
- US-015: AI capabilities
- US-017: Email service
- US-021: Cloud document storage
- US-022: Password vault

### User Experience

- US-018: Onboarding (setup wizard)
- US-019: Components (consistent UI)
- US-004: Multi-tenancy (org features)

## Recommended Sprint Planning

### Sprint 1 (2 weeks)

- US-001 (5 points)
- US-002 (8 points)
- US-003 (5 points)
- **Total:** 18 points

### Sprint 2 (2 weeks)

- US-004 (8 points)
- US-013 (8 points)
- US-012 (8 points)
- **Total:** 24 points

### Sprint 3-4 (4 weeks)

- US-011 (13 points)
- US-005 (13 points)
- **Total:** 26 points

### Sprint 5 (2 weeks)

- US-006 (13 points)
- **Total:** 13 points

### Sprint 6 (2 weeks)

- US-007 (8 points)
- US-009 (8 points)
- **Total:** 16 points

### Sprint 7 (2 weeks)

- US-008 (13 points)
- **Total:** 13 points

### Sprint 8 (2 weeks)

- US-010 (8 points)
- US-019 (21 points) [parallel web/mobile teams]
- **Total:** 29 points

### Sprint 9 (2 weeks)

- US-014 (13 points)
- US-016 (8 points)
- **Total:** 21 points

### Sprint 10 (2 weeks)

- US-015 (13 points)
- US-017 (21 points) [major feature, may span 2 sprints]
- **Total:** 34 points

### Sprint 11 (2 weeks)

- US-018 (13 points)
- **Total:** 13 points

### Sprint 12 (3 weeks)

- US-020 (21 points)
- **Total:** 21 points

**Total: 12 sprints = 24 weeks = 6 months**

## Testing Strategy by Story Type

### Auth Stories (US-001, US-002, US-003)

- Unit tests for validators
- Integration tests for flows
- Security tests for password handling
- E2E tests for complete flows

### CMS Stories (US-005, US-006, US-007, US-008, US-009, US-010)

- Unit tests for models and services
- Integration tests for workflows
- E2E tests for editor UX
- Performance tests for large content

### Infrastructure Stories (US-011, US-012, US-013, US-020)

- Load testing
- Security scanning
- Performance benchmarking
- Deployment testing

### Integration Stories (US-014, US-015, US-016, US-017)

- Mock external services
- Error handling tests
- Rate limit tests
- Security tests for credential handling

## Acceptance Criteria Quick Check

When implementing a story, verify:

1. ✅ All "Scenario 1" criteria implemented
2. ✅ All "Scenario 2+" criteria implemented
3. ✅ All "Dependencies" stories completed
4. ✅ All "Tasks" completed
5. ✅ Unit tests written (>80% coverage)
6. ✅ Integration tests pass
7. ✅ Code reviewed
8. ✅ Documentation updated
9. ✅ Audit logging in place (if applicable)
10. ✅ Performance tested

## Useful Commands

```bash
# View a specific story
cat /mnt/archive/OldRepos/backend_template/docs/STORIES/US-XXX-NAME.md

# List all stories
ls /mnt/archive/OldRepos/backend_template/docs/STORIES/US-*.md

# Count total stories
ls /mnt/archive/OldRepos/backend_template/docs/STORIES/US-*.md | wc -l

# View README with index
cat /mnt/archive/OldRepos/backend_template/docs/STORIES/README.md

# View development roadmap
cat /mnt/archive/OldRepos/backend_template/docs/STORIES/DEVELOPMENT-ROADMAP.md
```

## Next Steps

1. **Review:** Read the README.md for overview
2. **Plan:** Use DEVELOPMENT-ROADMAP.md for sprint planning
3. **Assign:** Use story points to balance team capacity
4. **Implement:** Follow tasks in individual stories
5. **Test:** Use acceptance criteria for validation
6. **Deploy:** Use US-020 deployment pipeline

---

**For details on a specific story, see `/docs/STORIES/US-XXX-FEATURE-NAME.md`**

**For architecture details, see `/docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md`**

**For project standards, see `/.claude/CLAUDE.md`**
