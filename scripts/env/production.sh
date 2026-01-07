#!/usr/bin/env bash
# =============================================================================
# Backend Template - Production Environment Helper Script
# =============================================================================
# Manages Docker-based production environment for Django application
# Usage: ./scripts/env/production.sh [command]
#
# WARNING: This script manages PRODUCTION systems. Use with extreme caution.
# =============================================================================

set -euo pipefail

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
COMPOSE_FILE="${PROJECT_ROOT}/docker/production/docker-compose.yml"
ENV_FILE="${PROJECT_ROOT}/.env.production"
ENV_EXAMPLE="${PROJECT_ROOT}/.env.production.example"
PROJECT_NAME="backend_template_production"

# Service names
WEB_SERVICE="web"

# Backup configuration
BACKUP_DIR="${PROJECT_ROOT}/backups/production"
BACKUP_RETENTION_DAYS=30

# -----------------------------------------------------------------------------
# Colour Output Functions
# -----------------------------------------------------------------------------
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD_RED='\033[1;31m'
NC='\033[0m' # No Colour

info() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }
critical() { echo -e "${BOLD_RED}[CRITICAL]${NC} $1"; }
header() { echo -e "\n${BOLD_RED}=== PRODUCTION: $1 ===${NC}\n"; }

# -----------------------------------------------------------------------------
# Safety Checks
# -----------------------------------------------------------------------------
production_warning() {
    echo ""
    echo -e "${BOLD_RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BOLD_RED}║                    ⚠️  PRODUCTION WARNING ⚠️                  ║${NC}"
    echo -e "${BOLD_RED}║                                                            ║${NC}"
    echo -e "${BOLD_RED}║  You are about to perform an action on PRODUCTION.         ║${NC}"
    echo -e "${BOLD_RED}║  This may affect live users and data.                      ║${NC}"
    echo -e "${BOLD_RED}║                                                            ║${NC}"
    echo -e "${BOLD_RED}║  Make sure you have:                                       ║${NC}"
    echo -e "${BOLD_RED}║  • A recent database backup                                ║${NC}"
    echo -e "${BOLD_RED}║  • Tested changes in staging                               ║${NC}"
    echo -e "${BOLD_RED}║  • Notified the team (if applicable)                       ║${NC}"
    echo -e "${BOLD_RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

confirm_production() {
    local action="$1"
    production_warning
    read -p "Type 'PRODUCTION' to confirm ${action}: " confirm
    if [[ "${confirm}" != "PRODUCTION" ]]; then
        info "Operation cancelled."
        exit 0
    fi
}

confirm_destructive() {
    local action="$1"
    production_warning
    echo -e "${BOLD_RED}This is a DESTRUCTIVE operation that cannot be undone!${NC}"
    read -p "Type 'I UNDERSTAND THE RISKS' to confirm ${action}: " confirm
    if [[ "${confirm}" != "I UNDERSTAND THE RISKS" ]]; then
        info "Operation cancelled."
        exit 0
    fi
}

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

    # Production requires environment file
    if [[ ! -f "${ENV_FILE}" ]]; then
        error "Production environment file required: ${ENV_FILE}"
        error "This file must be configured with production credentials."
        if [[ -f "${ENV_EXAMPLE}" ]]; then
            info "Example file available at: ${ENV_EXAMPLE}"
        fi
        exit 1
    fi
}

check_env_vars() {
    local required_vars=(
        "SECRET_KEY"
        "DATABASE_URL"
        "ALLOWED_HOSTS"
        "REDIS_URL"
    )
    local missing=0

    source "${ENV_FILE}" 2>/dev/null || true

    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            error "Required environment variable not set: ${var}"
            missing=1
        fi
    done

    # Check for placeholder values
    if [[ "${SECRET_KEY:-}" == *"changeme"* ]] || [[ "${SECRET_KEY:-}" == *"example"* ]]; then
        error "SECRET_KEY appears to be a placeholder. Please set a real secret key."
        missing=1
    fi

    if [[ ${missing} -eq 1 ]]; then
        error "Please configure all required variables in ${ENV_FILE}"
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
    header "Starting Production Environment"
    check_prerequisites
    check_env_vars
    confirm_production "starting production services"

    dc up -d
    success "Production environment started!"

    info "Running health checks..."
    sleep 10
    cmd_health
}

cmd_stop() {
    header "Stopping Production Environment"
    check_prerequisites
    confirm_production "stopping production services"

    dc down
    success "Production environment stopped."
}

