# CulicidaeLab Environment Variables Reference

This document provides a comprehensive reference for all environment variables used in the CulicidaeLab Docker deployment.

## Table of Contents

- [Overview](#overview)
- [Production Variables (.env.prod)](#production-variables-envprod)
- [Development Variables (.env.dev)](#development-variables-envdev)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Application Configuration](#application-configuration)
- [Performance Configuration](#performance-configuration)
- [Logging Configuration](#logging-configuration)
- [Security Configuration](#security-configuration)
- [Backup Configuration](#backup-configuration)
- [Resource Limits](#resource-limits)
- [Network Configuration](#network-configuration)
- [Development Tools](#development-tools)
- [Variable Validation](#variable-validation)

## Overview

Environment variables are used to configure the CulicidaeLab application for different deployment environments. Variables are organized into two main files:

- `.env.prod` - Production environment configuration
- `.env.dev` - Development environment configuration

### Variable Naming Convention

- `CULICIDAELAB_*` - Application-specific variables
- `DOMAIN_NAME` - Primary domain configuration
- `CERTBOT_*` - SSL certificate management
- `*_CPU_LIMIT` - Resource limit variables
- `*_PORT` - Port configuration variables

## Production Variables (.env.prod)

### Required Variables

| Variable | Description | Example | Notes |
|----------|-------------|---------|-------|
| `DOMAIN_NAME` | Primary domain name | `example.com` | **Required** for SSL certificates |
| `CERTBOT_EMAIL` | Email for Let's Encrypt | `admin@example.com` | **Required** for certificate notifications |
| `CULICIDAELAB_BACKEND_CORS_ORIGINS` | Allowed CORS origins | `https://example.com` | **Required** for API security |

### SSL/TLS Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DOMAIN_NAME` | Primary domain for SSL | - | `culicidaelab.example.com` |
| `CERTBOT_EMAIL` | Let's Encrypt email | - | `ssl-admin@example.com` |
| `SSL_CERT_PATH` | Certificate file path | `/etc/letsencrypt/live/${DOMAIN_NAME}/fullchain.pem` | Auto-generated |
| `SSL_KEY_PATH` | Private key path | `/etc/letsencrypt/live/${DOMAIN_NAME}/privkey.pem` | Auto-generated |

### Application Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `CULICIDAELAB_DATABASE_PATH` | Database file location | `/app/data/culicidaelab.db` | `/app/data/production.db` |
| `CULICIDAELAB_SAVE_PREDICTED_IMAGES` | Save prediction images | `true` | `true` or `false` |
| `BACKEND_URL` | Frontend backend URL | `http://backend:8000` | Internal Docker network |
| `ENVIRONMENT` | Environment name | `production` | `production`, `staging`, `development` |

### Performance Configuration

| Variable | Description | Default | Range | Notes |
|----------|-------------|---------|-------|-------|
| `WORKERS` | Backend worker processes | `2` | 1-8 | Based on CPU cores |
| `MAX_CONNECTIONS` | Max concurrent connections | `1000` | 100-5000 | Adjust based on load |
| `HEALTH_CHECK_INTERVAL` | Health check frequency (seconds) | `30` | 10-300 | Lower = more frequent |
| `HEALTH_CHECK_TIMEOUT` | Health check timeout (seconds) | `10` | 5-60 | Request timeout |

### Logging Configuration

| Variable | Description | Default | Options |
|----------|-------------|---------|---------|
| `LOG_LEVEL` | Application log level | `INFO` | `DEBUG`, `INFO`, `WARN`, `ERROR` |
| `JSON_LOGGING` | Enable JSON log format | `true` | `true`, `false` |

### Backup Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `BACKUP_RETENTION_DAYS` | Backup retention period | `30` | `7`, `30`, `90` |
| `BACKUP_SCHEDULE` | Cron schedule for backups | `"0 2 * * *"` | Daily at 2 AM |

### Resource Limits

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `BACKEND_CPU_LIMIT` | Backend CPU limit | `1.0` | `0.5`, `2.0` |
| `BACKEND_MEMORY_LIMIT` | Backend memory limit | `1G` | `512M`, `2G` |
| `BACKEND_CPU_RESERVATION` | Backend CPU reservation | `0.5` | `0.25`, `1.0` |
| `BACKEND_MEMORY_RESERVATION` | Backend memory reservation | `512M` | `256M`, `1G` |
| `FRONTEND_CPU_LIMIT` | Frontend CPU limit | `0.5` | `0.25`, `1.0` |
| `FRONTEND_MEMORY_LIMIT` | Frontend memory limit | `512M` | `256M`, `1G` |
| `NGINX_CPU_LIMIT` | Nginx CPU limit | `0.5` | `0.25`, `1.0` |
| `NGINX_MEMORY_LIMIT` | Nginx memory limit | `256M` | `128M`, `512M` |

### Network Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `NETWORK_SUBNET` | Docker network subnet | `172.20.0.0/16` | `172.21.0.0/16` |

### Data Persistence

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DATA_HOST_PATH` | Host path for data | `/var/lib/culicidaelab/data` | Custom path |
| `CERTS_HOST_PATH` | Host path for certificates | `/etc/letsencrypt` | Custom path |
| `STATIC_HOST_PATH` | Host path for static files | `/var/lib/culicidaelab/static` | Custom path |

## Development Variables (.env.dev)

### Development Mode Configuration

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `ENVIRONMENT` | Environment name | `development` | Enables dev features |
| `DEBUG` | Enable debug mode | `true` | Enhanced logging |
| `FASTAPI_ENV` | FastAPI environment | `development` | Enables auto-reload |
| `SOLARA_DEBUG` | Solara debug mode | `true` | Frontend debugging |

### Development Database

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `CULICIDAELAB_DATABASE_PATH` | Dev database path | `/app/data/culicidaelab_dev.db` | Separate from production |
| `DATABASE_TYPE` | Database type | `sqlite` | Development only |
| `DATABASE_FILE` | Database filename | `culicidaelab_dev.db` | Local development |

### Development CORS

| Variable | Description | Default |
|----------|-------------|---------|
| `CULICIDAELAB_BACKEND_CORS_ORIGINS` | Allowed origins | `http://localhost:3000,http://localhost:8765,http://127.0.0.1:3000,http://127.0.0.1:8765` |
| `CORS_ALLOW_ALL` | Allow all origins | `true` |

### Development Ports

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `BACKEND_PORT` | Backend port | `8000` | Exposed to host |
| `FRONTEND_PORT` | Frontend port | `8765` | Exposed to host |
| `NGINX_PORT` | Nginx port | `80` | Exposed to host |
| `ADMINER_PORT` | Database admin port | `8080` | Development tool |
| `DOZZLE_PORT` | Log viewer port | `9999` | Development tool |

### Development Features

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `RELOAD` | Enable auto-reload | `true` | Hot reload for development |
| `WATCH_FILES` | Enable file watching | `true` | Monitor file changes |
| `WATCH_PATTERNS` | File patterns to watch | `*.py,*.html,*.css,*.js` | File extensions |

### Development Security (Relaxed)

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `SSL_ENABLED` | Enable SSL | `false` | Disabled for local dev |
| `ALLOW_INSECURE` | Allow insecure connections | `true` | Development only |

### Development Logging

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `LOG_LEVEL` | Log level | `DEBUG` | Verbose logging |
| `JSON_LOGGING` | JSON log format | `false` | Human-readable logs |
| `VERBOSE_LOGGING` | Verbose logging | `true` | Extra debug info |
| `LOG_TO_CONSOLE` | Console logging | `true` | Direct output |

### Development Paths

| Variable | Description | Default | Notes |
|----------|-------------|---------|-------|
| `BACKEND_CODE_PATH` | Backend code path | `./backend` | Volume mount |
| `FRONTEND_CODE_PATH` | Frontend code path | `./frontend` | Volume mount |
| `DATA_PATH` | Data directory | `./data` | Local directory |
| `STATIC_PATH` | Static files path | `./static` | Local directory |

## Variable Validation

### Required Variable Check

```bash
#!/bin/bash
# validate-env.sh - Environment variable validation script

check_required_vars() {
    local env_file=$1
    local required_vars=("DOMAIN_NAME" "CERTBOT_EMAIL" "CULICIDAELAB_BACKEND_CORS_ORIGINS")

    echo "Validating required variables in $env_file..."

    for var in "${required_vars[@]}"; do
        if ! grep -q "^$var=" "$env_file"; then
            echo "ERROR: Required variable $var not found in $env_file"
            return 1
        fi

        local value=$(grep "^$var=" "$env_file" | cut -d'=' -f2)
        if [ -z "$value" ] || [ "$value" = "your-domain.com" ] || [ "$value" = "admin@your-domain.com" ]; then
            echo "ERROR: Variable $var has default/empty value in $env_file"
            return 1
        fi
    done

    echo "All required variables validated successfully"
    return 0
}

# Usage
check_required_vars ".env.prod"
```

### Variable Format Validation

```bash
validate_formats() {
    local env_file=$1

    # Validate email format
    local email=$(grep "^CERTBOT_EMAIL=" "$env_file" | cut -d'=' -f2)
    if [[ ! "$email" =~ ^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$ ]]; then
        echo "ERROR: Invalid email format for CERTBOT_EMAIL"
        return 1
    fi

    # Validate domain format
    local domain=$(grep "^DOMAIN_NAME=" "$env_file" | cut -d'=' -f2)
    if [[ ! "$domain" =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$ ]]; then
        echo "ERROR: Invalid domain format for DOMAIN_NAME"
        return 1
    fi

    # Validate resource limits
    local cpu_limit=$(grep "^BACKEND_CPU_LIMIT=" "$env_file" | cut -d'=' -f2)
    if [[ ! "$cpu_limit" =~ ^[0-9]+\.?[0-9]*$ ]]; then
        echo "ERROR: Invalid CPU limit format"
        return 1
    fi

    echo "All format validations passed"
    return 0
}
```

### Environment Comparison

```bash
compare_environments() {
    echo "=== Environment Variable Comparison ==="
    echo

    echo "Production-only variables:"
    comm -23 <(grep "^[A-Z]" .env.prod | cut -d'=' -f1 | sort) <(grep "^[A-Z]" .env.dev | cut -d'=' -f1 | sort)

    echo
    echo "Development-only variables:"
    comm -13 <(grep "^[A-Z]" .env.prod | cut -d'=' -f1 | sort) <(grep "^[A-Z]" .env.dev | cut -d'=' -f1 | sort)

    echo
    echo "Common variables with different values:"
    while IFS= read -r var; do
        prod_val=$(grep "^$var=" .env.prod | cut -d'=' -f2)
        dev_val=$(grep "^$var=" .env.dev | cut -d'=' -f2)
        if [ "$prod_val" != "$dev_val" ]; then
            echo "$var: prod='$prod_val' dev='$dev_val'"
        fi
    done < <(comm -12 <(grep "^[A-Z]" .env.prod | cut -d'=' -f1 | sort) <(grep "^[A-Z]" .env.dev | cut -d'=' -f1 | sort))
}
```

## Environment Templates

### Production Template (.env.prod.example)

```bash
# SSL/TLS Configuration
DOMAIN_NAME=your-domain.com
CERTBOT_EMAIL=admin@your-domain.com

# Application Configuration
CULICIDAELAB_DATABASE_PATH=/app/data/culicidaelab.db
CULICIDAELAB_SAVE_PREDICTED_IMAGES=true
CULICIDAELAB_BACKEND_CORS_ORIGINS=https://your-domain.com
BACKEND_URL=http://backend:8000
ENVIRONMENT=production

# Performance Configuration
WORKERS=2
MAX_CONNECTIONS=1000
HEALTH_CHECK_INTERVAL=30
HEALTH_CHECK_TIMEOUT=10

# Logging Configuration
LOG_LEVEL=INFO
JSON_LOGGING=true

# Backup Configuration
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE="0 2 * * *"

# Resource Limits
BACKEND_CPU_LIMIT=1.0
BACKEND_MEMORY_LIMIT=1G
BACKEND_CPU_RESERVATION=0.5
BACKEND_MEMORY_RESERVATION=512M
FRONTEND_CPU_LIMIT=0.5
FRONTEND_MEMORY_LIMIT=512M
FRONTEND_CPU_RESERVATION=0.25
FRONTEND_MEMORY_RESERVATION=256M
NGINX_CPU_LIMIT=0.5
NGINX_MEMORY_LIMIT=256M
NGINX_CPU_RESERVATION=0.1
NGINX_MEMORY_RESERVATION=128M

# Network Configuration
NETWORK_SUBNET=172.20.0.0/16
```

### Development Template (.env.dev.example)

```bash
# Development Mode
ENVIRONMENT=development
DEBUG=true
FASTAPI_ENV=development
SOLARA_DEBUG=true

# Application Configuration
CULICIDAELAB_DATABASE_PATH=/app/data/culicidaelab_dev.db
CULICIDAELAB_SAVE_PREDICTED_IMAGES=true
CULICIDAELAB_BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:8765,http://127.0.0.1:3000,http://127.0.0.1:8765
BACKEND_URL=http://localhost:8000

# Development Features
RELOAD=true
WATCH_FILES=true
WATCH_PATTERNS=*.py,*.html,*.css,*.js

# Development Ports
BACKEND_PORT=8000
FRONTEND_PORT=8765
NGINX_PORT=80
ADMINER_PORT=8080
DOZZLE_PORT=9999

# Development Security (Relaxed)
SSL_ENABLED=false
ALLOW_INSECURE=true
CORS_ALLOW_ALL=true

# Development Logging
LOG_LEVEL=DEBUG
JSON_LOGGING=false
VERBOSE_LOGGING=true
LOG_TO_CONSOLE=true

# Development Paths
BACKEND_CODE_PATH=./backend
FRONTEND_CODE_PATH=./frontend
DATA_PATH=./data
STATIC_PATH=./static

# Network Configuration
NETWORK_SUBNET=172.21.0.0/16
```

## Best Practices

### Security Best Practices

1. **Never commit .env files to version control**
   ```bash
   # Add to .gitignore
   .env
   .env.prod
   .env.dev
   .env.local
   ```

2. **Use strong, unique values for production**
   ```bash
   # Generate secure values
   openssl rand -base64 32  # For secrets
   ```

3. **Validate environment variables on startup**
   ```bash
   # Add validation to deployment scripts
   ./scripts/validate-env.sh .env.prod
   ```

4. **Use different values for different environments**
   ```bash
   # Never use production values in development
   # Use separate domains, databases, etc.
   ```

### Performance Best Practices

1. **Adjust resource limits based on usage**
   ```bash
   # Monitor actual usage
   docker stats --no-stream

   # Adjust limits accordingly
   BACKEND_MEMORY_LIMIT=2G  # If needed
   ```

2. **Optimize worker processes**
   ```bash
   # Rule of thumb: 2 * CPU cores
   WORKERS=$(nproc --all)
   ```

3. **Configure appropriate timeouts**
   ```bash
   # Balance between responsiveness and stability
   HEALTH_CHECK_TIMEOUT=10  # Reasonable default
   ```

### Maintenance Best Practices

1. **Document all custom variables**
   ```bash
   # Add comments to environment files
   # CUSTOM_VAR=value  # Purpose: explanation
   ```

2. **Regular environment audits**
   ```bash
   # Review and clean up unused variables
   # Update documentation when adding new variables
   ```

3. **Backup environment configurations**
   ```bash
   # Include in backup procedures
   cp .env.prod /backup/env-$(date +%Y%m%d).prod
   ```

---

**Last Updated**: October 2024
**Version**: 1.0
**Maintainer**: CulicidaeLab Team
