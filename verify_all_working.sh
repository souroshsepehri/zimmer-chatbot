#!/bin/bash

echo "=========================================="
echo "  Verifying All Services"
echo "=========================================="
echo ""

echo "=== PM2 Status ==="
pm2 status
echo ""

echo "=== Port Check ==="
lsof -i:8001 2>/dev/null | grep LISTEN && echo "✓ Backend (port 8001) is listening" || echo "⚠ Backend (port 8001) not listening"
lsof -i:8000 2>/dev/null | grep LISTEN && echo "✓ Frontend (port 8000) is listening" || echo "⚠ Frontend (port 8000) not listening"
echo ""

echo "=== Backend Health Check ==="
curl -s http://localhost:8001/docs > /dev/null 2>&1 && echo "✓ Backend API docs accessible" || echo "⚠ Backend API docs not accessible"
curl -s http://localhost:8001/api/health > /dev/null 2>&1 && echo "✓ Backend health endpoint working" || echo "⚠ Backend health endpoint not working"
echo ""

echo "=== Frontend Check ==="
curl -s -I http://localhost:8000 2>/dev/null | head -1 && echo "✓ Frontend responding" || echo "⚠ Frontend not responding"
echo ""

echo "=== Recent Logs ==="
echo "Backend (last 5 lines):"
pm2 logs chatbot-backend --lines 5 --nostream
echo ""
echo "Frontend (last 5 lines):"
pm2 logs chatbot-frontend --lines 5 --nostream
echo ""

echo "=========================================="
echo "  Summary"
echo "=========================================="
BACKEND_STATUS=$(pm2 jlist | grep -o '"name":"chatbot-backend"[^}]*' | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
FRONTEND_STATUS=$(pm2 jlist | grep -o '"name":"chatbot-frontend"[^}]*' | grep -o '"status":"[^"]*"' | cut -d'"' -f4)

if [ "$BACKEND_STATUS" == "online" ]; then
    echo "✓ Backend: ONLINE"
else
    echo "⚠ Backend: $BACKEND_STATUS"
fi

if [ "$FRONTEND_STATUS" == "online" ]; then
    echo "✓ Frontend: ONLINE"
else
    echo "⚠ Frontend: $FRONTEND_STATUS"
fi

echo ""
echo "Your chatbot should be accessible at:"
echo "  Frontend: http://your-server-ip:8000"
echo "  Backend API: http://your-server-ip:8001"
echo "  API Docs: http://your-server-ip:8001/docs"
echo ""

