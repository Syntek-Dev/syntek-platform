# Testing Commands

## Backend Tests (Django + GraphQL)

```bash
# Run all backend tests
cd backend
python manage.py test

# Run specific app tests
python manage.py test apps.cms.tests

# Run GraphQL schema tests
python manage.py test apps.api.tests.test_schema

# Test with coverage
coverage run --source='.' manage.py test
coverage report
coverage html
```

## Security Layer Tests (Rust)

```bash
# Run all Rust tests
cd security
cargo test

# Run with output
cargo test -- --nocapture

# Test specific module
cargo test auth::tests

# Integration tests
cargo test --test integration
```

## Frontend Tests (React + Jest)

```bash
# Run all frontend tests
cd frontend
npm test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test PageBuilder.test.tsx
```

## End-to-End Tests

```bash
# Start test environment
docker-compose -f docker/docker-compose.test.yml up -d

# Run Cypress tests
cd frontend
npm run test:e2e

# Run specific test
npm run test:e2e -- --spec "cypress/integration/page-builder.spec.ts"
```

## GraphQL Testing

```bash
# Test GraphQL schema
cd backend
python manage.py test apps.api.tests.test_schema

# Test GraphQL mutations
python manage.py test apps.api.tests.test_mutations

# Test GraphQL subscriptions
python manage.py test apps.api.tests.test_subscriptions
```

## Security Testing

```bash
# Run security audit on Rust code
cd security
cargo audit

# Run frontend security audit
cd frontend
npm audit

# Run backend security checks
cd backend
bandit -r apps/
safety check
```