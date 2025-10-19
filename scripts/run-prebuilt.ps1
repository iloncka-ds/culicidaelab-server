# Run docker-compose with prebuilt images
# Usage: .\scripts\run-prebuilt.ps1 [registry] [version]

param(
    [string]$Registry = "",
    [string]$Version = "latest"
)

Write-Host "Running CulicidaeLab with prebuilt images..." -ForegroundColor Green

# Set environment variables
$env:REGISTRY = $Registry
$env:VERSION = $Version
$env:FASTAPI_ENV = "production"
$env:DEBUG = "false"

Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Registry: $Registry" -ForegroundColor Cyan
Write-Host "  Version: $Version" -ForegroundColor Cyan
Write-Host "  Environment: production" -ForegroundColor Cyan

# Check if images exist locally
$BackendImage = if ($Registry) { "$Registry/culicidaelab-backend:$Version" } else { "culicidaelab-backend:$Version" }
$FrontendImage = if ($Registry) { "$Registry/culicidaelab-frontend:$Version" } else { "culicidaelab-frontend:$Version" }
$NginxImage = if ($Registry) { "$Registry/culicidaelab-nginx:$Version" } else { "culicidaelab-nginx:$Version" }

Write-Host "Checking for required images..." -ForegroundColor Yellow

$BackendExists = docker images -q $BackendImage
$FrontendExists = docker images -q $FrontendImage
$NginxExists = docker images -q $NginxImage

if (-not $BackendExists) {
    Write-Host "⚠️  Backend image not found locally: $BackendImage" -ForegroundColor Yellow
    Write-Host "   Attempting to pull from registry..." -ForegroundColor Cyan
    docker pull $BackendImage
}

if (-not $FrontendExists) {
    Write-Host "⚠️  Frontend image not found locally: $FrontendImage" -ForegroundColor Yellow
    Write-Host "   Attempting to pull from registry..." -ForegroundColor Cyan
    docker pull $FrontendImage
}

if (-not $NginxExists) {
    Write-Host "⚠️  Nginx image not found locally: $NginxImage" -ForegroundColor Yellow
    Write-Host "   Attempting to pull from registry..." -ForegroundColor Cyan
    docker pull $NginxImage
}

# Run docker-compose
Write-Host "Starting services with prebuilt images..." -ForegroundColor Green
docker-compose -f docker-compose.prebuilt.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Services started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access URLs:" -ForegroundColor Yellow
    Write-Host "  Backend API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  Backend Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "  Frontend: http://localhost:8765" -ForegroundColor Cyan
    Write-Host "  Nginx: http://localhost" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To view logs:" -ForegroundColor Yellow
    Write-Host "  docker-compose -f docker-compose.prebuilt.yml logs -f" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To stop services:" -ForegroundColor Yellow
    Write-Host "  docker-compose -f docker-compose.prebuilt.yml down" -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    Write-Host "Check logs with:" -ForegroundColor Yellow
    Write-Host "  docker-compose -f docker-compose.prebuilt.yml logs" -ForegroundColor Cyan
}