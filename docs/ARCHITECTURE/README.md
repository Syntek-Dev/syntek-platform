# Architecture Documentation

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [Architecture Documentation](#architecture-documentation)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [Key Documents](#key-documents)
    - [CMS-PLATFORM-PLAN.md](#cms-platform-planmd)
    - [US-001/ (User Story-Specific Architecture)](#us-001-user-story-specific-architecture)
  - [Platform Phases](#platform-phases)
  - [Related Documentation](#related-documentation)

---

## Directory Structure

```
ARCHITECTURE/
├── README.md                # This file
├── CMS-PLATFORM-PLAN.md     # Comprehensive 16-phase architecture plan
└── US-001/                  # User story-specific architecture docs
    └── [Architecture docs for US-001]
```

---

## Key Documents

### CMS-PLATFORM-PLAN.md

**Comprehensive platform architecture** covering:

- Platform vision and strategic goals
- 16-phase development roadmap
- Multi-repository architecture (backend, UI library, frontend web, mobile)
- Multi-tenancy design and isolation
- Design token system
- Content branching workflow (feature → testing → dev → staging → production)
- 9 site templates (e-commerce, blog, corporate, church, charity, SaaS, sole trader,
  estate agent, single page)
- SaaS product integrations (email service, cloud documents, password manager)
- AI integration (Anthropic Claude)
- Environment variable management
- Initial setup wizard
- Deployment pipeline
- Platform upgrade system

**Use this when:**

- Designing new features
- Understanding system architecture
- Planning implementation phases
- Reviewing multi-tenant design
- Understanding content branching workflow

### US-001/ (User Story-Specific Architecture)

Contains architecture and design documentation specific to User Story 001 (User Authentication).

---

## Platform Phases

The platform is built in 16 phases:

| Phase | Name                               | Status      |
| ----- | ---------------------------------- | ----------- |
| 1     | Core Foundation (Auth, 2FA, Audit) | In Progress |
| 2     | Design Token System                | Planned     |
| 3     | CMS Content Engine                 | Planned     |
| 4     | Template System (9 templates)      | Planned     |
| 5-7   | UI Library, Frontend Web/Mobile    | Planned     |
| 8-10  | SaaS Products (Email, Docs, Vault) | Planned     |
| 11    | Third-Party Integrations           | Planned     |
| 12    | AI Integration (Anthropic Claude)  | Planned     |
| 13    | Environment Variable Management    | Planned     |
| 14    | Initial Setup Wizard               | Planned     |
| 15    | Deployment Pipeline                | Planned     |
| 16    | Platform Upgrade System            | Planned     |

---

## Related Documentation

- [Project Overview](../README.md) - Documentation index
- [Platform Plan](./CMS-PLATFORM-PLAN.md) - Complete 16-phase architecture
- [Core App](../../apps/core/README.md) - Phase 1 implementation
- [Database Schema](../DATABASE/) - Database architecture
- [Stories](../STORIES/) - User requirements and acceptance criteria

---

**Project:** Backend Template
**Framework:** Django 6.0
**Last Updated:** 08/01/2026
