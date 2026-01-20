# Debugging Documentation

**Last Updated**: 08/01/2026
**Version**: 0.4.1
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [Debugging Documentation](#debugging-documentation)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Directory Structure](#directory-structure)
  - [Debugging Guides](#debugging-guides)
    - [Common Issues](#common-issues)
  - [Tools and Techniques](#tools-and-techniques)
    - [Debug Tools](#debug-tools)
    - [Testing Tools](#testing-tools)
    - [Database Tools](#database-tools)
  - [Related Documentation](#related-documentation)

---

## Overview

This directory contains debugging documentation, troubleshooting guides, and issue analysis reports
for specific user stories. Use these guides to diagnose and resolve development issues.

---

## Directory Structure

```
DEBUG/
├── README.md            # This file
└── US-001/              # Debugging documentation for User Story 001
    └── [Debugging guides and analysis]
```

---

## Debugging Guides

### Common Issues

**Authentication Issues**

- Token generation and validation
- Session expiration problems
- 2FA configuration issues

**Database Issues**

- Migration failures
- Query optimisation problems
- Connection pooling issues

**GraphQL Issues**

- Query depth limit violations
- Introspection problems
- Authentication in GraphQL

**Environment Issues**

- Environment variable configuration
- Docker container issues
- Port conflicts

---

## Tools and Techniques

### Debug Tools

- Django Debug Toolbar
- Postman for GraphQL testing
- Database query logging
- Application logging with Sentry

### Testing Tools

- pytest with verbose output
- Coverage reports
- Network request inspection

### Database Tools

- Django shell (`./scripts/env/dev.sh shell`)
- Direct database queries
- Migration inspection

---

## Related Documentation

- [User Story 001 Debugging](US-001/README.md) - Authentication debugging
- [Setup Guide](../DEVELOPER-SETUP.md) - Development environment setup
- [Testing](../TESTS/) - Testing and QA documentation
- [Logging](../LOGGING/) - Logging configuration
- [Architecture](../ARCHITECTURE/) - System design

---

**Project:** Backend Template
**Framework**: Django 5.2
**Last Updated**: 08/01/2026
