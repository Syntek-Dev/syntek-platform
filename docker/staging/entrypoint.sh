#!/usr/bin/env bash
# =============================================================================
# Backend Template - Staging Container Entrypoint
# =============================================================================
# Initializes the staging container before starting the application
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# Colour Output
# -----------------------------------------------------------------------------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${BLUE}[ENTRYPOINT]${NC} $1"; }
success() { echo -e "${GREEN}[ENTRYPOINT]${NC} $1"; }
warning() { echo -e "${YELLOW}[ENTRYPOINT]${NC} $1"; }

# -----------------------------------------------------------------------------
# Wait for Dependencies
# -----------------------------------------------------------------------------
wait_for_postgres() {
    info "Waiting for PostgreSQL..."

    local max_attempts=30
    local attempt=1

    while [[ ${attempt} -le ${max_attempts} ]]; do
        if python manage.py dbshell -- -c "SELECT 1;" &> /dev/null; then
            success "PostgreSQL is ready!"
            return 0
        fi
        info "Attempt ${attempt}/${max_attempts}: PostgreSQL not ready, waiting..."
        sleep 2
        ((attempt++))
    done

    warning "PostgreSQL did not become ready in time, proceeding anyway..."
    return 1
}

wait_for_redis() {
    info "Waiting for Redis..."

    if [[ -z "${REDIS_URL:-}" ]]; then
        warning "REDIS_URL not set, skipping Redis check"
        return 0
    fi

    local max_attempts=15
    local attempt=1

    while [[ ${attempt} -le ${max_attempts} ]]; do
        if python -c "import redis; r = redis.from_url('${REDIS_URL}'); r.ping()" &> /dev/null; then
            success "Redis is ready!"
            return 0
        fi
        info "Attempt ${attempt}/${max_attempts}: Redis not ready, waiting..."
        sleep 1
        ((attempt++))
    done

    warning "Redis did not become ready in time, proceeding anyway..."
    return 1
}

# -----------------------------------------------------------------------------
# Database Migrations
# -----------------------------------------------------------------------------
run_migrations() {
    info "Running database migrations..."

    if python manage.py migrate --noinput; then
        success "Migrations completed successfully."
    else
        warning "Migration failed - application may not work correctly."
        return 1
    fi
}

# -----------------------------------------------------------------------------
# Static Files
# -----------------------------------------------------------------------------
collect_static() {
    info "Collecting static files..."

    if python manage.py collectstatic --noinput --clear; then
        success "Static files collected."
    else
        warning "Static file collection failed."
        return 1
    fi
}

# -----------------------------------------------------------------------------
# Django Checks
# -----------------------------------------------------------------------------
run_checks() {
    info "Running Django deployment checks..."

    # Run checks but don't fail on warnings
    python manage.py check --deploy || warning "Some deployment checks have warnings."
}

# -----------------------------------------------------------------------------
# Main Entrypoint
# -----------------------------------------------------------------------------
main() {
    info "Starting staging container initialization..."
    info "Environment: ${DJANGO_SETTINGS_MODULE:-config.settings.staging}"

    # Wait for dependencies
    wait_for_postgres
    wait_for_redis

    # Run initialization tasks
    run_migrations
    collect_static
    run_checks

    success "Staging container initialization complete!"
    info "Starting application..."

    # Execute the main command (passed as arguments)
    exec "$@"
}

main "$@"
