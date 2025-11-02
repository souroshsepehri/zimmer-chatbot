#!/bin/bash

# Simple script to open chatbot in browser

# Get frontend port
FRONTEND_PORT=$(netstat -tuln 2>/dev/null | grep "300" | grep -oP ':\K[0-9]+' | head -1 || echo "3000")
SERVER_IP=$(hostname -I | awk '{print $1}')

echo "Opening chatbot..."
echo "Frontend Port: $FRONTEND_PORT"

# Check if servers are running
if ! pgrep -f "python3 app.py" > /dev/null; then
    echo "❌ Backend is not running!"
    exit 1
fi

if ! pgrep -f "npm run dev" > /dev/null && ! pgrep -f "next dev" > /dev/null; then
    echo "❌ Frontend is not running!"
    exit 1
fi

# Try to open browser
if command -v xdg-open > /dev/null; then
    xdg-open "http://localhost:$FRONTEND_PORT"
elif command -v gnome-open > /dev/null; then
    gnome-open "http://localhost:$FRONTEND_PORT"
else
    echo ""
    echo "========================================"
    echo "   Chatbot is Ready!"
    echo "========================================"
    echo ""
    echo "Open this URL in your browser:"
    echo ""
    echo "  http://localhost:$FRONTEND_PORT"
    echo ""
    echo "Or from external network:"
    echo "  http://$SERVER_IP:$FRONTEND_PORT"
    echo ""
fi
