# Syntek CMS Platform

**A comprehensive Content Management System platform for building and managing client websites with drag-and-drop functionality, online development tools, and enterprise-grade features.**

---

## Table of Contents

- [Overview](#overview)
- [5-Repository Architecture](#5-repository-architecture)
  - [Repository Breakdown](#repository-breakdown)
  - [Data Flow](#data-flow)
- [CMS Platform Features](#cms-platform-features)
  - [Drag-and-Drop Page Builder](#drag-and-drop-page-builder)
  - [Online Development Environment](#online-development-environment)
  - [Database Communication](#database-communication)
  - [Version Control Integration](#version-control-integration)
- [Technology Stack](#technology-stack)
- [Template System](#template-system)
- [Development Workflow](#development-workflow)
- [Getting Started](#getting-started)
- [Contact](#contact)

---

## Overview

The **Syntek CMS Platform** is a comprehensive solution for building and managing professional websites for clients across various industries. The platform combines the flexibility of a traditional CMS with advanced developer tools, providing both drag-and-drop functionality for non-technical users and full development capabilities for programmers.

**Key Capabilities:**

- **Client-Friendly Interface**: Drag-and-drop page builder with real-time preview
- **Developer Tools**: Online code editor (Monaco/VS Code) and TTY terminal access
- **Multi-Repository Architecture**: Modular design across 5 specialized repositories
- **Industry Templates**: 40 pre-built templates across 8 industry categories
- **Enterprise Features**: Version control, database management, infrastructure automation
- **Self-Hosted**: Complete control over data and customization

This repository serves as the central documentation hub for the entire platform architecture.

---

## 5-Repository Architecture

The Syntek Platform is designed as a modular system across 5 specialized repositories, each serving specific functions in the overall ecosystem.

### Repository Breakdown

#### 1. **syntek-infrastructure**

_NixOS + Rust CLI tooling for server design_

- **Purpose**: Infrastructure as Code (IaC) for server provisioning and management
- **Technology**: NixOS configuration + Rust CLI tools
- **Features**:
  - Automated server deployment and configuration
  - Reproducible development and production environments
  - Complete observability stack (Grafana dashboards, Loki log aggregation, Prometheus metrics, Glitchtip error tracking)
  - Workflow automation and service routing (n8n)
  - Infrastructure scaling and automated alerting
  - Security hardening and compliance
- **Target Users**: DevOps engineers, system administrators

#### 2. **syntek-modules**

_Modular design for authentication, accounting, payments, page layouts_

- **Purpose**: Reusable business logic modules and components
- **Technology**: Django packages, React components, shared libraries
- **Features**:
  - Authentication and user management modules
  - Payment processing and accounting systems
  - Page layout and design components
  - API integrations and data connectors
- **Target Users**: Backend developers, full-stack developers

#### 3. **syntek-ai**

_AI systems for syntek infrastructure and clients_

- **Purpose**: AI-powered features and automation
- **Technology**: Python, machine learning frameworks, AI APIs
- **Features**:
  - Content generation and optimization
  - SEO analysis and recommendations
  - Code assistance and debugging
  - Infrastructure monitoring and alerting
- **Target Users**: AI engineers, content creators

#### 4. **syntek-platform** _(this repository)_

_CMS documentation and architecture overview_

- **Purpose**: Central documentation and platform overview
- **Technology**: Markdown documentation
- **Features**:
  - Comprehensive platform documentation
  - Architecture guides and API references
  - Setup and deployment instructions
  - Developer onboarding materials
- **Target Users**: All developers, project managers, stakeholders

#### 5. **syntek-template**

_Starter templates with various industry-specific options_

- **Purpose**: Pre-built website templates for rapid deployment
- **Technology**: React/Next.js, Django, industry-specific configurations
- **Features**:
  - 40 professional templates (8 categories × 5 variants)
  - Customizable design systems and branding
  - Industry-specific functionality and integrations
  - Mobile-responsive and accessibility-compliant designs
- **Target Users**: Web designers, clients, project managers

### Data Flow

```
Client Request → syntek-template (Templates) → syntek-platform (CMS Core)
       ↓                                              ↓
syntek-modules (Business Logic) ← → syntek-ai (AI Features)
       ↓
syntek-infrastructure (Deployment & Hosting)
```

**Flow Explanation:**

1. **Client starts** with a template from `syntek-template`
2. **CMS core** in `syntek-platform` manages content and pages
3. **Business modules** from `syntek-modules` provide functionality (auth, payments, etc.)
4. **AI systems** from `syntek-ai` enhance content and provide automation
5. **Infrastructure** from `syntek-infrastructure` deploys and hosts the final website

**Observability Integration:**

- All repositories send structured logs to **Loki** (managed by syntek-infrastructure)
- Application metrics flow to **Prometheus** for monitoring and alerting
- Error tracking and performance monitoring via **Glitchtip**
- **Grafana dashboards** provide unified monitoring across all platform components
- **n8n workflows** handle service routing and API orchestration between repositories

---

## CMS Platform Features

### Drag-and-Drop Page Builder

**Visual Website Building for Non-Technical Users**

- **Real-Time Editing**: Live preview of changes as you build
- **Component Library**: Pre-built blocks (headers, galleries, forms, etc.)
- **Responsive Design**: Automatic mobile and tablet optimization
- **Custom Styling**: Brand colors, fonts, and design token management
- **Content Management**: Easy text, image, and media updates
- **SEO Tools**: Built-in optimization suggestions and meta tag management

**Technical Implementation:**

- React-based drag-and-drop interface
- JSON-based content structure for flexibility
- Database-driven design tokens for consistent branding
- Real-time WebSocket updates for collaborative editing

### Online Development Environment

**Full Development Stack in the Browser**

#### Code Editor Integration

- **Monaco Editor**: VS Code experience in the browser
- **Syntax Highlighting**: Support for all major languages (JavaScript, Python, CSS, HTML, etc.)
- **IntelliSense**: Code completion and error detection
- **Multi-File Editing**: Project-wide file management
- **Live Preview**: Real-time rendering of changes

#### TTY Terminal Access

- **Full Shell Access**: Complete command-line interface in the browser
- **Package Management**: Install and manage dependencies
- **Git Operations**: Version control directly in the terminal
- **Build Tools**: Run webpack, npm, pip, and other build processes
- **Server Management**: Start/stop services, monitor logs

**Technical Implementation:**

- Docker-containerized development environments
- WebSocket-based terminal emulation (xterm.js)
- Secure sandboxing for user code execution
- File system persistence and backup

### Database Communication

**Direct Database Access and Management**

- **Visual Query Builder**: Create database queries without SQL knowledge
- **Schema Management**: Design and modify database structures
- **Data Import/Export**: Bulk operations for data migration
- **API Generation**: Automatic REST/GraphQL API creation
- **Real-Time Sync**: Live updates between database and frontend

**Technical Implementation:**

- PostgreSQL as primary database
- GraphQL API layer (Strawberry Django)
- Database migrations with Django ORM
- Multi-tenancy with organization-based isolation

### Version Control Integration

**Git-Based Workflow with Forgejo**

#### Forgejo Integration

- **Self-Hosted Git**: Complete control over source code
- **Collaborative Development**: Multiple developers on same project
- **Branch Management**: Feature branches, pull requests, code reviews
- **Automated Backups**: Regular snapshots and disaster recovery
- **Release Management**: Tagged releases with deployment pipelines

#### Content Versioning

- **Content Branches**: Git-like workflow for content management
  - `feature` → `testing` → `dev` → `staging` → `production`
- **Rollback Capability**: Easily revert to previous versions
- **Change Tracking**: Full audit trail of all modifications
- **Collaborative Editing**: Team-based content creation and approval

**Forgejo Server Details:**

- **Location**: Hosted on Syntek Hetzner server infrastructure
- **Access**: Secure HTTPS with SSH key authentication
- **Backup**: Automated daily backups with redundancy
- **Integration**: Direct connection from CMS interface

---

## Technology Stack

### Backend Infrastructure

- **Framework**: Django 5.2 with Python 3.14
- **API Layer**: GraphQL (Strawberry Django)
- **Database**: PostgreSQL 18.1 with Redis caching
- **Authentication**: Multi-factor authentication (MFA) with JWT tokens
- **Security**: GDPR compliance, audit logging, encrypted data storage

### Frontend Applications

- **Web Application**: React 18+ with TypeScript and Tailwind CSS
- **Mobile Application**: React Native with TypeScript and NativeWind
- **Admin Interface**: Django Admin with custom CMS interface
- **Editor Integration**: Monaco Editor (VS Code) for code editing

### Development Tools

- **Containerization**: Docker and Docker Compose for all environments
- **Package Management**: uv (Python), npm/yarn (JavaScript)
- **Testing**: pytest (Python), Jest (JavaScript), Cypress (E2E)
- **Code Quality**: Ruff, Black, ESLint, Prettier

### Infrastructure & Deployment

- **Operating System**: NixOS for reproducible infrastructure
- **Orchestration**: Custom Rust CLI tools for deployment automation
- **Version Control**: Forgejo (self-hosted Git) on Hetzner infrastructure
- **Workflow Automation**: n8n for service routing, API orchestration, and inter-service communication
- **Observability Integration**: Structured logging to Loki, metrics to Prometheus, error tracking to Glitchtip
- **Monitoring & Alerting**: Managed by syntek-infrastructure (Grafana dashboards, alerting rules)

### AI & Automation

- **Content AI**: Anthropic Claude integration for content assistance
- **Code AI**: AI-powered code completion and debugging
- **SEO AI**: Automated SEO optimization and content suggestions
- **Infrastructure AI**: Predictive scaling and performance optimization

---

## Template System

The platform includes **40 professional website templates** across 8 industry categories, with 5 unique designs per category.

### Template Categories

#### 1. **E-commerce** (5 templates)

- Online stores with shopping carts and payment processing
- Product catalogs with search and filtering
- Inventory management and order tracking
- Integration with payment gateways (Stripe, PayPal, etc.)
- Customer accounts and wishlist functionality

#### 2. **Church & Religious** (5 templates)

- Sermon streaming and podcast integration
- Event calendars and registration systems
- Donation processing and member management
- Prayer request systems and community features
- Multi-location church management

#### 3. **Charity & Non-Profit** (5 templates)

- Donation campaigns and fundraising tools
- Volunteer management and registration
- Impact tracking and reporting dashboards
- Grant application systems
- Transparency and financial reporting

#### 4. **Small & Medium Business (SMB)** (5 templates)

- Professional service websites
- Lead generation and contact forms
- Customer testimonials and case studies
- Service booking and appointment systems
- Local SEO optimization

#### 5. **Estate Agent & Property** (5 templates)

- Property listings with search and filters
- Virtual tours and photo galleries
- Mortgage calculators and financing tools
- Agent profiles and contact systems
- MLS integration and property management

#### 6. **High Street Shop & Retail** (5 templates)

- Local business directories and maps
- Click-and-collect ordering systems
- Local event promotion and community features
- Customer loyalty programs
- Multi-location inventory management

#### 7. **Corporate & Enterprise** (5 templates)

- Professional corporate websites
- Team directories and leadership pages
- Investor relations and financial reporting
- News and press release systems
- Career pages and job applications

#### 8. **Restaurant & Hospitality** (5 templates)

- Online menu and ordering systems
- Table reservation and booking
- Event hosting and catering services
- Customer reviews and feedback
- Multi-location restaurant management

### Template Features

**Every template includes:**

- **Mobile-First Design**: Responsive across all device sizes
- **SEO Optimization**: Built-in search engine optimization
- **Accessibility Compliance**: WCAG 2.1 AA standards
- **Performance Optimized**: Fast loading times and Core Web Vitals
- **Customization Ready**: Easy branding and color scheme changes
- **Content Management**: Integrated CMS for easy updates

**Technical Specifications:**

- **Framework**: Next.js 14+ with React Server Components
- **Styling**: Tailwind CSS with custom design systems
- **Performance**: Lighthouse scores of 90+ across all metrics
- **Deployment**: Automated deployment pipelines
- **Maintenance**: Regular updates and security patches

---

## Development Workflow

### For Non-Technical Users (Content Creators)

1. **Template Selection**: Choose from 40 industry-specific templates
2. **Drag-and-Drop Building**: Use visual editor to customize pages
3. **Content Management**: Add text, images, and media through intuitive interface
4. **Preview & Testing**: Real-time preview across different device sizes
5. **Publishing**: One-click deployment to staging and production environments

### For Developers

1. **Code Editor Access**: Full Monaco/VS Code experience in browser
2. **Terminal Access**: Complete shell access for advanced development
3. **Version Control**: Integrated Forgejo Git workflow with branching
4. **Database Management**: Direct database access and query tools
5. **API Development**: GraphQL/REST API creation and testing
6. **Deployment**: Automated CI/CD pipelines for testing and production

### Collaborative Workflow

1. **Project Setup**: Initialize from template with team permissions
2. **Content Branching**: Parallel development on different features
3. **Code Review**: Pull request workflow with automated testing
4. **Approval Process**: Staged deployment (testing → staging → production)
5. **Client Handoff**: Training and documentation for ongoing maintenance

### Quality Assurance

- **Automated Testing**: Unit, integration, and E2E tests
- **Performance Monitoring**: Real-time performance metrics and alerts
- **Security Scanning**: Regular vulnerability assessments
- **Accessibility Testing**: Automated and manual accessibility compliance
- **Cross-Browser Testing**: Compatibility across all major browsers

---

## Getting Started

### For Project Managers & Stakeholders

1. **Platform Overview**: Review this documentation and architecture guides
2. **Template Gallery**: Browse available templates at [syntek-template repository]
3. **Requirements Gathering**: Use our project planning templates and checklists
4. **Team Setup**: Establish development team and assign repository access
5. **Project Kickoff**: Initial platform setup and customization planning

### For Developers

1. **Repository Access**: Clone relevant repositories based on your role:
   - **Full-Stack**: `syntek-modules` + `syntek-platform`
   - **Frontend**: `syntek-template` + `syntek-modules`
   - **DevOps**: `syntek-infrastructure` + `syntek-platform`
   - **AI/ML**: `syntek-ai` + `syntek-platform`

2. **Development Environment**:

   ```bash
   # Clone the core platform documentation
   git clone https://github.com/syntek-studio/syntek-platform.git

   # Review setup guides for your specific role
   cd syntek-platform
   cat docs/DEVELOPER-SETUP-{ROLE}.md
   ```

3. **Local Development**: Follow environment-specific setup guides
4. **Documentation**: Read architecture guides and API references
5. **First Contribution**: Start with good-first-issue labeled tickets

### For Clients

1. **Demo Access**: Request a demo environment for testing
2. **Template Selection**: Choose your industry template
3. **Content Preparation**: Gather branding materials, content, and media
4. **Training Session**: Scheduled onboarding with the drag-and-drop interface
5. **Go-Live Planning**: Migration and launch timeline coordination

### Repository Links

- **🏗️ [syntek-infrastructure](https://github.com/Syntek-Dev/syntek-infrastructure)** - Server infrastructure and automation
- **🧩 [syntek-modules](https://github.com/Syntek-Dev/syntek-modules)** - Business logic and reusable components
- **🤖 [syntek-ai](https://github.com/Syntek-Dev/syntek-ai)** - AI features and automation
- **📋 [syntek-platform](https://github.com/Syntek-Dev/syntek-platform)** - Documentation and architecture _(this repo)_
- **🎨 [syntek-template](https://github.com/Syntek-Dev/syntek-template)** - Website templates and themes

### Documentation Structure

```
syntek-platform/
├── README.md                    # This overview
├── docs/
│   ├── ARCHITECTURE/            # Platform architecture guides
│   ├── API/                     # API references and examples
│   ├── DEPLOYMENT/              # Deployment and infrastructure guides
│   ├── DEVELOPMENT/             # Developer onboarding and guides
│   ├── TEMPLATES/               # Template documentation and customization
│   ├── USER-GUIDES/             # End-user documentation
│   └── TROUBLESHOOTING/         # Common issues and solutions
└── examples/                    # Code examples and tutorials
```

---

## Contact

### Support & Documentation

- **Documentation**: This repository's `/docs` folder
- **API Reference**: [Platform API Documentation](docs/API/)
- **Video Tutorials**: [YouTube Channel](https://youtube.com/syntek-studio)

### Development Community

- **GitHub Discussions**: [Community Forum](https://github.com/syntek-studio/syntek-platform/discussions)
- **Discord Server**: [Developer Community](https://discord.gg/syntek)
- **Office Hours**: Weekly developer Q&A sessions

### Commercial Support

- **Sales Inquiries**: sales@syntek-studio.com
- **Technical Support**: support@syntek-studio.com
- **Partnership Opportunities**: partners@syntek-studio.com

### Infrastructure

- **Forgejo Server**: https://git.syntek-studio.com
- **Status Page**: https://status.syntek-studio.com
- **Security Reports**: security@syntek-studio.com

---

**Built with ❤️ by the Syntek Studio team**

_Last updated: March 2026_
