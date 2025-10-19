#!/bin/bash

# Certbot initialization script for Let's Encrypt SSL certificates
# This script handles initial certificate generation with domain validation

set -e

# Configuration
DOMAINS=${DOMAINS:-"example.com www.example.com"}
EMAIL=${EMAIL:-"admin@example.com"}
STAGING=${STAGING:-0}
RSA_KEY_SIZE=${RSA_KEY_SIZE:-4096}
DATA_PATH="./certbot"
NGINX_CONF_PATH="./nginx"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Validate required environment variables
validate_config() {
    log "Validating configuration..."
    
    if [ -z "$DOMAINS" ]; then
        error "DOMAINS environment variable is required"
        exit 1
    fi
    
    if [ -z "$EMAIL" ]; then
        error "EMAIL environment variable is required"
        exit 1
    fi
    
    # Validate email format
    if ! echo "$EMAIL" | grep -E '^[^@]+@[^@]+\.[^@]+$' > /dev/null; then
        error "Invalid email format: $EMAIL"
        exit 1
    fi
    
    log "Configuration validated successfully"
}

# Check if certificates already exist
check_existing_certificates() {
    local domain_array=($DOMAINS)
    local primary_domain=${domain_array[0]}
    
    if [ -d "$DATA_PATH/conf/live/$primary_domain" ]; then
        warn "Certificates for $primary_domain already exist"
        read -p "Do you want to recreate them? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log "Keeping existing certificates"
            return 1
        fi
        log "Removing existing certificates..."
        rm -rf "$DATA_PATH/conf/live/$primary_domain"
        rm -rf "$DATA_PATH/conf/archive/$primary_domain"
        rm -f "$DATA_PATH/conf/renewal/$primary_domain.conf"
    fi
    return 0
}

# Create necessary directories
create_directories() {
    log "Creating necessary directories..."
    
    mkdir -p "$DATA_PATH/conf"
    mkdir -p "$DATA_PATH/www"
    mkdir -p "$DATA_PATH/logs"
    
    # Set proper permissions
    chmod 755 "$DATA_PATH"
    chmod 755 "$DATA_PATH/www"
    
    log "Directories created successfully"
}

# Download recommended TLS parameters
download_tls_params() {
    log "Downloading recommended TLS parameters..."
    
    if [ ! -f "$DATA_PATH/conf/options-ssl-nginx.conf" ]; then
        curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$DATA_PATH/conf/options-ssl-nginx.conf"
        log "Downloaded options-ssl-nginx.conf"
    else
        log "TLS parameters already exist"
    fi
    
    if [ ! -f "$DATA_PATH/conf/ssl-dhparams.pem" ]; then
        curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$DATA_PATH/conf/ssl-dhparams.pem"
        log "Downloaded ssl-dhparams.pem"
    else
        log "DH parameters already exist"
    fi
}

# Create dummy certificates for nginx startup
create_dummy_certificates() {
    local domain_array=($DOMAINS)
    local primary_domain=${domain_array[0]}
    
    log "Creating dummy certificates for nginx startup..."
    
    mkdir -p "$DATA_PATH/conf/live/$primary_domain"
    
    # Generate dummy certificate
    openssl req -x509 -nodes -newkey rsa:$RSA_KEY_SIZE -days 1 \
        -keyout "$DATA_PATH/conf/live/$primary_domain/privkey.pem" \
        -out "$DATA_PATH/conf/live/$primary_domain/fullchain.pem" \
        -subj "/CN=localhost" 2>/dev/null
    
    log "Dummy certificates created"
}

# Start nginx with dummy certificates
start_nginx() {
    log "Starting nginx with dummy certificates..."
    
    if ! docker-compose up -d nginx; then
        error "Failed to start nginx"
        return 1
    fi
    
    # Wait for nginx to be ready
    sleep 5
    
    if ! docker-compose ps nginx | grep -q "Up"; then
        error "Nginx failed to start properly"
        docker-compose logs nginx
        return 1
    fi
    
    log "Nginx started successfully"
}

