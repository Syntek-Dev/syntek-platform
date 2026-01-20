# Sprint 4: Audit Logging & Security

<!-- CLICKUP_LIST_ID: 901519464092 -->

**Sprint Duration:** 17/02/2026 - 03/03/2026 (2 weeks)
**Capacity:** 8/11 points (buffer available)
**Status:** Planned

---

## Overview

This sprint implements comprehensive audit logging with IP encryption and completes remaining caching strategies from Sprint 3. The single user story **US-012 (Audit Logging System)** creates an automated logging framework that tracks all CRUD operations, authentication events, and GraphQL queries with encrypted IP storage. Administrators gain visibility through filterable audit log viewers with change comparison and export capabilities. The 3-point buffer provides flexibility for security hardening, performance optimisation of caching strategies from Sprint 3, and technical debt. Critical security focus: IP encryption keys must be securely stored, sensitive data (passwords, tokens) must be excluded from logs, and log retention policies must align with compliance requirements.

---

## Sprint Goal

Implement comprehensive audit logging system with IP encryption and complete remaining caching
strategies. This sprint establishes security compliance, traceability, and performance
optimisation infrastructure.

---

## MoSCoW Breakdown

### Must Have (8 points)

| Story ID                                     | Title                | Points | Status  |
| -------------------------------------------- | -------------------- | ------ | ------- |
| [US-012](../STORIES/US-012-AUDIT-LOGGING.md) | Audit Logging System | 8      | Pending |

### Should Have (0 points)

_None in this sprint_

### Could Have (0 points)

_None in this sprint_

---

## Dependencies

| Story  | Depends On             | Notes                                                       |
| ------ | ---------------------- | ----------------------------------------------------------- |
| US-012 | US-001, US-004, US-011 | Logs user actions, organisation operations, GraphQL queries |

**All dependencies satisfied:** Sprints 1-3 have completed the required foundation.

---

## Implementation Order

### Week 1 (17/02 - 24/02)

1. **US-012: Audit Logging (Priority 1)**
   - Backend: AuditLog model with encrypted IP storage
   - Backend: IP encryption/decryption service (Fernet)
   - Backend: Django middleware for automatic logging
   - Backend: GraphQL query logging middleware
   - Backend: Signal handlers for CRUD events

**Milestone:** All user actions and system changes are audit-logged

### Week 2 (24/02 - 03/03)

2. **US-012: Audit Logging UI & Export (Priority 2)**
   - Frontend Web: Audit log viewer, filtering, search
   - Frontend Web: Change comparison view (old vs new values)
   - Backend: Export service (CSV, JSON)
   - Shared UI: Table component, filter panel

**Milestone:** Administrators can view, search, and export audit logs

---

## Repository Breakdown

| Story  | Backend | Frontend Web | Frontend Mobile | Shared UI |
| ------ | ------- | ------------ | --------------- | --------- |
| US-012 | ✅      | ✅           | ❌              | ✅        |

**Note:** Mobile not applicable - audit logs are admin-only feature accessed via web.

---

## Technical Focus

### Backend

- **Audit Logging:** Automatic logging of all CRUD operations
- **IP Encryption:** Fernet encryption for IP address storage
- **GraphQL Logging:** Query execution time, response size, errors
- **Export:** CSV and JSON export with filters applied
- **Performance:** Indexing on frequently queried fields (user_id, action, timestamp)

### Frontend Web

- **Audit Viewer:** Paginated log display with expandable details
- **Filtering:** By user, action, resource type, date range
- **Search:** Full-text search across log entries
- **Export:** Download filtered logs as CSV or JSON

### Shared UI

- Table component, FilterPanel, DateRangeSelector, ExpandableRow components

---

## Risks & Mitigations

| Risk                                      | Likelihood | Impact | Mitigation                                                   |
| ----------------------------------------- | ---------- | ------ | ------------------------------------------------------------ |
| Audit log database growth                 | High       | Medium | Implement archival strategy (90-day retention, then archive) |
| IP encryption performance overhead        | Medium     | Low    | Cache decrypted IPs in session for admins                    |
| Sensitive data in logs                    | Medium     | High   | Sanitise passwords, API keys, tokens from logs               |
| Log query performance with large datasets | High       | High   | Index timestamp, user_id, action fields                      |
| Export memory issues with large datasets  | Medium     | Medium | Implement streaming export for large datasets                |

---

## Acceptance Criteria Summary

### US-012: Audit Logging System

- [ ] All authentication events are logged (login, logout, failed login)
- [ ] All CRUD operations are logged with old/new values
- [ ] IP addresses are encrypted before storage (Fernet)
- [ ] Only security role can decrypt IP addresses
- [ ] IP viewing is logged as a security event
- [ ] GraphQL queries are logged with execution time and errors
- [ ] Administrators can view audit logs with pagination
- [ ] Filtering works by user, action, resource type, date range
- [ ] Search returns relevant results quickly (<500ms)
- [ ] Export to CSV and JSON works correctly
- [ ] Change comparison shows old vs new values side-by-side
- [ ] Sensitive data (passwords, tokens) is never logged

---

## Definition of Done

- [ ] All acceptance criteria met for US-012
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass for audit trail workflows
- [ ] Performance tests confirm log queries are fast (<500ms)
- [ ] Security review confirms IP encryption is secure
- [ ] Code reviewed and merged to main
- [ ] Documentation updated (audit logging design, IP encryption strategy)
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
| Log Query Speed   | <500ms | -      |

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

- **SECURITY:** IP encryption key must be stored securely (environment variable, never in code)
- Audit log retention policy should be documented and agreed with stakeholders
- Consider implementing log rotation and archival to prevent database growth
- Sensitive fields (password, API keys) must be excluded from change tracking
- Log query performance is critical - test with large datasets (100k+ entries)
- Export functionality should support streaming for large datasets to avoid memory issues
- Consider adding audit log monitoring/alerting for suspicious activity patterns
- IP decryption should be logged with admin ID for compliance tracking

**Buffer Allocation:** This sprint has 3 points of buffer (8/11 used). Use this for:

- Additional testing and security hardening
- Documentation improvements
- Technical debt from Sprints 1-3
- Performance optimisation for caching strategies

---

_Last Updated: 06/01/2026_
_Sprint Owner: Development Team_
