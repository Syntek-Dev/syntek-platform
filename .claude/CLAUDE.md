# Backend Template - Django Project

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

> **Stack:** Django + Wagtail + PostgreSQL + GraphQL
> **Container:** Docker Compose
> **Package:** backend-template
> **Last Updated:** 2026-01-03

## Table of Contents

- [Backend Template - Django Project](#backend-template---django-project)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
    - [Architecture](#architecture)
  - [Project Structure](#project-structure)
  - [Development Workflow](#development-workflow)
    - [Starting Development](#starting-development)
    - [Running Tests](#running-tests)
  - [Environment Configuration](#environment-configuration)
  - [Key Conventions](#key-conventions)
    - [Django Apps](#django-apps)
    - [GraphQL API](#graphql-api)
    - [Wagtail CMS](#wagtail-cms)
  - [Documentation Standards](#documentation-standards)
    - [Docstring Requirements](#docstring-requirements)
    - [Google-Style Docstring Format](#google-style-docstring-format)
    - [Type Hints](#type-hints)
    - [Django Models](#django-models)
    - [Django Views](#django-views)
    - [Django Serializers](#django-serializers)
    - [GraphQL Resolvers](#graphql-resolvers)
    - [Wagtail Page Models](#wagtail-page-models)
    - [Wagtail Snippets](#wagtail-snippets)
    - [Comments: When to Use Them](#comments-when-to-use-them)
    - [Module-Level Docstrings](#module-level-docstrings)
    - [Examples of What NOT to Document](#examples-of-what-not-to-document)
  - [Markdown Documentation Standards](#markdown-documentation-standards)
  - [Command Execution Requirements](#command-execution-requirements)
    - [Environment Scripts](#environment-scripts)
    - [Script Command Examples](#script-command-examples)
      - [Development (`scripts/env/dev.sh`)](#development-scriptsenvdevsh)
      - [Testing (`scripts/env/test.sh`)](#testing-scriptsenvtestsh)
      - [Staging (`scripts/env/staging.sh`)](#staging-scriptsenvstagingsh)
      - [Production (`scripts/env/production.sh`)](#production-scriptsenvproductionsh)
    - [Docker Container Access](#docker-container-access)
    - [Quick Reference](#quick-reference)
  - [Syntek Dev Suite Agents](#syntek-dev-suite-agents)
  - [Project Management](#project-management)
  - [Notes](#notes)

## Project Overview

This is a reusable backend template using Django, Wagtail, PostgreSQL, and GraphQL with environment-specific setups (dev, staging, prod, test). Each environment has dedicated Docker containers to prevent interference.

### Architecture

- **Framework:** Django with Wagtail CMS
- **Database:** PostgreSQL (containerised for dev/test, managed for staging/prod)
- **API:** GraphQL
- **Cache:** Redis or Valkey
- **Email:** Mailpit (dev/test simulation)
- **Containers:** Docker Compose per environment

## Project Structure

```
backend-template/
├── .claude/                 # Claude configuration
│   ├── CLAUDE.md           # This file
│   ├── SYNTEK-GUIDE.md     # Plugin usage guide
│   ├── settings.local.json # Local settings
│   └── commands/           # Custom commands
├── config/                  # Django settings
│   ├── settings/
│   │   ├── base.py
│   │   ├── dev.py
│   │   ├── test.py
│   │   ├── staging.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/                    # Django applications
├── api/                     # GraphQL API
├── docker/                  # Docker configurations
│   ├── dev/
│   ├── test/
│   ├── staging/
│   └── production/
├── docs/                    # Documentation
│   └── METRICS/            # Self-learning metrics
├── manage.py
├── requirements/
│   ├── base.txt
│   ├── dev.txt
│   ├── test.txt
│   └── production.txt
└── docker-compose.yml
```

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

| Environment | Database | Cache | Email |
|-------------|----------|-------|-------|
| dev | PostgreSQL (container) | Redis (container) | Mailpit |
| test | PostgreSQL (container) | Redis (container) | Mailpit |
| staging | PostgreSQL (AWS/DO) | Redis (managed) | SMTP |
| production | PostgreSQL (AWS/DO) | Redis (managed) | SMTP |

## Key Conventions

### Django Apps

- Each app should be self-contained in `apps/`
- Use `apps.app_name` for imports
- Models should include `created_at` and `updated_at` fields

### GraphQL API

- Schema defined in `api/schema.py`
- Use Strawberry or Graphene for GraphQL
- Mutations should return the modified object

### Wagtail CMS

- Page models in respective apps
- Snippets for reusable content blocks
- Images and documents in Wagtail media

## Documentation Standards

This project uses **Google-style docstrings** for all Python code. Documentation is essential for code maintainability and team collaboration.

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
- Magic methods (__str__, __repr__) if behaviour is obvious

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

### Wagtail Page Models

Wagtail page models should document their purpose, fields, and admin customisations:

```python
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, PublishingPanel
from django.db import models


class BlogPage(Page):
    """A page model for publishing blog articles with rich text content.

    This page type supports featured images, rich text body content, and
    automatic publication date tracking. BlogPage instances appear in
    the Wagtail admin with simplified content editing interface.

    Attributes:
        intro: Brief introduction or summary of the blog post.
        body: The main article content using Wagtail's rich text editor.
        featured_image: Optional image to display at the top of the article.
        publication_date: Automatically set when the page is first published.

    Admin Features:
        - Simple tab organisation with Content and Publishing tabs.
        - Rich text editing for article body.
        - Image selection panel for featured images.
    """

    intro = models.CharField(max_length=250, help_text="Brief introduction")
    body = RichTextField(help_text="Main article content")
    featured_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    publication_date = models.DateTimeField(auto_now_add=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("body"),
        FieldPanel("featured_image"),
    ]

    promote_panels = Page.promote_panels + [
        PublishingPanel(),
    ]

    def get_reading_time(self) -> int:
        """Calculate estimated reading time in minutes.

        Estimates based on average reading speed of 200 words per minute.
        Counts words in both title and body.

        Returns:
            Estimated reading time in minutes (minimum 1 minute).
        """
        word_count = len(self.title.split()) + len(self.body.split())
        reading_time = max(1, word_count // 200)
        return reading_time
```

### Wagtail Snippets

Snippet models should be documented with their purpose and usage:

```python
from wagtail.snippets.models import register_snippet
from django.db import models


@register_snippet
class SocialMediaLink(models.Model):
    """A reusable snippet representing a social media platform link.

    This snippet allows content editors to define social media links once
    and reuse them across multiple pages and content blocks. Commonly used
    in footer sections and author profiles.

    Attributes:
        platform: The name of the social media platform (Twitter, LinkedIn, etc.).
        url: The full URL to the social media profile or page.

    Admin Behaviour:
        Listed in Wagtail's snippet interface with filtering by platform.
    """

    PLATFORM_CHOICES = [
        ("twitter", "Twitter/X"),
        ("linkedin", "LinkedIn"),
        ("github", "GitHub"),
        ("instagram", "Instagram"),
    ]

    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    url = models.URLField(help_text="Full URL to the social media profile")

    class Meta:
        ordering = ["platform"]
        unique_together = [["platform"]]

    def __str__(self) -> str:
        """Return the platform name."""
        return self.get_platform_display()
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

## Markdown Documentation Standards

When writing or editing Markdown files (.md):
- Use **Markdown All in One** VS Code extension features
- Generate proper Table of Contents with links
- Use auto-formatting for consistent structure
- Follow standard Markdown conventions (headings, lists, code blocks)
- Ensure all internal links are valid and properly formatted

## Command Execution Requirements

**CRITICAL:** All commands MUST be run inside Docker containers, NOT on the host machine.

### Environment Scripts

Use the environment-specific helper scripts in `scripts/env/` for all operations:

| Script | Purpose | When to Use |
|--------|---------|-------------|
| `scripts/env/dev.sh` | Development environment | Daily development work, debugging |
| `scripts/env/test.sh` | Test environment | Running tests, CI pipeline, quality checks |
| `scripts/env/staging.sh` | Staging environment | Pre-production testing, staging deployments |
| `scripts/env/production.sh` | Production environment | Live deployments (use with extreme caution) |

### Script Command Examples

#### Development (`scripts/env/dev.sh`)

```bash
# Start development environment
./scripts/env/dev.sh start

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
```

#### Staging (`scripts/env/staging.sh`)

```bash
# Deploy to staging
./scripts/env/staging.sh deploy

# Run migrations
./scripts/env/staging.sh migrate

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

| Task | Command |
|------|---------|
| Start development | `./scripts/env/dev.sh start` |
| Run all tests | `./scripts/env/test.sh run` |
| Run tests with coverage | `./scripts/env/test.sh coverage` |
| Run linters | `./scripts/env/test.sh lint` |
| Format code | `./scripts/env/dev.sh format` |
| Run migrations | `./scripts/env/dev.sh migrate` |
| Create migrations | `./scripts/env/dev.sh makemigrations` |
| Open Django shell | `./scripts/env/dev.sh shell` |
| View logs | `./scripts/env/dev.sh logs` |
| Database backup | `./scripts/env/dev.sh backup` |
| Health check | `./scripts/env/dev.sh health` |
| Environment URLs | `./scripts/env/dev.sh urls` |

## Syntek Dev Suite Agents

Use these agents for development tasks:

| Agent | Purpose |
|-------|---------|
| `/syntek-dev-suite:backend` | API and database work |
| `/syntek-dev-suite:database` | Database optimisation |
| `/syntek-dev-suite:test-writer` | Generate tests |
| `/syntek-dev-suite:security` | Security hardening |
| `/syntek-dev-suite:docs` | Documentation |

## Project Management

- **Tool:** ClickUp
- **Workspace:** Syntek (ID: 90156744333)
- **Team ID:** 90151635198
- **Sprints Folder:** Sprint - Backend Template (ID: 901512938483)
- **Backlog Folder:** Backlog - Backend Template (ID: 901512938469)
- **Sync:** Enabled via GitHub Actions
- **Branch Pattern:** us{number}/feature-name
- **Documentation:** docs/PM-INTEGRATION/

## Notes

- PostgreSQL on AWS RDS or Digital Ocean for staging/production
- Redis/Valkey for caching and session storage
- Mailpit simulates email in dev/test environments
- Each environment has isolated containers
- ClickUp integration syncs tasks with Git workflow automatically
