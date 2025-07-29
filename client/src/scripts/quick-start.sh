#!/bin/bash

set -e

cp .env.example .env
echo "Installing dependencies..."
npm install

echo "Starting client-side service..."
npm run start

