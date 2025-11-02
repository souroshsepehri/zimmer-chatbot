#!/bin/bash

echo "========================================"
echo "   Ngrok Tunnel Solution"
echo "========================================"
echo ""

# Get frontend port
FRONTEND_PORT=$(netstat -tuln | grep "300" | grep -oP ':\K[0-9]+' | head -1 || echo "3000")

echo "Installing ngrok..."
# Download ngrok
if ! command -v ngrok > /dev/null; then
    wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
    tar xvzf ngrok-v3-stable-linux-amd64.tgz
    sudo mv ngrok /usr/local/bin/
    rm ngrok-v3-stable-linux-amd64.tgz
    echo "✅ ngrok installed"
else
    echo "✅ ngrok already installed"
fi

echo ""
echo "Starting ngrok tunnels..."
echo ""

# Start ngrok for frontend
echo "Frontend tunnel (port $FRONTEND_PORT):"
ngrok http $FRONTEND_PORT > /tmp/ngrok_frontend.log 2>&1 &
NGROK_FRONTEND_PID=$!

# Start ngrok for backend
echo "Backend tunnel (port 8002):"
ngrok http 8002 > /tmp/ngrok_backend.log 2>&1 &
NGROK_BACKEND_PID=$!

sleep 5

# Get ngrok URLs
FRONTEND_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*' | head -1 | cut -d'"' -f4 || echo "Starting...")
BACKEND_URL=$(curl -s http://localhost:4041/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*' | head -1 | cut -d'"' -f4 || echo "Starting...")

echo ""
echo "========================================"
echo "✅ Ngrok Tunnels Active!"
echo "========================================"
echo ""
echo "Frontend: $FRONTEND_URL"
echo "Backend:  $BACKEND_URL"
echo "Admin:    $FRONTEND_URL/admin"
echo ""
echo "These URLs work from anywhere - no firewall changes needed!"
echo ""
echo "To stop: kill $NGROK_FRONTEND_PID $NGROK_BACKEND_PID"
echo ""

