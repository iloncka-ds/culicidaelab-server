#!/bin/bash

# CulicidaeLab Backup Script
# This script creates comprehensive backups of the CulicidaeLab application
# Usage: ./scripts/backup.sh [--retention-days <days>] [--compress] [--verify]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="/var/backups/culicidaelab"
LOG_FILE="/var/log/culicidaelab/backup.log"
DEFAULT_RETENTION_DAYS=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

info() { log "INFO" "${BLUE}$*${NC}"; }
warn() { log "WARN" "${YELLOW}$*${NC}"; }
error() { log "ERROR" "${RED}$*${NC}"; }
success() { log "SUCCESS" "${GREEN}$*${NC}"; }

# Create comprehensive backup
create_backup() {
    local backup_id=$(date '+%Y%m%d_%H%M%S')
    local backup_path="$BACKUP_DIR/$backup_id"
    local compress=${1:-false}
    
    info "Creating backup with ID: $backup_id"
    
    # Create backup directory structure
    mkdir -p "$backup_path"/{database,config,certificates,logs,static}
    
    # Backup database
    backup_database "$backup_path/database"
    
    # Backup configuration files
    backup_configuration "$backup_path/config"
    
    # Backup SSL certificates
    backup_certificates "$backup_path/certificates"
    
    # Backup logs
    backup_logs "$backup_path/logs"
    
    # Backup static files
    backup_static_files "$backup_path/static"
    
    # Create backup metadata
    create_backup_metadata "$backup_path" "$backup_id"
    
    # Compress backup if requested
    if [ "$compress" = true ]; then
        compress_backup "$backup_path" "$backup_id"
    fi
    
    success "Backup created: $backup_path"
    echo "$backup_id"
}

# Backup database
backup_database() {
    local backup_path=$1
    
    info "Backing up database..."
    
    # Check if backend container is running
    if docker ps --format "table {{.Names}}" | grep -q "culicidaelab_backend_prod"; then
        # Create database backup inside container
        docker exec culicidaelab_backend_prod sh -c "
            if [ -f /app/data/culicidaelab.db ]; then
                cp /app/data/culicidaelab.db /tmp/backup_db.db
                echo 'Database file copied successfully'
            else
                echo 'Database file not found'
                exit 1
            fi
        "
        
        # Copy backup from container to host
        if docker cp culicidaelab_backend_prod:/tmp/backup_db.db "$backup_path/culicidaelab.db"; then
            success "Database backup completed"
            
            # Get database info
            local db_size=$(stat -f%z "$backup_path/culicidaelab.db" 2>/dev/null || stat -c%s "$backup_path/culicidaelab.db" 2>/dev/null || echo "unknown")
            info "Database size: $db_size bytes"
        else
            error "Failed to copy database backup"
            return 1
        fi
        
        # Clean up temporary file in container
        docker exec culicidaelab_backend_prod rm -f /tmp/backup_db.db
    else
        warn "Backend container not running, checking for database volume..."
        
        # Try to backup from volume directly
        if docker volume ls | grep -q "backend_data"; then
            docker run --rm -v backend_data:/data -v "$backup_path":/backup alpine sh -c "
                if [ -f /data/culicidaelab.db ]; then
                    cp /data/culicidaelab.db /backup/culicidaelab.db
                    echo 'Database backup from volume completed'
                else
                    echo 'Database file not found in volume'
                fi
            "
        else
            warn "No database found to backup"
        fi
    fi
}

# Backup configuration files
backup_configuration() {
    local backup_path=$1
    
    info "Backing up configuration files..."
    
    # Backup environment files
    for env_file in ".env.prod" ".env.dev" ".env"; do
        if [ -f "$PROJECT_ROOT/$env_file" ]; then
            cp "$PROJECT_ROOT/$env_file" "$backup_path/"
            info "Backed up $env_file"
        fi
    done
    
    # Backup Docker Compose files
    for compose_file in "docker-compose.prod.yml" "docker-compose.dev.yml" "docker-compose.yml"; do
        if [ -f "$PROJECT_ROOT/$compose_file" ]; then
            cp "$PROJECT_ROOT/$compose_file" "$backup_path/"
            info "Backed up $compose_file"
        fi
    done
    
    # Backup nginx configuration
    if [ -d "$PROJECT_ROOT/nginx" ]; then
        cp -r "$PROJECT_ROOT/nginx" "$backup_path/"
        info "Backed up nginx configuration"
    fi
    
    # Backup scripts
    if [ -d "$PROJECT_ROOT/scripts" ]; then
        cp -r "$PROJECT_ROOT/scripts" "$backup_path/"
        info "Backed up scripts directory"
    fi
    
    success "Configuration backup completed"
}

