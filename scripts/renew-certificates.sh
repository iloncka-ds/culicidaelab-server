#!/bin/bash

# Certificate renewal script for Let's Encrypt SSL certificates
# This script handles automatic certificate renewal with nginx reload

set -e

# Configuration
DATA_PATH="./certbot"
LOG_FILE="$DATA_PATH/logs/renewal.log"
EMAIL_NOTIFICATIONS=${EMAIL_NOTIFICATIONS:-1}
NOTIFICATION_EMAIL=${NOTIFICATION_EMAIL:-"admin@example.com"}
RENEWAL_THRESHOLD=${RENEWAL_THRESHOLD:-30}  # Days before expiry to renew

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function with file output
log() {
    local message="[$(date +'%Y-%m-%d %H:%M:%S')] $1"
    echo -e "${GREEN}$message${NC}"
    echo "$message" >> "$LOG_FILE"
}

warn() {
    local message="[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1"
    echo -e "${YELLOW}$message${NC}"
    echo "$message" >> "$LOG_FILE"
}

error() {
    local message="[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1"
    echo -e "${RED}$message${NC}"
    echo "$message" >> "$LOG_FILE"
}

# Create log directory if it doesn't exist
setup_logging() {
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Rotate log file if it's too large (>10MB)
    if [ -f "$LOG_FILE" ] && [ $(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null || echo 0) -gt 10485760 ]; then
        mv "$LOG_FILE" "$LOG_FILE.old"
        log "Log file rotated"
    fi
}

# Check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        error "docker-compose is not installed or not in PATH"
        return 1
    fi
    
    if ! docker-compose ps &> /dev/null; then
        error "Docker Compose services are not running"
        return 1
    fi
    
    return 0
}

