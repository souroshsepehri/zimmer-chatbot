#!/bin/bash

echo "=========================================="
echo "  Fixing Backend - Final Solution"
echo "=========================================="
echo ""

# Step 1: Delete the broken "backend" process
echo "[1/4] Deleting broken 'backend' process..."
pm2 delete backend
sleep 2
echo "✓ Deleted"
echo ""

# Step 2: Clear PM2 cache
echo "[2/4] Clearing PM2 cache..."
rm -f ~/.pm2/dump.pm2
echo "✓ Cache cleared"
echo ""

# Step 3: Navigate to project
echo "[3/4] Navigating to project..."
cd ~/chatbot2 || cd /home/chatbot/chatbot2
echo "✓ Current directory: $(pwd)"
echo ""

# Step 4: Verify files and start correct backend
echo "[4/4] Starting chatbot-backend from ecosystem.config.js..."
if [ ! -f "backend/start_server.py" ]; then
    echo "❌ backend/start_server.py not found!"
    exit 1
fi
if [ ! -f "ecosystem.config.js" ]; then
    echo "❌ ecosystem.config.js not found!"
    exit 1
fi

# Show the config to verify
echo ""
echo "Backend config:"
grep -A 3 "name: 'chatbot-backend'" ecosystem.config.js
echo ""

# Start the backend
pm2 start ecosystem.config.js --only chatbot-backend --update-env
pm2 save

echo ""
echo "=========================================="
echo "  Status Check"
echo "=========================================="
pm2 status
echo ""

echo "Waiting 5 seconds for startup..."
sleep 5

echo ""
echo "=== Backend Logs (last 20 lines) ==="
pm2 logs chatbot-backend --lines 20 --nostream
echo ""

echo "=== Backend Error Logs (if any) ==="
pm2 logs chatbot-backend --err --lines 10 --nostream
echo ""

echo "=========================================="
echo "  Done!"
echo "=========================================="
echo ""
echo "If backend is still errored, check:"
echo "  pm2 describe chatbot-backend"
echo "  pm2 logs chatbot-backend --err"
echo ""

