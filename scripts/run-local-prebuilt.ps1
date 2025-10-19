# Run docker-compose with locally built images
# Usage: .\scripts\run-local-prebuilt.ps1 [version]

param(
    [string]$Version = "latest"
)

Write-Host "Running CulicidaeLab with local prebuilt images..." -ForegroundColor Green

# Check if local images exist
$BackendImage = "culicidaelab-backend:$Version"
$FrontendImage = "culicidaelab-frontend:$Version"
$NginxImage = "culicidaelab-nginx:$Version"

$BackendExists = docker images -q $BackendImage
$FrontendExists = docker images -q $FrontendImage
$NginxExists = docker images -q $NginxImage

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

if (-not $NginxExists) {
    Write-Host "❌ Nginx image not found: $NginxImage" -ForegroundColor Red
    Write-Host "Build it first with: .\scripts\build-docker.ps1 $Version" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ All required images found locally" -ForegroundColor Green

# Set environment variables for local images (no registry)
$env:REGISTRY = ""
$env:VERSION = $Version
$env:FASTAPI_ENV = "production"
$env:DEBUG = "false"

# Run docker-compose
Write-Host "Starting services with local prebuilt images..." -ForegroundColor Green
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
}