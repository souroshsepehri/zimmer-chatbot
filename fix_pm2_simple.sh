#!/bin/bash

echo "=========================================="
echo "  Quick Fix for PM2 Frontend Issue"
echo "=========================================="
echo ""

# Step 1: Stop and delete the problematic process
echo "[1/3] Stopping chatbot-frontend..."
pm2 stop chatbot-frontend 2>/dev/null
pm2 delete chatbot-frontend 2>/dev/null
sleep 2
echo "✓ Done"
echo ""

# Step 2: Kill any process on port 3000
echo "[2/3] Freeing port 3000..."
# Try multiple methods to find and kill the process
if command -v lsof &> /dev/null; then
    PID=$(lsof -ti:3000 2>/dev/null)
    if [ ! -z "$PID" ]; then
        kill -9 $PID 2>/dev/null
        echo "✓ Killed process $PID on port 3000"
    else
        echo "✓ Port 3000 is free"
    fi
elif command -v fuser &> /dev/null; then
    PID=$(fuser 3000/tcp 2>/dev/null | awk '{print $NF}')
    if [ ! -z "$PID" ]; then
        kill -9 $PID 2>/dev/null
        echo "✓ Killed process on port 3000"
    else
        echo "✓ Port 3000 is free"
    fi
else
    echo "⚠ Could not check port 3000 (lsof/fuser not available)"
    echo "  Please manually check: netstat -tlnp | grep 3000"
fi
sleep 2
echo ""

# Step 3: Restart with updated config
echo "[3/3] Restarting with correct configuration..."
pm2 start ecosystem.config.js --only chatbot-frontend --env production --update-env
pm2 save
echo ""
echo "=========================================="
echo "  Status"
echo "=========================================="
pm2 status chatbot-frontend
echo ""
echo "Waiting 3 seconds to verify startup..."
sleep 3
echo ""
pm2 logs chatbot-frontend --lines 5 --nostream
echo ""
echo "=========================================="
echo "  Done!"
echo "=========================================="
echo ""
echo "If you see errors, check:"
echo "  pm2 logs chatbot-frontend"
echo ""

