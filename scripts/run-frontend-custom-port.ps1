# Run frontend on custom port
# Usage: .\scripts\run-frontend-custom-port.ps1 [port]

param(
    [int]$Port = 3000
)

Write-Host "Starting frontend on port $Port..." -ForegroundColor Green

# Stop existing container if running
docker stop culicidaelab-frontend-custom 2>$null
docker rm culicidaelab-frontend-custom 2>$null

# Run frontend container on custom port
docker run -d `
  --name culicidaelab-frontend-custom `
  -p "${Port}:8765" `
  -e BACKEND_URL=http://host.docker.internal:8000 `
  -e SOLARA_DEBUG=true `
  -e SOLARA_ASSETS_PROXY=false `
  -e HOME=/app `
  culicidaelab-frontend:latest

if ($LASTEXITCODE -eq 0) {
    Write-Host "Frontend started successfully!" -ForegroundColor Green
    Write-Host "Access URL: http://localhost:$Port" -ForegroundColor Yellow
    
    Write-Host "Container logs:" -ForegroundColor Yellow
    Start-Sleep -Seconds 3
    docker logs culicidaelab-frontend-custom
} else {
    Write-Host "Failed to start frontend container" -ForegroundColor Red
}