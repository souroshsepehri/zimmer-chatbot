#!/bin/bash

echo "========================================"
echo "   Your Chatbot Access"
echo "========================================"
echo ""

# Check if servers are running
if ! pgrep -f "python3 app.py" > /dev/null; then
    echo "❌ Backend is NOT running"
    echo "Run: cd ~/zimmer-chatbot && ./start_chatbot_server.sh"
    exit 1
fi

if ! pgrep -f "npm run dev" > /dev/null && ! pgrep -f "next dev" > /dev/null; then
    echo "❌ Frontend is NOT running"
    echo "Run: cd ~/zimmer-chatbot && ./start_chatbot_server.sh"
    exit 1
fi

# Get frontend port
FRONTEND_PORT=$(netstat -tuln 2>/dev/null | grep "300" | grep -oP ':\K[0-9]+' | head -1 || echo "3000")

echo "✅ Backend is running (port 8002)"
echo "✅ Frontend is running (port $FRONTEND_PORT)"
echo ""

echo "========================================"
echo "   HOW TO SEE YOUR CHATBOT"
echo "========================================"
echo ""
echo "On YOUR COMPUTER (Windows), open PowerShell/CMD"
echo "and run this EXACT command:"
echo ""
echo "   ssh -L 8080:localhost:$FRONTEND_PORT chatbot@vm-185117"
echo ""
echo "Then open in your browser:"
echo ""
echo "   🌐 http://localhost:8080"
echo "   🔧 http://localhost:8080/admin"
echo ""
echo "========================================"
echo ""

