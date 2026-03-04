# Development Guide - Syntek CMS Platform

## Overview

This guide covers development workflows for the full-stack Syntek CMS platform featuring Django + Strawberry GraphQL backend, React + Next.js frontend, and Rust security layer.

## Architecture Stack

```
React Frontend (Next.js + TypeScript)
           ↓
Strawberry GraphQL API (Django + Python)
           ↓
Rust Security Layer (Authentication + Authorization)
           ↓
PostgreSQL Database + Redis Cache
```

## Prerequisites

### Required Software
- **Python 3.14.3** with pip and virtualenv
- **Node.js 24.14.0** with npm 11.11.0
- **Rust** (latest stable) with Cargo
- **PostgreSQL 18.3**
- **Redis** (latest stable)
- **Docker** and **Docker Compose** (for containerized development)

### Development Tools
- **VS Code** with extensions for Python, TypeScript, Rust, GraphQL
- **Git** with SSH keys configured
- **Forgejo** access for version control

## Quick Start

### 1. Repository Setup
```bash
# Clone the repository
git clone github-syntek:Syntek-Dev/syntek-platform.git
cd syntek-platform

# Initialize development environment
/syntek-dev-suite:setup  # If available, or manual setup below
```

### 2. Backend Setup (Django + Strawberry)
```bash
# Create virtual environment
python3.14 -m venv venv
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r backend/requirements/dev.txt

# Environment configuration
cp backend/.env.example backend/.env
# Edit .env with your database credentials

# Database setup
python backend/manage.py migrate
python backend/manage.py createsuperuser

# Start development server
python backend/manage.py runserver  # Runs on :8000
```

### 3. Security Layer Setup (Rust)
```bash
# Navigate to security directory
cd security

# Build and run in development mode
cargo run --dev  # Runs on :3001

# For auto-reload during development
cargo watch -x 'run --dev'
```

### 4. Frontend Setup (React + Next.js)
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Environment configuration
cp .env.example .env.local
# Edit .env.local with API URLs

# Generate GraphQL types from backend schema
npm run graphql:generate

# Start development server
npm run dev  # Runs on :3000
```

## Development Workflow

### 1. Feature Development Process

#### Planning Phase
```bash
# Plan the feature architecture
/syntek-dev-suite:plan Plan [feature name] implementation across full stack

# Create feature branch
/syntek-dev-suite:git Create feature branch us###/[feature-name]
```

#### Backend Development
```bash
# Design GraphQL schema
/syntek-dev-suite:backend Create GraphQL schema for [feature]

# Create Django models and migrations
python backend/manage.py makemigrations
python backend/manage.py migrate

# Implement business logic and resolvers
# Test GraphQL API at http://localhost:8000/graphql
```

#### Security Integration
```bash
# Implement security policies
/syntek-dev-suite:security Add authentication/authorization for [feature]

# Test security layer
cargo test auth::tests::[feature_test]
```

#### Frontend Development
```bash
# Generate updated GraphQL types
npm run graphql:generate

# Implement React components
/syntek-dev-suite:frontend Create components for [feature]

# Test components
npm test -- --watch
```

### 2. Real-Time Collaboration Features

For features requiring real-time updates:

#### Backend (GraphQL Subscriptions)
```python
# backend/apps/api/schema.py
@strawberry.type
class Subscription:
    @strawberry.subscription
    async def page_updates(self, page_id: strawberry.ID) -> Page:
        # Implementation for real-time page updates
```

#### Frontend (WebSocket Integration)
```typescript
// frontend/graphql/subscriptions.ts
const PAGE_UPDATES_SUBSCRIPTION = gql`
  subscription PageUpdates($pageId: ID!) {
    pageUpdates(pageId: $pageId) {
      id
      title
      content
      lastModified
    }
  }
`;
```

### 3. Database Development

#### Schema Design
```bash
# Design database schema
/syntek-dev-suite:database Design schema for [feature]

# Create models in Django
# apps/cms/models.py
class Page(models.Model):
    title = models.CharField(max_length=255)
    content = models.JSONField()
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
```

#### Query Optimization
```bash
# Optimize GraphQL resolvers
/syntek-dev-suite:database Optimize queries for [specific resolvers]

# Use select_related and prefetch_related
# Implement DataLoaders for N+1 prevention
```

## Testing Strategy

### Backend Testing
```bash
# Run Django tests
python backend/manage.py test

# Test GraphQL schema
python backend/manage.py test apps.api.tests

# Generate test coverage
coverage run --source='.' backend/manage.py test
coverage html
```

### Security Testing
```bash
# Run Rust tests
cd security
cargo test