cmd_restart() {
    header "Restarting Production Environment"
    check_prerequisites
    confirm_production "restarting production services"

    info "Performing graceful restart..."
    dc restart
    sleep 5
    cmd_health
    success "Production environment restarted."
}

cmd_build() {
    header "Building Production Containers"
    check_prerequisites
    confirm_production "building production containers"

    dc build
    success "Production containers built."
}

cmd_rebuild() {
    header "Rebuilding Production Containers"
    check_prerequisites
    confirm_production "rebuilding production containers (no cache)"

    dc build --no-cache
    success "Production containers rebuilt."
}

cmd_logs() {
    local service="${1:-}"
    local lines="${2:-100}"

    if [[ -n "${service}" ]]; then
        dc logs -f --tail="${lines}" "${service}"
    else
        dc logs -f --tail="${lines}"
    fi
}

cmd_status() {
    header "Production Environment Status"
    dc ps
    echo ""
    info "Resource usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" \
        $(dc ps -q) 2>/dev/null || warning "Could not get resource stats"
}

# -----------------------------------------------------------------------------
# Deployment Commands
# -----------------------------------------------------------------------------
cmd_deploy() {
    header "Deploying to Production"
    check_prerequisites
    check_env_vars

    echo ""
    info "Pre-deployment checklist:"
    echo "  [ ] Changes tested in staging"
    echo "  [ ] Database backup created"
    echo "  [ ] Team notified of deployment"
    echo "  [ ] Rollback plan ready"
    echo ""

    confirm_production "deploying to production"

    local timestamp=$(date +%Y%m%d_%H%M%S)

    info "Step 1/6: Creating pre-deployment backup..."
    cmd_backup || warning "Backup failed - proceeding with caution"

    info "Step 2/6: Pulling latest images..."
    dc pull || true

    info "Step 3/6: Building containers..."
    dc build

    info "Step 4/6: Running migrations..."
    dc run --rm ${WEB_SERVICE} python manage.py migrate --noinput

    info "Step 5/6: Collecting static files..."
    dc run --rm ${WEB_SERVICE} python manage.py collectstatic --noinput

    info "Step 6/6: Restarting services..."
    dc up -d

    sleep 10

    info "Running post-deployment health checks..."
    if cmd_health; then
        success "Deployment completed successfully!"
        echo ""
        echo "Deployment timestamp: ${timestamp}"
    else
        error "Health checks failed after deployment!"
        warning "Consider rolling back if issues persist."
    fi
}

cmd_rollback() {
    header "Production Rollback"

    warning "Rollback Procedure:"
    echo "1. Stop current containers"
    echo "2. Restore database from backup (manual step)"
    echo "3. Deploy previous version"
    echo ""

    confirm_destructive "initiating rollback"

    info "Step 1: Stopping current containers..."
    dc down

    echo ""
    warning "MANUAL STEP REQUIRED:"
    echo "1. Restore your database from the most recent backup:"
    echo "   Backups are located in: ${BACKUP_DIR}"
    echo ""
    echo "2. After restoring the database, deploy the previous version:"
    echo "   git checkout <previous-tag>"
    echo "   $0 deploy"
    echo ""

    info "Rollback initiated. Complete manual steps to finish."
}

cmd_scale() {
    local replicas="${1:-}"
    if [[ -z "${replicas}" ]]; then
        error "Usage: $0 scale <number_of_replicas>"
        exit 1
    fi

    header "Scaling Production Web Service"
    confirm_production "scaling to ${replicas} replicas"

    dc up -d --scale ${WEB_SERVICE}="${replicas}"
    success "Scaled to ${replicas} web service replicas."
}

# -----------------------------------------------------------------------------
# Database Commands
# -----------------------------------------------------------------------------
cmd_migrate() {
    header "Running Production Migrations"
    check_prerequisites
    check_env_vars

    warning "This will run migrations on the PRODUCTION database."
    confirm_production "running migrations"

    info "Creating backup before migration..."
    cmd_backup

    dc exec ${WEB_SERVICE} python manage.py migrate
    success "Migrations completed."
}

