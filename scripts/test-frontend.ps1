# Test frontend container separately
# Usage: .\scripts\test-frontend.ps1

Write-Host "Starting frontend container..." -ForegroundColor Green

# Stop and remove existing container if it exists
docker stop culicidaelab-frontend-test 2>$null
docker rm culicidaelab-frontend-test 2>$null

# Run frontend container
docker run -d `
  --name culicidaelab-frontend-test `
  -p 8765:8765 `
  -e BACKEND_URL=http://host.docker.internal:8000 `
  -e SOLARA_DEBUG=true `
  -e SOLARA_ASSETS_PROXY=false `
  -e HOME=/app `
  culicidaelab-frontend:latest

if ($LASTEXITCODE -eq 0) {
    Write-Host "Frontend container started successfully!" -ForegroundColor Green
    Write-Host "Container name: culicidaelab-frontend-test" -ForegroundColor Yellow
    Write-Host "Port: 8765" -ForegroundColor Yellow
    Write-Host "URL: http://localhost:8765" -ForegroundColor Yellow
    
    Write-Host "Waiting for container to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    Write-Host "Container logs:" -ForegroundColor Yellow
    docker logs culicidaelab-frontend-test
    
    Write-Host "Testing frontend endpoint..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8765" -TimeoutSec 10
        Write-Host "Frontend check: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "Frontend check failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "Failed to start frontend container" -ForegroundColor Red
}