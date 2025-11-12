#!/bin/bash

echo "========================================"
echo "   Fixing 502 Bad Gateway Error"
echo "========================================"
echo ""

cd ~/chatbot2

# Step 1: Check what's running
echo "[1/5] Checking services..."
echo ""
echo "Backend processes:"
ps aux | grep uvicorn | grep -v grep || echo "  ❌ No backend running"
echo ""
echo "Frontend processes:"
ps aux | grep -E "next dev|npm run dev" | grep -v grep || echo "  ❌ No frontend running"
echo ""

# Step 2: Check ports
echo "[2/5] Checking ports..."
echo ""
if netstat -tuln 2>/dev/null | grep -q ":8001"; then
    echo "✅ Port 8001 is listening (Backend)"
    netstat -tuln 2>/dev/null | grep ":8001"
else
    echo "❌ Port 8001 is NOT listening"
fi
echo ""
if netstat -tuln 2>/dev/null | grep -q ":8000"; then
    echo "✅ Port 8000 is listening (Frontend)"
    netstat -tuln 2>/dev/null | grep ":8000"
else
    echo "❌ Port 8000 is NOT listening"
fi
echo ""

# Step 3: Test backend
echo "[3/5] Testing backend..."
echo ""
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Backend is responding on port 8001"
    curl -s http://localhost:8001/health | head -1
else
    echo "❌ Backend is NOT responding on port 8001"
    echo "   Starting backend..."
    cd backend
    source venv/bin/activate
    nohup uvicorn app:app --host 0.0.0.0 --port 8001 --workers 1 > ../backend.log 2>&1 &
    sleep 5
    cd ..
fi
echo ""

# Step 4: Check frontend logs
echo "[4/5] Checking recent frontend errors..."
echo ""
if [ -f "frontend.log" ]; then
    echo "Last 20 lines of frontend.log:"
    tail -20 frontend.log | grep -i error || echo "  No errors found in last 20 lines"
else
    echo "  No frontend.log found"
fi
echo ""

# Step 5: Restart frontend with correct configuration
echo "[5/5] Restarting frontend..."
echo ""

# Stop old frontend
pkill -f "npm run dev" 2>/dev/null
pkill -f "next dev" 2>/dev/null
pkill -f "node.*next" 2>/dev/null
sleep 3

# Check API configuration
cd frontend
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local with correct API URL..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8001/api" > .env.local
    echo "✅ Created .env.local"
fi

# Clear Next.js cache
echo "Clearing Next.js cache..."
rm -rf .next

# Start frontend
echo "Starting frontend..."
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
cd ..

# Wait for frontend to start
echo "Waiting 10 seconds for frontend to initialize..."
sleep 10

# Test frontend
echo ""
echo "Testing frontend..."
if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ Frontend is responding on port 8000"
else
    echo "⚠️  Frontend may still be starting, check logs: tail -f ~/chatbot2/frontend.log"
fi
echo ""

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo "========================================"
echo "   ✅ Fix Applied!"
echo "========================================"
echo ""
echo "📍 Your Chatbot URLs:"
echo ""
echo "  Frontend:  http://193.162.129.249:8000"
echo "  Admin:     http://193.162.129.249:8000/admin"
echo "  Backend:   http://193.162.129.249:8001"
echo "  API Docs:  http://193.162.129.249:8001/docs"
echo ""
echo "📋 Check logs if still not working:"
echo "  tail -f ~/chatbot2/backend.log"
echo "  tail -f ~/chatbot2/frontend.log"
echo ""
echo "🔍 Verify services:"
echo "  ps aux | grep uvicorn"
echo "  ps aux | grep 'npm run dev'"
echo ""

