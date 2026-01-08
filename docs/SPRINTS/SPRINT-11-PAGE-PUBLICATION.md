# Sprint 11: Page Publication and Public Website

<!-- CLICKUP_LIST_ID: 901519464122 -->

**Sprint Duration:** 26/05/2026 - 09/06/2026 (2 weeks)
**Capacity:** 8/11 points (3 points buffer)
**Status:** Planned

---

## Overview

This sprint implements page publication workflow enabling content to go live on public websites with proper routing, SEO metadata, and sitemap generation. Published pages are rendered beautifully using organisation design tokens and block renderers. The system supports URL redirects for changed slugs, generates dynamic sitemaps, and includes comprehensive SEO validation. Content remains editable in draft branches while published production pages are immutable, providing a complete separation between editing and live content.

---

## Sprint Goal

Implement page publication workflow enabling content to go live on public websites with proper
routing, SEO metadata, and sitemap generation. This sprint makes content publicly accessible
to visitors.

---

## MoSCoW Breakdown

### Must Have (8 points)

| Story ID                                        | Title            | Points | Status  |
| ----------------------------------------------- | ---------------- | ------ | ------- |
| [US-010](../STORIES/US-010-PAGE-PUBLICATION.md) | Page Publication | 8      | Pending |

### Should Have (0 points)

_None in this sprint_

### Could Have (0 points)

_None in this sprint_

---

## Dependencies

| Story  | Depends On     | Notes                                             |
| ------ | -------------- | ------------------------------------------------- |
| US-010 | US-006, US-007 | CMS page creation and content branching completed |

**Dependencies satisfied:** CMS page creation (Sprint 8) and content branching (Sprint 10) are complete.

---

## Implementation Order

### Week 1 (26/05 - 02/06)

1. **Publication Backend (Priority 1)**
   - Backend: published_at field on Page model
   - Backend: is_published boolean field
   - Backend: publishPage GraphQL mutation
   - Backend: unpublishPage GraphQL mutation
   - Backend: Public page query (published pages only)
   - Backend: URL routing for published pages
   - Backend: 404 handling for unpublished pages
   - Backend: Redirect model for URL redirects
   - Backend: Redirect checking middleware
   - Backend: Sitemap generation service
   - Backend: Publication notifications
   - Backend: Metadata validation before publishing

**Milestone:** Pages can be published and accessed via public URLs

### Week 2 (02/06 - 09/06)

2. **Public Website Rendering (Priority 2)**
   - Frontend Web: PageRenderer component for public display
   - Frontend Web: Responsive block rendering
   - Frontend Web: Public page layout with header/footer
   - Frontend Web: Meta tag rendering (title, description, og tags)
   - Frontend Web: 404 error page
   - Frontend Web: Publish confirmation dialog in editor
   - Frontend Web: Publication status indicator
   - Frontend Web: Preview-as-public feature
   - Shared UI: BlockRenderer components (8 types)
   - Shared UI: PublicLayout component
   - Testing: Public rendering tests
   - Documentation: Publication workflow guide

**Milestone:** Published pages are rendered beautifully on public website

---

## Repository Breakdown

| Story  | Backend | Frontend Web | Frontend Mobile | Shared UI |
| ------ | ------- | ------------ | --------------- | --------- |
| US-010 | ✅      | ✅           | ✅              | ✅        |

**All 4 repositories** will be active this sprint.

---

## Technical Focus

### Backend

- **Publication Workflow:** Mark pages as published with timestamp
- **Public Routing:** Dynamic URL routing for published pages
- **SEO:** Sitemap.xml generation with all published pages
- **Redirects:** 301 redirects for changed URLs
- **Validation:** Ensure required metadata before publishing

### Frontend Web

- **Page Rendering:** Convert blocks to public HTML
- **SEO Meta Tags:** Title, description, Open Graph, Twitter cards
- **Layout:** Public website layout with navigation
- **Responsive:** Mobile-friendly public pages
- **Performance:** Fast page loads, optimised assets

### Frontend Mobile

- **Public View:** View published pages in mobile app
- **Responsive:** Native rendering of public content

### Shared UI

