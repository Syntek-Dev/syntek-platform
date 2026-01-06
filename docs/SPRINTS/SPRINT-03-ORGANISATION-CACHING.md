# Sprint 3: Organisation & Caching Infrastructure

<!-- CLICKUP_LIST_ID: 901519464091 -->

**Sprint Duration:** 03/02/2026 - 17/02/2026 (2 weeks)
**Capacity:** 11/11 points (at capacity)
**Status:** Planned

---

## Sprint Goal

Implement organisation-based multi-tenancy with team management and establish Redis/Valkey caching system for performance optimisation. This sprint creates the organisational structure that isolates customer data and implements caching to support future scalability.

---

## MoSCoW Breakdown

### Must Have (11 points)

| Story ID                                          | Title                   | Points | Status  |
| ------------------------------------------------- | ----------------------- | ------ | ------- |
| [US-004](../STORIES/US-004-ORGANISATION-SETUP.md) | Organisation Setup      | 8      | Pending |
| [US-013](../STORIES/US-013-CACHING-SYSTEM.md)     | Caching System (Part 1) | 3\*    | Pending |

_US-013 split: 3 points for Redis setup and basic caching this sprint, remaining 5 points integrated across Sprints 4-6 as cache strategies evolve_

### Should Have (0 points)

_None in this sprint_

### Could Have (0 points)

_None in this sprint_

---

## Dependencies

| Story  | Depends On | Notes                                                       |
| ------ | ---------- | ----------------------------------------------------------- |
| US-004 | US-001     | Requires User model for organisation ownership              |
| US-013 | US-004     | Caching keys use organisation ID for multi-tenant isolation |

**Implementation Order:**

1. **US-004** must be completed first (creates Organisation model)
2. **US-013** implements org-based cache isolation

---

## Implementation Order

### Week 1 (03/02 - 10/02)

1. **US-004: Organisation Setup (Priority 1)**
   - Backend: Organisation model, Team model, TeamInvitation model
   - Backend: Multi-tenancy middleware for GraphQL
   - Backend: Subscription tracking (free/starter/professional/enterprise)
   - Frontend Web: Organisation setup wizard, team management UI
   - Shared UI: Form components, user invitation components

**Milestone:** Users can create organisations and invite team members

### Week 2 (10/02 - 17/02)

2. **US-013: Caching System Foundation (Priority 2)**
   - Backend: Redis/Valkey setup in Docker
   - Backend: django-redis integration
   - Backend: TenantCache wrapper with org-based key prefixing
   - Backend: Session storage in Redis
   - Backend: Cache health check endpoint

**Milestone:** Redis is active with multi-tenant cache isolation

---

## Repository Breakdown

| Story  | Backend | Frontend Web | Frontend Mobile | Shared UI |
| ------ | ------- | ------------ | --------------- | --------- |
| US-004 | ✅      | ✅           | ❌              | ✅        |
| US-013 | ✅      | ✅           | ✅              | ❌        |

**Note:** Mobile support for US-004 is deferred (not applicable for Phase 1 - web-only organisation setup)

---

## Technical Focus

### Backend

- **Multi-Tenancy:** Organisation model, data filtering middleware, cache isolation
- **Invitations:** Email-based team invitations with 7-day expiry
- **Caching:** Redis setup, cache key prefixing (`org:{id}:*`), session storage
- **GraphQL:** Organisation queries and mutations with multi-tenant filtering

### Frontend Web

- **Organisation Wizard:** Multi-step form for organisation creation
- **Team Management:** Team member list, invitation UI, role assignment
- **Domain Setup:** Subdomain and custom domain configuration

### Shared UI

- FormInput, SlugGenerator, DomainInput, UserInvitationForm components

### DevOps

- Docker Compose configuration for Redis (4 databases: cache, sessions, Celery broker, Celery results)
- Redis persistence (AOF) and memory limits

---

## Risks & Mitigations

| Risk                                       | Likelihood | Impact | Mitigation                                                   |
| ------------------------------------------ | ---------- | ------ | ------------------------------------------------------------ |
| Multi-tenancy data leakage                 | Low        | High   | Comprehensive testing, middleware validation, audit logging  |
| Cache key collisions between organisations | Medium     | High   | Strict key prefixing: `org:{id}:resource:identifier`         |
| Redis memory exhaustion                    | Medium     | Medium | Set eviction policy (LRU), monitor memory usage              |
| Domain DNS verification complexity         | High       | Medium | Start with subdomain support only, defer custom domains      |
| Team invitation email delivery failures    | Medium     | Medium | Queue emails via Celery, retry failed deliveries             |
| Organisation slug conflicts                | Low        | Low    | Auto-generate unique slugs with suffix if collision detected |

---

## Acceptance Criteria Summary

### US-004: Organisation Setup

- [ ] Users can create an organisation during or after registration
- [ ] Organisation slug is auto-generated and unique
- [ ] User becomes organisation owner on creation
- [ ] Team members can be invited via email
- [ ] Invitation emails include 7-day expiry
- [ ] Team members can accept/decline invitations
- [ ] Roles are assigned (Admin/Editor/Viewer)
- [ ] Subdomain setup works (orgslug.domain.com)
- [ ] Multi-tenancy filtering is automatic in all GraphQL queries
- [ ] Cross-organisation data access returns errors (not exposed data)
- [ ] Custom domain DNS verification is documented (deferred to future sprint)

### US-013: Caching System

- [ ] Redis/Valkey is running in Docker
- [ ] 4 Redis databases are configured (cache, sessions, broker, results)
- [ ] Cache keys use org-based prefixing: `org:{id}:*`
- [ ] Session storage uses Redis (24-hour TTL)
- [ ] Multi-tenant cache isolation is enforced
- [ ] Cache health check endpoint returns status
- [ ] Memory limits and eviction policy are configured
- [ ] Cache hit/miss is logged for monitoring

---

## Definition of Done

- [ ] All acceptance criteria met for US-004 and US-013
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass for multi-tenancy isolation
- [ ] Security tests confirm no cross-org data leakage
- [ ] Code reviewed and merged to main
- [ ] Documentation updated (multi-tenancy design, caching strategy)
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
| Cache Hit Rate    | >60%   | -      |

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

- **SECURITY:** Multi-tenancy isolation is critical - all queries MUST filter by organisation ID
- Test cross-organisation access thoroughly to ensure no data leakage
- Redis configuration should match production environment requirements
- Consider implementing CAPTCHA on team invitation acceptance to prevent spam
- Document cache key naming conventions for consistency across all future features
- Organisation slug generation should handle edge cases (profanity filter, reserved words)
- Custom domain setup can be deferred to future sprint - start with subdomain support only

---

_Last Updated: 06/01/2026_
_Sprint Owner: Development Team_
