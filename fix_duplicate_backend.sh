#!/bin/bash

echo "========================================"
echo "   Fixing Duplicate Backend Processes"
echo "========================================"
echo ""

# Stop the old backend on port 8000
echo "Stopping old backend on port 8000..."
kill 1716165 2>/dev/null
sleep 2

# Check if it's still running
if ps -p 1716165 > /dev/null 2>&1; then
    echo "Force killing old backend..."
    kill -9 1716165 2>/dev/null
fi

# Verify only one backend is running
echo ""
echo "Checking backend processes..."
ps aux | grep uvicorn | grep -v grep

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Unable to detect")

echo ""
echo "========================================"
echo "   ✅ Fixed! Use These URLs:"
echo "========================================"
echo ""
if [ "$EXTERNAL_IP" != "Unable to detect" ]; then
    echo "📍 From Your Computer:"
    echo ""
    echo "  Frontend:  http://$EXTERNAL_IP:8000"
    echo "  Admin:     http://$EXTERNAL_IP:8000/admin"
    echo "  Backend:   http://$EXTERNAL_IP:8001"
    echo "  API Docs:  http://$EXTERNAL_IP:8001/docs"
    echo ""
    echo "  👉 Copy this URL: http://$EXTERNAL_IP:8000"
else
    echo "📍 Use Local IP:"
    echo ""
    echo "  Frontend:  http://$SERVER_IP:8000"
    echo "  Admin:     http://$SERVER_IP:8000/admin"
    echo ""
    echo "  👉 Copy this URL: http://$SERVER_IP:8000"
fi
echo ""

