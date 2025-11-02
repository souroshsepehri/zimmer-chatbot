#!/bin/bash

echo "========================================"
echo "   Complete Diagnostic & Fix"
echo "========================================"
echo ""

cd ~/zimmer-chatbot

# Check if servers are actually running
echo "1. Checking if servers are running..."
BACKEND_PID=$(pgrep -f "python3 app.py")
FRONTEND_PID=$(pgrep -f "npm run dev" || pgrep -f "next dev")

if [ -z "$BACKEND_PID" ]; then
    echo "   ❌ Backend is NOT running"
    echo "   Starting backend..."
    cd backend
    source venv/bin/activate 2>/dev/null || true
    python3 app.py > ../backend.log 2>&1 &
    sleep 5
    echo "   ✅ Backend started"
else
    echo "   ✅ Backend is running (PID: $BACKEND_PID)"
fi

if [ -z "$FRONTEND_PID" ]; then
    echo "   ❌ Frontend is NOT running"
    echo "   Starting frontend..."
    cd frontend
    npm run dev > ../frontend.log 2>&1 &
    sleep 10
    echo "   ✅ Frontend started"
else
    echo "   ✅ Frontend is running (PID: $FRONTEND_PID)"
fi

echo ""

# Get actual frontend port
echo "2. Checking frontend port..."
FRONTEND_PORT=$(netstat -tuln 2>/dev/null | grep "300" | grep -oP ':\K[0-9]+' | head -1)
if [ -z "$FRONTEND_PORT" ]; then
    echo "   ⚠️  Frontend port not detected, waiting..."
    sleep 5
    FRONTEND_PORT=$(netstat -tuln 2>/dev/null | grep "300" | grep -oP ':\K[0-9]+' | head -1 || echo "3000")
fi
echo "   Frontend is on port: $FRONTEND_PORT"

# Test if ports are accessible locally
echo ""
echo "3. Testing local access..."
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "   ✅ Backend responds on localhost:8002"
else
    echo "   ❌ Backend NOT responding"
fi

if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
    echo "   ✅ Frontend responds on localhost:$FRONTEND_PORT"
else
    echo "   ❌ Frontend NOT responding (might still be starting)"
    echo "   Wait 30 seconds and check again"
fi

echo ""
echo "========================================"
echo "   SOLUTION: Access Chatbot"
echo "========================================"
echo ""
echo "📌 On YOUR COMPUTER (Windows/Mac), open a NEW terminal"
echo "   (Not on the server, but on your local computer)"
echo ""
echo "Run this command (use port 8080 to avoid conflicts):"
echo ""
echo "   ssh -L 8080:localhost:$FRONTEND_PORT chatbot@vm-185117"
echo ""
echo "Then wait 5 seconds and open in your browser:"
echo ""
echo "   ✅ http://localhost:8080"
echo "   ✅ http://localhost:8080/admin"
echo ""
echo "========================================"
echo ""
echo "If port 8080 is also busy, try 8081, 9000, etc:"
echo "   ssh -L 8081:localhost:$FRONTEND_PORT chatbot@vm-185117"
echo "   Then open: http://localhost:8081"
echo ""
echo "========================================"
echo "   Debug Info"
echo "========================================"
echo "Frontend Port: $FRONTEND_PORT"
echo "Backend Port: 8002"
echo ""
echo "Check logs:"
echo "  tail -20 backend.log"
echo "  tail -20 frontend.log"
echo ""

