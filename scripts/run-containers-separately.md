# Running Containers Separately

This guide shows how to run each container individually for testing and debugging.

## Prerequisites

First, build your images:
```powershell
.\scripts\build-docker.ps1 "0.1.0"
```

## 1. Run Backend Container Only

```powershell
# Run backend container
docker run -d `
  --name culicidaelab-backend-test `
  -p 8000:8000 `
  -e CULICIDAELAB_DATABASE_PATH=/app/data/.lancedb `
  -e CULICIDAELAB_SAVE_PREDICTED_IMAGES=true `
  -e FASTAPI_ENV=development `
  -e DEBUG=true `
  -v ${PWD}/data:/app/data `
  -v ${PWD}/static:/app/static `
  culicidaelab-backend:0.1.0

# Check if it's running
docker ps | findstr backend

# View logs
docker logs culicidaelab-backend-test

# Test the API
curl http://localhost:8000/api/health
```

**Access:** http://localhost:8000

## 2. Run Frontend Container Only

```powershell
# Run frontend container (assumes backend is running)
docker run -d `
  --name culicidaelab-frontend-test `
  -p 8765:8765 `
  -e BACKEND_URL=http://host.docker.internal:8000 `
  -e SOLARA_DEBUG=true `
  culicidaelab-frontend:0.1.0

# Check if it's running
docker ps | findstr frontend

# View logs
docker logs culicidaelab-frontend-test

# Test the frontend
curl http://localhost:8765
```

**Access:** http://localhost:8765

## 3. Run Nginx Container Only

```powershell
# Run nginx container (assumes backend and frontend are running)
docker run -d `
  --name culicidaelab-nginx-test `
  -p 80:80 `
  -v ${PWD}/static:/var/www/static:ro `
  -v ${PWD}/nginx/nginx.dev.conf:/etc/nginx/nginx.conf:ro `
  -e NGINX_ENV=development `
  culicidaelab-nginx:0.1.0

# Check if it's running
docker ps | findstr nginx

# View logs
docker logs culicidaelab-nginx-test

# Test nginx
curl http://localhost
```

**Access:** http://localhost

## 4. Run All Containers with Custom Network

Create a custom network for better communication:

```powershell
# Create network
docker network create culicidaelab-test

# Run backend
docker run -d `
  --name backend-test `
  --network culicidaelab-test `
  -p 8000:8000 `
  -e CULICIDAELAB_DATABASE_PATH=/app/data/culicidaelab.db `
  -e FASTAPI_ENV=development `
  -v ${PWD}/data:/app/data `
  culicidaelab-backend:0.1.0

# Run frontend
docker run -d `
  --name frontend-test `
  --network culicidaelab-test `
  -p 8765:8765 `
  -e BACKEND_URL=http://backend-test:8000 `
  culicidaelab-frontend:0.1.0

# Run nginx
docker run -d `
  --name nginx-test `
  --network culicidaelab-test `
  -p 80:80 `
  -v ${PWD}/static:/var/www/static:ro `
  culicidaelab-nginx:0.1.0
```

## 5. Interactive Mode (for debugging)

Run containers interactively to see real-time output:

```powershell
# Backend interactive
docker run -it --rm `
  -p 8000:8000 `
  -e FASTAPI_ENV=development `
  -v ${PWD}/data:/app/data `
  culicidaelab-backend:0.1.0

# Frontend interactive
docker run -it --rm `
  -p 8765:8765 `
  -e BACKEND_URL=http://host.docker.internal:8000 `
  culicidaelab-frontend:0.1.0
```

## 6. Container Management Commands

```powershell
# List running containers
docker ps

# Stop containers
docker stop culicidaelab-backend-test
docker stop culicidaelab-frontend-test
docker stop culicidaelab-nginx-test

# Remove containers
docker rm culicidaelab-backend-test
docker rm culicidaelab-frontend-test
docker rm culicidaelab-nginx-test

# View logs
docker logs -f culicidaelab-backend-test

# Execute commands inside container
docker exec -it culicidaelab-backend-test /bin/bash

# Inspect container
docker inspect culicidaelab-backend-test
```

## 7. Testing Individual Services

### Backend Testing
```powershell
# Health check
curl http://localhost:8000/api/health

# API documentation
# Visit: http://localhost:8000/docs
```

### Frontend Testing
```powershell
# Frontend health
curl http://localhost:8765

# Visit the app: http://localhost:8765
```

### Nginx Testing
```powershell
# Nginx status
curl http://localhost/health

# Static files
curl http://localhost/static/
```

## 8. Cleanup

```powershell
# Stop and remove all test containers
docker stop $(docker ps -q --filter "name=*test")
docker rm $(docker ps -aq --filter "name=*test")

# Remove test network
docker network rm culicidaelab-test

# Remove unused volumes
docker volume prune
```

## Troubleshooting

### Container won't start
```powershell
# Check container logs
docker logs container-name

# Check if ports are available
netstat -an | findstr :8000
```

### Network connectivity issues
```powershell
# Test network connectivity between containers
docker exec backend-test ping frontend-test

# Check container IP addresses
docker inspect backend-test | findstr IPAddress
```

### Volume mount issues
```powershell
# Check if volumes are mounted correctly
docker exec backend-test ls -la /app/data

# Check Windows path format
echo ${PWD}
```