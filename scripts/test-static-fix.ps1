#!/usr/bin/env pwsh
# Test script to verify static files are working after the fix

Write-Host "Testing static file access after Docker configuration fix..." -ForegroundColor Green

# Test direct backend static file access
Write-Host "`nTesting direct backend static access (http://localhost:8000/static/)..." -ForegroundColor Yellow
try {
    $backendResponse = Invoke-WebRequest -Uri "http://localhost:8000/static/images/test-image.txt" -UseBasicParsing
    Write-Host "✓ Backend static files accessible: $($backendResponse.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Backend static files failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test nginx proxy static file access
Write-Host "`nTesting nginx proxy static access (http://localhost/static/)..." -ForegroundColor Yellow
try {
    $nginxResponse = Invoke-WebRequest -Uri "http://localhost/static/images/test-image.txt" -UseBasicParsing
    Write-Host "✓ Nginx static files accessible: $($nginxResponse.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Nginx static files failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test API endpoints that return image URLs
Write-Host "`nTesting API endpoints for image URL generation..." -ForegroundColor Yellow
try {
    $speciesResponse = Invoke-WebRequest -Uri "http://localhost/api/species" -UseBasicParsing
    $speciesData = $speciesResponse.Content | ConvertFrom-Json
    if ($speciesData.Count -gt 0) {
        $firstSpecies = $speciesData[0]
        Write-Host "✓ Species API accessible, first species image URL: $($firstSpecies.image_url)" -ForegroundColor Green
        
        # Test if the image URL is accessible
        if ($firstSpecies.image_url) {
            try {
                $imageResponse = Invoke-WebRequest -Uri $firstSpecies.image_url -UseBasicParsing
                Write-Host "✓ Species image accessible: $($imageResponse.StatusCode)" -ForegroundColor Green
            } catch {
                Write-Host "✗ Species image not accessible: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
} catch {
    Write-Host "✗ Species API failed: $($_.Exception.Message)" -ForegroundColor Red
}

try {
    $diseasesResponse = Invoke-WebRequest -Uri "http://localhost/api/diseases" -UseBasicParsing
    $diseasesData = $diseasesResponse.Content | ConvertFrom-Json
    if ($diseasesData.Count -gt 0) {
        $firstDisease = $diseasesData[0]
        Write-Host "✓ Diseases API accessible, first disease image URL: $($firstDisease.image_url)" -ForegroundColor Green
        
        # Test if the image URL is accessible
        if ($firstDisease.image_url) {
            try {
                $imageResponse = Invoke-WebRequest -Uri $firstDisease.image_url -UseBasicParsing
                Write-Host "✓ Disease image accessible: $($imageResponse.StatusCode)" -ForegroundColor Green
            } catch {
                Write-Host "✗ Disease image not accessible: $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
} catch {
    Write-Host "✗ Diseases API failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nTest completed!" -ForegroundColor Green