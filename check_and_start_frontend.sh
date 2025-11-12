#!/bin/bash

# Check and Start Frontend
echo "========================================"
echo "   Checking Frontend Status"
echo "========================================"
echo ""

# Check PM2 status
echo "[1/3] Checking PM2 status..."
pm2 status

echo ""
echo "[2/3] Checking if frontend is running..."
if pm2 list | grep -q "chatbot-frontend"; then
    echo "✅ Frontend process found in PM2"
    pm2 logs chatbot-frontend --lines 10 --nostream
else
    echo "❌ Frontend not running in PM2"
    echo ""
    echo "[3/3] Starting frontend..."
    cd ~/chatbot2/frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies..."
        npm install
    fi
    
    # Start with PM2
    pm2 start npm --name chatbot-frontend -- run dev
    pm2 save
    
    echo "✅ Frontend started!"
    echo ""
    echo "Waiting 10 seconds for frontend to start..."
    sleep 10
    
    # Check logs
    pm2 logs chatbot-frontend --lines 15 --nostream
fi

echo ""
echo "========================================"
echo "   Testing Services"
echo "========================================"
echo ""

# Test backend
echo "Testing backend..."
curl -s http://localhost:8002/health && echo " ✅ Backend working" || echo " ❌ Backend not working"

# Test frontend
echo "Testing frontend..."
curl -s http://localhost:3000 > /dev/null && echo " ✅ Frontend working" || echo " ❌ Frontend not working (may need more time to start)"

echo ""
echo "PM2 Status:"
pm2 status



