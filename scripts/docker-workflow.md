# Docker Image Management Workflow

This document explains how to build, tag, push, and use pre-built Docker images for CulicidaeLab.

## Quick Start

### 1. Build Images Locally

**Windows:**
```powershell
.\scripts\build-images.ps1
```

**Linux/Mac:**
```bash
./scripts/build-images.sh
```

### 2. Build with Version and Registry

**Windows:**
```powershell
.\scripts\build-images.ps1 -Version "v1.0.0" -Registry "your-registry.com/username"
```

**Linux/Mac:**
```bash
./scripts/build-images.sh v1.0.0 your-registry.com/username
```

### 3. Push to Registry

**Windows:**
```powershell
.\scripts\push-images.ps1 -Version "v1.0.0" -Registry "your-registry.com/username"
```

**Linux/Mac:**
```bash
./scripts/push-images.sh v1.0.0 your-registry.com/username
```

### 4. Use Pre-built Images

Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

Edit `.env` with your registry details:
```env
REGISTRY=your-registry.com/username
VERSION=v1.0.0
```

Run with pre-built images:
```bash
docker-compose -f docker-compose.prebuilt.yml up
```

## Registry Options

### Docker Hub
```bash
# Build and tag for Docker Hub
./scripts/build-images.sh v1.0.0 yourusername

# Push to Docker Hub
./scripts/push-images.sh v1.0.0 yourusername
```

### GitHub Container Registry
```bash
# Build and tag for GHCR
./scripts/build-images.sh v1.0.0 ghcr.io/yourusername

# Push to GHCR (requires authentication)
./scripts/push-images.sh v1.0.0 ghcr.io/yourusername
```

### AWS ECR
```bash
# Build and tag for ECR
./scripts/build-images.sh v1.0.0 123456789012.dkr.ecr.us-west-2.amazonaws.com

# Push to ECR (requires AWS CLI authentication)
./scripts/push-images.sh v1.0.0 123456789012.dkr.ecr.us-west-2.amazonaws.com
```

## Image Management

### List Built Images
```bash
docker images | grep culicidaelab
```

### Remove Local Images
```bash
docker rmi culicidaelab-backend:latest
docker rmi culicidaelab-frontend:latest
docker rmi culicidaelab-nginx:latest
```

### Pull Images from Registry
```bash
docker pull your-registry.com/username/culicidaelab-backend:latest
docker pull your-registry.com/username/culicidaelab-frontend:latest
docker pull your-registry.com/username/culicidaelab-nginx:latest
```

## Development vs Production

### Development (with live code changes)
```bash
docker-compose -f docker-compose.dev.yml up
```

### Production (with pre-built images)
```bash
docker-compose -f docker-compose.prebuilt.yml up
```

### Production (build from source)
```bash
docker-compose -f docker-compose.prod.yml up --build
```

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Build and Push Images
  run: |
    ./scripts/build-images.sh ${{ github.sha }} ghcr.io/${{ github.repository_owner }}
    ./scripts/push-images.sh ${{ github.sha }} ghcr.io/${{ github.repository_owner }}
```

### GitLab CI Example
```yaml
build-images:
  script:
    - ./scripts/build-images.sh $CI_COMMIT_SHA $CI_REGISTRY_IMAGE
    - ./scripts/push-images.sh $CI_COMMIT_SHA $CI_REGISTRY_IMAGE
```

## Troubleshooting

### Authentication Issues
```bash
# Docker Hub
docker login

# GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# AWS ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com
```

### Image Size Optimization
- Images use multi-stage builds for smaller size
- Non-root users for security
- Minimal base images (python:3.11-slim)
- Cleanup of package caches and temporary files