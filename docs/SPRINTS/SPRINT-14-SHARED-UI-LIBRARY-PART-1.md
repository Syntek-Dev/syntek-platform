# Sprint 14: Shared UI Component Library (Part 1)

<!-- CLICKUP_LIST_ID: 901519464129 -->

**Sprint Duration:** 07/07/2026 - 21/07/2026 (2 weeks)
**Capacity:** 11/11 points (at capacity)
**Status:** Planned

---

## Sprint Goal

Build the core shared UI component library with base components, form components, and layout
components. This sprint establishes the foundation for consistent interfaces across web
and mobile applications.

---

## MoSCoW Breakdown

### Must Have (11 points)

| Story ID                                         | Title                      | Points | Status  |
| ------------------------------------------------ | -------------------------- | ------ | ------- |
| [US-019](../STORIES/US-019-SHARED-UI-LIBRARY.md) | Shared UI Library (Part 1) | 11     | Pending |

_US-019 split: 11 points for base components, form components, and layout components this sprint,
10 points for navigation, data display, and Storybook in Sprint 15_

### Should Have (0 points)

_None in this sprint_

### Could Have (0 points)

_None in this sprint_

---

## Dependencies

| Story  | Depends On | Notes                         |
| ------ | ---------- | ----------------------------- |
| US-019 | US-005     | Design token system completed |

**Dependencies satisfied:** Design tokens (Sprint 6) are complete.

---

## Implementation Order

### Week 1 (07/07 - 14/07)

1. **Base Components (Priority 1)**
   - Shared UI: Button component (primary, secondary, tertiary, sizes, states)
   - Shared UI: Input component (text, email, password, validation, error states)
   - Shared UI: Card component (simple, with header/footer)
   - Shared UI: Modal component (dialog with overlay)
   - Shared UI: Alert component (success, warning, error, info)
   - Shared UI: Badge component (label with variants)
   - Shared UI: Spinner component (loading indicator)
   - Shared UI: Tooltip component (hover help text)
   - Shared UI: Avatar component (user profile image)
   - Shared UI: Divider component (separator line)

**Milestone:** 10 base components operational with full TypeScript support

### Week 2 (14/07 - 21/07)

2. **Form and Layout Components (Priority 2)**
   - Shared UI: TextField component (input with label and validation)
   - Shared UI: Select component (dropdown with search)
   - Shared UI: Checkbox component (single and multi-select)
   - Shared UI: Radio component (radio button groups)
   - Shared UI: TextArea component (multi-line input)
   - Shared UI: FileInput component (file upload)
   - Shared UI: Form wrapper component
   - Shared UI: Container component (fixed/fluid width)
   - Shared UI: Grid component (CSS Grid layout)
   - Shared UI: Stack component (flexbox spacing)
   - Shared UI: Center component
   - Shared UI: useDesignTokens hook
   - Shared UI: useMediaQuery hook
   - Shared UI: useTheme hook

**Milestone:** Form and layout components complete with design token integration

---

## Repository Breakdown

| Story  | Backend | Frontend Web | Frontend Mobile | Shared UI |
| ------ | ------- | ------------ | --------------- | --------- |
| US-019 | ❌      | ✅           | ✅              | ✅        |

**3 repositories** will be active this sprint (Frontend Web, Frontend Mobile, Shared UI).

---

## Technical Focus

### Shared UI

- **Base Components:** Essential UI building blocks with variants
- **Form Components:** Comprehensive form building system
- **Layout Components:** Responsive layout primitives
- **TypeScript:** Full type safety for all components
- **Design Tokens:** Integration with backend token system
- **Accessibility:** ARIA labels, keyboard navigation, focus management
- **Responsive:** Mobile-first responsive design
- **Testing:** Unit tests for all components (>80% coverage)

### Frontend Web

- **Consumption:** Use components from shared UI library
- **Integration Testing:** Ensure components work in web context

### Frontend Mobile

- **NativeWind:** Mobile versions of all components
- **Touch Optimisation:** Mobile-friendly interactions

---

## Risks & Mitigations

