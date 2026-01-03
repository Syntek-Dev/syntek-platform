#!/usr/bin/env bash
# =============================================================================
# Backend Template - Test Environment Helper Script
# =============================================================================
# Manages Docker-based test environment for Django/Wagtail application
# Usage: ./scripts/env/test.sh [command]
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
COMPOSE_FILE="${PROJECT_ROOT}/docker/test/docker-compose.yml"
ENV_FILE="${PROJECT_ROOT}/.env.test"
ENV_EXAMPLE="${PROJECT_ROOT}/.env.test.example"
PROJECT_NAME="backend_template_test"

# Service names
WEB_SERVICE="web"
DB_SERVICE="db"
REDIS_SERVICE="redis"

# -----------------------------------------------------------------------------
# Colour Output Functions
# -----------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Colour

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
header() { echo -e "\n${MAGENTA}=== $1 ===${NC}\n"; }

# -----------------------------------------------------------------------------
# Prerequisites Check
# -----------------------------------------------------------------------------
check_prerequisites() {
    local missing=0

    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
        missing=1
    fi

    if ! docker compose version &> /dev/null; then
        error "Docker Compose is not installed or not available."
        missing=1
    fi

    if [[ ! -f "${COMPOSE_FILE}" ]]; then
        error "Docker Compose file not found: ${COMPOSE_FILE}"
        missing=1
    fi

    if [[ ${missing} -eq 1 ]]; then
        exit 1
    fi

    # Create .env file from example if it doesn't exist
    if [[ ! -f "${ENV_FILE}" ]] && [[ -f "${ENV_EXAMPLE}" ]]; then
        warning "Environment file not found. Creating from example..."
        cp "${ENV_EXAMPLE}" "${ENV_FILE}"
        success "Created ${ENV_FILE} from example."
    fi
}

# -----------------------------------------------------------------------------
# Docker Compose Wrapper
# -----------------------------------------------------------------------------
dc() {
    docker compose -f "${COMPOSE_FILE}" -p "${PROJECT_NAME}" "$@"
}

# -----------------------------------------------------------------------------
# Test Environment Commands
# -----------------------------------------------------------------------------
cmd_up() {
    header "Starting Test Environment"
    check_prerequisites
    dc up -d ${DB_SERVICE} ${REDIS_SERVICE}
    info "Waiting for services to be ready..."
    sleep 3
    success "Test environment services started."
}

cmd_down() {
    header "Stopping Test Environment"
    dc down -v --remove-orphans
    success "Test environment stopped and cleaned."
}

cmd_build() {
    header "Building Test Containers"
    check_prerequisites
    dc build
    success "Test containers built."
}

cmd_rebuild() {
    header "Rebuilding Test Containers (no cache)"
    check_prerequisites
    dc build --no-cache
    success "Test containers rebuilt."
}

# -----------------------------------------------------------------------------
# Test Execution Commands
# -----------------------------------------------------------------------------
cmd_run() {
    local args="${*:-}"
    header "Running Test Suite"
    check_prerequisites

    # Start services if not running
    if ! dc ps | grep -q "${DB_SERVICE}.*running"; then
        cmd_up
    fi

    info "Running pytest..."
    if [[ -n "${args}" ]]; then
        dc run --rm ${WEB_SERVICE} pytest ${args}
    else
        dc run --rm ${WEB_SERVICE} pytest
    fi

    local exit_code=$?
    if [[ ${exit_code} -eq 0 ]]; then
        success "All tests passed!"
    else
        error "Some tests failed (exit code: ${exit_code})"
    fi
    return ${exit_code}
}

cmd_run_fast() {
    header "Running Tests (Fast Mode - No Coverage)"
    check_prerequisites

    if ! dc ps | grep -q "${DB_SERVICE}.*running"; then
        cmd_up
    fi

    dc run --rm ${WEB_SERVICE} pytest --no-cov -x -q "$@"
}

cmd_run_verbose() {
    header "Running Tests (Verbose Mode)"
    check_prerequisites

    if ! dc ps | grep -q "${DB_SERVICE}.*running"; then
        cmd_up
    fi

    dc run --rm ${WEB_SERVICE} pytest -v --tb=long "$@"
}

