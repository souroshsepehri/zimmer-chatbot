#!/bin/bash

echo "=========================================="
echo "  Checking All Services"
echo "=========================================="
echo ""

# Check PM2 status
echo "[1/5] PM2 Status:"
pm2 status
echo ""

# Check what's on port 8000
echo "[2/5] Port 8000 (should be frontend):"
if command -v lsof &> /dev/null; then
    PORT_8000=$(lsof -i:8000 2>/dev/null)
    if [ ! -z "$PORT_8000" ]; then
        echo "$PORT_8000"
        # Try to identify the process
        PID=$(echo "$PORT_8000" | awk 'NR==2 {print $2}')
        if [ ! -z "$PID" ]; then
            PROCESS=$(ps -p $PID -o comm= 2>/dev/null)
            echo "  Process: $PROCESS (PID: $PID)"
        fi
    else
        echo "  ⚠ Nothing listening on port 8000"
    fi
else
    netstat -tlnp 2>/dev/null | grep 8000 || echo "  ⚠ Nothing listening on port 8000"
fi
echo ""

# Check what's on port 8001
echo "[3/5] Port 8001 (should be backend):"
if command -v lsof &> /dev/null; then
    PORT_8001=$(lsof -i:8001 2>/dev/null)
    if [ ! -z "$PORT_8001" ]; then
        echo "$PORT_8001"
    else
        echo "  ⚠ Nothing listening on port 8001"
    fi
else
    netstat -tlnp 2>/dev/null | grep 8001 || echo "  ⚠ Nothing listening on port 8001"
fi
echo ""

# Test backend
echo "[4/5] Testing backend (port 8001):"
BACKEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/health 2>/dev/null || echo "000")
if [ "$BACKEND_RESPONSE" == "200" ] || [ "$BACKEND_RESPONSE" == "404" ]; then
    echo "  ✓ Backend responding on port 8001"
else
    echo "  ⚠ Backend not responding on port 8001 (HTTP $BACKEND_RESPONSE)"
fi
echo ""

# Test frontend
echo "[5/5] Testing frontend (port 8000):"
FRONTEND_RESPONSE=$(curl -s -I http://localhost:8000 2>/dev/null | head -1)
if echo "$FRONTEND_RESPONSE" | grep -q "200\|301\|302"; then
    echo "  ✓ Frontend responding on port 8000"
    echo "  $FRONTEND_RESPONSE"
elif echo "$FRONTEND_RESPONSE" | grep -q "uvicorn"; then
    echo "  ⚠ Port 8000 is serving backend (uvicorn), not frontend!"
    echo "  $FRONTEND_RESPONSE"
else
    echo "  ⚠ Frontend not responding correctly"
    echo "  $FRONTEND_RESPONSE"
fi
echo ""

# Check frontend logs
echo "=========================================="
echo "  Frontend Logs (last 10 lines)"
echo "=========================================="
pm2 logs chatbot-frontend --lines 10 --nostream
echo ""

# Check backend logs
echo "=========================================="
echo "  Backend Logs (last 10 lines)"
echo "=========================================="
pm2 logs chatbot-backend --lines 10 --nostream
echo ""

