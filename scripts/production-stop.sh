#!/bin/bash

# Stop production deployment
# Usage: ./scripts/production-stop.sh

ENV_FILE=".env.production"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: $ENV_FILE not found. No production deployment to stop."
    exit 1
fi

echo "Stopping CulicidaeLab production deployment..."
docker-compose -f docker-compose.prebuilt.yml --env-file "$ENV_FILE" down

echo "Production deployment stopped."
echo ""
echo "To remove all data (WARNING: This will delete all application data):"
echo "  docker-compose -f docker-compose.prebuilt.yml --env-file $ENV_FILE down -v"