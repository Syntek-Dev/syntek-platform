#!/usr/bin/env bash
# =============================================================================
# Backend Template - Staging Environment Helper Script
# =============================================================================
# Manages Docker-based staging environment for Django application
# Usage: ./scripts/env/staging.sh [command]
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
COMPOSE_FILE="${PROJECT_ROOT}/docker/staging/docker-compose.yml"
ENV_FILE="${PROJECT_ROOT}/.env.staging"
ENV_EXAMPLE="${PROJECT_ROOT}/.env.staging.example"
PROJECT_NAME="backend_template_staging"

# Service names
WEB_SERVICE="web"
REDIS_SERVICE="redis"

# Staging-specific ports (offset from dev to allow parallel running)
WEB_PORT=8001
REDIS_PORT=6380

# -----------------------------------------------------------------------------
# Colour Output Functions
# -----------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
ORANGE='\033[0;33m'
NC='\033[0m' # No Colour

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
header() { echo -e "\n${ORANGE}=== STAGING: $1 ===${NC}\n"; }

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

    # Check for required environment file
    if [[ ! -f "${ENV_FILE}" ]]; then
        if [[ -f "${ENV_EXAMPLE}" ]]; then
            warning "Environment file not found. Creating from example..."
            cp "${ENV_EXAMPLE}" "${ENV_FILE}"
            warning "Created ${ENV_FILE}. Please update with staging credentials before deploying!"
            exit 1
        else
            error "Environment file required: ${ENV_FILE}"
            error "Please create it with staging configuration."
            exit 1
        fi
    fi
}

check_env_vars() {
    local required_vars=("SECRET_KEY" "DATABASE_URL" "ALLOWED_HOSTS")
    local missing=0

    source "${ENV_FILE}" 2>/dev/null || true

    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            error "Required environment variable not set: ${var}"
            missing=1
        fi
    done

    if [[ ${missing} -eq 1 ]]; then
        error "Please set all required variables in ${ENV_FILE}"
        exit 1
    fi
}

# -----------------------------------------------------------------------------
# Docker Compose Wrapper
# -----------------------------------------------------------------------------
dc() {
    docker compose -f "${COMPOSE_FILE}" -p "${PROJECT_NAME}" --env-file "${ENV_FILE}" "$@"
}

# -----------------------------------------------------------------------------
# Service Management Commands
# -----------------------------------------------------------------------------
cmd_start() {
    header "Starting Staging Environment"
    check_prerequisites
    check_env_vars

    warning "Starting staging environment..."
    read -p "Continue? (y/n): " confirm
    if [[ "${confirm}" != "y" ]]; then
        info "Operation cancelled."
        exit 0
    fi

    dc up -d
    success "Staging environment started!"
    cmd_urls
}

cmd_stop() {
    header "Stopping Staging Environment"

    warning "This will stop all staging services."
    read -p "Continue? (y/n): " confirm
    if [[ "${confirm}" != "y" ]]; then
        info "Operation cancelled."
        exit 0
    fi

    dc down
    success "Staging environment stopped."
}

cmd_restart() {
    header "Restarting Staging Environment"
    dc restart
    success "Staging environment restarted."
}

cmd_build() {
    header "Building Staging Containers"
    check_prerequisites
    dc build
    success "Staging containers built."
}

cmd_rebuild() {
    header "Rebuilding Staging Containers (no cache)"
    check_prerequisites

    warning "This will rebuild all staging containers from scratch."
    read -p "Continue? (y/n): " confirm
    if [[ "${confirm}" != "y" ]]; then
        info "Operation cancelled."
        exit 0
    fi

    dc build --no-cache
    success "Staging containers rebuilt."
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
    header "Staging Environment Status"
    dc ps
}

# -----------------------------------------------------------------------------
# Deployment Commands
# -----------------------------------------------------------------------------
cmd_deploy() {
    header "Deploying to Staging"
    check_prerequisites
    check_env_vars

    warning "This will deploy the current code to staging."
    warning "Make sure you have committed all changes."
    read -p "Continue? (y/n): " confirm
    if [[ "${confirm}" != "y" ]]; then
        info "Deployment cancelled."
        exit 0
    fi

    info "Step 1/5: Building containers..."
    dc build

    info "Step 2/5: Starting services..."
    dc up -d

    info "Step 3/5: Waiting for database..."
    sleep 10

    info "Step 4/5: Running migrations..."
    dc exec -T ${WEB_SERVICE} python manage.py migrate --noinput

    info "Step 5/5: Collecting static files..."
    dc exec -T ${WEB_SERVICE} python manage.py collectstatic --noinput

    success "Deployment to staging completed!"
    cmd_urls
    cmd_health
}

