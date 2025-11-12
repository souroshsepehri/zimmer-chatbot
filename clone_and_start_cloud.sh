#!/bin/bash

# Clone and Start Chatbot on Cloud Server
echo "========================================"
echo "   Clone and Start Chatbot on Cloud"
echo "========================================"
echo ""

# Exit venv if active
deactivate 2>/dev/null || true

# Go to home directory
cd ~

# Remove existing chatbot2 if it exists (optional)
if [ -d "chatbot2" ]; then
    echo "⚠️ Existing chatbot2 directory found"
    read -p "Remove existing chatbot2 and re-clone? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf chatbot2
        echo "✅ Removed existing directory"
    else
        echo "Using existing directory..."
        cd chatbot2
    fi
else
    # Clone the repository
    echo "[1/8] Cloning repository..."
    git clone https://github.com/souroshsepehri/zimmer-chatbot.git chatbot2
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to clone repository"
        echo "Make sure git is installed: sudo apt-get install git -y"
        exit 1
    fi
    echo "✅ Repository cloned"
    cd chatbot2
fi

echo ""
echo "Current directory: $(pwd)"
echo ""

# Verify git remote
echo "[2/8] Verifying Git remote..."
git remote -v
echo ""

# Go to backend
echo "[3/8] Setting up backend..."
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "[4/8] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment"
        echo "Install python3-venv: sudo apt-get install python3-venv -y"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "[4/8] Virtual environment already exists"
fi

# Activate venv
echo ""
echo "[5/8] Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "[6/8] Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Install dependencies
echo ""
echo "[7/8] Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
elif [ -f "../requirements.txt" ]; then
    pip install -r ../requirements.txt
else
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi

# Create directories
echo ""
echo "[8/8] Creating necessary directories..."
mkdir -p vectorstore logs __pycache__
echo "✅ Directories created"

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found in backend directory"
    exit 1
fi

# Start server
echo ""
echo "========================================"
echo "   Starting Chatbot Server"
echo "========================================"
echo ""

PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}

echo "Server starting on: http://$HOST:$PORT"
echo "API Documentation: http://$HOST:$PORT/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app:app --host $HOST --port $PORT --workers 1



