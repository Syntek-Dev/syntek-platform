#!/usr/bin/env bash
# =============================================================================
# Backend Template - Development Environment Helper Script
# =============================================================================
# Manages Docker-based development environment for Django/Wagtail application
# Usage: ./scripts/env/dev.sh [command]
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
COMPOSE_FILE="${PROJECT_ROOT}/docker/dev/docker-compose.yml"
ENV_FILE="${PROJECT_ROOT}/.env.dev"
ENV_EXAMPLE="${PROJECT_ROOT}/.env.dev.example"
PROJECT_NAME="backend_template_dev"

# Service names
WEB_SERVICE="web"
DB_SERVICE="db"
REDIS_SERVICE="redis"
MAILPIT_SERVICE="mailpit"

# -----------------------------------------------------------------------------
# Colour Output Functions
# -----------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Colour

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
header() { echo -e "\n${CYAN}=== $1 ===${NC}\n"; }

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
        success "Created ${ENV_FILE} from example. Please review and update settings."
    fi
}

# -----------------------------------------------------------------------------
# Docker Compose Wrapper
# -----------------------------------------------------------------------------
dc() {
    docker compose -f "${COMPOSE_FILE}" -p "${PROJECT_NAME}" "$@"
}

# -----------------------------------------------------------------------------
# Service Management Commands
# -----------------------------------------------------------------------------
cmd_start() {
    header "Starting Development Environment"
    check_prerequisites
    dc up -d
    success "Development environment started!"
    cmd_urls
}

cmd_stop() {
    header "Stopping Development Environment"
    dc down
    success "Development environment stopped."
}

cmd_restart() {
    header "Restarting Development Environment"
    dc restart
    success "Development environment restarted."
}

cmd_build() {
    header "Building Development Containers"
    check_prerequisites
    dc build
    success "Containers built successfully."
}

cmd_rebuild() {
    header "Rebuilding Development Containers (no cache)"
    check_prerequisites
    dc build --no-cache
    success "Containers rebuilt successfully."
}

cmd_logs() {
    local service="${1:-}"
    if [[ -n "${service}" ]]; then
        dc logs -f "${service}"
    else
        dc logs -f
    fi
}

cmd_status() {
    header "Development Environment Status"
    dc ps
}

# -----------------------------------------------------------------------------
# Django Management Commands
# -----------------------------------------------------------------------------
cmd_shell() {
    header "Opening Django Shell"
    dc exec ${WEB_SERVICE} python manage.py shell
}

cmd_bash() {
    header "Opening Bash Shell in Web Container"
    dc exec ${WEB_SERVICE} bash
}

cmd_migrate() {
    header "Running Database Migrations"
    dc exec ${WEB_SERVICE} python manage.py migrate
    success "Migrations completed."
}

cmd_makemigrations() {
    local app="${1:-}"
    header "Creating Database Migrations"
    if [[ -n "${app}" ]]; then
        dc exec ${WEB_SERVICE} python manage.py makemigrations "${app}"
    else
        dc exec ${WEB_SERVICE} python manage.py makemigrations
    fi
    success "Migrations created."
}

cmd_collectstatic() {
    header "Collecting Static Files"
    dc exec ${WEB_SERVICE} python manage.py collectstatic --noinput
    success "Static files collected."
}

cmd_createsuperuser() {
    header "Creating Superuser"
    dc exec ${WEB_SERVICE} python manage.py createsuperuser
}

cmd_dbshell() {
    header "Opening PostgreSQL Shell"
    dc exec ${DB_SERVICE} psql -U backend_template -d backend_template_dev
}

cmd_flush() {
    warning "This will DELETE ALL DATA in the development database!"
    read -p "Are you sure? Type 'yes' to confirm: " confirm
    if [[ "${confirm}" == "yes" ]]; then
        header "Flushing Database"
        dc exec ${WEB_SERVICE} python manage.py flush --noinput
        success "Database flushed."
    else
        info "Operation cancelled."
    fi
}

cmd_loaddata() {
    local fixture="${1:-}"
    if [[ -z "${fixture}" ]]; then
        error "Usage: $0 loaddata <fixture_name>"
        exit 1
    fi
    header "Loading Fixture: ${fixture}"
    dc exec ${WEB_SERVICE} python manage.py loaddata "${fixture}"
    success "Fixture loaded."
}