# Backup SSL certificates
backup_certificates() {
    local backup_path=$1
    
    info "Backing up SSL certificates..."
    
    # Backup Let's Encrypt certificates
    if [ -d "/etc/letsencrypt" ]; then
        tar -czf "$backup_path/letsencrypt.tar.gz" -C /etc letsencrypt
        success "SSL certificates backup completed"
    else
        warn "No SSL certificates found to backup"
    fi
    
    # Backup certificate volume if it exists
    if docker volume ls | grep -q "letsencrypt_certs"; then
        docker run --rm -v letsencrypt_certs:/certs -v "$backup_path":/backup alpine tar -czf /backup/letsencrypt_volume.tar.gz -C /certs .
        info "Certificate volume backup completed"
    fi
}

# Backup logs
backup_logs() {
    local backup_path=$1
    
    info "Backing up logs..."
    
    # Backup application logs
    if [ -d "/var/log/culicidaelab" ]; then
        cp -r /var/log/culicidaelab "$backup_path/"
        info "Application logs backup completed"
    fi
    
    # Backup Docker container logs
    local containers=("culicidaelab_backend_prod" "culicidaelab_frontend_prod" "culicidaelab_nginx_prod" "culicidaelab_certbot_prod")
    
    for container in "${containers[@]}"; do
        if docker ps -a --format "table {{.Names}}" | grep -q "$container"; then
            docker logs "$container" > "$backup_path/${container}.log" 2>&1
            info "Backed up logs for $container"
        fi
    done
    
    success "Logs backup completed"
}

# Backup static files
backup_static_files() {
    local backup_path=$1
    
    info "Backing up static files..."
    
    # Backup static files from volume
    if docker volume ls | grep -q "backend_static"; then
        docker run --rm -v backend_static:/static -v "$backup_path":/backup alpine tar -czf /backup/static_files.tar.gz -C /static .
        success "Static files backup completed"
    else
        warn "No static files volume found to backup"
    fi
}

# Create backup metadata
create_backup_metadata() {
    local backup_path=$1
    local backup_id=$2
    
    info "Creating backup metadata..."
    
    # Get Git information
    local git_commit="unknown"
    local git_branch="unknown"
    if cd "$PROJECT_ROOT" && git rev-parse HEAD &>/dev/null; then
        git_commit=$(git rev-parse HEAD)
        git_branch=$(git rev-parse --abbrev-ref HEAD)
    fi
    
    # Get Docker images information
    local docker_images=$(docker images --format "{{.Repository}}:{{.Tag}}" | grep culicidaelab | jq -R . | jq -s . 2>/dev/null || echo '[]')
    
    # Get system information
    local system_info=$(cat << EOF
{
    "hostname": "$(hostname)",
    "kernel": "$(uname -r)",
    "os": "$(lsb_release -d -s 2>/dev/null || echo 'Unknown')",
    "docker_version": "$(docker --version | cut -d' ' -f3 | tr -d ',')",
    "compose_version": "$(docker-compose --version | cut -d' ' -f3 | tr -d ',')"
}
EOF
)
    
    # Create comprehensive metadata
    cat > "$backup_path/metadata.json" << EOF
{
    "backup_id": "$backup_id",
    "timestamp": "$(date -Iseconds)",
    "unix_timestamp": $(date +%s),
    "git": {
        "commit": "$git_commit",
        "branch": "$git_branch"
    },
    "docker_images": $docker_images,
    "system": $system_info,
    "backup_size": "$(du -sh "$backup_path" | cut -f1)",
    "files": $(find "$backup_path" -type f -name "*.db" -o -name "*.tar.gz" -o -name "*.yml" -o -name "*.env" | jq -R . | jq -s .)
}
EOF
    
    success "Backup metadata created"
}

# Compress backup
compress_backup() {
    local backup_path=$1
    local backup_id=$2
    
    info "Compressing backup..."
    
    local compressed_file="$BACKUP_DIR/${backup_id}.tar.gz"
    
    if tar -czf "$compressed_file" -C "$BACKUP_DIR" "$backup_id"; then
        # Remove uncompressed directory
        rm -rf "$backup_path"
        success "Backup compressed: $compressed_file"
    else
        error "Failed to compress backup"
        return 1
    fi
}

