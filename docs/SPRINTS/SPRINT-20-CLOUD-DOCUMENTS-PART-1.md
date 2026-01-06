# Sprint 20: Cloud Documents Integration (Part 1)

<!-- CLICKUP_LIST_ID: 901519464158 -->

**Sprint Duration:** 29/09/2026 - 13/10/2026
**Capacity:** 8/11 points
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

Implement the foundation of the Cloud Documents application using OnlyOffice and S3/DO Spaces storage. This sprint focuses on OnlyOffice integration, document creation/editing, storage infrastructure, and basic document browser interface.

---

## MoSCoW Breakdown

### Must Have (8 points)

| Story ID                                                | Title                                 | Points | Status  |
| ------------------------------------------------------- | ------------------------------------- | ------ | ------- |
| [US-021](../STORIES/US-021-CLOUD-DOCUMENTS.md) (Part 1) | Cloud Documents (Core Implementation) | 8      | Pending |

**Scope for Part 1:**

- Document models (Document, DocumentVersion, DocumentFolder)
- OnlyOffice server integration
- S3/DO Spaces storage adapter
- Document creation (Text, Spreadsheet, Presentation)
- OnlyOffice editor interface
- Basic document browser UI
- Document upload and storage
- Auto-save functionality

### Should Have (0 points)

None for this sprint.

### Could Have (0 points)

None for this sprint (3 points buffer available for additional features or testing).

---

## Dependencies

| Story           | Depends On                      | Notes                                |
| --------------- | ------------------------------- | ------------------------------------ |
| US-021 (Part 1) | US-001 (User Authentication)    | User-based document ownership        |
|                 | US-004 (Organisation Setup)     | Organisation-scoped document storage |
|                 | US-005 (Design Token System)    | Custom branding in OnlyOffice        |
|                 | US-014 (Integrations Framework) | Integration adapter pattern          |

**Status:** All dependencies satisfied by Sprint 17.

---

## Implementation Order

Recommended order for development:

1. **Backend: Document Models** - Create Document, DocumentVersion, DocumentFolder models
2. **Backend: Storage Adapter** - Implement S3/DO Spaces storage integration
3. **Backend: OnlyOffice Integration** - Set up OnlyOffice service and document server
4. **Backend: Document Service** - Create document creation, upload, and retrieval services
5. **Backend: GraphQL API** - Create queries/mutations for document operations
6. **Frontend Web: Document Browser** - Build document browser with folder tree
7. **Frontend Web: OnlyOffice Editor** - Integrate OnlyOffice editor iframe/wrapper
8. **Frontend Web: Create Document Modal** - Build document creation interface
9. **Frontend Web: Document List** - Create document list with metadata display
10. **Shared UI: Document Components** - Build FileIcon, DocumentListItem, FolderTree components

---

## Repository Breakdown

| Story ID        | Backend | Frontend Web | Frontend Mobile | Shared UI |
| --------------- | ------- | ------------ | --------------- | --------- |
| US-021 (Part 1) | ✅      | ✅           | ✅              | ✅        |

**Backend:** Document models, OnlyOffice integration, S3/DO Spaces adapter, GraphQL API
**Frontend Web:** Document browser, OnlyOffice editor wrapper, create document modal
**Frontend Mobile:** Basic document viewing (defer editing to Part 2)
**Shared UI:** FileIcon, DocumentListItem, FolderTree, LoadingSpinner components

---

## Risks and Mitigations

| Risk                                    | Likelihood | Impact | Mitigation                                           |
| --------------------------------------- | ---------- | ------ | ---------------------------------------------------- |
| OnlyOffice server deployment complexity | Medium     | High   | Use Docker deployment, provide clear setup guide     |
| S3/DO Spaces configuration              | Low        | Medium | Test with both providers, document setup process     |
| OnlyOffice iframe integration           | Medium     | Medium | Follow OnlyOffice docs closely, test early           |
| Document versioning complexity          | Low        | Medium | Implement simple versioning first, enhance in Part 2 |
| Storage costs                           | Low        | Medium | Implement storage quota monitoring                   |

---

## Sprint Metrics (Post-Sprint)

_Fill in after sprint completion_

| Metric            | Planned | Actual |
| ----------------- | ------- | ------ |
| Points Committed  | 8       | -      |
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
