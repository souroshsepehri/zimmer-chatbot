#!/bin/bash

# Quick start script - stops old processes and starts both servers
cd ~/zimmer-chatbot

# Stop all existing servers
echo "Stopping existing servers..."
pkill -f "python3 app.py" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
pkill -f "next dev" 2>/dev/null
kill -9 $(lsof -ti:8002) 2>/dev/null 2>/dev/null
for port in 3000 3001 3002 3003; do
    kill -9 $(lsof -ti:$port) 2>/dev/null 2>/dev/null
done
sleep 2

# Start Backend
echo "Starting Backend..."
cd backend
source venv/bin/activate 2>/dev/null || true
python3 app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
sleep 5

# Start Frontend
echo "Starting Frontend..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
sleep 8

# Show status
SERVER_IP=$(hostname -I | awk '{print $1}')
FRONTEND_PORT=$(netstat -tuln 2>/dev/null | grep "300" | grep -oP ':\K[0-9]+' | head -1 || echo "3000")

echo ""
echo "========================================"
echo "✅ Servers Started!"
echo "========================================"
echo "Backend:  http://$SERVER_IP:8002"
echo "Frontend: http://$SERVER_IP:$FRONTEND_PORT"
echo "Admin:    http://$SERVER_IP:$FRONTEND_PORT/admin"
echo ""
echo "PIDs: Backend=$BACKEND_PID, Frontend=$FRONTEND_PID"
echo ""

