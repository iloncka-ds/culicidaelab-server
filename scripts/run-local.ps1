# PowerShell script to run local Docker containers with proper environment
# Usage: .\scripts\run-local.ps1

Write-Host "Starting CulicidaeLab local development environment..." -ForegroundColor Green

# Check if .env.local exists
if (-not (Test-Path ".env.local")) {
    Write-Host "Error: .env.local file not found!" -ForegroundColor Red
    Write-Host "Please create .env.local file with local development settings." -ForegroundColor Yellow
    exit 1
}

# Stop any existing containers
Write-Host "Stopping existing containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.local.yml --env-file .env.local down

# Pull latest images
Write-Host "Pulling latest images..." -ForegroundColor Yellow
docker-compose -f docker-compose.local.yml --env-file .env.local pull

# Start containers
Write-Host "Starting containers..." -ForegroundColor Yellow
docker-compose -f docker-compose.local.yml --env-file .env.local up -d

# Show status
Write-Host "Container status:" -ForegroundColor Green
docker-compose -f docker-compose.local.yml --env-file .env.local ps

Write-Host ""
Write-Host "Local development environment is running!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:8765" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Nginx: http://localhost" -ForegroundColor Cyan
Write-Host ""
Write-Host "To view logs: docker-compose -f docker-compose.local.yml --env-file .env.local logs -f" -ForegroundColor Yellow
Write-Host "To stop: docker-compose -f docker-compose.local.yml --env-file .env.local down" -ForegroundColor Yellow