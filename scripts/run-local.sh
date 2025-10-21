#!/bin/bash
# Bash script to run local Docker containers with proper environment
# Usage: ./scripts/run-local.sh

echo "Starting CulicidaeLab local development environment..."

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "Error: .env.local file not found!"
    echo "Please create .env.local file with local development settings."
    exit 1
fi

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose -f docker-compose.local.yml --env-file .env.local down

# Pull latest images
echo "Pulling latest images..."
docker-compose -f docker-compose.local.yml --env-file .env.local pull

# Start containers
echo "Starting containers..."
docker-compose -f docker-compose.local.yml --env-file .env.local up -d

# Show status
echo "Container status:"
docker-compose -f docker-compose.local.yml --env-file .env.local ps

echo ""
echo "Local development environment is running!"
echo "Frontend: http://localhost:8765"
echo "Backend API: http://localhost:8000"
echo "Nginx: http://localhost"
echo ""
echo "To view logs: docker-compose -f docker-compose.local.yml --env-file .env.local logs -f"
echo "To stop: docker-compose -f docker-compose.local.yml --env-file .env.local down"