| Risk                                        | Likelihood | Impact | Mitigation                                              |
| ------------------------------------------- | ---------- | ------ | ------------------------------------------------------- |
| Component API design decisions take time    | High       | Medium | Follow established patterns (Radix UI, Chakra UI, MUI)  |
| TypeScript complexity                       | Medium     | Medium | Use simple, clear prop types, provide examples          |
| Accessibility requirements slow development | Medium     | High   | Use established a11y patterns, test with screen readers |
| Mobile/web component parity difficult       | High       | High   | Focus on web first, defer mobile to testing phases      |
| Design token integration complexity         | Medium     | Medium | Create simple token consumption hooks                   |

---

## Acceptance Criteria Summary

### US-019: Shared UI Library (Part 1)

**Base Components (10):**

- [ ] Button: Primary, secondary, tertiary variants with sizes and disabled states
- [ ] Input: Text, email, password with validation and error states
- [ ] Card: Simple container with optional header/footer
- [ ] Modal: Dialog with overlay and customisable content
- [ ] Alert: Success, warning, error, info variants
- [ ] Badge: Label component with colour variants
- [ ] Spinner: Loading indicator with sizes
- [ ] Tooltip: Hover-triggered help text
- [ ] Avatar: User profile image with fallback initials
- [ ] Divider: Horizontal/vertical separator line

**Form Components (7):**

- [ ] TextField: Input with label and validation
- [ ] Select: Dropdown with search capability
- [ ] Checkbox: Single and multi-select
- [ ] Radio: Radio button groups
- [ ] TextArea: Multi-line input
- [ ] FileInput: File upload with drag-and-drop
- [ ] Form: Form wrapper with validation

**Layout Components (4):**

- [ ] Container: Fixed/fluid width wrapper
- [ ] Grid: CSS Grid-based layout
- [ ] Stack: Flexbox horizontal/vertical spacing
- [ ] Center: Center content component

**Hooks (3):**

- [ ] useDesignTokens: Access design tokens from backend
- [ ] useMediaQuery: Responsive breakpoint detection
- [ ] useTheme: Theme switching (light/dark)

**Quality:**

- [ ] All components have TypeScript types
- [ ] All components are accessible (ARIA labels, keyboard nav)
- [ ] All components are responsive
- [ ] Unit tests pass (>80% coverage per component)
- [ ] Components consume design tokens

**Deferred to Sprint 15:**

- Navigation components (NavBar, Sidebar, Breadcrumb, Tabs, Pagination)
- Data display components (Table, List, EmptyState, Skeleton)
- DatePicker component
- Storybook documentation
- Mobile (NativeWind) versions

---

## Definition of Done

- [ ] All acceptance criteria met for US-019 (Part 1)
- [ ] Unit tests pass (>80% coverage)
- [ ] Accessibility tests pass
- [ ] TypeScript builds without errors
- [ ] Code reviewed and merged to main
- [ ] Documentation updated (component API docs)
- [ ] Published to npm (if separate package)
- [ ] Web and mobile apps can consume components
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
| Components        | 21     | -      |

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

- Component library architecture:
  - Single shared UI repository
  - Exported as npm package (or workspace)
  - Web and mobile apps import from package
  - Design tokens fetched from backend via GraphQL
- Component API design principles:
  - Simple, clear prop names
  - Sensible defaults
  - Composable (can be nested)
  - Extensible (className support for custom styles)
  - Consistent naming across all components
- Accessibility requirements (WCAG 2.1 AA):
  - Keyboard navigation for all interactive elements
  - ARIA labels for screen readers
  - Focus indicators
  - Colour contrast ratios (4.5:1 for text)
  - Skip links for navigation
- Testing strategy:
  - Unit tests with Jest and React Testing Library
  - Visual regression tests (Chromatic or Percy)
  - Accessibility tests (jest-axe)
  - Snapshot tests for UI consistency
- Design token consumption:
  <!-- prettier-ignore -->
  ```tsx
  const { colors, spacing, typography } = useDesignTokens();
  return <Button style={{ background: colors.primary }}>Click</Button>
  ```
- Component composition example:
  ```jsx
  <Card>
    <Card.Header>
      <Typography variant="h3">Card Title</Typography>
    </Card.Header>
    <Card.Body>
      <Text>Card content goes here</Text>
    </Card.Body>
    <Card.Footer>
      <Button>Action</Button>
    </Card.Footer>
  </Card>
  ```

**Sprint 15 Preparation:**

- Storybook setup and configuration
- Navigation components design
- Data display components design
- Mobile (NativeWind) conversion strategy

---

_Last Updated: 06/01/2026_
_Sprint Owner: Development Team_
