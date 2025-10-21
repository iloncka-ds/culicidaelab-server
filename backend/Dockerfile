# Backend Dockerfile for CulicidaeLab FastAPI application
# Multi-stage build for optimized production image with security hardening

# Build stage
FROM python:3.11-slim AS builder

# Set environment variables for build
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Security: Update system packages and install minimal dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# Set work directory
WORKDIR /app

# Install uv for faster dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml ./
COPY uv.lock ./

# Install Python dependencies
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.11-slim AS production

# Security: Set secure environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app" \
    # Security: Disable Python bytecode generation
    PYTHONDONTWRITEBYTECODE=1 \
    # Security: Force stdout/stderr to be unbuffered
    PYTHONUNBUFFERED=1

# Security: Update system packages and install minimal runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/* \
    && rm -rf /root/.cache

# Security: Create non-root user with minimal privileges
RUN groupadd -r -g 1001 appuser \
    && useradd -r -g appuser -u 1001 -s /bin/false -M -d /app appuser

# Set work directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY backend/ ./backend/
COPY __init__.py ./

# Copy and set up entrypoint script
COPY backend/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Security: Create necessary directories with proper permissions
RUN mkdir -p /app/backend/data /app/backend/static \
    && mkdir -p /app/backend/static/images/predicted/original \
    && mkdir -p /app/backend/static/images/predicted/224x224 \
    && mkdir -p /app/backend/static/images/predicted/100x100 \
    && chown -R appuser:appuser /app \
    && chmod -R 750 /app \
    && chmod -R 755 /app/backend/static

# Note: Volume permissions will be handled by Docker and the host system
# No need for runtime permission fixes as the appuser will inherit proper access

# Database construction steps
# Note: Running as root temporarily for database setup, then switching to appuser
# Set the database path environment variable for build time
ENV CULICIDAELAB_DATABASE_PATH="/app/backend/data/.lancedb"

RUN python -m backend.data.sample_data.generate_sample_data \
    && python -m backend.scripts.populate_lancedb \
    && echo "Database files created:" \
    && find /app/backend/data -type f -name "*.lance" | head -10 \
    && chown -R appuser:appuser /app/backend/data

# Security: Remove unnecessary packages and clean up
RUN apt-get autoremove -y \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Switch to appuser for security
USER appuser

# Security: Set working directory with proper ownership
WORKDIR /app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default environment variables
ENV CULICIDAELAB_DATABASE_PATH="/app/backend/data/.lancedb" \
    CULICIDAELAB_SAVE_PREDICTED_IMAGES="false" \
    CULICIDAELAB_BACKEND_CORS_ORIGINS="http://localhost:8765,http://127.0.0.1:8765"

# Start command (running as appuser)
ENTRYPOINT ["/app/entrypoint.sh"]
