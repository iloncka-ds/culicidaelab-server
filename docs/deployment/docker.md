# Docker Deployment

This guide covers deploying CulicidaeLab Server using Docker containers. Docker provides a consistent, portable deployment environment that simplifies setup and scaling.

## Prerequisites

- Docker Engine 20.10+ installed
- Docker Compose 2.0+ installed
- At least 4GB RAM and 2 CPU cores
- 10GB+ available disk space

## Docker Setup

### 1. Create Dockerfile for Backend

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install uv for faster dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./
COPY backend/ ./backend/

# Install Python dependencies
RUN uv sync --frozen --no-dev

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Create data directories
RUN mkdir -p /app/data /app/models /app/logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uv", "run", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Create Dockerfile for Frontend

Create `frontend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Install uv for faster dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./
COPY frontend/ ./frontend/
COPY backend/config.py ./backend/config.py
COPY backend/__init__.py ./backend/__init__.py

# Install Python dependencies
RUN uv sync --frozen --no-dev

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8765

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8765/ || exit 1

# Start command
CMD ["uv", "run", "solara", "run", "frontend.main:routes", "--host", "0.0.0.0", "--port", "8765", "--production"]
```

### 3. Create Multi-stage Dockerfile (Recommended)

Create `Dockerfile` in project root:

```dockerfile
# Multi-stage build for optimized production image
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Build stage
FROM base as builder

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Production stage
FROM base as production

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Create data directories
RUN mkdir -p /app/data /app/models /app/logs

# Backend image
FROM production as backend
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["/app/.venv/bin/uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend image
FROM production as frontend
EXPOSE 8765
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8765/ || exit 1
CMD ["/app/.venv/bin/solara", "run", "frontend.main:routes", "--host", "0.0.0.0", "--port", "8765", "--production"]
```

## Docker Compose Configuration

### 1. Basic Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      target: backend
    ports:
      - "8000:8000"
    environment:
      - CULICIDAELAB_DATABASE_PATH=/app/data/.lancedb
      - CULICIDAELAB_SAVE_PREDICTED_IMAGES=1
      - ENVIRONMENT=production
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: .
      target: frontend
    ports:
      - "8765:8765"
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8765/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  data:
  models:
  logs:
```

### 2. Production Docker Compose

Create `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      target: backend
    environment:
      - CULICIDAELAB_DATABASE_PATH=/app/data/.lancedb
      - CULICIDAELAB_SAVE_PREDICTED_IMAGES=1
      - ENVIRONMENT=production
    volumes:
      - data:/app/data
      - models:/app/models
      - logs:/app/logs
    restart: unless-stopped
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '1.0'
          memory: 2G
        reservations:
          cpus: '0.5'
          memory: 1G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build:
      context: .
      target: frontend
    environment:
      - BACKEND_URL=http://backend:8000
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
    deploy:
      replicas: 1
      resources:
        limits:
          cpus: '0.5'
          memory: 1G
        reservations:
          cpus: '0.25'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8765/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  redis:
    image: redis:alpine
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: '0.25'
          memory: 256M

volumes:
  data:
    driver: local
  models:
    driver: local
  logs:
    driver: local

networks:
  default:
    driver: bridge
```

## Nginx Configuration for Docker

Create `nginx/nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:8765;
    }

    server {
        listen 80;
        server_name localhost;

        # Redirect HTTP to HTTPS in production
        # return 301 https://$server_name$request_uri;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Backend API
        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Increase timeout for model predictions
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # Health checks
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }

    # HTTPS server (uncomment for production)
    # server {
    #     listen 443 ssl http2;
    #     server_name your-domain.com;
    #     
    #     ssl_certificate /etc/nginx/ssl/certificate.crt;
    #     ssl_certificate_key /etc/nginx/ssl/private.key;
    #     
    #     # Include locations from above
    # }
}
```

## Deployment Commands

### 1. Development Deployment

```bash
# Build and start services
docker-compose up --build

