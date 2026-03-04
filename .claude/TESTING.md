# Testing Guide - Syntek CMS Platform

## Overview

Comprehensive testing strategy for the full-stack Syntek CMS platform covering Django + Strawberry GraphQL backend, React + Next.js frontend, and Rust security layer.

## Testing Philosophy

### Test Pyramid Structure
```
                    E2E Tests
                   (Cypress/Playwright)
                  /               \
            Integration Tests    API Tests
           (Django + GraphQL)  (Strawberry)
          /                              \
    Unit Tests                     Component Tests
   (Python/Rust)                    (React/Jest)
```

### Testing Principles
- **Test Behavior, Not Implementation**: Focus on what the system does, not how it does it
- **Test-Driven Development (TDD)**: Write tests before implementation
- **Fast Feedback**: Unit tests should run in milliseconds
- **Realistic Data**: Use meaningful test data that resembles production
- **Isolated Tests**: Each test should be independent and repeatable

## Backend Testing (Django + Strawberry GraphQL)

### Unit Testing

#### Django Models
```python
# backend/apps/cms/tests/test_models.py
from django.test import TestCase
from apps.cms.models import Page, Template, Organization

class PageModelTest(TestCase):
    def setUp(self):
        self.organization = Organization.objects.create(
            name="Test Organization",
            slug="test-org"
        )
        self.template = Template.objects.create(
            name="Basic Template",
            organization=self.organization
        )

    def test_page_creation(self):
        page = Page.objects.create(
            title="Test Page",
            content={"blocks": []},
            template=self.template,
            organization=self.organization
        )
        self.assertEqual(page.title, "Test Page")
        self.assertEqual(page.organization, self.organization)
```

#### GraphQL Schema Testing
```python
# backend/apps/api/tests/test_schema.py
import pytest
from strawberry.test import BaseGraphQLTestClient
from apps.api.schema import schema

class TestPageSchema:
    def test_page_query(self):
        client = BaseGraphQLTestClient(schema)
        query = """
            query GetPages {
                pages {
                    id
                    title
                    template {
                        name
                    }
                }
            }
        """
        result = client.query(query)
        assert result.errors is None
        assert "pages" in result.data

    def test_create_page_mutation(self):
        client = BaseGraphQLTestClient(schema)
        mutation = """
            mutation CreatePage($input: CreatePageInput!) {
                createPage(input: $input) {
                    page {
                        id
                        title
                    }
                    errors {
                        message
                    }
                }
            }
        """
        variables = {
            "input": {
                "title": "New Test Page",
                "templateId": "1",
                "content": {"blocks": []}
            }
        }
        result = client.query(mutation, variables)
        assert result.errors is None
        assert result.data["createPage"]["page"]["title"] == "New Test Page"
```

### Integration Testing

#### Database Integration
```python
# backend/apps/cms/tests/test_integration.py
from django.test import TransactionTestCase
from django.db import transaction
from apps.cms.models import Page, Template

class PageIntegrationTest(TransactionTestCase):
    def test_concurrent_page_updates(self):
        """Test handling of concurrent page updates"""
        page = Page.objects.create(
            title="Concurrent Test Page",
            content={"blocks": []}
        )

        # Simulate concurrent updates
        with transaction.atomic():
            page_1 = Page.objects.select_for_update().get(id=page.id)
            page_1.title = "Update 1"
            page_1.save()

            # This should handle the conflict appropriately
            page_2 = Page.objects.get(id=page.id)
            page_2.title = "Update 2"
            page_2.save()
```

### API Testing Commands

```bash
# Run all backend tests
python backend/manage.py test

# Run specific test modules
python backend/manage.py test apps.cms.tests.test_models
python backend/manage.py test apps.api.tests.test_schema

# Run tests with coverage
coverage run --source='.' backend/manage.py test
coverage report --show-missing
coverage html  # Generates htmlcov/index.html

# Run tests in parallel
python backend/manage.py test --parallel

# Run specific test with verbose output
python backend/manage.py test apps.cms.tests.test_models.PageModelTest.test_page_creation -v 2
```

## Security Layer Testing (Rust)

