#!/bin/bash

echo "=========================================="
echo "  Checking Backend Error"
echo "=========================================="
echo ""

# Check backend error logs
echo "=== Backend Error Logs ==="
pm2 logs backend --err --lines 30 --nostream
echo ""

# Check backend output logs
echo "=== Backend Output Logs ==="
pm2 logs backend --out --lines 20 --nostream
echo ""

# Check what command it's trying to run
echo "=== Backend Process Info ==="
pm2 describe backend
echo ""

echo "=========================================="
echo "  Fixing Backend"
echo "=========================================="

# Delete the old "backend" process
echo "Deleting old 'backend' process..."
pm2 delete backend

# Clear PM2 cache
rm -f ~/.pm2/dump.pm2

# Navigate to project
cd ~/chatbot2

# Start the correct backend from ecosystem.config.js
echo "Starting chatbot-backend from ecosystem.config.js..."
pm2 start ecosystem.config.js --only chatbot-backend --update-env

# Wait
sleep 5

# Check status
echo ""
echo "=== Status ==="
pm2 status

# Check logs
echo ""
echo "=== New Backend Logs ==="
pm2 logs chatbot-backend --lines 20 --nostream

