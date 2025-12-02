#!/bin/bash

echo "=========================================="
echo "  Port and Process Diagnosis"
echo "=========================================="
echo ""

# Check PM2 status
echo "[1/5] PM2 Status:"
pm2 status
echo ""

# Check what's on port 8000
echo "[2/5] Port 8000 (should be frontend/Next.js):"
if command -v lsof &> /dev/null; then
    lsof -i:8000 2>/dev/null || echo "  No process found on port 8000"
elif command -v netstat &> /dev/null; then
    netstat -tlnp 2>/dev/null | grep :8000 || echo "  No process found on port 8000"
else
    echo "  Cannot check (lsof/netstat not available)"
fi
echo ""

# Check what's on port 8001
echo "[3/5] Port 8001 (should be backend/FastAPI):"
if command -v lsof &> /dev/null; then
    lsof -i:8001 2>/dev/null || echo "  No process found on port 8001"
elif command -v netstat &> /dev/null; then
    netstat -tlnp 2>/dev/null | grep :8001 || echo "  No process found on port 8001"
else
    echo "  Cannot check (lsof/netstat not available)"
fi
echo ""

# Test port 8000
echo "[4/5] Testing port 8000:"
RESPONSE_8000=$(curl -s -I http://localhost:8000 2>/dev/null | head -1)
if [ ! -z "$RESPONSE_8000" ]; then
    echo "  Response: $RESPONSE_8000"
    SERVER=$(curl -s -I http://localhost:8000 2>/dev/null | grep -i server | head -1)
    if [ ! -z "$SERVER" ]; then
        echo "  $SERVER"
        if echo "$SERVER" | grep -qi "uvicorn"; then
            echo "  ⚠ WARNING: Port 8000 is serving backend (uvicorn), not frontend!"
        elif echo "$SERVER" | grep -qi "next"; then
            echo "  ✓ Port 8000 is serving frontend (Next.js)"
        fi
    fi
else
    echo "  No response from port 8000"
fi
echo ""

# Test port 8001
echo "[5/5] Testing port 8001:"
RESPONSE_8001=$(curl -s -I http://localhost:8001 2>/dev/null | head -1)
if [ ! -z "$RESPONSE_8001" ]; then
    echo "  Response: $RESPONSE_8001"
    SERVER=$(curl -s -I http://localhost:8001 2>/dev/null | grep -i server | head -1)
    if [ ! -z "$SERVER" ]; then
        echo "  $SERVER"
    fi
else
    echo "  No response from port 8001"
fi
echo ""

echo "=========================================="
echo "  Summary"
echo "=========================================="
echo ""
echo "Expected:"
echo "  - Port 8000: Frontend (Next.js)"
echo "  - Port 8001: Backend (FastAPI/uvicorn)"
echo ""
echo "If port 8000 shows uvicorn, the backend is on the wrong port."
echo "If port 8000 shows nothing, the frontend isn't running."
echo ""

