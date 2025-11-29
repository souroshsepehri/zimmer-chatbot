#!/bin/bash

echo "=========================================="
echo "  Installing Dependencies & Fixing Backend"
echo "=========================================="

cd ~/chatbot2

# Check if virtual environment exists
if [ -d "backend/venv" ]; then
    echo "✓ Virtual environment found"
    echo "Activating virtual environment..."
    source backend/venv/bin/activate
    PYTHON_CMD="backend/venv/bin/python3"
elif [ -d "venv" ]; then
    echo "✓ Virtual environment found in root"
    source venv/bin/activate
    PYTHON_CMD="venv/bin/python3"
else
    echo "⚠ No virtual environment found, using system python3"
    PYTHON_CMD="python3"
fi

# Install dependencies
echo ""
echo "Installing Python dependencies..."
cd backend
$PYTHON_CMD -m pip install --upgrade pip
$PYTHON_CMD -m pip install -r requirements.txt
cd ..

# Update backend startup script to use correct Python
echo ""
echo "Updating backend startup script..."
cat > backend/start_backend.sh << SCRIPT
#!/bin/bash
cd "\$(dirname "\$0")"

# Try to use venv if it exists
if [ -f "../venv/bin/python3" ]; then
    PYTHON="../venv/bin/python3"
elif [ -f "venv/bin/python3" ]; then
    PYTHON="venv/bin/python3"
else
    PYTHON="python3"
fi

export PORT=\${PORT:-8001}
export HOST=\${HOST:-0.0.0.0}
exec \$PYTHON -m uvicorn main:app --host \$HOST --port \$PORT
SCRIPT
chmod +x backend/start_backend.sh

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

