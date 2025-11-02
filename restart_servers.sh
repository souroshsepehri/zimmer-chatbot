#!/bin/bash

echo "========================================"
echo "   Stopping Old Servers"
echo "========================================"

# Kill existing processes
echo "Killing existing backend processes..."
pkill -f "python3 app.py"
pkill -f "uvicorn"

echo "Killing existing frontend processes..."
pkill -f "npm run dev"
pkill -f "next dev"
pkill -f "next-server"

# Wait for processes to stop
sleep 3

# Make sure ports are free
echo "Checking ports..."
if lsof -ti:8002 > /dev/null 2>&1; then
    echo "Port 8002 still in use, killing process..."
    kill -9 $(lsof -ti:8002) 2>/dev/null
fi

if lsof -ti:3000 > /dev/null 2>&1; then
    echo "Port 3000 still in use, killing process..."
    kill -9 $(lsof -ti:3000) 2>/dev/null
fi

sleep 2

echo "✅ Old processes stopped"
echo ""

echo "========================================"
echo "   Starting Servers"
echo "========================================"

# Get project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Start Backend
echo "[1/2] Starting Backend Server on port 8002..."
cd backend
source venv/bin/activate 2>/dev/null || true
python3 app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
sleep 5

# Verify backend started
if ps -p $BACKEND_PID > /dev/null; then
    echo "✅ Backend started (PID: $BACKEND_PID)"
else
    echo "❌ Backend failed to start - check backend.log"
    tail -10 backend.log
fi

# Start Frontend
echo ""
echo "[2/2] Starting Frontend Server on port 3000..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
sleep 8

# Verify frontend started
if ps -p $FRONTEND_PID > /dev/null; then
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
else
    echo "❌ Frontend failed to start - check frontend.log"
    tail -10 frontend.log
fi

echo ""
echo "========================================"
echo "   Server Status"
echo "========================================"

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

# Check which ports are actually listening
BACKEND_PORT=$(netstat -tuln 2>/dev/null | grep "python3\|uvicorn" | grep -oP ':\K[0-9]+' | head -1 || echo "8002")
FRONTEND_PORT=$(netstat -tuln 2>/dev/null | grep "300" | grep -oP ':\K[0-9]+' | head -1 || echo "3000")

echo ""
echo "Backend PID:  $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "Access URLs:"
echo "  Backend:  http://localhost:$BACKEND_PORT"
echo "  Backend:  http://$SERVER_IP:$BACKEND_PORT"
echo "  Frontend: http://localhost:$FRONTEND_PORT"
echo "  Frontend: http://$SERVER_IP:$FRONTEND_PORT"
echo "  Admin:    http://$SERVER_IP:$FRONTEND_PORT/admin"
echo ""
echo "To stop servers:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo ""

