#!/bin/bash
# Usage: ./stage-backend.sh <container_name>
# Runs db_manager.py init and seed inside the given Docker container
# Initializes a feaux database for testing purposes

set -e

if [ -z "$1" ]; then
  echo "Usage: $0 <container_name>"
  exit 1
fi

CONTAINER_NAME="$1"

echo "Running database initialization in container: $CONTAINER_NAME"
docker exec -it "$CONTAINER_NAME" python db_manager.py init

echo "Seeding database in container: $CONTAINER_NAME"
docker exec -it "$CONTAINER_NAME" python db_manager.py seed

echo "Database staged successfully."
