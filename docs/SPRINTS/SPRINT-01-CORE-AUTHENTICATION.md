# Sprint 1: Core Authentication

<!-- CLICKUP_LIST_ID: 901519464073 -->

**Sprint Duration:** 06/01/2026 - 20/01/2026 (2 weeks)
**Capacity:** 10/11 points
**Status:** Planned

---

## Sprint Goal

Establish the foundational authentication system enabling users to register, verify their email,
and reset forgotten passwords. This sprint creates the core user management infrastructure
required for all subsequent features.

---

## MoSCoW Breakdown

### Must Have (10 points)

| Story ID                                           | Title               | Points | Status  |
| -------------------------------------------------- | ------------------- | ------ | ------- |
| [US-001](../STORIES/US-001-USER-AUTHENTICATION.md) | User Authentication | 5      | Pending |
| [US-003](../STORIES/US-003-PASSWORD-RESET.md)      | Password Reset      | 5      | Pending |

### Should Have (0 points)

_None in this sprint_

### Could Have (0 points)

_None in this sprint_

---

## Dependencies

| Story  | Depends On | Notes                                                     |
| ------ | ---------- | --------------------------------------------------------- |
| US-001 | None       | Foundation story - no dependencies                        |
| US-003 | US-001     | Requires User model and authentication system from US-001 |

**Dependency Order:**

1. **US-001** must be completed first (creates User model, email verification)
2. **US-003** builds on US-001 (password reset for existing users)

---

## Implementation Order

### Week 1 (06/01 - 13/01)

1. **US-001: User Authentication (Priority 1)**
   - Backend: User model, email verification, GraphQL mutations
   - Frontend Web: Registration form, verification page
   - Shared UI: Form input components, validation components
   - Mobile: Registration form

**Milestone:** Users can register and verify their email address

### Week 2 (13/01 - 20/01)

2. **US-003: Password Reset (Priority 2)**
   - Backend: Password reset tokens, email templates
   - Frontend Web: Forgot password form, reset page
   - Shared UI: Password strength indicator
   - Mobile: Password reset flow

**Milestone:** Users can reset forgotten passwords via email

---

## Repository Breakdown

| Story  | Backend | Frontend Web | Frontend Mobile | Shared UI |
| ------ | ------- | ------------ | --------------- | --------- |
| US-001 | ✅      | ✅           | ✅              | ✅        |
| US-003 | ✅      | ✅           | ✅              | ✅        |

**All 4 repositories** will be active this sprint.

---

## Technical Focus

### Backend

- Django User model with email verification
- GraphQL mutations for registration and password reset
- Email service configuration (Mailpit for dev)
- Password validators and security
- Token generation for email verification and password reset

### Frontend Web

- Registration form with real-time validation
- Email verification page
- Password reset request and completion forms
- Error handling and user feedback

### Frontend Mobile

- Registration form optimised for mobile
- Password reset flow
- Deep linking for email verification

### Shared UI

- FormInput component with validation
- Button component
- ValidationError component
- PasswordStrengthIndicator component
- AlertBox component

---

## Risks & Mitigations

| Risk                                 | Likelihood | Impact | Mitigation                                                |
| ------------------------------------ | ---------- | ------ | --------------------------------------------------------- |
| Email service configuration delays   | Medium     | High   | Use Mailpit for dev, document SMTP setup for staging/prod |
| Password validation complexity       | Low        | Medium | Use battle-tested django validators                       |
| Mobile deep linking for verification | Medium     | Medium | Start with web-only verification, add mobile in Sprint 2  |
| Cross-repository coordination        | High       | Medium | Daily standups, shared component library setup early      |
| GraphQL schema design decisions      | Medium     | High   | Design schema early in week 1, review with team           |

---

## Acceptance Criteria Summary

### US-001: User Authentication

- [ ] User can register with email and password
- [ ] Email verification link is sent
- [ ] Password must meet complexity requirements (12+ chars, upper, lower, number, special)
- [ ] Email verification activates account
- [ ] Duplicate email addresses are rejected with clear error
- [ ] All actions are audit-logged (for Sprint 4 integration)

### US-003: Password Reset

- [ ] User can request password reset via email
- [ ] Password reset link is valid for 24 hours
- [ ] New password cannot be one of last 5 passwords
- [ ] Password reset link can only be used once
- [ ] Multiple reset requests invalidate previous links
- [ ] Successful reset sends confirmation email

---

## Definition of Done

- [ ] All acceptance criteria met for US-001 and US-003
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass for email flows
- [ ] Code reviewed and merged to main
- [ ] Documentation updated (API docs, README)
- [ ] Deployed to development environment
- [ ] QA tested on dev environment
- [ ] Demo prepared for sprint review

---

## Sprint Metrics

| Metric            | Target | Actual |
| ----------------- | ------ | ------ |
| Points Committed  | 10     | -      |
| Points Completed  | -      | -      |
| Stories Completed | 2      | -      |
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

- This is the first sprint of the project - establish good development practices early
- Focus on code quality and testing from day one
- GraphQL schema design decisions made this sprint will affect all future work
- Email service setup is critical - ensure Mailpit works correctly in dev environment
- Cross-repository work requires careful coordination - consider pair programming for shared UI components

---

_Last Updated: 06/01/2026_
_Sprint Owner: Development Team_
