#!/bin/bash

echo "Checking servers..."
sleep 2

# Get frontend port
FRONTEND_PORT=$(netstat -tuln | grep "300" | grep -oP ':\K[0-9]+' | head -1 || echo "3000")

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "")

echo ""
echo "========================================"
echo "   Chatbot is Ready!"
echo "========================================"
echo ""
echo "Open this URL in your browser:"
echo ""
if [ ! -z "$EXTERNAL_IP" ]; then
    echo "  🌐 http://$EXTERNAL_IP:$FRONTEND_PORT"
else
    echo "  🌐 http://$SERVER_IP:$FRONTEND_PORT"
fi
echo ""
echo "Or if using SSH tunnel:"
echo "  🌐 http://localhost:$FRONTEND_PORT"
echo ""
echo "========================================"
echo ""

