#!/bin/bash

# CulicidaeLab SSL Production Deployment Script
# Usage: ./scripts/deploy-ssl.sh -d yourdomain.com -e admin@yourdomain.com [options]

set -e

# Default values
VERSION="latest"
REGISTRY=""
DOMAIN=""
EMAIL=""
STAGING=false
FORCE_RENEWAL=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

show_usage() {
    echo "Usage: $0 -d DOMAIN -e EMAIL [OPTIONS]"
    echo ""
    echo "Required:"
    echo "  -d, --domain DOMAIN     Your domain name"
    echo "  -e, --email EMAIL       Email for Let's Encrypt registration"
    echo ""
    echo "Options:"
    echo "  -v, --version VERSION   Docker image version (default: latest)"
    echo "  -r, --registry REGISTRY Docker registry prefix (optional)"
    echo "  -s, --staging           Use Let's Encrypt staging environment"
    echo "  -f, --force-renewal     Force certificate renewal"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -d yourdomain.com -e admin@yourdomain.com"
    echo "  $0 -d yourdomain.com -e admin@yourdomain.com -v 1.0.0 -s"
    echo "  $0 -d yourdomain.com -e admin@yourdomain.com -r myregistry.com/"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        -e|--email)
            EMAIL="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -s|--staging)
            STAGING=true
            shift
            ;;
        -f|--force-renewal)
            FORCE_RENEWAL=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [[ -z "$DOMAIN" ]]; then
    print_error "Domain is required!"
    show_usage
    exit 1
fi

if [[ -z "$EMAIL" ]]; then
    print_error "Email is required for Let's Encrypt!"
    show_usage
    exit 1
fi

