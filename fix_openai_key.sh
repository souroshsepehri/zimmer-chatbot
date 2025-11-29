#!/bin/bash

echo "=========================================="
echo "  Setting OpenAI API Key"
echo "=========================================="

cd ~/chatbot2

# Option 1: Update the startup script to pass through env vars
echo "Updating backend startup script..."
cat > backend/start_backend.sh << 'SCRIPT'
#!/bin/bash
cd "$(dirname "$0")"

# Try venv first, then system python
if [ -f "../venv/bin/python3" ]; then
    PYTHON="../venv/bin/python3"
elif [ -f "venv/bin/python3" ]; then
    PYTHON="venv/bin/python3"
else
    PYTHON="python3"
fi

# Pass through all environment variables (including OPENAI_API_KEY from PM2)
export PORT=${PORT:-8001}
export HOST=${HOST:-0.0.0.0}
# OPENAI_API_KEY should already be set by PM2, but ensure it's passed through
export OPENAI_API_KEY=${OPENAI_API_KEY:-}

exec $PYTHON -m uvicorn main:app --host $HOST --port $PORT
SCRIPT
chmod +x backend/start_backend.sh

# Option 2: Also create/update .env file (more reliable)
echo "Creating .env file in backend directory..."
cat > backend/.env << ENV
OPENAI_API_KEY=your_openai_api_key_here
ENV

# Restart backend
echo "Restarting backend..."
pm2 restart chatbot-backend

# Wait
sleep 5

# Check logs
echo ""
echo "=== Backend Logs (checking for API key) ==="
pm2 logs chatbot-backend --lines 15 --nostream | grep -i "openai\|api key\|smart agent" || echo "No OpenAI messages found in recent logs"

echo ""
echo "✓ Done! The API key should now be loaded."
echo "Check logs to confirm the warning is gone."

