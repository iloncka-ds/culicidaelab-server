# Remote Monitoring Deployment Guide

This guide explains how to deploy the CulicidaeLab monitoring stack on a separate server or location from your main application.

## Overview

Remote monitoring provides several benefits:
- **Isolation**: Monitoring infrastructure is separate from application infrastructure
- **Centralization**: Monitor multiple application instances from one location
- **Reliability**: Monitoring continues even if application servers have issues
- **Security**: Monitoring access can be controlled independently
- **Scalability**: Dedicated resources for monitoring without affecting application performance

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Production    │    │    Staging      │    │  Development    │
│   Server        │    │    Server       │    │    Server       │
│                 │    │                 │    │                 │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Application │ │    │ │ Application │ │    │ │ Application │ │
│ │ Services    │ │    │ │ Services    │ │    │ │ Services    │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ Node        │ │    │ │ Node        │ │    │ │ Node        │ │
│ │ Exporter    │ │    │ │ Exporter    │ │    │ │ Exporter    │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
│ ┌─────────────┐ │    │ ┌─────────────┐ │    │ ┌─────────────┐ │
│ │ cAdvisor    │ │    │ │ cAdvisor    │ │    │ │ cAdvisor    │ │
│ └─────────────┘ │    │ └─────────────┘ │    │ └─────────────┘ │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │ Metrics               │ Metrics               │ Metrics
         │ (HTTP/HTTPS)          │ (HTTP/HTTPS)          │ (HTTP/HTTPS)
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Monitoring Server     │
                    │                         │
                    │ ┌─────────────────────┐ │
                    │ │    Prometheus       │ │
                    │ │  (Metrics Storage)  │ │
                    │ └─────────────────────┘ │
                    │ ┌─────────────────────┐ │
                    │ │     Grafana         │ │
                    │ │  (Visualization)    │ │
                    │ └─────────────────────┘ │
                    │ ┌─────────────────────┐ │
                    │ │   Alertmanager      │ │
                    │ │  (Alert Routing)    │ │
                    │ └─────────────────────┘ │
                    │ ┌─────────────────────┐ │
                    │ │      Loki           │ │
                    │ │  (Log Aggregation)  │ │
                    │ └─────────────────────┘ │
                    └─────────────────────────┘
```

## Quick Start

### 1. Automated Deployment

Use the automated deployment script:

```bash
# Make the script executable
chmod +x scripts/deploy-remote-monitoring.sh

# Deploy to remote server
./scripts/deploy-remote-monitoring.sh monitoring.culicidaelab.com

# Or specify custom SSH key and user
MONITORING_USER=ubuntu SSH_KEY=~/.ssh/monitoring-key ./scripts/deploy-remote-monitoring.sh 10.0.1.200
```

### 2. Manual Deployment

If you prefer manual deployment:

```bash
# 1. Copy files to monitoring server
scp -r docker-compose.monitoring-remote.yml docker/monitoring/ user@monitoring-server:~/culicidaelab-monitoring/

# 2. SSH to monitoring server
ssh user@monitoring-server

# 3. Start monitoring stack
cd ~/culicidaelab-monitoring
docker-compose -f docker-compose.monitoring-remote.yml up -d
```

## Configuration

### Environment Variables

Create a `.env` file on your monitoring server:

```bash
# Monitoring server configuration
GRAFANA_ADMIN_PASSWORD=secure_admin_password
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@culicidaelab.com
SMTP_PASSWORD=your_smtp_password
SMTP_FROM=alerts@culicidaelab.com

# Application server IPs
PROD_SERVER_IP=10.0.1.100
STAGING_SERVER_IP=10.0.1.101
DEV_SERVER_IP=10.0.1.102

# Monitoring authentication
MONITORING_USER=monitoring
MONITORING_PASSWORD=secure_monitoring_password

# Alert email addresses
ALERT_EMAIL=admin@culicidaelab.com
CRITICAL_EMAIL=admin@culicidaelab.com
PROD_CRITICAL_EMAIL=production-team@culicidaelab.com
```

### Application Server Configuration

Add monitoring agents to your application servers by including these services in your `docker-compose.yml`:

```yaml
services:
  # Your existing services...

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
```

## Security Configuration

### Firewall Setup

Configure firewall on monitoring server:

```bash
# Allow SSH, HTTP, HTTPS, and monitoring ports
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 3000/tcp  # Grafana
sudo ufw allow 9090/tcp  # Prometheus
sudo ufw allow 9093/tcp  # Alertmanager
sudo ufw enable
```

### Authentication

#### Basic Authentication

Create `.htpasswd` file for Prometheus/Alertmanager access:

```bash
# Install htpasswd utility
sudo apt-get install apache2-utils

# Create password file
htpasswd -c /etc/nginx/.htpasswd monitoring
```

#### SSL/TLS Configuration

For production, configure SSL certificates:

```bash
# Using Let's Encrypt
sudo apt-get install certbot
sudo certbot certonly --standalone -d monitoring.culicidaelab.com

# Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/monitoring.culicidaelab.com/fullchain.pem /etc/ssl/certs/monitoring.crt
sudo cp /etc/letsencrypt/live/monitoring.culicidaelab.com/privkey.pem /etc/ssl/certs/monitoring.key
```

## Access and Usage

### Web Interfaces

- **Grafana Dashboard**: `http://monitoring-server:3000`
  - Username: `admin`
  - Password: (from GRAFANA_ADMIN_PASSWORD)

