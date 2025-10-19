#!/bin/bash

# nginx-certbot-renew.sh - Certificate renewal script for nginx with certbot
# This script is typically run by cron to automatically renew SSL certificates

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠${NC} $1"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ✗${NC} $1"
}

# Environment variables
DOMAIN=${DOMAIN:-localhost}
RENEWAL_LOG="/var/log/letsencrypt/renewal.log"

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$RENEWAL_LOG")"

log "Starting certificate renewal check for $DOMAIN..."

# Function to check if nginx is running
check_nginx() {
    if pgrep nginx > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to reload nginx configuration
reload_nginx() {
    log "Reloading nginx configuration..."
    
    if check_nginx; then
        if nginx -s reload; then
            log_success "nginx configuration reloaded"
            return 0
        else
            log_error "Failed to reload nginx configuration"
            return 1
        fi
    else
        log_warning "nginx is not running, skipping reload"
        return 0
    fi
}

# Function to test nginx configuration
test_nginx_config() {
    log "Testing nginx configuration..."
    
    if nginx -t >/dev/null 2>&1; then
        log_success "nginx configuration is valid"
        return 0
    else
        log_error "nginx configuration test failed"
        return 1
    fi
}

# Function to renew certificates
renew_certificates() {
    log "Attempting to renew certificates..."
    
    # Run certbot renewal
    if certbot renew --quiet --no-self-upgrade --webroot --webroot-path=/var/www/certbot; then
        log_success "Certificate renewal completed successfully"
        
        # Test nginx configuration before reloading
        if test_nginx_config; then
            reload_nginx
        else
            log_error "nginx configuration test failed after renewal, not reloading"
            return 1
        fi
        
        return 0
    else
        local exit_code=$?
        if [[ $exit_code -eq 0 ]]; then
            log "No certificates were due for renewal"
            return 0
        else
            log_error "Certificate renewal failed with exit code $exit_code"
            return 1
        fi
    fi
}

# Function to check certificate expiration
check_certificate_expiration() {
    local domain=$1
    local cert_path="/etc/letsencrypt/live/$domain/fullchain.pem"
    
    if [[ -f "$cert_path" ]]; then
        local expiry_date=$(openssl x509 -enddate -noout -in "$cert_path" | cut -d= -f2)
        local expiry_epoch=$(date -d "$expiry_date" +%s)
        local current_epoch=$(date +%s)
        local days_until_expiry=$(( (expiry_epoch - current_epoch) / 86400 ))
        
        log "Certificate for $domain expires in $days_until_expiry days"
        
        if [[ $days_until_expiry -lt 30 ]]; then
            log_warning "Certificate for $domain expires in less than 30 days"
            return 1
        else
            log_success "Certificate for $domain is valid for $days_until_expiry more days"
            return 0
        fi
    else
        log_warning "No certificate found for $domain"
        return 1
    fi
}

# Function to send notification (placeholder for future email notifications)
send_notification() {
    local subject=$1
    local message=$2
    
    # Log the notification (could be extended to send emails)
    log "NOTIFICATION: $subject - $message"
}

# Main renewal process
main() {
    log "Certificate renewal script started"
    
    # Skip renewal for localhost or IP addresses
    if [[ "$DOMAIN" == "localhost" || "$DOMAIN" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log "Domain is localhost or IP address, skipping Let's Encrypt renewal"
        exit 0
    fi
    
    # Check if certificates exist
    if [[ ! -d "/etc/letsencrypt/live/$DOMAIN" ]]; then
        log_warning "No certificates found for $DOMAIN, skipping renewal"
        exit 0
    fi
    
    # Check certificate expiration
    if check_certificate_expiration "$DOMAIN"; then
        log "Certificate is still valid, no renewal needed"
        exit 0
    fi
    
    # Attempt renewal
    if renew_certificates; then
        log_success "Certificate renewal process completed successfully"
        send_notification "SSL Certificate Renewed" "Certificate for $DOMAIN has been successfully renewed"
    else
        log_error "Certificate renewal process failed"
        send_notification "SSL Certificate Renewal Failed" "Failed to renew certificate for $DOMAIN"
        exit 1
    fi
    
    log "Certificate renewal script completed"
}

# Run main function and log output
main "$@" 2>&1 | tee -a "$RENEWAL_LOG"