### Unit Testing

#### Authentication Tests
```rust
// security/src/auth/tests.rs
#[cfg(test)]
mod tests {
    use super::*;
    use crate::auth::{validate_token, generate_token, Claims};

    #[test]
    fn test_token_generation_and_validation() {
        let user_id = "123".to_string();
        let token = generate_token(&user_id).unwrap();
        let claims = validate_token(&token).unwrap();
        assert_eq!(claims.sub, user_id);
    }

    #[test]
    fn test_invalid_token_rejection() {
        let invalid_token = "invalid.token.here";
        let result = validate_token(invalid_token);
        assert!(result.is_err());
    }

    #[test]
    fn test_expired_token_rejection() {
        // Test with expired token
        let expired_token = create_expired_token();
        let result = validate_token(&expired_token);
        assert!(matches!(result, Err(AuthError::TokenExpired)));
    }
}
```

#### Authorization Tests
```rust
// security/src/auth/tests/authorization.rs
#[test]
fn test_role_based_access_control() {
    let admin_claims = Claims {
        sub: "admin-user".to_string(),
        roles: vec!["admin".to_string()],
        permissions: vec!["page.create", "page.delete"].iter().map(|s| s.to_string()).collect(),
        exp: chrono::Utc::now().timestamp() + 3600,
    };

    assert!(can_access_resource(&admin_claims, "page.delete"));

    let user_claims = Claims {
        sub: "regular-user".to_string(),
        roles: vec!["user".to_string()],
        permissions: vec!["page.read"].iter().map(|s| s.to_string()).collect(),
        exp: chrono::Utc::now().timestamp() + 3600,
    };

    assert!(!can_access_resource(&user_claims, "page.delete"));
    assert!(can_access_resource(&user_claims, "page.read"));
}
```

### Integration Testing
```rust
// security/tests/integration_test.rs
use reqwest;
use serde_json::json;

#[tokio::test]
async fn test_authentication_flow() {
    let client = reqwest::Client::new();

    // Test login
    let login_response = client
        .post("http://localhost:3001/auth/login")
        .json(&json!({
            "email": "test@example.com",
            "password": "testpassword"
        }))
        .send()
        .await
        .unwrap();

    assert_eq!(login_response.status(), 200);

    let auth_data: AuthResponse = login_response.json().await.unwrap();
    let token = auth_data.token;

    // Test protected endpoint
    let protected_response = client
        .get("http://localhost:3001/auth/validate")
        .header("Authorization", format!("Bearer {}", token))
        .send()
        .await
        .unwrap();

    assert_eq!(protected_response.status(), 200);
}
```

### Security Testing Commands

```bash
# Run all Rust tests
cd security
cargo test

# Run tests with output
cargo test -- --nocapture

# Run specific test module
cargo test auth::tests

# Run integration tests
cargo test --test integration_test

# Security audit
cargo audit

# Benchmark tests
cargo bench

# Test with code coverage
cargo tarpaulin --out Html
```

## Frontend Testing (React + Next.js)

### Component Testing

#### React Component Tests
```typescript
// frontend/components/__tests__/PageBuilder.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import PageBuilder from '../PageBuilder';
import { GET_PAGE_QUERY, UPDATE_PAGE_MUTATION } from '../../graphql/queries';

const mockPage = {
  id: '1',
  title: 'Test Page',
  content: { blocks: [] },
  template: { id: '1', name: 'Basic Template' }
};

const mocks = [
  {
    request: {
      query: GET_PAGE_QUERY,
      variables: { id: '1' }
    },
    result: {
      data: { page: mockPage }
    }
  }
];

describe('PageBuilder', () => {
  test('renders page title', async () => {
    render(
      <MockedProvider mocks={mocks} addTypename={false}>
        <PageBuilder pageId="1" />
      </MockedProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Test Page')).toBeInTheDocument();
    });
  });

  test('handles page updates', async () => {
    const updateMocks = [
      ...mocks,
      {
        request: {
          query: UPDATE_PAGE_MUTATION,
          variables: {
            id: '1',
            input: { title: 'Updated Title' }
          }
        },
        result: {
          data: {
            updatePage: {
              page: { ...mockPage, title: 'Updated Title' }
            }
          }
        }
      }
    ];

    render(
      <MockedProvider mocks={updateMocks} addTypename={false}>
        <PageBuilder pageId="1" />
      </MockedProvider>
    );

    await waitFor(() => {
      const titleInput = screen.getByDisplayValue('Test Page');
      fireEvent.change(titleInput, { target: { value: 'Updated Title' } });
      fireEvent.click(screen.getByText('Save'));
    });

    await waitFor(() => {
      expect(screen.getByDisplayValue('Updated Title')).toBeInTheDocument();
    });
  });
});
```