cmd_rollback() {
    header "Rolling Back Staging Deployment"

    warning "This will stop current containers and restore from last backup."
    warning "Make sure you have a recent backup before proceeding."
    read -p "Type 'ROLLBACK' to confirm: " confirm
    if [[ "${confirm}" != "ROLLBACK" ]]; then
        info "Rollback cancelled."
        exit 0
    fi

    info "Stopping current containers..."
    dc down

    info "Please restore your database backup manually."
    info "Then run: $0 start"

    warning "Rollback process initiated. Complete manual steps to finish."
}

# -----------------------------------------------------------------------------
# Database Commands
# -----------------------------------------------------------------------------
cmd_migrate() {
    header "Running Staging Migrations"

    warning "This will run migrations on the staging database."
    read -p "Continue? (y/n): " confirm
    if [[ "${confirm}" != "y" ]]; then
        info "Operation cancelled."
        exit 0
    fi

    dc exec ${WEB_SERVICE} python manage.py migrate
    success "Migrations completed."
}

cmd_makemigrations() {
    local app="${1:-}"
    header "Creating Database Migrations (Staging)"

    warning "This will create new migrations in the staging environment."
    read -p "Continue? (y/n): " confirm
    if [[ "${confirm}" != "y" ]]; then
        info "Operation cancelled."
        exit 0
    fi

    if [[ -n "${app}" ]]; then
        dc exec ${WEB_SERVICE} python manage.py makemigrations "${app}"
    else
        dc exec ${WEB_SERVICE} python manage.py makemigrations
    fi
    success "Migrations created."
}

