# Sprint 12: Template System (Part 1)

<!-- CLICKUP_LIST_ID: 901519464125 -->

**Sprint Duration:** 09/06/2026 - 23/06/2026 (2 weeks)
**Capacity:** 11/11 points (at capacity)
**Status:** Planned

---

## Sprint Goal

Implement the site template system providing 9 pre-built templates (e-commerce, blog, corporate,
church, charity, SaaS, sole trader, estate agent, single page) with selection UI and initialisation
logic. This sprint enables rapid website creation with industry-specific structures.

---

## MoSCoW Breakdown

### Must Have (11 points)

| Story ID                                       | Title                    | Points | Status  |
| ---------------------------------------------- | ------------------------ | ------ | ------- |
| [US-008](../STORIES/US-008-TEMPLATE-SYSTEM.md) | Template System (Part 1) | 11     | Pending |

_US-008 split: 11 points for template definitions, selection UI, and initialisation logic this
sprint, 2 points for customisation wizard and polish in Sprint 13_

### Should Have (0 points)

_None in this sprint_

### Could Have (0 points)

_None in this sprint_

---

## Dependencies

| Story  | Depends On     | Notes                                          |
| ------ | -------------- | ---------------------------------------------- |
| US-008 | US-004, US-005 | Organisation setup and design tokens completed |

**Dependencies satisfied:** Organisation setup (Sprint 3) and design tokens (Sprint 6) are complete.

---

## Implementation Order

### Week 1 (09/06 - 16/06)

1. **Template Models and Definitions (Priority 1)**
   - Backend: TemplateCategory model
   - Backend: SiteTemplate model (name, slug, description, preview image)
   - Backend: TemplateConfiguration model
   - Backend: Define 9 template schemas:
     1. E-commerce (products, cart, checkout)
     2. Blog (posts, categories, authors)
     3. Corporate (about, services, team, contact)
     4. Church (events, sermons, donations)
     5. Charity (campaigns, donations, impact)
     6. SaaS (pricing, features, testimonials)
     7. Sole Trader (services, portfolio, booking)
     8. Estate Agent (listings, search, contact)
     9. Single Page (sections, smooth scroll)
   - Backend: Template initialisation service
   - Backend: Default design token sets per template
   - Backend: GraphQL query for listing templates
   - Backend: GraphQL query for template details
   - Backend: GraphQL mutation for initialiseTemplate

**Milestone:** All 9 templates are defined with schemas and default content

### Week 2 (16/06 - 23/06)

2. **Template Selection and Initialisation (Priority 2)**
   - Frontend Web: TemplateGallery page
   - Frontend Web: TemplateCategoryGrid component
   - Frontend Web: TemplateCard with preview images
   - Frontend Web: TemplatePreview modal (desktop/tablet/mobile views)
   - Frontend Web: Template selection flow
   - Backend: Template page creation logic (create pages based on template)
   - Backend: Default content generation per template
   - Backend: Navigation structure creation
   - Testing: Template initialisation tests
   - Documentation: Template system guide

**Milestone:** Users can browse, preview, and initialise templates

---

## Repository Breakdown

| Story  | Backend | Frontend Web | Frontend Mobile | Shared UI |
| ------ | ------- | ------------ | --------------- | --------- |
| US-008 | ✅      | ✅           | ❌              | ✅        |

**3 repositories** will be active this sprint (Backend, Frontend Web, Shared UI).

---

## Technical Focus

### Backend

- **Template Definitions:** 9 complete template schemas with page structures
- **Initialisation Service:** Create pages, navigation, default content
- **Design Token Mapping:** Each template has default design tokens
- **Page Creation:** Generate pages based on template structure
- **Content Generation:** Industry-specific placeholder content

### Frontend Web

- **Template Gallery:** Browse all 9 templates by category
- **Preview System:** View templates on desktop/tablet/mobile
- **Selection UI:** Clear selection and confirmation flow
- **Category Filtering:** Filter templates by industry

### Shared UI

- **TemplateCard:** Preview card component
- **Gallery:** Grid layout for templates
- **PreviewModal:** Full-page preview component

---

## Risks & Mitigations

