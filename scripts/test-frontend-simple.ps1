# Test frontend with simpler approach
# Usage: .\scripts\test-frontend-simple.ps1

Write-Host "Testing frontend with Python directly..." -ForegroundColor Green

# Stop and remove existing container if it exists
docker stop culicidaelab-frontend-simple 2>$null
docker rm culicidaelab-frontend-simple 2>$null

Write-Host "Running frontend container with Python module..." -ForegroundColor Yellow

# Try running with python -m instead of solara command
docker run -d `
  --name culicidaelab-frontend-simple `
  -p 8765:8765 `
  -e BACKEND_URL=http://host.docker.internal:8000 `
  -e SOLARA_DEBUG=true `
  -e SOLARA_ASSETS_PROXY=false `
  -e HOME=/app `
  -e PYTHONPATH=/app `
  culicidaelab-frontend:latest `
  python -c "import frontend.main; print('Frontend module imported successfully')"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Frontend module test completed" -ForegroundColor Green
    Write-Host "Container logs:" -ForegroundColor Yellow
    docker logs culicidaelab-frontend-simple
} else {
    Write-Host "Frontend module test failed" -ForegroundColor Red
}

# Clean up
docker stop culicidaelab-frontend-simple 2>$null
docker rm culicidaelab-frontend-simple 2>$null