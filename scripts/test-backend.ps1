# Test backend container separately
# Usage: .\scripts\test-backend.ps1

Write-Host "Starting backend container..." -ForegroundColor Green

# Stop and remove existing container if it exists
docker stop culicidaelab-backend-test 2>$null
docker rm culicidaelab-backend-test 2>$null

# Create data directory if it doesn't exist
if (!(Test-Path "data")) {
    New-Item -ItemType Directory -Path "data"
}

# Run backend container
docker run -d `
  --name culicidaelab-backend-test `
  -p 8000:8000 `
  -e CULICIDAELAB_DATABASE_PATH=/app/backend/data/.lancedb `
  -e CULICIDAELAB_SAVE_PREDICTED_IMAGES=true `
  -e FASTAPI_ENV=development `
  -e DEBUG=true `
  -e CULICIDAELAB_BACKEND_CORS_ORIGINS="http://localhost:3000,http://localhost:8765,http://127.0.0.1:3000,http://127.0.0.1:8765" `
  -v "${PWD}/backend/data:/app/backend/data" `
  -v "${PWD}/backend/static:/app/backend/static" `
  culicidaelab-backend:0.1.0

if ($LASTEXITCODE -eq 0) {
    Write-Host "Backend container started successfully!" -ForegroundColor Green
    Write-Host "Container name: culicidaelab-backend-test" -ForegroundColor Yellow
    Write-Host "Port: 8000" -ForegroundColor Yellow
    Write-Host "API docs: http://localhost:8000/docs" -ForegroundColor Yellow
    
    Write-Host "Waiting for container to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    Write-Host "Container logs:" -ForegroundColor Yellow
    docker logs culicidaelab-backend-test
    
    Write-Host "Testing health endpoint..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 10
        Write-Host "Health check: $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    }
} else {
    Write-Host "Failed to start backend container" -ForegroundColor Red
}