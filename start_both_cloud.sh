#!/bin/bash

# Start Backend and Frontend Together on Cloud Server
echo "========================================"
echo "   Starting Backend + Frontend"
echo "========================================"
echo ""

# Get project root
PROJECT_ROOT="$HOME/chatbot2"
cd "$PROJECT_ROOT"

# Step 1: Start Backend
echo "[1/2] Starting Backend Server..."
cd backend

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating it..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Create directories
mkdir -p vectorstore logs __pycache__

# Start backend with PM2 (if PM2 is available) or nohup
if command -v pm2 &> /dev/null; then
    echo "Using PM2 to start backend..."
    pm2 stop chatbot-backend 2>/dev/null
    pm2 delete chatbot-backend 2>/dev/null
    pm2 start uvicorn --name chatbot-backend \
      --interpreter python3 \
      -- app:app --host 0.0.0.0 --port 8000
    pm2 save
    BACKEND_PID=$(pm2 pid chatbot-backend)
    echo "✅ Backend started with PM2 (PID: $BACKEND_PID)"
else
    echo "Using nohup to start backend..."
    nohup uvicorn app:app --host 0.0.0.0 --port 8000 --workers 1 > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo "✅ Backend started (PID: $BACKEND_PID)"
fi

cd ..

# Wait for backend to start
echo "Waiting 5 seconds for backend to start..."
sleep 5

# Step 2: Start Frontend
echo ""
echo "[2/2] Starting Frontend Server..."
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "❌ Error: npm install failed!"
        exit 1
    fi
fi

# Start frontend with PM2 (if available) or nohup
if command -v pm2 &> /dev/null; then
    echo "Using PM2 to start frontend..."
    pm2 stop chatbot-frontend 2>/dev/null
    pm2 delete chatbot-frontend 2>/dev/null
    pm2 start npm --name chatbot-frontend -- run dev
    pm2 save
    FRONTEND_PID=$(pm2 pid chatbot-frontend)
    echo "✅ Frontend started with PM2 (PID: $FRONTEND_PID)"
else
    echo "Using nohup to start frontend..."
    nohup npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "✅ Frontend started (PID: $FRONTEND_PID)"
fi

cd ..

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo ""
echo "========================================"
echo "   Both Servers Started Successfully!"
echo "========================================"
echo ""
echo "Backend:"
echo "  Local:  http://localhost:8000"
echo "  Server: http://$SERVER_IP:8000"
echo "  API Docs: http://$SERVER_IP:8000/docs"
echo ""
echo "Frontend:"
echo "  Local:  http://localhost:3000"
echo "  Server: http://$SERVER_IP:3000"
echo "  Admin:  http://$SERVER_IP:3000/admin"
echo ""

if command -v pm2 &> /dev/null; then
    echo "PM2 Status:"
    pm2 status
    echo ""
    echo "Useful commands:"
    echo "  pm2 logs chatbot-backend   - View backend logs"
    echo "  pm2 logs chatbot-frontend   - View frontend logs"
    echo "  pm2 restart all            - Restart both"
    echo "  pm2 stop all                - Stop both"
else
    echo "Process IDs:"
    echo "  Backend PID:  $BACKEND_PID"
    echo "  Frontend PID: $FRONTEND_PID"
    echo ""
    echo "View logs:"
    echo "  tail -f backend.log    - Backend logs"
    echo "  tail -f frontend.log   - Frontend logs"
    echo ""
    echo "To stop:"
    echo "  kill $BACKEND_PID $FRONTEND_PID"
fi

echo ""


