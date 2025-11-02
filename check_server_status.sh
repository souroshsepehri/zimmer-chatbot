#!/bin/bash

echo "========================================"
echo "   Checking Server Status"
echo "========================================"
echo ""

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')
echo "Server IP: $SERVER_IP"
echo ""

# Check if processes are running
echo "Checking processes..."
if pgrep -f "python3 app.py" > /dev/null; then
    echo "✅ Backend is running (PID: $(pgrep -f 'python3 app.py'))"
else
    echo "❌ Backend is NOT running"
fi

if pgrep -f "npm run dev" > /dev/null || pgrep -f "next dev" > /dev/null; then
    echo "✅ Frontend is running (PID: $(pgrep -f 'npm run dev' || pgrep -f 'next dev'))"
else
    echo "❌ Frontend is NOT running"
fi
echo ""

# Check if ports are listening
echo "Checking ports..."
if netstat -tuln 2>/dev/null | grep -q ":8002"; then
    LISTEN_ADDR=$(netstat -tuln 2>/dev/null | grep ":8002" | awk '{print $4}')
    echo "✅ Backend port 8002 is listening on: $LISTEN_ADDR"
else
    echo "❌ Backend port 8002 is NOT listening"
fi

if netstat -tuln 2>/dev/null | grep -q ":3000"; then
    LISTEN_ADDR=$(netstat -tuln 2>/dev/null | grep ":3000" | awk '{print $4}')
    echo "✅ Frontend port 3000 is listening on: $LISTEN_ADDR"
else
    echo "❌ Frontend port 3000 is NOT listening"
fi
echo ""

# Check firewall
echo "Checking firewall..."
if command -v ufw > /dev/null; then
    UFW_STATUS=$(sudo ufw status 2>/dev/null | head -1)
    echo "UFW Status: $UFW_STATUS"
    if echo "$UFW_STATUS" | grep -q "active"; then
        echo "⚠️  Firewall is active - ports may be blocked"
        echo "   To open ports, run:"
        echo "   sudo ufw allow 3000/tcp"
        echo "   sudo ufw allow 8002/tcp"
    fi
elif command -v firewall-cmd > /dev/null; then
    echo "Firewalld detected - check firewall rules"
elif command -v iptables > /dev/null; then
    echo "iptables detected - check firewall rules"
fi
echo ""

# Show access URLs
echo "========================================"
echo "   Access URLs"
echo "========================================"
echo "From server itself:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8002"
echo ""
echo "From external network:"
echo "  Frontend: http://$SERVER_IP:3000"
echo "  Backend:  http://$SERVER_IP:8002"
echo "  Admin:    http://$SERVER_IP:3000/admin"
echo ""

# Check logs for errors
echo "========================================"
echo "   Recent Logs (last 5 lines)"
echo "========================================"
if [ -f backend.log ]; then
    echo "Backend log:"
    tail -5 backend.log
    echo ""
fi
if [ -f frontend.log ]; then
    echo "Frontend log:"
    tail -5 frontend.log
    echo ""
fi

