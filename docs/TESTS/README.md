# Tests

## Table of Contents

- [Tests](#tests)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Tree](#directory-tree)
  - [Folders](#folders)
  - [Related Documentation](#related-documentation)

---

## Overview

This folder contains comprehensive testing documentation for the backend template project. It includes testing strategy reviews, test coverage analysis, and testing recommendations for all user stories and features.

The testing documentation covers:

- Unit testing with pytest (TDD approach)
- Behaviour-Driven Development with pytest-bdd and Gherkin syntax
- Integration testing strategies
- End-to-End (E2E) testing approaches
- GraphQL API testing
- Security testing and validation
- Test coverage analysis and targets
- Missing test scenarios and recommendations

---

## Directory Tree

```
TESTS/
├── README.md                                    # This file
└── REVIEWS/
    ├── US-001-TESTING-REVIEW-CONSOLIDATED.md  # Consolidated review for US-001
    └── US-001/                                 # Individual reviews directory
```

---

## Folders

| Folder     | Purpose                                                     |
| ---------- | ----------------------------------------------------------- |
| `REVIEWS/` | Testing reviews and strategy documentation for user stories |

---

## Related Documentation

For detailed testing standards and implementation guidelines, see:

- [../README.md](../README.md) - Documentation index
- [../../.claude/CLAUDE.md](../../.claude/CLAUDE.md) - Project testing standards section
- [../PLANS/US-001-USER-AUTHENTICATION.md](../PLANS/US-001-USER-AUTHENTICATION.md) - US-001 detailed plan