cmd_run_coverage() {
    header "Running Tests with Coverage Report"
    check_prerequisites

    if ! dc ps | grep -q "${DB_SERVICE}.*running"; then
        cmd_up
    fi

    dc run --rm ${WEB_SERVICE} pytest \
        --cov=apps \
        --cov-report=html:htmlcov \
        --cov-report=xml:coverage.xml \
        --cov-report=term-missing:skip-covered \
        --cov-branch \
        "$@"

    success "Coverage reports generated:"
    echo "  - HTML: htmlcov/index.html"
    echo "  - XML:  coverage.xml"
}

cmd_run_unit() {
    header "Running Unit Tests Only"
    check_prerequisites

    if ! dc ps | grep -q "${DB_SERVICE}.*running"; then
        cmd_up
    fi

    dc run --rm ${WEB_SERVICE} pytest -m "unit" "$@"
}

cmd_run_integration() {
    header "Running Integration Tests Only"
    check_prerequisites

    if ! dc ps | grep -q "${DB_SERVICE}.*running"; then
        cmd_up
    fi

    dc run --rm ${WEB_SERVICE} pytest -m "integration" "$@"
}

cmd_run_graphql() {
    header "Running GraphQL Tests Only"
    check_prerequisites

    if ! dc ps | grep -q "${DB_SERVICE}.*running"; then
        cmd_up
    fi

    dc run --rm ${WEB_SERVICE} pytest -m "graphql" "$@"
}

cmd_run_wagtail() {
    header "Running Wagtail Tests Only"
    check_prerequisites

    if ! dc ps | grep -q "${DB_SERVICE}.*running"; then
        cmd_up
    fi

    dc run --rm ${WEB_SERVICE} pytest -m "wagtail" "$@"
}

cmd_run_failed() {
    header "Re-running Failed Tests"
    check_prerequisites

    if ! dc ps | grep -q "${DB_SERVICE}.*running"; then
        cmd_up
    fi

    dc run --rm ${WEB_SERVICE} pytest --lf "$@"
}

cmd_run_app() {
    local app="${1:-}"
    if [[ -z "${app}" ]]; then
        error "Usage: $0 app <app_name>"
        exit 1
    fi
    shift

    header "Running Tests for App: ${app}"
    check_prerequisites

    if ! dc ps | grep -q "${DB_SERVICE}.*running"; then
        cmd_up
    fi

    dc run --rm ${WEB_SERVICE} pytest "apps/${app}/" "$@"
}

# -----------------------------------------------------------------------------
# Code Quality Commands
# -----------------------------------------------------------------------------
cmd_lint() {
    header "Running Linters"
    check_prerequisites

    local exit_code=0

    info "Running Ruff..."
    if ! dc run --rm ${WEB_SERVICE} ruff check .; then
        exit_code=1
    fi

    info "Running Black (check mode)..."
    if ! dc run --rm ${WEB_SERVICE} black --check .; then
        exit_code=1
    fi

    info "Running isort (check mode)..."
    if ! dc run --rm ${WEB_SERVICE} isort --check-only .; then
        exit_code=1
    fi

    if [[ ${exit_code} -eq 0 ]]; then
        success "All linting checks passed!"
    else
        error "Some linting checks failed."
    fi
    return ${exit_code}
}

cmd_typecheck() {
    header "Running Type Checker"
    check_prerequisites
    dc run --rm ${WEB_SERVICE} mypy .
}

cmd_security() {
    header "Running Security Checks"
    check_prerequisites

    info "Running Bandit..."
    dc run --rm ${WEB_SERVICE} bandit -r apps/ -ll

    info "Running Safety check on dependencies..."
    dc run --rm ${WEB_SERVICE} pip-audit || warning "pip-audit not installed"

    success "Security checks completed."
}

cmd_all() {
    header "Running Full Test Suite + Quality Checks"

    local exit_code=0

    cmd_lint || exit_code=1
    cmd_typecheck || exit_code=1
    cmd_run_coverage || exit_code=1

    if [[ ${exit_code} -eq 0 ]]; then
        success "All checks passed!"
    else
        error "Some checks failed."
    fi
    return ${exit_code}
}

# -----------------------------------------------------------------------------
# CI/CD Commands
# -----------------------------------------------------------------------------
cmd_ci() {
    header "Running CI Pipeline"

    # Start with fresh environment
    cmd_down 2>/dev/null || true
    cmd_build
    cmd_up

    local exit_code=0

    # Run linting
    info "Step 1/4: Linting..."
    if ! cmd_lint; then
        error "Linting failed!"
        exit_code=1
    fi

    # Run type checking
    info "Step 2/4: Type checking..."
    if ! cmd_typecheck; then
        warning "Type checking had issues (non-blocking)"
    fi

    # Run security checks
    info "Step 3/4: Security checks..."
    cmd_security || warning "Security checks had warnings"

    # Run tests with coverage
    info "Step 4/4: Running tests..."
    if ! cmd_run_coverage; then
        error "Tests failed!"
        exit_code=1
    fi

    # Cleanup
    cmd_down

    if [[ ${exit_code} -eq 0 ]]; then
        success "CI Pipeline completed successfully!"
    else
        error "CI Pipeline failed!"
    fi
    return ${exit_code}
}

