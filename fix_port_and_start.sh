#!/bin/bash

echo "========================================"
echo "   Fixing Port and Starting Server"
echo "========================================"
echo ""

cd ~/zimmer-chatbot

# Kill all existing processes
echo "Stopping all existing servers..."
pkill -f "python3 app.py" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
pkill -f "next dev" 2>/dev/null

# Kill processes on ports
for port in 3000 3001 3002 3003 8002; do
    if lsof -ti:$port > /dev/null 2>&1; then
        echo "Killing process on port $port..."
        kill -9 $(lsof -ti:$port) 2>/dev/null
    fi
done

sleep 3
echo "✅ All processes stopped"
echo ""

# Start backend
echo "Starting backend..."
cd backend
source venv/bin/activate 2>/dev/null || true
python3 app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
sleep 5

# Start frontend
echo "Starting frontend..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
sleep 10

# Get actual port
FRONTEND_PORT=$(netstat -tuln 2>/dev/null | grep "300" | grep -oP ':\K[0-9]+' | head -1 || echo "3000")
SERVER_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "========================================"
echo "   ✅ Chatbot Started!"
echo "========================================"
echo ""
echo "Frontend port: $FRONTEND_PORT"
echo ""
echo "On YOUR computer, run:"
echo "   ssh -L 8080:localhost:$FRONTEND_PORT chatbot@vm-185117"
echo ""
echo "Then open: http://localhost:8080"
echo ""

