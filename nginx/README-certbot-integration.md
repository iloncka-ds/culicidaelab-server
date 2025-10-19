# Nginx Container with Integrated Certbot

This directory contains an enhanced nginx Docker container that includes integrated SSL certificate management using Certbot and Let's Encrypt.

## Overview

Instead of using a separate certbot container, this approach integrates SSL certificate management directly into the nginx container, providing:

- **Simplified architecture**: Single container handles both web serving and SSL management
- **Automatic SSL initialization**: Certificates are requested automatically on first startup
- **Automatic renewal**: Built-in cron job handles certificate renewal
- **Graceful fallback**: Falls back to HTTP if SSL initialization fails
- **Health monitoring**: Comprehensive health checks and logging

## Files Structure

```
nginx/
├── Dockerfile.with-certbot          # Enhanced Dockerfile with certbot
├── nginx-ssl.conf                   # SSL-enabled nginx configuration template
├── scripts/
│   ├── nginx-entrypoint.sh         # Main entrypoint with SSL initialization
│   ├── nginx-certbot-init.sh       # Manual certificate initialization
│   └── nginx-certbot-renew.sh      # Certificate renewal script
└── README-certbot-integration.md   # This file
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `DOMAIN_NAME` | Your domain name | `localhost` | Yes* |
| `EMAIL` | Email for Let's Encrypt notifications | `admin@example.com` | Yes* |
| `STAGING` | Use Let's Encrypt staging server (0/1) | `0` | No |
| `BACKEND_HOST` | Backend service hostname | `backend` | No |
| `BACKEND_PORT` | Backend service port | `8000` | No |
| `FRONTEND_HOST` | Frontend service hostname | `frontend` | No |
| `FRONTEND_PORT` | Frontend service port | `8765` | No |
| `RSA_KEY_SIZE` | RSA key size for certificates | `4096` | No |
| `RENEWAL_THRESHOLD` | Days before expiry to renew | `30` | No |

*Required for SSL functionality. If `DOMAIN_NAME` is `localhost`, SSL will be disabled.

### Environment File Example

Create a `.env` file:

```bash
# Domain and SSL Configuration
DOMAIN_NAME=yourdomain.com
EMAIL=admin@yourdomain.com
STAGING=0

# Optional: Advanced Configuration
RSA_KEY_SIZE=4096
RENEWAL_THRESHOLD=30
```

## Usage

### 1. Using Docker Compose (Recommended)

Use the provided `docker-compose.nginx-certbot.yml`:

```bash
# Set your domain and email
export DOMAIN_NAME=yourdomain.com
export EMAIL=admin@yourdomain.com

# Start the services
docker-compose -f docker-compose.nginx-certbot.yml up -d
```

### 2. Manual Docker Build and Run

```bash
# Build the nginx container with certbot
docker build -f nginx/Dockerfile.with-certbot -t nginx-certbot ./nginx

# Run with SSL configuration
docker run -d \
  --name nginx-certbot \
  -p 80:80 -p 443:443 \
  -e DOMAIN_NAME=yourdomain.com \
  -e EMAIL=admin@yourdomain.com \
  -v letsencrypt_certs:/etc/letsencrypt \
  -v certbot_webroot:/var/www/certbot \
  nginx-certbot
```

### 3. Development Mode (HTTP Only)

For local development without SSL:

```bash
# Use localhost domain (disables SSL)
docker-compose -f docker-compose.nginx-certbot.yml up -d
```

## SSL Certificate Management

### Automatic Initialization

The container automatically:

1. **Validates configuration** on startup
2. **Creates dummy certificates** for nginx startup
3. **Requests real certificates** from Let's Encrypt
4. **Configures nginx** with SSL settings
5. **Sets up automatic renewal** via cron

### Manual Certificate Operations

Execute commands inside the running container:

```bash
# Check certificate status
docker exec nginx-certbot /scripts/nginx-certbot-renew.sh status

# Force certificate renewal
docker exec nginx-certbot /scripts/nginx-certbot-renew.sh force-renew

# Manual certificate initialization
docker exec nginx-certbot /scripts/nginx-certbot-init.sh
```

### Certificate Renewal

Certificates are automatically renewed via cron job:
- **Schedule**: Twice daily at 3:30 AM and 3:30 PM
- **Threshold**: 30 days before expiry (configurable)
- **Process**: Check → Renew → Test → Reload nginx
- **Logging**: All operations logged to `/var/log/letsencrypt/renewal.log`

## Monitoring and Troubleshooting

### Health Checks

The container includes comprehensive health monitoring:

```bash
# Check container health
docker ps

