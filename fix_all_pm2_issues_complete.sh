#!/bin/bash

echo "=========================================="
echo "  Complete PM2 Fix - Backend & Frontend"
echo "=========================================="
echo ""

# Step 1: Check current status
echo "[1/7] Current PM2 Status:"
pm2 status
echo ""

# Step 2: Check backend errors
echo "[2/7] Backend Error Logs:"
pm2 logs backend --err --lines 10 --nostream 2>/dev/null || pm2 logs chatbot-backend --err --lines 10 --nostream 2>/dev/null || echo "No backend error logs found"
echo ""

# Step 3: Check frontend errors
echo "[3/7] Frontend Error Logs:"
pm2 logs frontend --err --lines 10 --nostream 2>/dev/null || pm2 logs chatbot-frontend --err --lines 10 --nostream 2>/dev/null || echo "No frontend error logs found"
echo ""

# Step 4: Delete ALL processes
echo "[4/7] Deleting all PM2 processes..."
pm2 delete all 2>/dev/null
pm2 kill 2>/dev/null
sleep 2
rm -f ~/.pm2/dump.pm2
echo "✓ All processes deleted and cache cleared"
echo ""

# Step 5: Navigate to project
echo "[5/7] Navigating to project..."
cd ~/chatbot2 || cd /home/chatbot/chatbot2
echo "✓ Current directory: $(pwd)"
echo ""

# Step 6: Verify files exist
echo "[6/7] Verifying required files..."
if [ ! -f "backend/main.py" ]; then
    echo "❌ backend/main.py not found!"
    exit 1
fi
if [ ! -f "frontend/package.json" ]; then
    echo "❌ frontend/package.json not found!"
    exit 1
fi
echo "✓ All required files found"
echo ""

# Step 7: Start backend directly (bypassing ecosystem.config.js issues)
echo "[7/7] Starting backend and frontend..."
echo ""

# Start backend with explicit command
cd backend
pm2 start "python3 -m uvicorn main:app --host 0.0.0.0 --port 8001" \
  --name chatbot-backend \
  --interpreter bash \
  --env PORT=8001 \
  --env HOST=0.0.0.0 \
  --error ../logs/backend-error.log \
  --output ../logs/backend-out.log \
  --max-memory-restart 1G \
  --autorestart \
  --restart-delay 4000
cd ..

# Start frontend
cd frontend
pm2 start "npm run dev" \
  --name chatbot-frontend \
  --interpreter bash \
  --env PORT=8000 \
  --env NEXT_PUBLIC_API_URL=http://localhost:8001/api \
  --error ../logs/frontend-error.log \
  --output ../logs/frontend-out.log \
  --max-memory-restart 512M \
  --autorestart \
  --restart-delay 4000
cd ..

# Save PM2 configuration
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
echo "=== Backend Logs (last 15 lines) ==="
pm2 logs chatbot-backend --lines 15 --nostream
echo ""

echo "=== Frontend Logs (last 15 lines) ==="
pm2 logs chatbot-frontend --lines 15 --nostream
echo ""

echo "=== Backend Errors (if any) ==="
pm2 logs chatbot-backend --err --lines 5 --nostream
echo ""

echo "=== Frontend Errors (if any) ==="
pm2 logs chatbot-frontend --err --lines 5 --nostream
echo ""

echo "=========================================="
echo "  Port Check"
echo "=========================================="
lsof -i:8001 2>/dev/null | grep LISTEN && echo "✓ Backend (port 8001) is listening" || echo "⚠ Backend (port 8001) not listening"
lsof -i:8000 2>/dev/null | grep LISTEN && echo "✓ Frontend (port 8000) is listening" || echo "⚠ Frontend (port 8000) not listening"
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

