#!/bin/bash

echo "=========================================="
echo "  Complete PM2 Fix for Backend & Frontend"
echo "=========================================="
echo ""

# Step 1: Stop and delete all PM2 processes
echo "[1/6] Stopping all PM2 processes..."
pm2 stop all 2>/dev/null
pm2 delete all 2>/dev/null
sleep 2
echo "✓ All processes stopped"
echo ""

# Step 2: Kill any processes on ports 3000, 8000, 8001
echo "[2/6] Freeing ports 3000, 8000, 8001..."
for port in 3000 8000 8001; do
    if command -v lsof &> /dev/null; then
        PID=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$PID" ]; then
            kill -9 $PID 2>/dev/null
            echo "  ✓ Freed port $port (killed PID $PID)"
        fi
    elif command -v fuser &> /dev/null; then
        fuser -k $port/tcp 2>/dev/null && echo "  ✓ Freed port $port"
    fi
done
sleep 2
echo ""

# Step 3: Navigate to project directory
echo "[3/6] Navigating to project directory..."
cd ~/chatbot2 || cd /home/chatbot/chatbot2 || {
    echo "❌ Cannot find project directory. Please run this from the project root."
    exit 1
}
echo "✓ Current directory: $(pwd)"
echo ""

# Step 4: Verify frontend package.json has correct port
echo "[4/6] Verifying frontend configuration..."
if [ -f "frontend/package.json" ]; then
    # Check if port is 8000 in dev script
    if grep -q '"dev": "next dev -H 0.0.0.0 -p 8000"' frontend/package.json; then
        echo "✓ Frontend package.json has correct port (8000)"
    else
        echo "⚠ Frontend package.json may have wrong port. Updating..."
        # This is a backup - the file should already be correct
        sed -i 's/"dev": "next dev -H 0.0.0.0 -p [0-9]*"/"dev": "next dev -H 0.0.0.0 -p 8000"/' frontend/package.json
        echo "✓ Updated frontend package.json"
    fi
else
    echo "⚠ frontend/package.json not found"
fi
echo ""

# Step 5: Verify ecosystem.config.js
echo "[5/6] Verifying ecosystem.config.js..."
if [ -f "ecosystem.config.js" ]; then
    if grep -q "backend/start_server.py" ecosystem.config.js; then
        echo "✓ Backend script path is correct"
    else
        echo "⚠ Backend script path may be incorrect"
    fi
    if grep -q '"PORT": 8001' ecosystem.config.js; then
        echo "✓ Backend port is 8001"
    else
        echo "⚠ Backend port may be incorrect"
    fi
    if grep -q '"PORT": 8000' ecosystem.config.js; then
        echo "✓ Frontend port is 8000"
    else
        echo "⚠ Frontend port may be incorrect"
    fi
else
    echo "❌ ecosystem.config.js not found!"
    exit 1
fi
echo ""

# Step 6: Start PM2 with correct configuration
echo "[6/6] Starting PM2 with correct configuration..."
pm2 start ecosystem.config.js --env production --update-env
pm2 save
echo ""
echo "=========================================="
echo "  Status Check"
echo "=========================================="
pm2 status
echo ""
echo "Waiting 5 seconds for processes to start..."
sleep 5
echo ""
echo "=== Backend Logs (last 10 lines) ==="
pm2 logs chatbot-backend --lines 10 --nostream
echo ""
echo "=== Frontend Logs (last 10 lines) ==="
pm2 logs chatbot-frontend --lines 10 --nostream
echo ""
echo "=========================================="
echo "  Verification"
echo "=========================================="
echo "Checking ports..."
lsof -i:8001 2>/dev/null | grep -q LISTEN && echo "✓ Port 8001 (backend) is listening" || echo "⚠ Port 8001 not listening"
lsof -i:8000 2>/dev/null | grep -q LISTEN && echo "✓ Port 8000 (frontend) is listening" || echo "⚠ Port 8000 not listening"
lsof -i:3000 2>/dev/null | grep -q LISTEN && echo "⚠ Port 3000 is still in use!" || echo "✓ Port 3000 is free"
echo ""
echo "=========================================="
echo "  Done!"
echo "=========================================="
echo ""
echo "To monitor:"
echo "  pm2 status"
echo "  pm2 logs"
echo "  pm2 logs chatbot-backend"
echo "  pm2 logs chatbot-frontend"
echo ""

