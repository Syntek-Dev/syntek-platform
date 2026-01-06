# User Story: Media Library Management

<!-- CLICKUP_ID: 86c7d2p2c -->

## Story

**As a** content editor
**I want** to upload, organise, and manage media files (images, videos, documents)
**So that** I can easily insert them into pages and maintain a centralised asset repository

## MoSCoW Priority

- **Must Have:** Image upload, image storage, image retrieval, folder organisation, file metadata (alt text, title)
- **Should Have:** Image optimisation, multiple format support, bulk upload, search and filtering
- **Could Have:** Image cropping and editing, video hosting, document preview
- **Won't Have:** Automatic image generation in Phase 3

## Repository Coverage

| Repository      | Required | Notes                                                    |
| --------------- | -------- | -------------------------------------------------------- |
| Backend         | ✅       | Media model, file storage, image processing, GraphQL API |
| Frontend Web    | ✅       | Media library UI, upload interface, library browser      |
| Frontend Mobile | ✅       | Media picker for mobile                                  |
| Shared UI       | ✅       | Media picker component                                   |

## Acceptance Criteria

### Scenario 1: Upload Single Image

**Given** the user is in the media library
**When** they click "Upload" or drag files
**Then** they can select an image file
**And** the image is uploaded to the server
**And** a thumbnail is generated
**And** file metadata is captured (filename, size, dimensions)
**And** the upload progress is shown
**And** upon completion, the image appears in the library

### Scenario 2: Add Image Metadata

**Given** an image is uploaded
**When** the user views the image details
**Then** they can edit:

- Alt text (required for accessibility)
- Title
- Description
- Tags (for organisation)
  **And** the metadata is validated
  **And** changes are saved to the database

### Scenario 3: Organise Images in Folders

**Given** the media library has multiple images
**When** the user creates a folder
**Then** they can:

- Create nested folder structure
- Move images between folders
- Rename folders
- Delete empty folders
  **And** folder structure is reflected in the interface
  **And** breadcrumbs show current location

### Scenario 4: Search and Filter Media

**Given** the media library contains many files
**When** the user searches or filters
**Then** they can:

- Search by filename
- Search by alt text or tags
- Filter by file type (images, videos, documents)
- Filter by upload date
  **And** results are displayed with filtering active
  **And** folder context is maintained

### Scenario 5: Insert Media into Page Blocks

**Given** a text or content block requires an image
**When** the user clicks "Insert Image" in the block editor
**Then** the media library picker appears
**And** they can browse, search, and select an image
**And** the selected image is inserted into the block
**And** alt text is required before insertion

### Scenario 6: Image Optimisation

**Given** an image is uploaded
**When** the system processes the image
**Then** it:

- Creates multiple sizes (thumbnail, medium, large, full)
- Converts to modern formats (WebP with PNG fallback)
- Compresses for web delivery
- Strips metadata (EXIF)
  **And** responsive images are generated
  **And** the original is retained as backup

### Scenario 7: Bulk Upload

**Given** the user has multiple images to upload
**When** they drag multiple files or select them
**Then** all files are uploaded simultaneously
**And** progress is shown for each file
**And** errors are reported per file
**And** successful uploads are available immediately

### Scenario 8: Delete Media

**Given** an image is in the library
**When** the user deletes it
**Then** a warning is shown if the image is used in pages
**And** the user must confirm the deletion
**And** if deleted, it's removed from all pages (with placeholder)
**And** the file is deleted from storage

## Dependencies

- US-004: Organisation Creation and Setup
- US-006: Create and Edit CMS Pages
- File storage system (S3, local, etc.)
- Image processing library (Pillow)

## Tasks

### Backend Tasks

- [ ] Create MediaAsset model with fields: filename, file_path, file_size, dimensions, organisation
- [ ] Create MediaFolder model for folder organisation
- [ ] Create MediaMetadata model for alt text, title, description, tags
- [ ] Implement file upload endpoint (GraphQL mutation)
- [ ] Implement image processing service (resizing, format conversion)
- [ ] Create thumbnail generation logic
- [ ] Implement image optimisation pipeline
- [ ] Create file storage abstraction (support S3, local storage)
- [ ] Create GraphQL query for media library listing
- [ ] Create GraphQL mutation for folder creation
- [ ] Create GraphQL mutation for media metadata update
- [ ] Create GraphQL mutation for media deletion
- [ ] Implement search and filtering logic
- [ ] Add media usage tracking (which pages use which assets)
- [ ] Add file size limit validation
- [ ] Create audit logging for media operations
- [ ] Add unit tests for media operations
- [ ] Add integration tests for upload and processing

### Frontend Web Tasks

- [ ] Create MediaLibrary page
- [ ] Create MediaGrid component with thumbnail display
- [ ] Create MediaUpload component (drag-and-drop)
- [ ] Create FolderTree component for navigation
- [ ] Create MediaSearch component
- [ ] Create MediaFilter component
- [ ] Create MediaMetadataEditor component
- [ ] Create MediaPicker modal for insertion
- [ ] Show upload progress for files
- [ ] Add bulk upload support
- [ ] Create MediaDeleteConfirmation dialog
- [ ] Show file usage information
- [ ] Add responsive grid for media display
- [ ] Implement breadcrumb navigation
- [ ] Show metadata editor on image selection

### Frontend Mobile Tasks

- [ ] Create MediaPicker component for mobile
- [ ] Implement camera/photo library access
- [ ] Create image upload from mobile camera
- [ ] Support image selection from device storage

### Shared UI Tasks

- [ ] Create MediaUpload component with drag-and-drop
- [ ] Create MediaGrid component
- [ ] Create MediaPicker component (reusable)
- [ ] Create ProgressBar for uploads
- [ ] Create ConfirmationDialog for deletions
- [ ] Create SearchInput component
- [ ] Create FilterPanel component
- [ ] Create BreadcrumbNavigation component

## Story Points (Fibonacci)

**Estimate:** 8

**Complexity factors:**

- File upload and processing
- Image optimisation and format conversion
- Folder hierarchy management
- Search and filtering implementation
- Media usage tracking
- Delete confirmation with usage awareness
- Responsive image generation
- Integration with page editor blocks

---

## Related Stories

- US-006: Create and Edit CMS Pages with Block-Based Content
- US-045: Shared UI Component Library
