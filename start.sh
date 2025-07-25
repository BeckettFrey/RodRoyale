#!/bin/bash

# Rod Royale Backend Startup Script
echo "🎣 Starting Rod Royale Backend API..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if MongoDB is running (optional - can use MongoDB Atlas)
echo "📡 Checking MongoDB connection..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Set environment variables (modify as needed)
export MONGODB_URL=${MONGODB_URL:-"mongodb://localhost:27017"}
export DATABASE_NAME=${DATABASE_NAME:-"Rod Royale_db"}

echo "🚀 Starting FastAPI server..."
echo "🌐 API will be available at: http://localhost:8000"
echo "📚 API documentation at: http://localhost:8000/docs"
echo ""

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
