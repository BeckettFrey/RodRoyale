#!/bin/bash
set -euo pipefail

# Check for required commands
for cmd in sed make docker grep cp; do
    command -v "$cmd" >/dev/null 2>&1 || { echo "Error: $cmd is not installed."; exit 1; }
done

# Check if docker is running
if ! docker info >/dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Prompt for Cloudinary credentials
read -rp "Enter your Cloudinary Cloud Name: " CLOUDINARY_CLOUD_NAME
read -rp "Enter your Cloudinary API Key: " CLOUDINARY_API_KEY
read -rp "Enter your Cloudinary API Secret: " CLOUDINARY_API_SECRET

if [[ -z "$CLOUDINARY_CLOUD_NAME" || -z "$CLOUDINARY_API_KEY" || -z "$CLOUDINARY_API_SECRET" ]]; then
    echo "Error: All Cloudinary credentials must be provided."
    exit 1
fi

# Bootstrap .env from .env.example
if [ ! -f .env ]; then
    if [ ! -f .env.example ]; then
        echo "Error: .env.example not found."
        exit 1
    fi
    cp .env.example .env
    echo ".env created from .env.example."
fi

cp .env .env.bak

for var in CLOUDINARY_CLOUD_NAME CLOUDINARY_API_KEY CLOUDINARY_API_SECRET; do
    val="${!var}"
    if grep -q "^$var=" .env; then
        sed -i '' "s|^$var=.*|$var=$val|" .env
    else
        echo "$var=$val" >> .env
    fi
done

# Build the project
if make build; then
    echo "Build completed successfully."
else
    echo "Build failed. Exiting."
    exit 1
fi

docker-compose up -d

# Wait for backend container to start
for i in {1..10}; do
    CONTAINER_NAME=$(docker ps --format '{{.Names}}' | grep RodRoyale-api | head -n 1 || true)
    if [ -n "$CONTAINER_NAME" ]; then
        break
    fi
    echo "Waiting for backend container to start... ($i/10)"
    sleep 2
done

if [ -z "$CONTAINER_NAME" ]; then
    echo "Could not find backend container. Please ensure it is running."
    exit 1
fi

# Stage the backend
./scripts/stage-backend.sh "$CONTAINER_NAME"

echo "Quick start complete!"
