# Sprint 28: Initial Setup Wizard (Part 2)

<!-- CLICKUP_LIST_ID: 901519464183 -->

**Sprint Duration:** 19/01/2027 - 02/02/2027 (2 weeks)
**Capacity:** 2/11 points (9 points buffer)
**Status:** Planned

---

## Sprint Goal

Complete the setup wizard by implementing verification checks, completion flow, and success page with next steps.

---

## MoSCoW Breakdown

### Must Have (2 points)

| Story ID                                            | Title                 | Points | Status  |
| --------------------------------------------------- | --------------------- | ------ | ------- |
| [US-018](../STORIES/US-018-INITIAL-SETUP-WIZARD.md) | Setup Wizard (Part 2) | 2      | Pending |

---

## Dependencies

| Story  | Depends On | Notes                       |
| ------ | ---------- | --------------------------- |
| US-018 | Sprint 21  | Core wizard steps completed |

**Dependencies satisfied:** US-018 Part 1 completed in Sprint 21.

---

## Implementation Order

### Week 1 (27/10 - 03/11)

1. **Verification and Completion (Priority 1)**
   - Backend: Health check service
   - Backend: Database connectivity check
   - Backend: Redis connectivity check
   - Backend: Email service check
   - Backend: DNS verification check
   - Backend: Template initialisation trigger
   - Frontend Web: VerificationStep component
   - Frontend Web: Health check display

**Milestone:** Verification checks operational

### Week 2 (03/11 - 10/11)

2. **Success and Polish (Priority 2)**
   - Frontend Web: CompletionStep component
   - Frontend Web: SetupChecklist component
   - Frontend Web: Success page with next steps
   - Backend: Wizard completion logic
   - Documentation: Setup wizard guide
   - Testing: Complete wizard flow tests

**Milestone:** Setup wizard complete and polished

---

## Acceptance Criteria Summary

### US-018: Initial Setup Wizard (Part 2)

**Step 6: Verification**

- [ ] Database connectivity checked
- [ ] Redis connectivity checked
- [ ] Email service checked
- [ ] DNS configuration checked
- [ ] Green checkmarks show status
- [ ] Retry option available

**Step 7: Completion**

- [ ] Template initialised with default content
- [ ] Design tokens applied
- [ ] Admin user created
- [ ] Secrets stored
- [ ] Success page shows next steps
- [ ] Wizard marked complete

**Post-Setup:**

- [ ] Setup checklist available in dashboard
- [ ] Wizard doesn't reappear after completion
- [ ] Resume incomplete setup supported

**Completed from Sprint 21:**

- ✅ 5 core wizard steps operational
- ✅ Form validation working
- ✅ Progress tracking functional

---

## Definition of Done

- [ ] All acceptance criteria met for US-018 (Part 2)
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
| Points Committed | 2      | -      |
| Points Completed | -      | -      |
| Buffer Used      | 0 pts  | -      |

---

_Last Updated: 06/01/2026_
_Sprint Owner: Development Team_
