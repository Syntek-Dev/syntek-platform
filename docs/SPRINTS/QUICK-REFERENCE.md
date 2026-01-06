# Sprint Planning Quick Reference

**Last Updated:** 06/01/2026

---

## Sprint Capacity Rules

| Metric                | Value     | Notes                                         |
| --------------------- | --------- | --------------------------------------------- |
| **Sprint Duration**   | 2 weeks   | Fixed across all sprints                      |
| **Maximum Points**    | 11 points | Hard limit per sprint                         |
| **Target Points**     | 10 points | Leave 1 point buffer for bugs/unexpected work |
| **Story Point Scale** | Fibonacci | 1, 2, 3, 5, 8, 13, 21                         |

---

## MoSCoW Balance Guidelines

| Priority        | Target % | Typical Allocation                    |
| --------------- | -------- | ------------------------------------- |
| **Must Have**   | 50-60%   | 6-7 points per sprint (if applicable) |
| **Should Have** | 20-30%   | 2-3 points per sprint (if applicable) |
| **Could Have**  | 10-20%   | 1-2 points per sprint (if applicable) |
| **Won't Have**  | 0%       | Excluded from sprints                 |

**Note:** Most sprints focus on a single priority level (all Must Have or all Should Have).

---

## Story Splitting Strategy

Stories exceeding 11 points are split across multiple sprints:

| Story                   | Total Points | Split Strategy                                                 |
| ----------------------- | ------------ | -------------------------------------------------------------- |
| US-005 (Design Tokens)  | 13           | Sprint 5 (11 pts) + Sprint 6 (2 pts)                           |
| US-006 (CMS Pages)      | 13           | Sprint 7 (11 pts) + Sprint 8 (2 pts)                           |
| US-008 (Templates)      | 13           | Sprint 12 (11 pts) + Sprint 13 (2 pts)                         |
| US-011 (GraphQL API)    | 13           | Sprint 2 (3 pts foundation) + integrated across future sprints |
| US-014 (Integrations)   | 13           | Sprint 16 (11 pts) + Sprint 17 (2 pts)                         |
| US-015 (AI Integration) | 13           | Sprint 24 (11 pts) + Sprint 25 (2 pts)                         |
| US-017 (SaaS Email)     | 21           | Sprint 18 (11 pts) + Sprint 19 (10 pts)                        |
| US-018 (Setup Wizard)   | 13           | Sprint 27 (11 pts) + Sprint 28 (2 pts)                         |
| US-019 (UI Library)     | 21           | Sprint 14 (11 pts) + Sprint 15 (10 pts)                        |
| US-020 (Deployment)     | 21           | Sprint 29 (11 pts) + Sprint 30 (10 pts)                        |
| US-021 (Cloud Docs)     | 13           | Sprint 20 (8 pts) + Sprint 21 (5 pts)                          |
| US-022 (Password Mgr)   | 13           | Sprint 22 (8 pts) + Sprint 23 (5 pts)                          |

**Splitting Pattern:**

- **Part 1:** Core functionality, models, basic UI (11 pts)
- **Part 2:** Polish, additional features, testing, documentation (remaining pts)

---

## Critical Path Dependencies

These stories block multiple downstream stories - prioritise completion:

| Story                           | Blocks                         | Sprint | Critical Date                |
| ------------------------------- | ------------------------------ | ------ | ---------------------------- |
| **US-001: User Authentication** | US-002, US-003, US-004         | 1      | 20/01/2026                   |
| **US-011: GraphQL API**         | All future API features        | 2      | 27/01/2026 (week 1 deadline) |
| **US-004: Organisation**        | US-005, US-006, US-008, US-009 | 3      | 17/02/2026                   |
| **US-005: Design Tokens**       | US-006, US-008, US-019         | 5-6    | 31/03/2026                   |
| **US-006: CMS Pages**           | US-007, US-009, US-010         | 7-8    | 28/04/2026                   |

**Action:** Monitor these stories closely. If delayed, all dependent sprints shift.

---

## Phase Milestones

| Phase                         | Sprints | Completion Date | Key Deliverable                            |
| ----------------------------- | ------- | --------------- | ------------------------------------------ |
| **Phase 1: Core Foundation**  | 1-4     | 03/03/2026      | Authentication, GraphQL API, Audit Logging |
| **Phase 2: Design & Content** | 5-13    | 07/07/2026      | CMS, Templates, Media Library, Publication |
| **Phase 3: UI Library**       | 14-15   | 04/08/2026      | 30+ reusable components, Storybook         |
| **Phase 4: Integrations**     | 16-17   | 01/09/2026      | Third-party integration framework          |
| **Phase 5: SaaS Products**    | 18-23   | 24/11/2026      | Email, Cloud Docs, Password Manager        |
| **Phase 6: AI & Automation**  | 24-26   | 05/01/2027      | Claude AI, Environment Secrets             |
| **Phase 7: Deployment**       | 27-30   | 02/03/2027      | Setup wizard, CI/CD pipeline               |

**Review Points:**

- End of Phase 1: Architecture review
- End of Phase 2: User acceptance testing
- End of Phase 3: Component library release
- End of Phase 4: Integration framework testing
- End of Phase 5: SaaS products user testing
- End of Phase 6: AI integration and security audit
- End of Phase 7: Production deployment readiness

---

## Sprint Ceremonies

### Sprint Planning (First Monday of Sprint)

- **Duration:** 2 hours
- **Attendees:** Full team
- **Agenda:**
  1. Review sprint goal
  2. Review stories and acceptance criteria
  3. Break stories into tasks
  4. Assign tasks to team members
  5. Confirm sprint commitment

### Daily Standup

- **Duration:** 15 minutes
- **Time:** 10:00 AM Europe/London
- **Format:**
  - What I completed yesterday
  - What I'm working on today
  - Any blockers

