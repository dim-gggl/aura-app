#!/bin/bash

# =============================================================================
# Aura Art - Production Deployment Script
# =============================================================================
# This script handles the complete deployment process for Aura Art
# Usage: ./deploy.sh [environment]
#   environment: dev, staging, or production (default: production)
# =============================================================================

set -e  # Exit on error
set -u  # Exit on undefined variable

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Configuration
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_NAME="aura-app"
readonly ENVIRONMENT="${1:-production}"
readonly BACKUP_DIR="${SCRIPT_DIR}/backups"
readonly LOG_FILE="${SCRIPT_DIR}/deploy_$(date +%Y%m%d_%H%M%S).log"

# =============================================================================
# Helper Functions
# =============================================================================

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $*" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $*" | tee -a "$LOG_FILE" >&2
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $*" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $*" | tee -a "$LOG_FILE"
}

print_header() {
    echo -e "\n${BLUE}======================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}======================================${NC}\n"
}

check_command() {
    if ! command -v "$1" &> /dev/null; then
        log_error "Required command not found: $1"
        exit 1
    fi
}

confirm() {
    read -p "$(echo -e ${YELLOW}"$1 (y/N): "${NC})" -n 1 -r
    echo
    [[ $REPLY =~ ^[Yy]$ ]]
}

# =============================================================================
# Validation Functions
# =============================================================================

validate_environment() {
    case "$ENVIRONMENT" in
        dev|staging|production)
            log "Deploying to: $ENVIRONMENT"
            ;;
        *)
            log_error "Invalid environment: $ENVIRONMENT"
            log_error "Valid options: dev, staging, production"
            exit 1
            ;;
    esac
}

check_dependencies() {
    print_header "Checking Dependencies"

    check_command docker
    check_command docker-compose
    check_command git

    log "All dependencies are installed"
}

check_env_file() {
    print_header "Checking Environment Configuration"

    if [ ! -f "${SCRIPT_DIR}/.env" ]; then
        log_error "Missing .env file"
        log_error "Copy .env.production.example to .env and configure it"
        exit 1
    fi

    # Check for critical variables
    if ! grep -q "^SECRET_KEY=" "${SCRIPT_DIR}/.env" || grep -q "SECRET_KEY=REPLACE_WITH" "${SCRIPT_DIR}/.env"; then
        log_error "SECRET_KEY not configured in .env"
        exit 1
    fi

    log "Environment file validated"
}

# =============================================================================
# Backup Functions
# =============================================================================

create_backup() {
    if [ "$ENVIRONMENT" != "production" ]; then
        log_info "Skipping backup for $ENVIRONMENT environment"
        return 0
    fi

    print_header "Creating Backup"

    mkdir -p "$BACKUP_DIR"

    local backup_name="backup_$(date +%Y%m%d_%H%M%S)"
    local backup_path="${BACKUP_DIR}/${backup_name}"

    log "Creating backup: $backup_name"

    # Backup database
    if docker-compose ps | grep -q "aura_db.*Up"; then
        log "Backing up database..."
        docker-compose exec -T db pg_dump -U "${POSTGRES_USER:-aura_user}" "${POSTGRES_DB:-aura_db}" > "${backup_path}_db.sql" 2>/dev/null || {
            log_warning "Database backup failed"
        }
    else
        log_warning "Database container not running, skipping database backup"
    fi

    # Backup media files
    if [ -d "${SCRIPT_DIR}/media" ]; then
        log "Backing up media files..."
        tar -czf "${backup_path}_media.tar.gz" -C "${SCRIPT_DIR}" media/ 2>/dev/null || {
            log_warning "Media backup failed"
        }
    fi

    # Backup .env file
    if [ -f "${SCRIPT_DIR}/.env" ]; then
        cp "${SCRIPT_DIR}/.env" "${backup_path}_env"
    fi

    log "Backup completed: $backup_path"
}

# =============================================================================
# Deployment Functions
# =============================================================================

prepare_directories() {
    print_header "Preparing Directories"

    if [ "$ENVIRONMENT" = "production" ]; then
        # Create production directories on host
        sudo mkdir -p /var/lib/aura/{postgres,redis}
        sudo mkdir -p /var/www/aura/{static,media}
        sudo mkdir -p /etc/nginx/ssl

        # Set ownership
        sudo chown -R "$(whoami):$(whoami)" /var/lib/aura /var/www/aura

        log "Production directories created"
    else
        log "Development/staging mode - using Docker volumes"
    fi
}

