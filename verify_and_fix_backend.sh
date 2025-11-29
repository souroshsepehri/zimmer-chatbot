#!/bin/bash

echo "=========================================="
echo "  Verifying and Fixing Backend"
echo "=========================================="
echo ""

# Navigate to project
cd ~/chatbot2 || cd /home/chatbot/chatbot2
echo "Current directory: $(pwd)"
echo ""

# Check if files exist
echo "=== Checking Files ==="
if [ -f "backend/start_server.py" ]; then
    echo "✓ backend/start_server.py exists"
else
    echo "❌ backend/start_server.py NOT FOUND"
fi

if [ -f "backend/main.py" ]; then
    echo "✓ backend/main.py exists"
else
    echo "❌ backend/main.py NOT FOUND"
fi

if [ -f "ecosystem.config.js" ]; then
    echo "✓ ecosystem.config.js exists"
    echo ""
    echo "=== Backend Config in ecosystem.config.js ==="
    grep -A 10 "name: 'chatbot-backend'" ecosystem.config.js
else
    echo "❌ ecosystem.config.js NOT FOUND"
    exit 1
fi
echo ""

# Check if Python3 and uvicorn are available
echo "=== Checking Python Environment ==="
which python3 && echo "✓ python3 found" || echo "❌ python3 not found"
python3 -m uvicorn --help > /dev/null 2>&1 && echo "✓ uvicorn module available" || echo "❌ uvicorn module not available"
echo ""

# Try to start backend with explicit command
echo "=== Starting Backend with Explicit Command ==="
pm2 delete chatbot-backend 2>/dev/null
pm2 delete backend 2>/dev/null

# Start backend using uvicorn directly
cd backend
pm2 start "python3 -m uvicorn main:app --host 0.0.0.0 --port 8001" --name chatbot-backend --interpreter bash
cd ..

pm2 save

echo ""
echo "=== Status ==="
pm2 status

sleep 3

echo ""
echo "=== Logs ==="
pm2 logs chatbot-backend --lines 15 --nostream

