#!/bin/bash

echo "=========================================="
echo "  FIXING BACKEND - Complete Reset"
echo "=========================================="

# Step 1: Delete ALL PM2 processes and clear cache
echo "[1/5] Deleting all PM2 processes..."
pm2 delete all 2>/dev/null
pm2 kill 2>/dev/null
sleep 2

# Step 2: Remove PM2 dump file (clears saved processes)
echo "[2/5] Clearing PM2 saved processes..."
rm -f ~/.pm2/dump.pm2
sleep 1

# Step 3: Navigate to project
echo "[3/5] Navigating to project..."
cd ~/chatbot2 || cd /home/chatbot/chatbot2
echo "Current directory: $(pwd)"

# Step 4: Verify files exist
echo "[4/5] Verifying files..."
if [ ! -f "backend/start_server.py" ]; then
    echo "❌ backend/start_server.py not found!"
    exit 1
fi
if [ ! -f "backend/app.py" ]; then
    echo "❌ backend/app.py not found!"
    exit 1
fi
if [ ! -f "ecosystem.config.js" ]; then
    echo "❌ ecosystem.config.js not found!"
    exit 1
fi
echo "✓ All files found"

# Show the backend config
echo ""
echo "Backend config:"
grep -A 3 "name: 'chatbot-backend'" ecosystem.config.js | head -5
echo ""

# Step 5: Start PM2 fresh
echo "[5/5] Starting PM2 with fresh config..."
pm2 start ecosystem.config.js --only chatbot-backend --update-env
pm2 save

echo ""
echo "=========================================="
echo "  Status"
echo "=========================================="
pm2 status

echo ""
echo "Waiting 5 seconds for startup..."
sleep 5

echo ""
echo "=== Backend Logs (last 20 lines) ==="
pm2 logs chatbot-backend --lines 20 --nostream

echo ""
echo "=========================================="
echo "  Done!"
echo "=========================================="
echo ""
echo "If you see errors, check:"
echo "  pm2 logs chatbot-backend --err"
echo "  pm2 describe chatbot-backend"
echo ""

