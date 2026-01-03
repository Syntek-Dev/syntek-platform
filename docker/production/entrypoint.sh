#!/usr/bin/env bash
# =============================================================================
# Backend Template - Production Container Entrypoint
# =============================================================================
# Initializes the production container before starting the application
# Includes additional safety checks for production environment
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# Colour Output
# -----------------------------------------------------------------------------
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

info() { echo -e "${BLUE}[ENTRYPOINT]${NC} $1"; }
success() { echo -e "${GREEN}[ENTRYPOINT]${NC} $1"; }
warning() { echo -e "${YELLOW}[ENTRYPOINT]${NC} $1"; }
error() { echo -e "${RED}[ENTRYPOINT]${NC} $1"; }

# -----------------------------------------------------------------------------
# Environment Validation
# -----------------------------------------------------------------------------
validate_environment() {
    info "Validating production environment..."

    local required_vars=(
        "SECRET_KEY"
        "DATABASE_URL"
        "ALLOWED_HOSTS"
        "DJANGO_SETTINGS_MODULE"
    )
    local missing=0

    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            error "Required environment variable not set: ${var}"
            missing=1
        fi
    done

    # Verify SECRET_KEY is not a placeholder
    if [[ "${SECRET_KEY:-}" == *"changeme"* ]] || [[ "${SECRET_KEY:-}" == *"example"* ]] || [[ "${SECRET_KEY:-}" == *"insecure"* ]]; then
        error "SECRET_KEY appears to be a placeholder value!"
        missing=1
    fi

    # Verify DEBUG is not enabled
    if [[ "${DEBUG:-false}" == "true" ]] || [[ "${DEBUG:-false}" == "True" ]] || [[ "${DEBUG:-0}" == "1" ]]; then
        error "DEBUG must not be enabled in production!"
        missing=1
    fi

    if [[ ${missing} -eq 1 ]]; then
        error "Environment validation failed. Cannot start production container."
        exit 1
    fi

    success "Environment validation passed."
}

# -----------------------------------------------------------------------------
# Wait for Dependencies
# -----------------------------------------------------------------------------
wait_for_postgres() {
    info "Waiting for PostgreSQL..."

    local max_attempts=60
    local attempt=1

    while [[ ${attempt} -le ${max_attempts} ]]; do
        if python manage.py dbshell -- -c "SELECT 1;" &> /dev/null; then
            success "PostgreSQL is ready!"
            return 0
        fi
        if [[ $((attempt % 10)) -eq 0 ]]; then
            info "Still waiting for PostgreSQL... (attempt ${attempt}/${max_attempts})"
        fi
        sleep 2
        ((attempt++))
    done

    error "PostgreSQL did not become ready in time!"
    exit 1
}

wait_for_redis() {
    info "Waiting for Redis..."

    if [[ -z "${REDIS_URL:-}" ]]; then
        warning "REDIS_URL not set, skipping Redis check"
        return 0
    fi

    local max_attempts=30
    local attempt=1

    while [[ ${attempt} -le ${max_attempts} ]]; do
        if python -c "import redis; r = redis.from_url('${REDIS_URL}'); r.ping()" &> /dev/null; then
            success "Redis is ready!"
            return 0
        fi
        sleep 1
        ((attempt++))
    done

    warning "Redis did not become ready in time - caching may not work."
    return 0
}

# -----------------------------------------------------------------------------
# Database Operations
# -----------------------------------------------------------------------------
run_migrations() {
    info "Running database migrations..."

    # In production, we want migrations to succeed
    if python manage.py migrate --noinput; then
        success "Migrations completed successfully."
    else
        error "Migration failed! Cannot start production container."
        exit 1
    fi
}

check_database() {
    info "Checking database connectivity..."

    if python manage.py dbshell -- -c "SELECT COUNT(*) FROM django_migrations;" &> /dev/null; then
        success "Database connectivity verified."
    else
        error "Cannot verify database connectivity!"
        exit 1
    fi
}

# -----------------------------------------------------------------------------
# Static Files
# -----------------------------------------------------------------------------
collect_static() {
    info "Collecting static files..."

    if python manage.py collectstatic --noinput; then
        success "Static files collected."
    else
        warning "Static file collection had issues."
    fi
}

# -----------------------------------------------------------------------------
# Django Checks
# -----------------------------------------------------------------------------
run_checks() {
    info "Running Django deployment checks..."

    local check_output
    check_output=$(python manage.py check --deploy 2>&1)
    local check_exit=$?

    if [[ ${check_exit} -eq 0 ]]; then
        success "Django deployment checks passed."
    else
        warning "Django deployment checks returned warnings:"
        echo "${check_output}" | head -20
        # Don't fail on warnings, but log them
    fi

    # Check for critical security settings
    info "Verifying security settings..."
    python -c "
from django.conf import settings
import sys

errors = []
if settings.DEBUG:
    errors.append('DEBUG is True')
if not settings.SECURE_SSL_REDIRECT:
    print('WARNING: SECURE_SSL_REDIRECT is False')
if not settings.SESSION_COOKIE_SECURE:
    print('WARNING: SESSION_COOKIE_SECURE is False')
if not settings.CSRF_COOKIE_SECURE:
    print('WARNING: CSRF_COOKIE_SECURE is False')

if errors:
    print('CRITICAL ERRORS:', errors)
    sys.exit(1)
" || warning "Some security settings may need attention"
}

# -----------------------------------------------------------------------------
# Health Check Endpoint
# -----------------------------------------------------------------------------
create_health_marker() {
    # Create a marker file that the health check can use
    touch /tmp/container_initialized
    info "Health check marker created."
}

# -----------------------------------------------------------------------------
# Sentry Initialization
# -----------------------------------------------------------------------------
init_sentry() {
    if [[ -n "${SENTRY_DSN:-}" ]]; then
        info "Sentry DSN configured - error tracking enabled."
    else
        warning "Sentry DSN not configured - error tracking disabled."
    fi
}

# -----------------------------------------------------------------------------
# Pre-start Hooks
# -----------------------------------------------------------------------------
run_prestart_hooks() {
    # Run any custom pre-start scripts
    if [[ -d "/app/scripts/prestart" ]]; then
        info "Running pre-start hooks..."
        for script in /app/scripts/prestart/*.sh; do
            if [[ -f "${script}" ]] && [[ -x "${script}" ]]; then
                info "Running: ${script}"
                "${script}" || warning "Pre-start hook failed: ${script}"
            fi
        done
    fi
}

# -----------------------------------------------------------------------------
# Main Entrypoint
# -----------------------------------------------------------------------------
main() {
    info "=============================================="
    info "Starting production container initialization"
    info "=============================================="
    info "Environment: ${DJANGO_SETTINGS_MODULE:-config.settings.production}"
    info "Python: $(python --version)"
    info "Django: $(python -c 'import django; print(django.VERSION)' 2>/dev/null || echo 'Unknown')"

    # Step 1: Validate environment
    validate_environment

    # Step 2: Wait for dependencies
    wait_for_postgres
    wait_for_redis

    # Step 3: Database operations
    check_database
    run_migrations

    # Step 4: Static files
    collect_static

    # Step 5: Django checks
    run_checks

    # Step 6: Initialize monitoring
    init_sentry

    # Step 7: Run any pre-start hooks
    run_prestart_hooks

    # Step 8: Create health marker
    create_health_marker

    success "=============================================="
    success "Production container initialization complete!"
    success "=============================================="
    info "Starting application server..."

    # Execute the main command (passed as arguments)
    exec "$@"
}

main "$@"
