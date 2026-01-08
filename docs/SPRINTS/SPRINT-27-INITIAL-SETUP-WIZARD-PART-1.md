# Sprint 27: Initial Setup Wizard (Part 1)

<!-- CLICKUP_LIST_ID: 901519464181 -->

**Sprint Duration:** 05/01/2027 - 19/01/2027 (2 weeks)
**Capacity:** 11/11 points (at capacity)
**Status:** Planned

---

## Overview

This sprint implements the first part of the guided setup wizard for rapid Syntek platform deployment. The wizard provides a comprehensive step-by-step interface for new organisations to configure their instance, including domain setup, template selection, design token configuration, admin user creation, and environment variable management. This is the first of two sprints dedicated to the setup wizard, with Part 2 (Sprint 28) handling verification checks and completion workflows. Successful completion enables rapid onboarding and reduces manual configuration work.

---

## Sprint Goal

Implement a comprehensive guided setup wizard for rapid Syntek platform deployment with domain
configuration, template selection, design token setup, admin creation, and environment
variable configuration.

---

## MoSCoW Breakdown

### Must Have (11 points)

| Story ID                                            | Title                 | Points | Status  |
| --------------------------------------------------- | --------------------- | ------ | ------- |
| [US-018](../STORIES/US-018-INITIAL-SETUP-WIZARD.md) | Setup Wizard (Part 1) | 11     | Pending |

_US-018 split: 11 points for core wizard steps (domain, template, tokens, admin, secrets) this
sprint, 2 points for verification and polish in Sprint 22_

---

## Dependencies

| Story  | Depends On                           | Notes                               |
| ------ | ------------------------------------ | ----------------------------------- |
| US-018 | All previous (US-001 through US-020) | Setup wizard integrates all systems |

**Dependencies satisfied:** All previous user stories (Sprints 1-20) are complete.

---

## Implementation Order

### Week 1 (13/10 - 20/10)

1. **Wizard Backend and Core Steps (Priority 1)**
   - Backend: SetupSession model
   - Backend: SetupStep model
   - Backend: SetupConfiguration model
   - Backend: Wizard state machine
   - Backend: GraphQL mutations for wizard steps
   - Frontend Web: SetupWizard layout
   - Frontend Web: StepIndicator component
   - Frontend Web: DomainStep form
   - Frontend Web: TemplateSelectionStep
   - Frontend Web: DesignTokenStep

**Milestone:** Wizard steps 1-3 operational (domain, template, tokens)

### Week 2 (20/10 - 27/10)

2. **Admin and Secrets Steps (Priority 2)**
   - Frontend Web: AdminUserStep form
   - Frontend Web: SecretsStep with .env import
   - Backend: Admin user creation logic
   - Backend: Secret bulk import during setup
   - Frontend Web: Progress bar
   - Frontend Web: Form validation per step
   - Shared UI: Wizard components
   - Testing: End-to-end wizard flow tests

**Milestone:** Complete wizard flow operational (steps 1-5)

---

## Repository Breakdown

| Story  | Backend | Frontend Web | Frontend Mobile | Shared UI |
| ------ | ------- | ------------ | --------------- | --------- |
| US-018 | ✅      | ✅           | ❌              | ✅        |

**3 repositories** will be active this sprint.

---

## Technical Focus

### Backend

- **Wizard State:** Track progress through multi-step wizard
- **Validation:** Ensure each step has required data
- **Integration:** Combine all previous systems

### Frontend Web

- **Multi-Step Form:** Guided 5-step wizard
- **Validation:** Real-time form validation
- **Progress:** Visual progress indicator

### Shared UI

- **Wizard:** Stepper and form step components
- **Forms:** Domain, template, token, admin inputs

---

## Risks & Mitigations

| Risk                                   | Likelihood | Impact | Mitigation                                                |
| -------------------------------------- | ---------- | ------ | --------------------------------------------------------- |
| Wizard complexity confuses users       | Medium     | Medium | Clear instructions, helpful tooltips, skip optional steps |
| Integration with all systems difficult | High       | High   | Thorough testing, staged rollout                          |
| Form validation edge cases             | Medium     | Medium | Comprehensive validation rules, clear error messages      |

---

## Acceptance Criteria Summary

### US-018: Initial Setup Wizard (Part 1)

**Core Wizard:**

- [ ] Wizard starts on fresh instance
- [ ] Step indicator shows progress (Step X of 7)
- [ ] Previous/Next navigation works

**Step 1: Domain Configuration**

- [ ] Primary domain input
- [ ] Subdomain prefix input
- [ ] DNS configuration guide shown
- [ ] Domain validation performed

**Step 2: Template Selection**

- [ ] All 9 templates shown
- [ ] Template preview modal
- [ ] Template selection saved

**Step 3: Design Tokens**

- [ ] Primary/secondary colours selectable
- [ ] Font selection (system or Google Fonts)
- [ ] Live preview of tokens
- [ ] Default tokens available

**Step 4: Admin User**

- [ ] Name, email, password inputs
- [ ] Password requirements shown
- [ ] 2FA setup option
- [ ] User created on completion

**Step 5: Environment Secrets**

- [ ] Common secret templates shown
- [ ] .env file import supported
- [ ] Secrets encrypted and stored

**Deferred to Sprint 22:**

- Verification checks
- Completion flow
- Success page

---

## Definition of Done

- [ ] All acceptance criteria met for US-018 (Part 1)
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass
- [ ] Code reviewed and merged
- [ ] Documentation complete
- [ ] Deployed to development
- [ ] QA tested
- [ ] Demo prepared

---

## Sprint Metrics

| Metric           | Target | Actual |
| ---------------- | ------ | ------ |
| Points Committed | 11     | -      |
| Points Completed | -      | -      |
| Wizard Steps     | 5      | -      |

---

_Last Updated: 06/01/2026_
_Sprint Owner: Development Team_
