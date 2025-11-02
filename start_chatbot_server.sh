#!/bin/bash

# Script to start the chatbot server on Linux
echo "========================================"
echo "   Starting Chatbot Server (Linux)"
echo "========================================"
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Current directory: $(pwd)"
echo ""

# Step 1: Check and install frontend dependencies
echo "[1/3] Checking Frontend Dependencies..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "ERROR: npm install failed!"
        exit 1
    fi
else
    echo "Frontend dependencies found."
fi

cd ..

# Step 2: Start Backend Server
echo ""
echo "[2/3] Starting Backend Server..."
cd backend
source venv/bin/activate 2>/dev/null || true
python3 app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
sleep 5

# Step 3: Start Frontend Server
echo ""
echo "[3/3] Starting Frontend Server..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================"
echo "   Chatbot Started Successfully!"
echo "========================================"
echo ""
echo "Backend:  http://localhost:8002"
echo "Frontend: http://localhost:3000"
echo "Admin:    http://localhost:3000/admin"
echo ""
echo "Backend PID:  $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "To stop the servers, run:"
echo "kill $BACKEND_PID $FRONTEND_PID"
echo ""

