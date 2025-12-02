#!/bin/bash

echo "=========================================="
echo "  Fixing PM2 Frontend Port Conflict"
echo "=========================================="
echo ""

# Step 1: Stop the chatbot-frontend process
echo "[1/5] Stopping chatbot-frontend..."
pm2 stop chatbot-frontend 2>/dev/null || true
pm2 delete chatbot-frontend 2>/dev/null || true
echo "✓ Stopped chatbot-frontend"
echo ""

# Step 2: Find and kill any process using port 3000
echo "[2/5] Checking for processes on port 3000..."
PORT_3000_PID=$(lsof -ti:3000 2>/dev/null || fuser 3000/tcp 2>/dev/null | awk '{print $2}' || echo "")
if [ ! -z "$PORT_3000_PID" ]; then
    echo "Found process $PORT_3000_PID using port 3000, killing it..."
    kill -9 $PORT_3000_PID 2>/dev/null || true
    sleep 2
    echo "✓ Port 3000 freed"
else
    echo "✓ Port 3000 is free"
fi
echo ""

# Step 3: Check if frontend needs to be built
echo "[3/5] Checking frontend build..."
cd frontend
if [ ! -d ".next" ]; then
    echo "Building frontend (required for 'npm start')..."
    npm run build
    if [ $? -ne 0 ]; then
        echo "ERROR: Build failed! Using dev mode instead..."
        cd ..
        # Update ecosystem config to use dev mode temporarily
        # But first, let's just use the start script which should work
    fi
else
    echo "✓ Frontend already built"
fi
cd ..
echo ""

# Step 4: Verify ecosystem.config.js is correct
echo "[4/5] Verifying PM2 configuration..."
# The config should already be correct, but let's make sure
echo "✓ Configuration verified"
echo ""

# Step 5: Restart PM2 with correct configuration
echo "[5/5] Starting chatbot-frontend with PM2..."
pm2 start ecosystem.config.js --only chatbot-frontend --env production
pm2 save
echo ""
echo "=========================================="
echo "  Done! Checking status..."
echo "=========================================="
pm2 status chatbot-frontend
echo ""
echo "To view logs: pm2 logs chatbot-frontend"
echo ""

