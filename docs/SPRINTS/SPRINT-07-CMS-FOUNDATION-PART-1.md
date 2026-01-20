# Sprint 7: CMS Foundation (Part 1)

<!-- CLICKUP_LIST_ID: 901519464108 -->

**Sprint Duration:** 31/03/2026 - 14/04/2026 (2 weeks)
**Capacity:** 11/11 points (at capacity)
**Status:** Planned

---

## Overview

This sprint implements the core CMS page creation system with block-based content editing. User story **US-006 (Part 1)** establishes Page and ContentBlock models with JSON-based block storage, GraphQL CRUD operations, and an intuitive drag-and-drop editor UI. Eight core block types are implemented: Text (rich text), Heading (h1-h6), Image (URL input), Button, Card, Feature, CTA, and Spacer. The block system is designed for extensibility to support additional block types in Sprint 8 and beyond. Features include autosave every 30 seconds, responsive previews (desktop/tablet/mobile), design token integration for consistent styling, and comprehensive block validation. The foundation prioritises editor usability as this interface will be heavily used by content creators and designers.

---

## Sprint Goal

Implement the core CMS page creation system with block-based content editing. This sprint
establishes the foundation for content management enabling editors to create pages using
reusable content blocks.

---

## MoSCoW Breakdown

### Must Have (11 points)

| Story ID                                         | Title                      | Points | Status  |
| ------------------------------------------------ | -------------------------- | ------ | ------- |
| [US-006](../STORIES/US-006-CMS-PAGE-CREATION.md) | CMS Page Creation (Part 1) | 11     | Pending |

_US-006 split: 11 points for core page creation, block editor, and primary block types this sprint,
2 points for additional blocks and polish in Sprint 8_

### Should Have (0 points)

_None in this sprint_

### Could Have (0 points)

_None in this sprint_

---

## Dependencies

| Story  | Depends On     | Notes                                          |
| ------ | -------------- | ---------------------------------------------- |
| US-006 | US-004, US-005 | Organisation setup and design tokens completed |

**Dependencies satisfied:** Organisation setup (Sprint 3) and Design Tokens (Sprint 6) are complete.

---

## Implementation Order

### Week 1 (31/03 - 07/04)

1. **Page Models and Backend (Priority 1)**
   - Backend: Page model with title, slug, organisation, template fields
   - Backend: PageVersion model for versioning
   - Backend: ContentBlock model for block definitions
   - Backend: BlockType enumeration (8 core types)
   - Backend: JSON schema validation for blocks
   - Backend: GraphQL mutations for page CRUD operations
   - Backend: GraphQL queries for page retrieval with pagination

**Milestone:** Page models exist and pages can be created via GraphQL API

### Week 2 (07/04 - 14/04)

2. **Page Editor UI and Block System (Priority 2)**
   - Frontend Web: Pages dashboard with list view
   - Frontend Web: Page Editor layout (sidebar + main editor + properties panel)
   - Frontend Web: BlockPalette component with 8 core blocks:
     - Text block (rich text editor)
     - Heading block (h1-h6 selector)
     - Image block (upload/library integration)
     - Button block (link + style options)
     - Card block (title + description + image)
     - Feature block (icon + title + description)
     - CTA block (call-to-action with button)
     - Spacer block (layout control)
   - Frontend Web: Drag-and-drop block reordering
   - Frontend Web: PagePreview component (desktop/tablet/mobile views)
   - Shared UI: RichTextEditor component
   - Shared UI: Block editor components

**Milestone:** Content editors can create pages and add/edit core content blocks

---

## Repository Breakdown

| Story  | Backend | Frontend Web | Frontend Mobile | Shared UI |
| ------ | ------- | ------------ | --------------- | --------- |
| US-006 | ✅      | ✅           | ❌              | ✅        |

**3 repositories** will be active this sprint (Backend, Frontend Web, Shared UI).

---

## Technical Focus

### Backend

- **Page Management:** Create, read, update, delete pages with versioning
- **Block Architecture:** Flexible JSON-based content block system
- **Schema Validation:** Ensure block content matches defined schemas
- **Autosave:** Background autosave every 30 seconds
- **Slug Generation:** Auto-generate URL-friendly slugs from titles

### Frontend Web

- **Block-Based Editor:** Intuitive drag-and-drop interface
- **Rich Text Editing:** TipTap or similar for text blocks
- **Media Integration:** Connect with media library (Sprint 9)
- **Responsive Preview:** Show how pages look on different devices
- **Autosave Indicator:** Visual feedback for save status

