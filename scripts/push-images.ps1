# Push Docker images to registry (Windows PowerShell)
# Usage: .\scripts\push-images.ps1 [version] [registry]

param(
    [string]$Version = "latest",
    [Parameter(Mandatory=$true)]
    [string]$Registry
)

$ProjectName = "culicidaelab"

Write-Host "Pushing CulicidaeLab images to $Registry..." -ForegroundColor Green

function Push-Image {
    param([string]$Service)
    
    Write-Host "Pushing $Service..." -ForegroundColor Yellow
    
    # Push versioned tag
    $RegistryTagVersion = "$Registry/$ProjectName-$Service`:$Version"
    docker push $RegistryTagVersion
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to push $Service" -ForegroundColor Red
        exit 1
    }
    
    # Push latest tag
    $RegistryTagLatest = "$Registry/$ProjectName-$Service`:latest"
    docker push $RegistryTagLatest
    
    Write-Host "✓ $Service pushed successfully" -ForegroundColor Green
}

# Push all images
Push-Image -Service "backend"
Push-Image -Service "frontend"
Push-Image -Service "nginx"

Write-Host "All images pushed successfully to $Registry!" -ForegroundColor Green