#!/bin/bash

# Installation script for SSL certificate renewal configuration
# This script sets up automatic certificate renewal using cron or systemd

set -e

# Configuration
INSTALL_DIR="/opt/culicidaelab"
CRON_FILE="/etc/cron.d/certbot-renewal"
SYSTEMD_SERVICE="/etc/systemd/system/certbot-renewal.service"
SYSTEMD_TIMER="/etc/systemd/system/certbot-renewal.timer"
LOG_DIR="/var/log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        error "This script must be run as root"
        exit 1
    fi
}

# Detect init system
detect_init_system() {
    if systemctl --version &>/dev/null; then
        echo "systemd"
    elif command -v crontab &>/dev/null; then
        echo "cron"
    else
        echo "unknown"
    fi
}

# Install using systemd
install_systemd() {
    log "Installing systemd service and timer..."
    
    # Copy service and timer files
    cp "scripts/certbot-renewal.service" "$SYSTEMD_SERVICE"
    cp "scripts/certbot-renewal.timer" "$SYSTEMD_TIMER"
    
    # Update paths in service file
    sed -i "s|/opt/culicidaelab|$INSTALL_DIR|g" "$SYSTEMD_SERVICE"
    
    # Reload systemd
    systemctl daemon-reload
    
    # Enable and start timer
    systemctl enable certbot-renewal.timer
    systemctl start certbot-renewal.timer
    
    log "Systemd timer installed and started"
    log "Check status with: systemctl status certbot-renewal.timer"
}

# Install using cron
install_cron() {
    log "Installing cron job..."
    
    # Copy cron file
    cp "scripts/certbot-cron" "$CRON_FILE"
    
    # Update paths in cron file
    sed -i "s|/opt/culicidaelab|$INSTALL_DIR|g" "$CRON_FILE"
    
    # Set proper permissions
    chmod 644 "$CRON_FILE"
    
    # Restart cron service
    if systemctl restart cron 2>/dev/null || systemctl restart crond 2>/dev/null; then
        log "Cron service restarted"
    else
        warn "Could not restart cron service automatically"
    fi
    
    log "Cron job installed"
    log "Check with: crontab -l"
}

# Create log files and directories
setup_logging() {
    log "Setting up logging..."
    
    # Create log files
    touch "$LOG_DIR/certbot-renewal.log"
    touch "$LOG_DIR/certbot-health.log"
    
    # Set proper permissions
    chmod 644 "$LOG_DIR/certbot-renewal.log"
    chmod 644 "$LOG_DIR/certbot-health.log"
    
    # Create logrotate configuration
    cat > /etc/logrotate.d/certbot-renewal << EOF
$LOG_DIR/certbot-renewal.log {
    weekly
    rotate 12
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}

$LOG_DIR/certbot-health.log {
    monthly
    rotate 6
    compress
    delaycompress
    missingok
    notifempty
    create 644 root root
}
EOF
    
    log "Logging configuration created"
}

# Make scripts executable
setup_scripts() {
    log "Setting up scripts..."
    
    chmod +x "$INSTALL_DIR/scripts/renew-certificates.sh"
    chmod +x "$INSTALL_DIR/scripts/init-letsencrypt.sh"
    
    log "Scripts made executable"
}

# Test the renewal script
test_renewal() {
    log "Testing renewal script..."
    
    if "$INSTALL_DIR/scripts/renew-certificates.sh" status; then
        log "Renewal script test passed"
    else
        warn "Renewal script test failed - this is normal if certificates are not yet installed"
    fi
}

# Main installation function
main() {
    local method="${1:-auto}"
    
    log "Starting SSL certificate renewal installation..."
    
    check_root
    
    # Detect current directory and set install directory
    INSTALL_DIR="$(pwd)"
    log "Using installation directory: $INSTALL_DIR"
    
    setup_scripts
    setup_logging
    
    case "$method" in
        "systemd")
            install_systemd
            ;;
        "cron")
            install_cron
            ;;
        "auto")
            local init_system=$(detect_init_system)
            log "Detected init system: $init_system"
            
            case "$init_system" in
                "systemd")
                    install_systemd
                    ;;
                "cron")
                    install_cron
                    ;;
                *)
                    error "Could not detect init system. Please specify 'systemd' or 'cron'"
                    exit 1
                    ;;
            esac
            ;;
        *)
            echo "Usage: $0 [auto|systemd|cron]"
            echo "  auto    - Automatically detect and install (default)"
            echo "  systemd - Install using systemd timer"
            echo "  cron    - Install using cron job"
            exit 1
            ;;
    esac
    
    test_renewal
    
    log "SSL certificate renewal installation completed successfully!"
    log ""
    log "Next steps:"
    log "1. Configure your domains and email in environment variables"
    log "2. Run the initial certificate setup: ./scripts/init-letsencrypt.sh"
    log "3. Monitor renewal logs in $LOG_DIR/"
}

# Run main function
main "$@"