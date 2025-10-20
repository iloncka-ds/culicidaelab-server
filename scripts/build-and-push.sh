#!/bin/bash

# Build and push CulicidaeLab images to Docker Hub
# Usage: ./scripts/build-and-push.sh [version] [registry]

set -e

VERSION=${1:-latest}
REGISTRY=${2:-iloncka/}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${CYAN}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

echo "=================================================="
echo "Building and Pushing CulicidaeLab Images"
echo "=================================================="
print_info "Version: $VERSION"
print_info "Registry: $REGISTRY"
echo ""

# Check if logged into Docker Hub
print_info "Checking Docker Hub authentication..."
if ! docker info | grep -q "Username"; then
    print_warning "Not logged into Docker Hub. Please login first:"
    echo "  docker login"
    exit 1
fi
print_status "Docker Hub authentication verified"

# Build all images locally first
print_info "Building images locally..."

# Build backend
print_info "Building backend image..."
if docker build -f backend/Dockerfile -t "${REGISTRY}culicidaelab-backend:$VERSION" .; then
    print_status "Backend image built successfully"
else
    print_error "Failed to build backend image"
    exit 1
fi

# Build frontend
print_info "Building frontend image..."
if docker build -f frontend/Dockerfile -t "${REGISTRY}culicidaelab-frontend:$VERSION" .; then
    print_status "Frontend image built successfully"
else
    print_error "Failed to build frontend image"
    exit 1
fi

# Build nginx
print_info "Building nginx image..."
if docker build -f nginx/Dockerfile -t "${REGISTRY}culicidaelab-nginx:$VERSION" .; then
    print_status "Nginx image built successfully"
else
    print_error "Failed to build nginx image"
    exit 1
fi

# Build SSL nginx
print_info "Building SSL nginx image..."
if docker build -f nginx/Dockerfile.with-certbot -t "${REGISTRY}culicidaelab-nginx-ssl:$VERSION" .; then
    print_status "SSL nginx image built successfully"
else
    print_error "Failed to build SSL nginx image"
    exit 1
fi

echo ""
print_info "All images built successfully. Starting push to registry..."
echo ""

# Push images to registry
images=(
    "${REGISTRY}culicidaelab-backend:$VERSION"
    "${REGISTRY}culicidaelab-frontend:$VERSION"
    "${REGISTRY}culicidaelab-nginx:$VERSION"
    "${REGISTRY}culicidaelab-nginx-ssl:$VERSION"
)

for image in "${images[@]}"; do
    print_info "Pushing $image..."
    if docker push "$image"; then
        print_status "Successfully pushed $image"
    else
        print_error "Failed to push $image"
        exit 1
    fi
done

echo ""
echo "=================================================="
print_status "All images built and pushed successfully!"
echo "=================================================="
echo ""
print_info "Pushed images:"
for image in "${images[@]}"; do
    echo "  - $image"
done

echo ""
print_info "To deploy using these images:"
echo "  ./scripts/deploy-production.sh -d yourdomain.com -r $REGISTRY -v $VERSION"
echo "  ./scripts/deploy-ssl.sh -d yourdomain.com -e admin@yourdomain.com -r $REGISTRY -v $VERSION"

echo ""
print_info "Docker Hub repositories:"
echo "  https://hub.docker.com/r/${REGISTRY%/}/culicidaelab-backend"
echo "  https://hub.docker.com/r/${REGISTRY%/}/culicidaelab-frontend"
echo "  https://hub.docker.com/r/${REGISTRY%/}/culicidaelab-nginx"
echo "  https://hub.docker.com/r/${REGISTRY%/}/culicidaelab-nginx-ssl"