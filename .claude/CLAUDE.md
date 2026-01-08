# Backend Template - Django Project

**Last Updated**: 08/01/2026
**Version**: 0.5.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

> **Stack:** Django + PostgreSQL + GraphQL
> **Container:** Docker Compose
> **Package:** backend-template
> **Last Updated:** 2026-01-08

## Table of Contents

- [Backend Template - Django Project](#backend-template---django-project)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
    - [Architecture](#architecture)
    - [Platform Components](#platform-components)
  - [Structures to Gain Context](#structures-to-gain-context)
  - [Development Workflow](#development-workflow)
    - [Starting Development](#starting-development)
    - [Running Tests](#running-tests)
  - [Environment Configuration](#environment-configuration)
  - [Key Conventions](#key-conventions)
    - [Django Apps](#django-apps)
    - [GraphQL API](#graphql-api)
    - [CMS Content Management](#cms-content-management)
  - [Code Quality Principles](#code-quality-principles)
    - [Minimal Code Philosophy](#minimal-code-philosophy)
    - [DRY (Don't Repeat Yourself)](#dry-dont-repeat-yourself)
    - [Code Quality Checklist](#code-quality-checklist)
    - [Refactoring Guidelines](#refactoring-guidelines)
  - [Line Length Standards](#line-length-standards)
    - [Exceptions](#exceptions)
    - [Running Lint Checks](#running-lint-checks)
  - [Documentation Standards](#documentation-standards)
    - [Docstring Requirements](#docstring-requirements)
    - [Google-Style Docstring Format](#google-style-docstring-format)
    - [Type Hints](#type-hints)
    - [Django Models](#django-models)
    - [Django Views](#django-views)
    - [Django Serializers](#django-serializers)
    - [GraphQL Resolvers](#graphql-resolvers)
    - [Comments: When to Use Them](#comments-when-to-use-them)
    - [Module-Level Docstrings](#module-level-docstrings)
    - [Examples of What NOT to Document](#examples-of-what-not-to-document)
  - [Testing Standards](#testing-standards)
    - [Testing Philosophy](#testing-philosophy)
    - [Testing Framework Stack](#testing-framework-stack)
    - [Test Directory Structure](#test-directory-structure)
    - [Test File Naming Conventions](#test-file-naming-conventions)
    - [TDD (Test-Driven Development)](#tdd-test-driven-development)
    - [BDD (Behaviour-Driven Development)](#bdd-behaviour-driven-development)
    - [Integration Tests](#integration-tests)
    - [End-to-End Tests](#end-to-end-tests)
    - [GraphQL API Tests](#graphql-api-tests)
    - [Test Markers](#test-markers)
    - [Test Coverage Requirements](#test-coverage-requirements)
    - [Fixtures and Factory Pattern](#fixtures-and-factory-pattern)
    - [Test-Writer Agent Instructions](#test-writer-agent-instructions)
    - [Running Tests Summary](#running-tests-summary)
  - [Markdown Documentation Standards](#markdown-documentation-standards)
    - [File Naming Convention](#file-naming-convention)
    - [Required VS Code Extension](#required-vs-code-extension)
    - [Markdown All in One Commands](#markdown-all-in-one-commands)
    - [Table of Contents Requirements](#table-of-contents-requirements)
    - [Document Structure](#document-structure)
    - [Markdown Formatting Rules](#markdown-formatting-rules)
    - [Link Validation](#link-validation)
  - [Command Execution Requirements](#command-execution-requirements)
    - [Claude Agent Instructions](#claude-agent-instructions)
    - [Environment Scripts](#environment-scripts)
    - [Script Command Examples](#script-command-examples)
      - [Development (`scripts/env/dev.sh`)](#development-scriptsenvdevsh)
      - [Testing (`scripts/env/test.sh`)](#testing-scriptsenvtestsh)
      - [Staging (`scripts/env/staging.sh`)](#staging-scriptsenvstagingsh)
      - [Production (`scripts/env/production.sh`)](#production-scriptsenvproductionsh)
    - [Docker Container Access](#docker-container-access)
    - [Quick Reference](#quick-reference)
  - [Syntek Dev Suite Agents](#syntek-dev-suite-agents)
    - [Versioning Requirements](#versioning-requirements)
  - [Project Management](#project-management)
  - [Platform Architecture](#platform-architecture)
    - [Key Platform Features](#key-platform-features)
    - [Development Phases](#development-phases)
  - [Notes](#notes)

## Project Overview

This is a comprehensive Django CMS platform that serves as the backend for a multi-repository
architecture supporting web and mobile applications. It provides content management, design tokens,
multi-tenancy, SaaS integrations, and enterprise-grade security features.

**Platform Vision:** This backend is part of the Syntek CMS Platform - a comprehensive system
enabling businesses to build and manage websites/apps with integrated business tools, consistent
branding, and multi-platform deployment.
See [docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md](../docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md) for the
complete architectural plan.

### Architecture

- **Framework:** Django with custom CMS
- **Database:** PostgreSQL (containerised for dev/test, managed for staging/prod)
- **API:** GraphQL (Strawberry)
- **Cache:** Redis or Valkey
- **Email:** Mailpit (dev/test simulation)
- **Containers:** Docker Compose per environment
- **Multi-Tenancy:** Organisation-based with isolated data
- **Security:** 2FA, audit logging, encrypted secrets, IP encryption

### Platform Components

This backend integrates with:

- **ui_design** - Shared React component library for web and mobile
- **frontend_web** - React web application consuming this GraphQL API
- **frontend_mobile** - React Native mobile app for iOS/Android

For complete platform architecture and phase breakdown, see [docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md](../docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md).

## Structures to Gain Context

Look at the root `README.md` for the full project structure before carrying out any tasks.

Each directory and sub-directory has a `README.md` with the directory and sub-directory structures.
Read these structures to identify what needs accessing.

Each .md file should have an overview or executive summary near the start to allow you to gain an
understanding as to whether this `*.md` file is relevant to the agents task.

Each coding file should have a `docstring` at the very top explaining the overview of the code file. This will help the agent understand if the file needs updating.

Before each agent runs to gain the understanding do the following:

1. Read root `README.md` project structure tree to find all relevant files for the task
2. Read a directories `README.md` for the directories structure tree
3. Read the relevant sub-directories `README.md` for the sub-directories structure tree
4. If a `*.md` file read the `Overview` or `Executive Summary` to gain context of the file, if a code file read the `docstring` at the top of the file to gain context of the file

**Note:** The apps structure reflects the phased implementation plan. See
[docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md](../docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md) for the
complete 16-phase development roadmap.

## Development Workflow

### Starting Development

```bash
# Start development containers
docker compose -f docker/dev/docker-compose.yml up -d

# Run migrations
docker compose -f docker/dev/docker-compose.yml exec web python manage.py migrate

# Create superuser
docker compose -f docker/dev/docker-compose.yml exec web python manage.py createsuperuser

# Access the application
# Web: http://localhost:8000
# Admin: http://localhost:8000/admin
# Mailpit: http://localhost:8025
```

### Running Tests

```bash
# Run all tests
docker compose -f docker/test/docker-compose.yml run --rm web pytest

# Run with coverage
docker compose -f docker/test/docker-compose.yml run --rm web pytest --cov=apps
```

## Environment Configuration

| Environment | Database               | Cache             | Email   |
| ----------- | ---------------------- | ----------------- | ------- |
| dev         | PostgreSQL (container) | Redis (container) | Mailpit |
| test        | PostgreSQL (container) | Redis (container) | Mailpit |
| staging     | PostgreSQL (AWS/DO)    | Redis (managed)   | SMTP    |
| production  | PostgreSQL (AWS/DO)    | Redis (managed)   | SMTP    |

## Key Conventions

### Django Apps

- Each app should be self-contained in `apps/`
- Use `apps.app_name` for imports
- Models should include `created_at` and `updated_at` fields
- All models must support multi-tenancy via `organisation` foreign key

### GraphQL API

- Schema defined in `api/schema.py`
- Use Strawberry for GraphQL (preferred over Graphene)
- Mutations should return the modified object
- All queries/mutations must respect organisation boundaries
- Implement query depth limiting and complexity analysis

### CMS Content Management

- Page models use JSON content structure for flexibility
- Block-based content system for reusable components
- Content branching workflow: feature → testing → dev → staging → production
- Version history maintained per branch
- Design tokens stored in database and served via GraphQL
- Template system supports 9 site types (e-commerce, blog, corporate, etc.)

See [docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md](../docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md)
for detailed CMS architecture.

## Code Quality Principles

This project enforces strict code quality standards to maintain a clean, maintainable codebase.

### Minimal Code Philosophy

**CRITICAL:** Always write the minimum amount of code necessary to achieve the requirement.

**Principles:**

1. **No speculative code** - Only implement what is explicitly required
2. **No "just in case" features** - Don't add functionality that might be needed later
3. **No premature abstractions** - Three similar lines of code are better than a premature helper
4. **No extra configurability** - A simple feature doesn't need extra options
5. **No unnecessary validation** - Only validate at system boundaries (user input, external APIs)

**Examples:**

```python
# ❌ BAD - Over-engineered with unnecessary abstraction
class UserEmailValidator:
    """Validates user email addresses."""

    def __init__(self, allow_subdomains: bool = True, blocked_domains: list = None):
        self.allow_subdomains = allow_subdomains
        self.blocked_domains = blocked_domains or []

    def validate(self, email: str) -> bool:
        # ... 50 lines of validation logic
        pass

def validate_user_email(email: str) -> bool:
    """Validate email using the validator class."""
    validator = UserEmailValidator()
    return validator.validate(email)


# ✅ GOOD - Simple, direct implementation
def validate_user_email(email: str) -> bool:
    """Validate email format."""
    return bool(re.match(r'^[^@]+@[^@]+\.[^@]+$', email))
```

```python
# ❌ BAD - Unnecessary helper function for one-time operation
def get_active_user_emails(users: list[User]) -> list[str]:
    """Extract emails from active users."""
    return [u.email for u in users if u.is_active]

def send_newsletter():
    users = User.objects.all()
    emails = get_active_user_emails(users)
    send_bulk_email(emails)


# ✅ GOOD - Inline the simple logic
def send_newsletter():
    """Send newsletter to active users."""
    emails = User.objects.filter(is_active=True).values_list('email', flat=True)
    send_bulk_email(list(emails))
```

### DRY (Don't Repeat Yourself)

**CRITICAL:** Eliminate code duplication, but only when there's actual repetition.

**When to apply DRY:**

- Same logic appears in 3+ places
- Copy-pasting code between functions/classes
- Similar validation rules across multiple models
- Repeated query patterns

**When NOT to apply DRY:**

- Two pieces of code happen to look similar but serve different purposes
- Extracting code would require many parameters to handle variations
- The "shared" code is trivial (1-2 lines)

**Examples:**

```python
# ❌ BAD - Repeated logic across multiple views
class UserListView(ListView):
    def get_queryset(self):
        return User.objects.filter(
            organisation=self.request.user.organisation,
            is_active=True
        ).select_related('organisation')

class UserDetailView(DetailView):
    def get_queryset(self):
        return User.objects.filter(
            organisation=self.request.user.organisation,
            is_active=True
        ).select_related('organisation')

class UserUpdateView(UpdateView):
    def get_queryset(self):
        return User.objects.filter(
            organisation=self.request.user.organisation,
            is_active=True
        ).select_related('organisation')


# ✅ GOOD - Extract to mixin when pattern repeats 3+ times
class OrganisationFilterMixin:
    """Filter queryset by user's organisation."""

    def get_queryset(self):
        return super().get_queryset().filter(
            organisation=self.request.user.organisation,
            is_active=True
        ).select_related('organisation')

class UserListView(OrganisationFilterMixin, ListView):
    model = User

class UserDetailView(OrganisationFilterMixin, DetailView):
    model = User

class UserUpdateView(OrganisationFilterMixin, UpdateView):
    model = User
```

```python
# ❌ BAD - Forced DRY creating unnecessary complexity
def process_entity(entity_type: str, entity_id: int, action: str) -> dict:
    """Generic entity processor."""
    if entity_type == 'user':
        model = User
        serializer = UserSerializer
    elif entity_type == 'organisation':
        model = Organisation
        serializer = OrganisationSerializer
    # ... more conditionals

    instance = model.objects.get(id=entity_id)
    if action == 'serialize':
        return serializer(instance).data
    # ... more action handling


# ✅ GOOD - Keep separate when logic differs meaningfully
def get_user_data(user_id: int) -> dict:
    """Get serialised user data."""
    user = User.objects.select_related('organisation').get(id=user_id)
    return UserSerializer(user).data

def get_organisation_data(org_id: int) -> dict:
    """Get serialised organisation data."""
    org = Organisation.objects.prefetch_related('users').get(id=org_id)
    return OrganisationSerializer(org).data
```

### Code Quality Checklist

Before committing code, verify:

- [ ] **Minimal:** No unnecessary code, abstractions, or features
- [ ] **DRY:** No duplicated logic (3+ occurrences)
- [ ] **Single Responsibility:** Each function/class does one thing
- [ ] **No Dead Code:** No commented-out code, unused imports, or unreachable branches
- [ ] **No Magic Numbers:** Constants are named and documented
- [ ] **Clear Intent:** Code is self-documenting with meaningful names

### Refactoring Guidelines

**Only refactor when:**

1. There's measurable code duplication (3+ occurrences)
2. A function exceeds 50 lines
3. A class has more than 10 public methods
4. Cyclomatic complexity exceeds 10
5. The change is explicitly requested

**Never refactor:**

- Working code "just to improve it"
- Code that's not part of the current task
- To add "future-proofing" abstractions

## Line Length Standards

All files in this project must adhere to consistent line length limits. These are enforced by
linters and formatters in CI/CD pipelines.

| File Type          | Max Line Length | Enforced By  | Configuration File   |
| ------------------ | --------------- | ------------ | -------------------- |
| Python (`.py`)     | 100 characters  | Black, isort | `pyproject.toml`     |
| Markdown (`.md`)   | 120 characters  | markdownlint | `.markdownlint.json` |
| JavaScript (`.js`) | 100 characters  | Prettier     | `.prettierrc`        |
| TypeScript (`.ts`) | 100 characters  | Prettier     | `.prettierrc`        |
| HTML (`.html`)     | 120 characters  | Prettier     | `.prettierrc`        |
| CSS (`.css`)       | 100 characters  | Prettier     | `.prettierrc`        |
| YAML (`.yml`)      | 100 characters  | Prettier     | `.prettierrc`        |
| JSON (`.json`)     | 100 characters  | Prettier     | `.prettierrc`        |

### Exceptions

- **Tables in Markdown**: Line length is not enforced within tables
- **Code blocks in Markdown**: Line length is not enforced within fenced code blocks
- **URLs and links**: Long URLs may exceed the limit if they cannot be shortened

### Running Lint Checks

```bash
# Check all formatting and linting
npm run lint

# Check Python formatting
npm run lint:prettier

# Check Markdown linting
npm run lint:markdown

# Auto-fix Markdown issues where possible
npm run lint:markdown:fix
```

## Documentation Standards

This project uses **Google-style docstrings** for all Python code. Documentation is essential for
code maintainability and team collaboration.

### Docstring Requirements

Docstrings are **required** for:

- All modules (top-level file docstrings)
- All classes (including Django models, views, serializers)
- All public functions and methods
- All async functions
- Complex private methods (those containing business logic)

Docstrings are **optional** for:

- Simple getter/setter methods
- Methods that override parent class methods with no change in behaviour
- Magic methods (**str**, **repr**) if behaviour is obvious

### Google-Style Docstring Format

```python
def function_name(param1: str, param2: int = 10) -> dict:
    """Brief one-line description ending with a period.

    Extended description providing context, use cases, or important notes.
    This can span multiple lines if needed. Explain the 'why' not just the 'what'.

    Args:
        param1: Description of param1. Include type information here if helpful.
        param2: Description of param2. Defaults to 10.

    Returns:
        Description of the return value and its structure/contents.

    Raises:
        ValueError: When something specific goes wrong.
        TypeError: When wrong type is passed.

    Example:
        >>> result = function_name("test", 5)
        >>> print(result)
        {'success': True}
    """
    pass
```

### Type Hints

**Type hints are required** for all function signatures:

```python
def get_user(user_id: int) -> Optional[User]:
    """Retrieve a user by ID."""
    pass

def process_items(items: List[str]) -> Dict[str, int]:
    """Process items and return counts."""
    pass

async def fetch_data(url: str, timeout: int = 30) -> bytes:
    """Asynchronously fetch data from URL."""
    pass
```

### Django Models

Every Django model must include docstrings explaining its purpose and business logic:

```python
from django.db import models
from django.utils.translation import gettext_lazy as _


class Author(models.Model):
    """Represents a person who writes articles or content.

    This model stores core author information including name, email, and biography.
    Authors are linked to articles through foreign keys and can have multiple
    publications across different sections.

    Attributes:
        name: The author's full name.
        email: Unique email address for the author.
        bio: Extended biography of the author.
        created_at: Timestamp when the author record was created.
        updated_at: Timestamp when the author record was last modified.
    """

    name = models.CharField(max_length=255, help_text=_("Author's full name"))
    email = models.EmailField(unique=True, help_text=_("Contact email address"))
    bio = models.TextField(blank=True, help_text=_("Extended biography"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["email"]),
        ]

    def __str__(self) -> str:
        """Return the author's name."""
        return self.name

    def get_published_count(self) -> int:
        """Retrieve the total number of published articles by this author.

        Returns:
            The count of articles with status='published' linked to this author.
        """
        return self.articles.filter(status="published").count()
```

### Django Views

All views should include docstrings explaining their purpose and any special handling:

```python
from django.views.generic import DetailView
from apps.articles.models import Article


class ArticleDetailView(DetailView):
    """Display a single published article with related metadata.

    This view handles GET requests for individual articles. Articles must be
    published to be visible. It populates additional context with related
    articles, comments, and author information.

    Attributes:
        model: The Article model queryset.
        context_object_name: The name of the article in the template context.
        template_name: The template used to render the article detail page.

    Query Optimisation:
        Uses select_related('author') to reduce database queries when
        displaying author information alongside the article.
    """

    model = Article
    context_object_name = "article"
    template_name = "articles/article_detail.html"

    def get_queryset(self):
        """Filter articles to show only published items.

        Returns:
            QuerySet of published Article objects with author information
            optimised for database queries.
        """
        return Article.objects.filter(status="published").select_related("author")

    def get_context_data(self, **kwargs):
        """Add related articles and comment count to template context.

        Returns:
            Context dictionary containing the article and related metadata.
        """
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        context["related_articles"] = (
            Article.objects
            .filter(category=article.category, status="published")
            .exclude(id=article.id)[:5]
        )
        context["comment_count"] = article.comments.filter(approved=True).count()
        return context
```

### Django Serializers

Serializers should document custom fields and validation logic:

```python
from rest_framework import serializers
from apps.articles.models import Article, Author


class AuthorSerializer(serializers.ModelSerializer):
    """Serialise Author model for API responses.

    Used for nested author information in article listings and detail views.

    Fields:
        id: The author's unique identifier.
        name: The author's full name.
        email: The author's email address.
    """

    class Meta:
        model = Author
        fields = ["id", "name", "email"]
        read_only_fields = ["id"]


class ArticleSerializer(serializers.ModelSerializer):
    """Serialise Article model with nested author information.

    This serialiser includes author details, computed fields for comment counts,
    and validates that published articles have all required fields.

    Fields:
        id: The article's unique identifier.
        title: The article title.
        author: Nested author information.
        comment_count: Computed field for the number of approved comments.

    Validation:
        - Published articles must have a publication date.
        - Title must be unique per author per month.
    """

    author = AuthorSerializer(read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ["id", "title", "author", "comment_count", "status"]
        read_only_fields = ["id", "comment_count"]

    def get_comment_count(self, obj: Article) -> int:
        """Get the count of approved comments for this article.

        Args:
            obj: The Article instance being serialised.

        Returns:
            The number of approved comments.
        """
        return obj.comments.filter(approved=True).count()

    def validate(self, data: dict) -> dict:
        """Validate article data before saving.

        Args:
            data: The incoming serialiser data.

        Returns:
            The validated data.

        Raises:
            serializers.ValidationError: If published articles lack required fields.
        """
        if data.get("status") == "published" and not data.get("published_at"):
            raise serializers.ValidationError(
                "Published articles must have a publication date."
            )
        return data
```

### GraphQL Resolvers

GraphQL resolvers should document their purpose, arguments, and return types:

```python
import strawberry
from typing import List, Optional
from apps.articles.models import Article as ArticleModel


@strawberry.type
class Article:
    """Represents an article in the GraphQL schema.

    This type exposes article information and related metadata to clients
    querying the GraphQL API.
    """

    id: strawberry.ID
    title: str
    content: str
    author_name: str

    @strawberry.field
    def comment_count(self) -> int:
        """Get the number of approved comments for this article.

        Returns:
            The count of comments where approved=True.
        """
        article = ArticleModel.objects.get(id=int(self.id))
        return article.comments.filter(approved=True).count()


@strawberry.type
class Query:
    """Root query type for the GraphQL API.

    Provides access to articles, authors, and other publicly available data.
    All resolvers use select_related and prefetch_related optimisations
    to reduce database queries.
    """

    @strawberry.field
    def article(self, id: strawberry.ID) -> Optional[Article]:
        """Retrieve a single published article by ID.

        This resolver fetches a published article with author information
        optimised for database queries.

        Args:
            id: The unique identifier of the article.

        Returns:
            The Article object if found and published, None otherwise.
        """
        try:
            article = (
                ArticleModel.objects
                .filter(status="published")
                .select_related("author")
                .get(id=id)
            )
            return Article(
                id=strawberry.ID(str(article.id)),
                title=article.title,
                content=article.content,
                author_name=article.author.name,
            )
        except ArticleModel.DoesNotExist:
            return None

    @strawberry.field
    def articles(self, limit: int = 10) -> List[Article]:
        """Retrieve a paginated list of published articles.

        Articles are ordered by most recent first. This resolver uses
        select_related to fetch author information in a single query.

        Args:
            limit: Maximum number of articles to return (default: 10, max: 100).

        Returns:
            A list of Article objects.
        """
        if limit > 100:
            limit = 100

        articles = (
            ArticleModel.objects
            .filter(status="published")
            .order_by("-created_at")[:limit]
            .select_related("author")
        )

        return [
            Article(
                id=strawberry.ID(str(article.id)),
                title=article.title,
                content=article.content,
                author_name=article.author.name,
            )
            for article in articles
        ]
```

### Comments: When to Use Them

**Add comments when:**

- Explaining business logic that isn't obvious from the code.
- Documenting workarounds or hacks with explanation of why they exist.
- Noting performance considerations or optimisations.
- Clarifying complex algorithms or mathematical operations.
- Linking to external resources, tickets, or documentation.

```python
# Good: Explains non-obvious business logic
def calculate_shipping_cost(weight: float, distance: int) -> float:
    """Calculate shipping cost based on weight and distance.

    Uses a progressive pricing model where costs increase non-linearly
    with distance to account for fuel and route optimisation costs.
    """
    # Base cost plus distance-adjusted markup (exponential for long distances)
    base = 5.0 + (weight * 0.5)
    distance_factor = 1 + (distance / 1000) ** 1.1
    return base * distance_factor
```

**Avoid comments when:**

- The code is self-documenting (clear variable/function names explain intent).
- The comment simply restates what the code does.
- Using a comment when a well-named variable or function would be clearer.
- Commenting obvious operations like incrementing counters.

```python
# Bad: Comment states the obvious
count = 0
for item in items:
    count += 1  # Increment count by 1

# Good: Self-documenting code
item_count = len(items)
```

```python
# Bad: Comment repeats the code
user = User.objects.get(id=user_id)  # Get user from database

# Good: Code is self-documenting
current_user = User.objects.get(id=user_id)
```

### Module-Level Docstrings

Every Python module should begin with a docstring:

```python
"""Module for handling article publication workflows.

This module contains functions and classes responsible for publishing articles,
managing publication schedules, and notifying subscribers of new content.
It integrates with the notification system and analytics tracking.

Classes:
    PublicationScheduler: Manages scheduled article publishing.
    PublicationNotifier: Sends notifications to subscribers.

Functions:
    publish_article: Immediately publish an article.
    schedule_publication: Schedule an article for future publishing.
"""

from django.utils import timezone
from apps.articles.models import Article
from apps.notifications.tasks import send_notification

# Module code follows...
```

### Examples of What NOT to Document

```python
# Bad: Over-documenting obvious code
def get_name(self) -> str:
    """Return the name of the user.

    This method retrieves the name attribute from the User instance
    and returns it as a string. The name was set during model creation.
    """
    return self.name

# Good: Let obvious code speak for itself
def get_name(self) -> str:
    """Return the user's name."""
    return self.name


# Bad: Obvious loop counter
for i in range(10):
    # Loop 10 times
    process_item(items[i])

# Good: Use descriptive variable names
for item in items:
    process_item(item)
```

## Testing Standards

This project follows a comprehensive testing strategy using TDD, BDD, and E2E testing approaches.
The test-writer agent (`/syntek-dev-suite:test-writer`) must adhere to these standards.

### Testing Philosophy

**Test-Driven Development (TDD):** Write tests before implementation
**Behaviour-Driven Development (BDD):** Write human-readable scenarios using Gherkin syntax
**End-to-End Testing (E2E):** Test complete user workflows across the entire system

### Testing Framework Stack

| Test Type   | Framework      | Purpose                                      |
| ----------- | -------------- | -------------------------------------------- |
| Unit (TDD)  | pytest         | Fast, isolated tests for individual units    |
| BDD         | pytest-bdd     | Behaviour scenarios in Gherkin syntax        |
| Integration | pytest-django  | Test Django components together              |
| E2E         | pytest-django  | Full user workflows, multi-service tests     |
| GraphQL API | pytest + utils | Test GraphQL queries, mutations, permissions |

### Test Directory Structure

```
tests/
├── conftest.py                  # Global fixtures and pytest configuration
├── fixtures/                    # Shared test fixtures
│   ├── users.py                # User-related fixtures
│   ├── organisations.py        # Organisation fixtures
│   └── common.py               # Common test data
├── unit/                        # TDD unit tests (fast, isolated)
│   ├── test_models.py
│   ├── test_serializers.py
│   ├── test_validators.py
│   ├── test_services.py
│   └── apps/
│       ├── core/
│       │   ├── test_user_model.py
│       │   ├── test_organisation_model.py
│       │   └── test_auth_service.py
│       ├── design/
│       └── cms/
├── bdd/                         # BDD behaviour tests (Gherkin)
│   ├── features/               # Feature files (Gherkin scenarios)
│   │   ├── authentication.feature
│   │   ├── user_management.feature
│   │   ├── organisation_setup.feature
│   │   └── content_publishing.feature
│   ├── step_defs/              # Step definitions
│   │   ├── test_authentication_steps.py
│   │   ├── test_user_steps.py
│   │   ├── test_organisation_steps.py
│   │   └── test_content_steps.py
│   └── conftest.py             # BDD-specific fixtures
├── integration/                 # Integration tests (multiple components)
│   ├── test_auth_flow.py
│   ├── test_organisation_workflow.py
│   ├── test_graphql_api.py
│   ├── test_cms_publishing.py
│   └── test_multi_tenancy.py
├── e2e/                         # End-to-end tests (complete workflows)
│   ├── test_user_registration_to_login.py
│   ├── test_organisation_setup_complete.py
│   ├── test_content_creation_to_publish.py
│   ├── test_design_token_propagation.py
│   └── test_multi_user_collaboration.py
├── graphql/                     # GraphQL-specific tests
│   ├── test_queries.py
│   ├── test_mutations.py
│   ├── test_permissions.py
│   ├── test_filtering.py
│   └── test_pagination.py
└── performance/                 # Performance and load tests
    ├── test_query_performance.py
    └── test_bulk_operations.py
```

### Test File Naming Conventions

| Test Type   | Naming Pattern                        | Example                         |
| ----------- | ------------------------------------- | ------------------------------- |
| Unit        | `test_<component>_<functionality>.py` | `test_user_model_validation.py` |
| BDD Feature | `<feature_name>.feature`              | `authentication.feature`        |
| BDD Steps   | `test_<feature>_steps.py`             | `test_authentication_steps.py`  |
| Integration | `test_<workflow>_integration.py`      | `test_auth_flow_integration.py` |
| E2E         | `test_<workflow>_e2e.py`              | `test_user_registration_e2e.py` |
| GraphQL     | `test_<operation>_<entity>.py`        | `test_query_users.py`           |

### TDD (Test-Driven Development)

**Principles:**

1. Write the test first (Red)
2. Write minimal code to pass (Green)
3. Refactor while keeping tests green (Refactor)

**Unit Test Requirements:**

```python
"""Unit tests for User model validation.

Tests cover:
- Model field validation
- Custom validators
- Model methods
- Business logic
"""

import pytest
from django.core.exceptions import ValidationError
from apps.core.models import User


class TestUserModel:
    """Unit tests for User model."""

    def test_user_creation_with_valid_data(self) -> None:
        """Test user is created successfully with valid data.

        Given: Valid user data (email, name, password)
        When: User.objects.create() is called
        Then: User is created with correct attributes
        """
        user = User.objects.create(
            email="test@example.com",
            first_name="Test",
            last_name="User",
        )

        assert user.id is not None
        assert user.email == "test@example.com"
        assert user.get_full_name() == "Test User"

    def test_user_email_must_be_unique(self) -> None:
        """Test user email must be unique.

        Given: A user with email "test@example.com" exists
        When: Creating another user with the same email
        Then: ValidationError is raised
        """
        User.objects.create(email="test@example.com", first_name="First")

        with pytest.raises(ValidationError):
            user = User(email="test@example.com", first_name="Second")
            user.full_clean()

    def test_user_password_is_hashed(self) -> None:
        """Test user password is hashed on save.

        Given: A plain text password
        When: User is created with set_password()
        Then: Password is stored as a hash, not plain text
        """
        user = User.objects.create(email="test@example.com")
        user.set_password("secret123")
        user.save()

        assert user.password != "secret123"
        assert user.check_password("secret123")
```

**Key Rules for TDD:**

- Test class names: `TestComponentName`
- Test method names: `test_<what>_<condition>_<expected_result>`
- Use type hints for all test methods
- Include docstrings explaining Given/When/Then
- Use pytest assertions (`assert`, not `self.assert*`)
- Mock external dependencies with `pytest.mock` or `unittest.mock`
- Mark slow tests with `@pytest.mark.slow`

### BDD (Behaviour-Driven Development)

**Principles:**

- Write scenarios in Gherkin (Given/When/Then)
- Make tests readable by non-developers
- Focus on behaviour, not implementation

**Feature File Requirements:**

Create feature files in `tests/bdd/features/` using Gherkin syntax:

```gherkin
# tests/bdd/features/authentication.feature

Feature: User Authentication
  As a registered user
  I want to log in to the system
  So that I can access my account

  Background:
    Given the system is running
    And the database is clean

  Scenario: Successful login with valid credentials
    Given a user with email "user@example.com" and password "secret123"
    When I submit login credentials:
      | email            | password  |
      | user@example.com | secret123 |
    Then I should be logged in
    And I should see the dashboard
    And I should see a welcome message "Welcome back, User"

  Scenario: Failed login with invalid password
    Given a user with email "user@example.com" and password "secret123"
    When I submit login credentials:
      | email            | password |
      | user@example.com | wrong    |
    Then I should not be logged in
    And I should see an error message "Invalid credentials"
    And I should remain on the login page

  Scenario Outline: Login validation
    Given a user with email "user@example.com" exists
    When I attempt to login with email "<email>" and password "<password>"
    Then the login result should be "<result>"

    Examples:
      | email             | password  | result  |
      | user@example.com  | secret123 | success |
      | user@example.com  | wrong     | failure |
      | wrong@example.com | secret123 | failure |
      | invalid-email     | secret123 | failure |
```

**Step Definition Requirements:**

Create step definitions in `tests/bdd/step_defs/`:

```python
"""Step definitions for authentication feature.

This module implements step definitions for the authentication.feature file.
"""

import pytest
from pytest_bdd import given, when, then, scenarios, parsers
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

# Load all scenarios from the feature file
scenarios('../features/authentication.feature')


@pytest.fixture
def auth_context():
    """Shared context for authentication tests."""
    return {
        'client': Client(),
        'user': None,
        'response': None,
    }


@given('the system is running')
def system_running():
    """Verify system is operational."""
    # System checks here
    pass


@given('the database is clean')
def database_clean(django_db_setup, django_db_blocker):
    """Ensure database is clean before tests."""
    with django_db_blocker.unblock():
        User.objects.all().delete()


@given(parsers.parse('a user with email "{email}" and password "{password}"'))
def create_user(auth_context, email: str, password: str):
    """Create a test user.

    Args:
        auth_context: Shared test context
        email: User email address
        password: User password
    """
    user = User.objects.create_user(
        email=email,
        password=password,
        first_name="Test",
        last_name="User",
    )
    auth_context['user'] = user


@when('I submit login credentials:')
def submit_login(auth_context, datatable):
    """Submit login form.

    Args:
        auth_context: Shared test context
        datatable: Gherkin datatable with credentials
    """
    credentials = datatable[0]  # First row of data
    response = auth_context['client'].post('/api/auth/login/', {
        'email': credentials['email'],
        'password': credentials['password'],
    })
    auth_context['response'] = response


@then('I should be logged in')
def verify_logged_in(auth_context):
    """Verify user is authenticated.

    Args:
        auth_context: Shared test context
    """
    assert auth_context['response'].status_code == 200
    assert auth_context['client'].session.get('_auth_user_id') is not None


@then(parsers.parse('I should see a welcome message "{message}"'))
def verify_welcome_message(auth_context, message: str):
    """Verify welcome message appears.

    Args:
        auth_context: Shared test context
        message: Expected welcome message
    """
    response_data = auth_context['response'].json()
    assert message in response_data.get('message', '')
```

**BDD Configuration:**

Add to `tests/bdd/conftest.py`:

```python
"""pytest-bdd configuration and fixtures."""

import pytest
from pytest_bdd import given, when, then


@pytest.fixture
def bdd_context():
    """Shared context for BDD tests."""
    return {}
```

Install pytest-bdd dependency in `pyproject.toml`:

```toml
[project.optional-dependencies]
dev = [
    # ... existing dependencies ...
    "pytest-bdd>=7.3.0",  # BDD testing with Gherkin
]
```

### Integration Tests

**Purpose:** Test multiple components working together

```python
"""Integration tests for authentication flow.

Tests the complete authentication workflow including:
- User registration
- Email verification
- Login
- Session management
- Logout
"""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from apps.core.models import Organisation

User = get_user_model()


@pytest.mark.integration
class TestAuthenticationFlow:
    """Integration tests for auth workflow."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Set up test data."""
        self.client = Client()
        self.organisation = Organisation.objects.create(
            name="Test Org",
            slug="test-org",
        )

    def test_complete_registration_and_login_flow(self) -> None:
        """Test user can register, verify email, and login.

        Workflow:
        1. User submits registration form
        2. User receives verification email
        3. User clicks verification link
        4. User logs in
        5. User accesses protected resource
        """
        # Step 1: Register
        response = self.client.post('/api/auth/register/', {
            'email': 'newuser@example.com',
            'password': 'secret123',
            'first_name': 'New',
            'last_name': 'User',
            'organisation': self.organisation.id,
        })
        assert response.status_code == 201

        # Step 2: Verify email token was created
        user = User.objects.get(email='newuser@example.com')
        assert not user.email_verified
        assert user.verification_token is not None

        # Step 3: Verify email
        response = self.client.get(
            f'/api/auth/verify-email/{user.verification_token}/'
        )
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.email_verified

        # Step 4: Login
        response = self.client.post('/api/auth/login/', {
            'email': 'newuser@example.com',
            'password': 'secret123',
        })
        assert response.status_code == 200
        assert 'token' in response.json()

        # Step 5: Access protected resource
        token = response.json()['token']
        response = self.client.get('/api/users/me/', HTTP_AUTHORIZATION=f'Bearer {token}')
        assert response.status_code == 200
        assert response.json()['email'] == 'newuser@example.com'
```

### End-to-End Tests

**Purpose:** Test complete user workflows across the entire system

```python
"""End-to-end tests for organisation setup workflow.

Tests the complete organisation setup process from registration to first content publish.
"""

import pytest
from django.contrib.auth import get_user_model
from apps.core.models import Organisation
from apps.cms.models import Page

User = get_user_model()


@pytest.mark.e2e
class TestOrganisationSetupE2E:
    """E2E tests for organisation setup."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Set up test environment."""
        self.client = Client()

    def test_complete_organisation_setup_workflow(self) -> None:
        """Test complete workflow: register -> create org -> setup -> publish content.

        This test covers:
        1. User registration
        2. Organisation creation
        3. Design token configuration
        4. Template selection
        5. Content creation
        6. Content publishing
        7. Viewing published content
        """
        # Step 1: User registration
        register_response = self.client.post('/api/auth/register/', {
            'email': 'owner@neworg.com',
            'password': 'secret123',
            'first_name': 'Organisation',
            'last_name': 'Owner',
        })
        assert register_response.status_code == 201
        token = register_response.json()['token']

        # Step 2: Create organisation
        org_response = self.client.post(
            '/api/organisations/',
            {
                'name': 'New Organisation',
                'slug': 'new-org',
                'industry': 'technology',
            },
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert org_response.status_code == 201
        org_id = org_response.json()['id']

        # Step 3: Configure design tokens
        design_response = self.client.post(
            f'/api/organisations/{org_id}/design-tokens/',
            {
                'primary_color': '#007bff',
                'secondary_color': '#6c757d',
                'font_family': 'Inter',
            },
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert design_response.status_code == 201

        # Step 4: Select template
        template_response = self.client.post(
            f'/api/organisations/{org_id}/select-template/',
            {'template_type': 'corporate'},
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert template_response.status_code == 200

        # Step 5: Create content
        page_response = self.client.post(
            f'/api/organisations/{org_id}/pages/',
            {
                'title': 'About Us',
                'slug': 'about',
                'content': {
                    'blocks': [
                        {
                            'type': 'heading',
                            'content': 'About Our Company',
                        },
                        {
                            'type': 'paragraph',
                            'content': 'We are a leading provider...',
                        },
                    ],
                },
                'branch': 'feature',
            },
            HTTP_AUTHORIZATION=f'Bearer {token}'
        )
        assert page_response.status_code == 201
        page_id = page_response.json()['id']

        # Step 6: Publish content (feature -> testing -> dev -> staging -> production)
        branches = ['testing', 'dev', 'staging', 'production']
        for branch in branches:
            publish_response = self.client.post(
                f'/api/organisations/{org_id}/pages/{page_id}/promote/',
                {'target_branch': branch},
                HTTP_AUTHORIZATION=f'Bearer {token}'
            )
            assert publish_response.status_code == 200

        # Step 7: View published content
        page = Page.objects.get(id=page_id, branch='production')
        assert page.title == 'About Us'
        assert page.published
```

### GraphQL API Tests

**Purpose:** Test GraphQL queries, mutations, and permissions

```python
"""Tests for GraphQL user queries."""

import pytest
from django.contrib.auth import get_user_model
from apps.core.models import Organisation

User = get_user_model()


@pytest.mark.graphql
class TestUserQueries:
    """Test GraphQL queries for users."""

    @pytest.fixture(autouse=True)
    def setup(self, db):
        """Set up test data."""
        self.org = Organisation.objects.create(name="Test Org", slug="test-org")
        self.user = User.objects.create_user(
            email="test@example.com",
            password="secret123",
            organisation=self.org,
        )

    def test_user_query_returns_user_data(self, graphql_client) -> None:
        """Test user query returns correct data.

        GraphQL Query:
        query {
          user(id: "1") {
            id
            email
            firstName
            lastName
            organisation { name }
          }
        }
        """
        query = """
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                email
                firstName
                lastName
                organisation {
                    name
                }
            }
        }
        """

        response = graphql_client.execute(
            query,
            variables={'id': str(self.user.id)},
        )

        assert response['data']['user']['id'] == str(self.user.id)
        assert response['data']['user']['email'] == "test@example.com"
        assert response['data']['user']['organisation']['name'] == "Test Org"

    def test_user_query_respects_organisation_boundaries(self, graphql_client) -> None:
        """Test users can only query their own organisation's users."""
        other_org = Organisation.objects.create(name="Other Org", slug="other-org")
        other_user = User.objects.create_user(
            email="other@example.com",
            organisation=other_org,
        )

        # Authenticate as self.user
        graphql_client.authenticate(self.user)

        # Try to query other_user
        query = """
        query GetUser($id: ID!) {
            user(id: $id) {
                id
                email
            }
        }
        """

        response = graphql_client.execute(
            query,
            variables={'id': str(other_user.id)},
        )

        # Should return None or error due to organisation boundary
        assert response['data']['user'] is None
```

### Test Markers

Use pytest markers to categorise tests:

```python
# Unit tests (fast, isolated)
@pytest.mark.unit
def test_user_validation():
    pass

# Integration tests (multiple components)
@pytest.mark.integration
def test_auth_flow():
    pass

# E2E tests (complete workflows)
@pytest.mark.e2e
def test_organisation_setup():
    pass

# GraphQL tests
@pytest.mark.graphql
def test_user_query():
    pass

# Slow tests (long-running)
@pytest.mark.slow
def test_bulk_import():
    pass
```

Run specific test categories:

```bash
# Run only unit tests
./scripts/env/test.sh run -m unit

# Run only integration tests
./scripts/env/test.sh run -m integration

# Run only E2E tests
./scripts/env/test.sh run -m e2e

# Run only GraphQL tests
./scripts/env/test.sh run -m graphql

# Exclude slow tests
./scripts/env/test.sh run -m "not slow"
```

### Test Coverage Requirements

| Test Type   | Coverage Target | Purpose                   |
| ----------- | --------------- | ------------------------- |
| Unit        | 90%+            | Core business logic       |
| Integration | 80%+            | Component interactions    |
| E2E         | 60%+            | Critical user workflows   |
| GraphQL     | 85%+            | API queries and mutations |
| Overall     | 80%+            | Entire codebase           |

### Fixtures and Factory Pattern

Use factories for creating test data:

```python
"""Test factories for creating test data."""

import factory
from factory.django import DjangoModelFactory
from apps.core.models import User, Organisation


class OrganisationFactory(DjangoModelFactory):
    """Factory for Organisation model."""

    class Meta:
        model = Organisation

    name = factory.Sequence(lambda n: f"Organisation {n}")
    slug = factory.Sequence(lambda n: f"org-{n}")


class UserFactory(DjangoModelFactory):
    """Factory for User model."""

    class Meta:
        model = User

    email = factory.Sequence(lambda n: f"user{n}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    organisation = factory.SubFactory(OrganisationFactory)

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password after user creation."""
        if not create:
            return
        if extracted:
            self.set_password(extracted)
        else:
            self.set_password('default_password')
```

Usage in tests:

```python
def test_user_creation_with_factory():
    """Test user creation using factory."""
    user = UserFactory.create(email="specific@example.com", password="secret123")
    assert user.email == "specific@example.com"
    assert user.check_password("secret123")
```

### Test-Writer Agent Instructions

When using `/syntek-dev-suite:test-writer`, the agent MUST:

1. **Ask which test type to create:**
   - TDD (unit tests)
   - BDD (feature files + step definitions)
   - Integration tests
   - E2E tests
   - GraphQL tests

2. **Follow the directory structure** specified above

3. **Use appropriate naming conventions** for test files

4. **Include comprehensive docstrings** using Google-style format

5. **Apply correct pytest markers** (@pytest.mark.unit, etc.)

6. **Create factories** for complex test data using factory-boy

7. **Write Given/When/Then** comments in TDD tests

8. **Use Gherkin syntax** for BDD feature files

9. **Test organisation boundaries** for multi-tenancy

10. **Mock external services** (email, API calls, etc.)

11. **Include both positive and negative test cases**

12. **Verify error handling** with pytest.raises()

13. **Check authentication/authorisation** where applicable

14. **Test GraphQL permissions** and filtering

15. **Follow the Arrange-Act-Assert pattern**

### Running Tests Summary

```bash
# Run all tests
./scripts/env/test.sh run

# Run with coverage
./scripts/env/test.sh coverage

# Run specific test types
./scripts/env/test.sh run -m unit
./scripts/env/test.sh run -m integration
./scripts/env/test.sh run -m e2e
./scripts/env/test.sh run -m graphql

# Run specific test file
./scripts/env/test.sh run tests/unit/test_user_model.py

# Run specific test class
./scripts/env/test.sh run tests/unit/test_user_model.py::TestUserModel

# Run specific test method
./scripts/env/test.sh run tests/unit/test_user_model.py::TestUserModel::test_user_creation

# Run fast tests only
./scripts/env/test.sh fast

# Run full CI pipeline
./scripts/env/test.sh ci
```

---

## Markdown Documentation Standards

This project uses comprehensive Markdown standards for all documentation files.

### File Naming Convention

All Markdown files MUST follow this naming pattern:

```
UPPERCASE-NAME.md
```

**Examples:**

- `README.md` - Project readme
- `CLAUDE.md` - Claude configuration
- `CHANGELOG.md` - Version changelog
- `SETUP-GUIDE.md` - Setup instructions
- `API-REFERENCE.md` - API documentation
- `CMS-PLATFORM-PLAN.md` - Architecture plan

**Rules:**

- File name in UPPERCASE with hyphens separating words
- Extension always lowercase `.md`
- No spaces or underscores in file names
- Use descriptive, concise names

### Required VS Code Extension

Install the **Markdown All in One** extension for VS Code:

- Extension ID: `yzhang.markdown-all-in-one`
- Install: `code --install-extension yzhang.markdown-all-in-one`

### Markdown All in One Commands

Use these keyboard shortcuts and commands when editing `.md` files:

| Command                    | Shortcut                                    | Description                       |
| -------------------------- | ------------------------------------------- | --------------------------------- |
| Create/Update TOC          | `Ctrl+Shift+P` → "Create Table of Contents" | Generate linked TOC from headings |
| Update TOC on Save         | Automatic                                   | TOC updates when file is saved    |
| Format Table               | `Alt+Shift+F`                               | Auto-align table columns          |
| Toggle Bold                | `Ctrl+B`                                    | Wrap selection in `**bold**`      |
| Toggle Italic              | `Ctrl+I`                                    | Wrap selection in `*italic*`      |
| Toggle Code                | `Ctrl+`` `                                  | Wrap selection in backticks       |
| Toggle Strikethrough       | `Alt+S`                                     | Wrap selection in `~~strike~~`    |
| Check/Uncheck Task         | `Alt+C`                                     | Toggle `[ ]` ↔ `[x]`              |
| Promote Heading            | `Ctrl+Shift+]`                              | Decrease heading level (## → #)   |
| Demote Heading             | `Ctrl+Shift+[`                              | Increase heading level (# → ##)   |
| Add/Update Section Numbers | Command Palette                             | Number headings automatically     |
| Print to HTML              | Command Palette                             | Export markdown to HTML           |

### Table of Contents Requirements

Every documentation file with more than 3 sections MUST include a Table of Contents:

1. Place TOC after the document header/metadata
2. Use "Markdown All in One: Create Table of Contents" command
3. TOC will auto-update on save when configured

**VS Code Settings for Auto-Update:**

```json
{
  "markdown.extension.toc.updateOnSave": true,
  "markdown.extension.toc.levels": "2..4"
}
```

### Document Structure

All Markdown documentation files should follow this structure:

```markdown
# Document Title

**Last Updated**: DD/MM/YYYY
**Version**: X.Y.Z
**Maintained By**: Team/Person Name

---

## Table of Contents

- [Section 1](#section-1)
- [Section 2](#section-2)

## Section 1

Content...

## Section 2

Content...
```

### Markdown Formatting Rules

- Use **ATX-style headers** (`#`, `##`, `###`) not Setext-style
- Use **fenced code blocks** with language identifiers (` ```python `)
- Use **reference-style links** for repeated URLs
- Use **tables** for structured data (format with `Alt+Shift+F`)
- Use **task lists** for checklists (`- [ ]` and `- [x]`)
- Leave **one blank line** before and after headings, code blocks, and lists
- Use **British English** spelling (colour, organise, behaviour)

### Link Validation

Before committing, validate all internal links:

- Use "Markdown All in One: Check for broken links" if available
- Manually verify relative paths: `[Link](../docs/FILE.md)`
- Ensure anchor links match heading slugs: `[Section](#section-name)`

## Command Execution Requirements

**CRITICAL:** All commands MUST be run inside Docker containers, NOT on the host machine.

### Claude Agent Instructions

**MANDATORY:** When executing any Django or Docker commands, Claude MUST:

1. **ALWAYS use the `scripts/env/*.sh` helper scripts** - Never run `python manage.py` directly
2. **Select the correct environment script** based on the task:
   - `./scripts/env/dev.sh` - For development work
   - `./scripts/env/test.sh` - For running tests
   - `./scripts/env/staging.sh` - For staging operations
   - `./scripts/env/production.sh` - For production (extreme caution)
3. **Never run Docker commands directly** unless the environment script doesn't support the operation
4. **Check script help first** if unsure: `./scripts/env/dev.sh help`

```bash
# ❌ WRONG - Never do this
python manage.py migrate
python manage.py makemigrations
docker compose exec web python manage.py shell

# ✅ CORRECT - Always use environment scripts
./scripts/env/dev.sh migrate
./scripts/env/dev.sh makemigrations
./scripts/env/dev.sh shell
```

### Environment Scripts

Use the environment-specific helper scripts in `scripts/env/` for all operations:

| Script                      | Purpose                 | When to Use                                 |
| --------------------------- | ----------------------- | ------------------------------------------- |
| `scripts/env/dev.sh`        | Development environment | Daily development work, debugging           |
| `scripts/env/test.sh`       | Test environment        | Running tests, CI pipeline, quality checks  |
| `scripts/env/staging.sh`    | Staging environment     | Pre-production testing, staging deployments |
| `scripts/env/production.sh` | Production environment  | Live deployments (use with extreme caution) |

### Script Command Examples

#### Development (`scripts/env/dev.sh`)

```bash
# Start development environment
./scripts/env/dev.sh start

# Create new migrations
./scripts/env/dev.sh makemigrations           # All apps
./scripts/env/dev.sh makemigrations core      # Specific app

# Run Django migrations inside container
./scripts/env/dev.sh migrate

# Open Django shell
./scripts/env/dev.sh shell

# Run tests in dev environment
./scripts/env/dev.sh test

# Format code
./scripts/env/dev.sh format

# View logs
./scripts/env/dev.sh logs [service]

# Database backup
./scripts/env/dev.sh backup

# Full environment reset
./scripts/env/dev.sh reset
```

#### Testing (`scripts/env/test.sh`)

```bash
# Run full test suite
./scripts/env/test.sh run

# Fast tests (no coverage)
./scripts/env/test.sh fast

# Run with coverage report
./scripts/env/test.sh coverage

# Run specific test category
./scripts/env/test.sh unit
./scripts/env/test.sh integration
./scripts/env/test.sh graphql

# Run tests for specific app
./scripts/env/test.sh app users

# Run linting checks
./scripts/env/test.sh lint

# Run type checking
./scripts/env/test.sh typecheck

# Full CI pipeline
./scripts/env/test.sh ci

# Database migrations (test environment)
./scripts/env/test.sh makemigrations
./scripts/env/test.sh migrate
```

#### Staging (`scripts/env/staging.sh`)

```bash
# Deploy to staging
./scripts/env/staging.sh deploy

# Database migrations (requires confirmation)
./scripts/env/staging.sh makemigrations       # Create migrations
./scripts/env/staging.sh migrate              # Apply migrations

# Create database backup
./scripts/env/staging.sh backup

# Health checks
./scripts/env/staging.sh health

# Smoke tests
./scripts/env/staging.sh test
```

#### Production (`scripts/env/production.sh`)

**WARNING:** Production commands require confirmation and should only be used with extreme caution.

```bash
# Deploy to production (requires confirmation)
./scripts/env/production.sh deploy

# Database migrations (requires "PRODUCTION" confirmation)
./scripts/env/production.sh migrate           # Auto-backup before migration
./scripts/env/production.sh makemigrations    # Not recommended in production

# Create production backup
./scripts/env/production.sh backup

# Run health checks
./scripts/env/production.sh health

# Scale web services
./scripts/env/production.sh scale 3

# Enable/disable maintenance mode
./scripts/env/production.sh maintenance-on
./scripts/env/production.sh maintenance-off
```

### Docker Container Access

**All Django management commands must be run through the environment scripts** or directly via Docker Compose:

```bash
# WRONG - Do NOT run on host
python manage.py migrate

# CORRECT - Use environment script
./scripts/env/dev.sh migrate

# CORRECT - Use Docker Compose directly
docker compose -f docker/dev/docker-compose.yml exec web python manage.py migrate
```

### Quick Reference

| Task                    | Command                               |
| ----------------------- | ------------------------------------- |
| Start development       | `./scripts/env/dev.sh start`          |
| Run all tests           | `./scripts/env/test.sh run`           |
| Run tests with coverage | `./scripts/env/test.sh coverage`      |
| Run linters             | `./scripts/env/test.sh lint`          |
| Format code             | `./scripts/env/dev.sh format`         |
| Run migrations          | `./scripts/env/dev.sh migrate`        |
| Create migrations       | `./scripts/env/dev.sh makemigrations` |
| Open Django shell       | `./scripts/env/dev.sh shell`          |
| View logs               | `./scripts/env/dev.sh logs`           |
| Database backup         | `./scripts/env/dev.sh backup`         |
| Health check            | `./scripts/env/dev.sh health`         |
| Environment URLs        | `./scripts/env/dev.sh urls`           |

## Syntek Dev Suite Agents

When an agent from `syntek-marketplace` within `syntek-dev-suite` calls a plugin, remember
plugins are located in `.claude/plugins/*.py`.

### Versioning Requirements

When updating version numbers, the following files MUST be updated:

| File                 | Update Required                      |
| -------------------- | ------------------------------------ |
| `VERSION`            | Semantic version number              |
| `CHANGELOG.md`       | Release notes and changes            |
| `SECURITY.md`        | Supported versions table (root file) |
| `VERSION-HISTORY.md` | Version history documentation        |
| `RELEASES.md`        | Release documentation                |
| `.claude/CLAUDE.md`  | Version in header metadata           |
| `pyproject.toml`     | Package version                      |
| `package.json`       | Package version                      |

**CRITICAL:** Always update `SECURITY.md` in the project root when releasing new versions to keep
the "Supported Versions" table accurate. This ensures users know which versions receive security
updates.

## Project Management

- **Tool:** ClickUp
- **Workspace:** Syntek
- **Space:** Syntek
- **Sprints Folder:** Sprint - Backend Template
- **Backlog Folder:** Backlog - Backend Template
- **Sync:** Enabled via GitHub Actions
- **Branch Pattern:** us{number}/feature-name
- **Documentation:** docs/PM-INTEGRATION/

**Environment Variables:**
All ClickUp IDs are configured via environment variables. See `.env.*.example` files for required variables:

- `CLICKUP_API_TOKEN` - Your ClickUp API token from Settings > Apps
- `CLICKUP_WORKSPACE_ID` - ClickUp workspace ID
- `CLICKUP_SPACE_ID` - ClickUp space ID
- `CLICKUP_SPRINT_FOLDER_ID` - Sprint folder ID
- `CLICKUP_BACKLOG_FOLDER_ID` - Backlog folder ID
- `CLICKUP_BACKLOG_LIST_ID` - Backlog list ID

## Platform Architecture

This backend is part of a comprehensive CMS platform architecture. For complete details:

**See:** [docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md](../docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md)

### Key Platform Features

- **Multi-Repository Architecture:** Backend, UI library, Web frontend, Mobile app
- **Multi-Tenancy:** Organisation-based isolation with encrypted data
- **Design Token System:** Database-driven theming for consistent branding
- **Content Branching:** Git-like workflow (feature → testing → dev → staging → production)
- **9 Site Templates:** E-commerce, Blog, Corporate, Church, Charity, SaaS, Sole Trader,
  Estate Agent, Single Page
- **SaaS Integrations:** Email service, Cloud documents (OnlyOffice), Password manager
  (Vaultwarden)
- **AI Integration:** Anthropic Claude across all systems (content, SEO, code assistance)
- **Environment Variable Management:** Encrypted secrets with versioning and audit logs
- **Initial Setup Wizard:** Guided deployment and configuration
- **Platform Upgrade System:** Managed updates through testing → dev → staging → production

### Development Phases

The platform is being built in 16 phases. Current status:

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

## Notes

- PostgreSQL on AWS RDS or Digital Ocean for staging/production
- Redis/Valkey for caching and session storage
- Mailpit simulates email in dev/test environments
- Each environment has isolated containers
- ClickUp integration syncs tasks with Git workflow automatically
- **Architecture:** Refer to [CMS-PLATFORM-PLAN.md](../docs/ARCHITECTURE/CMS-PLATFORM-PLAN.md)
  for the complete system design

## Overview
