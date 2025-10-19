#!/usr/bin/env pwsh
# Test script to verify static images are working correctly

Write-Host "Testing static image access for species and diseases..." -ForegroundColor Green

# Test species API and image URLs
Write-Host "`nTesting species API and images..." -ForegroundColor Yellow
try {
    $speciesResponse = Invoke-WebRequest -Uri "http://localhost/api/species" -UseBasicParsing
    $speciesData = $speciesResponse.Content | ConvertFrom-Json
    
    if ($speciesData.species -and $speciesData.species.Count -gt 0) {
        $firstSpecies = $speciesData.species[0]
        Write-Host "✓ Species API working. First species: $($firstSpecies.scientific_name)" -ForegroundColor Green
        Write-Host "  Image URL: $($firstSpecies.image_url)" -ForegroundColor Cyan
        
        # Test if the image URL is accessible
        try {
            $imageResponse = Invoke-WebRequest -Uri $firstSpecies.image_url -UseBasicParsing
            Write-Host "✓ Species image accessible: $($imageResponse.StatusCode)" -ForegroundColor Green
        } catch {
            Write-Host "✗ Species image not accessible: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ No species data returned" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Species API failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test diseases API and image URLs
Write-Host "`nTesting diseases API and images..." -ForegroundColor Yellow
try {
    $diseasesResponse = Invoke-WebRequest -Uri "http://localhost/api/diseases" -UseBasicParsing
    $diseasesData = $diseasesResponse.Content | ConvertFrom-Json
    
    if ($diseasesData.diseases -and $diseasesData.diseases.Count -gt 0) {
        $firstDisease = $diseasesData.diseases[0]
        Write-Host "✓ Diseases API working. First disease: $($firstDisease.name)" -ForegroundColor Green
        Write-Host "  Image URL: $($firstDisease.image_url)" -ForegroundColor Cyan
        
        # Test if the image URL is accessible
        try {
            $imageResponse = Invoke-WebRequest -Uri $firstDisease.image_url -UseBasicParsing
            Write-Host "✓ Disease image accessible: $($imageResponse.StatusCode)" -ForegroundColor Green
        } catch {
            Write-Host "✗ Disease image not accessible: $($_.Exception.Message)" -ForegroundColor Red
        }
    } else {
        Write-Host "✗ No diseases data returned" -ForegroundColor Red
    }
} catch {
    Write-Host "✗ Diseases API failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test direct static file access
Write-Host "`nTesting direct static file access..." -ForegroundColor Yellow
try {
    $staticResponse = Invoke-WebRequest -Uri "http://localhost/static/images/test-image.txt" -UseBasicParsing
    Write-Host "✓ Static files accessible: $($staticResponse.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "✗ Static files not accessible: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nTest completed!" -ForegroundColor Green
Write-Host "You can now access the application at: http://localhost" -ForegroundColor Cyan