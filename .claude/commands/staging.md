# Staging Environment Commands

## Build and Deploy

```bash
# Build production images
docker-compose -f docker/docker-compose.staging.yml build

# Deploy to staging
docker-compose -f docker/docker-compose.staging.yml up -d

# Check deployment status
docker-compose -f docker/docker-compose.staging.yml ps
```

## Database Operations

```bash
# Run migrations on staging
docker-compose -f docker/docker-compose.staging.yml exec backend python manage.py migrate

# Load fixtures for testing
docker-compose -f docker/docker-compose.staging.yml exec backend python manage.py loaddata fixtures/staging_data.json

# Create staging superuser
docker-compose -f docker/docker-compose.staging.yml exec backend python manage.py createsuperuser
```

## Monitoring

```bash
# View application logs
docker-compose -f docker/docker-compose.staging.yml logs -f backend
docker-compose -f docker/docker-compose.staging.yml logs -f frontend
docker-compose -f docker/docker-compose.staging.yml logs -f security

# Monitor resource usage
docker stats

# Check GraphQL endpoint
curl -X POST https://staging.syntek-cms.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "query { __schema { types { name } } }"}'
```

## Testing on Staging

```bash
# Run smoke tests against staging
cd frontend
npm run test:staging

# Test authentication flow
cd security
cargo test --test staging_auth -- --ignored

# Load test the API
cd backend
locust -f tests/load/staging_load_test.py --host=https://staging-api.syntek-cms.com
```

## Configuration

```bash
# View current configuration
docker-compose -f docker/docker-compose.staging.yml config

# Update environment variables
# Edit docker/staging.env

# Restart specific services
docker-compose -f docker/docker-compose.staging.yml restart backend
```

## Backup and Restore

```bash
# Create database backup
docker-compose -f docker/docker-compose.staging.yml exec postgres pg_dump -U postgres syntek_cms > staging_backup.sql

# Restore from backup
docker-compose -f docker/docker-compose.staging.yml exec postgres psql -U postgres syntek_cms < staging_backup.sql

# Backup uploaded files
docker-compose -f docker/docker-compose.staging.yml exec backend tar -czf /tmp/media_backup.tar.gz media/
```