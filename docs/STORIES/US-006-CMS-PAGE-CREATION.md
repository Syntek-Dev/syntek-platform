# User Story: Create and Edit CMS Pages with Block-Based Content

<!-- CLICKUP_ID: 86c7d2n36 -->

## Story

**As a** content editor
**I want** to create and edit pages using a block-based content system
**So that** I can build dynamic website content without coding knowledge

## MoSCoW Priority

- **Must Have:** Page creation, block-based content editing, JSON content storage, page metadata (title, slug, description)
- **Should Have:** Rich text editor, image/media blocks, layout blocks, page preview, autosave
- **Could Have:** AI-assisted content writing, SEO suggestions, A/B testing variants
- **Won't Have:** Advanced design blocks in Phase 3

## Repository Coverage

| Repository      | Required | Notes                                                       |
| --------------- | -------- | ----------------------------------------------------------- |
| Backend         | ✅       | Page model, block definitions, GraphQL API, content storage |
| Frontend Web    | ✅       | Page editor interface, block editor, preview                |
| Frontend Mobile | ❌       | Not applicable in Phase 3                                   |
| Shared UI       | ✅       | Block components, editor components                         |

## Acceptance Criteria

### Scenario 1: Create New Page

**Given** a content editor is in the CMS dashboard
**When** they click "Create Page"
**Then** they can enter:

- Page title
- Page slug (auto-generated from title, editable)
- Meta title and description
  **And** the page is created with an empty content area
  **And** they are taken to the page editor

### Scenario 2: Add Content Blocks

**Given** the page editor is open
**When** the user clicks "Add Block"
**Then** a block palette appears showing available block types:

- Text (with rich text editor)
- Heading (with heading level selector)
- Image (with upload/library selection)
- Button (with link and styling options)
- Card (with title, description, image)
- Feature (icon + title + description)
- CTA (call-to-action block with button)
- Video (embedded video support)
- Spacer (for layout control)
  **And** the selected block is inserted into the page
  **And** the block editor appears for immediate editing

### Scenario 3: Edit Block Content

**Given** a block is added to the page
**When** the user clicks on the block to edit
**Then** a context-specific editor appears:

- Text block shows rich text editor (bold, italic, links, lists)
- Image block shows upload/media library picker
- Button block shows text and URL input with style options
- Heading block shows text and level selector
  **And** changes are reflected in real-time preview
  **And** the block can be duplicated or deleted

### Scenario 4: Reorder Blocks

**Given** multiple blocks exist on a page
**When** the user drags a block
**Then** the block can be reordered
**And** the new order is reflected in the page content JSON
**And** the change is persisted automatically

### Scenario 5: Page Preview

**Given** a page has content blocks
**When** the user clicks "Preview"
**Then** a preview panel appears showing:

- How the page will look on desktop
- How the page will look on tablet
- How the page will look on mobile
  **And** responsive breakpoints are accurate
  **And** design tokens are applied correctly

### Scenario 6: Save and Publish Draft

**Given** a page is being edited
**When** the user clicks "Save Draft"
**Then** the page is saved to the feature branch
**And** a version is created with timestamp
**And** the user can continue editing
**And** when "Publish" is clicked, the page moves to production branch

## Dependencies

- US-004: Organisation Creation and Setup
- US-005: Design Token System
- US-020: Template Selection and Initialization
- Block definitions and schema

## Tasks

### Backend Tasks

- [ ] Create Page model with fields: title, slug, organisation, template
- [ ] Create PageVersion model for versioning
- [ ] Create ContentBlock model for block definitions
- [ ] Create BlockType enumeration (text, heading, image, button, card, etc.)
- [ ] Implement JSON schema validation for block content
- [ ] Create block type definitions with schema validation
- [ ] Create page creation GraphQL mutation
- [ ] Create page update GraphQL mutation
- [ ] Create page retrieval GraphQL query
- [ ] Create block add/update/delete mutations
- [ ] Create page list query with pagination
- [ ] Implement autosave functionality (Celery task)
- [ ] Create page preview endpoint
- [ ] Add URL slug uniqueness validation per organisation
- [ ] Add audit logging for all page changes
- [ ] Add unit tests for block validation
- [ ] Add integration tests for page editor

### Frontend Web Tasks

- [ ] Create Pages dashboard with list view
- [ ] Create Page Editor layout (left sidebar, main editor, right panel)
- [ ] Create BlockPalette component with available blocks
- [ ] Create TextBlockEditor with rich text editor
- [ ] Create HeadingBlockEditor with level selector
- [ ] Create ImageBlockEditor with upload and media library
- [ ] Create ButtonBlockEditor with link and style options
- [ ] Create CardBlockEditor
- [ ] Create FeatureBlockEditor
- [ ] Create CTABlockEditor
- [ ] Create VideoBlockEditor
- [ ] Create SpacerBlockEditor
- [ ] Implement drag-and-drop for block reordering
- [ ] Create PagePreview component (desktop, tablet, mobile views)
- [ ] Implement autosave indicator
- [ ] Add save and publish buttons
- [ ] Create version history browser
- [ ] Add page metadata editor (title, description, keywords)

### Shared UI Tasks

- [ ] Create RichTextEditor component (with bold, italic, links, lists)
- [ ] Create FileUploadButton component
- [ ] Create ColorPicker component (for text/background colors using tokens)
- [ ] Create LinkInput component
- [ ] Create TextInput component
- [ ] Create SelectInput component
- [ ] Create MetadataEditor component
- [ ] Create PagePreview wrapper component

## Story Points (Fibonacci)

**Estimate:** 13

**Complexity factors:**

- Block-based architecture with multiple block types
- Rich text editor integration
- JSON schema validation
- Real-time preview generation
- Drag-and-drop functionality
- Version management
- Autosave functionality
- Responsive preview system
- Complex form state management
- Media library integration

---

## Related Stories

- US-004: Organisation Creation and Setup
- US-005: Design Token System
- US-007: Content Branching Workflow
- US-020: Template Selection and Initialization
