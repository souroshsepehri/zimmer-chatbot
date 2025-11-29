#!/bin/bash

echo "=========================================="
echo "  Fixing API Key and Port"
echo "=========================================="

cd ~/chatbot2

# Create/update .env file in backend directory
echo "Creating .env file with API key..."
cat > backend/.env << EOF
OPENAI_API_KEY=your_openai_api_key_here
PORT=8001
HOST=0.0.0.0
EOF
echo "✓ .env file created"

# Update startup script to ensure PORT is set
echo "Updating startup script..."
cat > backend/start_backend.sh << 'SCRIPT'
#!/bin/bash
cd "$(dirname "$0")"

# Load .env file if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Try to use venv if it exists
if [ -f "../venv/bin/python3" ]; then
    PYTHON="../venv/bin/python3"
elif [ -f "venv/bin/python3" ]; then
    PYTHON="venv/bin/python3"
else
    PYTHON="python3"
fi

# Ensure PORT is set
export PORT=${PORT:-8001}
export HOST=${HOST:-0.0.0.0}

exec $PYTHON -m uvicorn main:app --host $HOST --port $PORT
SCRIPT
chmod +x backend/start_backend.sh
echo "✓ Startup script updated"

# Check if port 8001 is in use
echo ""
echo "Checking port 8001..."
if lsof -i:8001 2>/dev/null | grep -q LISTEN; then
    echo "⚠ Port 8001 is in use. Checking what's using it..."
    lsof -i:8001
    echo "Killing process on port 8001..."
    lsof -ti:8001 | xargs kill -9 2>/dev/null
    sleep 2
fi

# Restart backend
echo ""
echo "Restarting backend..."
pm2 delete chatbot-backend 2>/dev/null
pm2 start backend/start_backend.sh \
  --name chatbot-backend \
  --env PORT=8001 \
  --env HOST=0.0.0.0 \
  --max-memory-restart 1G \
  --autorestart

pm2 save

sleep 5

echo ""
echo "=== Status ==="
pm2 status

echo ""
echo "=== Backend Logs ==="
pm2 logs chatbot-backend --lines 15 --nostream

echo ""
echo "=== Checking for API key warning ==="
if pm2 logs chatbot-backend --err --lines 5 --nostream | grep -q "OpenAI API key not set"; then
    echo "⚠ API key still not loaded"
else
    echo "✓ API key loaded successfully!"
fi










