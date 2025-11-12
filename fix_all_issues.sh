#!/bin/bash

echo "========================================"
echo "   Fixing All Issues"
echo "========================================"
echo ""

cd ~/chatbot2

# Step 1: Stop ALL processes
echo "[1/5] Stopping all services..."
pkill -f uvicorn
pkill -f "npm run dev"
pkill -f "next dev"
pkill -f "node.*next"
pkill -f "node.*3000"
sleep 3
echo "✅ All processes stopped"
echo ""

# Step 2: Kill processes on ports
echo "[2/5] Clearing ports..."
for port in 3000 8000 8001; do
    if lsof -ti:$port > /dev/null 2>&1; then
        echo "Killing process on port $port..."
        kill -9 $(lsof -ti:$port) 2>/dev/null
    fi
done
sleep 2
echo "✅ Ports cleared"
echo ""

# Step 3: Start Backend (only on 8001)
echo "[3/5] Starting Backend on port 8001..."
cd backend
source venv/bin/activate
mkdir -p vectorstore logs __pycache__

# Start backend
nohup uvicorn app:app --host 0.0.0.0 --port 8001 --workers 1 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
cd ..

# Wait for backend
sleep 5

# Test backend
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Backend is responding!"
else
    echo "⚠️  Backend may not be ready, check: tail -f ~/chatbot2/backend.log"
fi
echo ""

# Step 4: Configure Frontend
echo "[4/5] Configuring Frontend..."
cd frontend

# Create .env.local with correct API URL
echo "NEXT_PUBLIC_API_URL=http://localhost:8001/api" > .env.local
echo "✅ Created .env.local"

# Clear Next.js cache
rm -rf .next
echo "✅ Cleared Next.js cache"

# Verify package.json has correct port
if grep -q '"dev": "next dev -H 0.0.0.0 -p 8000"' package.json; then
    echo "✅ Frontend configured for port 8000"
else
    echo "⚠️  Warning: Frontend port may not be 8000 in package.json"
fi
echo ""

# Step 5: Start Frontend
echo "[5/5] Starting Frontend on port 8000..."
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
cd ..

# Wait for frontend
echo "Waiting 15 seconds for frontend to initialize..."
sleep 15

# Test frontend
echo ""
echo "Testing services..."
if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ Frontend is responding on port 8000!"
else
    echo "⚠️  Frontend may still be starting..."
    echo "   Check logs: tail -f ~/chatbot2/frontend.log"
fi

if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "✅ Backend is responding on port 8001!"
else
    echo "❌ Backend is NOT responding"
fi
echo ""

# Show status
echo "========================================"
echo "   Status Check"
echo "========================================"
echo ""
echo "Backend processes:"
ps aux | grep uvicorn | grep -v grep || echo "  ❌ No backend running"
echo ""
echo "Frontend processes:"
ps aux | grep -E "next dev|npm run dev" | grep -v grep || echo "  ❌ No frontend running"
echo ""
echo "Ports listening:"
netstat -tuln 2>/dev/null | grep -E ":8000|:8001" || echo "  No ports listening"
echo ""

# Show URLs
echo "========================================"
echo "   ✅ Your Chatbot URLs"
echo "========================================"
echo ""
echo "  Frontend:  http://193.162.129.249:8000"
echo "  Admin:     http://193.162.129.249:8000/admin"
echo "  Backend:   http://193.162.129.249:8001"
echo "  API Docs:  http://193.162.129.249:8001/docs"
echo ""
echo "📋 If still not working, check logs:"
echo "  tail -f ~/chatbot2/backend.log"
echo "  tail -f ~/chatbot2/frontend.log"
echo ""

