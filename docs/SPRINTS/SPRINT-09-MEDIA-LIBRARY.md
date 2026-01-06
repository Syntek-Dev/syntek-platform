# Sprint 9: Media Library Management

<!-- CLICKUP_LIST_ID: 901519464116 -->

**Sprint Duration:** 28/04/2026 - 12/05/2026 (2 weeks)
**Capacity:** 8/11 points (3 points buffer)
**Status:** Planned

---

## Sprint Goal

Implement a comprehensive media library system for uploading, organising, and managing images
and documents. This sprint enables content editors to maintain a centralised asset repository
with search, folders, and metadata management.

---

## MoSCoW Breakdown

### Must Have (8 points)

| Story ID                                     | Title         | Points | Status  |
| -------------------------------------------- | ------------- | ------ | ------- |
| [US-009](../STORIES/US-009-MEDIA-LIBRARY.md) | Media Library | 8      | Pending |

### Should Have (0 points)

_None in this sprint_

### Could Have (0 points)

_None in this sprint_

---

## Dependencies

| Story  | Depends On     | Notes                                          |
| ------ | -------------- | ---------------------------------------------- |
| US-009 | US-004, US-006 | Organisation setup and page creation completed |

**Dependencies satisfied:** Organisation setup (Sprint 3) and CMS page creation (Sprint 8) are complete.

---

## Implementation Order

### Week 1 (28/04 - 05/05)

1. **Media Storage and Backend (Priority 1)**
   - Backend: MediaAsset model (filename, path, size, dimensions, organisation)
   - Backend: MediaFolder model for folder structure
   - Backend: MediaMetadata model (alt text, title, description, tags)
   - Backend: File upload GraphQL mutation
   - Backend: Image processing service (Pillow for resize, format conversion)
   - Backend: Thumbnail generation (150x150, 300x300, 600x600)
   - Backend: File storage abstraction (S3 or local storage)
   - Backend: GraphQL queries for media listing with pagination
   - Backend: GraphQL mutations for folder management
   - Backend: Search and filter implementation

**Milestone:** Images can be uploaded, processed, and stored in organised folders

### Week 2 (05/05 - 12/05)

2. **Media Library UI and Integration (Priority 2)**
   - Frontend Web: MediaLibrary page with grid view
   - Frontend Web: MediaUpload component (drag-and-drop, multi-file)
   - Frontend Web: FolderTree navigation
   - Frontend Web: MediaSearch with filtering
   - Frontend Web: MediaMetadataEditor (alt text, title, tags)
   - Frontend Web: MediaPicker modal for page editor integration
   - Frontend Web: Upload progress indicators
   - Frontend Web: Bulk upload support
   - Shared UI: MediaGrid component
   - Shared UI: MediaUpload component
   - Shared UI: MediaPicker component
   - Integration: Connect image blocks to media library

**Milestone:** Media library is fully operational and integrated with page editor

---

## Repository Breakdown

| Story  | Backend | Frontend Web | Frontend Mobile | Shared UI |
| ------ | ------- | ------------ | --------------- | --------- |
| US-009 | ✅      | ✅           | ✅              | ✅        |

**All 4 repositories** will be active this sprint.

---

## Technical Focus

### Backend

- **File Upload:** Multipart file upload with validation
- **Image Processing:** Resize, format conversion (WebP), compression
- **Storage:** Abstraction layer supporting S3 and local storage
- **Thumbnails:** Multiple sizes for responsive images
- **Folder Management:** Nested folder structure with move operations
- **Search:** Full-text search across filename, alt text, tags
- **Validation:** File size limits (10MB images), allowed formats

### Frontend Web

- **Drag-and-Drop:** File upload via drag-and-drop or file picker
- **Grid View:** Thumbnail grid with folder navigation
- **Media Picker:** Modal for selecting images in page editor
- **Metadata Editor:** Inline editing of alt text and tags
- **Bulk Operations:** Multi-select for batch operations
- **Upload Progress:** Real-time progress for uploads

### Frontend Mobile

- **Media Picker:** Mobile-optimised picker for image selection
- **Camera Integration:** Upload from device camera
- **Gallery Integration:** Upload from device photo library

### Shared UI

