#!/bin/bash

# Ensure the user provides the Heroku app name
if [ -z "$1" ]; then
  echo "Usage: ./set-heroku-env.sh <heroku-app-name> [<project-subdirectory>]"
  exit 1
fi

HEROKU_APP=$1

# Check if .env file exists
if [ ! -f .env ]; then
  echo ".env file not found in current directory"
  exit 1
fi

# Export and apply each variable
echo "Setting environment variables for Heroku app: $HEROKU_APP"

# Read each line in .env, ignore empty lines and comments
while IFS='=' read -r key value || [ -n "$key" ]; do
  if [[ ! "$key" =~ ^# && -n "$key" && -n "$value" ]]; then
    echo "Setting $key"
    heroku config:set "$key=$value" --app "$HEROKU_APP"
  fi
done < .env