- **Prometheus**: `http://monitoring-server:9090`
- **Alertmanager**: `http://monitoring-server:9093`

### Service Management

```bash
# Check service status
cd ~/culicidaelab-monitoring
docker-compose ps

# View logs
docker-compose logs -f prometheus
docker-compose logs -f grafana
docker-compose logs -f alertmanager

# Restart services
docker-compose restart

# Update configuration
docker-compose down
# Edit configuration files
docker-compose up -d
```

## Monitoring Multiple Environments

The remote monitoring setup supports monitoring multiple environments:

### Production Environment
- High-frequency monitoring (15-30 second intervals)
- Critical alert notifications
- Comprehensive dashboards
- Long-term data retention

### Staging Environment
- Medium-frequency monitoring (30-60 second intervals)
- Warning-level alerts
- Development team notifications
- Medium-term data retention

### Development Environment
- Low-frequency monitoring (60+ second intervals)
- Info-level alerts only
- Developer notifications
- Short-term data retention

## Alert Configuration

### Email Notifications

Configure SMTP settings in `.env`:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=alerts@culicidaelab.com
SMTP_PASSWORD=your_app_password
```

### Slack Integration

Add Slack webhook URL:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
```

### PagerDuty Integration

For critical production alerts:

```bash
PAGERDUTY_ROUTING_KEY=your_pagerduty_routing_key
```

## Performance Optimization

### Resource Allocation

Monitoring server recommended specifications:

- **CPU**: 2-4 cores
- **Memory**: 4-8 GB RAM
- **Storage**: 100+ GB SSD
- **Network**: Stable connection to application servers

### Data Retention

Configure retention policies:

```yaml
# Prometheus retention
--storage.tsdb.retention.time=90d

# Grafana data source settings
timeInterval: "15s"
queryTimeout: "60s"
```

### Network Optimization

- Use dedicated monitoring network if possible
- Configure compression for metric transmission
- Implement connection pooling
- Use persistent connections where possible

## Troubleshooting

### Common Issues

1. **Connection Refused**
   ```bash
   # Check if services are running
   docker-compose ps

   # Check firewall rules
   sudo ufw status

   # Test connectivity
   telnet application-server 9100
   ```

2. **Authentication Failures**
   ```bash
   # Verify credentials in .env file
   cat .env | grep MONITORING

   # Check Prometheus targets
   curl http://monitoring-server:9090/api/v1/targets
   ```

3. **High Resource Usage**
   ```bash
   # Monitor resource usage
   docker stats

   # Adjust scrape intervals
   # Edit prometheus-remote.yml
   ```

### Log Analysis

```bash
# View service logs
docker-compose logs -f prometheus
docker-compose logs -f grafana
docker-compose logs -f alertmanager

# Check system logs
sudo journalctl -u docker
sudo journalctl -f
```

## Backup and Recovery

### Configuration Backup

```bash
# Backup monitoring configuration
tar -czf monitoring-backup-$(date +%Y%m%d).tar.gz \
  docker-compose.monitoring-remote.yml \
  docker/monitoring/ \
  .env

# Backup data volumes
docker run --rm -v culicidaelab_prometheus_data:/data \
  -v $(pwd):/backup alpine \
  tar -czf /backup/prometheus-data-$(date +%Y%m%d).tar.gz -C /data .
```

### Recovery

```bash
# Restore configuration
tar -xzf monitoring-backup-YYYYMMDD.tar.gz

# Restore data
docker run --rm -v culicidaelab_prometheus_data:/data \
  -v $(pwd):/backup alpine \
  tar -xzf /backup/prometheus-data-YYYYMMDD.tar.gz -C /data
```

## Scaling Considerations

### Horizontal Scaling

For large deployments:

1. **Multiple Monitoring Servers**: Deploy monitoring servers per region/datacenter
2. **Federation**: Use Prometheus federation to aggregate metrics
3. **Load Balancing**: Use load balancers for Grafana access
4. **Sharding**: Shard metrics collection by service or environment

### Vertical Scaling

Increase resources based on monitoring load:

```yaml
deploy:
  resources:
    limits:
      memory: 4G      # Increase for more metrics
      cpus: '2.0'     # Increase for more processing
    reservations:
      memory: 2G
      cpus: '1.0'
```

## Best Practices

1. **Security**
   - Use strong passwords and API keys
   - Enable HTTPS for all web interfaces
   - Implement network segmentation
   - Regular security updates

2. **Monitoring**
   - Set appropriate alert thresholds
   - Avoid alert fatigue with proper routing
   - Regular dashboard reviews
   - Monitor the monitoring system itself

3. **Maintenance**
   - Regular backups of configuration and data
   - Update monitoring stack components
   - Review and optimize resource usage
   - Document configuration changes

4. **Documentation**
   - Maintain runbooks for common issues
   - Document alert escalation procedures
   - Keep inventory of monitored services
   - Regular review of monitoring coverage

This remote monitoring setup provides a robust, scalable solution for monitoring your CulicidaeLab deployment from a centralized location while maintaining security and performance.
