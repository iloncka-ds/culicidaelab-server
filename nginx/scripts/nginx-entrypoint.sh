#!/bin/bash

# nginx-entrypoint.sh - Enhanced entrypoint script for nginx with SSL/certbot support
# This script handles SSL certificate initialization and nginx startup

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

# Environment variables with defaults
DOMAIN=${DOMAIN:-localhost}
EMAIL=${EMAIL:-admin@${DOMAIN}}
SSL_ENABLED=${SSL_ENABLED:-false}
STAGING=${STAGING:-false}
FORCE_RENEWAL=${FORCE_RENEWAL:-false}

log "Starting nginx with SSL support..."
log "Domain: $DOMAIN"
log "Email: $EMAIL"
log "SSL Enabled: $SSL_ENABLED"
log "Staging: $STAGING"

# Create necessary directories
mkdir -p /var/www/certbot
mkdir -p /var/log/letsencrypt
mkdir -p /etc/letsencrypt/live
mkdir -p /etc/nginx/conf.d

# Set proper permissions (skip if read-only)
if touch /var/www/test_write 2>/dev/null; then
    rm -f /var/www/test_write
    chown -R nginx:nginx /var/www
    chmod -R 755 /var/www
    log_success "Set permissions for /var/www"
else
    log_warning "Skipping permission changes for /var/www (read-only filesystem)"
fi

# Function to check if certificate exists and is valid
check_certificate() {
    local domain=$1
    local cert_path="/etc/letsencrypt/live/$domain/fullchain.pem"
    local key_path="/etc/letsencrypt/live/$domain/privkey.pem"
    
    if [[ -f "$cert_path" && -f "$key_path" ]]; then
        # Check if certificate is valid and not expiring soon (30 days)
        if openssl x509 -checkend 2592000 -noout -in "$cert_path" >/dev/null 2>&1; then
            log_success "Valid SSL certificate found for $domain"
            return 0
        else
            log_warning "SSL certificate for $domain is expiring soon or invalid"
            return 1
        fi
    else
        log "No SSL certificate found for $domain"
        return 1
    fi
}

# Function to generate self-signed certificate for development
generate_self_signed_cert() {
    local domain=$1
    local cert_dir="/etc/letsencrypt/live/$domain"
    
    log "Generating self-signed certificate for $domain..."
    
    mkdir -p "$cert_dir"
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$cert_dir/privkey.pem" \
        -out "$cert_dir/fullchain.pem" \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=$domain" \
        >/dev/null 2>&1
    
    if [[ $? -eq 0 ]]; then
        log_success "Self-signed certificate generated for $domain"
        return 0
    else
        log_error "Failed to generate self-signed certificate"
        return 1
    fi
}

# Function to obtain Let's Encrypt certificate
obtain_letsencrypt_cert() {
    local domain=$1
    local email=$2
    local staging=$3
    
    log "Obtaining Let's Encrypt certificate for $domain..."
    
    local staging_flag=""
    if [[ "$staging" == "true" ]]; then
        staging_flag="--staging"
        log "Using Let's Encrypt staging environment"
    fi
    
    # Create temporary nginx config for Let's Encrypt challenge
    cat > /tmp/nginx-challenge.conf << 'EOF'
worker_processes 1;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    server {
        listen 80;
        server_name _;
        
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
            try_files $uri =404;
        }
        
        location / {
            return 200 'Challenge server running';
            add_header Content-Type text/plain;
        }
    }
}
EOF
    
    # Start nginx with challenge config
    nginx -c /tmp/nginx-challenge.conf -g "daemon off;" &
    local nginx_pid=$!
    
    # Wait for nginx to start
    sleep 3
    
    # Attempt to obtain certificate
    certbot certonly \
        --webroot \
        --webroot-path=/var/www/certbot \
        --email "$email" \
        --agree-tos \
        --no-eff-email \
        --domains "$domain" \
        $staging_flag \
        --non-interactive \
        --verbose
    
    local certbot_exit_code=$?
    
    # Stop background nginx
    kill $nginx_pid 2>/dev/null || true
    wait $nginx_pid 2>/dev/null || true
    
    if [[ $certbot_exit_code -eq 0 ]]; then
        log_success "Let's Encrypt certificate obtained for $domain"
        return 0
    else
        log_error "Failed to obtain Let's Encrypt certificate"
        return 1
    fi
}

# Function to setup SSL configuration
setup_ssl_config() {
    local domain=$1
    
    log "Setting up SSL configuration for $domain..."
    
    # Process the nginx template and create the final config
    if [[ -f "/etc/nginx/nginx.conf.template" ]]; then
        # Create a complete nginx.conf with proper structure
        cat > /etc/nginx/nginx.conf << EOF
# Main nginx configuration with SSL
worker_processes auto;
error_log /var/log/nginx/error.log notice;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
EOF
        
        # Append the processed SSL template (which contains the server blocks)
        sed "s/\${DOMAIN}/$domain/g" /etc/nginx/nginx.conf.template >> /etc/nginx/nginx.conf
        
        # Close the http block
        echo "}" >> /etc/nginx/nginx.conf
        
        log_success "SSL configuration created from template for $domain"
    else
        log_error "SSL configuration template not found at /etc/nginx/nginx.conf.template"
        return 1
    fi
    
    log_success "SSL configuration updated for $domain"
}

# Function to test nginx configuration
test_nginx_config() {
    log "Testing nginx configuration..."
    
    if nginx -t >/dev/null 2>&1; then
        log_success "nginx configuration is valid"
        return 0
    else
        log_error "nginx configuration test failed"
        nginx -t
        return 1
    fi
}

# Main SSL setup logic
setup_ssl() {
    if [[ "$SSL_ENABLED" != "true" ]]; then
        log "SSL is disabled, skipping certificate setup"
        return 0
    fi
    
    if [[ "$DOMAIN" == "localhost" || "$DOMAIN" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        log "Domain is localhost or IP address, generating self-signed certificate"
        generate_self_signed_cert "$DOMAIN"
        setup_ssl_config "$DOMAIN"
        return $?
    fi
    
    # Check if we need to obtain/renew certificate
    if ! check_certificate "$DOMAIN" || [[ "$FORCE_RENEWAL" == "true" ]]; then
        if ! obtain_letsencrypt_cert "$DOMAIN" "$EMAIL" "$STAGING"; then
            log_warning "Let's Encrypt failed, falling back to self-signed certificate"
            generate_self_signed_cert "$DOMAIN"
        fi
    fi
    
    setup_ssl_config "$DOMAIN"
}

# Start cron daemon for certificate renewal
start_cron() {
    log "Starting cron daemon for certificate renewal..."
    crond -b -l 8
    log_success "Cron daemon started"
}

# Main execution
main() {
    log "nginx entrypoint starting..."
    
    # Setup SSL if enabled
    setup_ssl
    
    # Start cron for certificate renewal
    if [[ "$SSL_ENABLED" == "true" ]]; then
        start_cron
    fi
    
    # Test nginx configuration
    if ! test_nginx_config; then
        log_error "nginx configuration is invalid, exiting"
        exit 1
    fi
    
    log_success "nginx entrypoint setup completed"
    
    # Execute the main command (nginx)
    exec "$@"
}

# Handle signals for graceful shutdown
trap 'log "Received shutdown signal, stopping..."; exit 0' SIGTERM SIGINT

# Run main function
main "$@"