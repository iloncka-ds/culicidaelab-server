# Quick test of backend accessibility
Write-Host "Quick backend test..." -ForegroundColor Green

# Test if backend container is running
$backendContainer = docker ps --filter "name=backend" --format "{{.Names}}"
if ($backendContainer) {
    Write-Host "✓ Backend container running: $backendContainer" -ForegroundColor Green
} else {
    Write-Host "✗ No backend container running" -ForegroundColor Red
    exit 1
}

# Test backend health
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 5
    Write-Host "✓ Backend health: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend health failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test diseases endpoint specifically
try {
    $diseases = Invoke-RestMethod -Uri "http://localhost:8000/api/diseases" -TimeoutSec 5
    Write-Host "✓ Diseases endpoint: $($diseases.Count) diseases" -ForegroundColor Green
} catch {
    Write-Host "✗ Diseases endpoint failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test with curl to see raw response
Write-Host "Testing with curl..." -ForegroundColor Yellow
try {
    $curlResult = curl -s -w "HTTP_CODE:%{http_code}" "http://localhost:8000/api/diseases"
    Write-Host "Curl result: $curlResult" -ForegroundColor Cyan
} catch {
    Write-Host "Curl failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Check what ports are actually listening
Write-Host "Checking listening ports..." -ForegroundColor Yellow
netstat -an | findstr ":8000"