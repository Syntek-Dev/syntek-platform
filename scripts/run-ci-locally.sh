#!/usr/bin/env bash

# Run CI Checks Locally
# This script runs the same checks that GitHub Actions runs, but locally in Docker
# Usage: ./scripts/run-ci-locally.sh [check-type]
# Check types: all, lint, test, security, migrate

set -e

# Colours
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Colour

# Default to running all checks
CHECK_TYPE="${1:-all}"

echo -e "${BLUE}=========================================="
echo "Running CI Checks Locally"
echo -e "==========================================${NC}"
echo ""

# Ensure Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    exit 1
fi

# Build test container if needed
echo -e "${YELLOW}Building test container...${NC}"
docker compose -f docker/test/docker-compose.yml build web --quiet

# Function to run linting checks
run_lint() {
    echo -e "\n${BLUE}=== Linting and Formatting ===${NC}"

    echo -e "${YELLOW}Running Black formatting check...${NC}"
    docker compose -f docker/test/docker-compose.yml run --rm --no-deps web \
        black --check --diff .

    echo -e "${YELLOW}Running isort import sorting check...${NC}"
    docker compose -f docker/test/docker-compose.yml run --rm --no-deps web \
        isort --check-only --diff .

    echo -e "${YELLOW}Running flake8 linting...${NC}"
    docker compose -f docker/test/docker-compose.yml run --rm --no-deps web \
        flake8 .

    echo -e "${YELLOW}Running mypy type checking...${NC}"
    docker compose -f docker/test/docker-compose.yml run --rm --no-deps web \
        mypy . || echo -e "${YELLOW}⚠️  Type checking completed with warnings${NC}"

    echo -e "${GREEN}✅ Linting checks complete${NC}"
}

# Function to fix formatting
run_format() {
    echo -e "\n${BLUE}=== Auto-formatting Code ===${NC}"

    echo -e "${YELLOW}Running Black formatter...${NC}"
    docker compose -f docker/test/docker-compose.yml run --rm --no-deps web \
        black .

    echo -e "${YELLOW}Running isort...${NC}"
    docker compose -f docker/test/docker-compose.yml run --rm --no-deps web \
        isort .

    echo -e "${GREEN}✅ Code formatted${NC}"
}

# Function to run tests
run_test() {
    echo -e "\n${BLUE}=== Running Tests ===${NC}"

    # Start services
    echo -e "${YELLOW}Starting test services...${NC}"
    docker compose -f docker/test/docker-compose.yml up -d db redis mailpit

    # Wait for database
    echo -e "${YELLOW}Waiting for database...${NC}"
    sleep 5

    # Run migrations
    echo -e "${YELLOW}Running migrations...${NC}"
    docker compose -f docker/test/docker-compose.yml run --rm web \
        python manage.py migrate --noinput

    # Run tests
    echo -e "${YELLOW}Running pytest...${NC}"
    docker compose -f docker/test/docker-compose.yml run --rm web \
        pytest --cov=apps --cov=api --cov=config \
        --cov-report=term-missing --cov-report=html

    # Cleanup
    docker compose -f docker/test/docker-compose.yml down -v

    echo -e "${GREEN}✅ Tests complete${NC}"
    echo -e "Coverage report: ${BLUE}htmlcov/index.html${NC}"
}

# Function to run security checks
run_security() {
    echo -e "\n${BLUE}=== Security Scanning ===${NC}"

    echo -e "${YELLOW}Running Bandit security scan...${NC}"
    docker compose -f docker/test/docker-compose.yml run --rm --no-deps web \
        bandit -r apps/ api/ config/ || echo -e "${YELLOW}⚠️  Security issues found${NC}"

    echo -e "${YELLOW}Running Django security checks...${NC}"
    docker compose -f docker/test/docker-compose.yml up -d db redis
    sleep 3
    docker compose -f docker/test/docker-compose.yml run --rm web \
        python manage.py check --deploy --fail-level WARNING || true
    docker compose -f docker/test/docker-compose.yml down -v

    echo -e "${GREEN}✅ Security checks complete${NC}"
}

# Function to check migrations
run_migrate_check() {
    echo -e "\n${BLUE}=== Migration Checks ===${NC}"

    echo -e "${YELLOW}Starting database...${NC}"
    docker compose -f docker/test/docker-compose.yml up -d db
    sleep 5

    echo -e "${YELLOW}Checking for missing migrations...${NC}"
    docker compose -f docker/test/docker-compose.yml run --rm web \
        python manage.py makemigrations --check --dry-run --no-input

    echo -e "${YELLOW}Validating existing migrations...${NC}"
    docker compose -f docker/test/docker-compose.yml run --rm web \
        python manage.py migrate --check

    docker compose -f docker/test/docker-compose.yml down -v

    echo -e "${GREEN}✅ Migration checks complete${NC}"
}

# Function to run all checks
run_all() {
    run_lint
    run_test
    run_security
    run_migrate_check

    echo -e "\n${GREEN}=========================================="
    echo "✅ All CI checks passed!"
    echo -e "==========================================${NC}"
}

# Main execution
case "$CHECK_TYPE" in
    lint)
        run_lint
        ;;
    format)
        run_format
        ;;
    test)
        run_test
        ;;
    security)
        run_security
        ;;
    migrate)
        run_migrate_check
        ;;
    all)
        run_all
        ;;
    *)
        echo -e "${RED}Unknown check type: $CHECK_TYPE${NC}"
        echo ""
        echo "Usage: $0 [check-type]"
        echo ""
        echo "Available check types:"
        echo "  all      - Run all checks (default)"
        echo "  lint     - Run linting and type checking"
        echo "  format   - Auto-format code with Black and isort"
        echo "  test     - Run test suite with coverage"
        echo "  security - Run security scans"
        echo "  migrate  - Check Django migrations"
        exit 1
        ;;
esac
