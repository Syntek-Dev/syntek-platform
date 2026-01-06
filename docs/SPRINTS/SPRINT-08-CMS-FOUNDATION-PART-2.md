# Sprint 8: CMS Foundation (Part 2)

<!-- CLICKUP_LIST_ID: 901519464112 -->

**Sprint Duration:** 14/04/2026 - 28/04/2026 (2 weeks)
**Capacity:** 2/11 points (9 points buffer)
**Status:** Planned

---

## Sprint Goal

Complete the CMS page creation system by adding advanced block types, performance optimisation,
and polish features. This sprint finalises the content editing experience before adding
media library support.

---

## MoSCoW Breakdown

### Must Have (2 points)

| Story ID                                         | Title                      | Points | Status  |
| ------------------------------------------------ | -------------------------- | ------ | ------- |
| [US-006](../STORIES/US-006-CMS-PAGE-CREATION.md) | CMS Page Creation (Part 2) | 2      | Pending |

_US-006 completion: 2 points for additional block types, performance optimisation, and polish_

### Should Have (0 points)

_None in this sprint_

### Could Have (0 points)

_None in this sprint_

---

## Dependencies

| Story  | Depends On | Notes                                          |
| ------ | ---------- | ---------------------------------------------- |
| US-006 | Sprint 7   | Core page creation and 8 block types completed |

**Dependencies satisfied:** US-006 Part 1 completed in Sprint 7.

---

## Implementation Order

### Week 1 (14/04 - 21/04)

1. **Additional Block Types (Priority 1)**
   - Backend: Video block definition and validation
   - Backend: Embed block (iframe) with URL validation
   - Frontend Web: VideoBlockEditor with YouTube/Vimeo support
   - Frontend Web: EmbedBlockEditor with preview
   - Frontend Web: Block styling options (background colour, padding, margins)
   - Shared UI: Video embed component
   - Shared UI: Iframe wrapper component

**Milestone:** All planned block types are available

### Week 2 (21/04 - 28/04)

2. **Performance and Polish (Priority 2)**
   - Frontend Web: Virtual scrolling for pages with many blocks
   - Frontend Web: Block search in palette
   - Frontend Web: Keyboard shortcuts for common actions
   - Frontend Web: Undo/redo functionality
   - Frontend Web: Block duplication with keyboard shortcut
   - Backend: Query optimisation for page loading
   - Testing: Performance testing with 50+ blocks
   - Documentation: Block development guide

**Milestone:** CMS page editor is complete, polished, and performant

---

## Repository Breakdown

| Story  | Backend | Frontend Web | Frontend Mobile | Shared UI |
| ------ | ------- | ------------ | --------------- | --------- |
| US-006 | ✅      | ✅           | ❌              | ✅        |

**3 repositories** will be active this sprint (Backend, Frontend Web, Shared UI).

---

## Technical Focus

### Backend

- **Video Block:** YouTube, Vimeo, direct video URL support
- **Embed Block:** Safe iframe embedding with validation
- **Query Optimisation:** Reduce database queries for page loads
- **Block Validation:** Ensure embed URLs are safe

### Frontend Web

- **Video Embedding:** Responsive video player with lazy loading
- **Embed Preview:** Show preview of embedded content in editor
- **Virtual Scrolling:** Performance for long pages
- **Undo/Redo:** Command pattern for edit history
- **Keyboard Shortcuts:** Common actions (Cmd+Z, Cmd+D, Cmd+S)

### Shared UI

- **Video Component:** Responsive video embed
- **Embed Component:** Safe iframe wrapper
- **Performance:** Optimise component rendering

---

## Risks & Mitigations

| Risk                                       | Likelihood | Impact | Mitigation                                                |
| ------------------------------------------ | ---------- | ------ | --------------------------------------------------------- |
| Embed security (XSS vulnerabilities)       | High       | High   | Strict URL validation, CSP headers, sandboxed iframes     |
| Video autoplay browser restrictions        | Medium     | Low    | Disable autoplay by default, document browser limitations |
| Undo/redo complexity                       | Medium     | Medium | Use established pattern (command pattern or Immer)        |
| Performance regression with virtual scroll | Low        | Medium | Test with 100+ block pages, measure metrics               |
| Large buffer may reduce focus              | Low        | Low    | Use buffer for technical debt from Sprint 7               |

