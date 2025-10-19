#!/bin/bash

# CulicidaeLab Rollback Script
# This script handles rollback operations for the CulicidaeLab application
# Usage: ./scripts/rollback.sh <backup_id> [--force] [--dry-run]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="/var/backups/culicidaelab"
LOG_FILE="/var/log/culicidaelab/rollback.log"
COMPOSE_FILE="docker-compose.prod.yml"

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

# Error handling
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        error "Rollback failed with exit code $exit_code"
        error "Check logs at $LOG_FILE for details"
    fi
    exit $exit_code
}

trap cleanup EXIT

# Validate backup
validate_backup() {
    local backup_id=$1
    local backup_path="$BACKUP_DIR/$backup_id"
    
    info "Validating backup: $backup_id"
    
    # Check if backup exists (directory or compressed file)
    if [ ! -d "$backup_path" ] && [ ! -f "$backup_path.tar.gz" ]; then
        error "Backup $backup_id not found"
        return 1
    fi
    
    # Extract compressed backup if needed
    local temp_extracted=false
    if [ -f "$backup_path.tar.gz" ] && [ ! -d "$backup_path" ]; then
        info "Extracting compressed backup..."
        tar -xzf "$backup_path.tar.gz" -C "$BACKUP_DIR"
        temp_extracted=true
    fi
    
    # Validate metadata
    if [ ! -f "$backup_path/metadata.json" ]; then
        error "Backup metadata file missing"
        return 1
    fi
    
    # Parse and display backup information
    local backup_timestamp=$(jq -r '.timestamp // "unknown"' "$backup_path/metadata.json")
    local git_commit=$(jq -r '.git.commit // "unknown"' "$backup_path/metadata.json")
    local git_branch=$(jq -r '.git.branch // "unknown"' "$backup_path/metadata.json")
    
    info "Backup Information:"
    info "  Timestamp: $backup_timestamp"
    info "  Git Commit: $git_commit"
    info "  Git Branch: $git_branch"
    
    # Validate essential files
    local essential_files=("config/.env.prod" "config/docker-compose.prod.yml")
    for file in "${essential_files[@]}"; do
        if [ ! -f "$backup_path/$file" ]; then
            error "Essential file missing from backup: $file"
            return 1
        fi
    done
    
    success "Backup validation passed"
    
    # Clean up temporary extraction if it was created
    if [ "$temp_extracted" = true ]; then
        rm -rf "$backup_path"
    fi
    
    return 0
}

# Create pre-rollback backup
create_pre_rollback_backup() {
    info "Creating pre-rollback backup..."
    
    local pre_rollback_id="pre_rollback_$(date '+%Y%m%d_%H%M%S')"
    
    # Use the backup script to create a backup
    if "$SCRIPT_DIR/backup.sh" --compress; then
        success "Pre-rollback backup created"
        echo "$pre_rollback_id"
    else
        error "Failed to create pre-rollback backup"
        return 1
    fi
}

# Stop services gracefully
stop_services() {
    info "Stopping current services..."
    
    cd "$PROJECT_ROOT"
    
    # Stop services with timeout
    if docker-compose -f "$COMPOSE_FILE" down --timeout 30; then
        success "Services stopped successfully"
    else
        warn "Some services may not have stopped gracefully"
    fi
    
    # Wait for containers to fully stop
    local max_wait=60
    local wait_time=0
    
    while docker ps --format "table {{.Names}}" | grep -q "culicidaelab_.*_prod" && [ $wait_time -lt $max_wait ]; do
        info "Waiting for containers to stop... ($wait_time/$max_wait seconds)"
        sleep 5
        wait_time=$((wait_time + 5))
    done
    
    if [ $wait_time -ge $max_wait ]; then
        warn "Containers did not stop within expected time, forcing stop..."
        docker ps --format "table {{.Names}}" | grep "culicidaelab_.*_prod" | xargs -r docker stop
    fi
}