# Security audit
cargo audit

# Integration tests
cargo test --test integration_tests
```

### Frontend Testing
```bash
# Unit tests
npm test

# Component testing
npm run test:components

# End-to-end testing
npm run test:e2e
```

### GraphQL Testing
```bash
# Test schema validity
python backend/manage.py graphql_schema --check

# Test query performance
# Use GraphQL playground at :8000/graphql with query profiling
```

## Performance Optimization

### Database Performance
- Use `select_related()` and `prefetch_related()` in GraphQL resolvers
- Implement database indexes based on query patterns
- Monitor slow queries with Django Debug Toolbar

### GraphQL Performance
- Implement DataLoaders to prevent N+1 queries
- Use query depth limiting and rate limiting
- Cache frequently accessed data with Redis

### Frontend Performance
- Use React.memo() for expensive components
- Implement code splitting for large features
- Optimize bundle size with webpack analysis

### Security Layer Performance
- Profile authentication middleware
- Use async/await for I/O-bound operations
- Implement request caching where appropriate

## Code Quality Standards

### Python (Django + Strawberry)
```bash
# Code formatting
black backend/
isort backend/

# Linting
ruff backend/

# Type checking
mypy backend/
```

### TypeScript (React + Next.js)
```bash
# Code formatting
npm run format

# Linting
npm run lint

# Type checking
npm run type-check
```

### Rust (Security Layer)
```bash
# Code formatting
cd security
cargo fmt

# Linting
cargo clippy

# Check for security issues
cargo audit
```

## Environment Management

### Development Environment Variables

#### Backend (.env)
```bash
DEBUG=True
SECRET_KEY=development-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/syntek_cms_dev
REDIS_URL=redis://localhost:6379/0
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

#### Security Layer (.env)
```bash
RUST_LOG=debug
JWT_SECRET=development-jwt-secret
DATABASE_URL=postgresql://user:password@localhost:5432/syntek_cms_dev
AUTH_SERVICE_PORT=3001
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/graphql
NEXT_PUBLIC_WS_URL=ws://localhost:8000/graphql
NEXT_PUBLIC_AUTH_URL=http://localhost:3001
```

## Debugging

### Backend Debugging
```bash
# Django Debug Toolbar
# Add to INSTALLED_APPS in development
# Access at /__debug__/

# GraphQL debugging
# Use Strawberry Studio at /graphql

# Database query debugging
# Enable DEBUG=True and use Django Debug Toolbar
```

### Frontend Debugging
```bash
# React Developer Tools
# Apollo Developer Tools for GraphQL debugging
# Next.js debugging with Chrome DevTools

# GraphQL query debugging
npm run graphql:debug
```

### Security Layer Debugging
```bash
# Rust debugging with logs
RUST_LOG=debug cargo run --dev

# Debug with GDB (if needed)
cargo build
gdb target/debug/security-layer
```

## API Documentation

### GraphQL Schema
- **Introspection**: Available at `/graphql` endpoint
- **Documentation**: Auto-generated from schema descriptions
- **Playground**: Strawberry Studio for query testing

### Authentication Flow
1. User login → Rust security layer validates credentials
2. Security layer returns JWT token
3. Frontend includes token in Authorization header
4. GraphQL resolvers validate token through security layer

## Common Issues and Solutions

### Port Conflicts
- Backend: :8000 (Django)
- Security: :3001 (Rust)
- Frontend: :3000 (Next.js)
- Database: :5432 (PostgreSQL)
- Cache: :6379 (Redis)

### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -h localhost -U postgres -d syntek_cms_dev
```

### GraphQL Schema Issues
```bash
# Regenerate schema
python backend/manage.py export_schema > schema.graphql

# Update frontend types
cd frontend
npm run graphql:generate
```

## Integration with Other Repositories

### syntek-template Integration
- API endpoints for template import/export
- GraphQL mutations for template management
- Template validation and deployment workflows

### syntek-ai Integration
- AI-powered content generation APIs
- Integration with content editing workflows
- AI-based SEO and optimization features

### syntek-infrastructure Integration
- Deployment automation through infrastructure repository
- Monitoring and observability integration
- Backup and disaster recovery procedures

---

**For more specific development tasks, use the appropriate Syntek Dev Suite agents:**
- `/syntek-dev-suite:backend` for Django/GraphQL development
- `/syntek-dev-suite:frontend` for React/Next.js development
- `/syntek-dev-suite:security` for Rust security layer
- `/syntek-dev-suite:database` for PostgreSQL optimization