#!/bin/bash
set -e

echo "Starting CulicidaeLab Backend..."

# Create predicted image directories if they don't exist
echo "Creating predicted image directories..."
mkdir -p /app/backend/static/images/predicted/original 2>/dev/null || echo "Directory already exists"
mkdir -p /app/backend/static/images/predicted/224x224 2>/dev/null || echo "Directory already exists"
mkdir -p /app/backend/static/images/predicted/100x100 2>/dev/null || echo "Directory already exists"

# Skip permission changes - they're not needed for functionality
echo "Skipping permission changes (not required for volume mounts)"

# Test write permissions without changing them
echo "Testing write permissions..."
test_dirs=("/app/backend/static/images/predicted/original" "/app/backend/static/images/predicted/224x224" "/app/backend/static/images/predicted/100x100")

for dir in "${test_dirs[@]}"; do
    if touch "$dir/test_write_$$" 2>/dev/null; then
        rm -f "$dir/test_write_$$"
        echo "✓ $dir is writable"
    else
        echo "⚠ Warning: $dir is not writable - image saving may fail"
    fi
done

# Verify directories exist
echo "Verifying directory structure:"
ls -la /app/backend/static/images/predicted/ 2>/dev/null || echo "Could not list directory contents"

# Check environment variables
echo "Environment variables:"
echo "CULICIDAELAB_SAVE_PREDICTED_IMAGES: ${CULICIDAELAB_SAVE_PREDICTED_IMAGES:-not set}"
echo "CULICIDAELAB_DATABASE_PATH: ${CULICIDAELAB_DATABASE_PATH:-not set}"

# Start the application
echo "Starting FastAPI application..."
exec python -m backend.main