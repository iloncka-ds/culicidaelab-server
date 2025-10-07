# Production Deployment

This guide covers deploying CulicidaeLab Server to a production environment. The application consists of a FastAPI backend and a Solara frontend that can be deployed together or separately.

## Prerequisites

Before deploying to production, ensure you have:

- Python 3.11 or higher
- Access to a server with at least 4GB RAM and 2 CPU cores
- Domain name and SSL certificate (recommended)
- Database storage (local or cloud-based)
- Model files for species prediction

## Deployment Architecture

CulicidaeLab Server can be deployed in several configurations:

### Single Server Deployment
- Both backend and frontend on the same server
- Suitable for small to medium workloads
- Easier to manage and maintain

### Microservices Deployment
- Backend and frontend on separate servers
- Better scalability and resource allocation
- Requires load balancer configuration

## Environment Setup

### 1. Server Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3.11-dev

# Install system dependencies
sudo apt install build-essential curl git nginx supervisor
```

### 2. Application Setup

```bash
# Clone the repository
git clone https://github.com/your-org/culicidaelab-server.git
cd culicidaelab-server

# Create virtual environment
python3.11 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install uv
uv sync --group production
```

### 3. Environment Configuration

Create production environment file:

```bash
# Copy example environment file
cp backend/.env.example backend/.env

# Edit configuration for production
nano backend/.env
```

Required production environment variables:

```bash
# Database configuration
CULICIDAELAB_DATABASE_PATH="/var/lib/culicidaelab/data/.lancedb"

# Image storage
CULICIDAELAB_SAVE_PREDICTED_IMAGES=1

# Environment
ENVIRONMENT=production

# Security (generate secure values)
SECRET_KEY="your-secure-secret-key-here"
ALLOWED_HOSTS="your-domain.com,www.your-domain.com"

# CORS origins for frontend
CULICIDAELAB_BACKEND_CORS_ORIGINS="https://your-domain.com,https://www.your-domain.com"
```

## Application Deployment

### 1. Backend Deployment

Create systemd service for the backend:

```bash
sudo nano /etc/systemd/system/culicidaelab-backend.service
```

```ini
[Unit]
Description=CulicidaeLab Backend API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/culicidaelab-server
Environment=PATH=/path/to/culicidaelab-server/.venv/bin
ExecStart=/path/to/culicidaelab-server/.venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 2. Frontend Deployment

Create systemd service for the frontend:

```bash
sudo nano /etc/systemd/system/culicidaelab-frontend.service
```

```ini
[Unit]
Description=CulicidaeLab Frontend
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/path/to/culicidaelab-server
Environment=PATH=/path/to/culicidaelab-server/.venv/bin
ExecStart=/path/to/culicidaelab-server/.venv/bin/solara run frontend.main:routes --host 127.0.0.1 --port 8765 --production
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

### 3. Enable and Start Services

```bash
# Enable services
sudo systemctl enable culicidaelab-backend
sudo systemctl enable culicidaelab-frontend

# Start services
sudo systemctl start culicidaelab-backend
sudo systemctl start culicidaelab-frontend

# Check status
sudo systemctl status culicidaelab-backend
sudo systemctl status culicidaelab-frontend
```

## Reverse Proxy Configuration

### Nginx Configuration

Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/culicidaelab
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /path/to/ssl/certificate.crt;
    ssl_certificate_key /path/to/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # Frontend (main application)
    location / {
        proxy_pass http://127.0.0.1:8765;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support for Solara
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Backend API
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Increase timeout for model predictions
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # Static files
    location /static {
        alias /path/to/culicidaelab-server/backend/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # File upload size limit
    client_max_body_size 50M;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/culicidaelab /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Database Setup

### 1. Create Database Directory

```bash
sudo mkdir -p /var/lib/culicidaelab/data
sudo chown -R www-data:www-data /var/lib/culicidaelab
sudo chmod 755 /var/lib/culicidaelab
```

### 2. Initialize Database

```bash
# Run database initialization script if available
cd /path/to/culicidaelab-server
source .venv/bin/activate
python -m backend.scripts.init_database
```

## Model Files Setup

### 1. Download Model Files

```bash
# Create models directory
sudo mkdir -p /var/lib/culicidaelab/models
sudo chown -R www-data:www-data /var/lib/culicidaelab/models

# Download or copy model files
# This depends on your model distribution method
```

### 2. Configure Model Paths

Update your environment configuration to point to the model files:

```bash
# In backend/.env
CULICIDAELAB_MODEL_PATH="/var/lib/culicidaelab/models"
```

## Health Checks and Monitoring

### 1. Application Health Checks

The application provides health check endpoints:

- Backend: `https://your-domain.com/api/health`
- Frontend: Monitor the main application URL

### 2. Log Monitoring

Configure log rotation and monitoring:

```bash
# Create log directories
sudo mkdir -p /var/log/culicidaelab
sudo chown -R www-data:www-data /var/log/culicidaelab

# Configure logrotate
sudo nano /etc/logrotate.d/culicidaelab
```

```
/var/log/culicidaelab/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload culicidaelab-backend
        systemctl reload culicidaelab-frontend
    endscript
}
```

## Backup Strategy

### 1. Database Backup

```bash
#!/bin/bash
# backup-database.sh
BACKUP_DIR="/var/backups/culicidaelab"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/database_$DATE.tar.gz /var/lib/culicidaelab/data/
```

### 2. Application Backup

```bash
#!/bin/bash
# backup-application.sh
BACKUP_DIR="/var/backups/culicidaelab"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/application_$DATE.tar.gz /path/to/culicidaelab-server/
```

## Scaling Considerations

### Horizontal Scaling

For high-traffic deployments:

1. **Load Balancer**: Use nginx or HAProxy to distribute traffic
2. **Multiple Backend Instances**: Run multiple backend workers
3. **Database Scaling**: Consider database clustering or replication
4. **CDN**: Use CDN for static assets and images

### Vertical Scaling

Resource recommendations by load:

- **Small (< 100 users)**: 2 CPU cores, 4GB RAM
- **Medium (100-1000 users)**: 4 CPU cores, 8GB RAM  
- **Large (1000+ users)**: 8+ CPU cores, 16GB+ RAM

## Troubleshooting

### Common Issues

1. **Service Won't Start**
   ```bash
   sudo journalctl -u culicidaelab-backend -f
   sudo journalctl -u culicidaelab-frontend -f
   ```

2. **Permission Issues**
   ```bash
   sudo chown -R www-data:www-data /path/to/culicidaelab-server
   sudo chmod -R 755 /path/to/culicidaelab-server
   ```

3. **Database Connection Issues**
   - Check database path permissions
   - Verify environment variables
   - Check disk space

4. **Model Loading Issues**
   - Verify model file paths
   - Check model file permissions
   - Ensure sufficient memory

### Performance Optimization

1. **Enable Gzip Compression** in Nginx
2. **Configure Caching** for static assets
3. **Optimize Database** queries and indexing
4. **Monitor Resource Usage** with tools like htop, iotop

## Security Checklist

- [ ] SSL/TLS certificates configured
- [ ] Firewall rules configured (only ports 80, 443, 22 open)
- [ ] Regular security updates applied
- [ ] Strong passwords and SSH key authentication
- [ ] Database access restricted
- [ ] Application logs monitored
- [ ] Backup strategy implemented
- [ ] Rate limiting configured
- [ ] CORS origins properly configured