# Production Commands

## Deploy to Production

```bash
# Build and push production image
docker build -f docker/production/Dockerfile -t backend-template:latest .
docker push registry.example.com/backend-template:latest

# Deploy (update as per your CI/CD)
./scripts/deploy-production.sh
```

## Run Migrations on Production

```bash
# Use CI/CD pipeline for production migrations
# Manual migrations should be avoided in production
docker compose -f docker/production/docker-compose.yml exec web python manage.py migrate --plan
docker compose -f docker/production/docker-compose.yml exec web python manage.py migrate
```

## View Production Logs

```bash
# Use your logging service (CloudWatch, Datadog, etc.)
# Or access container logs
docker compose -f docker/production/docker-compose.yml logs -f web
```

## Production Environment Variables

Required in production:

- `DJANGO_SETTINGS_MODULE=config.settings.production`
- `DATABASE_URL` - PostgreSQL connection string (AWS RDS or DO)
- `REDIS_URL` - Redis/Valkey connection string
- `SECRET_KEY` - Strong secret key
- `ALLOWED_HOSTS` - Production domain(s)
- `EMAIL_*` - Production SMTP configuration
- `SENTRY_DSN` - Error tracking
- `AWS_*` or `DO_*` - Cloud provider credentials

## Health Check

```bash
curl -I https://example.com/health/
```

## Rollback

```bash
# Deploy previous image version
docker pull registry.example.com/backend-template:previous-tag
./scripts/deploy-production.sh previous-tag
```