# Validate domain (should not be localhost or IP)
if [[ "$DOMAIN" == "localhost" || "$DOMAIN" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    print_error "SSL deployment requires a valid domain name, not localhost or IP address"
    exit 1
fi

# Display configuration
echo "=================================================="
echo "CulicidaeLab SSL Production Deployment"
echo "=================================================="
print_info "Domain: $DOMAIN"
print_info "Email: $EMAIL"
print_info "Version: $VERSION"
print_info "Registry: ${REGISTRY:-local images}"
print_info "Staging: $STAGING"
print_info "Force Renewal: $FORCE_RENEWAL"
echo ""

# Check prerequisites
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed"
    exit 1
fi

# Check if SSL nginx image exists
SSL_IMAGE="${REGISTRY}culicidaelab-nginx-ssl:$VERSION"
if ! docker images --format "{{.Repository}}:{{.Tag}}" | grep -q "^$SSL_IMAGE$"; then
    print_warning "SSL nginx image not found locally: $SSL_IMAGE"
    print_info "Building SSL nginx image..."
    
    if [[ -n "$REGISTRY" ]]; then
        ./scripts/build-nginx-ssl.sh "$VERSION" "$REGISTRY"
    else
        ./scripts/build-nginx-ssl.sh "$VERSION"
    fi
fi

# Create SSL production environment file
ENV_FILE=".env.ssl.production"
print_info "Creating SSL production environment file: $ENV_FILE"

cat > "$ENV_FILE" << EOF
# SSL Production Environment Configuration
# Generated on $(date)

DOMAIN=$DOMAIN
EMAIL=$EMAIL
REGISTRY=$REGISTRY
VERSION=$VERSION
ENVIRONMENT=production
FASTAPI_ENV=production
NGINX_ENV=production
DEBUG=false
SOLARA_DEBUG=false

# SSL Configuration
SSL_ENABLED=true
STAGING=$STAGING
FORCE_RENEWAL=$FORCE_RENEWAL

# URLs for production (HTTPS)
CLIENT_BACKEND_URL=https://$DOMAIN
STATIC_URL_BASE=https://$DOMAIN
STATIC_FILES_URL=https://$DOMAIN

# CORS origins
CORS_ORIGINS=https://$DOMAIN,http://$DOMAIN
EOF

print_status "Created $ENV_FILE"

# Stop existing containers
print_info "Stopping existing containers..."
docker-compose -f docker-compose.ssl.yml --env-file "$ENV_FILE" down 2>/dev/null || true
print_status "Stopped existing containers"

# Pull latest images (if using registry)
if [[ -n "$REGISTRY" ]]; then
    print_info "Pulling latest images from registry..."
    if docker-compose -f docker-compose.ssl.yml --env-file "$ENV_FILE" pull; then
        print_status "Successfully pulled images"
    else
        print_warning "Failed to pull some images, continuing with local images"
    fi
fi

# Start services
print_info "Starting SSL production services..."
if docker-compose -f docker-compose.ssl.yml --env-file "$ENV_FILE" up -d; then
    print_status "Services started successfully"
else
    print_error "Failed to start services"
    exit 1
fi

# Wait for services to start
print_info "Waiting for services to start and SSL certificates to be obtained..."
print_warning "This may take a few minutes for initial SSL certificate generation..."
sleep 30

# Check service health
print_info "Checking service health..."
services=("culicidaelab_backend_ssl" "culicidaelab_frontend_ssl" "culicidaelab_nginx_ssl")

all_healthy=true
for service in "${services[@]}"; do
    if docker ps --filter "name=$service" --filter "status=running" --format "table {{.Names}}" | grep -q "$service"; then
        print_status "$service is running"
    else
        print_error "$service is not running"
        all_healthy=false
    fi
done

# Test SSL endpoints
print_info "Testing SSL endpoints..."

# Test HTTP redirect
if curl -s -I "http://$DOMAIN/health" | grep -q "301\|302"; then
    print_status "HTTP to HTTPS redirect is working"
else
    print_warning "HTTP to HTTPS redirect may not be working"
fi

# Test HTTPS endpoint
if curl -s -f "https://$DOMAIN/health" > /dev/null 2>&1; then
    print_status "HTTPS endpoint is accessible"
else
    print_warning "HTTPS endpoint is not accessible yet (SSL certificate may still be generating)"
fi

# Show certificate information
print_info "Checking SSL certificate..."
if docker exec culicidaelab_nginx_ssl ls -la /etc/letsencrypt/live/$DOMAIN/ 2>/dev/null; then
    print_status "SSL certificate files found"
    
    # Show certificate expiration
    if docker exec culicidaelab_nginx_ssl openssl x509 -enddate -noout -in /etc/letsencrypt/live/$DOMAIN/fullchain.pem 2>/dev/null; then
        print_status "Certificate expiration information shown above"
    fi
else
    print_warning "SSL certificate files not found yet"
fi

echo ""
echo "=================================================="
if [[ $all_healthy == true ]]; then
    echo -e "${GREEN}🎉 SSL deployment completed successfully!${NC}"
else
    echo -e "${YELLOW}⚠ SSL deployment completed with warnings${NC}"
fi
echo "=================================================="
print_info "Access your application at: https://$DOMAIN"
print_info "HTTP requests will be automatically redirected to HTTPS"
echo ""
print_info "Useful commands:"
echo "  View logs:    docker-compose -f docker-compose.ssl.yml --env-file $ENV_FILE logs -f"
echo "  Stop services: docker-compose -f docker-compose.ssl.yml --env-file $ENV_FILE down"
echo "  Restart:      docker-compose -f docker-compose.ssl.yml --env-file $ENV_FILE restart"
echo "  Status:       docker-compose -f docker-compose.ssl.yml --env-file $ENV_FILE ps"
echo "  SSL logs:     docker logs culicidaelab_nginx_ssl"

# Show container status
echo ""
print_info "Current container status:"
docker-compose -f docker-compose.ssl.yml --env-file "$ENV_FILE" ps

# Show nginx logs for SSL setup
if [[ $all_healthy != true ]]; then
    echo ""
    print_warning "If there are SSL issues, check nginx logs:"
    echo "  docker logs culicidaelab_nginx_ssl"
fi

echo ""
print_info "SSL deployment script completed!"

if [[ "$STAGING" == "true" ]]; then
    echo ""
    print_warning "You used staging certificates. For production, run again without -s flag:"
    echo "  $0 -d $DOMAIN -e $EMAIL -f"
fi