cmd_backup() {
    header "Creating Staging Database Backup"

    local backup_dir="${PROJECT_ROOT}/backups/staging"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${backup_dir}/staging_backup_${timestamp}.sql"

    mkdir -p "${backup_dir}"

    # Extract database credentials from environment
    source "${ENV_FILE}"

    info "Creating backup: ${backup_file}"

    # Parse DATABASE_URL for pg_dump
    # Format: postgres://user:password@host:port/dbname
    if [[ "${DATABASE_URL}" =~ postgres://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
        local db_user="${BASH_REMATCH[1]}"
        local db_pass="${BASH_REMATCH[2]}"
        local db_host="${BASH_REMATCH[3]}"
        local db_port="${BASH_REMATCH[4]}"
        local db_name="${BASH_REMATCH[5]}"

        PGPASSWORD="${db_pass}" pg_dump -h "${db_host}" -p "${db_port}" -U "${db_user}" "${db_name}" > "${backup_file}"
        success "Backup created: ${backup_file}"
    else
        error "Could not parse DATABASE_URL. Please backup manually."
        exit 1
    fi
}

cmd_shell() {
    header "Opening Django Shell (Staging)"
    dc exec ${WEB_SERVICE} python manage.py shell
}

cmd_bash() {
    header "Opening Bash Shell (Staging)"
    dc exec ${WEB_SERVICE} bash
}

# -----------------------------------------------------------------------------
# Testing Commands (Staging)
# -----------------------------------------------------------------------------
cmd_test() {
    header "Running Smoke Tests on Staging"

    info "Running basic connectivity tests..."

    # Test web service
    local web_status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${WEB_PORT}/admin/" || echo "000")
    if [[ "${web_status}" =~ ^(200|301|302)$ ]]; then
        success "Web service responding (HTTP ${web_status})"
    else
        error "Web service not responding (HTTP ${web_status})"
    fi

    # Test health endpoint
    local health_status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:${WEB_PORT}/health/" || echo "000")
    if [[ "${health_status}" == "200" ]]; then
        success "Health endpoint OK"
    else
        warning "Health endpoint returned ${health_status}"
    fi

    success "Smoke tests completed."
}

# -----------------------------------------------------------------------------
# Monitoring Commands
# -----------------------------------------------------------------------------
cmd_health() {
    header "Staging Health Check"

    info "Checking Web Service..."
    if dc exec -T ${WEB_SERVICE} python manage.py check --deploy 2>/dev/null; then
        success "Django deployment checks passed"
    else
        warning "Some deployment checks have warnings"
    fi

    info "Checking Redis..."
    if dc exec -T ${REDIS_SERVICE} redis-cli ping &> /dev/null; then
        success "Redis is healthy"
    else
        error "Redis is not responding"
    fi

    info "Testing database connection..."
    if dc exec -T ${WEB_SERVICE} python manage.py dbshell -c "SELECT 1;" &> /dev/null; then
        success "Database connection OK"
    else
        error "Database connection failed"
    fi
}

cmd_urls() {
    header "Staging URLs"
    echo -e "  ${GREEN}Web Application:${NC}  http://localhost:${WEB_PORT}"
    echo -e "  ${GREEN}Django Admin:${NC}     http://localhost:${WEB_PORT}/admin"
    echo -e "  ${GREEN}GraphQL:${NC}          http://localhost:${WEB_PORT}/graphql"
    echo -e "  ${GREEN}Health Check:${NC}     http://localhost:${WEB_PORT}/health/"
    echo ""
    warning "Note: These are local staging URLs. Production URLs may differ."
}

# -----------------------------------------------------------------------------
# Maintenance Commands
# -----------------------------------------------------------------------------
cmd_clean() {
    header "Cleaning Staging Environment"

    warning "This will remove all staging containers, volumes, and images!"
    warning "Make sure you have backed up any important data."
    read -p "Type 'DELETE' to confirm: " confirm
    if [[ "${confirm}" != "DELETE" ]]; then
        info "Operation cancelled."
        exit 0
    fi

    dc down -v --remove-orphans --rmi local
    success "Staging environment cleaned."
}

cmd_collectstatic() {
    header "Collecting Static Files (Staging)"
    dc exec ${WEB_SERVICE} python manage.py collectstatic --noinput
    success "Static files collected."
}

# -----------------------------------------------------------------------------
# Help
# -----------------------------------------------------------------------------
cmd_help() {
    echo -e "${ORANGE}Backend Template - Staging Environment Helper${NC}"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo -e "${YELLOW}Service Management:${NC}"
    echo "  start              Start staging environment"
    echo "  stop               Stop staging environment"
    echo "  restart            Restart staging environment"
    echo "  build              Build containers"
    echo "  rebuild            Rebuild containers (no cache)"
    echo "  logs [service]     View logs"
    echo "  status             Show container status"
    echo ""
    echo -e "${YELLOW}Deployment:${NC}"
    echo "  deploy             Full deployment to staging"
    echo "  rollback           Initiate rollback procedure"
    echo ""
    echo -e "${YELLOW}Database:${NC}"
    echo "  migrate            Run database migrations"
    echo "  makemigrations     Create new migrations"
    echo "  backup             Create database backup"
    echo "  shell              Open Django shell"
    echo "  bash               Open bash shell in container"
    echo ""
    echo -e "${YELLOW}Monitoring:${NC}"
    echo "  health             Run health checks"
    echo "  test               Run smoke tests"
    echo "  urls               Show staging URLs"
    echo ""
    echo -e "${YELLOW}Maintenance:${NC}"
    echo "  collectstatic      Collect static files"
    echo "  clean              Remove all containers and volumes"
    echo ""
    echo -e "${YELLOW}Notes:${NC}"
    echo "  - Staging uses port ${WEB_PORT} to avoid conflicts with dev"
    echo "  - Ensure .env.staging is configured before deployment"
    echo "  - Always backup before major operations"
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

        # Deployment
        deploy)          cmd_deploy ;;
        rollback)        cmd_rollback ;;

        # Database
        migrate)         cmd_migrate ;;
        makemigrations)  cmd_makemigrations "$@" ;;
        backup)          cmd_backup ;;
        shell)           cmd_shell ;;
        bash)            cmd_bash ;;

        # Monitoring
        health)          cmd_health ;;
        test)            cmd_test ;;
        urls)            cmd_urls ;;

        # Maintenance
        collectstatic)   cmd_collectstatic ;;
        clean)           cmd_clean ;;

        help|--help|-h)  cmd_help ;;

        *)
            error "Unknown command: ${command}"
            cmd_help
            exit 1
            ;;
    esac
}

main "$@"