cmd_dumpdata() {
    local app="${1:-}"
    if [[ -z "${app}" ]]; then
        error "Usage: $0 dumpdata <app_name>"
        exit 1
    fi
    header "Dumping Data: ${app}"
    dc exec ${WEB_SERVICE} python manage.py dumpdata "${app}" --indent 2
}

# -----------------------------------------------------------------------------
# Testing Commands
# -----------------------------------------------------------------------------
cmd_test() {
    local args="${*:-}"
    header "Running Tests"
    if [[ -n "${args}" ]]; then
        dc exec ${WEB_SERVICE} pytest ${args}
    else
        dc exec ${WEB_SERVICE} pytest
    fi
}

cmd_test_cov() {
    header "Running Tests with Coverage"
    dc exec ${WEB_SERVICE} pytest --cov=apps --cov-report=html --cov-report=term-missing
    success "Coverage report generated in htmlcov/"
}

cmd_lint() {
    header "Running Linters"
    info "Running Ruff..."
    dc exec ${WEB_SERVICE} ruff check .
    info "Running Black (check mode)..."
    dc exec ${WEB_SERVICE} black --check .
    info "Running isort (check mode)..."
    dc exec ${WEB_SERVICE} isort --check-only .
    success "Linting completed."
}

cmd_format() {
    header "Formatting Code"
    info "Running Black..."
    dc exec ${WEB_SERVICE} black .
    info "Running isort..."
    dc exec ${WEB_SERVICE} isort .
    info "Running Ruff fix..."
    dc exec ${WEB_SERVICE} ruff check --fix .
    success "Code formatted."
}

cmd_typecheck() {
    header "Running Type Checker"
    dc exec ${WEB_SERVICE} mypy .
}

# -----------------------------------------------------------------------------
# Maintenance Commands
# -----------------------------------------------------------------------------
cmd_clean() {
    warning "This will remove all development containers, volumes, and orphans!"
    read -p "Are you sure? Type 'DELETE' to confirm: " confirm
    if [[ "${confirm}" == "DELETE" ]]; then
        header "Cleaning Development Environment"
        dc down -v --remove-orphans
        success "Development environment cleaned."
    else
        info "Operation cancelled."
    fi
}

cmd_reset() {
    warning "This will reset the entire development environment (containers, volumes, database)!"
    read -p "Are you sure? Type 'RESET' to confirm: " confirm
    if [[ "${confirm}" == "RESET" ]]; then
        header "Resetting Development Environment"
        dc down -v --remove-orphans
        dc build --no-cache
        dc up -d
        sleep 5
        dc exec ${WEB_SERVICE} python manage.py migrate
        success "Development environment reset complete."
        cmd_urls
    else
        info "Operation cancelled."
    fi
}

cmd_backup() {
    local backup_dir="${PROJECT_ROOT}/backups"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${backup_dir}/dev_backup_${timestamp}.sql"

    mkdir -p "${backup_dir}"
    header "Creating Database Backup"
    dc exec -T ${DB_SERVICE} pg_dump -U backend_template backend_template_dev > "${backup_file}"
    success "Backup created: ${backup_file}"
}

cmd_restore() {
    local backup_file="${1:-}"
    if [[ -z "${backup_file}" ]]; then
        error "Usage: $0 restore <backup_file.sql>"
        exit 1
    fi
    if [[ ! -f "${backup_file}" ]]; then
        error "Backup file not found: ${backup_file}"
        exit 1
    fi

    warning "This will replace the current database with the backup!"
    read -p "Are you sure? Type 'yes' to confirm: " confirm
    if [[ "${confirm}" == "yes" ]]; then
        header "Restoring Database from Backup"
        dc exec -T ${DB_SERVICE} psql -U backend_template -d backend_template_dev < "${backup_file}"
        success "Database restored from: ${backup_file}"
    else
        info "Operation cancelled."
    fi
}

# -----------------------------------------------------------------------------
# Information Commands
# -----------------------------------------------------------------------------
cmd_urls() {
    header "Development URLs"
    echo -e "  ${GREEN}Web Application:${NC}  http://localhost:8000"
    echo -e "  ${GREEN}Django Admin:${NC}     http://localhost:8000/admin"
    echo -e "  ${GREEN}Wagtail Admin:${NC}    http://localhost:8000/cms"
    echo -e "  ${GREEN}GraphQL:${NC}          http://localhost:8000/graphql"
    echo -e "  ${GREEN}Mailpit:${NC}          http://localhost:8025"
    echo -e "  ${GREEN}PostgreSQL:${NC}       localhost:5432"
    echo -e "  ${GREEN}Redis:${NC}            localhost:6379"
}

