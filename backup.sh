#!/bin/bash

# =============================================================================
# Aura Art - Automated Backup Script
# =============================================================================
# This script creates automated backups of database, media files, and configs
# Usage: ./backup.sh [options]
#   Options:
#     --db-only       Backup database only
#     --media-only    Backup media files only
#     --upload        Upload to S3 (requires AWS CLI)
#     --restore FILE  Restore from backup file
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
readonly BACKUP_DIR="${BACKUP_DIR:-${SCRIPT_DIR}/backups}"
readonly TIMESTAMP=$(date +%Y%m%d_%H%M%S)
readonly BACKUP_NAME="aura_backup_${TIMESTAMP}"
readonly LOG_FILE="${BACKUP_DIR}/backup_${TIMESTAMP}.log"

# Load environment variables
if [ -f "${SCRIPT_DIR}/.env" ]; then
    set -a
    source "${SCRIPT_DIR}/.env"
    set +a
fi

# Backup configuration
readonly POSTGRES_USER="${POSTGRES_USER:-aura_user}"
readonly POSTGRES_DB="${POSTGRES_DB:-aura_db}"
readonly BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
readonly BACKUP_S3_BUCKET="${BACKUP_S3_BUCKET:-}"

# Parse command line arguments
DB_ONLY=false
MEDIA_ONLY=false
UPLOAD_TO_S3=false
RESTORE_FILE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --db-only)
            DB_ONLY=true
            shift
            ;;
        --media-only)
            MEDIA_ONLY=true
            shift
            ;;
        --upload)
            UPLOAD_TO_S3=true
            shift
            ;;
        --restore)
            RESTORE_FILE="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

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

check_docker_running() {
    if ! docker-compose ps | grep -q "Up"; then
        log_error "Docker services are not running"
        log_error "Start services with: docker-compose up -d"
        exit 1
    fi
}

# =============================================================================
# Backup Functions
# =============================================================================

create_backup_directory() {
    mkdir -p "$BACKUP_DIR"
    log "Backup directory: $BACKUP_DIR"
}

backup_database() {
    print_header "Backing Up Database"

    local backup_file="${BACKUP_DIR}/${BACKUP_NAME}_db.sql"
    local backup_file_gz="${backup_file}.gz"

    log "Creating database backup..."
    log "Database: $POSTGRES_DB"
    log "Output: $backup_file_gz"

    # Create SQL dump
    docker-compose exec -T db pg_dump \
        -U "$POSTGRES_USER" \
        -d "$POSTGRES_DB" \
        --format=plain \
        --no-owner \
        --no-acl \
        --clean \
        --if-exists > "$backup_file" 2>/dev/null || {
            log_error "Database backup failed"
            return 1
        }

    # Compress the backup
    gzip -f "$backup_file"

    local size=$(du -h "$backup_file_gz" | cut -f1)
    log "Database backup completed: $size"
    echo "$backup_file_gz"
}

backup_media() {
    print_header "Backing Up Media Files"

    local media_dir="${SCRIPT_DIR}/media"
    local backup_file="${BACKUP_DIR}/${BACKUP_NAME}_media.tar.gz"

    if [ ! -d "$media_dir" ]; then
        log_warning "Media directory not found: $media_dir"
        return 0
    fi

    local file_count=$(find "$media_dir" -type f | wc -l)
    log "Found $file_count files in media directory"

    if [ "$file_count" -eq 0 ]; then
        log_warning "No media files to backup"
        return 0
    fi

    log "Creating media backup..."
    log "Output: $backup_file"

    tar -czf "$backup_file" -C "${SCRIPT_DIR}" media/ 2>/dev/null || {
        log_error "Media backup failed"
        return 1
    }

    local size=$(du -h "$backup_file" | cut -f1)
    log "Media backup completed: $size"
    echo "$backup_file"
}

backup_static() {
    print_header "Backing Up Static Files"

    local static_dir="${SCRIPT_DIR}/staticfiles"
    local backup_file="${BACKUP_DIR}/${BACKUP_NAME}_static.tar.gz"

    if [ ! -d "$static_dir" ]; then
        log_info "Static directory not found (not critical)"
        return 0
    fi

    log "Creating static files backup..."
    tar -czf "$backup_file" -C "${SCRIPT_DIR}" staticfiles/ 2>/dev/null || {
        log_warning "Static files backup failed (not critical)"
        return 0
    }

    local size=$(du -h "$backup_file" | cut -f1)
    log "Static files backup completed: $size"
    echo "$backup_file"
}

backup_config() {
    print_header "Backing Up Configuration"

    local config_backup="${BACKUP_DIR}/${BACKUP_NAME}_config.tar.gz"

    log "Creating configuration backup..."

    # Backup important config files
    tar -czf "$config_backup" \
        -C "${SCRIPT_DIR}" \
        --exclude='.env' \
        docker-compose.yml \
        docker-compose.prod.yml \
        Dockerfile \
        Dockerfile.nginx \
        nginx.conf \
        entrypoint.sh \
        2>/dev/null || {
            log_warning "Configuration backup failed (not critical)"
            return 0
        }

    # Backup .env separately (encrypted if possible)
    if [ -f "${SCRIPT_DIR}/.env" ]; then
        cp "${SCRIPT_DIR}/.env" "${BACKUP_DIR}/${BACKUP_NAME}_env"
        chmod 600 "${BACKUP_DIR}/${BACKUP_NAME}_env"
        log "Environment file backed up (restricted permissions)"
    fi

    local size=$(du -h "$config_backup" | cut -f1)
    log "Configuration backup completed: $size"
    echo "$config_backup"
}

