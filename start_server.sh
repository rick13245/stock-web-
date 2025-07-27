#!/bin/bash

# Advanced Stock Market Signal Bot - FastAPI Server Startup Script

echo "🚀 Starting Advanced Stock Market Signal Bot API Server..."
echo "==============================================="

# Add local bin to PATH
export PATH=$PATH:/home/ubuntu/.local/bin

# Create necessary directories
mkdir -p static logs data/historical reports charts

# Check if required files exist
if [ ! -f "fastapi_app.py" ]; then
    echo "❌ Error: fastapi_app.py not found"
    exit 1
fi

if [ ! -f "static/index.html" ]; then
    echo "❌ Error: static/index.html not found"
    exit 1
fi

# Start the server
echo "📡 Starting FastAPI server on http://localhost:8000"
echo "📚 API Documentation will be available at: http://localhost:8000/docs"
echo "🌐 Web Interface will be available at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start uvicorn with proper settings
python3 -m uvicorn fastapi_app:app --host 0.0.0.0 --port 8000 --reload --log-level info