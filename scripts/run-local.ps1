# Run local development setup with simplified nginx (no SSL)
# Usage: .\scripts\run-local.ps1 [version]

param(
    [string]$Version = "latest"
)

Write-Host "Running CulicidaeLab locally with simplified nginx..." -ForegroundColor Green

# Check if images exist
$BackendImage = "culicidaelab-backend:$Version"
$FrontendImage = "culicidaelab-frontend:$Version"

$BackendExists = docker images -q $BackendImage
$FrontendExists = docker images -q $FrontendImage

if (-not $BackendExists) {
    Write-Host "❌ Backend image not found: $BackendImage" -ForegroundColor Red
    Write-Host "Build it first with: .\scripts\build-docker.ps1 $Version" -ForegroundColor Yellow
    exit 1
}

if (-not $FrontendExists) {
    Write-Host "❌ Frontend image not found: $FrontendImage" -ForegroundColor Red
    Write-Host "Build it first with: .\scripts\build-docker.ps1 $Version" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ All required images found locally" -ForegroundColor Green

# Set environment variables
$env:VERSION = $Version

# Stop any existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.local.yml down 2>$null

# Start services
Write-Host "Starting services..." -ForegroundColor Green
docker-compose -f docker-compose.local.yml up -d

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Services started successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access URLs:" -ForegroundColor Yellow
    Write-Host "  Main App (via Nginx): http://localhost" -ForegroundColor Cyan
    Write-Host "  Backend API: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  Backend Docs: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host "  Frontend: http://localhost:8765" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Nginx routes:" -ForegroundColor Yellow
    Write-Host "  API: http://localhost/api/" -ForegroundColor Cyan
    Write-Host "  Static: http://localhost/static/" -ForegroundColor Cyan
    Write-Host "  Health: http://localhost/health" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To view logs:" -ForegroundColor Yellow
    Write-Host "  docker-compose -f docker-compose.local.yml logs -f" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To stop services:" -ForegroundColor Yellow
    Write-Host "  docker-compose -f docker-compose.local.yml down" -ForegroundColor Cyan
} else {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    Write-Host "Check logs with:" -ForegroundColor Yellow
    Write-Host "  docker-compose -f docker-compose.local.yml logs" -ForegroundColor Cyan
}