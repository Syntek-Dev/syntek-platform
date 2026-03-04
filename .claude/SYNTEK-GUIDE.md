# Syntek Dev Suite Guide - CMS Platform

Complete reference for using Syntek Dev Suite agents with the full-stack CMS platform.

## Quick Reference

| Agent | Purpose | Best For |
|-------|---------|----------|
| `/syntek-dev-suite:backend` | Django + GraphQL API development | Strawberry schema, Django models, API optimization |
| `/syntek-dev-suite:frontend` | React + Next.js development | Component building, GraphQL client, UI/UX |
| `/syntek-dev-suite:security` | Rust security layer | Authentication, authorization, security middleware |
| `/syntek-dev-suite:database` | PostgreSQL optimization | Schema design, query performance, migrations |
| `/syntek-dev-suite:test-writer` | Test generation | TDD/BDD for all stack layers |
| `/syntek-dev-suite:git` | Version control workflow | Branch management, commits, PRs |

## Architecture-Specific Agents

### Backend Development

#### `/syntek-dev-suite:backend`
**Specializes in:** Django + Strawberry GraphQL API development

**Use Cases:**
- Design GraphQL schema with Strawberry types and resolvers
- Create Django models for CMS entities (pages, templates, users)
- Implement business logic for page builder functionality
- Optimize API performance with DataLoaders
- Handle authentication integration with Rust security layer

**Example Commands:**
```bash
/syntek-dev-suite:backend Create a GraphQL schema for the page builder with types for Page, Template, and Component
/syntek-dev-suite:backend Implement Django models for multi-tenant CMS with organization isolation
/syntek-dev-suite:backend Add GraphQL subscriptions for real-time collaborative editing
```

#### `/syntek-dev-suite:database`
**Specializes in:** PostgreSQL schema design and optimization

**Use Cases:**
- Design database schema for CMS entities
- Create migrations for multi-tenant architecture
- Optimize queries for GraphQL resolvers
- Set up indexes for performance
- Handle data relationships between organizations, users, pages

**Example Commands:**
```bash
/syntek-dev-suite:database Design a PostgreSQL schema for multi-tenant CMS platform
/syntek-dev-suite:database Optimize GraphQL resolver queries to prevent N+1 problems
/syntek-dev-suite:database Create database indexes for page search functionality
```

### Frontend Development

#### `/syntek-dev-suite:frontend`
**Specializes in:** React + Next.js with GraphQL client

**Use Cases:**
- Build drag-and-drop page builder components
- Implement GraphQL queries and mutations with Apollo Client
- Create real-time collaboration features with subscriptions
- Design responsive UI with Tailwind CSS
- Integrate Monaco editor for code editing

**Example Commands:**
```bash
/syntek-dev-suite:frontend Create a drag-and-drop page builder using React and Apollo GraphQL
/syntek-dev-suite:frontend Implement real-time collaboration with GraphQL subscriptions
/syntek-dev-suite:frontend Build Monaco editor integration for code editing in the CMS
```

### Security & Authentication

#### `/syntek-dev-suite:security`
**Specializes in:** Rust security layer and authentication

**Use Cases:**
- Implement JWT token validation in Rust
- Create role-based access control (RBAC) middleware
- Handle GraphQL security (query depth limiting, rate limiting)
- Integrate with Django authentication
- Implement MFA for admin users

**Example Commands:**
```bash
/syntek-dev-suite:security Implement Rust middleware for JWT token validation
/syntek-dev-suite:security Create role-based permissions for CMS users
/syntek-dev-suite:security Add rate limiting and query depth limiting for GraphQL API
```

## Development Workflow Agents

### Planning & Architecture

#### `/syntek-dev-suite:plan`
**Specializes in:** Feature planning and architecture design

**Use Cases:**
- Plan new CMS features across full stack
- Design API contracts between frontend and backend
- Plan database schema changes and migrations
- Coordinate development across multiple repositories

**Example Commands:**
```bash
/syntek-dev-suite:plan Plan the implementation of template system integration
/syntek-dev-suite:plan Design the architecture for real-time collaborative editing
/syntek-dev-suite:plan Create a development plan for mobile app integration
```

### Testing & Quality Assurance

#### `/syntek-dev-suite:test-writer`
**Specializes in:** Test generation for TDD/BDD

**Use Cases:**
- Generate GraphQL API tests for Strawberry resolvers
- Create React component tests with Testing Library
- Write Rust security layer unit tests
- Generate Django model and view tests
- Create end-to-end tests for CMS workflows

**Example Commands:**
```bash
/syntek-dev-suite:test-writer Generate tests for GraphQL page management API
/syntek-dev-suite:test-writer Create React tests for drag-and-drop page builder
/syntek-dev-suite:test-writer Write Rust security tests for authentication middleware
```

#### `/syntek-dev-suite:qa-tester`
**Specializes in:** Bug detection and security analysis

**Use Cases:**
- Find security vulnerabilities in Rust authentication code
- Detect GraphQL API security issues
- Identify React performance problems
- Test CMS workflows for edge cases
- Analyze accessibility compliance

**Example Commands:**
```bash
/syntek-dev-suite:qa-tester Analyze security vulnerabilities in the authentication flow
/syntek-dev-suite:qa-tester Test the page builder for accessibility compliance
/syntek-dev-suite:qa-tester Find edge cases in multi-tenant data isolation
```

### DevOps & Infrastructure

#### `/syntek-dev-suite:cicd`
**Specializes in:** CI/CD pipelines and Docker configuration

**Use Cases:**
- Set up Docker containers for Django, Rust, and React
- Create CI/CD pipelines for multi-language stack
- Configure development environment with Docker Compose
- Set up production deployment workflows

