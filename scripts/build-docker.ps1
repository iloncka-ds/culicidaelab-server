# Simple Docker build script for CulicidaeLab
# Usage: .\scripts\build-docker.ps1 [version] [registry]

param(
    [string]$Version = "latest",
    [string]$Registry = ""
)

Write-Host "Building CulicidaeLab Docker images..." -ForegroundColor Green

# Build backend
Write-Host "Building backend..." -ForegroundColor Yellow
docker build -f backend/Dockerfile -t culicidaelab-backend:$Version .
if ($LASTEXITCODE -ne 0) { exit 1 }

if ($Registry) {
    docker tag culicidaelab-backend:$Version $Registry/culicidaelab-backend:$Version
    docker tag culicidaelab-backend:$Version $Registry/culicidaelab-backend:latest
}

Write-Host "Backend built successfully" -ForegroundColor Green

# Build frontend (standalone)
Write-Host "Building frontend (standalone)..." -ForegroundColor Yellow
docker build -f frontend/Dockerfile -t culicidaelab-frontend:$Version .
if ($LASTEXITCODE -ne 0) { exit 1 }

if ($Registry) {
    docker tag culicidaelab-frontend:$Version $Registry/culicidaelab-frontend:$Version
    docker tag culicidaelab-frontend:$Version $Registry/culicidaelab-frontend:latest
}

Write-Host "Frontend built successfully" -ForegroundColor Green

# Build nginx
Write-Host "Building nginx..." -ForegroundColor Yellow
docker build -f nginx/Dockerfile -t culicidaelab-nginx:$Version .
if ($LASTEXITCODE -ne 0) { exit 1 }

if ($Registry) {
    docker tag culicidaelab-nginx:$Version $Registry/culicidaelab-nginx:$Version
    docker tag culicidaelab-nginx:$Version $Registry/culicidaelab-nginx:latest
}

Write-Host "Nginx built successfully" -ForegroundColor Green

Write-Host "All images built successfully!" -ForegroundColor Green

# Show images
Write-Host "Built images:" -ForegroundColor Yellow
docker images | findstr culicidaelab