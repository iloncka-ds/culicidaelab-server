# Build only the frontend container for testing
# Usage: .\scripts\build-frontend-only.ps1

Write-Host "Building frontend container..." -ForegroundColor Green

Write-Host "Building standalone frontend..." -ForegroundColor Cyan
docker build -f frontend/Dockerfile -t culicidaelab-frontend:latest .

if ($LASTEXITCODE -eq 0) {
    Write-Host "Frontend built successfully!" -ForegroundColor Green
    
    Write-Host "Testing frontend container..." -ForegroundColor Yellow
    
    # Test the container by running it briefly
    docker run --rm `
      -e BACKEND_URL=http://host.docker.internal:8000 `
      -e SOLARA_DEBUG=true `
      culicidaelab-frontend:latest `
      python -c "import frontend.main; print('✓ Frontend module imported successfully')"
      
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Frontend module test passed!" -ForegroundColor Green
    } else {
        Write-Host "✗ Frontend module test failed" -ForegroundColor Red
    }
} else {
    Write-Host "Failed to build frontend container" -ForegroundColor Red
}