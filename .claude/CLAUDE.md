# Syntek CMS Platform

This repository contains the **core CMS application** where users interact with and edit their websites. This is the central platform that powers the Syntek website building ecosystem.

## Project Overview

**Syntek Platform** is a comprehensive Content Management System that combines:
- **Drag-and-Drop Page Builder** for non-technical users
- **Online Development Environment** with Monaco editor and TTY terminal
- **Multi-Repository Coordination** across the 5-repository architecture
- **Real-time Collaboration** and version control integration

## Architecture Stack

### Backend (Django + GraphQL)
- **Framework**: Django 6.0.4 with Python 3.14.3
- **API Layer**: **Strawberry GraphQL 0.307.1** (September 2025 spec) - *Primary communication layer*
- **Database**: PostgreSQL 18.3 with Redis caching
- **Authentication**: Multi-factor authentication (MFA) with JWT tokens

### Frontend (React + Next.js)
- **Framework**: Next.js 16.1.6 with React 19.2
- **Language**: TypeScript 5.9
- **Styling**: Tailwind CSS 4.2
- **Runtime**: Node.js 24.14.0 with npm 11.11.0
- **API Communication**: GraphQL client connecting to Strawberry backend

### Security Layer (Rust)
- **Security Framework**: Custom Rust security layer
- **Authentication**: Token validation and session management
- **Authorization**: Role-based access control (RBAC)
- **Data Protection**: Encryption, GDPR compliance, audit logging
- **API Security**: Rate limiting, input sanitization, threat detection

### Communication Architecture
```
React Frontend ↔ Strawberry GraphQL API ↔ Django Backend
                        ↓
                 Rust Security Layer
                        ↓
                PostgreSQL + Redis
```

## Repository Structure

This repository follows a monolithic structure for the CMS application:

```
syntek-platform/
├── backend/                 # Django application
│   ├── apps/               # Django apps (cms, auth, api, etc.)
│   ├── graphql/            # Strawberry GraphQL schema and resolvers
│   ├── config/             # Django settings and configuration
│   ├── requirements/       # Python dependencies
│   └── manage.py           # Django management script
├── security/               # Rust security layer
│   ├── src/                # Rust source code
│   ├── auth/               # Authentication modules
│   ├── middleware/         # Security middleware
│   └── Cargo.toml          # Rust dependencies
├── frontend/               # Next.js application
│   ├── components/         # React components
│   ├── graphql/            # GraphQL queries, mutations, subscriptions
│   ├── pages/              # Next.js pages and API routes
│   ├── styles/             # Tailwind CSS and global styles
│   ├── utils/              # TypeScript utilities
│   └── package.json        # Node.js dependencies
├── docker/                 # Docker configuration
│   ├── backend.Dockerfile  # Django container
│   ├── security.Dockerfile # Rust security layer
│   ├── frontend.Dockerfile # Next.js container
│   └── docker-compose.yml  # Full stack orchestration
├── docs/                   # Platform documentation
└── README.md               # Platform overview
```

## GraphQL API Architecture

### Strawberry GraphQL as Communication Hub

**Strawberry GraphQL** serves as the central nervous system connecting frontend and backend:

#### Schema Definition
```python
# backend/graphql/schema.py
import strawberry
from strawberry_django import auto

@strawberry.type
class Query:
    pages: List[Page] = strawberry_django.field()
    users: List[User] = strawberry_django.field()
    templates: List[Template] = strawberry_django.field()

@strawberry.type
class Mutation:
    create_page: Page = strawberry_django.mutations.create()
    update_page: Page = strawberry_django.mutations.update()
    delete_page: bool = strawberry_django.mutations.delete()

@strawberry.type
class Subscription:
    page_updates: Page = strawberry.subscription()
```

#### Frontend GraphQL Integration
```typescript
// frontend/graphql/queries.ts
import { gql } from '@apollo/client';

export const GET_PAGES = gql`
  query GetPages {
    pages {
      id
      title
      content
      template {
        name
        category
      }
    }
  }
`;
```

#### Real-time Features
- **Subscriptions**: Live page updates during collaborative editing
- **Optimistic Updates**: Immediate UI feedback with rollback capability
- **Cache Management**: Apollo Client cache for optimal performance

## Multi-Repository Ecosystem

This CMS platform coordinates with 4 other specialized repositories:

1. **syntek-infrastructure** - NixOS + Rust CLI for server automation
2. **syntek-modules** - Reusable Django/React components and business logic
3. **syntek-ai** - AI systems for content generation and optimization
4. **syntek-template** - 40 industry-specific website templates

## Development Workflow

### Backend Development (Django + Strawberry)
1. **Django Models**: Define data structures for CMS entities
2. **GraphQL Schema**: Create Strawberry types and resolvers
3. **Business Logic**: Implement CMS functionality in Django apps
4. **Security Integration**: Connect with Rust security layer

