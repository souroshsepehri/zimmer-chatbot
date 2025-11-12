#!/bin/bash

# Cloud Server Setup and Start Script for Persian Chatbot
echo "========================================"
echo "   Persian Chatbot - Cloud Server Setup"
echo "========================================"
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Current directory: $(pwd)"
echo ""

# Step 1: Check if we're in the right directory
if [ ! -f "requirements.txt" ] && [ ! -d "backend" ]; then
    echo "❌ Error: Not in chatbot2 project directory"
    echo "Please navigate to your chatbot2 directory first:"
    echo "  cd /path/to/chatbot2"
    exit 1
fi

# Step 2: Create backend directory if it doesn't exist
if [ ! -d "backend" ]; then
    echo "⚠️ Backend directory not found. Creating structure..."
    mkdir -p backend
    echo "✅ Created backend directory"
fi

# Step 3: Navigate to backend
cd backend

# Step 4: Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "[1/5] Creating Python virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment"
        echo "Make sure python3 is installed: sudo apt-get install python3-venv"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "[1/5] Virtual environment already exists"
fi

# Step 5: Activate virtual environment
echo ""
echo "[2/5] Activating virtual environment..."
source venv/bin/activate

# Step 6: Upgrade pip
echo ""
echo "[3/5] Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Step 7: Install dependencies
echo ""
echo "[4/5] Installing Python dependencies..."
if [ -f "../requirements.txt" ]; then
    pip install -r ../requirements.txt
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt not found, installing from backend/requirements.txt"
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
    else
        echo "❌ Error: No requirements.txt found"
        exit 1
    fi
fi

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi

# Step 8: Create necessary directories
echo ""
echo "[5/5] Creating necessary directories..."
mkdir -p vectorstore
mkdir -p logs
mkdir -p __pycache__
echo "✅ Directories created"

# Step 9: Check if app.py exists
if [ ! -f "app.py" ]; then
    echo ""
    echo "❌ Error: app.py not found in backend directory"
    echo "Please make sure your project files are uploaded correctly"
    exit 1
fi

# Step 10: Start the server
echo ""
echo "========================================"
echo "   Starting Chatbot Server"
echo "========================================"
echo ""

# Get port from environment or use default
PORT=${PORT:-8001}
HOST=${HOST:-0.0.0.0}

echo "Server will start on: http://$HOST:$PORT"
echo "API Documentation: http://$HOST:$PORT/docs"
echo ""
echo "To stop the server, press Ctrl+C"
echo ""

# Start uvicorn
uvicorn app:app --host $HOST --port $PORT --workers 1



