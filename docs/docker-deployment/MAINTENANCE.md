# CulicidaeLab Maintenance Procedures

This document outlines the maintenance procedures for the CulicidaeLab Docker deployment to ensure optimal performance, security, and reliability.

## Table of Contents

- [Maintenance Schedule](#maintenance-schedule)
- [Daily Maintenance](#daily-maintenance)
- [Weekly Maintenance](#weekly-maintenance)
- [Monthly Maintenance](#monthly-maintenance)
- [Quarterly Maintenance](#quarterly-maintenance)
- [Emergency Procedures](#emergency-procedures)
- [Update Procedures](#update-procedures)
- [Backup Management](#backup-management)
- [Performance Monitoring](#performance-monitoring)
- [Security Maintenance](#security-maintenance)
- [Maintenance Checklists](#maintenance-checklists)

## Maintenance Schedule

### Overview

| Frequency | Tasks | Duration | Downtime |
|-----------|-------|----------|----------|
| Daily | Health checks, log review | 15 min | None |
| Weekly | Backups, updates, cleanup | 30 min | <5 min |
| Monthly | Security audit, performance review | 2 hours | <15 min |
| Quarterly | Major updates, capacity planning | 4 hours | <30 min |

### Automated Tasks

```bash
# Set up automated maintenance cron jobs
sudo crontab -e

# Daily health check (every 6 hours)
0 */6 * * * /path/to/culicidaelab/scripts/health-check.sh --json > /var/log/culicidaelab/health-$(date +\%Y\%m\%d-\%H).json

# Daily backup (2 AM)
0 2 * * * /path/to/culicidaelab/scripts/backup.sh --compress

# Weekly cleanup (Sunday 3 AM)
0 3 * * 0 /path/to/culicidaelab/scripts/maintenance-weekly.sh

# Monthly maintenance (1st of month, 4 AM)
0 4 1 * * /path/to/culicidaelab/scripts/maintenance-monthly.sh
```

## Daily Maintenance

### Health Monitoring

```bash
# Run comprehensive health check
./scripts/health-check.sh --verbose

# Check for any unhealthy services
docker-compose -f docker-compose.prod.yml ps | grep -v "Up (healthy)"

# Monitor system resources
df -h
free -h
uptime
```

### Log Review

```bash
# Check for errors in application logs
docker-compose -f docker-compose.prod.yml logs --since 24h | grep -i error

# Review nginx access logs for unusual activity
tail -100 /var/log/culicidaelab/nginx/access.log | grep -E "(40[0-9]|50[0-9])"

# Check system logs for issues
sudo journalctl --since "24 hours ago" --priority=err
```

### Performance Monitoring

```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost/api/health

# Monitor container resource usage
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Check database size growth
docker exec culicidaelab_backend_prod sqlite3 /app/data/culicidaelab.db ".dbinfo" | grep "database page size\|number of pages"
```

### Daily Checklist

- [ ] Health check passes
- [ ] All services running and healthy
- [ ] No critical errors in logs
- [ ] System resources within normal ranges
- [ ] Backup completed successfully
- [ ] SSL certificate valid (>30 days)
- [ ] Response times acceptable (<2s)

## Weekly Maintenance

### System Updates

```bash
# Update system packages
sudo apt update
sudo apt list --upgradable
sudo apt upgrade -y

# Update Docker if needed
sudo apt list --upgradable | grep docker
# If Docker updates available, plan maintenance window
```

### Docker Maintenance

```bash
# Clean up unused Docker resources
docker system prune -f

# Remove old images (keep last 3 versions)
docker images | grep culicidaelab | tail -n +4 | awk '{print $3}' | xargs -r docker rmi

# Check for image updates
docker-compose -f docker-compose.prod.yml pull --dry-run
```

### Backup Management

```bash
# Verify recent backups
sudo ./scripts/backup.sh --list | head -10

# Test backup integrity
LATEST_BACKUP=$(sudo ./scripts/backup.sh --list | head -1 | awk '{print $1}')
sudo ./scripts/backup.sh --verify $LATEST_BACKUP

# Clean up old backups (keep 30 days)
sudo ./scripts/backup.sh --retention-days 30
```

### Log Rotation

```bash
# Rotate application logs
sudo logrotate -f /etc/logrotate.d/culicidaelab

# Clean up old Docker logs
docker system events --since 168h --until 0h | wc -l  # Check log volume
# If high, consider adjusting log retention in docker-compose.yml
```

### Weekly Checklist

- [ ] System packages updated
- [ ] Docker resources cleaned up
- [ ] Backup integrity verified
- [ ] Old backups cleaned up
- [ ] Logs rotated
- [ ] No security alerts
- [ ] Performance metrics reviewed

## Monthly Maintenance

### Security Audit

```bash
# Check for security updates
sudo apt list --upgradable | grep -i security

# Scan containers for vulnerabilities
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image culicidaelab_backend_prod
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image culicidaelab_frontend_prod

# Review SSL certificate security
openssl x509 -in /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem -text -noout | grep -A 2 "Signature Algorithm"

# Check for failed login attempts
sudo grep "Failed password" /var/log/auth.log | tail -20
```

### Performance Review

```bash
# Analyze monthly performance trends
# Create performance report
cat > /tmp/performance-report.sh << 'EOF'
#!/bin/bash
echo "=== Monthly Performance Report ==="
echo "Date: $(date)"
echo

echo "=== System Resources ==="
df -h /
free -h
uptime

echo "=== Container Performance ==="
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

echo "=== Database Statistics ==="
docker exec culicidaelab_backend_prod sqlite3 /app/data/culicidaelab.db ".dbinfo"

echo "=== Response Time Test ==="
curl -w "Total time: %{time_total}s\n" -o /dev/null -s http://localhost/api/health

echo "=== Recent Error Summary ==="
docker-compose -f docker-compose.prod.yml logs --since 720h | grep -i error | wc -l
EOF

chmod +x /tmp/performance-report.sh
/tmp/performance-report.sh > /var/log/culicidaelab/performance-$(date +%Y%m).txt
```

### Database Maintenance

```bash
# Optimize database
docker exec culicidaelab_backend_prod sqlite3 /app/data/culicidaelab.db "VACUUM;"
docker exec culicidaelab_backend_prod sqlite3 /app/data/culicidaelab.db "ANALYZE;"

# Check database integrity
docker exec culicidaelab_backend_prod sqlite3 /app/data/culicidaelab.db "PRAGMA integrity_check;"

# Review database growth
docker exec culicidaelab_backend_prod sqlite3 /app/data/culicidaelab.db ".dbinfo" | grep "database page size\|number of pages"
```

### Configuration Review

```bash
# Review and update configuration
# Check for new environment variables
diff .env.prod.example .env.prod

# Review resource limits
docker-compose -f docker-compose.prod.yml config | grep -A 5 -B 5 "resources:"

# Update documentation if needed
git log --since="1 month ago" --oneline -- docs/ README.md
```

### Monthly Checklist

- [ ] Security scan completed
- [ ] Performance report generated
- [ ] Database optimized
- [ ] Configuration reviewed
- [ ] Documentation updated
- [ ] Capacity planning reviewed
- [ ] Monitoring alerts configured

## Quarterly Maintenance

### Major Updates

```bash
# Plan major update maintenance window
# 1. Create comprehensive backup
sudo ./scripts/backup.sh --compress

# 2. Update application dependencies
# Review and update requirements.txt, package.json, etc.

# 3. Update base images
# Review Dockerfiles for base image updates

# 4. Test updates in staging environment
# Deploy to staging and run comprehensive tests

# 5. Deploy to production
sudo ./scripts/deploy.sh
```

### Capacity Planning

```bash
# Analyze resource usage trends
# Generate quarterly capacity report
cat > /tmp/capacity-report.sh << 'EOF'
#!/bin/bash
echo "=== Quarterly Capacity Report ==="
echo "Date: $(date)"
echo

echo "=== Disk Usage Trends ==="
df -h / | tail -1
du -sh /var/lib/culicidaelab/
du -sh /var/backups/culicidaelab/

echo "=== Memory Usage Analysis ==="
free -h
cat /proc/meminfo | grep -E "(MemTotal|MemAvailable|SwapTotal|SwapFree)"

echo "=== Network Usage ==="
# Analyze nginx logs for traffic patterns
awk '{print $1}' /var/log/culicidaelab/nginx/access.log | sort | uniq -c | sort -nr | head -10

echo "=== Database Growth ==="
docker exec culicidaelab_backend_prod sqlite3 /app/data/culicidaelab.db ".dbinfo"

echo "=== Backup Storage ==="
du -sh /var/backups/culicidaelab/*/ | tail -10
EOF

chmod +x /tmp/capacity-report.sh
/tmp/capacity-report.sh > /var/log/culicidaelab/capacity-$(date +%Y%m).txt
```

### Infrastructure Review

```bash
# Review and update infrastructure
# 1. Server specifications vs. usage
# 2. Network bandwidth requirements
# 3. Storage capacity planning
# 4. Backup storage requirements
# 5. Disaster recovery procedures

# Update infrastructure documentation
# Document any changes to server specs, network config, etc.
```

### Quarterly Checklist

- [ ] Major updates completed
- [ ] Capacity planning reviewed
- [ ] Infrastructure assessment done
- [ ] Disaster recovery tested
- [ ] Documentation updated
- [ ] Performance benchmarks updated
- [ ] Security policies reviewed

## Emergency Procedures

### Service Outage Response

```bash
# 1. Immediate Assessment
./scripts/health-check.sh --json
docker-compose -f docker-compose.prod.yml ps

# 2. Quick Recovery Attempt
docker-compose -f docker-compose.prod.yml restart

# 3. If restart fails, rollback to last known good state
LATEST_BACKUP=$(sudo ./scripts/backup.sh --list | head -1 | awk '{print $1}')
sudo ./scripts/rollback.sh $LATEST_BACKUP

# 4. Verify recovery
./scripts/health-check.sh --verbose
```

### Security Incident Response

```bash
# 1. Isolate affected systems
docker-compose -f docker-compose.prod.yml down

# 2. Create forensic backup
sudo ./scripts/backup.sh --compress
mv /var/backups/culicidaelab/$(ls -t /var/backups/culicidaelab/ | head -1) /var/backups/culicidaelab/forensic-$(date +%Y%m%d_%H%M%S)

# 3. Investigate
# Review logs, check for unauthorized access, identify attack vectors

# 4. Remediate
# Apply security patches, update configurations, restore from clean backup

# 5. Monitor
# Implement additional monitoring, update security measures
```

### Data Corruption Recovery

```bash
# 1. Stop services immediately
docker-compose -f docker-compose.prod.yml down

# 2. Assess corruption extent
docker run --rm -v backend_data:/data alpine ls -la /data/
docker run --rm -v backend_data:/data -v /tmp:/backup alpine cp /data/culicidaelab.db /backup/corrupted-$(date +%Y%m%d_%H%M%S).db

# 3. Restore from backup
sudo ./scripts/rollback.sh <backup_id>

# 4. Verify data integrity
./scripts/health-check.sh --verbose
```

## Update Procedures

### Application Updates

```bash
# 1. Pre-update backup
sudo ./scripts/backup.sh --compress

# 2. Pull latest code
git fetch origin
git checkout main
git pull origin main

# 3. Review changes
git log --oneline --since="1 week ago"
git diff HEAD~5..HEAD -- docker-compose.prod.yml .env.prod

# 4. Deploy updates
sudo ./scripts/deploy.sh

# 5. Verify deployment
./scripts/health-check.sh --verbose
```

### System Updates

```bash
# 1. Check for updates
sudo apt update
sudo apt list --upgradable

# 2. Plan maintenance window for critical updates
# Schedule during low-traffic periods

# 3. Create system backup
sudo ./scripts/backup.sh --compress

# 4. Apply updates
sudo apt upgrade -y

# 5. Reboot if kernel updates
if [ -f /var/run/reboot-required ]; then
    sudo reboot
fi

# 6. Verify services after reboot
./scripts/health-check.sh --verbose
```

### Docker Updates

```bash
# 1. Check Docker version
docker --version
docker-compose --version

# 2. Plan update (may require service restart)
sudo ./scripts/backup.sh --compress

# 3. Update Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 4. Restart services
sudo ./scripts/deploy.sh

# 5. Verify functionality
./scripts/health-check.sh --verbose
```

## Backup Management

### Backup Strategy

```bash
# Daily automated backups
0 2 * * * /path/to/culicidaelab/scripts/backup.sh --compress

# Weekly backup verification
0 3 * * 0 /path/to/culicidaelab/scripts/backup.sh --verify $(ls -t /var/backups/culicidaelab/ | head -1)

# Monthly backup cleanup
0 4 1 * * /path/to/culicidaelab/scripts/backup.sh --retention-days 90
```

### Backup Testing

```bash
# Monthly backup restore test
# 1. Create test environment
mkdir -p /tmp/backup-test
cd /tmp/backup-test

# 2. Restore backup to test environment
sudo ./scripts/rollback.sh <backup_id> --dry-run

# 3. Verify restored data integrity
# Test database connectivity, file integrity, etc.

# 4. Document test results
echo "Backup test $(date): SUCCESS/FAILURE" >> /var/log/culicidaelab/backup-tests.log
```

### Offsite Backup

```bash
# Configure offsite backup sync
# Example: rsync to remote server
rsync -avz --delete /var/backups/culicidaelab/ backup-server:/backups/culicidaelab/

# Or cloud storage (AWS S3, Google Cloud, etc.)
aws s3 sync /var/backups/culicidaelab/ s3://your-backup-bucket/culicidaelab/
```

## Performance Monitoring

### Key Metrics

```bash
# Response time monitoring
curl -w "@curl-format.txt" -o /dev/null -s http://localhost/api/health

# Resource utilization
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}"

# Database performance
docker exec culicidaelab_backend_prod sqlite3 /app/data/culicidaelab.db ".timer on" ".stats on" "SELECT COUNT(*) FROM sqlite_master;"

# Disk I/O
iostat -x 1 5
```

### Performance Alerts

```bash
# Set up performance monitoring alerts
cat > /usr/local/bin/performance-monitor.sh << 'EOF'
#!/bin/bash
# Check CPU usage
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
if (( $(echo "$CPU_USAGE > 80" | bc -l) )); then
    echo "High CPU usage: $CPU_USAGE%" | mail -s "Performance Alert" admin@example.com
fi

# Check memory usage
MEM_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
if (( $(echo "$MEM_USAGE > 85" | bc -l) )); then
    echo "High memory usage: $MEM_USAGE%" | mail -s "Performance Alert" admin@example.com
fi

# Check disk usage
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    echo "High disk usage: $DISK_USAGE%" | mail -s "Performance Alert" admin@example.com
fi
EOF

chmod +x /usr/local/bin/performance-monitor.sh

# Run every 15 minutes
echo "*/15 * * * * /usr/local/bin/performance-monitor.sh" | crontab -
```

## Security Maintenance

### Security Monitoring

```bash
# Daily security checks
# 1. Check for failed login attempts
sudo grep "Failed password" /var/log/auth.log | tail -20

# 2. Monitor unusual network activity
sudo netstat -tuln | grep LISTEN

# 3. Check for unauthorized processes
ps aux | grep -v "^\(root\|www-data\|systemd\)"

# 4. Review file integrity
find /etc -type f -name "*.conf" -newer /tmp/last-security-check 2>/dev/null
touch /tmp/last-security-check
```

### Security Updates

```bash
# Weekly security update check
sudo apt list --upgradable | grep -i security

# Apply security updates immediately
sudo unattended-upgrades --dry-run
sudo unattended-upgrades

# Update container base images for security patches
docker pull python:3.11-slim
docker pull nginx:alpine
docker pull certbot/certbot
```

### Access Control Review

```bash
# Monthly access review
# 1. Review SSH keys
sudo cat /root/.ssh/authorized_keys
sudo cat /home/*/.ssh/authorized_keys

# 2. Check sudo access
sudo cat /etc/sudoers
sudo ls -la /etc/sudoers.d/

# 3. Review firewall rules
sudo ufw status numbered

# 4. Check for unauthorized users
sudo cat /etc/passwd | grep -E ":[0-9]{4,}:"
```

## Maintenance Checklists

### Pre-Maintenance Checklist

- [ ] Maintenance window scheduled and communicated
- [ ] Current backup created and verified
- [ ] Rollback plan prepared
- [ ] Monitoring alerts configured
- [ ] Emergency contacts available
- [ ] Documentation updated

### Post-Maintenance Checklist

- [ ] All services running and healthy
- [ ] Health checks passing
- [ ] Performance metrics normal
- [ ] No errors in logs
- [ ] Backup integrity verified
- [ ] Documentation updated
- [ ] Maintenance log completed

### Emergency Response Checklist

- [ ] Issue identified and categorized
- [ ] Stakeholders notified
- [ ] Immediate mitigation applied
- [ ] Root cause analysis initiated
- [ ] Recovery plan executed
- [ ] Post-incident review scheduled
- [ ] Preventive measures implemented

---

**Last Updated**: October 2024
**Version**: 1.0
**Maintainer**: CulicidaeLab Team