# View health check logs
docker inspect nginx-certbot | grep -A 10 Health

# Manual health check
curl http://localhost/.well-known/health
```

### Log Access

```bash
# Container logs (startup and nginx)
docker logs nginx-certbot

# Certificate renewal logs
docker exec nginx-certbot cat /var/log/letsencrypt/renewal.log

# Nginx access logs
docker exec nginx-certbot cat /var/log/nginx/access.log

# Nginx error logs
docker exec nginx-certbot cat /var/log/nginx/error.log
```

### Common Issues

#### 1. Domain Validation Fails

**Symptoms**: Certificate request fails during initialization

**Solutions**:
- Ensure domain points to your server's IP
- Check firewall allows ports 80 and 443
- Verify DNS propagation: `nslookup yourdomain.com`

#### 2. Rate Limiting

**Symptoms**: "too many certificates already issued" error

**Solutions**:
- Use staging server: `STAGING=1`
- Wait for rate limit reset (weekly)
- Check existing certificates: `docker exec nginx-certbot certbot certificates`

#### 3. Nginx Configuration Errors

**Symptoms**: Container fails to start or health checks fail

**Solutions**:
- Check nginx config: `docker exec nginx-certbot nginx -t`
- Review container logs: `docker logs nginx-certbot`
- Verify environment variables are set correctly

## Security Features

### Container Security

- **Non-root execution**: nginx runs as nginx user
- **Minimal attack surface**: Alpine Linux base image
- **Secure file permissions**: Proper ownership and permissions
- **Health monitoring**: Automatic restart on failure

### SSL Security

- **Strong ciphers**: Modern TLS 1.2/1.3 configuration
- **HSTS headers**: Strict Transport Security enabled
- **OCSP stapling**: Certificate validation optimization
- **Security headers**: XSS, clickjacking, and content-type protection

### Certificate Security

- **4096-bit RSA keys**: Strong encryption by default
- **Automatic renewal**: Prevents certificate expiration
- **Secure storage**: Certificates stored in protected volumes
- **Validation**: Certificate integrity checks

## Comparison with Separate Certbot Container

### Advantages of Integrated Approach

✅ **Simpler architecture**: One container instead of two
✅ **Faster startup**: No container coordination needed
✅ **Better error handling**: Direct nginx control
✅ **Reduced complexity**: Fewer moving parts
✅ **Easier debugging**: All logs in one place

### Disadvantages

❌ **Larger container**: Includes certbot dependencies
❌ **Less modular**: Tighter coupling of concerns
❌ **Update complexity**: Need to rebuild for certbot updates

### When to Use Each Approach

**Use Integrated Approach When**:
- You want simpler deployment
- You have a single domain
- You prefer fewer containers
- You want faster startup times

**Use Separate Container When**:
- You manage multiple domains/services
- You want maximum modularity
- You frequently update certbot
- You have complex certificate requirements

## Migration from Separate Certbot

If migrating from a separate certbot container:

1. **Backup existing certificates**:
   ```bash
   docker cp certbot_container:/etc/letsencrypt ./letsencrypt_backup
   ```

2. **Stop existing services**:
   ```bash
   docker-compose down
   ```

3. **Import certificates** (optional):
   ```bash
   docker run --rm -v letsencrypt_certs:/etc/letsencrypt -v ./letsencrypt_backup:/backup alpine cp -r /backup/* /etc/letsencrypt/
   ```

4. **Start with new configuration**:
   ```bash
   docker-compose -f docker-compose.nginx-certbot.yml up -d
   ```

## Support and Maintenance

### Regular Maintenance

- **Monitor logs**: Check renewal logs weekly
- **Update container**: Rebuild monthly for security updates
- **Backup certificates**: Regular backup of letsencrypt volume
- **Test renewals**: Periodic manual renewal testing

### Updates

To update the container with latest security patches:

```bash
# Rebuild the container
docker-compose -f docker-compose.nginx-certbot.yml build --no-cache nginx

# Restart with new image
docker-compose -f docker-compose.nginx-certbot.yml up -d nginx
```

This integrated approach provides a robust, secure, and maintainable SSL solution for your application deployment.