# Get certificate expiry date
get_cert_expiry() {
    local cert_path="$1"
    
    if [ ! -f "$cert_path" ]; then
        echo "0"
        return
    fi
    
    local expiry_date=$(openssl x509 -in "$cert_path" -noout -enddate 2>/dev/null | cut -d= -f2)
    if [ -n "$expiry_date" ]; then
        date -d "$expiry_date" +%s 2>/dev/null || date -j -f "%b %d %T %Y %Z" "$expiry_date" +%s 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

# Check if certificate needs renewal
needs_renewal() {
    local cert_path="$1"
    local threshold_days="$2"
    
    local expiry_timestamp=$(get_cert_expiry "$cert_path")
    local current_timestamp=$(date +%s)
    local threshold_timestamp=$((current_timestamp + threshold_days * 86400))
    
    if [ "$expiry_timestamp" -le "$threshold_timestamp" ]; then
        return 0  # Needs renewal
    else
        return 1  # Does not need renewal
    fi
}

# List all certificates and their status
check_certificate_status() {
    log "Checking certificate status..."
    
    local renewal_needed=0
    
    if [ ! -d "$DATA_PATH/conf/live" ]; then
        warn "No certificates found in $DATA_PATH/conf/live"
        return 1
    fi
    
    for domain_dir in "$DATA_PATH/conf/live"/*; do
        if [ ! -d "$domain_dir" ]; then
            continue
        fi
        
        local domain=$(basename "$domain_dir")
        local cert_path="$domain_dir/fullchain.pem"
        
        if [ ! -f "$cert_path" ]; then
            warn "Certificate file not found for domain: $domain"
            continue
        fi
        
        local expiry_timestamp=$(get_cert_expiry "$cert_path")
        local current_timestamp=$(date +%s)
        local days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))
        
        if [ "$expiry_timestamp" -eq 0 ]; then
            error "Could not read expiry date for domain: $domain"
            continue
        fi
        
        log "Domain: $domain"
        log "  Certificate expires in: $days_until_expiry days"
        log "  Expiry date: $(date -d "@$expiry_timestamp" 2>/dev/null || date -r "$expiry_timestamp" 2>/dev/null)"
        
        if needs_renewal "$cert_path" "$RENEWAL_THRESHOLD"; then
            warn "  Certificate needs renewal (threshold: $RENEWAL_THRESHOLD days)"
            renewal_needed=1
        else
            log "  Certificate is valid"
        fi
    done
    
    return $renewal_needed
}

# Perform certificate renewal
renew_certificates() {
    log "Starting certificate renewal process..."
    
    # Run certbot renewal
    if docker-compose run --rm --entrypoint "\
        certbot renew \
        --webroot -w /var/www/certbot \
        --email $NOTIFICATION_EMAIL \
        --no-eff-email \
        --keep-until-expiring \
        --quiet" certbot; then
        
        log "Certificate renewal completed successfully"
        return 0
    else
        error "Certificate renewal failed"
        return 1
    fi
}

# Reload nginx after successful renewal
reload_nginx() {
    log "Reloading nginx configuration..."
    
    # Test nginx configuration first
    if docker-compose exec nginx nginx -t; then
        log "Nginx configuration test passed"
    else
        error "Nginx configuration test failed"
        return 1
    fi
    
    # Reload nginx
    if docker-compose exec nginx nginx -s reload; then
        log "Nginx reloaded successfully"
        return 0
    else
        error "Failed to reload nginx"
        return 1
    fi
}

# Send email notification
send_notification() {
    local subject="$1"
    local message="$2"
    local status="$3"  # success, warning, error
    
    if [ "$EMAIL_NOTIFICATIONS" != "1" ]; then
        return 0
    fi
    
    # Create email content
    local email_content="Subject: $subject

$message

---
Certificate Renewal Service
$(date)
Server: $(hostname)
"
    
    # Try to send email using available methods
    if command -v mail &> /dev/null; then
        echo "$email_content" | mail -s "$subject" "$NOTIFICATION_EMAIL"
        log "Email notification sent to $NOTIFICATION_EMAIL"
    elif command -v sendmail &> /dev/null; then
        echo "$email_content" | sendmail "$NOTIFICATION_EMAIL"
        log "Email notification sent to $NOTIFICATION_EMAIL"
    else
        warn "No mail command available for notifications"
        # Log the notification content instead
        log "NOTIFICATION: $subject - $message"
    fi
}

# Main renewal process
perform_renewal() {
    local renewal_attempted=0
    local renewal_successful=0
    
    # Check if any certificates need renewal
    if check_certificate_status; then
        log "No certificates need renewal at this time"
        return 0
    fi
    
    log "Certificate renewal is needed"
    renewal_attempted=1
    
    # Perform the renewal
    if renew_certificates; then
        renewal_successful=1
        log "Certificate renewal successful"
        
        # Reload nginx
        if reload_nginx; then
            log "Nginx reload successful"
            send_notification "SSL Certificate Renewal Successful" \
                "SSL certificates have been successfully renewed and nginx has been reloaded." \
                "success"
        else
            error "Nginx reload failed after certificate renewal"
            send_notification "SSL Certificate Renewal Warning" \
                "SSL certificates were renewed successfully, but nginx reload failed. Manual intervention may be required." \
                "warning"
            return 1
        fi
    else
        error "Certificate renewal failed"
        send_notification "SSL Certificate Renewal Failed" \
            "SSL certificate renewal failed. Please check the logs and renew manually if necessary." \
            "error"
        return 1
    fi
    
    return 0
}

# Cleanup old log files
cleanup_logs() {
    local log_dir="$(dirname "$LOG_FILE")"
    
    # Remove log files older than 90 days
    find "$log_dir" -name "*.log*" -type f -mtime +90 -delete 2>/dev/null || true
    
    # Keep only the last 10 rotated log files
    ls -t "$log_dir"/*.log.* 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
}

# Health check function
health_check() {
    log "Performing health check..."
    
    if ! check_docker_compose; then
        error "Docker Compose health check failed"
        return 1
    fi
    
    # Check if nginx is responding
    if docker-compose exec nginx curl -f http://localhost/health &>/dev/null; then
        log "Nginx health check passed"
    else
        warn "Nginx health check failed"
    fi
    
    # Check certificate status
    check_certificate_status
    
    log "Health check completed"
}

# Main function
main() {
    local command="${1:-renew}"
    
    setup_logging
    
    case "$command" in
        "renew")
            log "Starting certificate renewal check..."
            
            if ! check_docker_compose; then
                error "Docker Compose is not available"
                exit 1
            fi
            
            perform_renewal
            cleanup_logs
            ;;
        "status")
            log "Checking certificate status..."
            check_certificate_status
            ;;
        "health")
            health_check
            ;;
        "force-renew")
            log "Forcing certificate renewal..."
            RENEWAL_THRESHOLD=365  # Force renewal regardless of expiry
            perform_renewal
            ;;
        *)
            echo "Usage: $0 [renew|status|health|force-renew]"
            echo "  renew       - Check and renew certificates if needed (default)"
            echo "  status      - Show certificate status"
            echo "  health      - Perform health check"
            echo "  force-renew - Force certificate renewal"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"