# CulicidaeLab Troubleshooting Guide

This guide provides solutions to common issues encountered when deploying and running the CulicidaeLab application.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Container Issues](#container-issues)
- [SSL Certificate Problems](#ssl-certificate-problems)
- [Database Issues](#database-issues)
- [Network Connectivity](#network-connectivity)
- [Performance Problems](#performance-problems)
- [Backup and Recovery Issues](#backup-and-recovery-issues)
- [Development Environment Issues](#development-environment-issues)
- [Error Code Reference](#error-code-reference)

## Quick Diagnostics

### Health Check Command
```bash
# Run comprehensive health check
./scripts/health-check.sh --verbose

# Get JSON output for detailed analysis
./scripts/health-check.sh --json | jq .
```

### System Status Overview
```bash
# Check all container status
docker-compose -f docker-compose.prod.yml ps

# Check system resources
df -h && free -h

# Check recent logs
docker-compose -f docker-compose.prod.yml logs --tail=50
```

## Container Issues

### Issue: Containers Not Starting

**Symptoms:**
- Containers exit immediately after starting
- `docker-compose ps` shows containers as "Exit 1" or "Exit 125"
- Services are not accessible

**Diagnosis:**
```bash
# Check container status and exit codes
docker-compose -f docker-compose.prod.yml ps

# View container logs
docker-compose -f docker-compose.prod.yml logs [service_name]

# Check Docker daemon status
sudo systemctl status docker

# Verify Docker Compose file syntax
docker-compose -f docker-compose.prod.yml config
```

**Common Causes and Solutions:**

1. **Port Conflicts**
   ```bash
   # Check what's using ports 80/443
   sudo netstat -tulpn | grep :80
   sudo netstat -tulpn | grep :443

   # Stop conflicting services
   sudo systemctl stop apache2  # or nginx if running outside Docker
   ```

2. **Insufficient Disk Space**
   ```bash
   # Check disk usage
   df -h

   # Clean up Docker resources
   docker system prune -f
   docker volume prune -f
   ```

3. **Memory Issues**
   ```bash
   # Check memory usage
   free -h

   # Reduce resource limits in docker-compose.prod.yml
   # Or add swap space
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

4. **Environment Configuration Errors**
   ```bash
   # Validate environment file
   cat .env.prod | grep -v '^#' | grep -v '^$'

   # Check for missing required variables
   grep -E "DOMAIN_NAME|CERTBOT_EMAIL" .env.prod
   ```

### Issue: Container Health Checks Failing

**Symptoms:**
- Containers show as "unhealthy" in `docker ps`
- Services are running but marked as unhealthy

**Diagnosis:**
```bash
# Check health check logs
docker inspect culicidaelab_backend_prod | jq '.[0].State.Health'

# Test health endpoints manually
curl -f http://localhost/api/health
curl -f http://localhost:8765/
```

**Solutions:**

1. **Backend Health Check Issues**
   ```bash
   # Check if backend is responding
   docker exec culicidaelab_backend_prod curl -f http://localhost:8000/api/health

   # Check backend logs
   docker logs culicidaelab_backend_prod --tail=100

   # Restart backend if needed
   docker-compose -f docker-compose.prod.yml restart backend
   ```

2. **Frontend Health Check Issues**
   ```bash
   # Check frontend accessibility
   docker exec culicidaelab_frontend_prod curl -f http://localhost:8765/

   # Check if frontend can reach backend
   docker exec culicidaelab_frontend_prod curl -f http://backend:8000/api/health
   ```

### Issue: Container Resource Limits

**Symptoms:**
- Containers being killed (OOMKilled)
- Poor performance
- High CPU usage

**Solutions:**
```bash
# Monitor resource usage
docker stats --no-stream

# Adjust limits in docker-compose.prod.yml
# Increase memory limits:
deploy:
  resources:
    limits:
      memory: 2G  # Increase from 1G
    reservations:
      memory: 1G  # Increase from 512M
```

## SSL Certificate Problems

### Issue: Certificate Generation Fails

**Symptoms:**
- HTTPS not working
- Certificate files missing in `/etc/letsencrypt/`
- Certbot container logs show errors

**Diagnosis:**
```bash
# Check certbot logs
docker logs culicidaelab_certbot_prod

# Verify domain DNS
nslookup $DOMAIN_NAME

# Test HTTP accessibility (required for certificate generation)
curl -I http://$DOMAIN_NAME/
```

**Common Causes and Solutions:**

1. **Domain Not Pointing to Server**
   ```bash
   # Check DNS resolution
   dig $DOMAIN_NAME

   # Verify external accessibility
   curl -I http://$DOMAIN_NAME/ --connect-timeout 10
   ```
   **Solution**: Update DNS records to point to your server's IP

2. **Firewall Blocking Port 80**
   ```bash
   # Check firewall status
   sudo ufw status

   # Allow HTTP traffic
   sudo ufw allow 80/tcp
   ```

3. **Rate Limiting**
   ```bash
   # Check for rate limit errors in logs
   docker logs culicidaelab_certbot_prod | grep -i "rate limit"
   ```
   **Solution**: Wait for rate limit to reset or use staging environment for testing

4. **Webroot Challenge Issues**
   ```bash
   # Verify webroot directory is accessible
   docker exec culicidaelab_nginx_prod ls -la /var/www/certbot/

   # Test challenge endpoint
   echo "test" | docker exec -i culicidaelab_nginx_prod tee /var/www/certbot/test.txt
   curl http://$DOMAIN_NAME/.well-known/acme-challenge/test.txt
   ```

### Issue: Certificate Renewal Fails

**Symptoms:**
- Certificate expired
- Renewal process failing
- HTTPS stops working after some time

**Solutions:**
```bash
# Force certificate renewal
docker exec culicidaelab_certbot_prod certbot renew --force-renewal

# Check certificate expiration
openssl x509 -enddate -noout -in /etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem

# Restart nginx after renewal
docker-compose -f docker-compose.prod.yml restart nginx
```

### Issue: Mixed Content Errors

**Symptoms:**
- Some resources load over HTTP instead of HTTPS
- Browser security warnings

**Solutions:**
```bash
# Check nginx SSL configuration
docker exec culicidaelab_nginx_prod nginx -t

# Verify HSTS headers
curl -I https://$DOMAIN_NAME/ | grep -i strict

# Update nginx configuration to force HTTPS
# Add to nginx.conf:
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## Database Issues

### Issue: Database Connection Errors

**Symptoms:**
- Backend API returns database errors
- "Database locked" or "Database not found" errors

**Diagnosis:**
```bash
# Check database file exists
docker exec culicidaelab_backend_prod ls -la /app/data/

# Test database connection
docker exec culicidaelab_backend_prod sqlite3 /app/data/culicidaelab.db ".tables"

# Check database file permissions
docker exec culicidaelab_backend_prod stat /app/data/culicidaelab.db
```

**Solutions:**

1. **Database File Missing**
   ```bash
   # Initialize new database
   docker exec culicidaelab_backend_prod python -c "
   import sqlite3
   conn = sqlite3.connect('/app/data/culicidaelab.db')
   conn.execute('CREATE TABLE IF NOT EXISTS test (id INTEGER)')
   conn.close()
   print('Database initialized')
   "
   ```

2. **Permission Issues**
   ```bash
   # Fix database permissions
   docker exec culicidaelab_backend_prod chown app:app /app/data/culicidaelab.db
   docker exec culicidaelab_backend_prod chmod 664 /app/data/culicidaelab.db
   ```

3. **Database Corruption**
   ```bash
   # Check database integrity
   docker exec culicidaelab_backend_prod sqlite3 /app/data/culicidaelab.db "PRAGMA integrity_check;"

   # Restore from backup if corrupted
   sudo ./scripts/rollback.sh <backup_id>
   ```

### Issue: Database Performance Problems

**Symptoms:**
- Slow query responses
- High CPU usage from backend
- Timeout errors

**Solutions:**
```bash
# Analyze database size
docker exec culicidaelab_backend_prod sqlite3 /app/data/culicidaelab.db ".dbinfo"

# Vacuum database to optimize
docker exec culicidaelab_backend_prod sqlite3 /app/data/culicidaelab.db "VACUUM;"

# Check for long-running queries
docker logs culicidaelab_backend_prod | grep -i "slow query"
```

## Network Connectivity

### Issue: Services Cannot Communicate

**Symptoms:**
- Frontend cannot reach backend
- API calls failing with connection errors
- Internal service discovery not working

**Diagnosis:**
```bash
# Check Docker network
docker network ls
docker network inspect culicidaelab_network

# Test internal connectivity
docker exec culicidaelab_frontend_prod ping backend
docker exec culicidaelab_frontend_prod curl http://backend:8000/api/health

# Check service names resolution
docker exec culicidaelab_frontend_prod nslookup backend
```

**Solutions:**

1. **Network Configuration Issues**
   ```bash
   # Recreate Docker network
   docker-compose -f docker-compose.prod.yml down
   docker network rm culicidaelab_network
   docker-compose -f docker-compose.prod.yml up -d
   ```

2. **Service Dependencies**
   ```bash
   # Check service startup order
   docker-compose -f docker-compose.prod.yml logs | grep "depends_on"

   # Restart services in correct order
   docker-compose -f docker-compose.prod.yml restart backend
   docker-compose -f docker-compose.prod.yml restart frontend
   ```

### Issue: External Connectivity Problems

**Symptoms:**
- Cannot access application from internet
- Timeouts when accessing domain
- DNS resolution issues

**Solutions:**
```bash
# Check external accessibility
curl -I http://$DOMAIN_NAME/ --connect-timeout 10

# Verify firewall rules
sudo ufw status numbered

# Check nginx configuration
docker exec culicidaelab_nginx_prod nginx -t
docker logs culicidaelab_nginx_prod | grep -i error
```

## Performance Problems

### Issue: Slow Response Times

**Symptoms:**
- High response times (>5 seconds)
- Timeouts on API calls
- Poor user experience

**Diagnosis:**
```bash
# Check response times
./scripts/health-check.sh --verbose | grep "response_time"

# Monitor container performance
docker stats --no-stream

# Check system load
uptime
iostat 1 5
```

**Solutions:**

1. **Resource Optimization**
   ```bash
   # Increase worker processes
   # Edit .env.prod:
   WORKERS=4  # Increase based on CPU cores

   # Optimize memory allocation
   # Edit docker-compose.prod.yml resource limits
   ```

2. **Database Optimization**
   ```bash
   # Optimize database
   docker exec culicidaelab_backend_prod sqlite3 /app/data/culicidaelab.db "ANALYZE;"
   docker exec culicidaelab_backend_prod sqlite3 /app/data/culicidaelab.db "VACUUM;"
   ```

3. **Nginx Optimization**
   ```bash
   # Enable gzip compression (check nginx.conf)
   gzip on;
   gzip_types text/plain application/json application/javascript text/css;

   # Enable caching for static files
   location /static/ {
       expires 1y;
       add_header Cache-Control "public, immutable";
   }
   ```

### Issue: High Memory Usage

**Symptoms:**
- System running out of memory
- OOMKilled containers
- Swap usage high

**Solutions:**
```bash
# Check memory usage by container
docker stats --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"

# Reduce memory limits if needed
# Edit docker-compose.prod.yml:
deploy:
  resources:
    limits:
      memory: 512M  # Reduce if necessary

# Add swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

## Backup and Recovery Issues

### Issue: Backup Creation Fails

**Symptoms:**
- Backup script exits with errors
- Incomplete backups
- Cannot create backup files

**Diagnosis:**
```bash
# Run backup with verbose output
sudo ./scripts/backup.sh --verbose

# Check disk space for backups
df -h /var/backups/culicidaelab/

# Check backup directory permissions
ls -la /var/backups/culicidaelab/
```

**Solutions:**

1. **Insufficient Disk Space**
   ```bash
   # Clean up old backups
   sudo ./scripts/backup.sh --retention-days 7

   # Move backups to different location
   sudo mv /var/backups/culicidaelab/* /external/storage/backups/
   ```

2. **Permission Issues**
   ```bash
   # Fix backup directory permissions
   sudo chown -R root:root /var/backups/culicidaelab/
   sudo chmod 755 /var/backups/culicidaelab/
   ```

### Issue: Restore/Rollback Fails

**Symptoms:**
- Rollback script fails
- Services don't start after restore
- Data inconsistencies after rollback

**Solutions:**
```bash
# Verify backup integrity before restore
sudo ./scripts/backup.sh --verify <backup_id>

# Perform dry run first
sudo ./scripts/rollback.sh <backup_id> --dry-run

# Check rollback logs
tail -f /var/log/culicidaelab/rollback.log
```

## Development Environment Issues

### Issue: Hot Reload Not Working

**Symptoms:**
- Code changes not reflected
- Need to restart containers manually
- Development workflow slow

**Solutions:**
```bash
# Check volume mounts
docker-compose -f docker-compose.dev.yml config | grep volumes -A 5

# Verify file watching
docker logs culicidaelab_backend_dev | grep -i reload

# Restart development services
docker-compose -f docker-compose.dev.yml restart
```

### Issue: Development Tools Not Accessible

**Symptoms:**
- Cannot access Adminer or Dozzle
- Development ports not exposed
- Tools not starting

**Solutions:**
```bash
# Check if tools are enabled
docker-compose -f docker-compose.dev.yml --profile tools up -d

# Verify port mappings
docker-compose -f docker-compose.dev.yml ps

# Check tool-specific logs
docker logs culicidaelab_adminer_dev
docker logs culicidaelab_logs_dev
```

## Error Code Reference

### HTTP Error Codes

| Code | Description | Common Causes | Solutions |
|------|-------------|---------------|-----------|
| 502 | Bad Gateway | Backend not responding | Check backend health, restart services |
| 503 | Service Unavailable | Service overloaded | Check resources, scale services |
| 504 | Gateway Timeout | Slow backend response | Optimize database, increase timeouts |
| 404 | Not Found | Routing issues | Check nginx configuration |
| 500 | Internal Server Error | Application error | Check backend logs |

### Docker Exit Codes

| Code | Description | Common Causes | Solutions |
|------|-------------|---------------|-----------|
| 0 | Success | Normal exit | No action needed |
| 1 | General Error | Application error | Check logs, fix configuration |
| 125 | Docker Error | Docker daemon issue | Restart Docker, check syntax |
| 126 | Permission Error | File permissions | Fix file permissions |
| 127 | Command Not Found | Missing executable | Check Dockerfile, install dependencies |

### SSL/TLS Error Codes

| Error | Description | Solutions |
|-------|-------------|-----------|
| SSL_ERROR_BAD_CERT_DOMAIN | Domain mismatch | Update certificate for correct domain |
| SSL_ERROR_EXPIRED_CERT | Certificate expired | Renew certificate |
| SSL_ERROR_SELF_SIGNED_CERT | Self-signed certificate | Use proper CA certificate |

## Getting Help

### Log Collection for Support

```bash
# Collect comprehensive logs
mkdir -p /tmp/culicidaelab-logs
docker-compose -f docker-compose.prod.yml logs > /tmp/culicidaelab-logs/docker-logs.txt
./scripts/health-check.sh --json > /tmp/culicidaelab-logs/health-check.json
cp /var/log/culicidaelab/* /tmp/culicidaelab-logs/ 2>/dev/null || true
tar -czf culicidaelab-logs-$(date +%Y%m%d_%H%M%S).tar.gz -C /tmp culicidaelab-logs/
```

### Support Channels

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check latest documentation
- **Community Forum**: Ask questions and share solutions
- **Email Support**: support@your-domain.com (for critical issues)

### Before Contacting Support

1. Run health check: `./scripts/health-check.sh --verbose`
2. Check recent logs: `docker-compose logs --tail=100`
3. Verify configuration: `docker-compose config`
4. Try basic troubleshooting steps from this guide
5. Collect logs using the script above

---

**Last Updated**: October 2024
**Version**: 1.0
**Maintainer**: CulicidaeLab Team
