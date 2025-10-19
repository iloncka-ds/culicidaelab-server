#!/bin/bash
# Deploy monitoring stack to remote server
# Usage: ./deploy-remote-monitoring.sh [monitoring-server-ip]

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MONITORING_SERVER="${1:-monitoring.culicidaelab.com}"
MONITORING_USER="${MONITORING_USER:-ubuntu}"
SSH_KEY="${SSH_KEY:-~/.ssh/id_rsa}"

echo -e "${GREEN}Deploying CulicidaeLab monitoring stack to remote server...${NC}"
echo -e "${GREEN}Target server: ${MONITORING_SERVER}${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to run command on remote server
run_remote() {
    ssh -i "${SSH_KEY}" "${MONITORING_USER}@${MONITORING_SERVER}" "$@"
}

# Function to copy files to remote server
copy_to_remote() {
    local source="$1"
    local destination="$2"
    scp -i "${SSH_KEY}" -r "${source}" "${MONITORING_USER}@${MONITORING_SERVER}:${destination}"
}

# Check prerequisites
check_prerequisites() {
    echo -e "${GREEN}Checking prerequisites...${NC}"
    
    if ! command_exists ssh; then
        echo -e "${RED}Error: SSH is required but not installed${NC}"
        exit 1
    fi
    
    if ! command_exists scp; then
        echo -e "${RED}Error: SCP is required but not installed${NC}"
        exit 1
    fi
    
    if [[ ! -f "${SSH_KEY}" ]]; then
        echo -e "${RED}Error: SSH key not found at ${SSH_KEY}${NC}"
        exit 1
    fi
    
    # Test SSH connection
    if ! ssh -i "${SSH_KEY}" -o ConnectTimeout=10 "${MONITORING_USER}@${MONITORING_SERVER}" "echo 'SSH connection successful'"; then
        echo -e "${RED}Error: Cannot connect to monitoring server${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Prerequisites check passed${NC}"
}

# Prepare monitoring server
prepare_server() {
    echo -e "${GREEN}Preparing monitoring server...${NC}"
    
    # Update system packages
    run_remote "sudo apt-get update && sudo apt-get upgrade -y"
    
    # Install Docker if not present
    if ! run_remote "command -v docker >/dev/null 2>&1"; then
        echo -e "${YELLOW}Installing Docker...${NC}"
        run_remote "curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh"
        run_remote "sudo usermod -aG docker ${MONITORING_USER}"
        run_remote "sudo systemctl enable docker && sudo systemctl start docker"
    fi
    
    # Install Docker Compose if not present
    if ! run_remote "command -v docker-compose >/dev/null 2>&1"; then
        echo -e "${YELLOW}Installing Docker Compose...${NC}"
        run_remote "sudo curl -L \"https://github.com/docker/compose/releases/latest/download/docker-compose-\$(uname -s)-\$(uname -m)\" -o /usr/local/bin/docker-compose"
        run_remote "sudo chmod +x /usr/local/bin/docker-compose"
    fi
    
    # Create monitoring directory
    run_remote "mkdir -p ~/culicidaelab-monitoring"
    
    echo -e "${GREEN}Server preparation completed${NC}"
}

# Deploy monitoring configuration
deploy_config() {
    echo -e "${GREEN}Deploying monitoring configuration...${NC}"
    
    # Copy monitoring files
    copy_to_remote "${SCRIPT_DIR}/docker-compose.monitoring-remote.yml" "~/culicidaelab-monitoring/docker-compose.yml"
    copy_to_remote "${SCRIPT_DIR}/docker/monitoring/" "~/culicidaelab-monitoring/docker/monitoring/"
    
    # Copy environment template
    cat > /tmp/monitoring.env << EOF
# Monitoring server configuration
GRAFANA_ADMIN_PASSWORD=secure_admin_password_change_me
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@culicidaelab.com
SMTP_PASSWORD=your_smtp_password
SMTP_FROM=alerts@culicidaelab.com

# Alert email addresses
ALERT_EMAIL=admin@culicidaelab.com
CRITICAL_EMAIL=admin@culicidaelab.com
PROD_CRITICAL_EMAIL=production-team@culicidaelab.com
PROD_EMAIL=production-team@culicidaelab.com
BACKEND_EMAIL=backend-team@culicidaelab.com
FRONTEND_EMAIL=frontend-team@culicidaelab.com
INFRA_EMAIL=infrastructure-team@culicidaelab.com
STAGING_EMAIL=staging-team@culicidaelab.com
DEV_EMAIL=dev-team@culicidaelab.com
WARNING_EMAIL=monitoring@culicidaelab.com

# Application server IPs
PROD_SERVER_IP=10.0.1.100
STAGING_SERVER_IP=10.0.1.101
DEV_SERVER_IP=10.0.1.102

# Monitoring authentication
MONITORING_USER=monitoring
MONITORING_PASSWORD=secure_monitoring_password_change_me

# Webhook configuration (optional)
WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
WEBHOOK_USER=webhook_user
WEBHOOK_PASSWORD=webhook_password

# Slack configuration (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# PagerDuty configuration (optional)
PAGERDUTY_ROUTING_KEY=your_pagerduty_routing_key

# Remote storage configuration (optional)
REMOTE_WRITE_URL=https://prometheus-remote-write.example.com/api/v1/write
REMOTE_WRITE_USER=remote_user
REMOTE_WRITE_PASSWORD=remote_password
REMOTE_READ_URL=https://prometheus-remote-read.example.com/api/v1/read
REMOTE_READ_USER=remote_user
REMOTE_READ_PASSWORD=remote_password
EOF
    
    copy_to_remote "/tmp/monitoring.env" "~/culicidaelab-monitoring/.env"
    rm /tmp/monitoring.env
    
    echo -e "${GREEN}Configuration deployment completed${NC}"
}

