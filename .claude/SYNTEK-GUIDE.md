# Syntek Dev Suite - Plugin Usage Guide

**Last Updated**: 07/01/2026
**Version**: 0.3.3
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Overview

Complete reference guide for using the Syntek Dev Suite plugin system with Claude Code. This guide covers:

- **Available Agents:** Specialised agents for planning, development, quality, security, and deployment
- **Typical Workflows:** Step-by-step examples for common development tasks
- **Self-Learning System:** Feedback, optimisations, and A/B testing for continuous improvement
- **Django-Specific Tips:** Recommendations for backend, database, and testing agents
- **Best Practices:** How to get the most from each agent
- **Troubleshooting:** Solutions for common issues

**Quick Start:** Use `/syntek-dev-suite:plan` to start new features, `/syntek-dev-suite:backend` for implementation, and `/syntek-dev-suite:test-writer` for tests.

---

## Table of Contents

- [Syntek Dev Suite - Plugin Usage Guide](#syntek-dev-suite---plugin-usage-guide)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Quick Start](#quick-start)
    - [Most Common Commands](#most-common-commands)
  - [Available Agents](#available-agents)
    - [Planning \& Architecture](#planning--architecture)
    - [Development](#development)
    - [Quality \& Security](#quality--security)
    - [DevOps \& Infrastructure](#devops--infrastructure)
    - [Documentation](#documentation)
    - [Compliance \& SEO](#compliance--seo)
    - [Other](#other)
  - [Typical Workflow](#typical-workflow)
    - [1. Planning Phase](#1-planning-phase)
    - [2. Development Phase](#2-development-phase)
    - [3. Quality Phase](#3-quality-phase)
    - [4. Documentation Phase](#4-documentation-phase)
    - [5. Deployment Phase](#5-deployment-phase)
  - [Self-Learning System](#self-learning-system)
    - [Providing Feedback](#providing-feedback)
    - [Reviewing Optimisations](#reviewing-optimisations)
    - [A/B Testing](#ab-testing)
    - [Metrics Location](#metrics-location)
  - [Django-Specific Tips](#django-specific-tips)
    - [Backend Agent](#backend-agent)
    - [Database Agent](#database-agent)
    - [Test Writer Agent](#test-writer-agent)
  - [Best Practices](#best-practices)
  - [Troubleshooting](#troubleshooting)
    - [Agent not producing expected results](#agent-not-producing-expected-results)
    - [Container issues](#container-issues)
    - [Database connection issues](#database-connection-issues)
  - [Getting Help](#getting-help)

## Quick Start

The Syntek Dev Suite provides specialised agents for different development tasks. Each agent has
deep expertise in its domain and follows consistent patterns.

### Most Common Commands

| Command                         | Purpose                                 |
| ------------------------------- | --------------------------------------- |
| `/syntek-dev-suite:plan`        | Create architectural plans for features |
| `/syntek-dev-suite:backend`     | API, database, and server logic         |
| `/syntek-dev-suite:test-writer` | Generate tests (TDD/BDD)                |
| `/syntek-dev-suite:review`      | Code review for security and style      |
| `/syntek-dev-suite:debug`       | Deep-dive debugging                     |

## Available Agents

### Planning & Architecture

| Agent   | Command                     | Use For                                 |
| ------- | --------------------------- | --------------------------------------- |
| Planner | `/syntek-dev-suite:plan`    | High-level system architecture          |
| Setup   | `/syntek-dev-suite:setup`   | Project scaffolding and configuration   |
| Stories | `/syntek-dev-suite:stories` | Generate user stories from requirements |
| Sprint  | `/syntek-dev-suite:sprint`  | Organise stories into sprints           |

### Development

| Agent    | Command                      | Use For                            |
| -------- | ---------------------------- | ---------------------------------- |
| Backend  | `/syntek-dev-suite:backend`  | APIs, DB schemas, server logic     |
| Frontend | `/syntek-dev-suite:frontend` | UI/UX, CSS, accessibility          |
| Database | `/syntek-dev-suite:database` | DB administration, optimisation    |
| Refactor | `/syntek-dev-suite:refactor` | Code modernisation, technical debt |

### Quality & Security

| Agent         | Command                         | Use For                               |
| ------------- | ------------------------------- | ------------------------------------- |
| Test Writer   | `/syntek-dev-suite:test-writer` | Generate tests and stubs (TDD)        |
| QA Tester     | `/syntek-dev-suite:qa-tester`   | Find bugs, security flaws, edge cases |
| Code Reviewer | `/syntek-dev-suite:review`      | Security, performance, style review   |
| Security      | `/syntek-dev-suite:security`    | Access control, security hardening    |
| Syntax        | `/syntek-dev-suite:syntax`      | Linting and language fixes            |

### DevOps & Infrastructure

| Agent   | Command                     | Use For                             |
| ------- | --------------------------- | ----------------------------------- |
| CI/CD   | `/syntek-dev-suite:cicd`    | GitHub Actions, Docker, deployments |
| Git     | `/syntek-dev-suite:git`     | Branch management, commits, PRs     |
| Logging | `/syntek-dev-suite:logging` | Sentry, file-based logging          |

### Documentation

| Agent            | Command                              | Use For                           |
| ---------------- | ------------------------------------ | --------------------------------- |
| Doc Writer       | `/syntek-dev-suite:docs`             | Developer docs, API docs, READMEs |
| Support Articles | `/syntek-dev-suite:support-articles` | User-facing help documentation    |

### Compliance & SEO

| Agent | Command                  | Use For                              |
| ----- | ------------------------ | ------------------------------------ |
| GDPR  | `/syntek-dev-suite:gdpr` | Data protection, consent management  |
| SEO   | `/syntek-dev-suite:seo`  | Meta tags, structured data, sitemaps |

### Other

| Agent          | Command                           | Use For                             |
| -------------- | --------------------------------- | ----------------------------------- |
| Auth           | `/syntek-dev-suite:auth`          | Authentication with MFA             |
| Notifications  | `/syntek-dev-suite:notifications` | Email, SMS, push notifications      |
| Export         | `/syntek-dev-suite:export`        | File export (PDF, Excel, CSV, JSON) |
| Reporting      | `/syntek-dev-suite:reporting`     | Data queries and aggregations       |
| Data Scientist | `/syntek-dev-suite:data`          | Python, Pandas, SQL analysis        |
| Debugger       | `/syntek-dev-suite:debug`         | Complex runtime issues              |
| Version        | `/syntek-dev-suite:version`       | Semantic versioning, changelogs     |
| Completion     | `/syntek-dev-suite:completion`    | Mark stories/sprints complete       |

## Typical Workflow

### 1. Planning Phase

```
User: I need to add user authentication to the API

1. /syntek-dev-suite:stories - Generate user stories
2. /syntek-dev-suite:sprint - Organise into sprints
3. /syntek-dev-suite:plan - Create architectural plan
```

### 2. Development Phase

```
1. /syntek-dev-suite:backend - Implement API endpoints
2. /syntek-dev-suite:test-writer - Generate tests
3. /syntek-dev-suite:auth - Add MFA support
```

### 3. Quality Phase

```
1. /syntek-dev-suite:review - Code review
2. /syntek-dev-suite:qa-tester - Find edge cases
3. /syntek-dev-suite:security - Security audit
```

### 4. Documentation Phase

```
1. /syntek-dev-suite:docs - API documentation
2. /syntek-dev-suite:support-articles - User guides
```

### 5. Deployment Phase

```
1. /syntek-dev-suite:cicd - Set up pipelines
2. /syntek-dev-suite:git - Create PR
3. /syntek-dev-suite:version - Update changelog
```

## Self-Learning System

The plugin includes a self-learning system that improves agent performance based on feedback.

### Providing Feedback

After any agent completes a task:

```
/syntek-dev-suite:learning-feedback
```

Rate the response and provide comments. This data is used to improve prompts.

### Reviewing Optimisations

```
/syntek-dev-suite:learning-optimise
```

Review and apply prompt improvements generated from feedback.

### A/B Testing

```
/syntek-dev-suite:learning-ab-test
```

Manage A/B tests for agent prompts.

### Metrics Location

All learning data is stored in `docs/METRICS/`:

```
docs/METRICS/
├── config.json        # System configuration
├── runs/              # Agent run records
├── feedback/          # User feedback
├── aggregates/        # Daily/weekly summaries
├── variants/          # A/B test variants
└── optimisations/     # Prompt improvements
```

## Django-Specific Tips

### Backend Agent

Use for:

- Creating Django models
- Building GraphQL schemas (Strawberry/Graphene)
- Django REST Framework viewsets
- Custom management commands

### Database Agent

Use for:

- PostgreSQL query optimisation
- Migration planning
- Index recommendations
- Query analysis with `EXPLAIN ANALYZE`

### Test Writer Agent

Use for:

- pytest test generation
- Factory Boy factories
- Django test client tests
- GraphQL query tests

## Best Practices

1. **Start with planning** - Use `/plan` before complex features
2. **Generate stories first** - Use `/stories` to clarify requirements
3. **Test-driven development** - Use `/test-writer` before implementation
4. **Review before merge** - Use `/review` on all significant changes
5. **Document as you go** - Use `/docs` after completing features
6. **Provide feedback** - Use `/learning-feedback` to improve agents

## Troubleshooting

### Agent not producing expected results

1. Check if you're using the right agent for the task
2. Provide more context in your request
3. Use `/learning-feedback` to report issues

### Container issues

```bash
# Check Docker status
docker ps

# Restart containers
docker compose -f docker/dev/docker-compose.yml restart
```

### Database connection issues

```bash
# Check PostgreSQL is running
docker compose -f docker/dev/docker-compose.yml ps db

# Check connection
docker compose -f docker/dev/docker-compose.yml exec web python manage.py dbshell
```

## Getting Help

- Review `.claude/CLAUDE.md` for project-specific context
- Check `.claude/commands/` for environment-specific commands
- Use the appropriate specialised agent for your task
