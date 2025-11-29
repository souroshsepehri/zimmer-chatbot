#!/bin/bash

echo "=========================================="
echo "  Fixing Backend & Frontend - Correct Way"
echo "=========================================="

# Delete all
pm2 delete all 2>/dev/null
pm2 kill 2>/dev/null
rm -f ~/.pm2/dump.pm2
sleep 2

# Navigate
cd ~/chatbot2

# Fix frontend package.json port first
echo "Fixing frontend port..."
sed -i 's/-p 3000/-p 8000/g' frontend/package.json
echo "✓ Frontend port fixed to 8000"

# Create backend startup script
echo "Creating backend startup script..."
cat > backend/start_backend.sh << 'SCRIPT'
#!/bin/bash
cd "$(dirname "$0")"
export PORT=${PORT:-8001}
export HOST=${HOST:-0.0.0.0}
exec python3 -m uvicorn main:app --host $HOST --port $PORT
SCRIPT
chmod +x backend/start_backend.sh
echo "✓ Backend script created"

# Create frontend startup script
echo "Creating frontend startup script..."
cat > frontend/start_frontend.sh << 'SCRIPT'
#!/bin/bash
cd "$(dirname "$0")"
export PORT=${PORT:-8000}
exec npm run dev
SCRIPT
chmod +x frontend/start_frontend.sh
echo "✓ Frontend script created"

# Start backend
echo "Starting backend..."
pm2 start backend/start_backend.sh \
  --name chatbot-backend \
  --env PORT=8001 \
  --env HOST=0.0.0.0 \
  --max-memory-restart 1G \
  --autorestart \
  --restart-delay 4000

# Start frontend
echo "Starting frontend..."
pm2 start frontend/start_frontend.sh \
  --name chatbot-frontend \
  --env PORT=8000 \
  --env NEXT_PUBLIC_API_URL=http://localhost:8001/api \
  --max-memory-restart 512M \
  --autorestart \
  --restart-delay 4000

# Save
pm2 save

# Wait
sleep 5

# Status
echo ""
echo "=== Status ==="
pm2 status

# Logs
echo ""
echo "=== Backend Logs ==="
pm2 logs chatbot-backend --lines 10 --nostream

echo ""
echo "=== Frontend Logs ==="
pm2 logs chatbot-frontend --lines 10 --nostream

# Check ports
echo ""
echo "=== Port Check ==="
lsof -i:8001 2>/dev/null | grep LISTEN && echo "✓ Backend on 8001" || echo "⚠ Backend not on 8001"
lsof -i:8000 2>/dev/null | grep LISTEN && echo "✓ Frontend on 8000" || echo "⚠ Frontend not on 8000"

