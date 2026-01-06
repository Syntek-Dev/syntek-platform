# Syntek CMS Platform - Comprehensive Architectural Plan

**Version**: 1.0.0
**Created**: 06/01/2026
**Status**: Approved
**Author**: System Architect

---

## Table of Contents

- [Syntek CMS Platform - Comprehensive Architectural Plan](#syntek-cms-platform---comprehensive-architectural-plan)
  - [Table of Contents](#table-of-contents)
  - [Executive Summary](#executive-summary)
  - [Project Overview](#project-overview)
    - [Vision](#vision)
    - [Core Repositories](#core-repositories)
    - [Technology Stack](#technology-stack)
  - [Architecture Decision: Subdomain vs Path Routing](#architecture-decision-subdomain-vs-path-routing)
    - [Recommendation: Hybrid Approach](#recommendation-hybrid-approach)
    - [Rationale](#rationale)
    - [Implementation](#implementation)
  - [Phase Breakdown](#phase-breakdown)
    - [Phase 1: Core Foundation (Backend)](#phase-1-core-foundation-backend)
    - [Phase 2: Design Token System](#phase-2-design-token-system)
    - [Phase 3: CMS Content Engine](#phase-3-cms-content-engine)
    - [Phase 4: Template System](#phase-4-template-system)
    - [Phase 5: UI Design Library](#phase-5-ui-design-library)
    - [Phase 6: Frontend Web](#phase-6-frontend-web)
    - [Phase 7: Frontend Mobile](#phase-7-frontend-mobile)
    - [Phase 8: SaaS Integrations - Email Service](#phase-8-saas-integrations---email-service)
    - [Phase 9: SaaS Integrations - Cloud Documents](#phase-9-saas-integrations---cloud-documents)
    - [Phase 10: SaaS Integrations - Password Manager](#phase-10-saas-integrations---password-manager)
    - [Phase 11: Third-Party Integrations](#phase-11-third-party-integrations)
    - [Phase 12: AI Integration (Anthropic Claude)](#phase-12-ai-integration-anthropic-claude)
    - [Phase 13: Environment Variable Management](#phase-13-environment-variable-management)
    - [Phase 14: Initial Setup Wizard](#phase-14-initial-setup-wizard)
    - [Phase 15: Deployment Pipeline](#phase-15-deployment-pipeline)
  - [Database Schema](#database-schema)
    - [Core Models](#core-models)
    - [CMS Models](#cms-models)
    - [Design Token Models](#design-token-models)
    - [Template Models](#template-models)
    - [Audit Models](#audit-models)
    - [Integration Models](#integration-models)
    - [Multi-Tenancy Models](#multi-tenancy-models)
  - [GraphQL API Contracts](#graphql-api-contracts)
    - [Authentication](#authentication)
    - [Design Tokens](#design-tokens)
    - [CMS Content](#cms-content)
    - [Pages](#pages)
    - [Templates](#templates)
    - [Audit Logs](#audit-logs)
  - [Repository Structure](#repository-structure)
    - [backend\_template](#backend_template)
    - [ui\_design](#ui_design)
    - [frontend\_web](#frontend_web)
    - [frontend\_mobile](#frontend_mobile)
  - [Security Architecture](#security-architecture)
    - [Authentication Flow](#authentication-flow)
    - [IP Address Encryption](#ip-address-encryption)
    - [Audit Logging](#audit-logging)
    - [Password Requirements](#password-requirements)
  - [Caching Architecture (Redis/Valkey)](#caching-architecture-redisvalkey)
    - [Overview](#overview)
    - [Cache Configuration by Environment](#cache-configuration-by-environment)
    - [Django Cache Settings](#django-cache-settings)
    - [Multi-Tenant Cache Isolation](#multi-tenant-cache-isolation)
    - [Cache Key Patterns](#cache-key-patterns)
    - [Cache Invalidation Strategy](#cache-invalidation-strategy)
    - [Celery Task-Based Cache Warming](#celery-task-based-cache-warming)
    - [GraphQL Query Caching](#graphql-query-caching)
    - [Session Storage](#session-storage)
    - [Rate Limiting with Redis](#rate-limiting-with-redis)
    - [Docker Compose Configuration](#docker-compose-configuration)
    - [Production Configuration (Managed Redis)](#production-configuration-managed-redis)
    - [Cache Monitoring](#cache-monitoring)
    - [Cache Health Checks](#cache-health-checks)
  - [Third-Party Integration Architecture](#third-party-integration-architecture)
    - [Integration Adapter Pattern](#integration-adapter-pattern)
    - [Supported Integrations](#supported-integrations)
  - [Template System Design](#template-system-design)
    - [Template Categories](#template-categories)
    - [Template Selection Workflow](#template-selection-workflow)
  - [Branch-Based Content Workflow](#branch-based-content-workflow)
    - [Content Branches](#content-branches)
    - [Workflow](#workflow)
  - [Deployment Pipeline](#deployment-pipeline)
    - [Web Deployment](#web-deployment)
    - [Mobile Deployment](#mobile-deployment)
    - [Version Control](#version-control)
  - [Risks and Mitigation](#risks-and-mitigation)
  - [Success Criteria](#success-criteria)
  - [Next Steps](#next-steps)
  - [CMS Platform Plan - Addendum](#cms-platform-plan---addendum)
  - [AI Integration (Anthropic Claude)](#ai-integration-anthropic-claude)
    - [AI Features](#ai-features)
    - [AI Models](#ai-models)
    - [AI GraphQL API](#ai-graphql-api)
  - [Environment Variable Management](#environment-variable-management)
    - [Secrets Architecture](#secrets-architecture)
    - [Environment Variable Models](#environment-variable-models)
    - [Encryption Strategy](#encryption-strategy)
  - [Initial Setup Wizard](#initial-setup-wizard)
    - [Setup Flow](#setup-flow)
    - [Setup Wizard Steps](#setup-wizard-steps)
    - [Setup GraphQL API](#setup-graphql-api)
  - [Client Configuration](#client-configuration)
    - [Hosting Providers (Client Choice)](#hosting-providers-client-choice)
    - [Payment Processors (Client Choice)](#payment-processors-client-choice)
    - [App Store Regions (Client Choice)](#app-store-regions-client-choice)
    - [Templates (All 9 Available)](#templates-all-9-available)
  - [Updated Phase Breakdown](#updated-phase-breakdown)
  - [Platform Upgrade System](#platform-upgrade-system)
    - [Overview](#overview-1)
    - [Upgrade Flow](#upgrade-flow)
    - [Upgrade Models](#upgrade-models)
    - [Upgrade GraphQL API](#upgrade-graphql-api)
    - [Upgrade Workflow Rules](#upgrade-workflow-rules)
    - [Notification System](#notification-system)
  - [Updated Next Steps](#updated-next-steps)
  - [Resolved Questions](#resolved-questions)

---

## Executive Summary

This document outlines the architecture for a comprehensive Django/React/React Native CMS platform
with integrated SaaS services. The platform will allow clients to manage content, styling, and
access various business tools through a unified interface with multi-tenancy support.

**Key Deliverables:**
- Custom CMS replacing Wagtail with pure Django
- Design token system for brand customisation
- Template marketplace for various site types (all 9 templates)
- SaaS products (Email, Password Manager, Cloud Docs, etc.)
- Multi-platform deployment (Web, iOS, Android)
- Enterprise-grade security with 2FA and audit logging
- AI-powered assistance via Anthropic Claude integration
- Secure environment variable management with encryption
- Initial setup wizard for rapid client deployment

---

## Project Overview

### Vision

Create a Pythonic CMS platform that empowers businesses to:
1. Build and manage websites/apps without deep technical knowledge
2. Access integrated business tools (email, documents, security)
3. Maintain consistent branding across all touchpoints
4. Deploy to web and mobile from a single codebase

### Core Repositories

| Repository | Purpose | Technology |
|------------|---------|------------|
| `backend_template` | API, CMS engine, integrations | Django, PostgreSQL, GraphQL (Strawberry) |
| `ui_design` | Shared component library | React, TypeScript, Tailwind, Storybook |
| `frontend_web` | Web application | React, TypeScript, Tailwind, Vite |
| `frontend_mobile` | Mobile application | React Native, TypeScript, NativeWind, Expo |

### Technology Stack

**Backend:**
- Django 6.x (no Wagtail)
- PostgreSQL 18
- Python 3.14
- Strawberry GraphQL
- Redis/Valkey (caching, sessions, queues)
- Celery (async tasks)
- Docker Compose

**Caching Layer:**
- Redis 7.x or Valkey 8.x (Redis-compatible)
- Django Cache Framework with django-redis
- Multi-tenant cache isolation via key prefixing
- Cache invalidation via signals and Celery tasks

**Frontend:**
- React 18 / React Native 0.73+
- TypeScript 5.x
- Tailwind CSS 4.x / NativeWind 4.x
- Apollo Client (GraphQL)
- Zustand (state management)

---

## Architecture Decision: Subdomain vs Path Routing

### Recommendation: Hybrid Approach

Use **subdomains for SaaS products** that require isolation, and **path-based routing for CMS features**.

### Rationale

| Approach | Use Case | Security | UX |
|----------|----------|----------|-----|
| **Subdomain** | Email, Docs, Vault | Separate auth tokens, cookie isolation | Professional appearance |
| **Path-based** | CMS, Settings, Analytics | Single session | Seamless navigation |

### Implementation

```
companywebsite.com/               → Public website
companywebsite.com/admin/         → Admin dashboard
companywebsite.com/admin/cms/     → Content management
companywebsite.com/admin/design/  → Design tokens
companywebsite.com/admin/settings/→ Configuration

email.companywebsite.com/         → Email service (separate auth)
docs.companywebsite.com/          → OnlyOffice (separate auth)
vault.companywebsite.com/         → Vaultwarden (separate auth)
```

**Benefits:**
1. SaaS products have their own security context
2. Compromised session doesn't affect all services
3. Services can be scaled independently
4. Clearer separation of concerns
5. Professional appearance for clients

---

## Phase Breakdown

### Phase 1: Core Foundation (Backend)

**Objective:** Remove Wagtail, establish pure Django foundation

**Tasks:**
- [ ] Remove Wagtail dependencies from requirements
- [ ] Create custom user model with 2FA support
- [ ] Implement organisation/tenant model
- [ ] Set up authentication with django-allauth
- [ ] Configure TOTP-based 2FA (django-otp)
- [ ] Create base audit logging infrastructure
- [ ] Set up Sentry integration
- [ ] Configure encrypted field support (django-encrypted-model-fields)

**Database Changes:**
```python
# apps/core/models.py
Organisation, User, UserProfile, AuditLog, EncryptedIPLog
```

**API Contracts:**

<!-- prettier-ignore -->
```graphql
mutation login(email: String!, password: String!, totpCode: String): AuthPayload!
mutation register(input: RegisterInput!): AuthPayload!
query me: User
```

**Testable Outcome:** Users can register, login with 2FA, and all actions are logged.

---

### Phase 2: Design Token System

**Objective:** Store and serve design tokens via GraphQL

**Tasks:**
- [ ] Create design token models (colours, fonts, spacing, breakpoints)
- [ ] Build GraphQL schema for token queries
- [ ] Implement token versioning
- [ ] Create admin interface for token management
- [ ] Add token export (CSS variables, Tailwind config, JSON)

**Database Changes:**
```python
# apps/design/models.py
DesignTokenSet, ColourToken, FontToken, SpacingToken, BreakpointToken, TypographyToken
```

**API Contracts:**

<!-- prettier-ignore -->
```graphql
query designTokens(organisationId: ID!): DesignTokenSet!
mutation updateColourToken(id: ID!, input: ColourInput!): ColourToken!
```

**Testable Outcome:** Frontend can fetch tokens and apply them dynamically.

---

### Phase 3: CMS Content Engine

**Objective:** Build page and content management system

**Tasks:**
- [ ] Create page model with JSON content structure
- [ ] Implement block-based content system
- [ ] Build page metadata storage
- [ ] Create page versioning system
- [ ] Implement content branching (feature, test, dev, staging, prod)
- [ ] Add media library integration
- [ ] Build SEO metadata management

**Database Changes:**
```python
# apps/cms/models.py
Page, PageVersion, ContentBlock, BlockType, MediaAsset, SEOMetadata, ContentBranch
```

**API Contracts:**
```graphql
query page(slug: String!, branch: String): Page
mutation createPage(input: PageInput!): Page!
mutation publishPage(id: ID!, fromBranch: String!, toBranch: String!): Page!
```

**Testable Outcome:** Content can be created, edited, versioned, and promoted through branches.

---

### Phase 4: Template System

**Objective:** Create selectable site templates

**Tasks:**
- [ ] Design template schema structure
- [ ] Create template categories (ecommerce, blog, corporate, etc.)
- [ ] Build template initialisation system
- [ ] Implement template preview functionality
- [ ] Create template customisation workflow

**Database Changes:**
```python
# apps/templates/models.py
SiteTemplate, TemplateCategory, TemplatePreset, TemplateConfiguration
```

**Templates to Build:**
1. E-commerce (products, cart, checkout)
2. Blog (posts, categories, authors)
3. Corporate (about, services, team, contact)
4. Church (events, sermons, donations)
5. Charity (campaigns, donations, impact)
6. SaaS (pricing, features, testimonials)
7. Sole Trader (services, portfolio, booking)
8. Estate Agent (listings, search, contact)
9. Single Page App (sections, smooth scroll)

**Testable Outcome:** User can select template and have base structure initialised.

---

### Phase 5: UI Design Library

**Objective:** Create shared component library for web and mobile

**Tasks:**
- [ ] Set up Storybook
- [ ] Create base components (Button, Input, Card, Modal, etc.)
- [ ] Build layout components (Container, Grid, Stack)
- [ ] Implement form components with validation
- [ ] Create data display components (Table, List, Charts)
- [ ] Build navigation components
- [ ] Add theming system consuming design tokens
- [ ] Create responsive utilities
- [ ] Document all components

**Repository:** `ui_design`

**Structure:**
```
ui_design/
├── src/
│   ├── components/
│   │   ├── base/
│   │   ├── forms/
│   │   ├── layout/
│   │   ├── navigation/
│   │   └── data/
│   ├── hooks/
│   ├── utils/
│   └── theme/
├── .storybook/
└── package.json
```

**Testable Outcome:** Components render correctly with design tokens applied.

---

### Phase 6: Frontend Web

**Objective:** Build React web application consuming the API

**Tasks:**
- [ ] Set up Vite with React and TypeScript
- [ ] Configure Apollo Client for GraphQL
- [ ] Implement authentication flow with 2FA
- [ ] Build admin dashboard layout
- [ ] Create CMS content editor
- [ ] Implement design token editor
- [ ] Build page builder interface
- [ ] Add media library UI
- [ ] Create settings management
- [ ] Implement real-time preview

**Repository:** `frontend_web`

**Testable Outcome:** Full admin interface functional with content editing.

---

### Phase 7: Frontend Mobile

**Objective:** Build React Native app for iOS and Android

**Tasks:**
- [ ] Set up Expo with React Native
- [ ] Configure NativeWind for styling
- [ ] Implement authentication with biometrics
- [ ] Build content viewing interface
- [ ] Create push notification support
- [ ] Add offline capability
- [ ] Implement deep linking
- [ ] Build app store deployment pipeline

**Repository:** `frontend_mobile`

**Testable Outcome:** App runs on iOS and Android with content display.

---

### Phase 8: SaaS Integrations - Email Service

**Objective:** Integrate email service with custom branding

**Tasks:**
- [ ] Create email provider adapter (Mailgun/SendGrid)
- [ ] Build email template system
- [ ] Implement inbox UI
- [ ] Add compose functionality
- [ ] Create contact management
- [ ] Build email tracking/analytics
- [ ] Implement subdomain routing

**Subdomain:** `email.{domain}`

**Database Changes:**
```python
# apps/email/models.py
EmailAccount, EmailMessage, EmailTemplate, EmailContact, EmailCampaign
```

---

### Phase 9: SaaS Integrations - Cloud Documents

**Objective:** Integrate OnlyOffice with custom branding

**Tasks:**
- [ ] Set up OnlyOffice Docker deployment
- [ ] Create document storage integration (S3/DO Spaces)
- [ ] Build document browser UI
- [ ] Implement sharing/permissions
- [ ] Add collaboration features
- [ ] Create version history

**Subdomain:** `docs.{domain}`

---

### Phase 10: SaaS Integrations - Password Manager

**Objective:** Integrate Vaultwarden with custom branding

**Tasks:**
- [ ] Deploy Vaultwarden instance
- [ ] Create admin interface
- [ ] Configure SSO integration
- [ ] Build browser extension wrapper
- [ ] Add mobile app deep linking
- [ ] Implement organisation policies

**Subdomain:** `vault.{domain}`

**Additional Clients:**
- Browser extension (Chrome, Firefox, Safari)
- Desktop app (Electron wrapper)
- Mobile app (React Native)

---

### Phase 11: Third-Party Integrations

**Objective:** Build adapter system for external services

**Categories:**
1. **Marketing:** Mailchimp, SendGrid, HubSpot
2. **Social Media:** Facebook, Twitter/X, LinkedIn, Instagram
3. **Accounting:** Xero, QuickBooks, FreeAgent
4. **CRM/PM:** ClickUp, Monday, Jira, HubSpot
5. **Payments:** Stripe, PayPal, Square, SumUp
6. **Security:** Cloudflare, Let's Encrypt
7. **Hosting:** AWS, Digital Ocean, Vercel
8. **AI:** Anthropic Claude

**Database Changes:**
```python
# apps/integrations/models.py
IntegrationProvider, IntegrationCredential, IntegrationWebhook, SyncLog
```

---

### Phase 12: AI Integration (Anthropic Claude)

**Objective:** Integrate Anthropic Claude AI across all systems

**Tasks:**
- [ ] Create AI service adapter for Anthropic API
- [ ] Build AI usage tracking per user/organisation
- [ ] Implement Anthropic account management interface
- [ ] Create AI-powered content assistant
- [ ] Build AI-powered code assistance for developers
- [ ] Add AI-powered SEO suggestions
- [ ] Implement AI-powered image alt text generation
- [ ] Create AI chat interface for admin support
- [ ] Build usage dashboards and cost tracking
- [ ] Implement rate limiting and budget controls

**Subdomain:** `ai.{domain}` (optional, can be path-based)

**Database Changes:**
```python
# apps/ai/models.py
AIProvider, AIUsageLog, AIConversation, AIMessage, AIBudget, AIUserSettings
```

**API Contracts:**
```graphql
mutation aiChat(input: AIChatInput!): AIResponse!
mutation aiGenerateContent(input: AIContentInput!): AIContentResponse!
query aiUsage(userId: ID, startDate: DateTime, endDate: DateTime): AIUsageStats!
query aiConversations(limit: Int, offset: Int): [AIConversation!]!
```

**Testable Outcome:** Users can interact with Claude AI, usage is tracked, and admins can manage budgets.

---

### Phase 13: Environment Variable Management

**Objective:** Secure, encrypted environment variable management

**Tasks:**
- [ ] Create encrypted secrets storage system
- [ ] Build admin interface for managing env variables
- [ ] Implement per-environment variable sets (dev, staging, prod)
- [ ] Add variable versioning and audit trail
- [ ] Create secure variable injection for deployments
- [ ] Build variable templates for common integrations
- [ ] Implement access control for sensitive variables
- [ ] Add variable validation and schema checking

**Database Changes:**
```python
# apps/secrets/models.py
SecretCategory, EncryptedSecret, SecretVersion, SecretAccessLog, SecretTemplate
```

**Testable Outcome:** Environment variables are securely stored, encrypted, and accessible only to authorised users.

---

### Phase 14: Initial Setup Wizard

**Objective:** Guided setup flow for new client deployments

**Tasks:**
- [ ] Create setup wizard state machine
- [ ] Build domain configuration step
- [ ] Implement hosting provider selection and connection
- [ ] Create template selection interface
- [ ] Build design token configuration wizard
- [ ] Implement integration setup flow
- [ ] Create first admin user setup
- [ ] Build deployment verification checks
- [ ] Add setup progress persistence
- [ ] Create setup completion checklist

**Database Changes:**
```python
# apps/setup/models.py
SetupSession, SetupStep, SetupConfiguration, DeploymentTarget
```

**Testable Outcome:** Developer can deploy repos and complete full client setup via /admin/ wizard.

---

### Phase 15: Deployment Pipeline

**Objective:** Automated deployment to all platforms

**Tasks:**
- [ ] Configure GitHub Actions workflows
- [ ] Set up Docker registry
- [ ] Create Kubernetes manifests (optional)
- [ ] Build iOS deployment (App Store Connect)
- [ ] Build Android deployment (Google Play)
- [ ] Implement blue-green deployments
- [ ] Add rollback capabilities
- [ ] Create monitoring dashboards

---

## Database Schema

### Core Models

```python
class Organisation(models.Model):
    """Multi-tenant organisation."""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    domain = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class User(AbstractUser):
    """Custom user with 2FA support."""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    is_2fa_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=32, blank=True)
    last_login_ip = models.CharField(max_length=255, blank=True)  # Encrypted

class Role(models.Model):
    """Permission roles."""
    name = models.CharField(max_length=100)
    permissions = models.JSONField(default=list)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
```

### CMS Models

```python
class Page(models.Model):
    """CMS page with versioned content."""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    template = models.CharField(max_length=100)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True)

class PageVersion(models.Model):
    """Version history for pages."""
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='versions')
    content = models.JSONField()  # Block-based content
    branch = models.CharField(max_length=50)  # feature, test, dev, staging, production
    version_number = models.PositiveIntegerField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class ContentBlock(models.Model):
    """Reusable content block types."""
    block_type = models.CharField(max_length=100)
    schema = models.JSONField()  # JSON Schema for block data
    preview_template = models.TextField()
```

### Design Token Models

```python
class DesignTokenSet(models.Model):
    """Complete set of design tokens for an organisation."""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    version = models.PositiveIntegerField(default=1)

class ColourToken(models.Model):
    """Colour definitions."""
    token_set = models.ForeignKey(DesignTokenSet, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # e.g., 'primary', 'secondary'
    value = models.CharField(max_length=50)  # e.g., '#3B82F6'
    variants = models.JSONField(default=dict)  # light, dark, hover states

class FontToken(models.Model):
    """Font definitions."""
    token_set = models.ForeignKey(DesignTokenSet, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # e.g., 'heading', 'body'
    family = models.CharField(max_length=255)
    fallback = models.CharField(max_length=255)
    weights = models.JSONField(default=list)  # [400, 500, 700]

class SpacingToken(models.Model):
    """Spacing scale."""
    token_set = models.ForeignKey(DesignTokenSet, on_delete=models.CASCADE)
    scale = models.JSONField()  # {"xs": "0.25rem", "sm": "0.5rem", ...}

class BreakpointToken(models.Model):
    """Responsive breakpoints."""
    token_set = models.ForeignKey(DesignTokenSet, on_delete=models.CASCADE)
    breakpoints = models.JSONField()  # {"sm": "640px", "md": "768px", ...}

class TypographyToken(models.Model):
    """Typography scale."""
    token_set = models.ForeignKey(DesignTokenSet, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # e.g., 'h1', 'body-lg'
    font_size = models.CharField(max_length=50)
    line_height = models.CharField(max_length=50)
    font_weight = models.CharField(max_length=50)
    letter_spacing = models.CharField(max_length=50, blank=True)
```

### Template Models

```python
class TemplateCategory(models.Model):
    """Template categories."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50)

class SiteTemplate(models.Model):
    """Selectable site templates."""
    category = models.ForeignKey(TemplateCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    preview_image = models.URLField()
    backend_schema = models.JSONField()  # Django models to create
    frontend_schema = models.JSONField()  # React components needed
    default_tokens = models.JSONField()  # Default design tokens
    is_premium = models.BooleanField(default=False)
```

### Audit Models

```python
class AuditLog(models.Model):
    """Comprehensive audit logging."""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    resource_type = models.CharField(max_length=100)
    resource_id = models.CharField(max_length=100)
    old_value = models.JSONField(null=True)
    new_value = models.JSONField(null=True)
    ip_address = models.BinaryField()  # Encrypted
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['organisation', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['resource_type', 'resource_id']),
        ]
```

### Integration Models

```python
class IntegrationProvider(models.Model):
    """Available integration providers."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=50)  # payment, crm, email, etc.
    config_schema = models.JSONField()  # Required configuration fields
    is_active = models.BooleanField(default=True)

class IntegrationCredential(models.Model):
    """Organisation-specific integration credentials."""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    provider = models.ForeignKey(IntegrationProvider, on_delete=models.CASCADE)
    credentials = models.JSONField()  # Encrypted
    is_active = models.BooleanField(default=True)
    last_sync = models.DateTimeField(null=True)
```

### Multi-Tenancy Models

```python
class Subscription(models.Model):
    """Organisation subscription/plan."""
    organisation = models.OneToOneField(Organisation, on_delete=models.CASCADE)
    plan = models.CharField(max_length=50)  # free, starter, professional, enterprise
    features = models.JSONField()  # Enabled features
    limits = models.JSONField()  # Usage limits
    valid_until = models.DateTimeField()
```

---

## GraphQL API Contracts

### Authentication

```graphql
type AuthPayload {
  token: String!
  refreshToken: String!
  user: User!
  requiresTwoFactor: Boolean!
}

type User {
  id: ID!
  email: String!
  firstName: String!
  lastName: String!
  organisation: Organisation!
  roles: [Role!]!
  is2faEnabled: Boolean!
}

input RegisterInput {
  email: String!
  password: String!
  firstName: String!
  lastName: String!
  organisationName: String!
}

input LoginInput {
  email: String!
  password: String!
  totpCode: String
}

type Mutation {
  register(input: RegisterInput!): AuthPayload!
  login(input: LoginInput!): AuthPayload!
  refreshToken(token: String!): AuthPayload!
  enable2FA: TwoFactorSetup!
  verify2FA(code: String!): Boolean!
  logout: Boolean!
}

type Query {
  me: User
}
```

### Design Tokens

```graphql
type DesignTokenSet {
  id: ID!
  name: String!
  version: Int!
  colours: [ColourToken!]!
  fonts: [FontToken!]!
  spacing: SpacingToken!
  breakpoints: BreakpointToken!
  typography: [TypographyToken!]!
}

type ColourToken {
  id: ID!
  name: String!
  value: String!
  variants: JSON
}

type FontToken {
  id: ID!
  name: String!
  family: String!
  fallback: String!
  weights: [Int!]!
}

input ColourInput {
  name: String!
  value: String!
  variants: JSON
}

type Query {
  designTokens: DesignTokenSet!
  designTokenHistory(limit: Int): [DesignTokenSet!]!
}

type Mutation {
  updateColourToken(id: ID!, input: ColourInput!): ColourToken!
  updateFontToken(id: ID!, input: FontInput!): FontToken!
  publishTokens: DesignTokenSet!
}
```

### CMS Content

```graphql
type Page {
  id: ID!
  title: String!
  slug: String!
  template: String!
  content: JSON!
  metadata: PageMetadata!
  isPublished: Boolean!
  publishedAt: DateTime
  currentVersion: PageVersion!
  versions(branch: String): [PageVersion!]!
}

type PageVersion {
  id: ID!
  versionNumber: Int!
  branch: String!
  content: JSON!
  createdBy: User!
  createdAt: DateTime!
}

type PageMetadata {
  title: String
  description: String
  keywords: [String!]
  ogImage: String
  canonicalUrl: String
}

input PageInput {
  title: String!
  slug: String!
  template: String!
  content: JSON!
  metadata: PageMetadataInput
}

type Query {
  page(slug: String!, branch: String): Page
  pages(branch: String, limit: Int, offset: Int): PageConnection!
}

type Mutation {
  createPage(input: PageInput!): Page!
  updatePage(id: ID!, input: PageInput!): Page!
  deletePage(id: ID!): Boolean!
  publishPage(id: ID!, fromBranch: String!, toBranch: String!): Page!
  revertPage(id: ID!, versionId: ID!): Page!
}
```

### Pages

```graphql
type PageConnection {
  edges: [PageEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type PageEdge {
  node: Page!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

### Templates

```graphql
type SiteTemplate {
  id: ID!
  name: String!
  slug: String!
  description: String!
  category: TemplateCategory!
  previewImage: String!
  isPremium: Boolean!
}

type TemplateCategory {
  id: ID!
  name: String!
  slug: String!
  description: String!
  templates: [SiteTemplate!]!
}

type Query {
  templates(category: String): [SiteTemplate!]!
  templateCategories: [TemplateCategory!]!
  template(slug: String!): SiteTemplate
}

type Mutation {
  initialiseTemplate(templateSlug: String!, tokens: TokenInput!): Organisation!
}
```

### Audit Logs

```graphql
type AuditLog {
  id: ID!
  user: User
  action: String!
  resourceType: String!
  resourceId: String!
  changes: JSON
  ipAddress: String  # Only visible to admins with security role
  userAgent: String
  createdAt: DateTime!
}

type Query {
  auditLogs(
    userId: ID
    resourceType: String
    resourceId: String
    startDate: DateTime
    endDate: DateTime
    limit: Int
    offset: Int
  ): AuditLogConnection!
}
```

---

## Repository Structure

### backend_template

```
backend_template/
├── .claude/
│   └── CLAUDE.md
├── apps/
│   ├── core/               # Users, organisations, auth
│   │   ├── models.py
│   │   ├── schema.py       # GraphQL types/resolvers
│   │   ├── services.py
│   │   └── tests/
│   ├── cms/                # Pages, content, media
│   │   ├── models.py
│   │   ├── schema.py
│   │   ├── blocks.py       # Block type definitions
│   │   └── tests/
│   ├── design/             # Design tokens
│   │   ├── models.py
│   │   ├── schema.py
│   │   ├── exporters.py    # CSS, Tailwind, JSON export
│   │   └── tests/
│   ├── templates/          # Site templates
│   │   ├── models.py
│   │   ├── schema.py
│   │   ├── initializers/   # Template setup scripts
│   │   └── tests/
│   ├── integrations/       # Third-party integrations
│   │   ├── models.py
│   │   ├── adapters/       # Provider-specific adapters
│   │   │   ├── stripe.py
│   │   │   ├── mailchimp.py
│   │   │   └── ...
│   │   └── tests/
│   ├── audit/              # Audit logging
│   │   ├── models.py
│   │   ├── middleware.py
│   │   ├── encryption.py
│   │   └── tests/
│   └── saas/               # SaaS product configs
│       ├── email/
│       ├── documents/
│       └── vault/
├── api/
│   ├── schema.py           # Root GraphQL schema
│   └── middleware.py
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   ├── test.py
│   │   ├── staging.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── docker/
│   ├── dev/
│   ├── test/
│   ├── staging/
│   └── production/
├── scripts/
│   └── env/
├── pyproject.toml          # Python dependencies and project config
└── manage.py
```

### ui_design

```
ui_design/
├── src/
│   ├── components/
│   │   ├── base/
│   │   │   ├── Button/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Button.stories.tsx
│   │   │   │   ├── Button.test.tsx
│   │   │   │   └── index.ts
│   │   │   ├── Input/
│   │   │   ├── Card/
│   │   │   ├── Modal/
│   │   │   └── ...
│   │   ├── forms/
│   │   │   ├── Form/
│   │   │   ├── Select/
│   │   │   ├── Checkbox/
│   │   │   └── ...
│   │   ├── layout/
│   │   │   ├── Container/
│   │   │   ├── Grid/
│   │   │   ├── Stack/
│   │   │   └── ...
│   │   ├── navigation/
│   │   │   ├── NavBar/
│   │   │   ├── Sidebar/
│   │   │   ├── Breadcrumb/
│   │   │   └── ...
│   │   └── data/
│   │       ├── Table/
│   │       ├── List/
│   │       ├── Chart/
│   │       └── ...
│   ├── hooks/
│   │   ├── useDesignTokens.ts
│   │   ├── useMediaQuery.ts
│   │   └── ...
│   ├── theme/
│   │   ├── TokenProvider.tsx
│   │   ├── useTheme.ts
│   │   └── defaultTokens.ts
│   ├── utils/
│   │   ├── cn.ts             # className utility
│   │   └── ...
│   └── index.ts
├── .storybook/
│   ├── main.ts
│   └── preview.ts
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── vite.config.ts
```

### frontend_web

```
frontend_web/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── login/
│   │   │   └── register/
│   │   ├── (admin)/
│   │   │   ├── dashboard/
│   │   │   ├── cms/
│   │   │   │   ├── pages/
│   │   │   │   ├── media/
│   │   │   │   └── blocks/
│   │   │   ├── design/
│   │   │   │   ├── tokens/
│   │   │   │   └── preview/
│   │   │   ├── templates/
│   │   │   ├── integrations/
│   │   │   └── settings/
│   │   └── (public)/
│   │       └── [...slug]/
│   ├── components/
│   │   ├── admin/
│   │   │   ├── PageEditor/
│   │   │   ├── BlockEditor/
│   │   │   ├── TokenEditor/
│   │   │   └── ...
│   │   └── public/
│   │       └── PageRenderer/
│   ├── graphql/
│   │   ├── client.ts
│   │   ├── queries/
│   │   └── mutations/
│   ├── stores/
│   │   ├── authStore.ts
│   │   ├── cmsStore.ts
│   │   └── tokenStore.ts
│   └── utils/
├── public/
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── vite.config.ts
```

### frontend_mobile

```
frontend_mobile/
├── app/
│   ├── (auth)/
│   │   ├── login.tsx
│   │   └── register.tsx
│   ├── (tabs)/
│   │   ├── _layout.tsx
│   │   ├── home.tsx
│   │   ├── content.tsx
│   │   └── settings.tsx
│   └── _layout.tsx
├── components/
│   ├── ui/                 # NativeWind components
│   └── screens/
├── graphql/
│   ├── client.ts
│   ├── queries/
│   └── mutations/
├── stores/
├── utils/
├── app.json
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── metro.config.js
```

---

## Security Architecture

### Authentication Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   Django    │────▶│  Database   │
│  (React)    │     │   (Auth)    │     │ (Postgres)  │
└─────────────┘     └─────────────┘     └─────────────┘
       │                   │
       │ 1. Login          │ 2. Validate
       │    Request        │    Credentials
       │                   │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│  2FA Check  │────▶│ TOTP Verify │
│             │     │             │
└─────────────┘     └─────────────┘
       │
       │ 3. Issue JWT
       ▼
┌─────────────┐
│   Return    │
│   Tokens    │
└─────────────┘
```

**Password Requirements:**
- Minimum 12 characters
- At least 1 uppercase, 1 lowercase, 1 number, 1 special character
- Not in common password list
- Not similar to email/username
- Password history (last 5 passwords cannot be reused)

**2FA Requirements:**
- TOTP-based (Google Authenticator, Authy compatible)
- Backup codes for recovery
- Required for admin users
- Optional for regular users (organisation configurable)

### IP Address Encryption

```python
# apps/audit/encryption.py
from cryptography.fernet import Fernet
from django.conf import settings

class IPEncryption:
    """Encrypt IP addresses for audit logs."""

    def __init__(self):
        self.cipher = Fernet(settings.IP_ENCRYPTION_KEY)

    def encrypt(self, ip_address: str) -> bytes:
        """Encrypt an IP address."""
        return self.cipher.encrypt(ip_address.encode())

    def decrypt(self, encrypted_ip: bytes) -> str:
        """Decrypt an IP address (security role required)."""
        return self.cipher.decrypt(encrypted_ip).decode()
```

### Audit Logging

All actions are logged with:
- User ID
- Action type
- Resource type and ID
- Old and new values (for updates)
- Encrypted IP address
- User agent
- Timestamp

**Actions Logged:**
- Authentication (login, logout, failed attempts)
- CRUD operations on all models
- Permission changes
- Configuration changes
- Integration connections
- Export/download events

### Password Requirements

```python
# config/settings/base.py
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12},
    },
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'apps.core.validators.ComplexityValidator',
    },
    {
        'NAME': 'apps.core.validators.PasswordHistoryValidator',
    },
]
```

---

## Caching Architecture (Redis/Valkey)

### Overview

The platform uses Redis or Valkey (Redis-compatible open-source alternative) as the primary caching layer. This provides:

1. **Database Query Caching** - Reduce PostgreSQL load for frequently accessed data
2. **Session Storage** - Fast, distributed session management
3. **Celery Message Broker** - Task queue backend
4. **Real-time Features** - Pub/sub for WebSocket notifications
5. **Rate Limiting** - API throttling and abuse prevention

### Cache Configuration by Environment

| Environment | Cache Backend | Purpose | TTL Strategy |
|-------------|---------------|---------|--------------|
| **dev** | Redis (container) | Development caching | Short TTLs, debug enabled |
| **test** | Redis (container) | Test isolation | Per-test cache clearing |
| **staging** | Redis (managed) | Production-like testing | Production TTLs |
| **production** | Redis/Valkey (managed) | High availability | Tiered TTLs |

### Django Cache Settings

```python
# config/settings/base.py

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://redis:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
        },
        'KEY_PREFIX': 'cms',
        'TIMEOUT': 300,  # 5 minutes default
    },
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://redis:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'session',
        'TIMEOUT': 86400,  # 24 hours
    },
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'

# Celery broker
CELERY_BROKER_URL = env('REDIS_URL', default='redis://redis:6379/2')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://redis:6379/3')
```

### Multi-Tenant Cache Isolation

Each organisation's cache is isolated using key prefixing to prevent data leakage:

```python
# apps/core/cache.py
from django.core.cache import cache
from functools import wraps
import hashlib

class TenantCache:
    """Multi-tenant cache wrapper with automatic key prefixing."""

    def __init__(self, organisation_id: str):
        self.prefix = f'org:{organisation_id}'

    def _make_key(self, key: str) -> str:
        """Create tenant-scoped cache key."""
        return f'{self.prefix}:{key}'

    def get(self, key: str, default=None):
        """Get value from tenant-scoped cache."""
        return cache.get(self._make_key(key), default)

    def set(self, key: str, value, timeout=None):
        """Set value in tenant-scoped cache."""
        return cache.set(self._make_key(key), value, timeout)

    def delete(self, key: str):
        """Delete key from tenant-scoped cache."""
        return cache.delete(self._make_key(key))

    def delete_pattern(self, pattern: str):
        """Delete all keys matching pattern for this tenant."""
        from django_redis import get_redis_connection
        conn = get_redis_connection('default')
        full_pattern = f'cms:{self.prefix}:{pattern}*'
        keys = conn.keys(full_pattern)
        if keys:
            conn.delete(*keys)

    def clear_tenant(self):
        """Clear all cache for this tenant."""
        self.delete_pattern('')


def tenant_cache_key(key_template: str):
    """Decorator to generate tenant-scoped cache keys."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            org_id = getattr(self, 'organisation_id', None)
            if org_id is None and hasattr(self, 'request'):
                org_id = self.request.user.organisation_id
            cache_key = f'org:{org_id}:{key_template}'
            return func(self, cache_key, *args, **kwargs)
        return wrapper
    return decorator
```

### Cache Key Patterns

| Data Type | Key Pattern | TTL | Invalidation |
|-----------|-------------|-----|--------------|
| **User Profile** | `org:{id}:user:{user_id}` | 15 min | On user update |
| **Design Tokens** | `org:{id}:tokens:{version}` | 1 hour | On token publish |
| **Page Content** | `org:{id}:page:{slug}:{branch}` | 5 min | On page update |
| **Page List** | `org:{id}:pages:{branch}:{page}` | 5 min | On any page CRUD |
| **Template Config** | `org:{id}:template:{slug}` | 24 hours | On template change |
| **Permissions** | `org:{id}:perms:{user_id}` | 30 min | On role change |
| **GraphQL Query** | `org:{id}:gql:{query_hash}` | 5 min | Varies by query |
| **Integration Config** | `org:{id}:integration:{provider}` | 1 hour | On credential update |
| **AI Conversation** | `org:{id}:ai:conv:{conv_id}` | 30 min | On new message |

### Cache Invalidation Strategy

```python
# apps/core/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.core.cache import TenantCache

@receiver(post_save, sender='core.User')
def invalidate_user_cache(sender, instance, **kwargs):
    """Invalidate user-related caches on update."""
    cache = TenantCache(instance.organisation_id)
    cache.delete(f'user:{instance.id}')
    cache.delete(f'perms:{instance.id}')

@receiver(post_save, sender='design.DesignTokenSet')
def invalidate_token_cache(sender, instance, **kwargs):
    """Invalidate design tokens on publish."""
    if instance.is_active:
        cache = TenantCache(instance.organisation_id)
        cache.delete_pattern('tokens:')

@receiver([post_save, post_delete], sender='cms.Page')
def invalidate_page_cache(sender, instance, **kwargs):
    """Invalidate page caches on CRUD operations."""
    cache = TenantCache(instance.organisation_id)
    cache.delete(f'page:{instance.slug}:*')
    cache.delete_pattern('pages:')  # Clear page lists

@receiver(post_save, sender='cms.PageVersion')
def invalidate_page_version_cache(sender, instance, **kwargs):
    """Invalidate page cache when new version created."""
    page = instance.page
    cache = TenantCache(page.organisation_id)
    cache.delete(f'page:{page.slug}:{instance.branch}')
```

### Celery Task-Based Cache Warming

```python
# apps/core/tasks.py
from celery import shared_task
from apps.core.cache import TenantCache

@shared_task
def warm_organisation_cache(organisation_id: str):
    """Pre-populate cache for an organisation after cold start."""
    from apps.design.models import DesignTokenSet
    from apps.cms.models import Page

    cache = TenantCache(organisation_id)

    # Warm design tokens
    tokens = DesignTokenSet.objects.filter(
        organisation_id=organisation_id,
        is_active=True
    ).first()
    if tokens:
        cache.set(f'tokens:{tokens.version}', tokens.to_dict(), timeout=3600)

    # Warm published pages
    pages = Page.objects.filter(
        organisation_id=organisation_id,
        is_published=True
    ).select_related('current_version')[:50]

    for page in pages:
        cache.set(
            f'page:{page.slug}:production',
            page.to_dict(),
            timeout=300
        )

@shared_task
def clear_organisation_cache(organisation_id: str):
    """Clear all cache for an organisation (e.g., on subscription change)."""
    cache = TenantCache(organisation_id)
    cache.clear_tenant()
```

### GraphQL Query Caching

```python
# api/middleware.py
import hashlib
from django.core.cache import cache

class GraphQLCacheMiddleware:
    """Cache GraphQL query results for authenticated users."""

    CACHEABLE_QUERIES = {
        'designTokens': 3600,  # 1 hour
        'page': 300,           # 5 minutes
        'pages': 300,          # 5 minutes
        'templates': 86400,    # 24 hours
        'me': 900,             # 15 minutes
    }

    def resolve(self, next, root, info, **kwargs):
        # Only cache for authenticated users
        if not info.context.user.is_authenticated:
            return next(root, info, **kwargs)

        operation_name = info.field_name
        if operation_name not in self.CACHEABLE_QUERIES:
            return next(root, info, **kwargs)

        # Generate cache key
        org_id = info.context.user.organisation_id
        query_hash = hashlib.sha256(
            f'{operation_name}:{kwargs}'.encode()
        ).hexdigest()[:16]
        cache_key = f'org:{org_id}:gql:{query_hash}'

        # Check cache
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        # Execute and cache
        result = next(root, info, **kwargs)
        ttl = self.CACHEABLE_QUERIES[operation_name]
        cache.set(cache_key, result, timeout=ttl)

        return result
```

### Session Storage

Sessions are stored in Redis for fast access and horizontal scaling:

```python
# config/settings/production.py

# Redis-backed sessions with security settings
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 86400  # 24 hours

# Session security
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True  # Extend session on activity
```

### Rate Limiting with Redis

```python
# apps/core/throttling.py
from rest_framework.throttling import SimpleRateThrottle
from django_redis import get_redis_connection

class TenantRateThrottle(SimpleRateThrottle):
    """Rate limiting per organisation to prevent abuse."""

    scope = 'tenant'
    THROTTLE_RATES = {
        'tenant': '1000/hour',
        'tenant_burst': '100/minute',
    }

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            org_id = request.user.organisation_id
            return f'throttle:org:{org_id}:{self.scope}'
        return None

class AIRateThrottle(SimpleRateThrottle):
    """Rate limiting for AI API calls to manage costs."""

    scope = 'ai'
    THROTTLE_RATES = {
        'ai': '100/hour',
        'ai_burst': '10/minute',
    }

    def get_cache_key(self, request, view):
        if request.user.is_authenticated:
            user_id = request.user.id
            return f'throttle:ai:user:{user_id}'
        return None
```

### Docker Compose Configuration

```yaml
# docker/dev/docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # OR use Valkey (Redis-compatible open source)
  valkey:
    image: valkey/valkey:8-alpine
    command: valkey-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    ports:
      - "6379:6379"
    volumes:
      - valkey_data:/data
    healthcheck:
      test: ["CMD", "valkey-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  redis_data:
  valkey_data:
```

### Production Configuration (Managed Redis)

```yaml
# docker/production/docker-compose.yml
# Production uses managed Redis from AWS ElastiCache or Digital Ocean
services:
  web:
    environment:
      - REDIS_URL=redis://:${REDIS_PASSWORD}@${REDIS_HOST}:6379/0
      - CELERY_BROKER_URL=redis://:${REDIS_PASSWORD}@${REDIS_HOST}:6379/1

# Environment variables for production
# REDIS_HOST=your-redis-cluster.cache.amazonaws.com
# REDIS_PASSWORD=your-secure-password
# REDIS_TLS=true
```

### Cache Monitoring

```python
# apps/core/management/commands/cache_stats.py
from django.core.management.base import BaseCommand
from django_redis import get_redis_connection

class Command(BaseCommand):
    help = 'Display Redis cache statistics'

    def handle(self, *args, **options):
        conn = get_redis_connection('default')
        info = conn.info()

        self.stdout.write(f"Redis Version: {info['redis_version']}")
        self.stdout.write(f"Used Memory: {info['used_memory_human']}")
        self.stdout.write(f"Peak Memory: {info['used_memory_peak_human']}")
        self.stdout.write(f"Connected Clients: {info['connected_clients']}")
        self.stdout.write(f"Total Commands: {info['total_commands_processed']}")
        self.stdout.write(f"Keyspace Hits: {info.get('keyspace_hits', 0)}")
        self.stdout.write(f"Keyspace Misses: {info.get('keyspace_misses', 0)}")

        # Calculate hit rate
        hits = info.get('keyspace_hits', 0)
        misses = info.get('keyspace_misses', 0)
        total = hits + misses
        if total > 0:
            hit_rate = (hits / total) * 100
            self.stdout.write(f"Cache Hit Rate: {hit_rate:.2f}%")
```

### Cache Health Checks

```python
# apps/core/health.py
from django.core.cache import cache
from django_redis import get_redis_connection

def check_cache_health() -> dict:
    """Check Redis cache health for monitoring."""
    try:
        # Test write
        cache.set('health_check', 'ok', timeout=10)

        # Test read
        value = cache.get('health_check')
        if value != 'ok':
            return {'status': 'unhealthy', 'error': 'Read verification failed'}

        # Test connection
        conn = get_redis_connection('default')
        conn.ping()

        return {
            'status': 'healthy',
            'backend': 'redis',
            'connected': True
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }
```

---

## Third-Party Integration Architecture

### Integration Adapter Pattern

```python
# apps/integrations/adapters/base.py
from abc import ABC, abstractmethod
from typing import Any, Dict

class IntegrationAdapter(ABC):
    """Base class for all integration adapters."""

    @abstractmethod
    def connect(self, credentials: Dict[str, Any]) -> bool:
        """Establish connection with the service."""
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """Disconnect from the service."""
        pass

    @abstractmethod
    def sync(self) -> Dict[str, Any]:
        """Sync data with the service."""
        pass

    @abstractmethod
    def webhook_handler(self, payload: Dict[str, Any]) -> None:
        """Handle incoming webhooks."""
        pass
```

### Supported Integrations

| Category | Providers | Priority |
|----------|-----------|----------|
| **Email** | Mailgun, SendGrid | Phase 8 |
| **Marketing** | Mailchimp, HubSpot | Phase 11 |
| **Social** | Facebook, Twitter/X, LinkedIn, Instagram | Phase 11 |
| **Accounting** | Xero, QuickBooks, FreeAgent | Phase 11 |
| **CRM/PM** | ClickUp, Monday, Jira, HubSpot | Phase 11 |
| **Payments** | Stripe, PayPal, Square, SumUp | Phase 11 |
| **Security** | Cloudflare, Let's Encrypt | Phase 11 |
| **Hosting** | AWS, Digital Ocean, Vercel | Phase 12 |
| **Documents** | OnlyOffice | Phase 9 |
| **Password** | Vaultwarden | Phase 10 |

---

## Template System Design

### Template Categories

| Category | Description | Key Features |
|----------|-------------|--------------|
| **E-commerce** | Online stores | Products, cart, checkout, inventory |
| **Blog** | Content publishing | Posts, categories, authors, comments |
| **Corporate** | Business websites | About, services, team, contact |
| **Church** | Religious organisations | Events, sermons, donations, groups |
| **Charity** | Non-profit organisations | Campaigns, donations, impact stories |
| **SaaS** | Software products | Pricing, features, testimonials, docs |
| **Sole Trader** | Individual businesses | Services, portfolio, booking, reviews |
| **Estate Agent** | Property listings | Listings, search, valuation, contact |
| **Single Page** | Landing pages | Hero, features, CTA, testimonials |

### Template Selection Workflow

```
1. User creates organisation
         │
         ▼
2. Select template category
         │
         ▼
3. Choose specific template
         │
         ▼
4. Configure design tokens
   ├── Upload logo
   ├── Set primary colours
   ├── Choose fonts
   └── Configure spacing/breakpoints
         │
         ▼
5. Template initialisation
   ├── Create Django models
   ├── Generate default pages
   ├── Apply design tokens
   └── Configure integrations
         │
         ▼
6. Ready to customise content
```

---

## Branch-Based Content Workflow

### Content Branches

| Branch | Purpose | Access |
|--------|---------|--------|
| `feature` | Individual work in progress | Assigned editor |
| `testing` | QA team review | QA role |
| `dev` | PM review | PM role |
| `staging` | Client/manager approval | Manager role |
| `production` | Live site | Published |

### Workflow

```
feature ──────▶ testing ──────▶ dev ──────▶ staging ──────▶ production
    │              │             │             │
    │              │             │             │
    └──── Review ──┘─── Review ──┘─── Review ──┘─── Publish
```

**Rules:**
1. Content must pass through each branch in order
2. Each transition requires approval from appropriate role
3. Content can be rejected and sent back to previous branch
4. Version history maintained at each branch
5. Production rollback available to any previous version

---

## Deployment Pipeline

### Web Deployment

```yaml
# .github/workflows/deploy-web.yml
name: Deploy Web Frontend

on:
  push:
    branches: [main]
    paths:
      - 'frontend_web/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build
        run: npm run build
      - name: Deploy to Vercel/DO
        run: ...

  deploy-staging:
    needs: build
    environment: staging
    steps:
      - name: Deploy to staging
        run: ...

  deploy-production:
    needs: deploy-staging
    environment: production
    steps:
      - name: Deploy to production
        run: ...
```

### Mobile Deployment

```yaml
# .github/workflows/deploy-mobile.yml
name: Deploy Mobile App

on:
  push:
    tags:
      - 'mobile-v*'

jobs:
  build-ios:
    runs-on: macos-latest
    steps:
      - name: Build iOS
        run: eas build --platform ios
      - name: Submit to App Store
        run: eas submit --platform ios

  build-android:
    runs-on: ubuntu-latest
    steps:
      - name: Build Android
        run: eas build --platform android
      - name: Submit to Play Store
        run: eas submit --platform android
```

### Version Control

**Mono-repo vs Multi-repo Decision:** **Multi-repo** recommended

| Approach | Pros | Cons |
|----------|------|------|
| **Multi-repo** | Independent versioning, clearer ownership, separate CI/CD | More complex dependency management |
| **Mono-repo** | Easier cross-repo changes, single source of truth | Larger repo, coupled releases |

**Versioning Strategy:**
- Semantic versioning (MAJOR.MINOR.PATCH)
- Automated changelog generation
- GitHub releases for each version
- npm/PyPI packages for shared libraries

---

## Risks and Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Scope creep** | High | High | Strict phase boundaries, MVP focus |
| **Integration complexity** | High | Medium | Adapter pattern, thorough testing |
| **Security vulnerabilities** | Medium | Critical | Regular audits, penetration testing |
| **Performance issues** | Medium | High | Load testing, caching strategy |
| **Third-party API changes** | Medium | Medium | Version pinning, abstraction layer |
| **Mobile app rejection** | Medium | Medium | Early App Store guideline review |
| **Data migration issues** | Low | High | Comprehensive backup strategy |
| **Team knowledge gaps** | Medium | Medium | Documentation, pair programming |

---

## Success Criteria

**Phase 1-4 (Core Platform):**
- [ ] User can register, login with 2FA
- [ ] Design tokens can be created and fetched via GraphQL
- [ ] Pages can be created, edited, and published
- [ ] Content branching workflow functions correctly
- [ ] All actions are audit logged

**Phase 5-7 (Frontend):**
- [ ] UI components render with design tokens
- [ ] Admin interface fully functional
- [ ] Mobile app runs on iOS and Android
- [ ] Real-time content preview works

**Phase 8-10 (SaaS Products):**
- [ ] Email service functional with custom branding
- [ ] Document editing works via OnlyOffice
- [ ] Vaultwarden accessible via all platforms

**Phase 11-12 (Integrations & Deployment):**
- [ ] At least 3 integrations per category functional
- [ ] Automated deployment pipeline working
- [ ] Mobile apps deployed to stores

---

## Next Steps

1. **Immediate:** Remove Wagtail dependencies, set up core models
2. **Week 1-2:** Complete Phase 1 (Core Foundation)
3. **Week 3-4:** Complete Phase 2 (Design Tokens)
4. **Week 5-6:** Complete Phase 3 (CMS Engine)
5. **Week 7-8:** Complete Phase 4 (Templates)
6. **Week 9-12:** Parallel work on UI, Web, Mobile frontends

**Questions to Resolve:**
1. Hosting provider preference (AWS vs Digital Ocean vs hybrid)?
2. Primary payment processor for subscriptions?
3. Target app store regions?
4. Initial template priorities (which 3-4 to build first)?

## CMS Platform Plan - Addendum

**Added**: 06/01/2026
**Status**: To be merged into main plan

This addendum adds three new sections to the CMS Platform Plan:
1. AI Integration (Anthropic Claude)
2. Environment Variable Management
3. Initial Setup Wizard

---

## AI Integration (Anthropic Claude)

### AI Features

The platform integrates Anthropic Claude AI across all systems to provide intelligent assistance:

| Feature | Description | Location |
|---------|-------------|----------|
| **Content Assistant** | Generate, edit, and improve content | CMS Editor |
| **SEO Suggestions** | AI-powered meta descriptions, titles, keywords | Page Metadata |
| **Image Alt Text** | Automatic accessibility descriptions | Media Library |
| **Code Assistant** | Help developers with template customisation | Developer Tools |
| **Chat Support** | AI-powered help desk for admin users | Admin Dashboard |
| **Translation** | Content translation assistance | CMS Editor |
| **Analytics Insights** | AI interpretation of usage data | Analytics Dashboard |
| **Document Writing** | AI assistance for creating and editing documents | OnlyOffice Docs |
| **Presentation Creator** | AI-powered slide generation and content suggestions | OnlyOffice PPT |
| **Spreadsheet Assistant** | Formula help, data analysis, chart suggestions | OnlyOffice Sheets |
| **Email Composer** | Draft emails, subject lines, reply suggestions | Email Service |
| **Marketing Copy** | Campaign content, A/B test variants, CTAs | Marketing Tools |
| **Social Media** | Post drafts, hashtag suggestions, scheduling copy | Social Manager |

### AI Models

```python
# apps/ai/models.py

class AIProvider(models.Model):
    """AI service provider configuration."""
    name = models.CharField(max_length=100)  # e.g., 'anthropic'
    api_base_url = models.URLField()
    is_active = models.BooleanField(default=True)
    default_model = models.CharField(max_length=100)  # e.g., 'claude-sonnet-4-20250514'
    supported_models = models.JSONField(default=list)

class AIUsageLog(models.Model):
    """Track AI usage per user and organisation."""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    provider = models.ForeignKey(AIProvider, on_delete=models.CASCADE)
    model = models.CharField(max_length=100)
    feature = models.CharField(max_length=100)  # content, seo, chat, etc.
    input_tokens = models.PositiveIntegerField()
    output_tokens = models.PositiveIntegerField()
    cost_cents = models.PositiveIntegerField()  # Cost in cents for billing
    request_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['organisation', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['feature']),
        ]

class AIConversation(models.Model):
    """AI chat conversation history."""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    context_type = models.CharField(max_length=100)  # cms, support, code, etc.
    context_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AIMessage(models.Model):
    """Individual messages in AI conversations."""
    conversation = models.ForeignKey(AIConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20)  # user, assistant
    content = models.TextField()
    tokens_used = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

class AIBudget(models.Model):
    """AI usage budgets per organisation/user."""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    monthly_limit_cents = models.PositiveIntegerField()
    current_usage_cents = models.PositiveIntegerField(default=0)
    alert_threshold_percent = models.PositiveIntegerField(default=80)
    is_hard_limit = models.BooleanField(default=False)
    period_start = models.DateField()
    period_end = models.DateField()

class AIUserSettings(models.Model):
    """User-specific AI preferences."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    preferred_model = models.CharField(max_length=100, blank=True)
    tone = models.CharField(max_length=50, default='professional')
    language = models.CharField(max_length=10, default='en-GB')
    features_enabled = models.JSONField(default=dict)
```

### AI GraphQL API

```graphql
type AIResponse {
  id: ID!
  content: String!
  tokensUsed: Int!
  model: String!
  conversationId: ID
}

type AIUsageStats {
  totalTokens: Int!
  totalCostCents: Int!
  byFeature: [AIFeatureUsage!]!
  byUser: [AIUserUsage!]!
  byDay: [AIDailyUsage!]!
}

type AIFeatureUsage {
  feature: String!
  tokens: Int!
  costCents: Int!
  requestCount: Int!
}

type AIUserUsage {
  user: User!
  tokens: Int!
  costCents: Int!
  requestCount: Int!
}

type AIDailyUsage {
  date: Date!
  tokens: Int!
  costCents: Int!
}

type AIConversation {
  id: ID!
  title: String!
  contextType: String!
  messages: [AIMessage!]!
  createdAt: DateTime!
  updatedAt: DateTime!
}

type AIMessage {
  id: ID!
  role: String!
  content: String!
  tokensUsed: Int!
  createdAt: DateTime!
}

type AIBudget {
  id: ID!
  monthlyLimitCents: Int!
  currentUsageCents: Int!
  remainingCents: Int!
  percentUsed: Float!
  isHardLimit: Boolean!
}

input AIChatInput {
  conversationId: ID
  message: String!
  contextType: String
  contextId: String
  model: String
}

input AIContentInput {
  content: String!
  action: AIContentAction!
  targetLanguage: String
  tone: String
}

enum AIContentAction {
  IMPROVE
  SUMMARISE
  EXPAND
  TRANSLATE
  SEO_OPTIMISE
  GENERATE_ALT_TEXT
}

type Query {
  aiUsage(organisationId: ID, userId: ID, startDate: DateTime, endDate: DateTime): AIUsageStats!
  aiConversations(contextType: String, limit: Int, offset: Int): [AIConversation!]!
  aiConversation(id: ID!): AIConversation
  aiBudget(organisationId: ID, userId: ID): AIBudget
  aiSettings: AIUserSettings!
}

type Mutation {
  aiChat(input: AIChatInput!): AIResponse!
  aiGenerateContent(input: AIContentInput!): AIContentResponse!
  aiGenerateAltText(mediaId: ID!): AIResponse!
  aiGenerateSEO(pageId: ID!): AIContentResponse!
  updateAIBudget(organisationId: ID!, userId: ID, monthlyLimitCents: Int!, alertThresholdPercent: Int, isHardLimit: Boolean): AIBudget!
  updateAISettings(input: AISettingsInput!): AIUserSettings!
  deleteAIConversation(id: ID!): Boolean!
}
```

---

## Environment Variable Management

### Secrets Architecture

All sensitive environment variables are encrypted at rest and in transit. The system supports:

1. **Per-Environment Secrets** - Separate values for dev, staging, production
2. **Inheritance** - Base secrets that can be overridden per environment
3. **Templates** - Pre-defined secret structures for common integrations
4. **Versioning** - Full history of secret changes with rollback
5. **Access Control** - Role-based access to view/edit secrets

```
┌─────────────────────────────────────────────────────────────┐
│                    Secrets Management                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │    Base     │  │   Staging   │  │ Production  │         │
│  │   Secrets   │──│   Override  │──│   Override  │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Encrypted Storage (AES-256)             │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                │                │                 │
│         ▼                ▼                ▼                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Dev Deploy  │  │Staging Deploy│ │ Prod Deploy │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### Environment Variable Models

```python
# apps/secrets/models.py

class SecretCategory(models.Model):
    """Categories for organising secrets."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50)
    order = models.PositiveIntegerField(default=0)

class EncryptedSecret(models.Model):
    """Encrypted environment variable storage."""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    category = models.ForeignKey(SecretCategory, on_delete=models.SET_NULL, null=True)
    key = models.CharField(max_length=255)  # e.g., STRIPE_SECRET_KEY
    value_encrypted = models.BinaryField()  # AES-256 encrypted value
    value_hash = models.CharField(max_length=64)  # SHA-256 hash for comparison
    environment = models.CharField(max_length=50)  # base, dev, staging, production
    description = models.TextField(blank=True)
    is_sensitive = models.BooleanField(default=True)  # Hide value in UI
    is_required = models.BooleanField(default=False)
    validation_regex = models.CharField(max_length=500, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='secrets_created')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='secrets_updated')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [['organisation', 'key', 'environment']]
        indexes = [
            models.Index(fields=['organisation', 'category']),
            models.Index(fields=['organisation', 'environment']),
        ]

class SecretVersion(models.Model):
    """Version history for secrets."""
    secret = models.ForeignKey(EncryptedSecret, on_delete=models.CASCADE, related_name='versions')
    value_encrypted = models.BinaryField()
    value_hash = models.CharField(max_length=64)
    version_number = models.PositiveIntegerField()
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    change_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SecretAccessLog(models.Model):
    """Audit log for secret access."""
    secret = models.ForeignKey(EncryptedSecret, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50)  # view, edit, delete, deploy
    ip_address = models.BinaryField()  # Encrypted
    user_agent = models.TextField()
    success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class SecretTemplate(models.Model):
    """Pre-defined templates for common integrations."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    provider = models.CharField(max_length=100)  # stripe, mailgun, aws, etc.
    description = models.TextField()
    required_keys = models.JSONField()  # List of required secret keys
    optional_keys = models.JSONField(default=list)  # Optional keys
    documentation_url = models.URLField(blank=True)
    setup_instructions = models.TextField(blank=True)
```

### Encryption Strategy

```python
# apps/secrets/encryption.py
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import hashlib
import base64

class SecretEncryption:
    """AES-256 encryption for secrets with key derivation."""

    def __init__(self, master_key: bytes, organisation_id: str):
        """Derive organisation-specific key from master key."""
        salt = hashlib.sha256(organisation_id.encode()).digest()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_key))
        self.cipher = Fernet(key)

    def encrypt(self, value: str) -> bytes:
        """Encrypt a secret value."""
        return self.cipher.encrypt(value.encode())

    def decrypt(self, encrypted_value: bytes) -> str:
        """Decrypt a secret value."""
        return self.cipher.decrypt(encrypted_value).decode()

    @staticmethod
    def hash_value(value: str) -> str:
        """Create SHA-256 hash of value for comparison."""
        return hashlib.sha256(value.encode()).hexdigest()

    @staticmethod
    def generate_master_key() -> bytes:
        """Generate a new master encryption key."""
        return Fernet.generate_key()
```

**Security Measures:**
1. Master key stored in HSM or secure vault (AWS KMS, HashiCorp Vault)
2. Per-organisation key derivation prevents cross-tenant access
3. All secret access logged with encrypted IP
4. Secrets never logged or displayed in full in UI
5. Automatic key rotation support
6. Secure memory handling (secrets cleared after use)

---

## Initial Setup Wizard

### Setup Flow

When a developer deploys the four repositories to a hosting provider and accesses `/admin/`
for the first time, they're guided through a setup wizard:

```
┌─────────────────────────────────────────────────────────────┐
│                    INITIAL SETUP WIZARD                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Step 1: Domain & Hosting                                    │
│  ────────────────────────                                    │
│  • Configure primary domain                                  │
│  • Connect hosting provider (AWS/DO/Vercel/etc.)            │
│  • Set up SSL/TLS certificates                              │
│  • Configure DNS settings                                    │
│                                                              │
│  Step 2: Database & Cache                                    │
│  ───────────────────────                                     │
│  • Connect PostgreSQL database                               │
│  • Configure Redis/Valkey cache                              │
│  • Run initial migrations                                    │
│  • Verify connections                                        │
│                                                              │
│  Step 3: Admin Account                                       │
│  ────────────────────                                        │
│  • Create first admin user                                   │
│  • Set up 2FA                                                │
│  • Configure password policy                                 │
│                                                              │
│  Step 4: Organisation Setup                                  │
│  ─────────────────────────                                   │
│  • Organisation name and details                             │
│  • Upload logo                                               │
│  • Set timezone and locale                                   │
│                                                              │
│  Step 5: Template Selection                                  │
│  ─────────────────────────                                   │
│  • Choose site template (all 9 available)                   │
│  • Preview template                                          │
│  • Select frontend variant                                   │
│                                                              │
│  Step 6: Design Tokens                                       │
│  ────────────────────                                        │
│  • Set primary/secondary colours                             │
│  • Choose fonts                                              │
│  • Configure spacing and breakpoints                         │
│  • Preview branding                                          │
│                                                              │
│  Step 7: Integrations                                        │
│  ───────────────────                                         │
│  • Email provider (Mailgun/SendGrid/etc.)                   │
│  • Payment processor (Stripe/PayPal/Square/etc.)            │
│  • Storage provider (S3/DO Spaces/Cloudinary)               │
│  • AI provider (Anthropic Claude)                           │
│                                                              │
│  Step 8: Environment Variables                               │
│  ────────────────────────────                                │
│  • Set API keys and tokens                                   │
│  • Configure webhooks                                        │
│  • Validate all connections                                  │
│                                                              │
│  Step 9: Mobile App Setup (Optional)                         │
│  ──────────────────────────────────                          │
│  • App Store Connect credentials                             │
│  • Google Play Console credentials                           │
│  • App signing certificates                                  │
│  • Push notification setup                                   │
│                                                              │
│  Step 10: Verification & Launch                              │
│  ─────────────────────────────                               │
│  • Run health checks                                         │
│  • Verify all integrations                                   │
│  • Generate deployment report                                │
│  • Complete setup                                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Setup Wizard Steps

```python
# apps/setup/models.py

class SetupSession(models.Model):
    """Track setup wizard progress."""
    organisation = models.OneToOneField(Organisation, on_delete=models.CASCADE, null=True)
    session_key = models.CharField(max_length=255, unique=True)
    current_step = models.PositiveIntegerField(default=1)
    is_complete = models.BooleanField(default=False)
    configuration = models.JSONField(default=dict)  # Accumulated config
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)
    setup_by_ip = models.BinaryField()  # Encrypted

class SetupStep(models.Model):
    """Individual setup step definitions."""
    order = models.PositiveIntegerField(unique=True)
    slug = models.SlugField(unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    is_required = models.BooleanField(default=True)
    is_skippable = models.BooleanField(default=False)
    validation_schema = models.JSONField()  # JSON Schema for step data
    depends_on = models.ManyToManyField('self', symmetrical=False, blank=True)

class SetupConfiguration(models.Model):
    """Saved configuration from setup wizard."""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    step = models.ForeignKey(SetupStep, on_delete=models.CASCADE)
    data = models.JSONField()
    is_valid = models.BooleanField(default=False)
    validated_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DeploymentTarget(models.Model):
    """Hosting/deployment configuration."""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    provider = models.CharField(max_length=50)  # aws, digitalocean, vercel, etc.
    environment = models.CharField(max_length=50)  # dev, staging, production
    region = models.CharField(max_length=50)
    credentials_encrypted = models.BinaryField()
    configuration = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    last_deployment = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Setup GraphQL API

```graphql
# Setup Types
type SetupSession {
  id: ID!
  currentStep: Int!
  totalSteps: Int!
  isComplete: Boolean!
  configuration: JSON!
  steps: [SetupStepStatus!]!
}

type SetupStepStatus {
  step: SetupStep!
  status: SetupStepStatusEnum!
  data: JSON
  errors: [String!]
}

type SetupStep {
  order: Int!
  slug: String!
  name: String!
  description: String!
  isRequired: Boolean!
  isSkippable: Boolean!
  validationSchema: JSON!
}

enum SetupStepStatusEnum {
  PENDING
  IN_PROGRESS
  COMPLETED
  SKIPPED
  ERROR
}

type SetupValidationResult {
  isValid: Boolean!
  errors: [SetupValidationError!]!
  warnings: [String!]
}

type SetupValidationError {
  field: String!
  message: String!
}

# Setup Queries
type Query {
  setupSession: SetupSession
  setupStep(slug: String!): SetupStep
  setupSteps: [SetupStep!]!
  setupValidate(step: String!, data: JSON!): SetupValidationResult!
}

# Setup Mutations
type Mutation {
  setupStart: SetupSession!

  setupSaveStep(step: String!, data: JSON!): SetupStepStatus!

  setupSkipStep(step: String!): SetupStepStatus!

  setupPreviousStep: SetupSession!

  setupNextStep: SetupSession!

  setupComplete: SetupCompleteResult!

  setupReset: Boolean!
}

type SetupCompleteResult {
  success: Boolean!
  organisation: Organisation
  adminUser: User
  deploymentReport: DeploymentReport!
  errors: [String!]
}

type DeploymentReport {
  domain: String!
  sslStatus: String!
  databaseStatus: String!
  cacheStatus: String!
  integrationsStatus: [IntegrationStatus!]!
  warnings: [String!]
}

type IntegrationStatus {
  provider: String!
  status: String!
  message: String
}
```

---

## Client Configuration

Each client deployment is fully configurable based on their preferences:

### Hosting Providers (Client Choice)

| Provider | Supported | Features |
|----------|-----------|----------|
| **AWS** | Yes | EC2, ECS, Lambda, RDS, S3, CloudFront |
| **Digital Ocean** | Yes | Droplets, App Platform, Spaces, Managed DB |
| **Vercel** | Yes | Frontend hosting, Edge Functions |
| **Google Cloud** | Yes | GKE, Cloud Run, Cloud SQL |
| **Azure** | Yes | App Service, AKS, Azure SQL |
| **Heroku** | Yes | Dynos, Heroku Postgres |
| **Railway** | Yes | Containers, PostgreSQL |
| **Render** | Yes | Web Services, PostgreSQL |

### Payment Processors (Client Choice)

| Provider | Supported | Features |
|----------|-----------|----------|
| **Stripe** | Yes | Cards, Apple Pay, Google Pay, Subscriptions |
| **PayPal** | Yes | PayPal, Venmo, Pay Later |
| **Square** | Yes | In-person, Online, Invoicing |
| **SumUp** | Yes | Card readers, Online payments |
| **GoCardless** | Yes | Direct Debit, Open Banking |
| **Adyen** | Yes | Global payments, Risk management |

### App Store Regions (Client Choice)

| Region | iOS | Android |
|--------|-----|---------|
| United Kingdom | App Store Connect UK | Google Play UK |
| United States | App Store Connect US | Google Play US |
| European Union | App Store Connect EU | Google Play EU |
| Australia | App Store Connect AU | Google Play AU |
| Global | All regions | All regions |

### Templates (All 9 Available)

All 9 templates are included in every deployment:

1. **E-commerce** - Full online store with products, cart, checkout
2. **Blog** - Content publishing with posts, categories, authors
3. **Corporate** - Professional business site with services, team
4. **Church** - Religious organisation with events, sermons, donations
5. **Charity** - Non-profit with campaigns, donations, impact stories
6. **SaaS** - Software product with pricing, features, documentation
7. **Sole Trader** - Individual business with portfolio, booking
8. **Estate Agent** - Property listings with search, valuations
9. **Single Page** - Landing page with sections, CTAs

---

## Updated Phase Breakdown

The plan now has 15 phases:

| Phase | Name | Description |
|-------|------|-------------|
| 1 | Core Foundation | Remove Wagtail, auth, 2FA, audit logging |
| 2 | Design Token System | Colours, fonts, spacing, breakpoints in DB |
| 3 | CMS Content Engine | Pages, blocks, versioning, branching |
| 4 | Template System | All 9 templates |
| 5 | UI Design Library | Shared React components |
| 6 | Frontend Web | React admin and public site |
| 7 | Frontend Mobile | React Native iOS/Android app |
| 8 | Email Service | Mailgun/SendGrid integration |
| 9 | Cloud Documents | OnlyOffice integration |
| 10 | Password Manager | Vaultwarden integration |
| 11 | Third-Party Integrations | All external service adapters |
| 12 | AI Integration | Anthropic Claude across all systems |
| 13 | Environment Variables | Encrypted secrets management |
| 14 | Setup Wizard | Initial deployment configuration |
| 15 | Deployment Pipeline | CI/CD for web, iOS, Android |
| 16 | Platform Upgrade System | Managed updates for languages, frameworks, templates |

---

## Platform Upgrade System

### Overview

The platform includes a managed upgrade system that allows clients to safely test and deploy updates to:
- **Language versions** (Python, Node.js, etc.)
- **Framework versions** (Django, React, React Native)
- **Package/dependency updates** (security patches, new features)
- **Template updates** (new features, improvements, bug fixes)
- **Platform enhancements** (new integrations, UI improvements)

### Upgrade Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    PLATFORM UPGRADE FLOW                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. New Update Available                                     │
│     ↓                                                        │
│  2. Admin notified in dashboard                              │
│     ↓                                                        │
│  3. Review changelog and breaking changes                    │
│     ↓                                                        │
│  4. Deploy to TESTING environment                            │
│     • Automated test suite runs                              │
│     • QA team validates functionality                        │
│     ↓                                                        │
│  5. Deploy to DEV environment                                │
│     • Project managers review changes                        │
│     • Integration testing                                    │
│     ↓                                                        │
│  6. Deploy to STAGING environment                            │
│     • Client/manager approval                                │
│     • User acceptance testing                                │
│     ↓                                                        │
│  7. Deploy to PRODUCTION                                     │
│     • Blue-green deployment                                  │
│     • Rollback available                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Upgrade Models

```python
# apps/upgrades/models.py

class PlatformVersion(models.Model):
    """Track platform versions available."""
    version = models.CharField(max_length=50)  # e.g., '1.2.0'
    release_date = models.DateTimeField()
    changelog = models.TextField()
    breaking_changes = models.JSONField(default=list)
    migration_notes = models.TextField(blank=True)
    min_python_version = models.CharField(max_length=20)
    min_node_version = models.CharField(max_length=20)
    dependencies = models.JSONField(default=dict)  # Package versions
    is_stable = models.BooleanField(default=False)
    is_lts = models.BooleanField(default=False)  # Long-term support
    created_at = models.DateTimeField(auto_now_add=True)

class TemplateVersion(models.Model):
    """Track template versions."""
    template = models.ForeignKey(SiteTemplate, on_delete=models.CASCADE)
    version = models.CharField(max_length=50)
    changelog = models.TextField()
    breaking_changes = models.JSONField(default=list)
    new_features = models.JSONField(default=list)
    bug_fixes = models.JSONField(default=list)
    migration_script = models.TextField(blank=True)
    release_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

class OrganisationVersion(models.Model):
    """Track which version each organisation is running."""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    platform_version = models.ForeignKey(PlatformVersion, on_delete=models.PROTECT)
    template_versions = models.JSONField(default=dict)  # {template_slug: version}
    environment = models.CharField(max_length=50)  # testing, dev, staging, production
    deployed_at = models.DateTimeField()
    deployed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = [['organisation', 'environment']]

class UpgradeRequest(models.Model):
    """Track upgrade requests through environments."""
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE)
    from_version = models.ForeignKey(PlatformVersion, on_delete=models.PROTECT, related_name='upgrades_from')
    to_version = models.ForeignKey(PlatformVersion, on_delete=models.PROTECT, related_name='upgrades_to')
    status = models.CharField(max_length=50)  # pending, testing, dev, staging, production, failed, rolled_back
    current_environment = models.CharField(max_length=50)
    initiated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class UpgradeEnvironmentStatus(models.Model):
    """Track upgrade status per environment."""
    upgrade_request = models.ForeignKey(UpgradeRequest, on_delete=models.CASCADE, related_name='environment_statuses')
    environment = models.CharField(max_length=50)
    status = models.CharField(max_length=50)  # pending, deploying, testing, approved, rejected, failed
    deployed_at = models.DateTimeField(null=True)
    tested_at = models.DateTimeField(null=True)
    approved_at = models.DateTimeField(null=True)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='approvals')
    test_results = models.JSONField(default=dict)
    notes = models.TextField(blank=True)

class UpgradeTestResult(models.Model):
    """Store test results for upgrades."""
    environment_status = models.ForeignKey(UpgradeEnvironmentStatus, on_delete=models.CASCADE)
    test_suite = models.CharField(max_length=100)
    passed = models.BooleanField()
    total_tests = models.PositiveIntegerField()
    passed_tests = models.PositiveIntegerField()
    failed_tests = models.PositiveIntegerField()
    skipped_tests = models.PositiveIntegerField()
    duration_seconds = models.FloatField()
    output = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### Upgrade GraphQL API

```graphql
type PlatformVersion {
  id: ID!
  version: String!
  releaseDate: DateTime!
  changelog: String!
  breakingChanges: [String!]!
  migrationNotes: String
  isStable: Boolean!
  isLts: Boolean!
  dependencies: JSON!
}

type TemplateVersion {
  id: ID!
  template: SiteTemplate!
  version: String!
  changelog: String!
  newFeatures: [String!]!
  bugFixes: [String!]!
  breakingChanges: [String!]!
  releaseDate: DateTime!
}

type OrganisationVersion {
  organisation: Organisation!
  platformVersion: PlatformVersion!
  templateVersions: JSON!
  environment: String!
  deployedAt: DateTime!
}

type UpgradeRequest {
  id: ID!
  fromVersion: PlatformVersion!
  toVersion: PlatformVersion!
  status: String!
  currentEnvironment: String!
  environmentStatuses: [UpgradeEnvironmentStatus!]!
  createdAt: DateTime!
}

type UpgradeEnvironmentStatus {
  environment: String!
  status: String!
  deployedAt: DateTime
  testedAt: DateTime
  approvedAt: DateTime
  approvedBy: User
  testResults: JSON
  notes: String
}

type UpgradeAvailability {
  hasUpdate: Boolean!
  currentVersion: PlatformVersion!
  availableVersions: [PlatformVersion!]!
  recommendedVersion: PlatformVersion
  templateUpdates: [TemplateVersion!]!
}

type Query {
  # Check for available upgrades
  upgradeAvailability: UpgradeAvailability!

  # Get current versions per environment
  organisationVersions: [OrganisationVersion!]!

  # Get upgrade request status
  upgradeRequest(id: ID!): UpgradeRequest
  upgradeRequests(status: String): [UpgradeRequest!]!

  # Get version history
  platformVersions(limit: Int): [PlatformVersion!]!
  templateVersions(templateSlug: String!): [TemplateVersion!]!
}

type Mutation {
  # Initiate an upgrade
  initiateUpgrade(toVersion: ID!): UpgradeRequest!

  # Deploy to next environment
  deployToEnvironment(upgradeId: ID!, environment: String!): UpgradeEnvironmentStatus!

  # Approve upgrade for environment
  approveUpgrade(upgradeId: ID!, environment: String!, notes: String): UpgradeEnvironmentStatus!

  # Reject upgrade (send back)
  rejectUpgrade(upgradeId: ID!, environment: String!, reason: String!): UpgradeEnvironmentStatus!

  # Rollback to previous version
  rollbackUpgrade(upgradeId: ID!, environment: String!): OrganisationVersion!

  # Run tests for environment
  runUpgradeTests(upgradeId: ID!, environment: String!): [UpgradeTestResult!]!
}
```

### Upgrade Workflow Rules

1. **Testing Environment**
   - Automated test suite must pass
   - QA team reviews and approves
   - Can reject with notes for developer review

2. **Dev Environment**
   - Project managers review functionality
   - Integration tests run
   - Can request changes before approval

3. **Staging Environment**
   - Client/manager approval required
   - User acceptance testing
   - Final sign-off before production

4. **Production Environment**
   - Blue-green deployment for zero downtime
   - Automatic rollback if health checks fail
   - Post-deployment monitoring

### Notification System

```python
# Upgrade notifications sent via:
# - Admin dashboard alerts
# - Email to organisation admins
# - In-app notifications
# - Webhook to external systems (optional)

UPGRADE_NOTIFICATIONS = {
    'new_version_available': {
        'recipients': ['org_admins'],
        'channels': ['dashboard', 'email'],
    },
    'upgrade_deployed_to_testing': {
        'recipients': ['qa_team'],
        'channels': ['dashboard', 'email'],
    },
    'upgrade_ready_for_approval': {
        'recipients': ['environment_approvers'],
        'channels': ['dashboard', 'email'],
    },
    'upgrade_approved': {
        'recipients': ['org_admins', 'initiator'],
        'channels': ['dashboard'],
    },
    'upgrade_rejected': {
        'recipients': ['initiator'],
        'channels': ['dashboard', 'email'],
    },
    'upgrade_failed': {
        'recipients': ['org_admins', 'initiator'],
        'channels': ['dashboard', 'email'],
    },
    'upgrade_complete': {
        'recipients': ['org_admins'],
        'channels': ['dashboard', 'email'],
    },
}
```

---

## Updated Next Steps

1. **Immediate:** Remove Wagtail dependencies, set up core models
2. **Phase 1:** Core Foundation (auth, 2FA, audit logging)
3. **Phase 2:** Design Token System
4. **Phase 3:** CMS Content Engine
5. **Phase 4:** All 9 Templates
6. **Phase 5-7:** UI Library, Frontend Web, Frontend Mobile (parallel)
7. **Phase 8-10:** SaaS Products (Email, Docs, Vault)
8. **Phase 11:** Third-Party Integrations
9. **Phase 12:** AI Integration (Anthropic Claude) - including SaaS product assistance
10. **Phase 13:** Environment Variable Management
11. **Phase 14:** Initial Setup Wizard
12. **Phase 15:** Deployment Pipeline
13. **Phase 16:** Platform Upgrade System

---

## Resolved Questions

- ✅ **Hosting provider:** Client choice (adapters for all major providers)
- ✅ **Payment processor:** Client choice (adapters for all major processors)
- ✅ **App store regions:** Client choice (configurable per deployment)
- ✅ **Template priorities:** All 9 templates to be built
