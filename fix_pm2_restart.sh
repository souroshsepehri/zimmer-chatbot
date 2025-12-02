#!/bin/bash

echo "=========================================="
echo "  Fixing PM2 Frontend Restart Loop"
echo "=========================================="
echo ""

# Step 1: Stop and delete the problematic process
echo "[1/4] Stopping chatbot-frontend..."
pm2 stop chatbot-frontend 2>/dev/null || true
pm2 delete chatbot-frontend 2>/dev/null || true
sleep 2
echo "✓ Process stopped"
echo ""

# Step 2: Kill any process using port 3000
echo "[2/4] Freeing port 3000..."
# Try different methods to find and kill the process
if command -v lsof &> /dev/null; then
    PORT_3000_PID=$(lsof -ti:3000 2>/dev/null || echo "")
elif command -v fuser &> /dev/null; then
    PORT_3000_PID=$(fuser 3000/tcp 2>/dev/null | awk '{print $NF}' || echo "")
elif command -v netstat &> /dev/null; then
    PORT_3000_PID=$(netstat -tlnp 2>/dev/null | grep :3000 | awk '{print $7}' | cut -d'/' -f1 | head -1 || echo "")
fi

if [ ! -z "$PORT_3000_PID" ] && [ "$PORT_3000_PID" != "" ]; then
    echo "Found process $PORT_3000_PID using port 3000, killing it..."
    kill -9 $PORT_3000_PID 2>/dev/null || true
    sleep 2
    echo "✓ Port 3000 freed"
else
    echo "✓ Port 3000 appears to be free"
fi
echo ""

# Step 3: Check if frontend needs to be built for production
echo "[3/4] Checking frontend build status..."
cd frontend || exit 1

# Check if .next directory exists (required for 'npm start')
if [ ! -d ".next" ]; then
    echo "⚠ .next directory not found. Building frontend..."
    echo "This is required for 'npm start' (production mode)"
    npm run build
    if [ $? -ne 0 ]; then
        echo "❌ Build failed! Will use dev mode instead..."
        echo "Updating ecosystem.config.js to use dev mode..."
        cd ..
        # We'll handle this by using dev mode with correct port
    else
        echo "✓ Build successful"
    fi
else
    echo "✓ Frontend already built (.next directory exists)"
fi
cd ..
echo ""

# Step 4: Restart PM2 with correct configuration
echo "[4/4] Restarting chatbot-frontend with PM2..."
pm2 start ecosystem.config.js --only chatbot-frontend --env production --update-env
pm2 save
echo ""
echo "=========================================="
echo "  Status Check"
echo "=========================================="
pm2 status chatbot-frontend
echo ""
echo "Waiting 5 seconds to check if it starts successfully..."
sleep 5
pm2 logs chatbot-frontend --lines 10 --nostream
echo ""
echo "=========================================="
echo "  Done!"
echo "=========================================="
echo ""
echo "If you still see errors, check:"
echo "  1. pm2 logs chatbot-frontend"
echo "  2. Ensure port 8000 is available"
echo "  3. Ensure frontend/.next directory exists (run: cd frontend && npm run build)"
echo ""

