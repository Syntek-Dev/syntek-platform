# User Story: Page Publication and Public Website Display

<!-- CLICKUP_ID: 86c7d2pe6 -->

## Story

**As a** content editor
**I want** to publish pages to make them live on the public website
**So that** visitors can view the content I've created

## MoSCoW Priority

- **Must Have:** Page publication workflow, public URL routing, published page display, 404 handling for unpublished pages
- **Should Have:** Publication scheduling, redirect management, sitemap generation
- **Could Have:** SEO pre-flight checks, performance optimisation on publish
- **Won't Have:** CDN edge caching in Phase 3


**Sprint:** Sprint 11

## Repository Coverage

| Repository      | Required | Notes                                              |
| --------------- | -------- | -------------------------------------------------- |
| Backend         | ✅       | Page publishing logic, public routing, GraphQL API |
| Frontend Web    | ✅       | Page rendering engine, public website display      |
| Frontend Mobile | ✅       | Ability to view published content                  |
| Shared UI       | ✅       | Page renderer component                            |

## Acceptance Criteria

### Scenario 1: Mark Page as Published

**Given** a page has content and is ready
**When** the editor clicks "Publish"
**Then** they are prompted to confirm publication
**And** upon confirmation, the page is marked as published
**And** a published_at timestamp is set
**And** the production branch is updated
**And** an audit log entry is created

### Scenario 2: Unpublish Page

**Given** a published page is live
**When** the editor clicks "Unpublish"
**Then** a confirmation dialog appears
**And** upon confirmation, the page is removed from public access
**And** visitors see a 404 error for that URL
**And** the action is logged in audit logs

### Scenario 3: Published Page Available via URL

**Given** a page is published
**When** a visitor accesses the page URL (e.g., /about or /blog/my-post)
**Then** the page content is displayed
**And** the correct template is used for rendering
**And** design tokens are applied correctly
**And** meta tags are included (title, description, og tags)

### Scenario 4: Unpublished Pages Return 404

**Given** a page is not published (draft or unpublished)
**When** a visitor tries to access its URL
**Then** a 404 page is displayed
**And** the request is logged (for debugging)

### Scenario 5: Sitemap Generation

**Given** pages are published
**When** a visitor requests /sitemap.xml
**Then** a sitemap is generated containing:

- All published pages
- Last modified date per page
- Page priority and change frequency
  **And** the sitemap is valid XML
  **And** it can be submitted to search engines

### Scenario 6: Redirect Management

**Given** a page URL changes
**When** the slug is updated
**Then** the editor can set up a redirect from the old URL
**And** visitors using the old URL are redirected with a 301 (permanent) status
**And** the redirect is logged

### Scenario 7: Version History in Production

**Given** a page is published and later edited
**When** the page is published again
**Then** a new version is created
**And** the previous version is retained in history
**And** the editor can view and revert to previous published versions

### Scenario 8: Publishing Notification

**Given** a page is published
**When** publication occurs
**Then** team members are notified (email or in-app)
**And** the notification includes the page title and URL
**And** the notification includes a link to the live page

## Dependencies

- US-006: Create and Edit CMS Pages
- US-007: Content Branching Workflow
- Page rendering system
- URL routing system

## Tasks

### Backend Tasks

- [ ] Create published_at field on Page model
- [ ] Create is_published boolean field on Page model
- [ ] Create publishPage GraphQL mutation
- [ ] Create unpublishPage GraphQL mutation
- [ ] Implement page state validation before publishing
- [ ] Create public page query (returns only published pages)
- [ ] Create URL routing for published pages (dynamic routing)
- [ ] Implement 404 handling for unpublished/non-existent pages
- [ ] Create Redirect model for URL redirects
- [ ] Create redirect checking middleware
- [ ] Create sitemap generation service
- [ ] Create sitemap GraphQL endpoint
- [ ] Implement publication notifications
- [ ] Add validation for required metadata (title, meta description)
- [ ] Create audit logging for publication events
- [ ] Add unit tests for publication logic
- [ ] Add integration tests for public routing

### Frontend Web Tasks

- [ ] Create public page template renderer
- [ ] Create PageRenderer component for displaying published content
- [ ] Implement responsive block rendering for public site
- [ ] Create layout component for public pages
- [ ] Create header/navigation for public site
- [ ] Create footer for public site
- [ ] Add meta tag rendering (title, description, og tags)
- [ ] Implement design token application in public renderer
- [ ] Create 404 error page
- [ ] Create publish confirmation dialog in editor
- [ ] Show publication status in page editor
- [ ] Create publication history browser
- [ ] Add preview-as-public feature in editor

### Shared UI Tasks

- [ ] Create BlockRenderer component for public display
- [ ] Create TextBlockRenderer
- [ ] Create ImageBlockRenderer
- [ ] Create ButtonBlockRenderer
- [ ] Create CardBlockRenderer
- [ ] Create FeatureBlockRenderer
- [ ] Create CTABlockRenderer
- [ ] Create VideoBlockRenderer

## Story Points (Fibonacci)

**Estimate:** 8

**Complexity factors:**

- Dynamic URL routing implementation
- Multiple block type renderers
- Meta tag generation and rendering
- Sitemap XML generation
- Redirect handling and validation
- Publication workflow state management
- Notification system integration
- Public vs private content separation

---

## Related Stories

- US-006: Create and Edit CMS Pages with Block-Based Content
- US-007: Content Branching Workflow
- US-030: SEO Metadata and Optimisation
