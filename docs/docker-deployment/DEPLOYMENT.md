# CulicidaeLab Docker Deployment Guide

This guide provides comprehensive instructions for deploying the CulicidaeLab application using Docker containers in both development and production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Environment Configuration](#environment-configuration)
- [Production Deployment](#production-deployment)
- [Development Setup](#development-setup)
- [SSL Certificate Management](#ssl-certificate-management)
- [Backup and Recovery](#backup-and-recovery)
- [Monitoring and Health Checks](#monitoring-and-health-checks)
- [Troubleshooting](#troubleshooting)
- [Maintenance Procedures](#maintenance-procedures)
- [Security Considerations](#security-considerations)

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended)
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Disk Space**: Minimum 10GB free space
- **CPU**: 2+ cores recommended

### Required Software

```bash
# Docker Engine (20.10+)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose (2.0+)
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Additional utilities
sudo apt update
sudo apt install -y curl jq bc sqlite3 openssl
```

### Network Requirements

- **Ports**: 80 (HTTP), 443 (HTTPS)
- **Domain**: Valid domain name for SSL certificates (production only)
- **DNS**: Domain must point to server IP address

## Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd culicidaelab-server

# Make scripts executable (Linux/Mac)
chmod +x scripts/*.sh

# Copy environment template
cp .env.prod.example .env.prod
```

### 2. Configure Environment

Edit `.env.prod` with your settings:

```bash
# Required: Set your domain name
DOMAIN_NAME=your-domain.com
CERTBOT_EMAIL=admin@your-domain.com
```

### 3. Deploy

```bash
# Production deployment
sudo ./scripts/deploy.sh

# Development deployment
docker-compose -f docker-compose.dev.yml up -d
```

## Environment Configuration

### Production Environment (`.env.prod`)

```bash
# SSL/TLS Configuration
DOMAIN_NAME=your-domain.com
CERTBOT_EMAIL=admin@your-domain.com

# Application Configuration
CULICIDAELAB_DATABASE_PATH=/app/data/culicidaelab.db
CULICIDAELAB_SAVE_PREDICTED_IMAGES=true
CULICIDAELAB_BACKEND_CORS_ORIGINS=https://your-domain.com

# Security Configuration
SSL_CERT_PATH=/etc/letsencrypt/live/your-domain.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/your-domain.com/privkey.pem

# Performance Configuration
WORKERS=2
MAX_CONNECTIONS=1000

# Logging Configuration
LOG_LEVEL=INFO
JSON_LOGGING=true

# Backup Configuration
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE="0 2 * * *"

# Resource Limits
BACKEND_CPU_LIMIT=1.0
BACKEND_MEMORY_LIMIT=1G
FRONTEND_CPU_LIMIT=0.5
FRONTEND_MEMORY_LIMIT=512M
NGINX_CPU_LIMIT=0.5
NGINX_MEMORY_LIMIT=256M
```

### Development Environment (`.env.dev`)

```bash
# Development Mode
ENVIRONMENT=development
DEBUG=true

# Application Configuration
CULICIDAELAB_DATABASE_PATH=/app/data/culicidaelab_dev.db
CULICIDAELAB_BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8765
BACKEND_URL=http://localhost:8000

# Development Tools
SOLARA_DEBUG=true
FASTAPI_ENV=development
RELOAD=true

# Ports (exposed to host)
BACKEND_PORT=8000
FRONTEND_PORT=8765
NGINX_PORT=80
ADMINER_PORT=8080
DOZZLE_PORT=9999

# Security (relaxed for development)
SSL_ENABLED=false
ALLOW_INSECURE=true
CORS_ALLOW_ALL=true
```

### Environment Variables Reference

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DOMAIN_NAME` | Primary domain for SSL certificates | - | Yes (prod) |
| `CERTBOT_EMAIL` | Email for Let's Encrypt notifications | - | Yes (prod) |
| `CULICIDAELAB_DATABASE_PATH` | Database file path | `/app/data/culicidaelab.db` | No |
| `CULICIDAELAB_SAVE_PREDICTED_IMAGES` | Save prediction images | `true` | No |
| `CULICIDAELAB_BACKEND_CORS_ORIGINS` | Allowed CORS origins | - | Yes |
| `BACKEND_URL` | Frontend backend URL | `http://backend:8000` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `WORKERS` | Backend worker processes | `2` | No |
| `BACKUP_RETENTION_DAYS` | Backup retention period | `30` | No |

## Production Deployment

### Automated Deployment

The recommended way to deploy in production is using the automated deployment script:

```bash
# Full deployment with backup
sudo ./scripts/deploy.sh

# Available options
sudo ./scripts/deploy.sh --help
```

### Manual Deployment Steps

If you prefer manual deployment:

```bash
# 1. Prepare environment
sudo mkdir -p /var/lib/culicidaelab/{data,static}
sudo mkdir -p /var/log/culicidaelab
sudo mkdir -p /var/backups/culicidaelab

# 2. Configure environment
cp .env.prod.example .env.prod
# Edit .env.prod with your settings

# 3. Build and start services
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# 4. Verify deployment
./scripts/health-check.sh
```

### Service Architecture

```
Internet → nginx (80/443) → {
    /api/* → backend:8000 (FastAPI)
    /static/* → static files
    /* → frontend:8765 (Solara)
}
```

### Container Services

| Service | Container Name | Purpose | Ports |
|---------|----------------|---------|-------|
| nginx | `culicidaelab_nginx_prod` | Reverse proxy, SSL termination | 80, 443 |
| backend | `culicidaelab_backend_prod` | FastAPI application | 8000 (internal) |
| frontend | `culicidaelab_frontend_prod` | Solara web interface | 8765 (internal) |
| certbot | `culicidaelab_certbot_prod` | SSL certificate management | - |

## Development Setup

### Quick Development Start

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Access services
# Frontend: http://localhost:8765
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Adminer (DB): http://localhost:8080
# Logs: http://localhost:9999
```

### Development Features

- **Hot Reload**: Code changes automatically reload services
- **Debug Mode**: Enhanced logging and error reporting
- **Development Tools**: Adminer for database management, Dozzle for log viewing
- **Volume Mounts**: Live code editing without rebuilds
- **Relaxed Security**: CORS and SSL disabled for easier development

### Development Workflow

```bash
# Start services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Restart specific service
docker-compose -f docker-compose.dev.yml restart backend

# Stop services
docker-compose -f docker-compose.dev.yml down
```

## SSL Certificate Management

### Automatic Certificate Generation

SSL certificates are automatically managed by Certbot:

```bash
# Certificates are automatically:
# 1. Generated on first deployment
# 2. Renewed every 12 hours (if needed)
# 3. Stored in /etc/letsencrypt/
```

### Manual Certificate Operations

```bash
# Force certificate renewal
docker exec culicidaelab_certbot_prod certbot renew --force-renewal

# Check certificate status
openssl x509 -in /etc/letsencrypt/live/your-domain.com/fullchain.pem -text -noout

# Test certificate
curl -I https://your-domain.com/
```

### Certificate Troubleshooting

**Common Issues:**

1. **Domain not pointing to server**
   ```bash
   # Check DNS resolution
   nslookup your-domain.com
   ```

2. **Port 80 blocked**
   ```bash
   # Check if port 80 is accessible
   curl -I http://your-domain.com/
   ```

3. **Rate limiting**
   ```bash
   # Use staging environment for testing
   # Edit certbot command to add --staging flag
   ```

## Backup and Recovery

### Automated Backups

```bash
# Create backup
sudo ./scripts/backup.sh

# Create compressed backup
sudo ./scripts/backup.sh --compress

# Set retention period
sudo ./scripts/backup.sh --retention-days 14
```

### Backup Components

- **Database**: SQLite database file
- **Configuration**: Environment files, Docker Compose files
- **SSL Certificates**: Let's Encrypt certificates and keys
- **Static Files**: Uploaded images and generated content
- **Logs**: Application and system logs

### Backup Schedule

Set up automated backups with cron:

```bash
# Edit crontab
sudo crontab -e

# Add daily backup at 2 AM
0 2 * * * /path/to/culicidaelab/scripts/backup.sh --compress

# Add weekly cleanup
0 3 * * 0 /path/to/culicidaelab/scripts/backup.sh --retention-days 30
```

### Recovery Procedures

```bash
# List available backups
sudo ./scripts/backup.sh --list

# Verify backup integrity
sudo ./scripts/backup.sh --verify 20241019_143022

# Perform rollback
sudo ./scripts/rollback.sh 20241019_143022

# Dry run (preview changes)
sudo ./scripts/rollback.sh 20241019_143022 --dry-run
```

## Monitoring and Health Checks

### Health Check Script

```bash
# Basic health check
./scripts/health-check.sh

# Verbose output
./scripts/health-check.sh --verbose

# JSON output (for monitoring systems)
./scripts/health-check.sh --json
```

### Health Check Components

- **Docker Services**: Container status and health
- **API Endpoints**: Backend health and response times
- **SSL Certificates**: Certificate validity and expiration
- **Database**: Connectivity and integrity
- **System Resources**: Disk space and memory usage
- **Network**: Internal and external connectivity

### Monitoring Integration

```bash
# Integrate with monitoring systems
./scripts/health-check.sh --json | curl -X POST -H "Content-Type: application/json" -d @- https://monitoring.example.com/api/health

# Set up monitoring cron job
*/5 * * * * /path/to/culicidaelab/scripts/health-check.sh --json > /var/log/culicidaelab/health.json
```

### Log Management

```bash
# View application logs
docker-compose -f docker-compose.prod.yml logs -f

# View specific service logs
docker logs culicidaelab_backend_prod

# View nginx access logs
tail -f /var/log/culicidaelab/nginx/access.log

# View system logs
tail -f /var/log/culicidaelab/deployment.log
```

## Troubleshooting

### Common Issues

#### 1. Services Not Starting

**Symptoms**: Containers exit immediately or fail to start

**Diagnosis**:
```bash
# Check container status
docker-compose -f docker-compose.prod.yml ps

# View container logs
docker-compose -f docker-compose.prod.yml logs

# Check system resources
df -h
free -h
```

**Solutions**:
- Check disk space (need >1GB free)
- Verify environment configuration
- Check port conflicts
- Review Docker daemon status

#### 2. SSL Certificate Issues

**Symptoms**: HTTPS not working, certificate errors

**Diagnosis**:
```bash
# Check certificate files
ls -la /etc/letsencrypt/live/your-domain.com/

# Test certificate
openssl x509 -in /etc/letsencrypt/live/your-domain.com/fullchain.pem -text -noout

# Check DNS
nslookup your-domain.com
```

**Solutions**:
- Verify domain DNS points to server
- Check firewall allows ports 80/443
- Ensure domain is accessible from internet
- Check Let's Encrypt rate limits

#### 3. Database Connection Issues

**Symptoms**: Backend API errors, database not accessible

**Diagnosis**:
```bash
# Check database file
docker exec culicidaelab_backend_prod ls -la /app/data/

# Test database connection
docker exec culicidaelab_backend_prod sqlite3 /app/data/culicidaelab.db ".tables"

# Check volume mounts
docker volume inspect backend_data
```

**Solutions**:
- Verify database file permissions
- Check volume mount configuration
- Restore from backup if corrupted
- Check disk space for database volume

#### 4. Network Connectivity Issues

**Symptoms**: Services can't communicate, external requests fail

**Diagnosis**:
```bash
# Check Docker network
docker network ls
docker network inspect culicidaelab_network

# Test internal connectivity
docker exec culicidaelab_frontend_prod curl http://backend:8000/api/health

# Check external connectivity
curl -I http://localhost/
```

**Solutions**:
- Verify Docker network configuration
- Check firewall rules
- Restart Docker daemon if needed
- Verify service dependencies

### Performance Issues

#### High Memory Usage

```bash
# Check container memory usage
docker stats

# Check system memory
free -h

# Adjust resource limits in docker-compose.prod.yml
```

#### Slow Response Times

```bash
# Check response times
./scripts/health-check.sh --verbose

# Monitor container performance
docker stats --no-stream

# Check nginx logs for slow requests
tail -f /var/log/culicidaelab/nginx/access.log
```

### Recovery Procedures

#### Complete System Recovery

```bash
# 1. Stop all services
docker-compose -f docker-compose.prod.yml down

# 2. Restore from backup
sudo ./scripts/rollback.sh <backup_id>

# 3. Verify recovery
./scripts/health-check.sh
```

#### Partial Recovery

```bash
# Restore only database
sudo ./scripts/rollback.sh <backup_id> --component database

# Restore only configuration
sudo ./scripts/rollback.sh <backup_id> --component config
```

## Maintenance Procedures

### Regular Maintenance Tasks

#### Daily
- Monitor health check results
- Review application logs
- Check disk space usage

#### Weekly
- Review backup integrity
- Update system packages
- Check SSL certificate expiration

#### Monthly
- Clean up old Docker images
- Review and rotate logs
- Update application dependencies
- Security audit

### Maintenance Commands

```bash
# Clean up Docker resources
docker system prune -f

# Update system packages
sudo apt update && sudo apt upgrade -y

# Rotate logs
sudo logrotate /etc/logrotate.d/culicidaelab

# Check for security updates
sudo unattended-upgrades --dry-run
```

### Update Procedures

#### Application Updates

```bash
# 1. Create backup
sudo ./scripts/backup.sh --compress

# 2. Pull latest code
git pull origin main

# 3. Deploy updates
sudo ./scripts/deploy.sh

# 4. Verify deployment
./scripts/health-check.sh
```

#### System Updates

```bash
# 1. Create system backup
sudo ./scripts/backup.sh --compress

# 2. Update packages
sudo apt update && sudo apt upgrade -y

# 3. Restart services if needed
sudo ./scripts/deploy.sh

# 4. Verify system health
./scripts/health-check.sh
```

## Security Considerations

### Security Best Practices

1. **Keep System Updated**
   ```bash
   # Enable automatic security updates
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

2. **Firewall Configuration**
   ```bash
   # Configure UFW firewall
   sudo ufw default deny incoming
   sudo ufw default allow outgoing
   sudo ufw allow ssh
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

3. **SSL/TLS Security**
   - Use strong SSL configurations
   - Enable HSTS headers
   - Regular certificate monitoring
   - Disable weak cipher suites

4. **Container Security**
   - Run containers as non-root users
   - Use minimal base images
   - Regular security scanning
   - Limit container resources

5. **Access Control**
   - Use SSH key authentication
   - Disable root SSH login
   - Implement fail2ban
   - Regular access audits

### Security Monitoring

```bash
# Check for security updates
sudo apt list --upgradable | grep -i security

# Scan for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image culicidaelab_backend_prod

# Monitor failed login attempts
sudo tail -f /var/log/auth.log | grep "Failed password"
```

### Incident Response

1. **Security Incident Detection**
   - Monitor logs for suspicious activity
   - Set up automated alerts
   - Regular security audits

2. **Incident Response Steps**
   ```bash
   # 1. Isolate affected systems
   sudo ./scripts/deploy.sh --backup
   docker-compose -f docker-compose.prod.yml down

   # 2. Investigate and document
   # Review logs, identify attack vectors

   # 3. Remediate and recover
   # Apply security patches, restore from clean backup

   # 4. Monitor and prevent
   # Implement additional security measures
   ```

## Support and Resources

### Documentation
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [Nginx Documentation](https://nginx.org/en/docs/)

### Community Support
- [Docker Community Forums](https://forums.docker.com/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/docker)
- [GitHub Issues](https://github.com/your-repo/issues)


---

**Last Updated**: October 2025
**Version**: 1.0
**Maintainer**: CulicidaeLab Team