#### GraphQL Hook Testing
```typescript
// frontend/hooks/__tests__/usePageData.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { MockedProvider } from '@apollo/client/testing';
import { usePageData } from '../usePageData';
import { GET_PAGE_QUERY } from '../../graphql/queries';

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <MockedProvider mocks={mocks} addTypename={false}>
    {children}
  </MockedProvider>
);

describe('usePageData', () => {
  test('fetches page data successfully', async () => {
    const { result } = renderHook(() => usePageData('1'), { wrapper });

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
      expect(result.current.data).toBeDefined();
      expect(result.current.data?.page.title).toBe('Test Page');
    });
  });
});
```

### End-to-End Testing

#### Cypress Tests
```typescript
// frontend/cypress/integration/page-builder.spec.ts
describe('Page Builder', () => {
  beforeEach(() => {
    cy.login('admin@example.com', 'password');
    cy.visit('/pages/1/edit');
  });

  it('should allow editing page content', () => {
    // Wait for page to load
    cy.get('[data-testid="page-title"]').should('contain', 'Test Page');

    // Edit page title
    cy.get('[data-testid="page-title-input"]')
      .clear()
      .type('Updated Page Title');

    // Add a text block
    cy.get('[data-testid="add-block-button"]').click();
    cy.get('[data-testid="text-block-option"]').click();
    cy.get('[data-testid="text-block-content"]')
      .type('This is test content');

    // Save the page
    cy.get('[data-testid="save-button"]').click();

    // Verify changes are saved
    cy.get('[data-testid="success-message"]')
      .should('contain', 'Page saved successfully');

    // Verify data persistence
    cy.reload();
    cy.get('[data-testid="page-title"]')
      .should('contain', 'Updated Page Title');
    cy.get('[data-testid="text-block-content"]')
      .should('contain', 'This is test content');
  });

  it('should handle collaborative editing', () => {
    // Open page in two browser contexts
    cy.window().then((win) => {
      win.open('/pages/1/edit', '_blank');
    });

    // Make changes in first window
    cy.get('[data-testid="page-title-input"]')
      .clear()
      .type('Collaborative Edit');

    // Verify real-time updates in second window
    cy.window().its('length').should('be.gt', 1);
    // Test real-time sync functionality
  });
});
```

### Frontend Testing Commands

```bash
# Unit and component tests
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test -- PageBuilder.test.tsx

# End-to-end tests
npm run test:e2e

# Run e2e tests in headed mode
npm run test:e2e:headed

# Run specific e2e test
npm run test:e2e -- --spec "cypress/integration/page-builder.spec.ts"

# Visual regression testing
npm run test:visual

# Accessibility testing
npm run test:a11y
```

## GraphQL API Testing

### Schema Validation
```bash
# Validate GraphQL schema
python backend/manage.py graphql_schema --check

# Export schema for frontend
python backend/manage.py export_schema > schema.graphql

# Generate TypeScript types
cd frontend
npm run graphql:generate
```

### Performance Testing
```python
# backend/apps/api/tests/test_performance.py
import time
from django.test import TestCase
from strawberry.test import BaseGraphQLTestClient
from apps.api.schema import schema

class GraphQLPerformanceTest(TestCase):
    def test_query_performance(self):
        client = BaseGraphQLTestClient(schema)

        # Complex query that might cause N+1 problems
        query = """
            query GetPagesWithTemplates {
                pages {
                    id
                    title
                    template {
                        id
                        name
                        components {
                            id
                            name
                        }
                    }
                    author {
                        id
                        name
                        organization {
                            id
                            name
                        }
                    }
                }
            }
        """

        start_time = time.time()
        result = client.query(query)
        end_time = time.time()

        # Assert query completes within reasonable time
        self.assertLess(end_time - start_time, 1.0)  # Should complete within 1 second
        self.assertIsNone(result.errors)
```