# =============================================================================
# Upload Functions
# =============================================================================

upload_to_s3() {
    if [ -z "$BACKUP_S3_BUCKET" ]; then
        log_warning "BACKUP_S3_BUCKET not configured, skipping S3 upload"
        return 0
    fi

    print_header "Uploading to S3"

    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not installed"
        log_error "Install with: pip install awscli"
        return 1
    fi

    log "Uploading backups to s3://$BACKUP_S3_BUCKET/"

    # Upload all backup files from this session
    for file in "${BACKUP_DIR}/${BACKUP_NAME}"*; do
        if [ -f "$file" ]; then
            local filename=$(basename "$file")
            log "Uploading: $filename"

            aws s3 cp "$file" "s3://${BACKUP_S3_BUCKET}/${filename}" \
                --storage-class STANDARD_IA \
                --only-show-errors || {
                    log_error "Failed to upload: $filename"
                }
        fi
    done

    log "S3 upload completed"
}

# =============================================================================
# Cleanup Functions
# =============================================================================

cleanup_old_backups() {
    print_header "Cleaning Up Old Backups"

    log "Removing backups older than $BACKUP_RETENTION_DAYS days..."

    local deleted=0

    # Find and delete old backup files
    while IFS= read -r -d '' file; do
        log "Deleting: $(basename "$file")"
        rm -f "$file"
        deleted=$((deleted + 1))
    done < <(find "$BACKUP_DIR" -name "aura_backup_*" -type f -mtime +"$BACKUP_RETENTION_DAYS" -print0)

    if [ $deleted -eq 0 ]; then
        log "No old backups to delete"
    else
        log "Deleted $deleted old backup files"
    fi
}

# =============================================================================
# Restore Functions
# =============================================================================

restore_from_backup() {
    local backup_file="$1"

    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        exit 1
    fi

    print_header "Restoring from Backup"

    log_warning "This will overwrite current data!"
    read -p "Are you sure you want to restore? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        log "Restore cancelled"
        exit 0
    fi

    # Detect backup type
    if [[ "$backup_file" == *"_db.sql"* ]]; then
        restore_database "$backup_file"
    elif [[ "$backup_file" == *"_media.tar.gz"* ]]; then
        restore_media "$backup_file"
    else
        log_error "Unknown backup type"
        exit 1
    fi
}

restore_database() {
    local backup_file="$1"

    log "Restoring database from: $backup_file"

    # Decompress if needed
    if [[ "$backup_file" == *.gz ]]; then
        log "Decompressing backup..."
        gunzip -c "$backup_file" | docker-compose exec -T db psql \
            -U "$POSTGRES_USER" \
            -d "$POSTGRES_DB" > /dev/null 2>&1 || {
                log_error "Database restore failed"
                exit 1
            }
    else
        docker-compose exec -T db psql \
            -U "$POSTGRES_USER" \
            -d "$POSTGRES_DB" < "$backup_file" > /dev/null 2>&1 || {
                log_error "Database restore failed"
                exit 1
            }
    fi

    log "Database restored successfully"
}

restore_media() {
    local backup_file="$1"

    log "Restoring media files from: $backup_file"

    tar -xzf "$backup_file" -C "${SCRIPT_DIR}" || {
        log_error "Media restore failed"
        exit 1
    }

    log "Media files restored successfully"
}

# =============================================================================
# Main Backup Flow
# =============================================================================

main_backup() {
    print_header "Aura Art Backup - $TIMESTAMP"

    log "Starting backup process..."
    log "Log file: $LOG_FILE"

    # Pre-backup checks
    check_docker_running
    create_backup_directory

    local backup_files=()

    # Perform backups based on options
    if [ "$MEDIA_ONLY" = false ]; then
        backup_files+=($(backup_database))
    fi

    if [ "$DB_ONLY" = false ]; then
        backup_files+=($(backup_media))
        backup_files+=($(backup_static))
        backup_files+=($(backup_config))
    fi

    # Upload to S3 if requested
    if [ "$UPLOAD_TO_S3" = true ]; then
        upload_to_s3
    fi

    # Cleanup old backups
    cleanup_old_backups

    print_header "Backup Completed Successfully"

    log "Backup files created:"
    for file in "${backup_files[@]}"; do
        if [ -n "$file" ] && [ -f "$file" ]; then
            log "  - $(basename "$file") ($(du -h "$file" | cut -f1))"
        fi
    done

    log "\nBackup location: $BACKUP_DIR"
    log "Total size: $(du -sh "$BACKUP_DIR" | cut -f1)"
}

# =============================================================================
# Script Entry Point
# =============================================================================

# Trap errors
trap 'log_error "Backup failed at line $LINENO"' ERR

# Change to script directory
cd "$SCRIPT_DIR"

# Main execution
if [ -n "$RESTORE_FILE" ]; then
    restore_from_backup "$RESTORE_FILE"
else
    main_backup
fi
