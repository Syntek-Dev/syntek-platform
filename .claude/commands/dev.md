# Development Commands

## Start Development Environment

```bash
docker compose -f docker/dev/docker-compose.yml up -d
```

## Stop Development Environment

```bash
docker compose -f docker/dev/docker-compose.yml down
```

## View Logs

```bash
docker compose -f docker/dev/docker-compose.yml logs -f
```

## Django Shell

```bash
docker compose -f docker/dev/docker-compose.yml exec web python manage.py shell
```

## Run Migrations

```bash
docker compose -f docker/dev/docker-compose.yml exec web python manage.py migrate
```

## Create Superuser

```bash
docker compose -f docker/dev/docker-compose.yml exec web python manage.py createsuperuser
```

## Access Points

- **Web Application:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin
- **GraphQL Playground:** http://localhost:8000/graphql
- **Mailpit:** http://localhost:8025