- **Block Renderers:** Public display for all block types
- **Layout Components:** Header, footer, navigation
- **SEO Components:** Meta tag generation

---

## Risks & Mitigations

| Risk                               | Likelihood | Impact | Mitigation                                              |
| ---------------------------------- | ---------- | ------ | ------------------------------------------------------- |
| SEO meta tags missing or incorrect | Medium     | High   | Validate metadata before publishing, provide defaults   |
| Published pages load slowly        | Medium     | High   | Implement caching, optimise images, lazy load blocks    |
| URL routing conflicts              | Low        | Medium | Validate slug uniqueness per organisation               |
| 404 pages not branded              | Low        | Low    | Create custom 404 page using organisation design tokens |
| Sitemap too large (10000+ pages)   | Low        | Medium | Paginate sitemap, create sitemap index                  |

---

## Acceptance Criteria Summary

### US-010: Page Publication

- [ ] Publish button marks page as published
- [ ] Published pages have published_at timestamp
- [ ] Production branch is updated on publish
- [ ] Audit log tracks publication events
- [ ] Unpublish button removes page from public access
- [ ] Published pages accessible via URL (e.g., /about)
- [ ] Unpublished pages return 404
- [ ] Correct template is used for rendering
- [ ] Design tokens are applied to public pages
- [ ] Meta tags included (title, description, og tags)
- [ ] Sitemap.xml generated with all published pages
- [ ] Sitemap includes last modified date
- [ ] URL redirects work (301 for changed slugs)
- [ ] Redirect model tracks old → new URL mappings
- [ ] Version history retained for published pages
- [ ] Publication notifications sent to team
- [ ] Preview-as-public works in editor
- [ ] All block types render correctly on public site
- [ ] Public pages are mobile-responsive
- [ ] 404 page is styled with organisation branding

---

## Definition of Done

- [ ] All acceptance criteria met for US-010
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass for publication workflow
- [ ] Public rendering tests pass
- [ ] SEO validation tests pass
- [ ] Performance tests pass (<2s page load)
- [ ] Code reviewed and merged to main
- [ ] Documentation updated (publication guide, SEO guide)
- [ ] Deployed to development environment
- [ ] QA tested on dev environment
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
| Page Load Speed   | <2s    | -      |

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

- SEO meta tags requirements:
  - **Title:** 50-60 characters (validate)
  - **Description:** 150-160 characters (validate)
  - **Open Graph tags:** og:title, og:description, og:image, og:url
  - **Twitter cards:** twitter:card, twitter:title, twitter:description, twitter:image
  - **Canonical URL:** Prevent duplicate content issues
- Sitemap.xml format:
  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
      <loc>https://example.com/about</loc>
      <lastmod>2026-05-01</lastmod>
      <changefreq>monthly</changefreq>
      <priority>0.8</priority>
    </url>
  </urlset>
  ```
- URL routing structure:
  - Homepage: `/`
  - Standard pages: `/about`, `/contact`, `/services`
  - Blog posts: `/blog/post-slug`
  - Nested pages: `/services/web-design`
  - Dynamic routing based on page slug
- Redirect types:
  - **301 Permanent:** Page URL changed permanently
  - **302 Temporary:** Temporary redirect (use sparingly)
  - **410 Gone:** Page permanently deleted
- Block rendering on public site:
  - All blocks render with design tokens applied
  - Images use responsive srcset
  - Videos are lazy-loaded
  - CTAs include analytics tracking
  - Links open in new tab if external
- Public page caching:
  - Cache rendered HTML for 1 hour
  - Invalidate on page republish
  - Use Redis for cache storage
  - Cache key: `page:{slug}:{branch}`
- Performance optimisations:
  - Minify HTML/CSS/JS
  - Compress images (WebP with fallback)
  - Lazy load images below fold
  - Inline critical CSS
  - Defer non-critical JavaScript
- 404 page requirements:
  - Use organisation design tokens
  - Show navigation back to homepage
  - Show search box for other pages
  - Track 404s for broken link detection

**Sprint 12 Preparation:**

- Template system ready
- 9 site templates defined
- Template selection initialises pages with default content

---

_Last Updated: 06/01/2026_
_Sprint Owner: Development Team_
