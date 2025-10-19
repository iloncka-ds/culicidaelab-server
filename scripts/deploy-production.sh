#!/bin/bash

# CulicidaeLab Production Deployment Script
# Usage: ./scripts/deploy-production.sh -d yourdomain.com [-v version] [-p http|https] [-r registry]

set -e  # Exit on any error

# Default values
VERSION="latest"
PROTOCOL="https"
REGISTRY=""
DOMAIN=""
USE_IP=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Function to show usage
show_usage() {
    echo "Usage: $0 -d DOMAIN [OPTIONS]"
    echo ""
    echo "Required:"
    echo "  -d, --domain DOMAIN     Your domain name or IP address"
    echo ""
    echo "Options:"
    echo "  -v, --version VERSION   Docker image version (default: latest)"
    echo "  -p, --protocol PROTOCOL Protocol to use: http or https (default: https)"
    echo "  -r, --registry REGISTRY Docker registry prefix (optional)"
    echo "  -i, --ip                Treat domain as IP address (disables HTTPS)"
    echo "  -h, --help              Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -d yourdomain.com"
    echo "  $0 -d yourdomain.com -v 1.0.0 -p https"
    echo "  $0 -d 192.168.1.100 -i -p http"
    echo "  $0 -d yourdomain.com -r myregistry.com/myproject/"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -d|--domain)
            DOMAIN="$2"
            shift 2
            ;;
        -v|--version)
            VERSION="$2"
            shift 2
            ;;
        -p|--protocol)
            PROTOCOL="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -i|--ip)
            USE_IP=true
            PROTOCOL="http"
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

# Validate protocol
if [[ "$PROTOCOL" != "http" && "$PROTOCOL" != "https" ]]; then
    print_error "Protocol must be 'http' or 'https'"
    exit 1
fi

# If using IP address, force HTTP
if [[ $USE_IP == true ]]; then
    PROTOCOL="http"
    print_warning "Using IP address, forcing HTTP protocol"
fi

# Display configuration
echo "=================================================="
echo "CulicidaeLab Production Deployment"
echo "=================================================="
print_info "Domain: $DOMAIN"
print_info "Version: $VERSION"
print_info "Protocol: $PROTOCOL"
print_info "Registry: ${REGISTRY:-local images}"
print_info "Use IP: $USE_IP"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed or not in PATH"
    exit 1
fi

# Create production environment file
ENV_FILE=".env.production"
print_info "Creating production environment file: $ENV_FILE"

cat > "$ENV_FILE" << EOF
# Production Environment Configuration
# Generated on $(date)

DOMAIN=$DOMAIN
REGISTRY=$REGISTRY
VERSION=$VERSION
ENVIRONMENT=production
FASTAPI_ENV=production
NGINX_ENV=production
DEBUG=false
SOLARA_DEBUG=false

# URLs for production
CLIENT_BACKEND_URL=${PROTOCOL}://$DOMAIN
STATIC_URL_BASE=${PROTOCOL}://$DOMAIN
STATIC_FILES_URL=${PROTOCOL}://$DOMAIN

# CORS origins
CORS_ORIGINS=${PROTOCOL}://$DOMAIN

# SSL/TLS
SSL_ENABLED=$([ "$PROTOCOL" = "https" ] && echo "true" || echo "false")
EOF

print_status "Created $ENV_FILE"

# Stop existing containers
print_info "Stopping existing containers..."
docker-compose -f docker-compose.prebuilt.yml --env-file "$ENV_FILE" down 2>/dev/null || true
print_status "Stopped existing containers"

# Pull latest images (if using registry)
if [[ -n "$REGISTRY" ]]; then
    print_info "Pulling latest images from registry..."
    if docker-compose -f docker-compose.prebuilt.yml --env-file "$ENV_FILE" pull; then
        print_status "Successfully pulled images"
    else
        print_warning "Failed to pull some images, continuing with local images"
    fi
fi

# Start services
print_info "Starting production services..."
if docker-compose -f docker-compose.prebuilt.yml --env-file "$ENV_FILE" up -d; then
    print_status "Services started successfully"
else
    print_error "Failed to start services"
    exit 1
fi

# Wait for services to start
print_info "Waiting for services to start..."
sleep 10

# Check service health
print_info "Checking service health..."
services=("culicidaelab_backend_prebuilt" "culicidaelab_frontend_prebuilt" "culicidaelab_nginx_prebuilt")

all_healthy=true
for service in "${services[@]}"; do
    if docker ps --filter "name=$service" --filter "status=running" --format "table {{.Names}}" | grep -q "$service"; then
        print_status "$service is running"
    else
        print_error "$service is not running"
        all_healthy=false
    fi
done

# Test application endpoints
print_info "Testing application endpoints..."

# Test health endpoint
if curl -s -f "${PROTOCOL}://$DOMAIN/health" > /dev/null 2>&1; then
    print_status "Health endpoint is accessible"
else
    print_warning "Health endpoint is not accessible (this might be normal if using HTTPS without proper SSL setup)"
fi

# Test API endpoint
if curl -s -f "${PROTOCOL}://$DOMAIN/api/species" > /dev/null 2>&1; then
    print_status "API endpoint is accessible"
else
    print_warning "API endpoint is not accessible (this might be normal if using HTTPS without proper SSL setup)"
fi

echo ""
echo "=================================================="
if [[ $all_healthy == true ]]; then
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
else
    echo -e "${YELLOW}⚠ Deployment completed with warnings${NC}"
fi
echo "=================================================="
print_info "Access your application at: ${PROTOCOL}://$DOMAIN"
echo ""
print_info "Useful commands:"
echo "  View logs:    docker-compose -f docker-compose.prebuilt.yml --env-file $ENV_FILE logs -f"
echo "  Stop services: docker-compose -f docker-compose.prebuilt.yml --env-file $ENV_FILE down"
echo "  Restart:      docker-compose -f docker-compose.prebuilt.yml --env-file $ENV_FILE restart"
echo "  Status:       docker-compose -f docker-compose.prebuilt.yml --env-file $ENV_FILE ps"

# Show container status
echo ""
print_info "Current container status:"
docker-compose -f docker-compose.prebuilt.yml --env-file "$ENV_FILE" ps

# If there were issues, show logs
if [[ $all_healthy != true ]]; then
    echo ""
    print_warning "Some services may have issues. Check logs with:"
    echo "  docker-compose -f docker-compose.prebuilt.yml --env-file $ENV_FILE logs"
fi

echo ""
print_info "Deployment script completed!"