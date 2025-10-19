#!/bin/bash

# CulicidaeLab Health Check Script
# This script performs comprehensive health checks for the CulicidaeLab application
# Usage: ./scripts/health-check.sh [--verbose] [--json] [--timeout <seconds>]

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="/var/log/culicidaelab/health-check.log"
DEFAULT_TIMEOUT=30

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global variables
VERBOSE=false
JSON_OUTPUT=false
TIMEOUT=$DEFAULT_TIMEOUT
HEALTH_STATUS=0
HEALTH_RESULTS=()

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    if [ "$JSON_OUTPUT" = false ]; then
        echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
    fi
}

info() { 
    if [ "$VERBOSE" = true ] || [ "$JSON_OUTPUT" = false ]; then
        log "INFO" "${BLUE}$*${NC}"
    fi
}
warn() { log "WARN" "${YELLOW}$*${NC}"; }
error() { log "ERROR" "${RED}$*${NC}"; }
success() { log "SUCCESS" "${GREEN}$*${NC}"; }

# Add health check result
add_result() {
    local service=$1
    local check=$2
    local status=$3
    local message=$4
    local response_time=${5:-"N/A"}
    
    HEALTH_RESULTS+=("{\"service\":\"$service\",\"check\":\"$check\",\"status\":\"$status\",\"message\":\"$message\",\"response_time\":\"$response_time\",\"timestamp\":\"$(date -Iseconds)\"}")
    
    if [ "$status" != "healthy" ]; then
        HEALTH_STATUS=1
    fi
}

# Check Docker daemon
check_docker() {
    info "Checking Docker daemon..."
    
    if docker info &> /dev/null; then
        add_result "docker" "daemon" "healthy" "Docker daemon is running"
        success "Docker daemon is running"
    else
        add_result "docker" "daemon" "unhealthy" "Docker daemon is not running"
        error "Docker daemon is not running"
    fi
}

# Check Docker Compose services
check_compose_services() {
    info "Checking Docker Compose services..."
    
    cd "$PROJECT_ROOT"
    
    # Check if compose file exists
    if [ ! -f "docker-compose.prod.yml" ]; then
        add_result "compose" "file" "unhealthy" "docker-compose.prod.yml not found"
        error "docker-compose.prod.yml not found"
        return
    fi
    
    # Get service status
    local services=("backend" "frontend" "nginx" "certbot")
    
    for service in "${services[@]}"; do
        local container_name="culicidaelab_${service}_prod"
        
        if docker ps --format "table {{.Names}}" | grep -q "$container_name"; then
            # Check if container is healthy
            local health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "no-healthcheck")
            
            case $health_status in
                "healthy")
                    add_result "$service" "container" "healthy" "Container is running and healthy"
                    success "$service container is healthy"
                    ;;
                "unhealthy")
                    add_result "$service" "container" "unhealthy" "Container is running but unhealthy"
                    error "$service container is unhealthy"
                    ;;
                "starting")
                    add_result "$service" "container" "starting" "Container is starting up"
                    warn "$service container is starting"
                    ;;
                "no-healthcheck")
                    # Check if container is just running
                    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep "$container_name" | grep -q "Up"; then
                        add_result "$service" "container" "running" "Container is running (no health check configured)"
                        info "$service container is running (no health check)"
                    else
                        add_result "$service" "container" "unhealthy" "Container is not running properly"
                        error "$service container is not running properly"
                    fi
                    ;;
                *)
                    add_result "$service" "container" "unknown" "Unknown health status: $health_status"
                    warn "$service container has unknown health status: $health_status"
                    ;;
            esac
        else
            add_result "$service" "container" "unhealthy" "Container is not running"
            error "$service container is not running"
        fi
    done
}

# Check backend API health
check_backend_api() {
    info "Checking backend API health..."
    
    local start_time=$(date +%s.%N)
    local health_url="http://localhost/api/health"
    
    if curl -f -s --max-time "$TIMEOUT" "$health_url" &> /dev/null; then
        local end_time=$(date +%s.%N)
        local response_time=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "N/A")
        
        add_result "backend" "api_health" "healthy" "API health endpoint is responding" "${response_time}s"
        success "Backend API health endpoint is responding"
        
        # Try to get detailed health info
        local health_response=$(curl -s --max-time "$TIMEOUT" "$health_url" 2>/dev/null || echo "{}")
        if echo "$health_response" | jq . &> /dev/null; then
            info "Backend health details: $health_response"
        fi
    else
        add_result "backend" "api_health" "unhealthy" "API health endpoint is not responding"
        error "Backend API health endpoint is not responding"
    fi
}

