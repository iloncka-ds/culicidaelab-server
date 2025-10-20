# CulicidaeLab Docker Hub Deployment Guide

This guide shows how to build, push, and deploy CulicidaeLab using Docker Hub registry.

## 🐳 Docker Hub Setup

### Your Docker Hub Registry
- **Username**: `iloncka`
- **Registry prefix**: `iloncka/`
- **Repositories**:
  - `iloncka/culicidaelab-backend`
  - `iloncka/culicidaelab-frontend`
  - `iloncka/culicidaelab-nginx`
  - `iloncka/culicidaelab-nginx-ssl`

## 🚀 Quick Start

### 1. Login to Docker Hub
```bash
docker login
# Enter your Docker Hub username (iloncka) and password
```

### 2. Build and Push Images

**Using PowerShell (Windows):**
```powershell
# Build and push all images with default settings
.\scripts\build-and-push.ps1

# Build and push specific version
.\scripts\build-and-push.ps1 -Version "1.0.0"

# Build and push to different registry
.\scripts\build-and-push.ps1 -Version "1.0.0" -Registry "myregistry/"
```

**Using Bash (Linux/macOS):**
```bash
# Build and push all images with default settings
./scripts/build-and-push.sh

# Build and push specific version
./scripts/build-and-push.sh 1.0.0

# Build and push to different registry
./scripts/build-and-push.sh 1.0.0 myregistry/
```

### 3. Deploy from Docker Hub

**Standard deployment:**
```bash
./scripts/deploy-production.sh -d yourdomain.com -r iloncka/ -v 1.0.0
```

**SSL deployment:**
```bash
./scripts/deploy-ssl.sh -d yourdomain.com -e admin@yourdomain.com -r iloncka/ -v 1.0.0
```

## 📋 Step-by-Step Process

### Building and Pushing

1. **Build all images locally:**
   ```bash
   # This builds all 4 images with your registry prefix
   docker build -f backend/Dockerfile -t iloncka/culicidaelab-backend:1.0.0 .
   docker build -f frontend/Dockerfile -t iloncka/culicidaelab-frontend:1.0.0 .
   docker build -f nginx/Dockerfile -t iloncka/culicidaelab-nginx:1.0.0 .
   docker build -f nginx/Dockerfile.with-certbot -t iloncka/culicidaelab-nginx-ssl:1.0.0 .
   ```

2. **Push to Docker Hub:**
   ```bash
   docker push iloncka/culicidaelab-backend:1.0.0
   docker push iloncka/culicidaelab-frontend:1.0.0
   docker push iloncka/culicidaelab-nginx:1.0.0
   docker push iloncka/culicidaelab-nginx-ssl:1.0.0
   ```

### Deploying from Registry

1. **Create environment file:**
   ```env
   REGISTRY=iloncka/
   VERSION=1.0.0
   DOMAIN=yourdomain.com
   ```

2. **Deploy:**
   ```bash
   docker-compose -f docker-compose.prebuilt.yml --env-file .env.production up -d
   ```

## 🔧 Environment Configuration

### For Docker Hub deployment, set:
```env
# .env.production
REGISTRY=iloncka/
VERSION=1.0.0
DOMAIN=yourdomain.com
CLIENT_BACKEND_URL=https://yourdomain.com
STATIC_URL_BASE=https://yourdomain.com
STATIC_FILES_URL=https://yourdomain.com
CORS_ORIGINS=https://yourdomain.com
```

## 📊 Managing Docker Hub Images

### View your repositories:
- Backend: https://hub.docker.com/r/iloncka/culicidaelab-backend
- Frontend: https://hub.docker.com/r/iloncka/culicidaelab-frontend
- Nginx: https://hub.docker.com/r/iloncka/culicidaelab-nginx
- SSL Nginx: https://hub.docker.com/r/iloncka/culicidaelab-nginx-ssl

### Pull images on server:
```bash
docker pull iloncka/culicidaelab-backend:1.0.0
docker pull iloncka/culicidaelab-frontend:1.0.0
docker pull iloncka/culicidaelab-nginx:1.0.0
docker pull iloncka/culicidaelab-nginx-ssl:1.0.0
```

## 🔄 Version Management

### Tagging Strategy
```bash
# Tag with version
docker tag culicidaelab-backend:latest iloncka/culicidaelab-backend:1.0.0

# Tag as latest
docker tag culicidaelab-backend:latest iloncka/culicidaelab-backend:latest

# Push both tags
docker push iloncka/culicidaelab-backend:1.0.0
docker push iloncka/culicidaelab-backend:latest
```

### Deployment with Different Versions
```bash
# Deploy specific version
./scripts/deploy-production.sh -d yourdomain.com -r iloncka/ -v 1.0.0

# Deploy latest
./scripts/deploy-production.sh -d yourdomain.com -r iloncka/ -v latest
```

## 🚀 Production Workflow

### 1. Development to Production Pipeline

```bash
# 1. Build and test locally
.\scripts\build-docker.ps1 "1.0.0"
.\scripts\run-local.ps1 "1.0.0"

# 2. Test locally, then build and push to Docker Hub
.\scripts\build-and-push.ps1 -Version "1.0.0"

# 3. Deploy on production server
./scripts/deploy-ssl.sh -d yourdomain.com -e admin@yourdomain.com -r iloncka/ -v 1.0.0
```

### 2. Update Production

```bash
# Build new version
.\scripts\build-and-push.ps1 -Version "1.0.1"

# Update production
./scripts/deploy-ssl.sh -d yourdomain.com -e admin@yourdomain.com -r iloncka/ -v 1.0.1
```

## 🔍 Troubleshooting

### Authentication Issues
```bash
# Re-login to Docker Hub
docker login

# Check authentication
docker info | grep Username
```

### Push/Pull Issues
```bash
# Check if repository exists
docker search iloncka/culicidaelab-backend

# Manual push
docker push iloncka/culicidaelab-backend:1.0.0
```

### Deployment Issues
```bash
# Check if images exist
docker pull iloncka/culicidaelab-backend:1.0.0

# Check environment variables
cat .env.production
```

## 💡 Best Practices

1. **Use semantic versioning**: `1.0.0`, `1.0.1`, `1.1.0`
2. **Tag both version and latest**: For easy updates
3. **Test locally first**: Before pushing to registry
4. **Use staging environment**: Test with staging certificates
5. **Monitor image sizes**: Keep images optimized
6. **Regular updates**: Keep base images updated

## 📈 Image Information

After building, you can check image sizes:
```bash
docker images iloncka/culicidaelab-*
```

Typical sizes:
- Backend: ~3.4GB (includes Python, ML libraries)
- Frontend: ~1.1GB (includes Python, Solara)
- Nginx: ~80MB (Alpine-based)
- SSL Nginx: ~120MB (includes certbot)