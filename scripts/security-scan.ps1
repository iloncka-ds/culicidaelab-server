# Security scanning PowerShell script for Docker containers
# Performs vulnerability scanning and Dockerfile linting

param(
    [string]$Service = "all",
    [switch]$SkipBuild = $false
)

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$ResultsDir = Join-Path $ProjectDir "security-reports"
$TrivyConfig = Join-Path $ProjectDir "docker\security\trivy.yaml"
$HadolintConfig = Join-Path $ProjectDir "docker\security\hadolint.yaml"

# Create results directory
if (-not (Test-Path $ResultsDir)) {
    New-Item -ItemType Directory -Path $ResultsDir -Force | Out-Null
}

Write-Host "Starting security scan for CulicidaeLab containers..." -ForegroundColor Green

# Function to check if command exists
function Test-Command {
    param([string]$Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Function to install trivy if not present
function Install-Trivy {
    if (-not (Test-Command "trivy")) {
        Write-Host "Installing Trivy security scanner..." -ForegroundColor Yellow
        
        # Download trivy for Windows
        $trivyUrl = "https://github.com/aquasecurity/trivy/releases/latest/download/trivy_Windows-64bit.zip"
        $trivyZip = Join-Path $env:TEMP "trivy.zip"
        $trivyDir = Join-Path $env:TEMP "trivy"
        
        try {
            Invoke-WebRequest -Uri $trivyUrl -OutFile $trivyZip
            Expand-Archive -Path $trivyZip -DestinationPath $trivyDir -Force
            
            # Add to PATH for current session
            $env:PATH += ";$trivyDir"
            
            Write-Host "Trivy installed successfully" -ForegroundColor Green
        }
        catch {
            Write-Host "Error installing Trivy: $_" -ForegroundColor Red
            exit 1
        }
    }
}

# Function to install hadolint if not present
function Install-Hadolint {
    if (-not (Test-Command "hadolint")) {
        Write-Host "Installing Hadolint Dockerfile linter..." -ForegroundColor Yellow
        
        # Download hadolint for Windows
        $hadolintUrl = "https://github.com/hadolint/hadolint/releases/latest/download/hadolint-Windows-x86_64.exe"
        $hadolintPath = Join-Path $env:TEMP "hadolint.exe"
        
        try {
            Invoke-WebRequest -Uri $hadolintUrl -OutFile $hadolintPath
            
            # Add to PATH for current session
            $env:PATH += ";$(Split-Path $hadolintPath)"
            
            Write-Host "Hadolint installed successfully" -ForegroundColor Green
        }
        catch {
            Write-Host "Error installing Hadolint: $_" -ForegroundColor Red
            exit 1
        }
    }
}

# Function to scan Dockerfile with hadolint
function Scan-Dockerfile {
    param(
        [string]$DockerfilePath,
        [string]$ServiceName
    )
    
    Write-Host "Scanning Dockerfile: $DockerfilePath" -ForegroundColor Green
    
    if (Test-Path $DockerfilePath) {
        $outputFile = Join-Path $ResultsDir "$ServiceName-dockerfile-scan.txt"
        
        try {
            $result = & hadolint --config $HadolintConfig $DockerfilePath 2>&1
            $result | Out-File -FilePath $outputFile -Encoding UTF8
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✓ Dockerfile scan passed for $ServiceName" -ForegroundColor Green
            }
            else {
                Write-Host "⚠ Dockerfile scan found issues for $ServiceName. Check $outputFile" -ForegroundColor Yellow
            }
        }
        catch {
            Write-Host "✗ Error scanning Dockerfile for $ServiceName`: $_" -ForegroundColor Red
        }
    }
    else {
        Write-Host "✗ Dockerfile not found: $DockerfilePath" -ForegroundColor Red
    }
}

# Function to scan container image with trivy
function Scan-Image {
    param(
        [string]$ImageName,
        [string]$ServiceName
    )
    
    Write-Host "Scanning container image: $ImageName" -ForegroundColor Green
    
    $outputFile = Join-Path $ResultsDir "$ServiceName-vulnerability-scan.txt"
    
    try {
        & trivy image --config $TrivyConfig --output $outputFile $ImageName
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Vulnerability scan completed for $ServiceName" -ForegroundColor Green
        }
        else {
            Write-Host "⚠ Vulnerability scan found issues for $ServiceName. Check $outputFile" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "✗ Error scanning image for $ServiceName`: $_" -ForegroundColor Red
    }
}

# Function to build and scan all services
function Scan-AllServices {
    $services = @("backend", "frontend", "nginx")
    
    foreach ($service in $services) {
        Write-Host "`n=== Scanning $service service ===" -ForegroundColor Green
        
        # Scan Dockerfile
        switch ($service) {
            "backend" {
                Scan-Dockerfile (Join-Path $ProjectDir "backend\Dockerfile") $service
            }
            "frontend" {
                Scan-Dockerfile (Join-Path $ProjectDir "frontend\Dockerfile") $service
            }
            "nginx" {
                Scan-Dockerfile (Join-Path $ProjectDir "nginx\Dockerfile") $service
            }
        }
        
        if (-not $SkipBuild) {
            # Build image for scanning
            Write-Host "Building $service image for security scan..." -ForegroundColor Green
            $imageName = "culicidaelab-$service`:security-scan"
            
            try {
                switch ($service) {
                    "backend" {
                        & docker build -t $imageName -f (Join-Path $ProjectDir "backend\Dockerfile") $ProjectDir
                    }
                    "frontend" {
                        & docker build -t $imageName -f (Join-Path $ProjectDir "frontend\Dockerfile") $ProjectDir
                    }
                    "nginx" {
                        & docker build -t $imageName -f (Join-Path $ProjectDir "nginx\Dockerfile") (Join-Path $ProjectDir "nginx")
                    }
                }
                
                if ($LASTEXITCODE -eq 0) {
                    Scan-Image $imageName $service
                    
                    # Clean up scan image
                    & docker rmi $imageName 2>$null
                }
                else {
                    Write-Host "✗ Failed to build $service image" -ForegroundColor Red
                }
            }
            catch {
                Write-Host "✗ Error building $service image: $_" -ForegroundColor Red
            }
        }
    }
}

# Function to generate security report
function Generate-Report {
    $reportFile = Join-Path $ResultsDir "security-summary.txt"
    
    Write-Host "`nGenerating security summary report..." -ForegroundColor Green
    
    $report = @"
CulicidaeLab Security Scan Summary
==================================
Scan Date: $(Get-Date)
Scan Directory: $ProjectDir

Dockerfile Lint Results:
------------------------
"@

    # Add Dockerfile scan results
    Get-ChildItem -Path $ResultsDir -Filter "*-dockerfile-scan.txt" | ForEach-Object {
        $serviceName = $_.BaseName -replace "-dockerfile-scan", ""
        $report += "`nService: $serviceName`n"
        
        if ($_.Length -gt 0) {
            $report += "Issues found - see $($_.FullName)`n"
        }
        else {
            $report += "No issues found`n"
        }
    }

    $report += @"

Vulnerability Scan Results:
---------------------------
"@

    # Add vulnerability scan results
    Get-ChildItem -Path $ResultsDir -Filter "*-vulnerability-scan.txt" | ForEach-Object {
        $serviceName = $_.BaseName -replace "-vulnerability-scan", ""
        $report += "`nService: $serviceName`n"
        $report += "Results in: $($_.FullName)`n"
    }

    $report += @"

Security Recommendations:
------------------------
1. Review all HIGH and CRITICAL vulnerabilities
2. Update base images regularly
3. Use specific version tags instead of 'latest'
4. Implement runtime security monitoring
5. Regular security scans in CI/CD pipeline
"@

    $report | Out-File -FilePath $reportFile -Encoding UTF8
    
    Write-Host "Security summary report generated: $reportFile" -ForegroundColor Green
}

# Main execution
function Main {
    Write-Host "CulicidaeLab Security Scanner" -ForegroundColor Green
    Write-Host "=============================" -ForegroundColor Green
    
    # Check prerequisites
    if (-not (Test-Command "docker")) {
        Write-Host "Error: Docker is required but not installed" -ForegroundColor Red
        exit 1
    }
    
    # Install scanning tools
    Install-Trivy
    Install-Hadolint
    
    # Perform scans
    if ($Service -eq "all") {
        Scan-AllServices
    }
    else {
        Write-Host "Scanning specific service: $Service" -ForegroundColor Green
        # Add specific service scanning logic here if needed
    }
    
    # Generate report
    Generate-Report
    
    Write-Host "`nSecurity scan completed!" -ForegroundColor Green
    Write-Host "Results available in: $ResultsDir" -ForegroundColor Green
}

# Run main function
Main