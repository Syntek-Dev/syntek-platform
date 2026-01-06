# User Story: Cloud Documents Integration

<!-- CLICKUP_ID: 86c7d2uqh -->

## Story

**As a** team member or content creator
**I want** to create, edit, and collaborate on documents directly within the platform
**So that** I can manage all my business documents in one place without switching between applications

## MoSCoW Priority

- **Must Have:** OnlyOffice integration, document browser UI, document creation/editing,
  storage (S3/DO Spaces), basic sharing permissions
- **Should Have:** Version history, document search, bulk operations, folder organisation,
  access control
- **Could Have:** Real-time collaboration indicators, document templates, export to multiple
  formats, integration with design tokens
- **Won't Have:** Advanced collaboration features (comments, @mentions) until Phase 11

**Sprint:** Sprint 21

## Repository Coverage

| Repository      | Required | Notes                                                                 |
| --------------- | -------- | --------------------------------------------------------------------- |
| Backend         | ✅       | OnlyOffice integration, storage adapter, document models, GraphQL API |
| Frontend Web    | ✅       | Document browser, editor interface, permission management             |
| Frontend Mobile | ✅       | Document viewing, basic editing                                       |
| Shared UI       | ✅       | Document list, file browser, permission selectors                     |

## Acceptance Criteria

### Scenario 1: Access Cloud Documents Application

**Given** a user is logged into the platform
**When** they navigate to the documents section
**Then** they can:

- View the Cloud Documents application at `docs.{domain}` subdomain
- See a document browser with folder structure
- View list of available documents with metadata (name, size, modified date, owner)
- Search for documents by name or content
  **And** OnlyOffice interface is loaded
  **And** custom branding is applied (logo, colours from design tokens)

### Scenario 2: Create New Document

**Given** a user is in the document browser
**When** they click "Create Document"
**Then** they can:

- Select document type (Text, Spreadsheet, Presentation)
- Enter document name
- Choose parent folder
- Set initial access level (private, team, organisation)
  **And** the document is created in storage
  **And** OnlyOffice editor opens automatically
  **And** user is redirected to the document editor

### Scenario 3: Edit Document in OnlyOffice

**Given** a document is open in the editor
**When** the user makes changes
**Then** the system:

- Displays real-time editor interface (OnlyOffice)
- Auto-saves changes at regular intervals (every 30 seconds)
- Shows last modified time and editor name
- Prevents concurrent editing conflicts (one editor at a time)
  **And** changes are stored in S3/DO Spaces
  **And** version is incremented on each save

### Scenario 4: Document Permissions and Sharing

**Given** a user owns a document
**When** they access document settings
**Then** they can:

- Set document access level (Private, Team, Organisation, Public)
- Add specific users/teams with granular permissions (View, Edit, Admin)
- Generate shareable link with expiration date
- Disable sharing link at any time
  **And** permissions are checked on each access
  **And** audit log is created for permission changes

### Scenario 5: Version History

**Given** a document has been edited multiple times
**When** the user views version history
**Then** they can:

- See list of all versions with timestamp and editor name
- Preview previous versions
- Restore to any previous version (with confirmation)
- View differences between versions (basic)
  **And** versions are stored separately in storage
  **And** restoration is logged in audit trail

### Scenario 6: Document Organisation

**Given** a user wants to organise documents
**When** they interact with the folder structure
**Then** they can:

- Create folders and subfolders
- Move documents between folders
- Rename documents and folders
- Delete documents (soft delete, with 30-day recovery)
  **And** folder structure is preserved in storage
  **And** operations trigger audit logs

### Scenario 7: Search and Discovery

**Given** a user is looking for a specific document
**When** they use the search function
**Then** they can:

- Search by document name
- Search by partial content (basic full-text search)
- Filter by document type (Text, Spreadsheet, Presentation)
- Filter by owner or last modified date
- Sort results by relevance, date, or name
  **And** search results show document preview/metadata
  **And** search is scoped to user's accessible documents

### Scenario 8: Document Metadata

**Given** a document exists in the system
**When** metadata is accessed
**Then** the user can see:

- Document name and type
- File size
- Creation date and creator name
- Last modified date and editor name
- Current access level
- Number of revisions
- Storage location
  **And** metadata is editable (name, description)
  **And** metadata is displayed in document browser

### Scenario 9: Storage Integration (S3/DO Spaces)

