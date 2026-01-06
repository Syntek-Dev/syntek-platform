# Release Notes

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Table of Contents

- [Latest Release](#latest-release)
- [Previous Releases](#previous-releases)

---

## Latest Release

### Version 0.2.0 - 3 January 2026

This release focuses on establishing a professional version management system and documentation standards for the project.

#### What's New

**Version Tracking Made Easy**

We've implemented a comprehensive version management system:

- **VERSION File**: Simple version number file for build systems and automation
- **Technical Change Log**: Detailed VERSION-HISTORY.md documenting all code changes
- **Developer Summary**: CHANGELOG.md following industry-standard Keep a Changelog format
- **User-Friendly Release Notes**: This file (RELEASES.md) explaining what's new in plain language

**Consistent Documentation**

All documentation now includes helpful metadata headers:

- Last updated date in British format (DD/MM/YYYY)
- Current version number
- Maintainer information
- Language specification (British English)
- Timezone reference (Europe/London)

This means you can quickly see when any documentation was last updated and which version it applies to.

**Better Project Organisation**

Over 60 documentation files throughout the project now follow consistent standards:

- Clear version tracking
- Standardised date formats
- Consistent language (British English throughout)
- Easy to identify outdated documentation

#### Why This Matters

**For Developers:**

- Quickly see what changed between versions
- Understand the technical details of each release
- Track when documentation was last updated
- Know which version of the docs matches your code

**For Project Managers:**

- Clear release history for stakeholder communication
- Version numbers follow semantic versioning (MAJOR.MINOR.PATCH)
- Easy to track project progress over time

**For Users:**

- Plain-language release notes explain what's new
- No need to decipher technical jargon
- Clear understanding of feature additions and improvements

#### Technical Details

This is a minor version bump (0.1.0 → 0.2.0) because we've added new features (version management documentation) without changing any existing functionality or breaking any APIs.

The version management system will make future releases more organised and easier to understand.

---

## Previous Releases

### Version 0.1.0 - 3 January 2026

Welcome to the first release of the Django/Wagtail Backend Template! This template provides everything you need to build modern, secure, and scalable backend applications.

#### What's New

**Complete Backend Foundation**

This release includes a fully configured Django and Wagtail CMS setup ready for your next project:

- **Content Management**: Wagtail CMS admin interface for managing your content without writing code
- **Modern API**: GraphQL API for flexible data querying from your frontend applications
- **Database Ready**: PostgreSQL database configured and ready to use
- **Fast Performance**: Redis caching ensures your application responds quickly

**Multiple Environments Made Easy**

Work confidently across different stages of your project:

- **Development**: Local Docker environment with hot reload - see your changes instantly
- **Testing**: Isolated test environment that doesn't interfere with your development work
- **Staging**: Test in production-like conditions before going live
- **Production**: Secure, optimised setup for serving real users

**Automated Quality Checks**

Never worry about code quality issues:

- Automatic code formatting keeps your code consistent
- Security scanning finds vulnerabilities before they become problems
- Automated tests run on every change
- Pull request validation ensures high-quality code

**Project Management Integration**

Stay organised with ClickUp integration:

- Automatic task synchronisation with your git branches
- Pull requests linked to user stories
- Clear visibility of what's being worked on

**Developer-Friendly**

Get started quickly with comprehensive tooling:

- One-command setup for each environment
- Pre-configured VS Code with recommended extensions
- Detailed documentation for every feature
- Example configurations for common scenarios

#### Key Features

**Security First**

- API authentication with modern JWT tokens
- Rate limiting prevents abuse and protects your server
- Security headers protect against common web vulnerabilities
- Automated security scanning in every build

**Testing Made Simple**

- Run all tests with a single command
- Code coverage reporting shows what's tested
- Fast test execution with optimised containers
- Easy to run tests locally before pushing code

**Deployment Automation**

- Push to staging with automatic deployment
- Production deployments with safety checks
- Database migrations handled automatically
- Health checks ensure deployments succeed

**Documentation**

- Step-by-step developer setup guide
- Clear examples for common tasks
- Troubleshooting guides for common issues
- API documentation with sample queries

#### Getting Started

To start using this template:

1. Clone the repository to your local machine
2. Run `./scripts/env/dev.sh start` to start the development environment
3. Visit `http://localhost:8000` to see your application
4. Visit `http://localhost:8000/admin` to access the Wagtail admin

The comprehensive documentation in the `docs/` folder will guide you through everything else.

#### What This Means for You

**For Developers:**

- Spend less time on setup, more time building features
- Consistent code quality across your team
- Confidence that your code is secure and tested

**For Project Managers:**

- Clear visibility into development progress via ClickUp integration
- Automated quality checks reduce bugs
- Faster deployment cycles with CI/CD automation

**For DevOps:**

- Environment isolation prevents conflicts
- Docker containers ensure consistency across environments
- Automated deployments reduce manual work
- Comprehensive logging and monitoring hooks

#### Coming Soon

In future releases, we're planning to add:

- Database migration rollback tools
- Performance monitoring integration
- Automated backup solutions
- API documentation generation
- Enhanced GraphQL subscriptions
- Multi-region deployment support
- Advanced caching strategies

---

## Previous Releases

None - This is the initial release.
