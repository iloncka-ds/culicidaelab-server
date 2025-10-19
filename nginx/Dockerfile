# Production nginx Dockerfile with security hardening
FROM nginx:alpine

# Security: Update packages and install minimal dependencies
RUN apk update && apk upgrade && \
    apk add --no-cache \
    curl \
    ca-certificates \
    && rm -rf /var/cache/apk/* \
    && rm -rf /tmp/*

# Security: Create nginx user with proper UID/GID and minimal privileges
RUN addgroup -g 101 -S nginx 2>/dev/null || true && \
    adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx nginx 2>/dev/null || true

# Security: Create necessary directories with proper permissions
RUN mkdir -p /var/www/static /var/www/certbot /var/log/nginx /var/cache/nginx /run/nginx && \
    chown -R nginx:nginx /var/www /var/log/nginx /var/cache/nginx /run/nginx && \
    chmod -R 755 /var/www && \
    chmod -R 750 /var/log/nginx /var/cache/nginx /run/nginx

# Copy custom nginx configuration
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# Security: Set proper permissions for configuration files
RUN chown root:root /etc/nginx/nginx.conf && \
    chmod 644 /etc/nginx/nginx.conf && \
    # Security: Remove default nginx configuration that might expose information
    rm -f /etc/nginx/conf.d/default.conf && \
    # Security: Create nginx.pid file with proper permissions
    touch /run/nginx/nginx.pid && \
    chown nginx:nginx /run/nginx/nginx.pid

# Create a simple index.html for testing
RUN echo '<html><body><h1>nginx is running</h1></body></html>' > /var/www/static/index.html && \
    chown nginx:nginx /var/www/static/index.html

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Use nginx user for security
USER nginx

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
