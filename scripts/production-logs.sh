#!/bin/bash

# View production logs
# Usage: ./scripts/production-logs.sh [service_name]

ENV_FILE=".env.production"

if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: $ENV_FILE not found. Run deploy-production.sh first."
    exit 1
fi

if [[ -n "$1" ]]; then
    echo "Showing logs for service: $1"
    docker-compose -f docker-compose.prebuilt.yml --env-file "$ENV_FILE" logs -f "$1"
else
    echo "Showing logs for all services (press Ctrl+C to exit)"
    docker-compose -f docker-compose.prebuilt.yml --env-file "$ENV_FILE" logs -f
fi