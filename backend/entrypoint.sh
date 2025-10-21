#!/bin/bash
set -e

echo "Starting CulicidaeLab Backend..."

# Create predicted image directories if they don't exist
echo "Creating predicted image directories..."
mkdir -p /app/backend/static/images/predicted/original
mkdir -p /app/backend/static/images/predicted/224x224
mkdir -p /app/backend/static/images/predicted/100x100

# Set proper permissions
echo "Setting permissions for predicted image directories..."
chmod -R 755 /app/backend/static/images/predicted

# Verify directories exist
echo "Verifying directory structure:"
ls -la /app/backend/static/images/predicted/

# Check environment variables
echo "Environment variables:"
echo "CULICIDAELAB_SAVE_PREDICTED_IMAGES: ${CULICIDAELAB_SAVE_PREDICTED_IMAGES:-not set}"
echo "CULICIDAELAB_DATABASE_PATH: ${CULICIDAELAB_DATABASE_PATH:-not set}"

# Start the application
echo "Starting FastAPI application..."
exec python -m backend.main