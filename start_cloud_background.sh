#!/bin/bash

# Start chatbot in background on cloud server
echo "Starting chatbot server in background..."

# Navigate to project root (adjust path as needed)
cd ~/chatbot2 || cd /path/to/chatbot2 || cd "$(dirname "$0")"

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "❌ Error: backend directory not found"
    echo "Current directory: $(pwd)"
    echo "Please run: ./setup_and_start_cloud.sh first"
    exit 1
fi

# Navigate to backend
cd backend

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating it..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "Installing dependencies..."
    pip install -r requirements.txt 2>/dev/null || pip install -r ../requirements.txt 2>/dev/null
fi

# Create directories
mkdir -p vectorstore logs __pycache__

# Get port from environment or use default
PORT=${PORT:-8002}
HOST=${HOST:-0.0.0.0}

# Start server in background
echo "Starting server on port $PORT..."
nohup uvicorn app:app --host $HOST --port $PORT --workers 1 > ../backend.log 2>&1 &
SERVER_PID=$!

echo ""
echo "✅ Chatbot server started!"
echo "   PID: $SERVER_PID"
echo "   URL: http://$HOST:$PORT"
echo "   API Docs: http://$HOST:$PORT/docs"
echo "   Logs: tail -f ../backend.log"
echo ""
echo "To stop: kill $SERVER_PID"
echo "To check status: ps aux | grep uvicorn"