### Sprint Review (Last Friday of Sprint)

- **Duration:** 1 hour
- **Attendees:** Full team + stakeholders
- **Agenda:**
  1. Demo completed stories
  2. Review acceptance criteria
  3. Gather feedback
  4. Discuss incomplete work

### Sprint Retrospective (Last Friday of Sprint)

- **Duration:** 1 hour
- **Attendees:** Full team
- **Agenda:**
  1. What went well
  2. What could improve
  3. Action items for next sprint

---

## Definition of Done Checklist

Use this for every story:

- [ ] All acceptance criteria met
- [ ] Unit tests written and passing (>80% coverage)
- [ ] Integration tests written and passing
- [ ] Code reviewed and approved
- [ ] Documentation updated (API docs, README)
- [ ] Deployed to development environment
- [ ] QA tested on dev environment
- [ ] No critical bugs
- [ ] Demo prepared for sprint review

---

## Repository Activity Per Sprint

| Sprint | Backend | Frontend Web | Frontend Mobile | Shared UI |
| ------ | ------- | ------------ | --------------- | --------- |
| 1      | ✅      | ✅           | ✅              | ✅        |
| 2      | ✅      | ✅           | ✅              | ✅        |
| 3      | ✅      | ✅           | ❌              | ✅        |
| 4      | ✅      | ✅           | ❌              | ✅        |
| 5-6    | ✅      | ✅           | ✅              | ✅        |
| 7-8    | ✅      | ✅           | ❌              | ✅        |
| 9      | ✅      | ✅           | ✅              | ✅        |
| 10     | ✅      | ✅           | ✅              | ✅        |
| 11     | ✅      | ✅           | ✅              | ✅        |
| 12-13  | ✅      | ✅           | ❌              | ✅        |
| 14-15  | ❌      | ❌           | ❌              | ✅        |
| 16-17  | ✅      | ✅           | ❌              | ✅        |
| 18-19  | ✅      | ✅           | ✅              | ✅        |
| 20-21  | ✅      | ✅           | ✅              | ✅        |
| 22-23  | ✅      | ✅           | ✅              | ✅        |
| 24-25  | ✅      | ✅           | ✅              | ✅        |
| 26     | ✅      | ✅           | ❌              | ✅        |
| 27-28  | ✅      | ✅           | ❌              | ✅        |
| 29-30  | ✅      | ✅           | ✅              | ✅        |

---

## Velocity Tracking Template

Update after each sprint:

```markdown
| Sprint | Planned | Completed | Variance | Notes   |
| ------ | ------- | --------- | -------- | ------- |
| 1      | 10      | X         | +/-X     | [Notes] |
| 2      | 11      | X         | +/-X     | [Notes] |
| 3      | 11      | X         | +/-X     | [Notes] |
```

**Calculate Rolling Average (Last 3 Sprints):**

```
Average Velocity = (Sprint N + Sprint N-1 + Sprint N-2) / 3
```

**Adjust future sprints** if rolling average differs significantly from planned capacity (±2 points).

---

## Risk Escalation

### When to Escalate

| Issue                               | Action                                                    |
| ----------------------------------- | --------------------------------------------------------- |
| **Blocker for >1 day**              | Notify team lead immediately                              |
| **Story at risk of not completing** | Raise in daily standup, consider moving to next sprint    |
| **Sprint capacity exceeded**        | Discuss in sprint planning, defer lowest priority story   |
| **Dependency delayed**              | Notify dependent sprint owners, adjust timeline           |
| **Velocity consistently low**       | Hold retrospective, identify bottlenecks, adjust capacity |

### Escalation Path

1. **Daily Standup** - Raise blockers and issues
2. **Team Lead** - For urgent blockers or cross-team dependencies
3. **Product Owner** - For scope changes or priority shifts
4. **Stakeholders** - For timeline impacts or major risks

---

## Common Sprint Patterns

### Pattern 1: Foundation Sprint (Sprints 1-4)

- Focus on infrastructure and core models
- All 4 repositories active
- High test coverage required
- Security review essential

### Pattern 2: Feature Sprint (Sprints 5-13)

- Build on foundation
- 2-3 repositories active
- UX/UI focus
- Integration with previous features

### Pattern 3: Polish Sprint (Sprints 6, 8, 13, 17, 25, 28)

- Low point allocation (2 pts)
- Focus on testing, documentation, performance
- Buffer for technical debt
- Opportunity for refactoring

### Pattern 4: Integration Sprint (Sprints 16-17, 24-26)

- External service integration
- Security-sensitive (credential management)
- Error handling and retry logic critical
- Thorough testing required

### Pattern 5: SaaS Product Sprint (Sprints 18-23)

- Large-scale integrations (OnlyOffice, Vaultwarden, SMTP)
- Multi-repository coordination
- Security-critical (encryption, authentication)
- Browser extension development (Sprint 22-23)

---

## Useful Commands

### Create New Sprint File

```bash
cp docs/SPRINTS/SPRINT-01-CORE-AUTHENTICATION.md docs/SPRINTS/SPRINT-XX-THEME.md
# Update sprint number, dates, stories, goals
```

### View All Sprint Files

```bash
ls -1 docs/SPRINTS/SPRINT-*.md
```

### Search Sprint Files

```bash
grep -r "US-XXX" docs/SPRINTS/
```

### Generate Sprint Report

```bash
# See README.md for sprint status
cat docs/SPRINTS/README.md
```

---

## Contact & Support

**Sprint Planning Questions:** Development Team Lead
**Story Clarification:** Product Owner
**Technical Blockers:** Tech Lead
**Cross-Team Dependencies:** Scrum Master

---

_Last Updated: 06/01/2026_
_Maintained By: Development Team_
