# Test static file serving
# Usage: .\scripts\test-static-files.ps1

Write-Host "Testing static file serving..." -ForegroundColor Green

# Test if backend is running
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 5
    Write-Host "✓ Backend is running" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend is not running. Start it first." -ForegroundColor Red
    exit 1
}

# Test static configuration endpoint
try {
    $staticTestResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/static-test" -TimeoutSec 5
    $staticInfo = $staticTestResponse.Content | ConvertFrom-Json
    
    Write-Host "Static directory info:" -ForegroundColor Yellow
    Write-Host "  Directory: $($staticInfo.static_directory)" -ForegroundColor Cyan
    Write-Host "  Exists: $($staticInfo.static_exists)" -ForegroundColor Cyan
    Write-Host "  Is Directory: $($staticInfo.static_is_dir)" -ForegroundColor Cyan
    Write-Host "  Files found: $($staticInfo.contents.Count)" -ForegroundColor Cyan
    
    if ($staticInfo.contents.Count -gt 0) {
        Write-Host "  Files:" -ForegroundColor Cyan
        foreach ($file in $staticInfo.contents) {
            Write-Host "    - $file" -ForegroundColor Gray
        }
    }
    
} catch {
    Write-Host "✗ Failed to get static info: $($_.Exception.Message)" -ForegroundColor Red
}

# Test direct static file access
Write-Host "Testing direct static file access..." -ForegroundColor Yellow

# Test accessing static directory
try {
    $staticResponse = Invoke-WebRequest -Uri "http://localhost:8000/static/" -TimeoutSec 5
    Write-Host "✓ Static directory is accessible" -ForegroundColor Green
} catch {
    Write-Host "✗ Static directory not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test accessing images directory
try {
    $imagesResponse = Invoke-WebRequest -Uri "http://localhost:8000/static/images/" -TimeoutSec 5
    Write-Host "✓ Images directory is accessible" -ForegroundColor Green
} catch {
    Write-Host "✗ Images directory not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "Static file test completed" -ForegroundColor Green