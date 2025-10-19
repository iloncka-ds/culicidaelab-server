# Debug static file serving issues
# Usage: .\scripts\debug-static.ps1

Write-Host "Debugging static file serving..." -ForegroundColor Green

# Check if backend container is running
$backendContainer = docker ps --filter "name=backend" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
if ($backendContainer) {
    Write-Host "Backend containers:" -ForegroundColor Yellow
    Write-Host $backendContainer -ForegroundColor Cyan
} else {
    Write-Host "No backend containers running" -ForegroundColor Red
    Write-Host "Starting backend container..." -ForegroundColor Yellow
    .\scripts\test-backend.ps1
    Start-Sleep -Seconds 10
}

# Test backend health
Write-Host "Testing backend health..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 10
    Write-Host "✓ Backend is healthy" -ForegroundColor Green
    Write-Host "  Status: $($healthResponse.status)" -ForegroundColor Cyan
} catch {
    Write-Host "✗ Backend health check failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Backend logs:" -ForegroundColor Yellow
    docker logs --tail 20 culicidaelab-backend-test
    return
}

# Test static configuration
Write-Host "Testing static configuration..." -ForegroundColor Yellow
try {
    $staticResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/static-test" -TimeoutSec 10
    Write-Host "✓ Static configuration retrieved" -ForegroundColor Green
    Write-Host "  Directory: $($staticResponse.static_directory)" -ForegroundColor Cyan
    Write-Host "  Exists: $($staticResponse.static_exists)" -ForegroundColor Cyan
    Write-Host "  Is Directory: $($staticResponse.static_is_dir)" -ForegroundColor Cyan
    Write-Host "  Files found: $($staticResponse.contents.Count)" -ForegroundColor Cyan
    
    if ($staticResponse.contents) {
        Write-Host "  Files:" -ForegroundColor Cyan
        foreach ($file in $staticResponse.contents) {
            Write-Host "    - $file" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "✗ Static configuration test failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test direct static file access
Write-Host "Testing static file access..." -ForegroundColor Yellow

# Test the test.txt file we created
try {
    $testFileResponse = Invoke-WebRequest -Uri "http://localhost:8000/static/test.txt" -TimeoutSec 10
    Write-Host "✓ test.txt accessible" -ForegroundColor Green
    Write-Host "  Content: $($testFileResponse.Content.Substring(0, 50))..." -ForegroundColor Cyan
} catch {
    Write-Host "✗ test.txt not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test static directory listing
try {
    $staticDirResponse = Invoke-WebRequest -Uri "http://localhost:8000/static/" -TimeoutSec 10
    Write-Host "✓ Static directory accessible" -ForegroundColor Green
} catch {
    Write-Host "✗ Static directory not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Test images directory
try {
    $imagesDirResponse = Invoke-WebRequest -Uri "http://localhost:8000/static/images/" -TimeoutSec 10
    Write-Host "✓ Images directory accessible" -ForegroundColor Green
} catch {
    Write-Host "✗ Images directory not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

# Check container file system
Write-Host "Checking container file system..." -ForegroundColor Yellow
try {
    $containerFiles = docker exec culicidaelab-backend-test find /app/backend/static -type f 2>$null
    if ($containerFiles) {
        Write-Host "Files in container static directory:" -ForegroundColor Cyan
        $containerFiles | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
    } else {
        Write-Host "No files found in container static directory" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Could not check container file system" -ForegroundColor Red
}

Write-Host "Static debugging completed" -ForegroundColor Green