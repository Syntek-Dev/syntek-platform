# Test Commands

**Last Updated**: 03/01/2026
**Version**: 0.2.0
**Maintained By**: Development Team
**Language**: British English (en_GB)
**Timezone**: Europe/London

---

## Run All Tests

```bash
docker compose -f docker/test/docker-compose.yml run --rm web pytest
```

## Run Tests with Coverage

```bash
docker compose -f docker/test/docker-compose.yml run --rm web pytest --cov=apps --cov-report=html
```

## Run Specific Test File

```bash
docker compose -f docker/test/docker-compose.yml run --rm web pytest apps/myapp/tests/test_models.py
```

## Run Tests with Verbose Output

```bash
docker compose -f docker/test/docker-compose.yml run --rm web pytest -v
```

## Run Tests Matching Pattern

```bash
docker compose -f docker/test/docker-compose.yml run --rm web pytest -k "test_user"
```

## Run Linting

```bash
docker compose -f docker/test/docker-compose.yml run --rm web flake8 apps/
docker compose -f docker/test/docker-compose.yml run --rm web black --check apps/
```

## Run Type Checking

```bash
docker compose -f docker/test/docker-compose.yml run --rm web mypy apps/
```
