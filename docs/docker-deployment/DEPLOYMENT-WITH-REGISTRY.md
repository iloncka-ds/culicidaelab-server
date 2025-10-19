# CulicidaeLab Production Deployment Guide

This guide explains how to deploy CulicidaeLab to a production VPS server.

## Prerequisites

1. **VPS Server** with Docker and Docker Compose installed
2. **Domain name** (optional, can use IP address)
3. **SSL certificate** (recommended for production)

## Quick Deployment

### Option 1: Using the Deployment Script

**Bash (Linux/macOS):**
```bash
# Deploy with automatic SSL (recommended for production)
./scripts/deploy-ssl.sh -d yourdomain.com -e admin@yourdomain.com

# Deploy with HTTPS proxy (no automatic SSL)
./scripts/deploy-production.sh -d yourdomain.com -v latest

# Deploy with HTTP only (for testing)
./scripts/deploy-production.sh -d yourdomain.com -v latest -p http

# Deploy using IP address
./scripts/deploy-production.sh -d 192.168.1.100 -i

# Deploy with custom registry
./scripts/deploy-production.sh -d yourdomain.com -r myregistry.com/myproject/

# Deploy SSL with staging certificates (for testing)
./scripts/deploy-ssl.sh -d yourdomain.com -e admin@yourdomain.com -s
```

**PowerShell (Windows):**
```powershell
# Deploy with HTTPS (recommended)
.\scripts\deploy-production.ps1 -Domain "yourdomain.com" -Version "latest"

# Deploy with HTTP only (for testing)
.\scripts\deploy-production.ps1 -Domain "yourdomain.com" -Version "latest" -UseHTTP
```

### Option 2: Manual Deployment

1. **Create production environment file:**
   ```bash
   cp .env.production.template .env.production
   ```

2. **Edit `.env.production`** and replace `yourdomain.com` with your actual domain:
   ```env
   DOMAIN=yourdomain.com
   CLIENT_BACKEND_URL=https://yourdomain.com
   STATIC_URL_BASE=https://yourdomain.com
   STATIC_FILES_URL=https://yourdomain.com
   CORS_ORIGINS=https://yourdomain.com,http://yourdomain.com
   ```

3. **Deploy the application:**
   ```bash
   docker-compose -f docker-compose.prebuilt.yml --env-file .env.production up -d
   ```

## Configuration for Different Scenarios

### Using IP Address Instead of Domain

If you don't have a domain name, you can use your VPS IP address:

```env
DOMAIN=123.456.789.012
CLIENT_BACKEND_URL=http://123.456.789.012
STATIC_URL_BASE=http://123.456.789.012
STATIC_FILES_URL=http://123.456.789.012
CORS_ORIGINS=http://123.456.789.012
```

### Using a Subdomain

```env
DOMAIN=culicidae.yourdomain.com
CLIENT_BACKEND_URL=https://culicidae.yourdomain.com
STATIC_URL_BASE=https://culicidae.yourdomain.com
STATIC_FILES_URL=https://culicidae.yourdomain.com
CORS_ORIGINS=https://culicidae.yourdomain.com
```

### Using Custom Port

If you need to run on a custom port:

```env
DOMAIN=yourdomain.com:8080
CLIENT_BACKEND_URL=https://yourdomain.com:8080
STATIC_URL_BASE=https://yourdomain.com:8080
STATIC_FILES_URL=https://yourdomain.com:8080
CORS_ORIGINS=https://yourdomain.com:8080
```

## Docker Registry Deployment

If you want to push your images to a Docker registry (Docker Hub, AWS ECR, etc.):

1. **Build and tag images:**
   ```bash
   .\scripts\build-docker.ps1 "1.0.0"
   docker tag culicidaelab-backend:1.0.0 your-registry/culicidaelab-backend:1.0.0
   docker tag culicidaelab-frontend:1.0.0 your-registry/culicidaelab-frontend:1.0.0
   docker tag culicidaelab-nginx:1.0.0 your-registry/culicidaelab-nginx:1.0.0
   ```

2. **Push to registry:**
   ```bash
   docker push your-registry/culicidaelab-backend:1.0.0
   docker push your-registry/culicidaelab-frontend:1.0.0
   docker push your-registry/culicidaelab-nginx:1.0.0
   ```

3. **Update `.env.production`:**
   ```env
   REGISTRY=your-registry/
   VERSION=1.0.0
   ```

## SSL/HTTPS Setup

For production, you should use HTTPS. The nginx container is configured to handle SSL certificates.

1. **Place your SSL certificates** in the `ssl_certs` volume or mount them:
   ```yaml
   volumes:
     - /path/to/your/ssl/certs:/etc/nginx/ssl:ro
   ```

2. **Update nginx configuration** if needed for your specific SSL setup.

## Monitoring and Logs

### Using utility scripts (recommended):
```bash
# Check overall status and health
./scripts/production-status.sh

# View logs (all services)
./scripts/production-logs.sh

# View logs for specific service
./scripts/production-logs.sh backend

# Stop production deployment
./scripts/production-stop.sh

# Update to new version
./scripts/production-update.sh 1.0.1
```

### Manual commands:
```bash
# All services logs
docker-compose -f docker-compose.prebuilt.yml --env-file .env.production logs -f

# Specific service logs
docker-compose -f docker-compose.prebuilt.yml --env-file .env.production logs -f backend

# Check service status
docker-compose -f docker-compose.prebuilt.yml --env-file .env.production ps

# Health checks
curl http://yourdomain.com/health
curl http://yourdomain.com/api/health
```

## Troubleshooting

### Static files not loading:
1. Check that `STATIC_URL_BASE` matches your domain
2. Verify nginx is serving static files correctly
3. Check CORS settings if accessing from different domain

### API calls failing:
1. Verify `CLIENT_BACKEND_URL` and `SERVER_BACKEND_URL` are correct
2. Check that services can communicate within Docker network
3. Verify CORS origins include your domain

### Container startup issues:
1. Check logs: `docker logs culicidaelab_backend_prebuilt`
2. Verify environment variables are set correctly
3. Ensure all required volumes are mounted

## Security Considerations

1. **Use HTTPS** in production
2. **Set strong passwords** for any databases
3. **Configure firewall** to only allow necessary ports
4. **Keep Docker images updated**
5. **Use non-root users** in containers (already configured)
6. **Set up log rotation** to prevent disk space issues

## Updating the Application

1. **Pull new images:**
   ```bash
   docker-compose -f docker-compose.prebuilt.yml --env-file .env.production pull
   ```

2. **Restart services:**
   ```bash
   docker-compose -f docker-compose.prebuilt.yml --env-file .env.production up -d
   ```

3. **Clean up old images:**
   ```bash
   docker image prune -f
   ```