### Frontend Development (React + GraphQL)
1. **GraphQL Queries**: Define data requirements in TypeScript
2. **React Components**: Build UI components consuming GraphQL data
3. **State Management**: Apollo Client for GraphQL cache and state
4. **Real-time Features**: Implement subscriptions for live updates

### Security Layer (Rust)
1. **Authentication**: Token validation and user session management
2. **Authorization**: Role-based permissions and access control
3. **Middleware**: Request/response security processing
4. **Monitoring**: Security event logging and threat detection

## Key Features Under Development

### Drag-and-Drop Page Builder
- **Component Library**: React components mapped to GraphQL data
- **Real-time Collaboration**: GraphQL subscriptions for live updates
- **Template System**: Integration with syntek-template repository
- **Version Control**: Git-like workflow for content management

### Online Development Environment
- **Monaco Editor**: Integrated with GraphQL for schema awareness
- **TTY Terminal**: Secure shell access through Rust security layer
- **Live Preview**: Real-time rendering via GraphQL subscriptions
- **Code Completion**: TypeScript + GraphQL schema integration

### Database Communication
- **GraphQL Introspection**: Auto-generated schema documentation
- **Query Optimization**: N+1 prevention, DataLoader integration
- **Real-time Sync**: Subscriptions for database change notifications
- **Multi-tenancy**: Organization-scoped GraphQL resolvers

## Technology Decisions

### Why Strawberry GraphQL?
- **Type Safety**: Automatic TypeScript generation from Python schema
- **Django Integration**: Native Django ORM integration with auto fields
- **Real-time Subscriptions**: WebSocket support for live collaboration
- **Performance**: DataLoader for efficient database queries
- **Developer Experience**: Code-first schema with Python type hints

### Why Rust for Security?
- **Memory Safety**: Zero-cost abstractions without runtime overhead
- **Performance**: Native speed for security-critical operations
- **Concurrency**: Safe parallel processing for high-load scenarios
- **Security**: Compile-time guarantees prevent common vulnerabilities

### API-First Architecture
```
Frontend (React) → GraphQL Client → Strawberry API → Django ORM → PostgreSQL
                                      ↓
                              Rust Security Middleware
```

## Agent Integration

This project uses specialized Syntek Dev Suite agents:

### Backend Development
- `/syntek-dev-suite:backend` - Django apps, GraphQL schema, API optimization
- `/syntek-dev-suite:database` - PostgreSQL schema, query performance
- `/syntek-dev-suite:security` - Rust security layer, authentication

### Frontend Development
- `/syntek-dev-suite:frontend` - React components, GraphQL integration
- `/syntek-dev-suite:seo` - SEO optimization, structured data

### API Development
- **GraphQL Focus**: All agents understand Strawberry GraphQL as primary API
- **Type Safety**: Agents ensure TypeScript/Python type consistency
- **Real-time Features**: Subscription-based live features

## Coding Standards

Follow the **Rob Pike 5 Rules** and **Linus Torvalds principles** (see `CODING-PRINCIPLES.md`):

### GraphQL Best Practices
- **Schema Design**: Consistent naming, logical field groupings
- **Query Optimization**: Use DataLoader to prevent N+1 queries
- **Type Safety**: Leverage Strawberry's type system fully
- **Error Handling**: Structured error responses with proper codes

### Security Requirements
- **Rust Layer**: All requests processed through security middleware
- **GraphQL Security**: Query depth limiting, rate limiting per user
- **Authentication**: JWT tokens validated by Rust security layer
- **Authorization**: Field-level permissions in GraphQL resolvers

## Environment Setup

### Development
```bash
# Backend (Django + Strawberry)
cd backend && pip install -r requirements/dev.txt
python manage.py migrate && python manage.py runserver

# Security Layer (Rust)
cd security && cargo run --dev

# Frontend (React + GraphQL)
cd frontend && npm install
npm run dev

# Full stack with Docker
docker-compose -f docker/docker-compose.dev.yml up
```

### GraphQL Development Tools
- **Strawberry Studio**: GraphQL playground at `/graphql`
- **Apollo Studio**: Client-side GraphQL debugging
- **Schema Introspection**: Auto-generated documentation

## Current Sprint Focus

Based on the platform architecture, current development priorities:

1. **Strawberry GraphQL API** - Core schema design and resolvers
2. **Rust Security Layer** - Authentication and authorization middleware
3. **React GraphQL Client** - Apollo Client setup and query management
4. **Page Builder Components** - Drag-and-drop interface with GraphQL backend
5. **Real-time Collaboration** - GraphQL subscriptions for live editing

## Contact & Support

- **Technical Questions**: Refer to `/docs` directory
- **GraphQL Schema**: Available at `/graphql` endpoint
- **Agent Commands**: See `.claude/SYNTEK-GUIDE.md` for full reference
- **Security Documentation**: Rust security layer docs in `/security/docs/`

---

**Built with the latest stable versions** - Django 6.0.4, Strawberry GraphQL 0.307.1, React 19.2, Next.js 16.1.6, Rust security layer, and TypeScript 5.9 for complete type safety across the stack.