# PowerShell script to fix SSL proxy header warnings in Solara frontend
# This script rebuilds the frontend image with proper proxy header configuration

Write-Host "🔧 Fixing SSL proxy header configuration..." -ForegroundColor Cyan

# Check if .env.production exists
if (-not (Test-Path ".env.production")) {
    Write-Host "❌ Error: .env.production file not found" -ForegroundColor Red
    Write-Host "Please ensure you have a production environment file configured" -ForegroundColor Yellow
    exit 1
}

try {
    # Stop the current SSL services
    Write-Host "🛑 Stopping current SSL services..." -ForegroundColor Yellow
    docker-compose -f docker-compose.ssl-simple.yml --env-file .env.production down

    # Rebuild the frontend image with proxy header fixes
    Write-Host "🔨 Rebuilding frontend image with proxy header configuration..." -ForegroundColor Yellow
    docker build -t iloncka/culicidaelab-frontend:0.1.1 -f frontend/Dockerfile frontend/

    # Start the services again
    Write-Host "🚀 Starting SSL services with fixed configuration..." -ForegroundColor Green
    docker-compose -f docker-compose.ssl-simple.yml --env-file .env.production up -d

    # Show the logs to verify the fix
    Write-Host "📋 Showing frontend logs to verify the fix..." -ForegroundColor Cyan
    Start-Sleep -Seconds 10
    docker logs culicidaelab_frontend_ssl --tail 20

    Write-Host "✅ SSL proxy header fix applied!" -ForegroundColor Green
    Write-Host "The Solara server should now properly handle forwarded headers from nginx." -ForegroundColor Green
    Write-Host ""
    Write-Host "Monitor the logs with:" -ForegroundColor Cyan
    Write-Host "docker logs -f culicidaelab_frontend_ssl" -ForegroundColor White
}
catch {
    Write-Host "❌ Error occurred: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}