**Given** documents are created or updated
**When** storage operations occur
**Then** the system:

- Stores document files in configured S3 or Digital Ocean Spaces
- Uses organisation-specific prefixes for file paths
- Encrypts files in transit and at rest
- Generates secure URLs for editor access
- Manages document lifecycle (versions, backups)
  **And** storage configuration can be changed per environment
  **And** backup copies are maintained

### Scenario 10: Export Document

**Given** a user has a document open
**When** they request export
**Then** they can:

- Export to PDF
- Export to DOCX (Word), XLSX (Excel), PPTX (PowerPoint)
- Export to ODF formats (ODT, ODS, ODP)
- Export with current formatting preserved
  **And** export happens without leaving the editor
  **And** exported file is available for download

## Dependencies

- OnlyOffice server deployment (Docker or managed)
- S3 or Digital Ocean Spaces storage account
- Document storage models and database
- GraphQL API
- Authentication and permission system (US-001)
- Design Token System (US-005) for branding

## Tasks

### Backend Tasks

- [ ] Create Document model (name, type, owner, permissions, metadata)
- [ ] Create DocumentVersion model for version history
- [ ] Create DocumentFolder model for folder structure
- [ ] Create DocumentPermission model for granular access control
- [ ] Create DocumentAccessLog model for audit trail
- [ ] Implement S3/DO Spaces storage adapter
- [ ] Create OnlyOffice integration service
- [ ] Implement document creation endpoint
- [ ] Implement document upload/storage handler
- [ ] Implement document version control system
- [ ] Create document sharing endpoint
- [ ] Create permission checking middleware
- [ ] Implement full-text search for documents
- [ ] Create export to PDF/Word/Excel functionality
- [ ] Create GraphQL queries for documents and folders
- [ ] Create GraphQL mutations for CRUD operations
- [ ] Implement document recovery (soft delete)
- [ ] Create document usage tracking (storage consumed)
- [ ] Add unit tests for document service
- [ ] Add integration tests with OnlyOffice and storage

### Frontend Web Tasks

- [ ] Create DocumentBrowser page/component
- [ ] Create FolderTree sidebar component
- [ ] Create DocumentList component with metadata columns
- [ ] Create DocumentCard for grid view
- [ ] Create OnlyOfficeEditor wrapper/iframe handler
- [ ] Create SearchBar component for documents
- [ ] Create CreateDocumentModal
- [ ] Create FolderCreationModal
- [ ] Create DocumentPermissionsPanel
- [ ] Create VersionHistory viewer
- [ ] Create DocumentMetadata editor
- [ ] Create ShareLink generator
- [ ] Create ExportMenu component
- [ ] Create DocumentPreview component
- [ ] Implement drag-and-drop for moving documents between folders
- [ ] Create ConfirmationDialog for delete/restore
- [ ] Add copy-to-clipboard for share links

### Frontend Mobile Tasks

- [ ] Create DocumentList view (optimised for mobile)
- [ ] Create DocumentDetail view
- [ ] Create SimplifiedEditor view (basic OnlyOffice integration)
- [ ] Implement document opening in mobile app
- [ ] Create download option for offline access
- [ ] Add swipe gestures for navigation

### Shared UI Tasks

- [ ] Create FileIcon component (for different document types)
- [ ] Create DocumentListItem component
- [ ] Create PermissionSelector component
- [ ] Create SearchBar component (reusable)
- [ ] Create ConfirmationDialog component
- [ ] Create LoadingSpinner component
- [ ] Create AlertBox for notifications
- [ ] Create ContextMenu for document operations

## Story Points (Fibonacci)

**Estimate:** 13

**Complexity factors:**

- OnlyOffice server integration and configuration
- S3/DO Spaces storage integration
- Document version control system
- Real-time auto-save implementation
- Permission system with granular access control
- Full-text search implementation
- Document export to multiple formats
- File conflict resolution
- Soft delete with recovery mechanism
- Multi-platform UI implementation (web and mobile)
- Storage management and backup strategy

---

## Related Stories

- US-001: User Authentication (permissions based on user roles)
- US-004: Organisation Setup (organisation-scoped storage)
- US-005: Design Token System (custom branding in OnlyOffice)
- US-009: Media Library (similar storage/browser patterns)
- US-012: Audit Logging (document access and permission changes)
- US-014: Third-Party Integrations (integration framework)
