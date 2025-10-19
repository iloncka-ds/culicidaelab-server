#!/bin/bash
# Security scanning script for Docker containers
# Performs vulnerability scanning and Dockerfile linting

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCAN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RESULTS_DIR="${SCAN_DIR}/security-reports"
TRIVY_CONFIG="${SCAN_DIR}/docker/security/trivy.yaml"
HADOLINT_CONFIG="${SCAN_DIR}/docker/security/hadolint.yaml"

# Create results directory
mkdir -p "${RESULTS_DIR}"

echo -e "${GREEN}Starting security scan for CulicidaeLab containers...${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install trivy if not present
install_trivy() {
    if ! command_exists trivy; then
        echo -e "${YELLOW}Installing Trivy security scanner...${NC}"
        if command_exists curl; then
            curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin
        else
            echo -e "${RED}Error: curl is required to install Trivy${NC}"
            exit 1
        fi
    fi
}

# Function to install hadolint if not present
install_hadolint() {
    if ! command_exists hadolint; then
        echo -e "${YELLOW}Installing Hadolint Dockerfile linter...${NC}"
        if command_exists curl; then
            curl -sL -o /usr/local/bin/hadolint "https://github.com/hadolint/hadolint/releases/latest/download/hadolint-$(uname -s)-$(uname -m)"
            chmod +x /usr/local/bin/hadolint
        else
            echo -e "${RED}Error: curl is required to install Hadolint${NC}"
            exit 1
        fi
    fi
}

# Function to scan Dockerfile with hadolint
scan_dockerfile() {
    local dockerfile="$1"
    local service_name="$2"
    
    echo -e "${GREEN}Scanning Dockerfile: ${dockerfile}${NC}"
    
    if [[ -f "${dockerfile}" ]]; then
        local output_file="${RESULTS_DIR}/${service_name}-dockerfile-scan.txt"
        
        if hadolint --config "${HADOLINT_CONFIG}" "${dockerfile}" > "${output_file}" 2>&1; then
            echo -e "${GREEN}✓ Dockerfile scan passed for ${service_name}${NC}"
        else
            echo -e "${YELLOW}⚠ Dockerfile scan found issues for ${service_name}. Check ${output_file}${NC}"
        fi
    else
        echo -e "${RED}✗ Dockerfile not found: ${dockerfile}${NC}"
    fi
}

# Function to scan container image with trivy
scan_image() {
    local image_name="$1"
    local service_name="$2"
    
    echo -e "${GREEN}Scanning container image: ${image_name}${NC}"
    
    local output_file="${RESULTS_DIR}/${service_name}-vulnerability-scan.txt"
    
    if trivy image --config "${TRIVY_CONFIG}" --output "${output_file}" "${image_name}"; then
        echo -e "${GREEN}✓ Vulnerability scan completed for ${service_name}${NC}"
    else
        echo -e "${YELLOW}⚠ Vulnerability scan found issues for ${service_name}. Check ${output_file}${NC}"
    fi
}

# Function to build and scan all services
scan_all_services() {
    local services=("backend" "frontend" "nginx")
    
    for service in "${services[@]}"; do
        echo -e "\n${GREEN}=== Scanning ${service} service ===${NC}"
        
        # Scan Dockerfile
        case "${service}" in
            "backend")
                scan_dockerfile "${SCAN_DIR}/backend/Dockerfile" "${service}"
                ;;
            "frontend")
                scan_dockerfile "${SCAN_DIR}/frontend/Dockerfile" "${service}"
                ;;
            "nginx")
                scan_dockerfile "${SCAN_DIR}/nginx/Dockerfile" "${service}"
                ;;
        esac
        
        # Build image for scanning
        echo -e "${GREEN}Building ${service} image for security scan...${NC}"
        local image_name="culicidaelab-${service}:security-scan"
        
        case "${service}" in
            "backend")
                if docker build -t "${image_name}" -f "${SCAN_DIR}/backend/Dockerfile" "${SCAN_DIR}"; then
                    scan_image "${image_name}" "${service}"
                else
                    echo -e "${RED}✗ Failed to build ${service} image${NC}"
                fi
                ;;
            "frontend")
                if docker build -t "${image_name}" -f "${SCAN_DIR}/frontend/Dockerfile" "${SCAN_DIR}"; then
                    scan_image "${image_name}" "${service}"
                else
                    echo -e "${RED}✗ Failed to build ${service} image${NC}"
                fi
                ;;
            "nginx")
                if docker build -t "${image_name}" -f "${SCAN_DIR}/nginx/Dockerfile" "${SCAN_DIR}/nginx"; then
                    scan_image "${image_name}" "${service}"
                else
                    echo -e "${RED}✗ Failed to build ${service} image${NC}"
                fi
                ;;
        esac
        
        # Clean up scan image
        docker rmi "${image_name}" 2>/dev/null || true
    done
}

# Function to generate security report
generate_report() {
    local report_file="${RESULTS_DIR}/security-summary.txt"
    
    echo -e "\n${GREEN}Generating security summary report...${NC}"
    
    {
        echo "CulicidaeLab Security Scan Summary"
        echo "=================================="
        echo "Scan Date: $(date)"
        echo "Scan Directory: ${SCAN_DIR}"
        echo ""
        
        echo "Dockerfile Lint Results:"
        echo "------------------------"
        for file in "${RESULTS_DIR}"/*-dockerfile-scan.txt; do
            if [[ -f "${file}" ]]; then
                local service=$(basename "${file}" -dockerfile-scan.txt)
                echo "Service: ${service}"
                if [[ -s "${file}" ]]; then
                    echo "Issues found - see ${file}"
                else
                    echo "No issues found"
                fi
                echo ""
            fi
        done
        
        echo "Vulnerability Scan Results:"
        echo "---------------------------"
        for file in "${RESULTS_DIR}"/*-vulnerability-scan.txt; do
            if [[ -f "${file}" ]]; then
                local service=$(basename "${file}" -vulnerability-scan.txt)
                echo "Service: ${service}"
                echo "Results in: ${file}"
                echo ""
            fi
        done
        
        echo "Security Recommendations:"
        echo "------------------------"
        echo "1. Review all HIGH and CRITICAL vulnerabilities"
        echo "2. Update base images regularly"
        echo "3. Use specific version tags instead of 'latest'"
        echo "4. Implement runtime security monitoring"
        echo "5. Regular security scans in CI/CD pipeline"
        
    } > "${report_file}"
    
    echo -e "${GREEN}Security summary report generated: ${report_file}${NC}"
}

# Main execution
main() {
    echo -e "${GREEN}CulicidaeLab Security Scanner${NC}"
    echo -e "${GREEN}=============================${NC}"
    
    # Check prerequisites
    if ! command_exists docker; then
        echo -e "${RED}Error: Docker is required but not installed${NC}"
        exit 1
    fi
    
    # Install scanning tools
    install_trivy
    install_hadolint
    
    # Perform scans
    scan_all_services
    
    # Generate report
    generate_report
    
    echo -e "\n${GREEN}Security scan completed!${NC}"
    echo -e "${GREEN}Results available in: ${RESULTS_DIR}${NC}"
}

# Run main function
main "$@"