| Risk                                           | Likelihood | Impact | Mitigation                                                    |
| ---------------------------------------------- | ---------- | ------ | ------------------------------------------------------------- |
| Template definitions take longer than expected | High       | High   | Focus on 3 core templates first (e-commerce, blog, corporate) |
| Default content needs design input             | Medium     | Medium | Use industry-standard placeholder content                     |
| Template initialisation complexity             | Medium     | High   | Start with simple page creation, defer advanced features      |
| Preview images need professional design        | Medium     | Low    | Use screenshots of completed templates or placeholders        |
| Template-specific features (e.g., cart)        | High       | Medium | Defer feature implementation, focus on page structure         |

---

## Acceptance Criteria Summary

### US-008: Template System (Part 1)

- [ ] 9 template categories are available
- [ ] Each template shows name, description, preview image
- [ ] Template gallery displays all templates
- [ ] Template cards show category icon and name
- [ ] Preview modal shows desktop/tablet/mobile views
- [ ] Template features list is displayed in preview
- [ ] Select Template button initialises template
- [ ] Template initialisation creates pages based on schema:
  - E-commerce: Home, Products, Product Detail, Cart, Checkout
  - Blog: Home, Blog List, Post Detail, About, Contact
  - Corporate: Home, About, Services, Team, Contact
  - Church: Home, About, Events, Sermons, Donate, Contact
  - Charity: Home, About, Campaigns, Donate, Impact, Contact
  - SaaS: Home, Features, Pricing, Testimonials, Contact, Sign Up
  - Sole Trader: Home, Services, Portfolio, About, Contact, Book
  - Estate Agent: Home, Properties, Property Detail, About, Contact
  - Single Page: Home (with sections: Hero, Features, About, Services, Contact)
- [ ] Default design tokens are applied per template
- [ ] Navigation structure is created based on template
- [ ] Placeholder content is industry-specific
- [ ] Template initialisation is logged in audit logs
- [ ] Only one template can be selected per organisation

**Deferred to Sprint 13:**

- Customisation wizard
- Template content customisation before initialisation
- Template switching after initialisation
- Advanced template features

---

## Definition of Done

- [ ] All acceptance criteria met for US-008 (Part 1)
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass for template initialisation
- [ ] All 9 templates tested and validated
- [ ] Code reviewed and merged to main
- [ ] Documentation updated (template guide, page structures)
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
| Templates Created | 9      | -      |

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

- Template definitions (page structures):

**1. E-commerce**

- Home, Products List, Product Detail, Cart, Checkout, Account
- Focus: Product showcase, shopping experience

**2. Blog**

- Home, Blog List, Post Detail, Category, Author, About, Contact
- Focus: Content publishing, readability

**3. Corporate**

- Home, About, Services, Service Detail, Team, Case Studies, Contact
- Focus: Professional presence, trust building

**4. Church**

- Home, About, Events, Event Detail, Sermons, Donate, Contact
- Focus: Community engagement, event management

**5. Charity**

- Home, About, Campaigns, Campaign Detail, Donate, Impact, Get Involved, Contact
- Focus: Fundraising, transparency

**6. SaaS**

- Home, Features, Pricing, Testimonials, Blog, Help, Contact, Sign Up
- Focus: Feature showcase, conversion

**7. Sole Trader**

- Home, Services, Portfolio, Portfolio Item, About, Testimonials, Contact, Book Now
- Focus: Personal brand, service showcase

**8. Estate Agent**

- Home, Properties, Property Detail, About, Team, Valuation, Contact
- Focus: Property listings, search

**9. Single Page**

- Home (sections: Hero, Features, About, Services, Portfolio, Testimonials, Contact)
- Focus: All content on one page, smooth scrolling

- Default design tokens per template:
  - E-commerce: Modern, trust-building (blue, white)
  - Blog: Readable, elegant (serif fonts, neutral colours)
  - Corporate: Professional, authoritative (navy, grey)
  - Church: Welcoming, traditional (warm colours)
  - Charity: Compassionate, impactful (green, orange)
  - SaaS: Modern, tech-forward (purple, gradients)
  - Sole Trader: Personal, approachable (varied by service)
  - Estate Agent: Premium, trustworthy (gold, grey)
  - Single Page: Modern, creative (varied)

- Template initialisation flow:
  1. User selects template
  2. System creates page records
  3. System applies default design tokens
  4. System generates placeholder content
  5. System creates navigation structure
  6. System redirects to page editor
  7. User can customise content

**Sprint 13 Preparation:**

- Customisation wizard for pre-initialisation settings
- Template switching capability
- Content import/migration between templates

---

_Last Updated: 06/01/2026_
_Sprint Owner: Development Team_
