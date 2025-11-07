#!/bin/bash

# Fix PM2 Setup Script
echo "========================================"
echo "   Fixing PM2 Setup"
echo "========================================"
echo ""

# Stop all PM2 processes
echo "[1/4] Stopping all PM2 processes..."
pm2 stop all
pm2 delete all

# Navigate to backend
cd ~/chatbot2/backend
source venv/bin/activate

# Get full path to Python interpreter
PYTHON_PATH=$(which python3)
echo "Using Python: $PYTHON_PATH"
echo ""

# Start with PM2 using full path
echo "[2/4] Starting chatbot with PM2..."
pm2 start uvicorn --name chatbot-backend --interpreter python3 -- app:app --host 0.0.0.0 --port 8002

# Wait a moment
sleep 2

# Check status
echo ""
echo "[3/4] Checking PM2 status..."
pm2 status

# Save PM2 configuration
echo ""
echo "[4/4] Saving PM2 configuration..."
pm2 save

echo ""
echo "========================================"
echo "   PM2 Setup Complete!"
echo "========================================"
echo ""
echo "PM2 Status:"
pm2 status
echo ""
echo "View logs:"
echo "  pm2 logs chatbot-backend"
echo ""
echo "To set up auto-start on boot, run:"
echo "  sudo env PATH=\$PATH:/usr/bin /usr/local/lib/node_modules/pm2/bin/pm2 startup systemd -u chatbot --hp /home/chatbot"
echo ""

