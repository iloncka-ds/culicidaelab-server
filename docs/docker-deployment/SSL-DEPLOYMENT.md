# CulicidaeLab SSL Deployment Guide

This guide explains how to deploy CulicidaeLab with automatic SSL certificate management using Let's Encrypt.

## 🔒 SSL Features

- **Automatic SSL certificate generation** using Let's Encrypt
- **Automatic certificate renewal** via cron jobs
- **HTTP to HTTPS redirect** for security
- **Self-signed certificates** for development/testing
- **Staging environment support** for testing
- **Security headers** and best practices

## 🚀 Quick SSL Deployment

### Prerequisites

1. **Valid domain name** (not localhost or IP address)
2. **Domain pointing to your server** (A record configured)
3. **Ports 80 and 443 open** in firewall
4. **Docker and Docker Compose** installed

### Deploy with SSL

```bash
# Build the SSL nginx image first
./scripts/build-nginx-ssl.sh 0.1.0

# Deploy with automatic SSL
./scripts/deploy-ssl.sh -d yourdomain.com -e admin@yourdomain.com

# Deploy with staging certificates (for testing)
./scripts/deploy-ssl.sh -d yourdomain.com -e admin@yourdomain.com -s

# Force certificate renewal
./scripts/deploy-ssl.sh -d yourdomain.com -e admin@yourdomain.com -f
```

## 📋 SSL Deployment Process

1. **Builds SSL-enabled nginx image** with certbot integration
2. **Creates environment configuration** with HTTPS URLs
3. **Starts services** with SSL support
4. **Obtains SSL certificates** from Let's Encrypt
5. **Configures automatic renewal** via cron
6. **Sets up HTTP to HTTPS redirect**

## 🔧 SSL Configuration Files

### Docker Images
- `culicidaelab-nginx-ssl:version` - nginx with certbot and SSL support

### Configuration Files
- `docker-compose.ssl.yml` - SSL-enabled Docker Compose configuration
- `nginx/nginx-ssl.conf` - SSL nginx configuration template
- `nginx/Dockerfile.with-certbot` - Dockerfile for SSL nginx image

### Scripts
- `scripts/deploy-ssl.sh` - Main SSL deployment script
- `scripts/build-nginx-ssl.sh` - Build SSL nginx image
- `nginx/scripts/nginx-entrypoint.sh` - SSL initialization script
- `nginx/scripts/nginx-certbot-renew.sh` - Certificate renewal script

## 🌐 Environment Variables

The SSL deployment creates `.env.ssl.production` with:

```env
DOMAIN=yourdomain.com
EMAIL=admin@yourdomain.com
SSL_ENABLED=true
STAGING=false
CLIENT_BACKEND_URL=https://yourdomain.com
STATIC_URL_BASE=https://yourdomain.com
STATIC_FILES_URL=https://yourdomain.com
CORS_ORIGINS=https://yourdomain.com
```

## 📊 SSL Management Commands

```bash
# Check SSL deployment status
docker-compose -f docker-compose.ssl.yml --env-file .env.ssl.production ps

# View SSL nginx logs
docker logs culicidaelab_nginx_ssl

# Check certificate expiration
docker exec culicidaelab_nginx_ssl openssl x509 -enddate -noout -in /etc/letsencrypt/live/yourdomain.com/fullchain.pem

# Force certificate renewal
docker exec culicidaelab_nginx_ssl /scripts/nginx-certbot-renew.sh

# Restart SSL services
docker-compose -f docker-compose.ssl.yml --env-file .env.ssl.production restart

# Stop SSL deployment
docker-compose -f docker-compose.ssl.yml --env-file .env.ssl.production down
```

## 🔍 SSL Troubleshooting

### Certificate Generation Issues

1. **Check domain DNS**: Ensure domain points to your server
   ```bash
   nslookup yourdomain.com
   ```

2. **Check firewall**: Ports 80 and 443 must be open
   ```bash
   sudo ufw status
   ```

3. **Check nginx logs**:
   ```bash
   docker logs culicidaelab_nginx_ssl
   ```

4. **Test Let's Encrypt connectivity**:
   ```bash
   curl -I http://yourdomain.com/.well-known/acme-challenge/test
   ```

### Common Issues

**"Domain validation failed"**
- Ensure domain DNS is correctly configured
- Check that port 80 is accessible from internet
- Verify nginx is serving the webroot correctly

**"Rate limit exceeded"**
- Use staging environment: `-s` flag
- Wait for rate limit reset (usually 1 hour)
- Check Let's Encrypt rate limits documentation

**"Certificate not found"**
- Check if certificate generation completed
- Look for errors in nginx logs
- Try force renewal with `-f` flag

## 🔄 Certificate Renewal

Certificates are automatically renewed via cron job that runs twice daily (3 AM and 3 PM).

### Manual Renewal
```bash
# Force renewal
docker exec culicidaelab_nginx_ssl /scripts/nginx-certbot-renew.sh

# Check renewal logs
docker exec culicidaelab_nginx_ssl cat /var/log/letsencrypt/renewal.log
```

## 🧪 Testing SSL Setup

### Test with Staging Certificates
```bash
# Deploy with staging certificates first
./scripts/deploy-ssl.sh -d yourdomain.com -e admin@yourdomain.com -s

# If successful, deploy with production certificates
./scripts/deploy-ssl.sh -d yourdomain.com -e admin@yourdomain.com -f
```

### SSL Testing Tools
```bash
# Test SSL configuration
curl -I https://yourdomain.com

# Check SSL certificate details
openssl s_client -connect yourdomain.com:443 -servername yourdomain.com

# Online SSL test
# Visit: https://www.ssllabs.com/ssltest/
```

## 🔐 Security Features

The SSL deployment includes:

- **TLS 1.2 and 1.3** support
- **Strong cipher suites**
- **HSTS headers** for security
- **Security headers** (X-Frame-Options, X-Content-Type-Options, etc.)
- **OCSP stapling** for performance
- **HTTP to HTTPS redirect**

## 📈 Production Recommendations

1. **Use production certificates** (not staging)
2. **Monitor certificate expiration**
3. **Set up log monitoring** for renewal failures
4. **Regular backups** of Let's Encrypt data
5. **Test renewal process** periodically
6. **Monitor SSL Labs rating**

## 🔄 Migration from HTTP to HTTPS

If you have an existing HTTP deployment:

1. **Stop HTTP deployment**:
   ```bash
   docker-compose -f docker-compose.prebuilt.yml down
   ```

2. **Deploy SSL version**:
   ```bash
   ./scripts/deploy-ssl.sh -d yourdomain.com -e admin@yourdomain.com
   ```

3. **Update DNS** if needed (should point to same server)

4. **Test HTTPS access** and HTTP redirect

The SSL deployment will automatically handle HTTP to HTTPS redirects, so existing bookmarks will continue to work.