# Check frontend accessibility
check_frontend() {
    info "Checking frontend accessibility..."
    
    local start_time=$(date +%s.%N)
    local frontend_url="http://localhost/"
    
    if curl -f -s --max-time "$TIMEOUT" "$frontend_url" &> /dev/null; then
        local end_time=$(date +%s.%N)
        local response_time=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "N/A")
        
        add_result "frontend" "accessibility" "healthy" "Frontend is accessible" "${response_time}s"
        success "Frontend is accessible"
    else
        add_result "frontend" "accessibility" "unhealthy" "Frontend is not accessible"
        error "Frontend is not accessible"
    fi
}

# Check SSL certificate
check_ssl_certificate() {
    info "Checking SSL certificate..."
    
    # Load environment variables
    if [ -f "$PROJECT_ROOT/.env.prod" ]; then
        source "$PROJECT_ROOT/.env.prod"
    fi
    
    if [ -z "${DOMAIN_NAME:-}" ]; then
        add_result "ssl" "certificate" "skipped" "No domain name configured"
        warn "No domain name configured, skipping SSL check"
        return
    fi
    
    # Check if certificate files exist
    local cert_path="/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem"
    local key_path="/etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem"
    
    if [ -f "$cert_path" ] && [ -f "$key_path" ]; then
        # Check certificate expiration
        local expiry_date=$(openssl x509 -enddate -noout -in "$cert_path" 2>/dev/null | cut -d= -f2)
        local expiry_timestamp=$(date -d "$expiry_date" +%s 2>/dev/null || echo "0")
        local current_timestamp=$(date +%s)
        local days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))
        
        if [ "$days_until_expiry" -gt 30 ]; then
            add_result "ssl" "certificate" "healthy" "Certificate is valid and expires in $days_until_expiry days"
            success "SSL certificate is valid (expires in $days_until_expiry days)"
        elif [ "$days_until_expiry" -gt 0 ]; then
            add_result "ssl" "certificate" "warning" "Certificate expires soon in $days_until_expiry days"
            warn "SSL certificate expires soon ($days_until_expiry days)"
        else
            add_result "ssl" "certificate" "unhealthy" "Certificate has expired"
            error "SSL certificate has expired"
        fi
        
        # Test HTTPS connectivity
        if curl -f -s --max-time "$TIMEOUT" "https://$DOMAIN_NAME/" &> /dev/null; then
            add_result "ssl" "https_connectivity" "healthy" "HTTPS connectivity is working"
            success "HTTPS connectivity is working"
        else
            add_result "ssl" "https_connectivity" "unhealthy" "HTTPS connectivity is not working"
            error "HTTPS connectivity is not working"
        fi
    else
        add_result "ssl" "certificate" "unhealthy" "Certificate files not found"
        error "SSL certificate files not found"
    fi
}