cmd_makemigrations() {
    local app="${1:-}"
    header "Creating Database Migrations (Production)"
    check_prerequisites
    check_env_vars

    warning "Creating migrations in production is unusual and should typically be done in development."
    warning "This will create new migration files in the PRODUCTION environment."
    confirm_production "creating migrations"

    if [[ -n "${app}" ]]; then
        dc exec ${WEB_SERVICE} python manage.py makemigrations "${app}"
    else
        dc exec ${WEB_SERVICE} python manage.py makemigrations
    fi
    success "Migrations created."
    warning "Remember to commit these migration files to version control."
}

cmd_backup() {
    header "Creating Production Database Backup"

    mkdir -p "${BACKUP_DIR}"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="${BACKUP_DIR}/production_backup_${timestamp}.sql.gz"

    source "${ENV_FILE}"

    info "Creating backup: ${backup_file}"

    # Parse DATABASE_URL for pg_dump
    if [[ "${DATABASE_URL}" =~ postgres://([^:]+):([^@]+)@([^:]+):([^/]+)/(.+) ]]; then
        local db_user="${BASH_REMATCH[1]}"
        local db_pass="${BASH_REMATCH[2]}"
        local db_host="${BASH_REMATCH[3]}"
        local db_port="${BASH_REMATCH[4]}"
        local db_name="${BASH_REMATCH[5]}"

        PGPASSWORD="${db_pass}" pg_dump -h "${db_host}" -p "${db_port}" -U "${db_user}" "${db_name}" | gzip > "${backup_file}"

        local backup_size=$(du -h "${backup_file}" | cut -f1)
        success "Backup created: ${backup_file} (${backup_size})"

        # Clean old backups
        info "Cleaning backups older than ${BACKUP_RETENTION_DAYS} days..."
        find "${BACKUP_DIR}" -name "*.sql.gz" -mtime +${BACKUP_RETENTION_DAYS} -delete
    else
        error "Could not parse DATABASE_URL. Please backup manually."
        return 1
    fi
}

cmd_list_backups() {
    header "Available Production Backups"
    if [[ -d "${BACKUP_DIR}" ]]; then
        ls -lah "${BACKUP_DIR}"/*.sql.gz 2>/dev/null || info "No backups found."
    else
        info "Backup directory does not exist: ${BACKUP_DIR}"
    fi
}

cmd_shell() {
    header "Opening Django Shell (Production)"
    warning "You are accessing the PRODUCTION Django shell."
    confirm_production "opening Django shell"

    dc exec ${WEB_SERVICE} python manage.py shell
}

cmd_bash() {
    header "Opening Bash Shell (Production)"
    warning "You are accessing a PRODUCTION container."
    confirm_production "opening bash shell"

    dc exec ${WEB_SERVICE} bash
}

cmd_dbshell() {
    header "Opening Database Shell (Production)"
    warning "You are accessing the PRODUCTION database directly."
    confirm_destructive "opening database shell"

    dc exec ${WEB_SERVICE} python manage.py dbshell
}

# -----------------------------------------------------------------------------
# Monitoring Commands
# -----------------------------------------------------------------------------
cmd_health() {
    header "Production Health Check"
    local healthy=true

    info "Checking container health..."
    local container_health=$(dc ps --format json | jq -r '.[] | "\(.Name): \(.Health // "N/A")"' 2>/dev/null || dc ps)
    echo "${container_health}"
    echo ""

    info "Checking Django deployment configuration..."
    if dc exec -T ${WEB_SERVICE} python manage.py check --deploy 2>&1; then
        success "Django deployment checks passed"
    else
        warning "Some deployment checks have warnings"
    fi

    info "Testing HTTP endpoint..."
    source "${ENV_FILE}"
    local host=$(echo "${ALLOWED_HOSTS}" | cut -d',' -f1)
    local http_status=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/health/" 2>/dev/null || echo "000")

    if [[ "${http_status}" == "200" ]]; then
        success "HTTP health endpoint returned 200"
    else
        warning "HTTP health check returned: ${http_status}"
        healthy=false
    fi

    if [[ "${healthy}" == "true" ]]; then
        success "All health checks passed!"
        return 0
    else
        warning "Some health checks failed."
        return 1
    fi
}

cmd_metrics() {
    header "Production Metrics"

    info "Container resource usage:"
    docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}\t{{.NetIO}}\t{{.BlockIO}}" \
        $(dc ps -q) 2>/dev/null || warning "Could not get container stats"

    echo ""
    info "Disk usage:"
    df -h "${PROJECT_ROOT}" 2>/dev/null || true

    echo ""
    info "Backup directory size:"
    du -sh "${BACKUP_DIR}" 2>/dev/null || echo "N/A"
}

# -----------------------------------------------------------------------------
# Maintenance Commands
# -----------------------------------------------------------------------------
cmd_maintenance_on() {
    header "Enabling Maintenance Mode"
    confirm_production "enabling maintenance mode"

    # This would typically set a flag that the application checks
    # Implementation depends on your application's maintenance mode setup
    dc exec ${WEB_SERVICE} python manage.py maintenance_mode on 2>/dev/null || \
        warning "Maintenance mode command not available. Implement in your Django app."

    success "Maintenance mode enabled."
}

cmd_maintenance_off() {
    header "Disabling Maintenance Mode"
    confirm_production "disabling maintenance mode"

    dc exec ${WEB_SERVICE} python manage.py maintenance_mode off 2>/dev/null || \
        warning "Maintenance mode command not available. Implement in your Django app."

    success "Maintenance mode disabled."
}

cmd_collectstatic() {
    header "Collecting Static Files (Production)"
    confirm_production "collecting static files"

    dc exec ${WEB_SERVICE} python manage.py collectstatic --noinput
    success "Static files collected."
}

cmd_clearsessions() {
    header "Clearing Expired Sessions"
    confirm_production "clearing expired sessions"

    dc exec ${WEB_SERVICE} python manage.py clearsessions
    success "Expired sessions cleared."
}

cmd_clean() {
    header "Cleaning Production Environment"

    critical "This will remove ALL production containers, volumes, and data!"
    critical "This action is IRREVERSIBLE!"

    confirm_destructive "DESTROYING production environment"

    info "Creating final backup..."
    cmd_backup || warning "Backup failed"

    dc down -v --remove-orphans
    success "Production environment cleaned."
}

# -----------------------------------------------------------------------------
# Help
# -----------------------------------------------------------------------------
cmd_help() {
    echo -e "${BOLD_RED}Backend Template - Production Environment Helper${NC}"
    echo ""
    echo "Usage: $0 <command> [options]"
    echo ""
    echo -e "${YELLOW}Service Management:${NC}"
    echo "  start              Start production environment"
    echo "  stop               Stop production environment"
    echo "  restart            Graceful restart"
    echo "  build              Build containers"
    echo "  rebuild            Rebuild containers (no cache)"
    echo "  logs [svc] [n]     View logs (default: last 100 lines)"
    echo "  status             Show status and resource usage"
    echo ""
    echo -e "${YELLOW}Deployment:${NC}"
    echo "  deploy             Full production deployment"
    echo "  rollback           Initiate rollback procedure"
    echo "  scale <n>          Scale web service to n replicas"
    echo ""
    echo -e "${YELLOW}Database:${NC}"
    echo "  migrate            Run database migrations"
    echo "  makemigrations     Create new migrations (not recommended)"
    echo "  backup             Create database backup"
    echo "  list-backups       List available backups"
    echo "  shell              Open Django shell"
    echo "  bash               Open bash shell in container"
    echo "  dbshell            Open database shell (dangerous)"
    echo ""
    echo -e "${YELLOW}Monitoring:${NC}"
    echo "  health             Run health checks"
    echo "  metrics            Show resource metrics"
    echo ""
    echo -e "${YELLOW}Maintenance:${NC}"
    echo "  maintenance-on     Enable maintenance mode"
    echo "  maintenance-off    Disable maintenance mode"
    echo "  collectstatic      Collect static files"
    echo "  clearsessions      Clear expired sessions"
    echo "  clean              Remove all containers (DESTRUCTIVE)"
    echo ""
    echo -e "${BOLD_RED}⚠️  All production operations require confirmation.${NC}"
    echo -e "${BOLD_RED}⚠️  Always backup before making changes.${NC}"
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
        scale)           cmd_scale "$@" ;;

        # Database
        migrate)         cmd_migrate ;;
        makemigrations)  cmd_makemigrations "$@" ;;
        backup)          cmd_backup ;;
        list-backups)    cmd_list_backups ;;
        shell)           cmd_shell ;;
        bash)            cmd_bash ;;
        dbshell)         cmd_dbshell ;;

        # Monitoring
        health)          cmd_health ;;
        metrics)         cmd_metrics ;;

        # Maintenance
        maintenance-on)  cmd_maintenance_on ;;
        maintenance-off) cmd_maintenance_off ;;
        collectstatic)   cmd_collectstatic ;;
        clearsessions)   cmd_clearsessions ;;
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
