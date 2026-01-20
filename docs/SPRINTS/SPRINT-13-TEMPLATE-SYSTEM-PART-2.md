# Sprint 13: Template System (Part 2)

<!-- CLICKUP_LIST_ID: 901519464127 -->

**Sprint Duration:** 23/06/2026 - 07/07/2026 (2 weeks)
**Capacity:** 2/11 points (9 points buffer)
**Status:** Planned

---

## Overview

This sprint completes the template system by implementing the customisation wizard, template preview refinements, and additional template features. Before template initialisation, users progress through a guided 5-step wizard to customise site name, design tokens, initial content, and social media links. This personalisation ensures templates reflect each business's branding and details. The sprint also enables template switching post-initialisation and provides comparison tools to help users select the right template. A large point buffer allows flexibility for additional template types, video tutorials, and extended testing.

---

## Sprint Goal

Complete the template system by implementing the customisation wizard, template preview refinements,
and additional template features. This sprint finalises the rapid website creation experience.

---

## MoSCoW Breakdown

### Must Have (2 points)

| Story ID                                       | Title                    | Points | Status  |
| ---------------------------------------------- | ------------------------ | ------ | ------- |
| [US-008](../STORIES/US-008-TEMPLATE-SYSTEM.md) | Template System (Part 2) | 2      | Pending |

_US-008 completion: 2 points for customisation wizard, template switching, and polish features_

### Should Have (0 points)

_None in this sprint_

### Could Have (0 points)

_None in this sprint_

---

## Dependencies

| Story  | Depends On | Notes                                          |
| ------ | ---------- | ---------------------------------------------- |
| US-008 | Sprint 12  | Core template system and 9 templates completed |

**Dependencies satisfied:** US-008 Part 1 completed in Sprint 12.

---

## Implementation Order

### Week 1 (23/06 - 30/06)

1. **Customisation Wizard (Priority 1)**
   - Frontend Web: SetupWizard component for template customisation
   - Frontend Web: SiteNameStep (site name, tagline)
   - Frontend Web: DesignTokenCustomisationStep (colours, fonts)
   - Frontend Web: InitialContentStep (company name, contact info)
   - Frontend Web: SocialMediaLinksStep
   - Frontend Web: Wizard progress indicator
   - Backend: Store wizard responses before initialisation
   - Backend: Apply customisations during initialisation

**Milestone:** Users can customise template before initialisation

### Week 2 (30/06 - 07/07)

2. **Polish and Testing (Priority 2)**
   - Frontend Web: Template switching capability (change template post-initialisation)
   - Frontend Web: Template comparison view
   - Frontend Web: Template success page with next steps
   - Backend: Template validation checks
   - Testing: End-to-end template initialisation tests
   - Testing: Template switching tests
   - Documentation: Template customisation guide
   - Documentation: Video tutorials per template

**Milestone:** Template system is complete and polished

---

## Repository Breakdown

| Story  | Backend | Frontend Web | Frontend Mobile | Shared UI |
| ------ | ------- | ------------ | --------------- | --------- |
| US-008 | ✅      | ✅           | ❌              | ✅        |

**3 repositories** will be active this sprint (Backend, Frontend Web, Shared UI).

---

## Technical Focus

### Backend

- **Wizard State:** Store customisation responses before initialisation
- **Customisation Application:** Apply user settings to template
- **Template Switching:** Migrate content when changing templates
- **Validation:** Ensure required customisations are provided

### Frontend Web

- **Multi-Step Wizard:** Guided customisation flow
- **Template Switching:** UI for changing templates post-initialisation
- **Success Page:** Clear next steps after template initialisation
- **Comparison Tool:** Compare templates side-by-side

### Shared UI

- **Wizard Components:** Stepper, form steps, progress bar
- **Customisation Forms:** Site info, design tokens, social links
- **Comparison:** Template comparison grid

---

## Risks & Mitigations

| Risk                               | Likelihood | Impact | Mitigation                                             |
| ---------------------------------- | ---------- | ------ | ------------------------------------------------------ |
| Template switching data loss       | Medium     | High   | Warn user of data loss, backup before switching        |
| Wizard complexity confusing users  | Low        | Medium | Simple 4-5 step wizard with clear instructions         |
| Customisation options overwhelming | Medium     | Low    | Provide sensible defaults, make steps optional         |
| Large buffer may slow progress     | Low        | Low    | Use buffer for technical debt and additional templates |

---

## Acceptance Criteria Summary

### US-008: Template System (Part 2)

- [ ] Customisation wizard appears after template selection
- [ ] Wizard shows 5 steps with progress indicator
- [ ] Step 1: Site name and tagline
- [ ] Step 2: Design token customisation (primary colour, font)
- [ ] Step 3: Initial content (company name, contact email, phone)
- [ ] Step 4: Social media links (Facebook, Twitter, LinkedIn, Instagram)
- [ ] Step 5: Review and confirm
- [ ] User can navigate back to previous steps
- [ ] User can skip optional steps
- [ ] Wizard stores responses before initialisation
- [ ] Customisations are applied during template initialisation
- [ ] Success page shows next steps (edit pages, add content, publish)
- [ ] Template switching option available in settings
- [ ] Template switching warns of potential data loss
- [ ] Template comparison view shows features side-by-side
- [ ] Video tutorials available per template
- [ ] Documentation explains each template type

**Completed from Sprint 12:**

- ✅ 9 templates defined and operational
- ✅ Template gallery and preview functional
- ✅ Template initialisation working
- ✅ Default design tokens applied

---

## Definition of Done

- [ ] All acceptance criteria met for US-008 (Part 2)
- [ ] Unit tests pass (>80% coverage)
- [ ] Integration tests pass for wizard flow
- [ ] Template switching tests pass
- [ ] Code reviewed and merged to main
- [ ] Documentation updated (wizard guide, video tutorials)
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
  - Additional template types (if requested)
  - Template preview improvements
  - Video tutorial creation
  - Template marketplace foundation
  - Extended testing and polish
  - Technical debt from Sprint 12
- Customisation wizard steps:
  1. **Site Info:** Name, tagline, description
  2. **Design:** Primary/secondary colours, font selection
  3. **Content:** Company name, email, phone, address
  4. **Social:** Facebook, Twitter, LinkedIn, Instagram, YouTube
  5. **Review:** Summary of choices, confirm to proceed
- Template switching considerations:
  - Backup current site before switching
  - Map content to new template structure
  - Warn user of incompatible features
  - Provide preview before confirming switch
  - Log template changes in audit log
- Success page next steps:
  1. Customise pages and content
  2. Upload images to media library
  3. Connect integrations (payments, email)
  4. Invite team members
  5. Preview and publish site
- Video tutorial topics per template:
  - Template overview and features
  - Customising design tokens
  - Editing page content
  - Adding products/posts/services (template-specific)
  - Publishing your site
- Template comparison criteria:
  - Number of pages included
  - Key features (e-commerce, blog, booking)
  - Complexity level (beginner, intermediate, advanced)
  - Industry focus
  - Recommended for (use cases)

**Sprint 14 Preparation:**

- Shared UI component library ready
- Templates consume components from library
- Design token integration complete

---

_Last Updated: 06/01/2026_
_Sprint Owner: Development Team_
