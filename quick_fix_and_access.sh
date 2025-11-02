#!/bin/bash

echo "========================================"
echo "   Quick Fix & Chatbot Access"
echo "========================================"
echo ""

# Fix git conflict
cd ~/zimmer-chatbot
echo "Fixing git conflicts..."
git stash
git pull origin main
echo "✅ Git updated"
echo ""

# Check if servers are running
echo "Checking servers..."
if pgrep -f "python3 app.py" > /dev/null; then
    echo "✅ Backend is running"
    BACKEND_RUNNING=true
else
    echo "❌ Backend not running"
    BACKEND_RUNNING=false
fi

if pgrep -f "npm run dev" > /dev/null || pgrep -f "next dev" > /dev/null; then
    echo "✅ Frontend is running"
    FRONTEND_RUNNING=true
else
    echo "❌ Frontend not running"
    FRONTEND_RUNNING=false
fi
echo ""

# Get frontend port
FRONTEND_PORT=$(netstat -tuln 2>/dev/null | grep "300" | grep -oP ':\K[0-9]+' | head -1 || echo "3000")

if [ "$BACKEND_RUNNING" = false ] || [ "$FRONTEND_RUNNING" = false ]; then
    echo "Starting servers..."
    chmod +x start_chatbot_server.sh
    ./start_chatbot_server.sh &
    sleep 15
    FRONTEND_PORT=$(netstat -tuln 2>/dev/null | grep "300" | grep -oP ':\K[0-9]+' | head -1 || echo "3000")
fi

echo ""
echo "========================================"
echo "   ✅ ACCESS YOUR CHATBOT NOW"
echo "========================================"
echo ""
echo "📌 On YOUR COMPUTER (not the server), run:"
echo ""
echo "   ssh -L 3000:localhost:$FRONTEND_PORT chatbot@vm-185117"
echo ""
echo "Then open in your browser:"
echo ""
echo "   ✅ http://localhost:3000"
echo "   ✅ http://localhost:3000/admin"
echo ""
echo "Keep the SSH command running while using the chatbot!"
echo ""

