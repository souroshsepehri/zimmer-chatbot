#!/bin/bash

# Script to start the chatbot server on Linux
echo "========================================"
echo "   Starting Chatbot Server (Linux)"
echo "========================================"
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Current directory: $(pwd)"
echo ""

# Stop existing servers first
echo "[0/3] Stopping existing servers..."
pkill -f "python3 app.py" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
pkill -f "next dev" 2>/dev/null

# Force kill processes on ports
if lsof -ti:8002 > /dev/null 2>&1; then
    kill -9 $(lsof -ti:8002) 2>/dev/null 2>/dev/null
fi

for port in 3000 3001 3002 3003; do
    if lsof -ti:$port > /dev/null 2>&1; then
        kill -9 $(lsof -ti:$port) 2>/dev/null 2>/dev/null
    fi
done

sleep 2
echo "✅ Old processes stopped"
echo ""

# Step 1: Check and install frontend dependencies
echo "[1/3] Checking Frontend Dependencies..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing npm dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "ERROR: npm install failed!"
        exit 1
    fi
else
    echo "Frontend dependencies found."
fi

cd ..

# Step 2: Start Backend Server
echo ""
echo "[2/3] Starting Backend Server..."
cd backend
source venv/bin/activate 2>/dev/null || true
python3 app.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..
sleep 5

# Step 3: Start Frontend Server
echo ""
echo "[3/3] Starting Frontend Server..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a bit more for frontend to be ready
sleep 5

# Get the actual frontend port
FRONTEND_PORT=$(netstat -tuln 2>/dev/null | grep "300" | grep -oP ':\K[0-9]+' | head -1 || echo "3000")
SERVER_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "========================================"
echo "   Chatbot Started Successfully!"
echo "========================================"
echo ""
echo "Backend:  http://localhost:8002"
echo "Frontend: http://localhost:$FRONTEND_PORT"
echo "Admin:    http://localhost:$FRONTEND_PORT/admin"
echo ""
echo "Backend PID:  $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""

# Create a simple HTML page that redirects to the chatbot
cat > chatbot_access.html << EOF
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="refresh" content="2;url=http://localhost:$FRONTEND_PORT">
    <title>Opening Chatbot...</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .container {
            text-align: center;
        }
        h1 { font-size: 2.5em; margin-bottom: 20px; }
        p { font-size: 1.2em; }
        a {
            display: inline-block;
            margin-top: 20px;
            padding: 15px 30px;
            background: white;
            color: #667eea;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Opening Chatbot...</h1>
        <p>Your chatbot is starting...</p>
        <p>If it doesn't open automatically, click below:</p>
        <a href="http://localhost:$FRONTEND_PORT">Open Chatbot</a>
    </div>
</body>
</html>
EOF

# Try to open browser (works on some Linux systems with GUI)
if command -v xdg-open > /dev/null; then
    xdg-open "http://localhost:$FRONTEND_PORT" 2>/dev/null &
elif command -v gnome-open > /dev/null; then
    gnome-open "http://localhost:$FRONTEND_PORT" 2>/dev/null &
fi

echo "✅ Chatbot is ready!"
echo ""
echo "Open in browser:"
echo "  http://localhost:$FRONTEND_PORT"
echo "  http://$SERVER_IP:$FRONTEND_PORT (from external)"
echo ""
echo "To stop the servers, run:"
echo "kill $BACKEND_PID $FRONTEND_PID"
echo ""

