#!/bin/bash

# Fix Frontend - Install Dependencies and Restart
echo "========================================"
echo "   Fixing Frontend"
echo "========================================"
echo ""

# Stop frontend
echo "[1/4] Stopping frontend..."
pm2 stop chatbot-frontend 2>/dev/null
pm2 delete chatbot-frontend 2>/dev/null

# Navigate to frontend
cd ~/chatbot2/frontend

# Remove node_modules if exists (fresh install)
if [ -d "node_modules" ]; then
    echo "[2/4] Removing old node_modules..."
    rm -rf node_modules
fi

# Install dependencies
echo "[3/4] Installing frontend dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Error: npm install failed!"
    exit 1
fi

echo "✅ Dependencies installed"

# Start frontend
echo "[4/4] Starting frontend with PM2..."
pm2 start npm --name chatbot-frontend -- run dev

# Save PM2 config
pm2 save

# Wait for frontend to start
echo ""
echo "Waiting 15 seconds for Next.js to start..."
sleep 15

# Check status
echo ""
echo "PM2 Status:"
pm2 status

# Check logs
echo ""
echo "Frontend logs:"
pm2 logs chatbot-frontend --lines 10 --nostream

# Test
echo ""
echo "Testing frontend..."
curl -s http://localhost:3000 > /dev/null && echo "✅ Frontend is working!" || echo "⏳ Frontend is still starting (may need more time)"


