# Test frontend connection to backend
# Usage: .\scripts\test-frontend-connection.ps1

Write-Host "Testing frontend-backend connectivity..." -ForegroundColor Green

# Test if containers are running
Write-Host "Checking container status..." -ForegroundColor Yellow
docker ps --filter "name=culicidaelab_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Test backend directly
Write-Host "Testing backend directly..." -ForegroundColor Yellow
try {
    $backendHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "✓ Backend accessible: $($backendHealth.status)" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend not accessible: $($_.Exception.Message)" -ForegroundColor Red
    return
}

# Test frontend directly
Write-Host "Testing frontend directly..." -ForegroundColor Yellow
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:8765" -TimeoutSec 10
    Write-Host "✓ Frontend accessible: $($frontendResponse.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Frontend not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test API endpoints that frontend uses
Write-Host "Testing API endpoints..." -ForegroundColor Yellow

$endpoints = @(
    "/api/diseases",
    "/api/species", 
    "/api/geo/filter_options",
    "/api/health"
)

foreach ($endpoint in $endpoints) {
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000$endpoint" -TimeoutSec 5
        if ($response -is [array]) {
            Write-Host "✓ $endpoint : $($response.Count) items" -ForegroundColor Green
        } elseif ($response.status) {
            Write-Host "✓ $endpoint : $($response.status)" -ForegroundColor Green
        } else {
            Write-Host "✓ $endpoint : OK" -ForegroundColor Green
        }
    } catch {
        Write-Host "✗ $endpoint : $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Check frontend logs for errors
Write-Host "Frontend container logs (last 20 lines):" -ForegroundColor Yellow
docker logs --tail 20 culicidaelab_frontend_local

# Check if frontend can reach backend from inside container
Write-Host "Testing backend connectivity from inside frontend container..." -ForegroundColor Yellow
try {
    $containerTest = docker exec culicidaelab_frontend_local curl -s -o /dev/null -w "%{http_code}" http://backend:8000/health 2>$null
    if ($containerTest -eq "200") {
        Write-Host "✓ Frontend container can reach backend container" -ForegroundColor Green
    } else {
        Write-Host "✗ Frontend container cannot reach backend container (HTTP $containerTest)" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Could not test container connectivity: $($_.Exception.Message)" -ForegroundColor Red
}

# Test browser-side connectivity (what the user's browser sees)
Write-Host "Testing what browser sees..." -ForegroundColor Yellow
try {
    # This simulates what the browser would do
    $browserTest = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 5
    Write-Host "✓ Browser can reach backend API: $($browserTest.status)" -ForegroundColor Green
} catch {
    Write-Host "✗ Browser cannot reach backend API: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Connection test completed" -ForegroundColor Green