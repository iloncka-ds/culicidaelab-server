# Test all containers separately with custom network
# Usage: .\scripts\test-all-separate.ps1

Write-Host "Setting up separate container testing..." -ForegroundColor Green

# Clean up existing containers and network
Write-Host "Cleaning up existing containers..." -ForegroundColor Yellow
docker stop culicidaelab-backend-test culicidaelab-frontend-test culicidaelab-nginx-test 2>$null
docker rm culicidaelab-backend-test culicidaelab-frontend-test culicidaelab-nginx-test 2>$null
docker network rm culicidaelab-test 2>$null

# Create custom network
Write-Host "Creating custom network..." -ForegroundColor Yellow
docker network create culicidaelab-test

# Create data directory if it doesn't exist
if (!(Test-Path "data")) {
    New-Item -ItemType Directory -Path "data"
}

# Start backend
Write-Host "Starting backend container..." -ForegroundColor Green
docker run -d `
  --name culicidaelab-backend-test `
  --network culicidaelab-test `
  -p 8000:8000 `
  -e CULICIDAELAB_DATABASE_PATH=/app/backend/data/.lancedb `
  -e CULICIDAELAB_SAVE_PREDICTED_IMAGES=true `
  -e FASTAPI_ENV=development `
  -e DEBUG=true `
  -v "${PWD}/data:/app/backend/data" `
  -v "${PWD}/backend/static:/app/backend/static" `
  culicidaelab-backend:latest

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start backend" -ForegroundColor Red
    exit 1
}

# Wait for backend to start
Write-Host "Waiting for backend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Start frontend
Write-Host "Starting frontend container..." -ForegroundColor Green
docker run -d `
  --name culicidaelab-frontend-test `
  --network culicidaelab-test `
  -p 8765:8765 `
  -e BACKEND_URL=http://culicidaelab-backend-test:8000 `
  -e SOLARA_DEBUG=true `
  -e SOLARA_ASSETS_PROXY=false `
  -e HOME=/app `
  culicidaelab-frontend:latest

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start frontend" -ForegroundColor Red
    exit 1
}

# Wait for frontend to start
Write-Host "Waiting for frontend to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Start nginx
Write-Host "Starting nginx container..." -ForegroundColor Green
docker run -d `
  --name culicidaelab-nginx-test `
  --network culicidaelab-test `
  -p 80:80 `
  -v "${PWD}/static:/var/www/static:ro" `
  -v "${PWD}/nginx/nginx.dev.conf:/etc/nginx/nginx.conf:ro" `
  -e NGINX_ENV=development `
  culicidaelab-nginx:latest

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to start nginx" -ForegroundColor Red
    exit 1
}

Write-Host "All containers started successfully!" -ForegroundColor Green

# Show running containers
Write-Host "Running containers:" -ForegroundColor Yellow
docker ps --filter "name=culicidaelab-*-test"

# Test endpoints
Write-Host "Testing endpoints..." -ForegroundColor Yellow

Write-Host "Backend health check..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 10
    Write-Host "✓ Backend: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Frontend check..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8765" -TimeoutSec 10
    Write-Host "✓ Frontend: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Frontend failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Nginx check..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost" -TimeoutSec 10
    Write-Host "✓ Nginx: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Nginx failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Access URLs:" -ForegroundColor Yellow
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "Backend Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:8765" -ForegroundColor Cyan
Write-Host "Nginx: http://localhost" -ForegroundColor Cyan

Write-Host ""
Write-Host "To view logs:" -ForegroundColor Yellow
Write-Host "docker logs culicidaelab-backend-test" -ForegroundColor Cyan
Write-Host "docker logs culicidaelab-frontend-test" -ForegroundColor Cyan
Write-Host "docker logs culicidaelab-nginx-test" -ForegroundColor Cyan

Write-Host ""
Write-Host "To stop all containers:" -ForegroundColor Yellow
Write-Host "docker stop culicidaelab-backend-test culicidaelab-frontend-test culicidaelab-nginx-test" -ForegroundColor Cyan