# Sprint 18: SaaS Email Service (Part 1)

<!-- CLICKUP_LIST_ID: 901519464142 -->

**Sprint Duration:** 01/09/2026 - 15/09/2026
**Capacity:** 11/11 points
**Status:** Planned

---

## Table of Contents

- [Sprint Goal](#sprint-goal)
- [MoSCoW Breakdown](#moscow-breakdown)
- [Dependencies](#dependencies)
- [Implementation Order](#implementation-order)
- [Repository Breakdown](#repository-breakdown)
- [Risks and Mitigations](#risks-and-mitigations)
- [Sprint Metrics](#sprint-metrics)
- [Retrospective Notes](#retrospective-notes)

---

## Sprint Goal

Implement the foundation of the SaaS email service including email account management, SMTP integration, inbox interface, and basic email composition. This sprint focuses on core email functionality with custom domain support and basic email operations.

---

## MoSCoW Breakdown

### Must Have (11 points)

| Story ID                                                   | Title                                    | Points | Status  |
| ---------------------------------------------------------- | ---------------------------------------- | ------ | ------- |
| [US-017](../STORIES/US-017-SAAS-EMAIL-SERVICE.md) (Part 1) | SaaS Email Service (Core Implementation) | 11     | Pending |

**Scope for Part 1:**

- Email account management and authentication
- SMTP server integration
- Email domain configuration (DNS setup, verification)
- Email inbox interface (view, list, folder management)
- Basic email composition and sending
- Email receiving and synchronisation
- Contact autocomplete foundation

### Should Have (0 points)

None for this sprint.

### Could Have (0 points)

None for this sprint.

---

## Dependencies

| Story           | Depends On                      | Notes                                      |
| --------------- | ------------------------------- | ------------------------------------------ |
| US-017 (Part 1) | US-004 (Organisation Setup)     | Organisation-scoped email domains          |
|                 | US-005 (Design Token System)    | Email template token integration           |
|                 | US-014 (Integrations Framework) | Email provider integration adapter pattern |

**Status:** All dependencies satisfied by Sprint 17.

---

## Implementation Order

Recommended order for development:

1. **Backend: Email Models** - Create EmailAccount, EmailMessage, EmailFolder, EmailDomain models
2. **Backend: SMTP Integration** - Implement SMTP service for sending and receiving emails
3. **Backend: Email Service** - Create email sending service and receiving/sync service
4. **Backend: Domain Verification** - Implement DNS configuration and domain verification
5. **Backend: GraphQL API** - Create queries/mutations for email operations
6. **Frontend Web: Email Application Layout** - Build the main email application structure
7. **Frontend Web: Inbox Component** - Create inbox with message list and folder navigation
8. **Frontend Web: Compose Window** - Build email compose interface with recipient input
9. **Frontend Web: Domain Setup Wizard** - Create domain configuration flow
10. **Shared UI: Email Components** - Build RichTextEditor, AttachmentList, MessageRenderer components

---

## Repository Breakdown

| Story ID        | Backend | Frontend Web | Frontend Mobile | Shared UI |
| --------------- | ------- | ------------ | --------------- | --------- |
| US-017 (Part 1) | ✅      | ✅           | ✅              | ✅        |

**Backend:** Email models, SMTP integration, GraphQL API, domain verification
**Frontend Web:** Email application, inbox, compose window, domain setup wizard
**Frontend Mobile:** Basic inbox view, message reading (defer compose to Part 2)
**Shared UI:** RichTextEditor, AttachmentList, MessageRenderer, ContactSelector (foundation)

---

## Risks and Mitigations

| Risk                                 | Likelihood | Impact | Mitigation                                             |
| ------------------------------------ | ---------- | ------ | ------------------------------------------------------ |
| SMTP provider integration complexity | Medium     | High   | Start with well-documented provider (Mailgun/SendGrid) |
| DNS verification delays              | Low        | Medium | Provide clear DNS setup guide and verification polling |
| Email storage volume                 | Medium     | Medium | Implement pagination and archive strategy early        |
| Rich text editor complexity          | Medium     | Medium | Use established library (TipTap, Quill)                |
| Spam filtering requirements          | Low        | Medium | Defer advanced spam filtering to Part 2                |

---

## Sprint Metrics (Post-Sprint)

_Fill in after sprint completion_

| Metric            | Planned | Actual |
| ----------------- | ------- | ------ |
| Points Committed  | 11      | -      |
| Points Completed  | -       | -      |
| Stories Completed | 1       | -      |
| Velocity          | -       | -      |

---

## Retrospective Notes

_Fill in after sprint completion_

- **What went well:**
- **What could improve:**
- **Action items:**

---

_Last Updated: 06/01/2026_
_Document Owner: Development Team_
