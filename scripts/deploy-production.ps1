#!/usr/bin/env pwsh
param(
    [Parameter(Mandatory=$true)]
    [string]$Domain,
    
    [Parameter(Mandatory=$false)]
    [string]$Version = "latest",
    
    [Parameter(Mandatory=$false)]
    [switch]$UseHTTP = $false
)

# Production deployment script for CulicidaeLab

Write-Host "Deploying CulicidaeLab to production..." -ForegroundColor Green
Write-Host "Domain: $Domain" -ForegroundColor Cyan
Write-Host "Version: $Version" -ForegroundColor Cyan

# Determine protocol
$Protocol = if ($UseHTTP) { "http" } else { "https" }
Write-Host "Protocol: $Protocol" -ForegroundColor Cyan

# Create production environment file
$envContent = @"
# Production Environment Configuration
DOMAIN=$Domain
REGISTRY=
VERSION=$Version
ENVIRONMENT=production
FASTAPI_ENV=production
NGINX_ENV=production
DEBUG=false
SOLARA_DEBUG=false

# URLs for production
CLIENT_BACKEND_URL=${Protocol}://$Domain
STATIC_URL_BASE=${Protocol}://$Domain
STATIC_FILES_URL=${Protocol}://$Domain

# CORS origins
CORS_ORIGINS=${Protocol}://$Domain

# SSL/TLS
SSL_ENABLED=$(!$UseHTTP)
"@

$envContent | Out-File -FilePath ".env.production" -Encoding UTF8
Write-Host "✓ Created .env.production file" -ForegroundColor Green

# Stop existing containers
Write-Host "`nStopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.prebuilt.yml --env-file .env.production down

# Pull latest images (if using registry)
Write-Host "`nPulling latest images..." -ForegroundColor Yellow
docker-compose -f docker-compose.prebuilt.yml --env-file .env.production pull

# Start services
Write-Host "`nStarting production services..." -ForegroundColor Yellow
docker-compose -f docker-compose.prebuilt.yml --env-file .env.production up -d

# Wait for services to start
Write-Host "`nWaiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check service health
Write-Host "`nChecking service health..." -ForegroundColor Yellow
$services = @("culicidaelab_backend_prebuilt", "culicidaelab_frontend_prebuilt", "culicidaelab_nginx_prebuilt")

foreach ($service in $services) {
    $status = docker inspect $service --format='{{.State.Health.Status}}' 2>$null
    if ($status -eq "healthy" -or $status -eq "") {
        Write-Host "✓ $service is running" -ForegroundColor Green
    } else {
        Write-Host "✗ $service health check failed: $status" -ForegroundColor Red
    }
}

Write-Host "`n🎉 Deployment completed!" -ForegroundColor Green
Write-Host "Access your application at: ${Protocol}://$Domain" -ForegroundColor Cyan
Write-Host "`nTo view logs:" -ForegroundColor Yellow
Write-Host "  docker-compose -f docker-compose.prebuilt.yml --env-file .env.production logs -f" -ForegroundColor Gray
Write-Host "`nTo stop services:" -ForegroundColor Yellow
Write-Host "  docker-compose -f docker-compose.prebuilt.yml --env-file .env.production down" -ForegroundColor Gray