# Restore configuration files
restore_configuration() {
    local backup_path=$1
    
    info "Restoring configuration files..."
    
    # Backup current configuration
    local current_backup_dir="/tmp/current_config_$(date +%s)"
    mkdir -p "$current_backup_dir"
    
    # Backup current files
    for file in ".env.prod" "docker-compose.prod.yml"; do
        if [ -f "$PROJECT_ROOT/$file" ]; then
            cp "$PROJECT_ROOT/$file" "$current_backup_dir/"
        fi
    done
    
    # Restore configuration files from backup
    if [ -d "$backup_path/config" ]; then
        cp -r "$backup_path/config"/* "$PROJECT_ROOT/"
        success "Configuration files restored"
    else
        error "Configuration directory not found in backup"
        return 1
    fi
    
    # Restore nginx configuration if present
    if [ -d "$backup_path/config/nginx" ]; then
        cp -r "$backup_path/config/nginx" "$PROJECT_ROOT/"
        info "Nginx configuration restored"
    fi
    
    # Restore scripts if present
    if [ -d "$backup_path/config/scripts" ]; then
        cp -r "$backup_path/config/scripts" "$PROJECT_ROOT/"
        info "Scripts restored"
    fi
    
    info "Current configuration backed up to: $current_backup_dir"
}

# Restore database
restore_database() {
    local backup_path=$1
    
    info "Restoring database..."
    
    if [ -f "$backup_path/database/culicidaelab.db" ]; then
        # Create a temporary container to restore the database
        info "Restoring database from backup..."
        
        # Ensure the volume exists
        docker volume create backend_data || true
        
        # Restore database to volume
        docker run --rm \
            -v backend_data:/data \
            -v "$backup_path/database":/backup \
            alpine sh -c "
                if [ -f /backup/culicidaelab.db ]; then
                    cp /backup/culicidaelab.db /data/culicidaelab.db
                    echo 'Database restored successfully'
                else
                    echo 'Database file not found in backup'
                    exit 1
                fi
            "
        
        success "Database restored"
    else
        warn "No database backup found, skipping database restore"
    fi
}

# Restore SSL certificates
restore_certificates() {
    local backup_path=$1
    
    info "Restoring SSL certificates..."
    
    # Restore Let's Encrypt certificates from tar.gz
    if [ -f "$backup_path/certificates/letsencrypt.tar.gz" ]; then
        info "Restoring Let's Encrypt certificates..."
        
        # Backup current certificates if they exist
        if [ -d "/etc/letsencrypt" ]; then
            local cert_backup_dir="/tmp/letsencrypt_backup_$(date +%s)"
            mv /etc/letsencrypt "$cert_backup_dir"
            info "Current certificates backed up to: $cert_backup_dir"
        fi
        
        # Extract certificates
        tar -xzf "$backup_path/certificates/letsencrypt.tar.gz" -C /etc/
        success "Let's Encrypt certificates restored"
    fi
    
    # Restore certificate volume if present
    if [ -f "$backup_path/certificates/letsencrypt_volume.tar.gz" ]; then
        info "Restoring certificate volume..."
        
        # Ensure the volume exists
        docker volume create letsencrypt_certs || true
        
        # Restore certificates to volume
        docker run --rm \
            -v letsencrypt_certs:/certs \
            -v "$backup_path/certificates":/backup \
            alpine sh -c "
                if [ -f /backup/letsencrypt_volume.tar.gz ]; then
                    tar -xzf /backup/letsencrypt_volume.tar.gz -C /certs/
                    echo 'Certificate volume restored successfully'
                else
                    echo 'Certificate volume backup not found'
                fi
            "
        
        info "Certificate volume restored"
    fi
    
    if [ ! -f "$backup_path/certificates/letsencrypt.tar.gz" ] && [ ! -f "$backup_path/certificates/letsencrypt_volume.tar.gz" ]; then
        warn "No SSL certificate backups found"
    fi
}

# Restore static files
restore_static_files() {
    local backup_path=$1
    
    info "Restoring static files..."
    
    if [ -f "$backup_path/static/static_files.tar.gz" ]; then
        # Ensure the volume exists
        docker volume create backend_static || true
        
        # Restore static files to volume
        docker run --rm \
            -v backend_static:/static \
            -v "$backup_path/static":/backup \
            alpine sh -c "
                if [ -f /backup/static_files.tar.gz ]; then
                    tar -xzf /backup/static_files.tar.gz -C /static/
                    echo 'Static files restored successfully'
                else
                    echo 'Static files backup not found'
                    exit 1
                fi
            "
        
        success "Static files restored"
    else
        warn "No static files backup found, skipping static files restore"
    fi
}

# Start services
start_services() {
    info "Starting services with restored configuration..."
    
    cd "$PROJECT_ROOT"
    
    # Validate Docker Compose configuration
    if ! docker-compose -f "$COMPOSE_FILE" config &> /dev/null; then
        error "Invalid Docker Compose configuration after restore"
        return 1
    fi
    
    # Start services
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for services to become healthy
    info "Waiting for services to become healthy..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        local healthy_services=$(docker-compose -f "$COMPOSE_FILE" ps | grep -c "Up (healthy)" || echo "0")
        local total_services=$(docker-compose -f "$COMPOSE_FILE" ps | grep -c "Up" || echo "0")
        
        if [ "$healthy_services" -gt 0 ] && [ "$healthy_services" -eq "$total_services" ]; then
            success "All services are healthy"
            break
        fi
        
        attempt=$((attempt + 1))
        info "Waiting for services to become healthy... (attempt $attempt/$max_attempts)"
        sleep 10
    done
    
    if [ $attempt -eq $max_attempts ]; then
        error "Services failed to become healthy within expected time"
        docker-compose -f "$COMPOSE_FILE" ps
        return 1
    fi
}

# Verify rollback
verify_rollback() {
    info "Verifying rollback..."
    
    # Check service status
    info "Checking service status..."
    docker-compose -f "$COMPOSE_FILE" ps
    
    # Test backend health endpoint
    info "Testing backend health endpoint..."
    local max_attempts=10
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f -s "http://localhost/api/health" &> /dev/null; then
            success "Backend health check passed"
            break
        fi
        
        attempt=$((attempt + 1))
        warn "Backend health check failed (attempt $attempt/$max_attempts)"
        sleep 5
    done
    
    if [ $attempt -eq $max_attempts ]; then
        error "Backend health check failed after rollback"
        return 1
    fi
    
    # Test frontend accessibility
    info "Testing frontend accessibility..."
    if curl -f -s "http://localhost/" &> /dev/null; then
        success "Frontend accessibility check passed"
    else
        error "Frontend accessibility check failed after rollback"
        return 1
    fi
    
    success "Rollback verification completed successfully"
}

# Perform dry run
dry_run() {
    local backup_id=$1
    local backup_path="$BACKUP_DIR/$backup_id"
    
    info "Performing dry run for rollback to: $backup_id"
    
    # Extract compressed backup if needed for dry run
    local temp_extracted=false
    if [ -f "$backup_path.tar.gz" ] && [ ! -d "$backup_path" ]; then
        info "Extracting compressed backup for dry run..."
        tar -xzf "$backup_path.tar.gz" -C "$BACKUP_DIR"
        temp_extracted=true
    fi
    
    # Check what would be restored
    info "Files that would be restored:"
    
    if [ -d "$backup_path/config" ]; then
        info "  Configuration files:"
        find "$backup_path/config" -type f | sed 's|^|    |'
    fi
    
    if [ -f "$backup_path/database/culicidaelab.db" ]; then
        local db_size=$(stat -f%z "$backup_path/database/culicidaelab.db" 2>/dev/null || stat -c%s "$backup_path/database/culicidaelab.db" 2>/dev/null)
        info "  Database: culicidaelab.db (${db_size} bytes)"
    fi
    
    if [ -f "$backup_path/certificates/letsencrypt.tar.gz" ]; then
        info "  SSL Certificates: letsencrypt.tar.gz"
    fi
    
    if [ -f "$backup_path/static/static_files.tar.gz" ]; then
        info "  Static files: static_files.tar.gz"
    fi
    
    # Check current vs backup differences
    info "Configuration differences:"
    if [ -f "$backup_path/config/.env.prod" ] && [ -f "$PROJECT_ROOT/.env.prod" ]; then
        if ! diff -q "$backup_path/config/.env.prod" "$PROJECT_ROOT/.env.prod" &> /dev/null; then
            warn "  .env.prod differs from current version"
        else
            info "  .env.prod is identical to current version"
        fi
    fi
    
    # Clean up temporary extraction
    if [ "$temp_extracted" = true ]; then
        rm -rf "$backup_path"
    fi
    
    success "Dry run completed"
}

# Main rollback function
perform_rollback() {
    local backup_id=$1
    local backup_path="$BACKUP_DIR/$backup_id"
    
    info "Starting rollback to backup: $backup_id"
    
    # Extract compressed backup if needed
    local temp_extracted=false
    if [ -f "$backup_path.tar.gz" ] && [ ! -d "$backup_path" ]; then
        info "Extracting compressed backup..."
        tar -xzf "$backup_path.tar.gz" -C "$BACKUP_DIR"
        temp_extracted=true
    fi
    
    # Create pre-rollback backup
    local pre_rollback_backup=$(create_pre_rollback_backup)
    
    # Stop services
    stop_services
    
    # Restore components
    restore_configuration "$backup_path"
    restore_database "$backup_path"
    restore_certificates "$backup_path"
    restore_static_files "$backup_path"
    
    # Start services
    start_services
    
    # Verify rollback
    verify_rollback
    
    # Clean up temporary extraction
    if [ "$temp_extracted" = true ]; then
        rm -rf "$backup_path"
    fi
    
    success "Rollback completed successfully!"
    info "Pre-rollback backup created: $pre_rollback_backup"
}

# Main function
main() {
    local backup_id=""
    local force=false
    local dry_run=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --force)
                force=true
                shift
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 <backup_id> [--force] [--dry-run]"
                echo "  backup_id: ID of the backup to rollback to"
                echo "  --force: Skip confirmation prompts"
                echo "  --dry-run: Show what would be restored without making changes"
                exit 0
                ;;
            -*)
                error "Unknown option: $1"
                exit 1
                ;;
            *)
                if [ -z "$backup_id" ]; then
                    backup_id="$1"
                else
                    error "Multiple backup IDs specified"
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Check if backup ID was provided
    if [ -z "$backup_id" ]; then
        error "Backup ID is required"
        echo "Usage: $0 <backup_id> [--force] [--dry-run]"
        exit 1
    fi
    
    # Create log directory
    mkdir -p "$(dirname "$LOG_FILE")"
    
    info "CulicidaeLab Rollback Script Started"
    info "Timestamp: $(date)"
    info "Target backup: $backup_id"
    
    # Validate backup
    if ! validate_backup "$backup_id"; then
        exit 1
    fi
    
    # Perform dry run if requested
    if [ "$dry_run" = true ]; then
        dry_run "$backup_id"
        exit 0
    fi
    
    # Confirm rollback
    if [ "$force" = false ]; then
        warn "This will rollback the application to backup: $backup_id"
        warn "Current state will be backed up before rollback"
        read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "Rollback cancelled"
            exit 0
        fi
    fi
    
    # Perform rollback
    perform_rollback "$backup_id"
    
    info "Logs available at: $LOG_FILE"
}

# Run main function
main "$@"