### Shared UI

- **RichTextEditor:** Reusable rich text component
- **Block Components:** Modular block editor UI elements
- **FileUpload:** Image upload component
- **LinkInput:** URL input with validation

---

## Risks & Mitigations

| Risk                                    | Likelihood | Impact | Mitigation                                                |
| --------------------------------------- | ---------- | ------ | --------------------------------------------------------- |
| Block architecture complexity           | High       | High   | Focus on 8 core blocks, defer advanced blocks to Sprint 8 |
| Rich text editor integration challenges | Medium     | High   | Use battle-tested library (TipTap, Slate, or DraftJS)     |
| Drag-and-drop UX issues                 | Medium     | Medium | Use established library (dnd-kit or react-beautiful-dnd)  |
| Performance with many blocks            | Medium     | Medium | Implement virtualization for long pages                   |
| Autosave conflicts                      | Low        | Medium | Use optimistic updates with conflict resolution           |
| Media library not ready                 | Medium     | High   | Use placeholder/URL-based images until Sprint 9           |

---

## Acceptance Criteria Summary

### US-006: CMS Page Creation (Part 1)

- [ ] Pages can be created with title and slug
- [ ] Page list view shows all pages with search/filter
- [ ] 8 core block types are available in block palette
- [ ] Blocks can be added to pages via drag or click
- [ ] Text blocks support rich text formatting (bold, italic, links, lists)
- [ ] Heading blocks support h1-h6 levels
- [ ] Image blocks support URL input (placeholder for Sprint 9 library)
- [ ] Button blocks support text, URL, and style options
- [ ] Card blocks support title, description, and image
- [ ] Feature blocks support icon selection, title, description
- [ ] CTA blocks support headline, description, and button
- [ ] Spacer blocks support height adjustment
- [ ] Blocks can be reordered via drag-and-drop
- [ ] Blocks can be duplicated and deleted
- [ ] Page preview shows desktop/tablet/mobile views
- [ ] Autosave runs every 30 seconds
- [ ] Save indicator shows save status
- [ ] Design tokens are applied to block styling

**Deferred to Sprint 8:**

- Video block
- Advanced layout blocks
- Custom HTML block
- Component library blocks

---

## Definition of Done

- [ ] All acceptance criteria met for US-006 (Part 1)
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass for page editor
- [ ] Block validation tests pass
- [ ] Code reviewed and merged to main
- [ ] Documentation updated (editor guide, block system architecture)
- [ ] Deployed to development environment
- [ ] QA tested on dev environment
- [ ] Demo prepared for sprint review

---

## Sprint Metrics

| Metric            | Target | Actual |
| ----------------- | ------ | ------ |
| Points Committed  | 11     | -      |
| Points Completed  | -      | -      |
| Stories Completed | 1      | -      |
| Velocity          | -      | -      |
| Test Coverage     | >80%   | -      |
| Block Types       | 8      | -      |

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

- This is a complex sprint with block-based architecture as the centerpiece
- Block system should be extensible for future block types
- Consider these architecture decisions:
  - Block data structure: JSON with type + properties
  - Block registration pattern for easy extensibility
  - Block validation per type
  - Block rendering consistency between editor and public site
- Rich text editor considerations:
  - TipTap (modern, extensible, TypeScript)
  - Slate (flexible, complex)
  - DraftJS (Facebook, mature but older)
  - Recommendation: TipTap for balance of features and simplicity
- Drag-and-drop library considerations:
  - dnd-kit (modern, accessible, TypeScript)
  - react-beautiful-dnd (mature, Atlassian)
  - Recommendation: dnd-kit for better TypeScript support
- Image handling:
  - Use URL input until Media Library (Sprint 9)
  - Plan for seamless transition to media library picker
  - Support both external URLs and future library images
- Autosave strategy:
  - Debounce user input (500ms)
  - Save draft every 30 seconds
  - Optimistic UI updates
  - Conflict resolution if multiple editors
- Block palette UX:
  - Searchable block list
  - Category grouping (Text, Media, Layout)
  - Recently used blocks at top
  - Drag from palette or click to insert

**Sprint 8 Preparation:**

- Additional block types (Video, Embed, HTML)
- Block styling customisation
- Advanced layout options
- Performance optimisation for many blocks

---

_Last Updated: 06/01/2026_
_Sprint Owner: Development Team_