- **MediaGrid:** Reusable media thumbnail grid
- **MediaUpload:** Drag-and-drop upload component
- **MediaPicker:** Modal for media selection

---

## Risks & Mitigations

| Risk                                  | Likelihood | Impact | Mitigation                                                  |
| ------------------------------------- | ---------- | ------ | ----------------------------------------------------------- |
| Large file uploads causing timeouts   | Medium     | High   | Implement chunked uploads, increase timeout limits          |
| S3 storage costs                      | Low        | Medium | Use local storage for dev, document S3 costs for production |
| Image processing performance          | Medium     | Medium | Process asynchronously, use Celery for background jobs      |
| File size limits need adjustment      | Medium     | Low    | Make limits configurable per organisation                   |
| Alt text validation for accessibility | Medium     | High   | Require alt text before image insertion into pages          |
| Mobile camera permissions             | Low        | Low    | Handle permission denied gracefully, document requirements  |

---

## Acceptance Criteria Summary

### US-009: Media Library

- [ ] Single image can be uploaded via drag-and-drop or file picker
- [ ] Bulk upload supports multiple images simultaneously
- [ ] Upload progress is shown per file
- [ ] Thumbnails are generated (150x150, 300x300, 600x600)
- [ ] Images are converted to WebP with PNG fallback
- [ ] Alt text can be added/edited (required for accessibility)
- [ ] Title and description can be added/edited
- [ ] Tags can be added for organisation
- [ ] Folders can be created, renamed, and deleted
- [ ] Nested folder structure is supported
- [ ] Images can be moved between folders
- [ ] Breadcrumb navigation shows current folder path
- [ ] Search finds images by filename, alt text, or tags
- [ ] Filter by file type (image, document, video)
- [ ] MediaPicker modal appears in image block editor
- [ ] Selected image is inserted into page block
- [ ] Alt text is validated before insertion
- [ ] Image usage is tracked (which pages use which images)
- [ ] Delete confirmation warns if image is in use
- [ ] Mobile camera upload works on iOS and Android
- [ ] Mobile gallery upload works on iOS and Android

---

## Definition of Done

- [ ] All acceptance criteria met for US-009
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass for upload and processing
- [ ] Security tests pass for file validation
- [ ] Performance tests pass for bulk uploads
- [ ] Code reviewed and merged to main
- [ ] Documentation updated (media library guide, storage config)
- [ ] Deployed to development environment
- [ ] QA tested on dev environment (web and mobile)
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
| Upload Speed      | <5s/MB | -      |

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

- File storage considerations:
  - **Local Storage:** Simple for dev, requires disk space
  - **AWS S3:** Scalable, cost per GB stored and transferred
  - **Digital Ocean Spaces:** S3-compatible, simpler pricing
  - **Recommendation:** Local for dev, S3 for production
- Image processing pipeline:
  1. Upload original to storage
  2. Generate thumbnails (150x, 300x, 600x)
  3. Convert to WebP with PNG fallback
  4. Strip EXIF metadata
  5. Store all variants
  6. Return URLs to frontend
- Thumbnail sizes rationale:
  - 150x150: List view thumbnail
  - 300x300: Grid view thumbnail
  - 600x600: Preview and small displays
  - Original: Full-size display
- Alt text requirements:
  - Required before inserting into page
  - Max 125 characters (recommended)
  - Should describe image content
  - Should not include "image of" prefix
- Folder structure:
  - Max 5 levels deep
  - Max 100 items per folder
  - Breadcrumb navigation for deep paths
  - Quick access to recent folders
- Search functionality:
  - Full-text search on filename, alt text, tags
  - Filter by file type, upload date, folder
  - Sort by name, date, size
  - Highlight search terms in results
- Mobile considerations:
  - Camera permission handling
  - Photo library permission handling
  - Image compression before upload
  - Offline support for uploads (queue when online)
- Integration with page editor:
  - MediaPicker appears on "Insert Image" click
  - Shows same interface as media library
  - Selected image populates block
  - Alt text is pre-filled if available
  - User can edit alt text before insertion

**Sprint 10 Preparation:**

- Content branching system ready
- Pages can exist in multiple branches
- Media library supports branch-specific assets (future enhancement)

---

_Last Updated: 06/01/2026_
_Sprint Owner: Development Team_