pull_latest_code() {
    print_header "Pulling Latest Code"

    # Only pull if this is a git repository
    if [ -d "${SCRIPT_DIR}/.git" ]; then
        log "Fetching latest changes from git..."
        git fetch origin

        local current_branch=$(git rev-parse --abbrev-ref HEAD)
        log "Current branch: $current_branch"

        if [ "$ENVIRONMENT" = "production" ]; then
            if confirm "Pull latest changes from origin/$current_branch?"; then
                git pull origin "$current_branch"
                log "Code updated successfully"
            else
                log_warning "Skipping code update"
            fi
        else
            log_info "Skipping git pull for $ENVIRONMENT"
        fi
    else
        log_warning "Not a git repository, skipping code update"
    fi
}

build_images() {
    print_header "Building Docker Images"

    local build_args=""
    build_args+=" --build-arg BUILD_DATE=$(date -u +'%Y-%m-%dT%H:%M:%SZ')"
    build_args+=" --build-arg VERSION=$(git describe --tags --always 2>/dev/null || echo 'latest')"
    build_args+=" --build-arg VCS_REF=$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"

    log "Building images with args: $build_args"

    if [ "$ENVIRONMENT" = "production" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml build $build_args
    else
        docker-compose build $build_args
    fi

    log "Images built successfully"
}

stop_services() {
    print_header "Stopping Services"

    if docker-compose ps | grep -q "Up"; then
        log "Stopping running services..."

        if [ "$ENVIRONMENT" = "production" ]; then
            docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
        else
            docker-compose down
        fi

        log "Services stopped"
    else
        log "No services running"
    fi
}

start_services() {
    print_header "Starting Services"

    if [ "$ENVIRONMENT" = "production" ]; then
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    else
        docker-compose up -d
    fi

    log "Services started"
}

wait_for_health() {
    print_header "Waiting for Services to be Healthy"

    local max_attempts=30
    local attempt=0

    log "Waiting for services to start..."
    sleep 10

    while [ $attempt -lt $max_attempts ]; do
        if docker-compose ps | grep -q "unhealthy"; then
            log_warning "Some services are unhealthy, waiting... (attempt $((attempt+1))/$max_attempts)"
            sleep 10
            attempt=$((attempt+1))
        else
            log "All services are healthy"
            return 0
        fi
    done

    log_error "Services did not become healthy in time"
    docker-compose ps
    return 1
}

run_migrations() {
    print_header "Running Database Migrations"

    log "Executing migrations..."
    docker-compose exec -T web python manage.py migrate --noinput

    log "Migrations completed"
}

collect_static() {
    print_header "Collecting Static Files"

    if [ "$ENVIRONMENT" = "production" ]; then
        log "Collecting static files for production..."
        docker-compose exec -T web python manage.py collectstatic --noinput --clear
        log "Static files collected"
    else
        log_info "Skipping static collection for $ENVIRONMENT"
    fi
}

run_checks() {
    print_header "Running System Checks"

    log "Running Django deployment checks..."
    docker-compose exec -T web python manage.py check --deploy || {
        log_warning "Some deployment checks failed"
    }
}

# =============================================================================
# Main Deployment Flow
# =============================================================================

main() {
    print_header "Aura Art Deployment - $ENVIRONMENT"

    log "Starting deployment at $(date)"
    log "Log file: $LOG_FILE"

    # Pre-deployment checks
    validate_environment
    check_dependencies
    check_env_file

    # Confirm production deployment
    if [ "$ENVIRONMENT" = "production" ]; then
        if ! confirm "Deploy to PRODUCTION?"; then
            log "Deployment cancelled"
            exit 0
        fi
    fi

    # Create backup
    create_backup

    # Prepare environment
    prepare_directories
    pull_latest_code

    # Build and deploy
    build_images
    stop_services
    start_services

    # Wait for services
    if ! wait_for_health; then
        log_error "Deployment failed - services are not healthy"
        log_error "Check logs with: docker-compose logs"
        exit 1
    fi

    # Post-deployment tasks
    run_migrations
    collect_static
    run_checks

    # Cleanup old images
    log "Cleaning up unused Docker images..."
    docker image prune -f

    print_header "Deployment Completed Successfully"

    log "Deployment finished at $(date)"
    log "Application is running at:"

    if [ "$ENVIRONMENT" = "production" ]; then
        log "  https://aura-art.org"
        log "  Admin: https://aura-art.org/${ADMIN_URL:-admin/}"
    else
        log "  http://localhost:${NGINX_HTTP_PORT:-80}"
        log "  Admin: http://localhost:${NGINX_HTTP_PORT:-80}/${ADMIN_URL:-admin/}"
    fi

    log "\nUseful commands:"
    log "  View logs: docker-compose logs -f"
    log "  Check status: docker-compose ps"
    log "  Shell access: docker-compose exec web bash"
}

# =============================================================================
# Script Entry Point
# =============================================================================

# Trap errors
trap 'log_error "Deployment failed at line $LINENO"' ERR

# Change to script directory
cd "$SCRIPT_DIR"

# Run main function
main "$@"
