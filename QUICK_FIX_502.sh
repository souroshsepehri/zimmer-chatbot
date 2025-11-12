#!/bin/bash

echo "========================================"
echo "   Quick Fix for 502 Error"
echo "========================================"
echo ""

cd ~/chatbot2

# Step 1: Check what's running
echo "[1/5] Checking current processes..."
echo ""
echo "Backend processes:"
ps aux | grep uvicorn | grep -v grep || echo "  ❌ No backend running"
echo ""
echo "Frontend processes:"
ps aux | grep -E "next|npm run dev" | grep -v grep || echo "  ❌ No frontend running"
echo ""

# Step 2: Check ports
echo "[2/5] Checking ports..."
if netstat -tuln 2>/dev/null | grep -q ":8001"; then
    echo "  ✅ Port 8001 (backend) is in use"
else
    echo "  ❌ Port 8001 (backend) is NOT in use"
fi

if netstat -tuln 2>/dev/null | grep -q ":8000"; then
    echo "  ✅ Port 8000 (frontend) is in use"
else
    echo "  ❌ Port 8000 (frontend) is NOT in use"
fi
echo ""

# Step 3: Stop everything
echo "[3/5] Stopping all existing processes..."
pkill -f uvicorn 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
pkill -f "next dev" 2>/dev/null
sleep 3
echo "  ✅ All processes stopped"
echo ""

# Step 4: Start Backend
echo "[4/5] Starting Backend on port 8001..."
cd backend

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "  Installing dependencies..."
    pip install -r requirements.txt > /dev/null 2>&1
fi

# Create directories
mkdir -p vectorstore logs __pycache__

# Start backend
nohup uvicorn app:app --host 0.0.0.0 --port 8001 --workers 1 > ../backend.log 2>&1 &
BACKEND_PID=$!
sleep 5

# Check if backend started
if ps -p $BACKEND_PID > /dev/null; then
    echo "  ✅ Backend started (PID: $BACKEND_PID)"
else
    echo "  ❌ Backend failed to start. Check backend.log"
    tail -20 ../backend.log
    exit 1
fi

# Test backend
if curl -s http://localhost:8001/health > /dev/null 2>&1; then
    echo "  ✅ Backend is responding"
else
    echo "  ⚠️  Backend started but not responding yet"
fi
echo ""

# Step 5: Start Frontend
echo "[5/5] Starting Frontend on port 8000..."
cd ../frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "  Installing npm dependencies (this may take a minute)..."
    npm install
fi

# Clear Next.js cache
rm -rf .next

# Start frontend
nohup npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
sleep 10

# Check if frontend started
if ps -p $FRONTEND_PID > /dev/null; then
    echo "  ✅ Frontend started (PID: $FRONTEND_PID)"
else
    echo "  ❌ Frontend failed to start. Check frontend.log"
    tail -20 ../frontend.log
    exit 1
fi

# Test frontend
if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "  ✅ Frontend is responding"
else
    echo "  ⚠️  Frontend started but not responding yet (may need more time)"
fi
echo ""

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Unknown")

echo "========================================"
echo "   ✅ Services Started!"
echo "========================================"
echo ""
echo "📍 Access URLs:"
echo ""
echo "  From Server:"
echo "    Frontend: http://localhost:8000"
echo "    Backend:  http://localhost:8001/health"
echo ""
echo "  From Your Computer:"
echo "    Frontend: http://$SERVER_IP:8000"
echo "    Backend:  http://$SERVER_IP:8001"
echo "    API Docs: http://$SERVER_IP:8001/docs"
echo ""
if [ "$EXTERNAL_IP" != "Unknown" ]; then
    echo "  External IP:"
    echo "    Frontend: http://$EXTERNAL_IP:8000"
    echo "    Backend:  http://$EXTERNAL_IP:8001"
fi
echo ""
echo "📊 Process IDs:"
echo "    Backend PID:  $BACKEND_PID"
echo "    Frontend PID: $FRONTEND_PID"
echo ""
echo "📝 View Logs:"
echo "    tail -f ~/chatbot2/backend.log"
echo "    tail -f ~/chatbot2/frontend.log"
echo ""
echo "🛑 To Stop:"
echo "    kill $BACKEND_PID $FRONTEND_PID"
echo ""