**Example Commands:**
```bash
/syntek-dev-suite:cicd Create Docker containers for Django backend and Rust security layer
/syntek-dev-suite:cicd Set up CI/CD pipeline for GraphQL schema validation
/syntek-dev-suite:cicd Configure development environment with Docker Compose
```

## Content & Documentation

#### `/syntek-dev-suite:docs`
**Specializes in:** Technical documentation

**Use Cases:**
- Generate GraphQL API documentation
- Create component documentation for React library
- Write setup guides for development environment
- Document architecture decisions
- Create user guides for CMS features

**Example Commands:**
```bash
/syntek-dev-suite:docs Generate comprehensive GraphQL API documentation
/syntek-dev-suite:docs Create setup guide for full-stack development environment
/syntek-dev-suite:docs Document the drag-and-drop page builder architecture
```

## Platform Integration Agents

### Multi-Repository Coordination

#### `/syntek-dev-suite:git`
**Specializes in:** Git workflow across repositories

**Use Cases:**
- Coordinate changes across syntek-platform and syntek-template
- Manage version compatibility between repositories
- Handle release workflows for the platform
- Synchronize API changes between frontend and backend

**Example Commands:**
```bash
/syntek-dev-suite:git Create coordinated release across syntek-platform and syntek-template
/syntek-dev-suite:git Manage API versioning between frontend and backend changes
/syntek-dev-suite:git Set up branch protection for GraphQL schema changes
```

### AI & Automation

#### `/syntek-dev-suite:ai`
**Note:** This agent interfaces with the separate syntek-ai repository

**Use Cases:**
- Integrate AI content generation into CMS
- Implement AI-powered code suggestions in Monaco editor
- Add AI-based SEO optimization features
- Connect with syntek-ai repository APIs

## Common Workflows

### Starting a New Feature

1. **Plan the feature:**
   ```bash
   /syntek-dev-suite:plan Plan implementation of [feature name] across full stack
   ```

2. **Set up branch and tests:**
   ```bash
   /syntek-dev-suite:git Create feature branch for [feature name]
   /syntek-dev-suite:test-writer Generate tests for [feature name] functionality
   ```

3. **Backend development:**
   ```bash
   /syntek-dev-suite:backend Implement GraphQL schema for [feature name]
   /syntek-dev-suite:database Create migrations for [feature name] data model
   /syntek-dev-suite:security Add security policies for [feature name]
   ```

4. **Frontend development:**
   ```bash
   /syntek-dev-suite:frontend Create React components for [feature name]
   /syntek-dev-suite:frontend Implement GraphQL queries for [feature name]
   ```

5. **Quality assurance:**
   ```bash
   /syntek-dev-suite:qa-tester Test [feature name] for bugs and security issues
   /syntek-dev-suite:review Review code quality for [feature name]
   ```

### Debugging Performance Issues

1. **Identify the layer:**
   ```bash
   /syntek-dev-suite:qa-tester Analyze performance bottleneck in [area]
   ```

2. **Database optimization:**
   ```bash
   /syntek-dev-suite:database Optimize queries for [specific functionality]
   ```

3. **API optimization:**
   ```bash
   /syntek-dev-suite:backend Optimize GraphQL resolvers for [specific queries]
   ```

4. **Frontend optimization:**
   ```bash
   /syntek-dev-suite:frontend Optimize React rendering for [specific components]
   ```

### Security Audit

1. **Full security review:**
   ```bash
   /syntek-dev-suite:security Audit Rust authentication and authorization code
   /syntek-dev-suite:qa-tester Find security vulnerabilities in GraphQL API
   /syntek-dev-suite:review Review code for security best practices
   ```

## Agent Coordination

### Cross-Stack Features
When working on features that span multiple parts of the stack:

1. **Start with planning:** Use `/syntek-dev-suite:plan` to design the full feature
2. **Backend first:** Use `/syntek-dev-suite:backend` and `/syntek-dev-suite:database`
3. **Security integration:** Use `/syntek-dev-suite:security` for authentication
4. **Frontend implementation:** Use `/syntek-dev-suite:frontend`
5. **Testing:** Use `/syntek-dev-suite:test-writer` and `/syntek-dev-suite:qa-tester`
6. **Documentation:** Use `/syntek-dev-suite:docs`

### Real-Time Collaboration Features
For implementing collaborative editing:

1. **GraphQL Subscriptions:** `/syntek-dev-suite:backend` for WebSocket handling
2. **Database Design:** `/syntek-dev-suite:database` for conflict resolution
3. **Security:** `/syntek-dev-suite:security` for subscription authentication
4. **React Integration:** `/syntek-dev-suite:frontend` for real-time UI updates

### Template System Integration
For connecting with syntek-template repository:

1. **API Design:** `/syntek-dev-suite:backend` for template import/export APIs
2. **Data Models:** `/syntek-dev-suite:database` for template storage
3. **Frontend Interface:** `/syntek-dev-suite:frontend` for template selection
4. **Documentation:** `/syntek-dev-suite:docs` for template developer guides

## Tips for Effective Agent Use

### Be Specific About Stack Layer
- Mention "GraphQL schema" instead of just "API"
- Specify "React components" instead of just "frontend"
- Indicate "Rust security middleware" instead of just "authentication"

### Provide Context
- Mention the full stack nature of the feature
- Explain how it fits into the CMS workflow
- Indicate any dependencies on other repositories

### Follow the Data Flow
Always consider the data flow: `React → GraphQL → Django → Rust Security → PostgreSQL`

### Use Multiple Agents for Complex Features
Don't try to do everything with one agent. Use the right specialist for each part of the implementation.

---

**Remember:** These agents are designed to work together. Use multiple agents for complex features that span the full stack.