# CulicidaeLab Deployment Scripts

This directory contains scripts for deploying and managing CulicidaeLab in different environments.

## Production Deployment Scripts

### Main Deployment Script

**`deploy-production.sh`** - Main production deployment script (Bash)
```bash
./scripts/deploy-production.sh -d yourdomain.com [options]
```

**`deploy-production.ps1`** - Main production deployment script (PowerShell)
```powershell
.\scripts\deploy-production.ps1 -Domain "yourdomain.com" [options]
```

### Production Management Scripts (Bash)

**`production-status.sh`** - Check deployment status and health
```bash
./scripts/production-status.sh
```

**`production-logs.sh`** - View application logs
```bash
./scripts/production-logs.sh [service_name]
```

**`production-stop.sh`** - Stop production deployment
```bash
./scripts/production-stop.sh
```

**`production-update.sh`** - Update to new version
```bash
./scripts/production-update.sh [version]
```

## Local Development Scripts

**`build-docker.ps1`** - Build Docker images locally
```powershell
.\scripts\build-docker.ps1 "version"
```

**`run-local.ps1`** - Run local development environment
```powershell
.\scripts\run-local.ps1 "version"
```

## Usage Examples

### Deploy to production with domain:
```bash
./scripts/deploy-production.sh -d myapp.example.com -v 1.0.0
```

### Deploy to production with IP address:
```bash
./scripts/deploy-production.sh -d 192.168.1.100 -i -p http
```

### Check production status:
```bash
./scripts/production-status.sh
```

### View logs:
```bash
# All services
./scripts/production-logs.sh

# Specific service
./scripts/production-logs.sh backend
```

### Update production:
```bash
./scripts/production-update.sh 1.0.1
```

### Stop production:
```bash
./scripts/production-stop.sh
```

## Script Options

### deploy-production.sh options:
- `-d, --domain DOMAIN` - Your domain name or IP address (required)
- `-v, --version VERSION` - Docker image version (default: latest)
- `-p, --protocol PROTOCOL` - Protocol: http or https (default: https)
- `-r, --registry REGISTRY` - Docker registry prefix (optional)
- `-i, --ip` - Treat domain as IP address (forces HTTP)
- `-h, --help` - Show help message

## Prerequisites

- Docker and Docker Compose installed
- Bash shell (for .sh scripts) or PowerShell (for .ps1 scripts)
- Network access to pull Docker images (if using registry)
- Proper firewall configuration for ports 80/443

## File Permissions

On Linux/macOS, make scripts executable:
```bash
chmod +x scripts/*.sh
```

## Environment Files

The deployment scripts create `.env.production` with your configuration. This file contains:
- Domain/IP configuration
- Protocol settings (HTTP/HTTPS)
- Docker image versions
- Environment-specific settings

Keep this file secure and don't commit it to version control if it contains sensitive information.
