# User Story: Template Selection and Site Initialization

<!-- CLICKUP_ID: 86c7d2ntg -->

## Story

**As a** new user creating their first website
**I want** to select a pre-built template that matches my business type
**So that** I can quickly get started with a fully configured website structure

## MoSCoW Priority

- **Must Have:** 9 template categories, template preview, template selection, initial page creation, default design tokens
- **Should Have:** Template customisation wizard, industry-specific content suggestions, example content
- **Could Have:** AI-generated content suggestions based on template, template marketplace
- **Won't Have:** User-created templates in Phase 4

**Sprint:** Sprint 13

## Repository Coverage

| Repository      | Required | Notes                                                |
| --------------- | -------- | ---------------------------------------------------- |
| Backend         | ✅       | Template models, initialisation logic, GraphQL API   |
| Frontend Web    | ✅       | Template gallery, selection UI, customisation wizard |
| Frontend Mobile | ❌       | Not applicable in Phase 4                            |
| Shared UI       | ✅       | Gallery components                                   |

## Acceptance Criteria

### Scenario 1: Browse Available Templates

**Given** a user is setting up a new organisation
**When** they navigate to template selection
**Then** they see 9 template categories:

1. E-commerce (products, cart, checkout)
2. Blog (posts, categories, authors)
3. Corporate (about, services, team, contact)
4. Church (events, sermons, donations)
5. Charity (campaigns, donations, impact)
6. SaaS (pricing, features, testimonials)
7. Sole Trader (services, portfolio, booking)
8. Estate Agent (listings, search, contact)
9. Single Page App (sections, smooth scroll)
   **And** each template shows:

- Category name and icon
- Template name
- Description
- Preview image
- Premium indicator (if applicable)

### Scenario 2: Preview Template

**Given** a user is viewing template options
**When** they click on a template
**Then** they can see:

- Full-page preview (desktop, tablet, mobile views)
- Template features list
- Example content
- Pricing (if premium)
- "Select Template" button

### Scenario 3: Select Template and Customise

**Given** a user has selected a template
**When** they click "Select Template"
**Then** they proceed through a setup wizard:

1. Site name and tagline
2. Design token customisation (colours, fonts)
3. Initial content (company name, contact info, etc.)
4. Social media links
5. Optional: Initial pages and content
   **And** the wizard shows progress
   **And** they can skip optional steps
   **And** they can go back to previous steps

### Scenario 4: Template Initialisation

**Given** the user has completed the customisation wizard
**When** they click "Create Site"
**Then** the system:

- Creates the page structure for the template
- Initialises default design tokens based on template
- Creates example pages with placeholder content
- Sets up navigation structure
- Applies template-specific metadata
  **And** the user is redirected to the CMS editor
  **And** they can immediately start editing content

### Scenario 5: Template-Specific Features

**Given** the user has selected the e-commerce template
**When** initialisation completes
**Then** e-commerce specific features are enabled:

- Product model creation
- Shopping cart functionality
- Checkout process pages
- Payment integration hooks
  **And** similar setup occurs for other templates with their specific features

### Scenario 6: Example Content Replacement

**Given** a newly created site with a template
**When** the user is in the page editor
**Then** all example content can be easily:

- Edited in place
- Replaced with own content
- Deleted if not needed
  **And** placeholder images have a clear indicator
  **And** users can use default images or upload their own

## Dependencies

- US-004: Organisation Creation and Setup
- US-005: Design Token System
- Template definitions and schemas
- Page creation system

## Tasks

### Backend Tasks

- [ ] Create TemplateCategory model
- [ ] Create SiteTemplate model with fields: name, slug, description, preview_image, is_premium
- [ ] Create TemplateConfiguration model
- [ ] Define 9 template schemas (backend structure and page templates)
- [ ] Create template initialisation service
- [ ] Create GraphQL query for listing templates
- [ ] Create GraphQL query for template details
- [ ] Create GraphQL mutation for initialiseTemplate
- [ ] Implement template page creation logic
- [ ] Implement default design token creation per template
- [ ] Add template validation
- [ ] Create audit logging for template selection
- [ ] Add unit tests for template initialisation
- [ ] Add integration tests for complete setup flow
- [ ] Create database seed data for all 9 templates

### Frontend Web Tasks

- [ ] Create TemplateGallery page
- [ ] Create TemplateCategoryGrid component
- [ ] Create TemplateCard component with preview image
- [ ] Create TemplatePreview modal (full-page preview)
- [ ] Create SetupWizard component (multi-step form)
- [ ] Create SiteNameStep component
- [ ] Create DesignTokenCustomisationStep component
- [ ] Create InitialContentStep component
- [ ] Create SocialMediaLinksStep component
- [ ] Create ReviewStep component
- [ ] Implement wizard progress tracking
- [ ] Add navigation between wizard steps
- [ ] Implement form validation for each step
- [ ] Create success page after template initialisation
- [ ] Add loading indicator during template creation

### Shared UI Tasks

- [ ] Create TemplateCard component
- [ ] Create Gallery component with filtering
- [ ] Create Wizard/Stepper component
- [ ] Create PreviewModal component
- [ ] Create FormGroup component for wizard steps
- [ ] Create ProgressBar component for wizard

## Story Points (Fibonacci)

**Estimate:** 13

**Complexity factors:**

- 9 different template definitions
- Complex multi-step wizard with form state
- Template initialisation logic creating multiple pages
- Design token mapping per template
- Template-specific feature enablement
- Example content generation
- Preview image handling
- Multi-platform preview functionality

---

## Related Stories

- US-004: Organisation Creation and Setup
- US-005: Design Token System
- US-006: Create and Edit CMS Pages
- US-020: Page Rendering and Public Website
