# Debug local setup issues
# Usage: .\scripts\debug-local.ps1

Write-Host "Debugging local setup..." -ForegroundColor Green

# Check if containers are running
Write-Host "Checking container status..." -ForegroundColor Yellow
$containers = docker ps --filter "name=culicidaelab_" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
if ($containers) {
    Write-Host $containers -ForegroundColor Cyan
} else {
    Write-Host "No CulicidaeLab containers running" -ForegroundColor Red
    Write-Host "Start them with: .\scripts\run-local.ps1" -ForegroundColor Yellow
    exit 1
}

# Test backend health
Write-Host "Testing backend health..." -ForegroundColor Yellow
try {
    $backendHealth = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 10
    Write-Host "✓ Backend health: $($backendHealth.status)" -ForegroundColor Green
    if ($backendHealth.caches_loaded) {
        Write-Host "✓ Database caches loaded" -ForegroundColor Green
    } else {
        Write-Host "✗ Database caches not loaded" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test backend API endpoints
Write-Host "Testing backend API endpoints..." -ForegroundColor Yellow

# Test diseases endpoint
try {
    $diseases = Invoke-RestMethod -Uri "http://localhost:8000/api/diseases" -TimeoutSec 10
    Write-Host "✓ Diseases API: $($diseases.Count) diseases found" -ForegroundColor Green
} catch {
    Write-Host "✗ Diseases API failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test species endpoint
try {
    $species = Invoke-RestMethod -Uri "http://localhost:8000/api/species" -TimeoutSec 10
    Write-Host "✓ Species API: $($species.Count) species found" -ForegroundColor Green
} catch {
    Write-Host "✗ Species API failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test static files
Write-Host "Testing static files..." -ForegroundColor Yellow
try {
    $staticTest = Invoke-WebRequest -Uri "http://localhost:8000/static/test.txt" -TimeoutSec 10
    Write-Host "✓ Static files accessible" -ForegroundColor Green
} catch {
    Write-Host "✗ Static files not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test frontend
Write-Host "Testing frontend..." -ForegroundColor Yellow
try {
    $frontend = Invoke-WebRequest -Uri "http://localhost:8765" -TimeoutSec 10
    Write-Host "✓ Frontend accessible: $($frontend.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Frontend not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test nginx routing
Write-Host "Testing nginx routing..." -ForegroundColor Yellow

# Test nginx health
try {
    $nginxHealth = Invoke-WebRequest -Uri "http://localhost/health" -TimeoutSec 10
    Write-Host "✓ Nginx health: $($nginxHealth.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Nginx health failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test API through nginx
try {
    $apiThroughNginx = Invoke-RestMethod -Uri "http://localhost/api/health" -TimeoutSec 10
    Write-Host "✓ API through nginx: $($apiThroughNginx.status)" -ForegroundColor Green
} catch {
    Write-Host "✗ API through nginx failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test static through nginx
try {
    $staticThroughNginx = Invoke-WebRequest -Uri "http://localhost/static/test.txt" -TimeoutSec 10
    Write-Host "✓ Static through nginx accessible" -ForegroundColor Green
} catch {
    Write-Host "✗ Static through nginx failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Check container logs for errors
Write-Host "Checking container logs for errors..." -ForegroundColor Yellow

Write-Host "Backend logs (last 10 lines):" -ForegroundColor Cyan
docker logs --tail 10 culicidaelab_backend_local 2>&1

Write-Host "Frontend logs (last 10 lines):" -ForegroundColor Cyan
docker logs --tail 10 culicidaelab_frontend_local 2>&1

Write-Host "Nginx logs (last 10 lines):" -ForegroundColor Cyan
docker logs --tail 10 culicidaelab_nginx_local 2>&1

# Check database files
Write-Host "Checking database files..." -ForegroundColor Yellow
try {
    $dbFiles = docker exec culicidaelab_backend_local find /app/backend/data -name "*.lance" -type f 2>$null
    if ($dbFiles) {
        Write-Host "✓ Database files found:" -ForegroundColor Green
        $dbFiles | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    } else {
        Write-Host "✗ No database files found" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Could not check database files: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Debug completed" -ForegroundColor Green