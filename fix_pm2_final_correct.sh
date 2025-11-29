#!/bin/bash

echo "=========================================="
echo "  Fixing PM2 - Correct Method"
echo "=========================================="

# Delete all
pm2 delete all 2>/dev/null
pm2 kill 2>/dev/null
rm -f ~/.pm2/dump.pm2
sleep 2

cd ~/chatbot2

# Start backend - use python3 directly, no bash interpreter
echo "Starting backend..."
cd backend
pm2 start python3 --name chatbot-backend \
  --interpreter python3 \
  -- -m uvicorn main:app --host 0.0.0.0 --port 8001 \
  --max-memory-restart 1G \
  --autorestart \
  --env PORT=8001 \
  --env HOST=0.0.0.0
cd ..

# Start frontend - use npm directly, fix port to 8000
echo "Starting frontend..."
cd frontend

# First, make sure package.json has port 8000
sed -i 's/-p 3000/-p 8000/g' package.json
sed -i 's/"dev": "next dev -H 0.0.0.0 -p [0-9]*"/"dev": "next dev -H 0.0.0.0 -p 8000"/' package.json

pm2 start npm --name chatbot-frontend \
  --interpreter none \
  -- run dev \
  --max-memory-restart 512M \
  --autorestart \
  --env PORT=8000 \
  --env NEXT_PUBLIC_API_URL=http://localhost:8001/api \
  --cwd $(pwd)
cd ..

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
lsof -i:3000 2>/dev/null | grep LISTEN && echo "⚠ Port 3000 still in use!" || echo "✓ Port 3000 is free"