cmd_health() {
    header "Health Check"

    info "Checking PostgreSQL..."
    if dc exec -T ${DB_SERVICE} pg_isready -U backend_template &> /dev/null; then
        success "PostgreSQL is healthy"
    else
        error "PostgreSQL is not responding"
    fi

    info "Checking Redis..."
    if dc exec -T ${REDIS_SERVICE} redis-cli ping &> /dev/null; then
        success "Redis is healthy"
    else
        error "Redis is not responding"
    fi

    info "Checking Web Service..."
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/admin/ | grep -q "200\|301\|302"; then
        success "Web service is healthy"
    else
        warning "Web service may not be ready yet"
    fi
}

# -----------------------------------------------------------------------------
# Help
# -----------------------------------------------------------------------------
cmd_help() {
    echo -e "${CYAN}Backend Template - Development Environment Helper${NC}"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo -e "${YELLOW}Service Management:${NC}"
    echo "  start              Start development environment"
    echo "  stop               Stop development environment"
    echo "  restart            Restart development environment"
    echo "  build              Build containers"
    echo "  rebuild            Rebuild containers (no cache)"
    echo "  logs [service]     View logs (optionally for specific service)"
    echo "  status             Show container status"
    echo ""
    echo -e "${YELLOW}Django Commands:${NC}"
    echo "  shell              Open Django shell"
    echo "  bash               Open bash shell in web container"
    echo "  migrate            Run database migrations"
    echo "  makemigrations     Create new migrations"
    echo "  collectstatic      Collect static files"
    echo "  createsuperuser    Create Django superuser"
    echo "  dbshell            Open PostgreSQL shell"
    echo "  flush              Flush database (destructive)"
    echo "  loaddata <fix>     Load fixture data"
    echo "  dumpdata <app>     Dump app data as JSON"
    echo ""
    echo -e "${YELLOW}Testing & Quality:${NC}"
    echo "  test [args]        Run pytest tests"
    echo "  test-cov           Run tests with coverage report"
    echo "  lint               Run linters (ruff, black, isort)"
    echo "  format             Auto-format code"
    echo "  typecheck          Run mypy type checker"
    echo ""
    echo -e "${YELLOW}Maintenance:${NC}"
    echo "  clean              Remove containers and volumes (destructive)"
    echo "  reset              Full environment reset (destructive)"
    echo "  backup             Create database backup"
    echo "  restore <file>     Restore database from backup"
    echo ""
    echo -e "${YELLOW}Information:${NC}"
    echo "  urls               Show development URLs"
    echo "  health             Run health checks"
    echo "  help               Show this help message"
}

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
main() {
    local command="${1:-help}"
    shift || true

    case "${command}" in
        # Service Management
        start)           cmd_start ;;
        stop)            cmd_stop ;;
        restart)         cmd_restart ;;
        build)           cmd_build ;;
        rebuild)         cmd_rebuild ;;
        logs)            cmd_logs "$@" ;;
        status)          cmd_status ;;

        # Django Commands
        shell)           cmd_shell ;;
        bash)            cmd_bash ;;
        migrate)         cmd_migrate ;;
        makemigrations)  cmd_makemigrations "$@" ;;
        collectstatic)   cmd_collectstatic ;;
        createsuperuser) cmd_createsuperuser ;;
        dbshell)         cmd_dbshell ;;
        flush)           cmd_flush ;;
        loaddata)        cmd_loaddata "$@" ;;
        dumpdata)        cmd_dumpdata "$@" ;;

        # Testing
        test)            cmd_test "$@" ;;
        test-cov)        cmd_test_cov ;;
        lint)            cmd_lint ;;
        format)          cmd_format ;;
        typecheck)       cmd_typecheck ;;

        # Maintenance
        clean)           cmd_clean ;;
        reset)           cmd_reset ;;
        backup)          cmd_backup ;;
        restore)         cmd_restore "$@" ;;

        # Information
        urls)            cmd_urls ;;
        health)          cmd_health ;;
        help|--help|-h)  cmd_help ;;

        *)
            error "Unknown command: ${command}"
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"