# Configure firewall
configure_firewall() {
    echo -e "${GREEN}Configuring firewall...${NC}"
    
    # Install ufw if not present
    if ! run_remote "command -v ufw >/dev/null 2>&1"; then
        run_remote "sudo apt-get install -y ufw"
    fi
    
    # Configure firewall rules
    run_remote "sudo ufw --force reset"
    run_remote "sudo ufw default deny incoming"
    run_remote "sudo ufw default allow outgoing"
    run_remote "sudo ufw allow ssh"
    run_remote "sudo ufw allow 80/tcp"   # HTTP
    run_remote "sudo ufw allow 443/tcp"  # HTTPS
    run_remote "sudo ufw allow 3000/tcp" # Grafana
    run_remote "sudo ufw allow 9090/tcp" # Prometheus
    run_remote "sudo ufw allow 9093/tcp" # Alertmanager
    run_remote "sudo ufw --force enable"
    
    echo -e "${GREEN}Firewall configuration completed${NC}"
}

# Start monitoring services
start_services() {
    echo -e "${GREEN}Starting monitoring services...${NC}"
    
    # Pull images
    run_remote "cd ~/culicidaelab-monitoring && docker-compose pull"
    
    # Start services
    run_remote "cd ~/culicidaelab-monitoring && docker-compose up -d"
    
    # Wait for services to start
    echo -e "${YELLOW}Waiting for services to start...${NC}"
    sleep 30
    
    # Check service status
    run_remote "cd ~/culicidaelab-monitoring && docker-compose ps"
    
    echo -e "${GREEN}Monitoring services started successfully${NC}"
}

# Configure application servers for remote monitoring
configure_app_servers() {
    echo -e "${GREEN}Configuring application servers for remote monitoring...${NC}"
    
    cat > /tmp/monitoring-agent.yml << 'EOF'
# Add this to your application server docker-compose files
# to enable remote monitoring

  # Node exporter for system metrics
  node-exporter:
    image: prom/node-exporter:v1.6.1
    container_name: culicidaelab-node-exporter
    restart: unless-stopped
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - culicidaelab_network

  # cAdvisor for container metrics
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.47.2
    container_name: culicidaelab-cadvisor
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    devices:
      - /dev/kmsg
    networks:
      - culicidaelab_network
EOF
    
    echo -e "${YELLOW}Application server configuration saved to /tmp/monitoring-agent.yml${NC}"
    echo -e "${YELLOW}Add these services to your application server docker-compose files${NC}"
    
    rm /tmp/monitoring-agent.yml
}

# Generate access information
generate_access_info() {
    echo -e "${GREEN}Generating access information...${NC}"
    
    cat > /tmp/monitoring-access.txt << EOF
CulicidaeLab Remote Monitoring Access Information
================================================

Monitoring Server: ${MONITORING_SERVER}

Services:
---------
Grafana Dashboard: http://${MONITORING_SERVER}:3000
  - Username: admin
  - Password: (check .env file for GRAFANA_ADMIN_PASSWORD)

Prometheus: http://${MONITORING_SERVER}:9090
Alertmanager: http://${MONITORING_SERVER}:9093

SSH Access:
-----------
ssh -i ${SSH_KEY} ${MONITORING_USER}@${MONITORING_SERVER}

Service Management:
------------------
# Check service status
cd ~/culicidaelab-monitoring && docker-compose ps

# View logs
cd ~/culicidaelab-monitoring && docker-compose logs -f [service_name]

# Restart services
cd ~/culicidaelab-monitoring && docker-compose restart

# Update configuration
cd ~/culicidaelab-monitoring && docker-compose down
# Edit configuration files
cd ~/culicidaelab-monitoring && docker-compose up -d

Configuration Files:
-------------------
~/culicidaelab-monitoring/.env - Environment variables
~/culicidaelab-monitoring/docker/monitoring/ - Monitoring configuration

Next Steps:
-----------
1. Update .env file with your specific configuration
2. Configure SSL certificates for HTTPS access
3. Add monitoring agents to your application servers
4. Configure alert notification channels
5. Import Grafana dashboards for visualization

EOF
    
    echo -e "${GREEN}Access information saved to /tmp/monitoring-access.txt${NC}"
    cat /tmp/monitoring-access.txt
}

# Main execution
main() {
    echo -e "${GREEN}CulicidaeLab Remote Monitoring Deployment${NC}"
    echo -e "${GREEN}=========================================${NC}"
    
    check_prerequisites
    prepare_server
    deploy_config
    configure_firewall
    start_services
    configure_app_servers
    generate_access_info
    
    echo -e "\n${GREEN}Remote monitoring deployment completed successfully!${NC}"
    echo -e "${GREEN}Access your monitoring dashboard at: http://${MONITORING_SERVER}:3000${NC}"
    echo -e "${YELLOW}Don't forget to update the .env file with your specific configuration${NC}"
}

# Run main function
main "$@"