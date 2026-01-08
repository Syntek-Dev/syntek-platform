# Refactoring Documentation

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [Refactoring Documentation](#refactoring-documentation)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [Refactoring Reports](#refactoring-reports)
    - [US-001-REPORT.md](#us-001-reportmd)
  - [What's in Refactoring Reports](#whats-in-refactoring-reports)
    - [Code Quality Metrics](#code-quality-metrics)
    - [Duplication Analysis](#duplication-analysis)
    - [Complexity Analysis](#complexity-analysis)
    - [Performance Issues](#performance-issues)
    - [Best Practice Deviations](#best-practice-deviations)
    - [Technical Debt](#technical-debt)
  - [How to Use Refactoring Reports](#how-to-use-refactoring-reports)
    - [Planning Refactoring Work](#planning-refactoring-work)
    - [During Development](#during-development)
    - [Code Review](#code-review)
    - [Technical Debt Management](#technical-debt-management)
  - [Refactoring Guidelines](#refactoring-guidelines)
    - [Project Philosophy](#project-philosophy)
    - [When to Refactor](#when-to-refactor)
    - [When NOT to Refactor](#when-not-to-refactor)
    - [Refactoring Process](#refactoring-process)
    - [Common Refactoring Patterns](#common-refactoring-patterns)
      - [Extract Method](#extract-method)
      - [Extract Variable](#extract-variable)
      - [Remove Duplication](#remove-duplication)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains refactoring documentation, including analysis of code quality issues,
refactoring opportunities, technical debt assessment, and improvement recommendations for the
codebase.

Refactoring reports are created by the Refactoring agent (`/syntek-dev-suite:refactor`) and help
maintain code quality by:

- Identifying code duplication
- Detecting complex or convoluted logic
- Finding opportunities for simplification
- Reducing technical debt
- Improving code maintainability
- Optimising performance

---

## Directory Structure

```
REFACTORING/
├── README.md                              # This file
└── US-001/                                # User story-specific refactoring reports
    └── REFACTORING-US-001-REPORT.md       # Refactoring analysis for US-001
```

---

## Refactoring Reports

### US-001-REPORT.md

**Purpose**: Comprehensive refactoring analysis for User Story 001 (User Authentication)

**Contents**:

- Code quality assessment
- Technical debt inventory
- Duplication analysis
- Complexity analysis (cyclomatic complexity, etc.)
- Performance improvement opportunities
- Code simplification suggestions
- Best practice deviations
- Refactoring priorities (high, medium, low)
- Estimated effort for each refactoring
- Risk assessment for changes
- Before/after code examples
- Implementation recommendations

**Status**: Completed

**User Story**: US-001 - User Authentication (Phase 1)

**Focus Areas**: Models, views, services, managers, utilities

---

## What's in Refactoring Reports

### Code Quality Metrics

- **Cyclomatic Complexity**: Measures code path complexity (target: < 10)
- **Lines of Code**: Tracks function/class size (functions should be < 50 lines)
- **Duplication Index**: Identifies repeated code patterns
- **Code Coverage**: Percentage of code covered by tests

### Duplication Analysis

Identifies:

- **Exact duplicates**: Same code repeated in multiple places
- **Similar code**: Nearly identical logic that could be consolidated
- **Copy-paste errors**: Duplicated code that diverged over time

**Why it matters**: DRY (Don't Repeat Yourself) principle reduces maintenance burden

### Complexity Analysis

Measures:

- **Cyclomatic complexity**: Number of independent code paths
- **Cognitive complexity**: How hard the code is to understand
- **Function length**: Lines of code per function
- **Parameter count**: Number of function parameters

**Why it matters**: Complex code is harder to test, understand, and maintain

### Performance Issues

Identifies:

- **N+1 query problems**: Inefficient database access patterns
- **Inefficient loops**: Unnecessary iterations or computations
- **Memory leaks**: Uncleaned resources
- **Blocking operations**: Synchronous operations that should be async

### Best Practice Deviations

Flags:

- **Django conventions**: Not following Django best practices
- **Python style**: PEP 8 violations beyond automated linting
- **Naming conventions**: Unclear or inconsistent naming
- **Error handling**: Missing exception handling or poor error messages
- **Security issues**: Potential vulnerabilities in code

### Technical Debt

Categorises:

- **High-interest debt**: Bugs waiting to happen
- **Medium-interest debt**: Code that will be painful to change
- **Low-interest debt**: Nice-to-have improvements

---

## How to Use Refactoring Reports

### Planning Refactoring Work

1. **Review the report** to understand identified issues
2. **Prioritise by impact**: Focus on high-complexity, high-duplication areas first
3. **Estimate effort**: Use provided estimates for sprint planning
4. **Assess risk**: Understand what could go wrong
5. **Plan testing**: Ensure refactoring won't break functionality

### During Development

1. **Check refactoring suggestions** before implementing new features
2. **Apply improvements** to related code while working in the area
3. **Avoid premature refactoring**: Only refactor when there's a good reason
4. **Keep tests green**: Refactoring should not change functionality
5. **Small changes**: Make refactoring changes in small, testable chunks

### Code Review

1. **Reference refactoring reports** when reviewing PRs
2. **Suggest improvements** based on documented issues
3. **Avoid refactoring scope creep**: Don't mix refactoring with feature work
4. **Verify tests pass**: Ensure refactoring doesn't break anything

### Technical Debt Management

1. **Prioritise high-interest debt** for next sprint
2. **Track improvements** over time
3. **Monitor trends**: Are complexity metrics improving?
4. **Set targets**: Aim for complexity < 10, functions < 50 lines

---

## Refactoring Guidelines

### Project Philosophy

This project follows **strict refactoring guidelines** based on the principle of minimal,
purposeful code changes:

**CRITICAL**: Only refactor when there's measurable benefit and a good reason.

### When to Refactor

Refactor ONLY when:

1. **There's code duplication** - Same logic appears in 3+ places
2. **Function exceeds 50 lines** - Too complex to understand easily
3. **Cyclomatic complexity > 10** - Too many code paths
4. **You're working in the area** - Improve code while making related changes
5. **Explicitly requested** - During a dedicated refactoring task
6. **Performance issues** - Measurable performance improvement available

### When NOT to Refactor

Do NOT refactor:

- **Working code "just to improve it"** - If it works, leave it alone
- **Code not part of the current task** - Stay focused on the feature
- **To add "future-proofing"** - Only abstract when there's actual repetition
- **Speculative optimisation** - Profile first, optimise second
- **Near a deadline** - Refactoring increases risk near releases
- **Someone else's code** - Unless explicitly asked to improve it

### Refactoring Process

```
1. Ensure tests are passing and comprehensive
2. Make one small, focused change
3. Run tests - they should still pass
4. Commit with clear message explaining change
5. Repeat for each refactoring
```

**Golden Rule**: Tests should never break during refactoring. If they do, revert and reconsider.

### Common Refactoring Patterns

#### Extract Method

When a function is too long, extract logical sections into helper functions:

```python
# Before: 80-line function
def process_user_registration(email, password):
    # validation logic... (20 lines)
    # user creation logic... (20 lines)
    # email sending logic... (20 lines)
    # logging logic... (20 lines)
    pass

# After: Modularised with helper methods
def process_user_registration(email, password):
    validate_input(email, password)
    user = create_user(email, password)
    send_verification_email(user)
    log_registration(user)
```

#### Extract Variable

When an expression is repeated, extract it to a named variable:

```python
# Before: Unclear what calculation means
if user.created_at + timedelta(days=30) < timezone.now():
    # user is old enough for action
    pass

# After: Named variable explains intent
days_since_registration = timezone.now() - user.created_at
if days_since_registration > timedelta(days=30):
    # user is old enough for action
    pass
```

#### Remove Duplication

When the same logic appears multiple times, consolidate it:

```python
# Before: Duplicated query logic
def get_active_users_in_org(org_id):
    return User.objects.filter(
        organisation_id=org_id,
        is_active=True
    ).select_related('organisation')

def get_org_admins(org_id):
    return User.objects.filter(
        organisation_id=org_id,
        is_active=True
    ).select_related('organisation')

# After: Use a manager method
class UserQuerySet(QuerySet):
    def for_organisation(self, org_id):
        return self.filter(
            organisation_id=org_id,
            is_active=True
        ).select_related('organisation')

def get_active_users_in_org(org_id):
    return User.objects.for_organisation(org_id)

def get_org_admins(org_id):
    return User.objects.for_organisation(org_id).filter(role='admin')
```

---

## Related Documentation

- [Code Quality Standards](../../.claude/CLAUDE.md#code-quality-principles) - Project code quality
  philosophy
- [Testing Documentation](../TESTS/) - Testing strategy and coverage
- [Architecture](../ARCHITECTURE/) - System design and patterns
- [User Stories](../STORIES/) - Feature requirements for context

---

**Project:** Backend Template
**Framework:** Django 5.2
**Quality Tool**: Manual refactoring analysis + automated metrics
**Last Updated:** 08/01/2026