# -----------------------------------------------------------------------------
# Utility Commands
# -----------------------------------------------------------------------------
cmd_shell() {
    header "Opening Test Shell"
    check_prerequisites

    if ! dc ps | grep -q "${DB_SERVICE}.*running"; then
        cmd_up
    fi

    dc run --rm ${WEB_SERVICE} bash
}

cmd_logs() {
    dc logs -f "$@"
}

cmd_status() {
    header "Test Environment Status"
    dc ps
}

cmd_clean() {
    header "Cleaning Test Environment"
    dc down -v --remove-orphans --rmi local
    success "Test environment cleaned (containers, volumes, and local images removed)."
}

# -----------------------------------------------------------------------------
# Help
# -----------------------------------------------------------------------------
cmd_help() {
    echo -e "${MAGENTA}Backend Template - Test Environment Helper${NC}"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo -e "${YELLOW}Environment Management:${NC}"
    echo "  up                 Start test services (db, redis)"
    echo "  down               Stop and clean test environment"
    echo "  build              Build test containers"
    echo "  rebuild            Rebuild containers (no cache)"
    echo "  status             Show container status"
    echo "  logs [service]     View logs"
    echo "  shell              Open bash shell in test container"
    echo "  clean              Remove all test containers and images"
    echo ""
    echo -e "${YELLOW}Test Execution:${NC}"
    echo "  run [args]         Run full test suite"
    echo "  fast [args]        Run tests without coverage (fast)"
    echo "  verbose [args]     Run tests with verbose output"
    echo "  coverage [args]    Run tests with coverage report"
    echo "  failed             Re-run only failed tests"
    echo "  app <name>         Run tests for specific app"
    echo ""
    echo -e "${YELLOW}Test Categories:${NC}"
    echo "  unit               Run unit tests only"
    echo "  integration        Run integration tests only"
    echo "  graphql            Run GraphQL tests only"
    echo "  wagtail            Run Wagtail tests only"
    echo ""
    echo -e "${YELLOW}Code Quality:${NC}"
    echo "  lint               Run linters (ruff, black, isort)"
    echo "  typecheck          Run mypy type checker"
    echo "  security           Run security checks"
    echo "  all                Run all quality checks + tests"
    echo ""
    echo -e "${YELLOW}CI/CD:${NC}"
    echo "  ci                 Run full CI pipeline"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 run                    # Run all tests"
    echo "  $0 fast -k test_login     # Run tests matching 'test_login' (fast)"
    echo "  $0 app users              # Run tests for 'users' app"
    echo "  $0 coverage --tb=short    # Coverage with short tracebacks"
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
main() {
    local command="${1:-help}"
    shift || true

    case "${command}" in
        # Environment
        up)             cmd_up ;;
        down)           cmd_down ;;
        build)          cmd_build ;;
        rebuild)        cmd_rebuild ;;
        status)         cmd_status ;;
        logs)           cmd_logs "$@" ;;
        shell)          cmd_shell ;;
        clean)          cmd_clean ;;

        # Test Execution
        run)            cmd_run "$@" ;;
        fast)           cmd_run_fast "$@" ;;
        verbose)        cmd_run_verbose "$@" ;;
        coverage)       cmd_run_coverage "$@" ;;
        failed)         cmd_run_failed "$@" ;;
        app)            cmd_run_app "$@" ;;

        # Test Categories
        unit)           cmd_run_unit "$@" ;;
        integration)    cmd_run_integration "$@" ;;
        graphql)        cmd_run_graphql "$@" ;;
        wagtail)        cmd_run_wagtail "$@" ;;

        # Code Quality
        lint)           cmd_lint ;;
        typecheck)      cmd_typecheck ;;
        security)       cmd_security ;;
        all)            cmd_all ;;

        # CI/CD
        ci)             cmd_ci ;;

        help|--help|-h) cmd_help ;;

        *)
            error "Unknown command: ${command}"
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"
