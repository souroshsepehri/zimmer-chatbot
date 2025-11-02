#!/bin/bash

echo "========================================"
echo "   Diagnosing Page Access Issue"
echo "========================================"
echo ""

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "Unable to detect")

echo "Server Internal IP: $SERVER_IP"
echo "Server External IP: $EXTERNAL_IP"
echo ""

# Check if servers are running
echo "1. Checking if servers are running..."
if pgrep -f "python3 app.py" > /dev/null; then
    echo "   ✅ Backend is running"
else
    echo "   ❌ Backend is NOT running"
fi

if pgrep -f "npm run dev" > /dev/null || pgrep -f "next dev" > /dev/null; then
    echo "   ✅ Frontend is running"
else
    echo "   ❌ Frontend is NOT running"
fi
echo ""

# Check what ports are listening
echo "2. Checking listening ports..."
BACKEND_PORT=$(netstat -tuln 2>/dev/null | grep ":8002" | awk '{print $4}' | head -1)
FRONTEND_PORT=$(netstat -tuln 2>/dev/null | grep "300" | awk '{print $4}' | head -1)

if [ ! -z "$BACKEND_PORT" ]; then
    echo "   ✅ Backend listening on: $BACKEND_PORT"
else
    echo "   ❌ Backend NOT listening"
fi

if [ ! -z "$FRONTEND_PORT" ]; then
    echo "   ✅ Frontend listening on: $FRONTEND_PORT"
    FRONTEND_PORT_NUM=$(echo $FRONTEND_PORT | grep -oP ':\K[0-9]+')
else
    echo "   ❌ Frontend NOT listening"
    FRONTEND_PORT_NUM="3000"
fi
echo ""

# Test from server itself
echo "3. Testing from server itself..."
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "   ✅ Backend responds on localhost"
else
    echo "   ❌ Backend doesn't respond on localhost"
fi

if curl -s http://localhost:$FRONTEND_PORT_NUM > /dev/null 2>&1; then
    echo "   ✅ Frontend responds on localhost"
else
    echo "   ❌ Frontend doesn't respond on localhost"
fi
echo ""

# Check firewall
echo "4. Checking firewall status..."
if command -v ufw > /dev/null; then
    UFW_STATUS=$(sudo ufw status 2>/dev/null | head -1)
    echo "   UFW Status: $UFW_STATUS"
    if echo "$UFW_STATUS" | grep -q "active"; then
        echo "   ⚠️  Firewall is ACTIVE - this might be blocking access!"
        echo ""
        echo "   Opening ports..."
        sudo ufw allow 8002/tcp comment "Chatbot Backend"
        sudo ufw allow 3000/tcp comment "Chatbot Frontend"
        sudo ufw allow 3001/tcp comment "Chatbot Frontend Alt"
        sudo ufw allow 3002/tcp comment "Chatbot Frontend Alt2"
        sudo ufw allow 3003/tcp comment "Chatbot Frontend Alt3"
        echo "   ✅ Ports opened in firewall"
    else
        echo "   ✅ Firewall is inactive"
    fi
elif command -v firewall-cmd > /dev/null; then
    echo "   Firewalld detected"
    echo "   Opening ports..."
    sudo firewall-cmd --permanent --add-port=8002/tcp
    sudo firewall-cmd --permanent --add-port=3000/tcp
    sudo firewall-cmd --permanent --add-port=3001/tcp
    sudo firewall-cmd --permanent --add-port=3002/tcp
    sudo firewall-cmd --permanent --add-port=3003/tcp
    sudo firewall-cmd --reload
    echo "   ✅ Ports opened in firewalld"
fi
echo ""

# Show access URLs
echo "========================================"
echo "   Access URLs"
echo "========================================"
echo ""
echo "From the server itself:"
echo "  Frontend: http://localhost:$FRONTEND_PORT_NUM"
echo "  Backend:  http://localhost:8002"
echo "  Admin:    http://localhost:$FRONTEND_PORT_NUM/admin"
echo ""
echo "From external network:"
echo "  Frontend: http://$SERVER_IP:$FRONTEND_PORT_NUM"
echo "  Backend:  http://$SERVER_IP:8002"
echo "  Admin:    http://$SERVER_IP:$FRONTEND_PORT_NUM/admin"
echo ""
if [ "$EXTERNAL_IP" != "Unable to detect" ] && [ "$EXTERNAL_IP" != "$SERVER_IP" ]; then
    echo "External IP (if different from internal):"
    echo "  Frontend: http://$EXTERNAL_IP:$FRONTEND_PORT_NUM"
    echo "  Backend:  http://$EXTERNAL_IP:8002"
    echo "  Admin:    http://$EXTERNAL_IP:$FRONTEND_PORT_NUM/admin"
    echo ""
fi
echo "========================================"
echo ""
echo "If still can't access:"
echo "1. Make sure you're using the correct IP address"
echo "2. Check if your cloud provider has security groups/firewall rules"
echo "3. For Google Cloud: Check VPC firewall rules"
echo "4. For AWS: Check Security Groups"
echo "5. For Azure: Check Network Security Groups"
echo ""

