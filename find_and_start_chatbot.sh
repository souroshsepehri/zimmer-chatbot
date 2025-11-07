#!/bin/bash

# Find and start chatbot script
echo "========================================"
echo "   Finding Chatbot Project"
echo "========================================"
echo ""

# Current directory
echo "Current directory: $(pwd)"
echo ""

# Search for chatbot files
echo "Searching for chatbot project..."
echo ""

# Look for app.py in common locations
SEARCH_PATHS=(
    "$HOME"
    "$HOME/projects"
    "$HOME/workspace"
    "/var/www"
    "/opt"
    "."
)

FOUND=false

for path in "${SEARCH_PATHS[@]}"; do
    if [ -d "$path" ]; then
        # Search for backend/app.py
        BACKEND_APP=$(find "$path" -type f -name "app.py" -path "*/backend/app.py" 2>/dev/null | head -1)
        if [ -n "$BACKEND_APP" ]; then
            PROJECT_DIR=$(dirname "$(dirname "$BACKEND_APP")")
            echo "✅ Found chatbot project at: $PROJECT_DIR"
            echo ""
            echo "Backend app.py location: $BACKEND_APP"
            echo ""
            read -p "Use this location? (y/n): " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                cd "$PROJECT_DIR"
                FOUND=true
                break
            fi
        fi
    fi
done

# If not found, list current directory
if [ "$FOUND" = false ]; then
    echo "⚠️ Project not found in common locations"
    echo ""
    echo "Current directory contents:"
    ls -la
    echo ""
    echo "Please provide the path to your chatbot2 directory, or"
    echo "run this script from within the chatbot2 directory"
    exit 1
fi

echo "========================================"
echo "   Setting Up Chatbot"
echo "========================================"
echo ""

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "❌ Backend directory not found in: $(pwd)"
    echo ""
    echo "Directory contents:"
    ls -la
    exit 1
fi

echo "✅ Project directory: $(pwd)"
echo "✅ Backend directory found"
echo ""

# Go to backend
cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "[1/6] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "[1/6] Virtual environment already exists"
fi

# Activate venv
echo ""
echo "[2/6] Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "[3/6] Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

# Find requirements.txt
echo ""
echo "[4/6] Installing dependencies..."
REQUIREMENTS_FILE=""
if [ -f "requirements.txt" ]; then
    REQUIREMENTS_FILE="requirements.txt"
elif [ -f "../requirements.txt" ]; then
    REQUIREMENTS_FILE="../requirements.txt"
else
    echo "❌ Error: requirements.txt not found"
    echo "Looking for requirements files..."
    find .. -name "requirements.txt" -type f 2>/dev/null | head -3
    exit 1
fi

echo "Using: $REQUIREMENTS_FILE"
pip install -r "$REQUIREMENTS_FILE"

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to install dependencies"
    exit 1
fi

# Create directories
echo ""
echo "[5/6] Creating necessary directories..."
mkdir -p vectorstore logs __pycache__
echo "✅ Directories created"

# Check if app.py exists
echo ""
echo "[6/6] Checking app.py..."
if [ ! -f "app.py" ]; then
    echo "❌ Error: app.py not found in backend directory"
    echo "Current directory: $(pwd)"
    echo "Files in backend:"
    ls -la
    exit 1
fi
echo "✅ app.py found"

# Start server
echo ""
echo "========================================"
echo "   Starting Chatbot Server"
echo "========================================"
echo ""

PORT=${PORT:-8002}
HOST=${HOST:-0.0.0.0}

echo "Server starting on: http://$HOST:$PORT"
echo "API Documentation: http://$HOST:$PORT/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn app:app --host $HOST --port $PORT --workers 1