# Verify backup integrity
verify_backup() {
    local backup_id=$1
    local backup_path="$BACKUP_DIR/$backup_id"
    
    info "Verifying backup integrity: $backup_id"
    
    # Check if backup exists
    if [ ! -d "$backup_path" ] && [ ! -f "$backup_path.tar.gz" ]; then
        error "Backup $backup_id not found"
        return 1
    fi
    
    # If compressed, extract temporarily for verification
    local temp_extracted=false
    if [ -f "$backup_path.tar.gz" ] && [ ! -d "$backup_path" ]; then
        info "Extracting compressed backup for verification..."
        tar -xzf "$backup_path.tar.gz" -C "$BACKUP_DIR"
        temp_extracted=true
    fi
    
    # Verify metadata file
    if [ ! -f "$backup_path/metadata.json" ]; then
        error "Backup metadata file missing"
        return 1
    fi
    
    # Verify database backup
    if [ -f "$backup_path/database/culicidaelab.db" ]; then
        # Check if database file is valid SQLite
        if command -v sqlite3 &> /dev/null; then
            if sqlite3 "$backup_path/database/culicidaelab.db" "SELECT name FROM sqlite_master WHERE type='table';" &> /dev/null; then
                success "Database backup verification passed"
            else
                error "Database backup appears to be corrupted"
                return 1
            fi
        else
            warn "sqlite3 not available, skipping database integrity check"
        fi
    else
        warn "No database backup found"
    fi
    
    # Verify configuration files
    local config_files=(".env.prod" "docker-compose.prod.yml")
    for config_file in "${config_files[@]}"; do
        if [ -f "$backup_path/config/$config_file" ]; then
            info "Configuration file $config_file verified"
        else
            warn "Configuration file $config_file not found in backup"
        fi
    done
    
    # Clean up temporary extraction
    if [ "$temp_extracted" = true ]; then
        rm -rf "$backup_path"
    fi
    
    success "Backup verification completed"
}

# Clean old backups
cleanup_old_backups() {
    local retention_days=$1
    
    info "Cleaning up backups older than $retention_days days..."
    
    # Find and remove old backup directories
    find "$BACKUP_DIR" -maxdepth 1 -type d -name "[0-9]*_[0-9]*" -mtime +$retention_days -exec rm -rf {} \;
    
    # Find and remove old compressed backups
    find "$BACKUP_DIR" -maxdepth 1 -type f -name "[0-9]*_[0-9]*.tar.gz" -mtime +$retention_days -delete
    
    success "Old backups cleanup completed"
}

# List available backups
list_backups() {
    info "Available backups:"
    
    # List directories
    for backup_dir in "$BACKUP_DIR"/[0-9]*_[0-9]*; do
        if [ -d "$backup_dir" ]; then
            local backup_id=$(basename "$backup_dir")
            local backup_date=$(echo "$backup_id" | sed 's/_/ /')
            local backup_size=$(du -sh "$backup_dir" | cut -f1)
            echo "  $backup_id (Directory, Size: $backup_size, Date: $backup_date)"
        fi
    done
    
    # List compressed files
    for backup_file in "$BACKUP_DIR"/[0-9]*_[0-9]*.tar.gz; do
        if [ -f "$backup_file" ]; then
            local backup_id=$(basename "$backup_file" .tar.gz)
            local backup_date=$(echo "$backup_id" | sed 's/_/ /')
            local backup_size=$(du -sh "$backup_file" | cut -f1)
            echo "  $backup_id (Compressed, Size: $backup_size, Date: $backup_date)"
        fi
    done
}

# Main function
main() {
    local retention_days=$DEFAULT_RETENTION_DAYS
    local compress=false
    local verify=false
    local list_only=false
    local verify_id=""
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --retention-days)
                retention_days="$2"
                shift 2
                ;;
            --compress)
                compress=true
                shift
                ;;
            --verify)
                if [ -n "${2:-}" ] && [[ ! "$2" =~ ^-- ]]; then
                    verify_id="$2"
                    shift 2
                else
                    verify=true
                    shift
                fi
                ;;
            --list)
                list_only=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  --retention-days <days>  Set backup retention period (default: $DEFAULT_RETENTION_DAYS)"
                echo "  --compress               Compress backup after creation"
                echo "  --verify [backup_id]     Verify backup integrity (all if no ID specified)"
                echo "  --list                   List available backups"
                echo "  -h, --help              Show this help message"
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    mkdir -p "$BACKUP_DIR"
    
    info "CulicidaeLab Backup Script Started"
    info "Timestamp: $(date)"
    
    # Handle list command
    if [ "$list_only" = true ]; then
        list_backups
        exit 0
    fi
    
    # Handle verify command
    if [ -n "$verify_id" ]; then
        verify_backup "$verify_id"
        exit 0
    fi
    
    # Create new backup
    local backup_id=$(create_backup "$compress")
    
    # Verify new backup if requested
    if [ "$verify" = true ]; then
        verify_backup "$backup_id"
    fi
    
    # Clean up old backups
    cleanup_old_backups "$retention_days"
    
    success "Backup process completed successfully!"
    info "Backup ID: $backup_id"
    info "Logs available at: $LOG_FILE"
}

# Run main function
main "$@"