# Sprint 29: Automated Deployment Pipeline (Part 1)

<!-- CLICKUP_LIST_ID: 901519464184 -->

**Sprint Duration:** 02/02/2027 - 16/02/2027 (2 weeks)
**Capacity:** 11/11 points (at capacity)
**Status:** Planned

---

## Overview

This sprint establishes the automated CI/CD pipeline using GitHub Actions for continuous integration and deployment. It covers the foundational infrastructure for testing, building Docker images, and deploying the backend and frontend web applications to staging environments. This is the first of two sprints for the deployment pipeline, focusing on CI/CD setup, automated testing on pull requests, backend Docker containerisation, database migration automation, and web frontend deployment. Part 2 (Sprint 30) will handle mobile app deployment, blue-green deployments, and advanced rollback features.

---

## Sprint Goal

Implement automated CI/CD pipeline with GitHub Actions for testing, building, and deploying
backend and frontend web applications with database migrations and health checks.

---

## MoSCoW Breakdown

### Must Have (11 points)

| Story ID                                           | Title                        | Points | Status  |
| -------------------------------------------------- | ---------------------------- | ------ | ------- |
| [US-020](../STORIES/US-020-DEPLOYMENT-PIPELINE.md) | Deployment Pipeline (Part 1) | 11     | Pending |

_US-020 split: 11 points for CI/CD setup, backend deployment, and web deployment this sprint,
10 points for mobile deployment and advanced features in Sprint 24_

---

## Dependencies

| Story  | Depends On             | Notes                                         |
| ------ | ---------------------- | --------------------------------------------- |
| US-020 | US-016, US-012, US-013 | Secrets, audit logging, and caching completed |

**Dependencies satisfied:** Secrets (Sprint 20), audit logging (Sprint 4), and caching (Sprint 3) are complete.

---

## Implementation Order

### Week 1 (10/11 - 17/11)

1. **CI/CD Setup and Testing (Priority 1)**
   - GitHub Actions: PR check workflow
   - GitHub Actions: Test workflow (unit, integration, linting)
   - GitHub Actions: Code coverage workflow
   - GitHub Actions: Type checking workflow
   - Backend: Dockerfile for production
   - Backend: docker-compose for production
   - Backend: Database backup script
   - Backend: Migration runner script

**Milestone:** Automated testing on all PRs

### Week 2 (17/11 - 24/11)

2. **Deployment Workflows (Priority 2)**
   - GitHub Actions: Staging deployment workflow
   - GitHub Actions: Production deployment workflow (manual trigger)
   - Backend: Health check endpoint
   - Backend: Deployment logging
   - Frontend Web: Build script
   - Frontend Web: Static site deployment
   - GitHub Actions: Docker build and push
   - GitHub Actions: Secret injection
   - Testing: Deployment pipeline tests

**Milestone:** Backend and web deployed to staging automatically

---

## Repository Breakdown

| Story  | Backend | Frontend Web | Frontend Mobile | Shared UI |
| ------ | ------- | ------------ | --------------- | --------- |
| US-020 | ✅      | ✅           | ❌              | ✅        |

**3 repositories** will be active this sprint (Frontend Mobile in Sprint 24).

---

## Technical Focus

### CI/CD

- **GitHub Actions:** Automated testing and deployment
- **Docker:** Containerised deployments
- **Secret Management:** Inject secrets during deployment
- **Testing:** Run full test suite on PRs

### Backend

- **Docker:** Production-ready containers
- **Migrations:** Automated database migrations
- **Health Checks:** Verify deployment success
- **Rollback:** Capability to revert deployments

### Frontend Web

- **Build:** Optimised production builds
- **Deployment:** Static site deployment (Vercel, Netlify, or S3)
- **CDN:** Cache invalidation

---

## Risks & Mitigations

| Risk                        | Likelihood | Impact | Mitigation                                          |
| --------------------------- | ---------- | ------ | --------------------------------------------------- |
| GitHub Actions complexity   | Medium     | High   | Use established workflow templates, test thoroughly |
| Database migration failures | Medium     | High   | Always backup before migrations, test in staging    |
| Docker build times slow     | Medium     | Medium | Use layer caching, multi-stage builds               |
| Secret injection security   | Medium     | High   | Use GitHub encrypted secrets, rotate regularly      |

---

## Acceptance Criteria Summary

### US-020: Deployment Pipeline (Part 1)

**CI/CD:**

- [ ] PR checks run automatically
- [ ] Unit tests run on all PRs
- [ ] Integration tests run on all PRs
- [ ] Linting checks run on all PRs
- [ ] Type checking runs on all PRs
- [ ] Code coverage tracked (>80%)

**Backend Deployment:**

- [ ] Docker image built and pushed
- [ ] Database migrations run automatically
- [ ] Health checks verify deployment
- [ ] Staging deployed on merge to main
- [ ] Production deployed manually with approval

**Frontend Web Deployment:**

- [ ] Build process optimised
- [ ] Static site deployed
- [ ] CDN cache invalidated
- [ ] Health checks verify URLs respond

**Deferred to Sprint 24:**

- Mobile app deployment (iOS/Android)
- Blue-green deployments
- Automatic rollback
- Advanced monitoring

---

## Definition of Done

- [ ] All acceptance criteria met for US-020 (Part 1)
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass
- [ ] Deployment workflows tested
- [ ] Code reviewed and merged
- [ ] Documentation complete
- [ ] CI/CD pipelines operational
- [ ] Demo prepared

---

## Sprint Metrics

| Metric           | Target | Actual |
| ---------------- | ------ | ------ |
| Points Committed | 11     | -      |
| Points Completed | -      | -      |
| Deployments      | 2      | -      |

---

_Last Updated: 06/01/2026_
_Sprint Owner: Development Team_
