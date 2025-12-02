#!/bin/bash

echo "=========================================="
echo "  Fixing Backend PM2 Configuration"
echo "=========================================="
echo ""

# Step 1: Delete ALL old processes
echo "[1/4] Deleting all PM2 processes..."
pm2 delete all
sleep 2
echo "✓ All processes deleted"
echo ""

# Step 2: Navigate to project
echo "[2/4] Navigating to project directory..."
cd ~/chatbot2 || cd /home/chatbot/chatbot2
echo "✓ Current directory: $(pwd)"
echo ""

# Step 3: Verify app.py exists
echo "[3/4] Verifying backend files..."
if [ -f "backend/app.py" ]; then
    echo "✓ backend/app.py exists"
else
    echo "❌ backend/app.py not found!"
    exit 1
fi

if [ -f "ecosystem.config.js" ]; then
    echo "✓ ecosystem.config.js exists"
    # Show the backend config
    echo ""
    echo "Backend config in ecosystem.config.js:"
    grep -A 15 "name: 'chatbot-backend'" ecosystem.config.js | head -10
else
    echo "❌ ecosystem.config.js not found!"
    exit 1
fi
echo ""

# Step 4: Start with correct config
echo "[4/4] Starting PM2 with correct configuration..."
pm2 start ecosystem.config.js --env production --update-env
pm2 save
echo ""

echo "=========================================="
echo "  Status Check"
echo "=========================================="
pm2 status
echo ""

echo "Waiting 3 seconds..."
sleep 3

echo "=== Backend Logs ==="
pm2 logs chatbot-backend --lines 10 --nostream
echo ""

echo "=== Frontend Logs ==="
pm2 logs chatbot-frontend --lines 5 --nostream
echo ""

echo "=========================================="
echo "  Done!"
echo "=========================================="

