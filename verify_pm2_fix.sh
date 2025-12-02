#!/bin/bash

echo "=========================================="
echo "  Verifying PM2 Frontend Fix"
echo "=========================================="
echo ""

# Check PM2 status
echo "[1/4] Checking PM2 status..."
pm2 status chatbot-frontend
echo ""

# Check if port 8000 is in use (should be)
echo "[2/4] Checking port 8000..."
if command -v lsof &> /dev/null; then
    PORT_8000=$(lsof -ti:8000 2>/dev/null)
    if [ ! -z "$PORT_8000" ]; then
        echo "✓ Port 8000 is in use by process $PORT_8000 (this is correct)"
    else
        echo "⚠ Port 8000 is not in use (frontend may not have started)"
    fi
elif command -v netstat &> /dev/null; then
    PORT_8000=$(netstat -tlnp 2>/dev/null | grep :8000 || echo "")
    if [ ! -z "$PORT_8000" ]; then
        echo "✓ Port 8000 is listening"
        echo "  $PORT_8000"
    else
        echo "⚠ Port 8000 is not listening"
    fi
fi
echo ""

# Check if port 3000 is free (should be)
echo "[3/4] Checking port 3000 (should be free)..."
if command -v lsof &> /dev/null; then
    PORT_3000=$(lsof -ti:3000 2>/dev/null)
    if [ ! -z "$PORT_3000" ]; then
        echo "⚠ Port 3000 is still in use by process $PORT_3000"
    else
        echo "✓ Port 3000 is free (this is correct)"
    fi
fi
echo ""

# Check recent logs
echo "[4/4] Recent logs (last 15 lines)..."
pm2 logs chatbot-frontend --lines 15 --nostream
echo ""

# Summary
echo "=========================================="
echo "  Summary"
echo "=========================================="
STATUS=$(pm2 jlist | grep -o '"name":"chatbot-frontend"[^}]*' | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
if [ "$STATUS" == "online" ]; then
    echo "✓ chatbot-frontend is ONLINE"
    
    # Check logs for port
    LOGS=$(pm2 logs chatbot-frontend --lines 20 --nostream 2>&1)
    if echo "$LOGS" | grep -q "port.*8000\|:8000"; then
        echo "✓ Logs show port 8000 (correct)"
    elif echo "$LOGS" | grep -q "port.*3000\|:3000"; then
        echo "⚠ Logs still show port 3000 (may need to check config)"
    fi
    
    if echo "$LOGS" | grep -q "EADDRINUSE\|address already in use"; then
        echo "⚠ Still seeing port conflicts in logs"
    else
        echo "✓ No port conflict errors"
    fi
else
    echo "⚠ chatbot-frontend status: $STATUS"
    echo "  Check logs for errors: pm2 logs chatbot-frontend"
fi
echo ""
echo "To view live logs: pm2 logs chatbot-frontend"
echo "To test frontend: curl http://localhost:8000"
echo ""

