# Sprint 2: User Management & GraphQL API

<!-- CLICKUP_LIST_ID: 901519464085 -->

**Sprint Duration:** 20/01/2026 - 03/02/2026 (2 weeks)
**Capacity:** 11/11 points (at capacity)
**Status:** Planned

---

## Sprint Goal

Implement two-factor authentication (2FA) for secure login and establish the GraphQL API
infrastructure with query depth limiting, complexity analysis, and authentication middleware.
This sprint creates critical security features and the API foundation that all future features
will depend on.

---

## MoSCoW Breakdown

### Must Have (11 points)

| Story ID                                      | Title                | Points | Status  |
| --------------------------------------------- | -------------------- | ------ | ------- |
| [US-002](../STORIES/US-002-LOGIN-WITH-2FA.md) | Login with 2FA       | 8      | Pending |
| [US-011](../STORIES/US-011-GRAPHQL-API.md)    | GraphQL API (Part 1) | 3\*    | Pending |

_US-011 split: 3 points for foundation setup this sprint, remaining work spreads across future sprints as features are added_

### Should Have (0 points)

_None in this sprint_

### Could Have (0 points)

_None in this sprint_

---

## Dependencies

| Story  | Depends On | Notes                                             |
| ------ | ---------- | ------------------------------------------------- |
| US-002 | US-001     | Requires User model from Sprint 1                 |
| US-011 | None       | Foundation work - enables all future API features |

**Critical Path:** US-011 (GraphQL API) is a blocker for many future stories - must be completed this sprint.

---

## Implementation Order

### Week 1 (20/01 - 27/01)

1. **US-011: GraphQL API Foundation (Priority 1 - CRITICAL)**
   - Strawberry GraphQL framework setup
   - Query depth limiting middleware
   - Query complexity calculation
   - Authentication decorator for resolvers
   - Base Query and Mutation types
   - Pagination helpers
   - Error handling

**Milestone:** GraphQL endpoint is live with authentication and query limiting

### Week 2 (27/01 - 03/02)

2. **US-002: Login with 2FA (Priority 2)**
   - Backend: django-otp setup, TOTP verification, backup codes
   - Backend: Account lockout mechanism (5 attempts in 15 min)
   - Backend: JWT token generation and refresh
   - Frontend Web: 2FA setup wizard, 2FA code entry (6-digit OTP)
   - Frontend Mobile: Biometric integration (Face ID/Touch ID)
   - Shared UI: OTP input component

**Milestone:** Users can enable 2FA and log in securely

---

## Repository Breakdown

| Story  | Backend | Frontend Web | Frontend Mobile | Shared UI |
| ------ | ------- | ------------ | --------------- | --------- |
| US-002 | ✅      | ✅           | ✅              | ✅        |
| US-011 | ✅      | ✅           | ✅              | ❌        |

**4 repositories** active for US-002, **3 repositories** for US-011.

---

## Technical Focus

### Backend

- **GraphQL:** Strawberry framework, schema definition, resolvers
- **Authentication:** JWT tokens, refresh mechanism, 2FA verification
- **Security:** Query depth/complexity limits, rate limiting, account lockout
- **TOTP:** django-otp integration, secret generation, backup codes

### Frontend Web

- **GraphQL Client:** Apollo Client setup, authentication middleware
- **2FA UI:** Setup wizard, QR code display, backup code download, OTP input
- **Token Management:** JWT storage, refresh, expiry handling

### Frontend Mobile

- **GraphQL Client:** Apollo Client for React Native
- **Biometric Auth:** Face ID/Touch ID integration
- **2FA UI:** Mobile-optimised OTP entry

### Shared UI

- OTPInput component (6-digit, auto-focus, auto-submit)
- TogglePassword component
- AlertBox for security messages

---

## Risks & Mitigations

| Risk                                          | Likelihood | Impact | Mitigation                                                      |
| --------------------------------------------- | ---------- | ------ | --------------------------------------------------------------- |
| GraphQL complexity calculation overhead       | Medium     | High   | Test performance early, use caching for complexity scores       |
| 2FA QR code generation issues                 | Low        | Medium | Use battle-tested library (pyqrcode)                            |
| Biometric authentication platform differences | High       | Medium | Start with iOS Face ID, add Android later if time constrained   |
| JWT refresh token security                    | Medium     | High   | Use short-lived access tokens (15 min), longer refresh (7 days) |
| Account lockout DoS potential                 | Medium     | High   | Implement progressive lockout, CAPTCHA after 3 failed attempts  |
| GraphQL API becomes blocker for future work   | High       | High   | **PRIORITY:** Complete US-011 by end of week 1                  |

---

## Acceptance Criteria Summary

### US-002: Login with 2FA

- [ ] Users can enable 2FA via setup wizard
- [ ] QR code is displayed for authenticator app setup
- [ ] 8 single-use backup codes are generated and downloadable
- [ ] TOTP codes are validated with 30-second window
- [ ] Invalid 2FA attempts are rate-limited (3 attempts per minute)
- [ ] Account locks after 5 failed password attempts in 15 minutes
- [ ] JWT tokens are issued on successful authentication
- [ ] Token refresh works correctly
- [ ] Biometric authentication works on iOS (minimum)
- [ ] Login events are audit-logged (integration with Sprint 4)

### US-011: GraphQL API

- [ ] GraphQL endpoint is available at /graphql
- [ ] Query depth limit enforced (max 10 levels)
- [ ] Query complexity limit enforced (max 1000 points)
- [ ] Authentication works via JWT in Authorization header
- [ ] Multi-tenancy filtering is automatic (organisation-based)
- [ ] Cursor-based pagination is implemented
- [ ] Error handling returns consistent error format
- [ ] API documentation is available (introspection query)
- [ ] Subscription support via WebSocket is configured
- [ ] Rate limiting per user is active

---

## Definition of Done

- [ ] All acceptance criteria met for US-002 and US-011
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass for 2FA flow and GraphQL API
- [ ] Load tests pass for GraphQL complexity limits
- [ ] Security review completed for JWT and 2FA implementation
- [ ] Code reviewed and merged to main
- [ ] API documentation published
- [ ] Deployed to development environment
- [ ] QA tested on dev environment
- [ ] Demo prepared for sprint review

---

## Sprint Metrics

| Metric            | Target | Actual |
| ----------------- | ------ | ------ |
| Points Committed  | 11     | -      |
| Points Completed  | -      | -      |
| Stories Completed | 2      | -      |
| Velocity          | -      | -      |
| Test Coverage     | >80%   | -      |
| API Endpoints     | 5+     | -      |

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

- **CRITICAL:** US-011 (GraphQL API) must be completed by end of week 1 to avoid blocking future sprints
- 2FA implementation should follow industry best practices (OWASP guidelines)
- Backup codes must be stored hashed (bcrypt) - never in plain text
- Consider implementing CAPTCHA after 3 failed login attempts to prevent brute force
- GraphQL schema design decisions impact all future API work - involve full team in design review
- JWT secret rotation strategy should be documented
- Mobile biometric auth can be deferred to Sprint 3 if time is constrained

---

_Last Updated: 06/01/2026_
_Sprint Owner: Development Team_
