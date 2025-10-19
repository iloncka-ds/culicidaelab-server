# Debug frontend container interactively
# Usage: .\scripts\debug-frontend.ps1

Write-Host "Starting frontend container in interactive mode for debugging..." -ForegroundColor Green

# Stop and remove existing container if it exists
docker stop culicidaelab-frontend-debug 2>$null
docker rm culicidaelab-frontend-debug 2>$null

Write-Host "Running frontend container interactively..." -ForegroundColor Yellow

# Run frontend container interactively
docker run -it --rm `
  --name culicidaelab-frontend-debug `
  -p 8765:8765 `
  -e BACKEND_URL=http://host.docker.internal:8000 `
  -e SOLARA_DEBUG=true `
  -e SOLARA_ASSETS_PROXY=false `
  -e HOME=/app `
  -e PYTHONPATH=/app `
  culicidaelab-frontend:latest `
  /bin/bash

Write-Host "Container exited" -ForegroundColor Yellow