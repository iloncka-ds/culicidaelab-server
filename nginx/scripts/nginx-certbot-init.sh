#!/bin/bash

# Initialization script for nginx container with certbot integration
# This script can be run to manually initialize or re-initialize SSL certificates

set -e

# Configuration from environment variables
DOMAIN_NAME=${DOMAIN_NAME:-"localhost"}
EMAIL=${EMAIL:-"admin@example.com"}
STAGING=${STAGING:-0}
RSA_KEY_SIZE=${RSA_KEY_SIZE:-4096}
FORCE=${FORCE:-0}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] nginx-certbot-init: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] nginx-certbot-init: WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] nginx-certbot-init: ERROR: $1${NC}"
}

# Validate configuration
validate_config() {
    log "Validating configuration..."
    
    if [ "$DOMAIN_NAME" = "localhost" ]; then
        error "Cannot initialize SSL certificates for localhost domain"
        exit 1
    fi
    
    if ! echo "$EMAIL" | grep -E '^[^@]+@[^@]+\.[^@]+$' > /dev/null; then
        error "Invalid email format: $EMAIL"
        exit 1
    fi
    
    log "Configuration validated successfully"
}

# Check if certificates already exist
check_existing_certificates() {
    local cert_dir="/etc/letsencrypt/live/$DOMAIN_NAME"
    
    if [ -d "$cert_dir" ] && [ -f "$cert_dir/fullchain.pem" ]; then
        if [ "$FORCE" != "1" ]; then
            warn "Certificates for $DOMAIN_NAME already exist"
            read -p "Do you want to recreate them? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                log "Keeping existing certificates"
                return 1
            fi
        fi
        log "Removing existing certificates..."
        rm -rf "$cert_dir"
    fi
    
    return 0
}

# Download recommended TLS parameters
download_tls_params() {
    log "Downloading recommended TLS parameters..."
    
    local ssl_dir="/etc/letsencrypt"
    
    if [ ! -f "$ssl_dir/options-ssl-nginx.conf" ]; then
        curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf \
            > "$ssl_dir/options-ssl-nginx.conf"
        log "Downloaded options-ssl-nginx.conf"
    fi
    
    if [ ! -f "$ssl_dir/ssl-dhparams.pem" ]; then
        curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem \
            > "$ssl_dir/ssl-dhparams.pem"
        log "Downloaded ssl-dhparams.pem"
    fi
}

# Request SSL certificates
request_certificates() {
    log "Requesting SSL certificates for $DOMAIN_NAME..."
    
    # Build certbot command
    local certbot_args="certonly --webroot -w /var/www/certbot"
    certbot_args="$certbot_args -d $DOMAIN_NAME"
    certbot_args="$certbot_args --email $EMAIL"
    certbot_args="$certbot_args --rsa-key-size $RSA_KEY_SIZE"
    certbot_args="$certbot_args --agree-tos"
    certbot_args="$certbot_args --non-interactive"
    
    if [ "$STAGING" != "0" ]; then
        certbot_args="$certbot_args --staging"
        warn "Using Let's Encrypt staging server"
    fi
    
    # Request certificate
    if certbot $certbot_args; then
        log "SSL certificates obtained successfully"
        
        # Create chain.pem for OCSP stapling
        cp "/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem" \
           "/etc/letsencrypt/live/$DOMAIN_NAME/chain.pem"
        
        return 0
    else
        error "Failed to obtain SSL certificates"
        return 1
    fi
}

# Verify certificates
verify_certificates() {
    local cert_file="/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem"
    
    log "Verifying SSL certificates..."
    
    if [ ! -f "$cert_file" ]; then
        error "Certificate file not found: $cert_file"
        return 1
    fi
    
    if openssl x509 -in "$cert_file" -text -noout > /dev/null 2>&1; then
        local expiry_date=$(openssl x509 -in "$cert_file" -noout -dates | grep notAfter | cut -d= -f2)
        log "Certificate is valid"
        log "Certificate expires: $expiry_date"
        return 0
    else
        error "Certificate is invalid"
        return 1
    fi
}

# Test and reload nginx
reload_nginx() {
    log "Testing and reloading nginx configuration..."
    
    if nginx -t; then
        log "Nginx configuration test passed"
        
        if nginx -s reload; then
            log "Nginx reloaded successfully"
            return 0
        else
            error "Failed to reload nginx"
            return 1
        fi
    else
        error "Nginx configuration test failed"
        return 1
    fi
}

# Main initialization function
main() {
    log "Starting SSL certificate initialization for $DOMAIN_NAME..."
    
    validate_config
    
    if ! check_existing_certificates; then
        log "Certificate initialization skipped"
        exit 0
    fi
    
    download_tls_params
    
    if ! request_certificates; then
        error "Certificate request failed"
        exit 1
    fi
    
    if ! verify_certificates; then
        error "Certificate verification failed"
        exit 1
    fi
    
    if ! reload_nginx; then
        error "Nginx reload failed"
        exit 1
    fi
    
    log "SSL certificate initialization completed successfully!"
    log "Your site should now be available over HTTPS at https://$DOMAIN_NAME"
}

# Show usage information
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Environment Variables:"
    echo "  DOMAIN_NAME    - Domain name for SSL certificate (required)"
    echo "  EMAIL          - Email for Let's Encrypt notifications (required)"
    echo "  STAGING        - Use staging server (0=production, 1=staging, default: 0)"
    echo "  RSA_KEY_SIZE   - RSA key size (default: 4096)"
    echo "  FORCE          - Force recreation of existing certificates (0=ask, 1=force, default: 0)"
    echo ""
    echo "Examples:"
    echo "  DOMAIN_NAME=example.com EMAIL=admin@example.com $0"
    echo "  STAGING=1 FORCE=1 DOMAIN_NAME=test.com EMAIL=test@test.com $0"
}

# Handle command line arguments
case "${1:-}" in
    "-h"|"--help"|"help")
        usage
        exit 0
        ;;
    "")
        main
        ;;
    *)
        error "Unknown argument: $1"
        usage
        exit 1
        ;;
esac