# Check database connectivity
check_database() {
    info "Checking database connectivity..."
    
    # Check if backend container is running
    if docker ps --format "table {{.Names}}" | grep -q "culicidaelab_backend_prod"; then
        # Test database connection through backend container
        local db_test_result=$(docker exec culicidaelab_backend_prod python -c "
import sqlite3
import sys
try:
    conn = sqlite3.connect('/app/data/culicidaelab.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\";')
    tables = cursor.fetchall()
    conn.close()
    print(f'Database accessible with {len(tables)} tables')
    sys.exit(0)
except Exception as e:
    print(f'Database error: {e}')
    sys.exit(1)
" 2>&1)
        
        local exit_code=$?
        
        if [ $exit_code -eq 0 ]; then
            add_result "database" "connectivity" "healthy" "$db_test_result"
            success "Database connectivity: $db_test_result"
        else
            add_result "database" "connectivity" "unhealthy" "$db_test_result"
            error "Database connectivity failed: $db_test_result"
        fi
    else
        add_result "database" "connectivity" "unhealthy" "Backend container not running"
        error "Cannot check database - backend container not running"
    fi
}

# Check disk space
check_disk_space() {
    info "Checking disk space..."
    
    local root_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    local available_space=$(df / | awk 'NR==2 {print $4}')
    
    if [ "$root_usage" -lt 80 ]; then
        add_result "system" "disk_space" "healthy" "Disk usage is ${root_usage}% (${available_space}KB available)"
        success "Disk usage is acceptable (${root_usage}%)"
    elif [ "$root_usage" -lt 90 ]; then
        add_result "system" "disk_space" "warning" "Disk usage is ${root_usage}% (${available_space}KB available)"
        warn "Disk usage is high (${root_usage}%)"
    else
        add_result "system" "disk_space" "unhealthy" "Disk usage is ${root_usage}% (${available_space}KB available)"
        error "Disk usage is critical (${root_usage}%)"
    fi
}

# Check memory usage
check_memory() {
    info "Checking memory usage..."
    
    local memory_info=$(free | awk 'NR==2{printf "%.0f %.0f %.0f", $3/1024, $2/1024, ($2-$3)/1024}')
    local used_mb=$(echo "$memory_info" | cut -d' ' -f1)
    local total_mb=$(echo "$memory_info" | cut -d' ' -f2)
    local available_mb=$(echo "$memory_info" | cut -d' ' -f3)
    local usage_percent=$(echo "scale=0; $used_mb * 100 / $total_mb" | bc)
    
    if [ "$usage_percent" -lt 80 ]; then
        add_result "system" "memory" "healthy" "Memory usage is ${usage_percent}% (${available_mb}MB available)"
        success "Memory usage is acceptable (${usage_percent}%)"
    elif [ "$usage_percent" -lt 90 ]; then
        add_result "system" "memory" "warning" "Memory usage is ${usage_percent}% (${available_mb}MB available)"
        warn "Memory usage is high (${usage_percent}%)"
    else
        add_result "system" "memory" "unhealthy" "Memory usage is ${usage_percent}% (${available_mb}MB available)"
        error "Memory usage is critical (${usage_percent}%)"
    fi
}

# Check Docker volumes
check_volumes() {
    info "Checking Docker volumes..."
    
    local required_volumes=("backend_data" "backend_static" "letsencrypt_certs")
    
    for volume in "${required_volumes[@]}"; do
        if docker volume ls | grep -q "$volume"; then
            add_result "docker" "volume_$volume" "healthy" "Volume $volume exists"
            success "Volume $volume exists"
        else
            add_result "docker" "volume_$volume" "unhealthy" "Volume $volume is missing"
            error "Volume $volume is missing"
        fi
    done
}

# Check network connectivity
check_network() {
    info "Checking network connectivity..."
    
    # Check if Docker network exists
    if docker network ls | grep -q "culicidaelab_network"; then
        add_result "docker" "network" "healthy" "Docker network exists"
        success "Docker network exists"
    else
        add_result "docker" "network" "unhealthy" "Docker network is missing"
        error "Docker network is missing"
    fi
    
    # Check external connectivity
    if ping -c 1 8.8.8.8 &> /dev/null; then
        add_result "system" "external_connectivity" "healthy" "External network connectivity is working"
        success "External network connectivity is working"
    else
        add_result "system" "external_connectivity" "unhealthy" "External network connectivity failed"
        error "External network connectivity failed"
    fi
}

# Generate JSON output
generate_json_output() {
    local overall_status="healthy"
    if [ $HEALTH_STATUS -ne 0 ]; then
        overall_status="unhealthy"
    fi
    
    local results_json=$(printf '%s\n' "${HEALTH_RESULTS[@]}" | jq -s .)
    
    cat << EOF
{
    "timestamp": "$(date -Iseconds)",
    "overall_status": "$overall_status",
    "checks_performed": ${#HEALTH_RESULTS[@]},
    "results": $results_json
}
EOF
}

# Generate summary report
generate_summary() {
    local total_checks=${#HEALTH_RESULTS[@]}
    local healthy_checks=0
    local warning_checks=0
    local unhealthy_checks=0
    
    for result in "${HEALTH_RESULTS[@]}"; do
        local status=$(echo "$result" | jq -r '.status')
        case $status in
            "healthy"|"running") healthy_checks=$((healthy_checks + 1)) ;;
            "warning"|"starting") warning_checks=$((warning_checks + 1)) ;;
            "unhealthy") unhealthy_checks=$((unhealthy_checks + 1)) ;;
        esac
    done
    
    echo
    echo "=== Health Check Summary ==="
    echo "Total checks: $total_checks"
    echo "Healthy: $healthy_checks"
    echo "Warnings: $warning_checks"
    echo "Unhealthy: $unhealthy_checks"
    echo
    
    if [ $HEALTH_STATUS -eq 0 ]; then
        success "Overall status: HEALTHY"
    else
        error "Overall status: UNHEALTHY"
    fi
}

# Main function
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --verbose)
                VERBOSE=true
                shift
                ;;
            --json)
                JSON_OUTPUT=true
                shift
                ;;
            --timeout)
                TIMEOUT="$2"
                shift 2
                ;;
            -h|--help)
                echo "Usage: $0 [--verbose] [--json] [--timeout <seconds>]"
                echo "  --verbose: Enable verbose output"
                echo "  --json: Output results in JSON format"
                echo "  --timeout: Set timeout for HTTP checks (default: $DEFAULT_TIMEOUT)"
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
    
    if [ "$JSON_OUTPUT" = false ]; then
        info "CulicidaeLab Health Check Started"
        info "Timestamp: $(date)"
    fi
    
    # Run health checks
    check_docker
    check_compose_services
    check_backend_api
    check_frontend
    check_ssl_certificate
    check_database
    check_disk_space
    check_memory
    check_volumes
    check_network
    
    # Output results
    if [ "$JSON_OUTPUT" = true ]; then
        generate_json_output
    else
        generate_summary
    fi
    
    exit $HEALTH_STATUS
}

# Run main function
main "$@"