#!/bin/bash
"""Setup script for logging infrastructure in production.

This script creates necessary directories and configures log rotation
for the CulicidaeLab Docker deployment.
"""

set -e

# Configuration
LOG_BASE_DIR="/var/log/culicidaelab"
NGINX_LOG_DIR="${LOG_BASE_DIR}/nginx"
DOCKER_LOG_DIR="/var/lib/docker/containers"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_error "This script must be run as root"
   exit 1
fi

log_info "Setting up logging infrastructure for CulicidaeLab..."

# Create log directories
log_info "Creating log directories..."
mkdir -p "${LOG_BASE_DIR}"
mkdir -p "${NGINX_LOG_DIR}"
mkdir -p "${LOG_BASE_DIR}/application"
mkdir -p "${LOG_BASE_DIR}/monitoring"

# Set proper permissions
chown -R root:root "${LOG_BASE_DIR}"
chmod -R 755 "${LOG_BASE_DIR}"

# Create logrotate configuration for nginx logs
log_info "Setting up log rotation for nginx..."
cat > /etc/logrotate.d/culicidaelab-nginx << 'EOF'
/var/log/culicidaelab/nginx/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        # Reload nginx to reopen log files
        docker exec culicidaelab_nginx_prod nginx -s reload 2>/dev/null || true
    endscript
}
EOF

# Create logrotate configuration for Docker container logs
log_info "Setting up log rotation for Docker containers..."
cat > /etc/logrotate.d/culicidaelab-docker << 'EOF'
/var/lib/docker/containers/*/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    copytruncate
    maxsize 100M
}
EOF

# Create systemd service for log monitoring
log_info "Creating log monitoring service..."
cat > /etc/systemd/system/culicidaelab-log-monitor.service << 'EOF'
[Unit]
Description=CulicidaeLab Log Monitor
After=docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/culicidaelab
ExecStart=/usr/bin/python3 /opt/culicidaelab/scripts/health_monitor.py --interval 60
Restart=always
RestartSec=30
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Create systemd timer for periodic health checks
log_info "Creating periodic health check timer..."
cat > /etc/systemd/system/culicidaelab-health-check.service << 'EOF'
[Unit]
Description=CulicidaeLab Health Check
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
User=root
WorkingDirectory=/opt/culicidaelab
ExecStart=/usr/bin/python3 /opt/culicidaelab/scripts/health_monitor.py --single
StandardOutput=journal
StandardError=journal
EOF

cat > /etc/systemd/system/culicidaelab-health-check.timer << 'EOF'
[Unit]
Description=Run CulicidaeLab Health Check every 5 minutes
Requires=culicidaelab-health-check.service

[Timer]
OnCalendar=*:0/5
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Configure rsyslog for structured logging (if available)
if command -v rsyslogd &> /dev/null; then
    log_info "Configuring rsyslog for structured logging..."
    cat > /etc/rsyslog.d/30-culicidaelab.conf << 'EOF'
# CulicidaeLab application logs
:programname, isequal, "culicidaelab" /var/log/culicidaelab/application/app.log
& stop

# Docker container logs with JSON parsing
$ModLoad imfile
$InputFileName /var/log/culicidaelab/nginx/access.log
$InputFileTag nginx-access:
$InputFileStateFile stat-nginx-access
$InputFileSeverity info
$InputFileFacility local0
$InputRunFileMonitor

# Log rotation signal
$WorkDirectory /var/spool/rsyslog
EOF

    systemctl restart rsyslog
    log_info "Rsyslog configured and restarted"
fi

# Create log analysis script
log_info "Creating log analysis script..."
cat > /usr/local/bin/culicidaelab-logs << 'EOF'
#!/bin/bash
# CulicidaeLab log analysis helper script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CULICIDAELAB_DIR="/opt/culicidaelab"

case "$1" in
    "follow")
        echo "Following all CulicidaeLab logs..."
        cd "$CULICIDAELAB_DIR" && python3 scripts/log_aggregator.py
        ;;
    "health")
        echo "Checking service health..."
        cd "$CULICIDAELAB_DIR" && python3 scripts/health_monitor.py --single
        ;;
    "nginx")
        echo "Following nginx logs..."
        tail -f /var/log/culicidaelab/nginx/*.log
        ;;
    "errors")
        echo "Showing recent errors..."
        journalctl -u docker.service --since "1 hour ago" | grep -i error
        docker logs culicidaelab_backend_prod 2>&1 | grep -i error | tail -20
        docker logs culicidaelab_frontend_prod 2>&1 | grep -i error | tail -20
        ;;
    "stats")
        echo "Log statistics..."
        echo "Nginx access logs (last 24h):"
        find /var/log/culicidaelab/nginx -name "*.log" -mtime -1 -exec wc -l {} \;
        echo ""
        echo "Docker container log sizes:"
        docker ps --format "table {{.Names}}\t{{.Size}}"
        ;;
    *)
        echo "Usage: $0 {follow|health|nginx|errors|stats}"
        echo ""
        echo "Commands:"
        echo "  follow  - Follow all application logs"
        echo "  health  - Check service health"
        echo "  nginx   - Follow nginx logs"
        echo "  errors  - Show recent errors"
        echo "  stats   - Show log statistics"
        exit 1
        ;;
esac
EOF

chmod +x /usr/local/bin/culicidaelab-logs

# Reload systemd and enable services
log_info "Enabling systemd services..."
systemctl daemon-reload
systemctl enable culicidaelab-health-check.timer
systemctl start culicidaelab-health-check.timer

# Test log rotation
log_info "Testing log rotation configuration..."
logrotate -d /etc/logrotate.d/culicidaelab-nginx
logrotate -d /etc/logrotate.d/culicidaelab-docker

log_info "Logging infrastructure setup completed!"
log_info ""
log_info "Available commands:"
log_info "  culicidaelab-logs follow   - Follow all logs"
log_info "  culicidaelab-logs health   - Check service health"
log_info "  culicidaelab-logs nginx    - Follow nginx logs"
log_info "  culicidaelab-logs errors   - Show recent errors"
log_info "  culicidaelab-logs stats    - Show log statistics"
log_info ""
log_info "Services enabled:"
log_info "  culicidaelab-health-check.timer - Periodic health checks"
log_info ""
log_info "Log directories created:"
log_info "  ${LOG_BASE_DIR}/nginx/        - Nginx logs"
log_info "  ${LOG_BASE_DIR}/application/  - Application logs"
log_info "  ${LOG_BASE_DIR}/monitoring/   - Monitoring logs"