# Remove dummy certificates
remove_dummy_certificates() {
    local domain_array=($DOMAINS)
    local primary_domain=${domain_array[0]}
    
    log "Removing dummy certificates..."
    rm -rf "$DATA_PATH/conf/live/$primary_domain"
}

# Request Let's Encrypt certificates
request_certificates() {
    local domain_array=($DOMAINS)
    local primary_domain=${domain_array[0]}
    
    log "Requesting Let's Encrypt certificates for: $DOMAINS"
    
    # Build domain arguments
    local domain_args=""
    for domain in $DOMAINS; do
        domain_args="$domain_args -d $domain"
    done
    
    # Select appropriate server URL
    local server_url=""
    if [ $STAGING != "0" ]; then
        server_url="--server https://acme-staging-v02.api.letsencrypt.org/directory"
        warn "Using Let's Encrypt staging server"
    fi
    
    # Request certificate
    if docker-compose run --rm --entrypoint "\
        certbot certonly --webroot -w /var/www/certbot \
        $server_url \
        $domain_args \
        --email $EMAIL \
        --rsa-key-size $RSA_KEY_SIZE \
        --agree-tos \
        --force-renewal \
        --non-interactive" certbot; then
        
        log "Certificates obtained successfully"
        return 0
    else
        error "Failed to obtain certificates"
        return 1
    fi
}

# Reload nginx with real certificates
reload_nginx() {
    log "Reloading nginx with real certificates..."
    
    if docker-compose exec nginx nginx -s reload; then
        log "Nginx reloaded successfully"
    else
        error "Failed to reload nginx"
        return 1
    fi
}

# Verify certificate installation
verify_certificates() {
    local domain_array=($DOMAINS)
    local primary_domain=${domain_array[0]}
    
    log "Verifying certificate installation..."
    
    # Check if certificate files exist
    if [ ! -f "$DATA_PATH/conf/live/$primary_domain/fullchain.pem" ] || \
       [ ! -f "$DATA_PATH/conf/live/$primary_domain/privkey.pem" ]; then
        error "Certificate files not found"
        return 1
    fi
    
    # Check certificate validity
    if openssl x509 -in "$DATA_PATH/conf/live/$primary_domain/fullchain.pem" -text -noout > /dev/null 2>&1; then
        log "Certificate is valid"
        
        # Show certificate details
        local expiry_date=$(openssl x509 -in "$DATA_PATH/conf/live/$primary_domain/fullchain.pem" -noout -dates | grep notAfter | cut -d= -f2)
        log "Certificate expires: $expiry_date"
        
        return 0
    else
        error "Certificate is invalid"
        return 1
    fi
}

# Cleanup function for error handling
cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        error "Script failed with exit code $exit_code"
        warn "Cleaning up..."
        
        # Stop containers
        docker-compose down 2>/dev/null || true
        
        # Remove dummy certificates if they exist
        local domain_array=($DOMAINS)
        local primary_domain=${domain_array[0]}
        if [ -f "$DATA_PATH/conf/live/$primary_domain/fullchain.pem" ]; then
            if openssl x509 -in "$DATA_PATH/conf/live/$primary_domain/fullchain.pem" -text -noout 2>/dev/null | grep -q "CN=localhost"; then
                warn "Removing dummy certificates"
                rm -rf "$DATA_PATH/conf/live/$primary_domain"
            fi
        fi
    fi
}

# Set up error handling
trap cleanup EXIT

# Main execution
main() {
    log "Starting Let's Encrypt certificate initialization..."
    
    validate_config
    
    if ! check_existing_certificates; then
        log "Certificate initialization skipped"
        exit 0
    fi
    
    create_directories
    download_tls_params
    create_dummy_certificates
    
    if ! start_nginx; then
        error "Failed to start nginx"
        exit 1
    fi
    
    remove_dummy_certificates
    
    if ! request_certificates; then
        error "Certificate request failed"
        exit 1
    fi
    
    if ! reload_nginx; then
        error "Failed to reload nginx"
        exit 1
    fi
    
    if ! verify_certificates; then
        error "Certificate verification failed"
        exit 1
    fi
    
    log "Let's Encrypt certificate initialization completed successfully!"
    log "Your site should now be available over HTTPS"
}

# Run main function
main "$@"