---

## Acceptance Criteria Summary

### US-006: CMS Page Creation (Part 2)

- [ ] Video blocks support YouTube, Vimeo, and direct URLs
- [ ] Video blocks show responsive embed in editor and preview
- [ ] Embed blocks support iframe embedding with URL validation
- [ ] Embed blocks show preview in editor
- [ ] XSS protection is active for embed blocks
- [ ] Block styling options available (background, padding, margin)
- [ ] Virtual scrolling works for pages with 50+ blocks
- [ ] Block palette has search functionality
- [ ] Keyboard shortcuts work (Undo: Cmd+Z, Redo: Cmd+Shift+Z, Duplicate: Cmd+D, Save: Cmd+S)
- [ ] Undo/redo works for block add/edit/delete/reorder
- [ ] Performance is <2s for page load with 50 blocks
- [ ] Editor is responsive on tablet screens

**Completed from Sprint 7:**

- ✅ 8 core block types operational
- ✅ Drag-and-drop reordering functional
- ✅ Page preview working
- ✅ Autosave implemented

---

## Definition of Done

- [ ] All acceptance criteria met for US-006 (Part 2)
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass for new block types
- [ ] Security tests pass for embed validation
- [ ] Performance tests pass (<2s page load with 50 blocks)
- [ ] Code reviewed and merged to main
- [ ] Documentation updated (block guide, keyboard shortcuts)
- [ ] Deployed to development environment
- [ ] QA tested on dev environment
- [ ] Demo prepared for sprint review

---

## Sprint Metrics

| Metric            | Target | Actual |
| ----------------- | ------ | ------ |
| Points Committed  | 2      | -      |
| Points Completed  | -      | -      |
| Stories Completed | 1      | -      |
| Velocity          | -      | -      |
| Test Coverage     | >80%   | -      |
| Page Load Time    | <2s    | -      |
| Buffer Used       | 0 pts  | -      |

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

- Large buffer (9 points) provides flexibility for:
  - Technical debt from Sprint 7
  - Additional block styling options
  - Extended performance testing
  - Accessibility improvements
  - Additional keyboard shortcuts
  - Editor UX polish
- Security considerations for embed blocks:
  - Whitelist allowed domains (YouTube, Vimeo, Spotify, etc.)
  - Sandbox iframes (allow-scripts allow-same-origin)
  - Content Security Policy headers
  - URL validation on backend
- Video block best practices:
  - Lazy load videos (don't autoplay)
  - Show thumbnail until user clicks play
  - Responsive aspect ratios (16:9, 4:3, 1:1)
  - Fallback for unsupported URLs
- Undo/redo implementation:
  - Command pattern for all editor actions
  - History stack with max 50 actions
  - Clear history on page save
  - Keyboard shortcuts (Cmd+Z, Cmd+Shift+Z)
- Virtual scrolling:
  - Only render visible blocks + buffer
  - Use react-window or react-virtual
  - Measure performance with 100+ blocks
  - Smooth scrolling experience
- Keyboard shortcuts to implement:
  - Cmd/Ctrl+Z: Undo
  - Cmd/Ctrl+Shift+Z: Redo
  - Cmd/Ctrl+S: Save
  - Cmd/Ctrl+D: Duplicate block
  - Delete/Backspace: Delete selected block
  - Cmd/Ctrl+K: Insert link (in text blocks)
  - Cmd/Ctrl+B: Bold (in text blocks)
  - Cmd/Ctrl+I: Italic (in text blocks)

**Sprint 9 Preparation:**

- Media library integration ready
- Image blocks can use library picker
- Media upload workflow seamless

---

_Last Updated: 06/01/2026_
_Sprint Owner: Development Team_
