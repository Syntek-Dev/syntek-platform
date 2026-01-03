# Staging Commands

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Deploy to Staging

```bash
# Build and push staging image
docker build -f docker/staging/Dockerfile -t backend-template:staging .
docker push registry.example.com/backend-template:staging

# Deploy (update as per your CI/CD)
./scripts/deploy-staging.sh
```

## Run Migrations on Staging

```bash
# SSH into staging server or use CI/CD
docker compose -f docker/staging/docker-compose.yml exec web python manage.py migrate
```

## View Staging Logs

```bash
docker compose -f docker/staging/docker-compose.yml logs -f web
```

## Staging Environment Variables

Ensure these are set in staging:

- `DJANGO_SETTINGS_MODULE=config.settings.staging`
- `DATABASE_URL` - PostgreSQL connection string (AWS RDS or DO)
- `REDIS_URL` - Redis connection string
- `SECRET_KEY` - Django secret key
- `ALLOWED_HOSTS` - Staging domain
- `EMAIL_*` - SMTP configuration

## Health Check

```bash
curl -I https://staging.example.com/health/
```
