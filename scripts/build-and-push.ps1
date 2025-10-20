#!/usr/bin/env pwsh
param(
    [Parameter(Mandatory=$false)]
    [string]$Version = "latest",
    
    [Parameter(Mandatory=$false)]
    [string]$Registry = "iloncka/"
)

# Build and push CulicidaeLab images to Docker Hub (PowerShell version)

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Building and Pushing CulicidaeLab Images" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "Version: $Version" -ForegroundColor Yellow
Write-Host "Registry: $Registry" -ForegroundColor Yellow
Write-Host ""

# Check if logged into Docker Hub
Write-Host "Checking Docker Hub authentication..." -ForegroundColor Blue
try {
    $dockerInfo = docker info 2>$null
    if (-not ($dockerInfo -match "Username")) {
        Write-Host "⚠ Not logged into Docker Hub. Please login first:" -ForegroundColor Yellow
        Write-Host "  docker login" -ForegroundColor Gray
        exit 1
    }
    Write-Host "✓ Docker Hub authentication verified" -ForegroundColor Green
} catch {
    Write-Host "✗ Failed to check Docker authentication" -ForegroundColor Red
    exit 1
}

# Build all images locally first
Write-Host "Building images locally..." -ForegroundColor Blue
Write-Host ""

# Build backend
Write-Host "Building backend image..." -ForegroundColor Yellow
try {
    docker build -f backend/Dockerfile -t "${Registry}culicidaelab-backend:$Version" .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Backend image built successfully" -ForegroundColor Green
    } else {
        throw "Build failed"
    }
} catch {
    Write-Host "✗ Failed to build backend image" -ForegroundColor Red
    exit 1
}

# Build frontend
Write-Host "Building frontend image..." -ForegroundColor Yellow
try {
    docker build -f frontend/Dockerfile -t "${Registry}culicidaelab-frontend:$Version" .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Frontend image built successfully" -ForegroundColor Green
    } else {
        throw "Build failed"
    }
} catch {
    Write-Host "✗ Failed to build frontend image" -ForegroundColor Red
    exit 1
}

# Build nginx
Write-Host "Building nginx image..." -ForegroundColor Yellow
try {
    docker build -f nginx/Dockerfile -t "${Registry}culicidaelab-nginx:$Version" .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Nginx image built successfully" -ForegroundColor Green
    } else {
        throw "Build failed"
    }
} catch {
    Write-Host "✗ Failed to build nginx image" -ForegroundColor Red
    exit 1
}

# Build SSL nginx
Write-Host "Building SSL nginx image..." -ForegroundColor Yellow
try {
    docker build -f nginx/Dockerfile.with-certbot -t "${Registry}culicidaelab-nginx-ssl:$Version" .
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ SSL nginx image built successfully" -ForegroundColor Green
    } else {
        throw "Build failed"
    }
} catch {
    Write-Host "✗ Failed to build SSL nginx image" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "All images built successfully. Starting push to registry..." -ForegroundColor Blue
Write-Host ""

# Push images to registry
$images = @(
    "${Registry}culicidaelab-backend:$Version",
    "${Registry}culicidaelab-frontend:$Version",
    "${Registry}culicidaelab-nginx:$Version",
    "${Registry}culicidaelab-nginx-ssl:$Version"
)

foreach ($image in $images) {
    Write-Host "Pushing $image..." -ForegroundColor Yellow
    try {
        docker push $image
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Successfully pushed $image" -ForegroundColor Green
        } else {
            throw "Push failed"
        }
    } catch {
        Write-Host "✗ Failed to push $image" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "==================================================" -ForegroundColor Green
Write-Host "✓ All images built and pushed successfully!" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Pushed images:" -ForegroundColor Blue
foreach ($image in $images) {
    Write-Host "  - $image" -ForegroundColor Gray
}

Write-Host ""
Write-Host "To deploy using these images:" -ForegroundColor Blue
Write-Host "  .\scripts\deploy-production.ps1 -Domain yourdomain.com -Registry $Registry -Version $Version" -ForegroundColor Gray
Write-Host ""
Write-Host "Docker Hub repositories:" -ForegroundColor Blue
$registryName = $Registry.TrimEnd('/')
Write-Host "  https://hub.docker.com/r/$registryName/culicidaelab-backend" -ForegroundColor Gray
Write-Host "  https://hub.docker.com/r/$registryName/culicidaelab-frontend" -ForegroundColor Gray
Write-Host "  https://hub.docker.com/r/$registryName/culicidaelab-nginx" -ForegroundColor Gray
Write-Host "  https://hub.docker.com/r/$registryName/culicidaelab-nginx-ssl" -ForegroundColor Gray