# Run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### 2. Production Deployment

```bash
# Build and start production services
docker-compose -f docker-compose.prod.yml up -d --build

# Scale backend services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Update services
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d --no-deps backend frontend

# View service status
docker-compose -f docker-compose.prod.yml ps
```

### 3. Docker Swarm Deployment

```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.prod.yml culicidaelab

# Scale services
docker service scale culicidaelab_backend=3

# Update service
docker service update --image culicidaelab_backend:latest culicidaelab_backend

# Remove stack
docker stack rm culicidaelab
```

## Environment Variables

### Backend Environment Variables

```bash
# Required
CULICIDAELAB_DATABASE_PATH=/app/data/.lancedb
CULICIDAELAB_SAVE_PREDICTED_IMAGES=1
ENVIRONMENT=production

# Optional
CULICIDAELAB_MODEL_PATH=/app/models
CULICIDAELAB_LOG_LEVEL=INFO
CULICIDAELAB_WORKERS=4
CULICIDAELAB_BACKEND_CORS_ORIGINS=http://localhost:8765
```

### Frontend Environment Variables

```bash
# Backend connection
BACKEND_URL=http://backend:8000
FRONTEND_PORT=8765
FRONTEND_HOST=0.0.0.0
```

## Data Persistence

### 1. Volume Management

```bash
# Create named volumes
docker volume create culicidaelab_data
docker volume create culicidaelab_models
docker volume create culicidaelab_logs

# Backup volumes
docker run --rm -v culicidaelab_data:/data -v $(pwd):/backup alpine tar czf /backup/data-backup.tar.gz /data

# Restore volumes
docker run --rm -v culicidaelab_data:/data -v $(pwd):/backup alpine tar xzf /backup/data-backup.tar.gz -C /
```

### 2. Bind Mounts

```yaml
# In docker-compose.yml
volumes:
  - ./data:/app/data              # Database files
  - ./models:/app/models          # Model files
  - ./logs:/app/logs              # Application logs
  - ./uploads:/app/uploads        # User uploads
```

## Monitoring and Logging

### 1. Container Monitoring

```bash
# Monitor resource usage
docker stats

# View container logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Execute commands in containers
docker-compose exec backend bash
docker-compose exec frontend bash
```

### 2. Log Configuration

Create `docker-compose.override.yml` for logging:

```yaml
version: '3.8'

services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  frontend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Security Best Practices

### 1. Container Security

```dockerfile
# Use non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Remove unnecessary packages
RUN apt-get remove --purge -y build-essential && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Set proper file permissions
RUN chmod -R 755 /app
```

### 2. Network Security

```yaml
# In docker-compose.yml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access

services:
  backend:
    networks:
      - backend
  frontend:
    networks:
      - frontend
      - backend
```

## Troubleshooting

### Common Issues

1. **Container Won't Start**
   ```bash
   docker-compose logs backend
   docker-compose logs frontend
   ```

2. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :8000
   
   # Use different ports
   ports:
     - "8001:8000"  # Map to different host port
   ```

3. **Volume Permission Issues**
   ```bash
   # Fix permissions
   sudo chown -R 1000:1000 ./data
   sudo chmod -R 755 ./data
   ```

4. **Memory Issues**
   ```bash
   # Increase memory limits
   deploy:
     resources:
       limits:
         memory: 4G
   ```

### Performance Optimization

1. **Multi-stage Builds** to reduce image size
2. **Layer Caching** for faster builds
3. **Resource Limits** to prevent resource exhaustion
4. **Health Checks** for proper load balancing
5. **Log Rotation** to manage disk usage

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build and Deploy

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker images
        run: |
          docker build -t culicidaelab-backend --target backend .
          docker build -t culicidaelab-frontend --target frontend .
      
      - name: Deploy to production
        run: |
          docker-compose -f docker-compose.prod.yml up -d
```