## Load Testing

### Backend Load Testing
```python
# backend/tests/load/locustfile.py
from locust import HttpUser, task, between

class CMSUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login and get authentication token"""
        response = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        self.token = response.json()["token"]
        self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    @task(3)
    def get_pages(self):
        """Test page listing performance"""
        self.client.post("/graphql", json={
            "query": "query { pages { id title } }"
        })

    @task(1)
    def create_page(self):
        """Test page creation performance"""
        self.client.post("/graphql", json={
            "query": """
                mutation CreatePage($input: CreatePageInput!) {
                    createPage(input: $input) {
                        page { id title }
                    }
                }
            """,
            "variables": {
                "input": {
                    "title": "Load Test Page",
                    "content": {"blocks": []}
                }
            }
        })
```

### Load Testing Commands
```bash
# Backend load testing
cd backend
locust -f tests/load/locustfile.py --host=http://localhost:8000

# Frontend load testing
cd frontend
npm run test:load

# Security layer load testing
cd security
cargo run --bin load_test
```

## Continuous Integration Testing

### GitHub Actions / Forgejo Actions
```yaml
# .forgejo/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:18.3
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: syntek_cms_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.14.3
        uses: actions/setup-python@v4
        with:
          python-version: 3.14.3

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements/test.txt

      - name: Run migrations
        run: |
          cd backend
          python manage.py migrate

      - name: Run tests
        run: |
          cd backend
          coverage run --source='.' manage.py test
          coverage xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3

  security-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Rust
        uses: actions-rs/toolchain@v1
        with:
          toolchain: stable

      - name: Run tests
        run: |
          cd security
          cargo test

      - name: Security audit
        run: |
          cd security
          cargo audit

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '24.14.0'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run tests
        run: |
          cd frontend
          npm run test:coverage

      - name: Run e2e tests
        run: |
          cd frontend
          npm run test:e2e:ci
```

## Testing Best Practices

### General Principles
1. **Write tests first (TDD)**: Tests define the expected behavior
2. **Keep tests simple**: One assertion per test when possible
3. **Use descriptive names**: Test names should explain what is being tested
4. **Test edge cases**: Test with empty data, large data, invalid data
5. **Clean up after tests**: Use proper tearDown/cleanup methods

### GraphQL Testing
- Test both successful queries and error cases
- Verify proper authentication and authorization
- Test query performance and N+1 prevention
- Validate schema changes don't break existing clients

### Security Testing
- Test all authentication flows
- Verify authorization at different permission levels
- Test against common security vulnerabilities (OWASP Top 10)
- Test token expiration and refresh flows

### Frontend Testing
- Test component behavior, not implementation details
- Use realistic data in tests
- Test accessibility compliance
- Test responsive design across different screen sizes

## Test Data Management

### Fixtures and Factories
```python
# backend/apps/cms/tests/factories.py
import factory
from apps.cms.models import Organization, Template, Page

class OrganizationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organization

    name = factory.Sequence(lambda n: f"Organization {n}")
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '-'))

class TemplateFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Template

    name = factory.Sequence(lambda n: f"Template {n}")
    organization = factory.SubFactory(OrganizationFactory)

class PageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Page

    title = factory.Sequence(lambda n: f"Page {n}")
    content = {"blocks": []}
    template = factory.SubFactory(TemplateFactory)
    organization = factory.SubFactory(OrganizationFactory)
```

---

**Use Syntek Dev Suite agents for test generation:**
- `/syntek-dev-suite:test-writer` - Generate comprehensive test suites
- `/syntek-dev-suite:qa-tester` - Find bugs and edge cases
- `/syntek-dev-suite:review` - Review test quality and coverage