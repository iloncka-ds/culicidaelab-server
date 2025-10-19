#!/bin/bash

# CulicidaeLab Production Deployment Script
# This script automates the deployment process for the CulicidaeLab application
# Usage: ./scripts/deploy.sh [--backup] [--rollback <backup_id>] [--force]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="/var/backups/culicidaelab"
LOG_FILE="/var/log/culicidaelab/deployment.log"
COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"

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
        error "Deployment failed with exit code $exit_code"
        error "Check logs at $LOG_FILE for details"
    fi
    exit $exit_code
}

trap cleanup EXIT

# Check prerequisites
check_prerequisites() {
    info "Checking prerequisites..."
    
    # Check if running as root or with sudo
    if [ "$EUID" -ne 0 ]; then
        error "This script must be run as root or with sudo"
        exit 1
    fi
    
    # Check required commands
    local required_commands=("docker" "docker-compose" "curl" "jq")
    for cmd in "${required_commands[@]}"; do
        if ! command -v "$cmd" &> /dev/null; then
            error "Required command '$cmd' not found"
            exit 1
        fi
    done
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    # Check environment file
    if [ ! -f "$PROJECT_ROOT/$ENV_FILE" ]; then
        error "Environment file $ENV_FILE not found"
        exit 1
    fi
    
    # Check compose file
    if [ ! -f "$PROJECT_ROOT/$COMPOSE_FILE" ]; then
        error "Docker Compose file $COMPOSE_FILE not found"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Create backup
create_backup() {
    local backup_id=$(date '+%Y%m%d_%H%M%S')
    local backup_path="$BACKUP_DIR/$backup_id"
    
    info "Creating backup with ID: $backup_id"
    
    # Create backup directory
    mkdir -p "$backup_path"
    
    # Backup database
    if docker ps --format "table {{.Names}}" | grep -q "culicidaelab_backend_prod"; then
        info "Backing up database..."
        docker exec culicidaelab_backend_prod cp /app/data/culicidaelab.db /tmp/backup_db.db 2>/dev/null || true
        docker cp culicidaelab_backend_prod:/tmp/backup_db.db "$backup_path/culicidaelab.db" 2>/dev/null || true
    fi
    
    # Backup configuration files
    info "Backing up configuration files..."
    cp "$PROJECT_ROOT/$ENV_FILE" "$backup_path/"
    cp "$PROJECT_ROOT/$COMPOSE_FILE" "$backup_path/"
    
    # Backup SSL certificates if they exist
    if [ -d "/etc/letsencrypt" ]; then
        info "Backing up SSL certificates..."
        tar -czf "$backup_path/letsencrypt.tar.gz" -C /etc letsencrypt 2>/dev/null || true
    fi
    
    # Create backup metadata
    cat > "$backup_path/metadata.json" << EOF
{
    "backup_id": "$backup_id",
    "timestamp": "$(date -Iseconds)",
    "git_commit": "$(cd "$PROJECT_ROOT" && git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "docker_images": $(docker images --format "{{.Repository}}:{{.Tag}}" | grep culicidaelab | jq -R . | jq -s .)
}
EOF
    
    success "Backup created: $backup_path"
    echo "$backup_id"
}

# Rollback to previous backup
rollback() {
    local backup_id=$1
    local backup_path="$BACKUP_DIR/$backup_id"
    
    if [ ! -d "$backup_path" ]; then
        error "Backup $backup_id not found"
        exit 1
    fi
    
    warn "Rolling back to backup: $backup_id"
    
    # Stop current services
    info "Stopping current services..."
    cd "$PROJECT_ROOT"
    docker-compose -f "$COMPOSE_FILE" down || true
    
    # Restore configuration files
    info "Restoring configuration files..."
    cp "$backup_path/$ENV_FILE" "$PROJECT_ROOT/"
    cp "$backup_path/$COMPOSE_FILE" "$PROJECT_ROOT/"
    
    # Restore database
    if [ -f "$backup_path/culicidaelab.db" ]; then
        info "Restoring database..."
        # Create temporary container to restore database
        docker run --rm -v backend_data:/data -v "$backup_path":/backup alpine cp /backup/culicidaelab.db /data/
    fi
    
    # Restore SSL certificates
    if [ -f "$backup_path/letsencrypt.tar.gz" ]; then
        info "Restoring SSL certificates..."
        tar -xzf "$backup_path/letsencrypt.tar.gz" -C /etc/
    fi
    
    # Start services with restored configuration
    info "Starting services with restored configuration..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    success "Rollback completed successfully"
}

# Pre-deployment health checks
pre_deployment_checks() {
    info "Running pre-deployment health checks..."
    
    # Check disk space
    local available_space=$(df / | awk 'NR==2 {print $4}')
    local required_space=1048576  # 1GB in KB
    
    if [ "$available_space" -lt "$required_space" ]; then
        error "Insufficient disk space. Available: ${available_space}KB, Required: ${required_space}KB"
        exit 1
    fi
    
    # Check memory
    local available_memory=$(free | awk 'NR==2{printf "%.0f", $7/1024}')
    local required_memory=512  # 512MB
    
    if [ "$available_memory" -lt "$required_memory" ]; then
        warn "Low available memory. Available: ${available_memory}MB, Recommended: ${required_memory}MB"
    fi
    
    # Validate Docker Compose configuration
    info "Validating Docker Compose configuration..."
    cd "$PROJECT_ROOT"
    if ! docker-compose -f "$COMPOSE_FILE" config &> /dev/null; then
        error "Invalid Docker Compose configuration"
        exit 1
    fi
    
    # Check if ports are available
    local ports=("80" "443")
    for port in "${ports[@]}"; do
        if netstat -tuln | grep -q ":$port "; then
            warn "Port $port is already in use"
        fi
    done
    
    success "Pre-deployment checks passed"
}

# Deploy application
deploy() {
    info "Starting deployment process..."
    
    cd "$PROJECT_ROOT"
    
    # Pull latest images
    info "Pulling latest Docker images..."
    docker-compose -f "$COMPOSE_FILE" pull
    
    # Build custom images
    info "Building application images..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    # Stop existing services gracefully
    info "Stopping existing services..."
    docker-compose -f "$COMPOSE_FILE" down --timeout 30
    
    # Start services
    info "Starting services..."
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for services to be healthy
    info "Waiting for services to become healthy..."
    local max_attempts=30
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up (healthy)"; then
            break
        fi
        
        attempt=$((attempt + 1))
        info "Waiting for services... (attempt $attempt/$max_attempts)"
        sleep 10
    done
    
    if [ $attempt -eq $max_attempts ]; then
        error "Services failed to become healthy within expected time"
        exit 1
    fi
    
    success "Deployment completed successfully"
}

# Post-deployment verification
post_deployment_checks() {
    info "Running post-deployment verification..."
    
    # Check service status
    info "Checking service status..."
    docker-compose -f "$COMPOSE_FILE" ps
    
    # Test backend health endpoint
    info "Testing backend health endpoint..."
    local backend_health_url="http://localhost/api/health"
    local max_attempts=10
    local attempt=0
    
    while [ $attempt -lt $max_attempts ]; do
        if curl -f -s "$backend_health_url" &> /dev/null; then
            success "Backend health check passed"
            break
        fi
        
        attempt=$((attempt + 1))
        warn "Backend health check failed (attempt $attempt/$max_attempts)"
        sleep 5
    done
    
    if [ $attempt -eq $max_attempts ]; then
        error "Backend health check failed"
        exit 1
    fi
    
    # Test frontend accessibility
    info "Testing frontend accessibility..."
    if curl -f -s "http://localhost/" &> /dev/null; then
        success "Frontend accessibility check passed"
    else
        error "Frontend accessibility check failed"
        exit 1
    fi
    
    # Check SSL certificate if HTTPS is configured
    source "$PROJECT_ROOT/$ENV_FILE"
    if [ -n "${DOMAIN_NAME:-}" ]; then
        info "Testing SSL certificate..."
        if curl -f -s "https://$DOMAIN_NAME/" &> /dev/null; then
            success "SSL certificate check passed"
        else
            warn "SSL certificate check failed - this is normal for new deployments"
        fi
    fi
    
    success "Post-deployment verification completed"
}

# Clean up old Docker resources
cleanup_docker() {
    info "Cleaning up old Docker resources..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes (be careful with this)
    docker volume prune -f
    
    # Remove unused networks
    docker network prune -f
    
    success "Docker cleanup completed"
}

# Main deployment function
main() {
    local backup_only=false
    local rollback_id=""
    local force=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --backup)
                backup_only=true
                shift
                ;;
            --rollback)
                rollback_id="$2"
                shift 2
                ;;
            --force)
                force=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [--backup] [--rollback <backup_id>] [--force]"
                echo "  --backup: Create backup only, don't deploy"
                echo "  --rollback <backup_id>: Rollback to specified backup"
                echo "  --force: Skip confirmation prompts"
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
    
    info "CulicidaeLab Deployment Script Started"
    info "Timestamp: $(date)"
    info "User: $(whoami)"
    info "Working directory: $PROJECT_ROOT"
    
    # Check prerequisites
    check_prerequisites
    
    # Handle rollback
    if [ -n "$rollback_id" ]; then
        if [ "$force" = false ]; then
            read -p "Are you sure you want to rollback to $rollback_id? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                info "Rollback cancelled"
                exit 0
            fi
        fi
        rollback "$rollback_id"
        exit 0
    fi
    
    # Create backup
    local backup_id=$(create_backup)
    
    # If backup only, exit here
    if [ "$backup_only" = true ]; then
        info "Backup completed. Backup ID: $backup_id"
        exit 0
    fi
    
    # Confirm deployment
    if [ "$force" = false ]; then
        read -p "Proceed with deployment? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            info "Deployment cancelled"
            exit 0
        fi
    fi
    
    # Run deployment
    pre_deployment_checks
    deploy
    post_deployment_checks
    cleanup_docker
    
    success "Deployment completed successfully!"
    info "Backup ID: $backup_id (use for rollback if needed)"
    info "Logs available at: $LOG_FILE"
}

# Run main function
main "$@"