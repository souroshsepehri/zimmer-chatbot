#!/bin/bash

LOCAL_IP=$(hostname -I | awk '{print $1}')
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Unable to detect")

echo "========================================"
echo "   Your Chatbot Access URLs"
echo "========================================"
echo ""
echo "📍 From Your Computer (Use External IP):"
echo ""
if [ "$EXTERNAL_IP" != "Unable to detect" ]; then
    echo "  ✅ Frontend:  http://$EXTERNAL_IP:8000"
    echo "  ✅ Admin:     http://$EXTERNAL_IP:8000/admin"
    echo "  ✅ Backend:   http://$EXTERNAL_IP:8001"
    echo "  ✅ API Docs:  http://$EXTERNAL_IP:8001/docs"
else
    echo "  External IP: Unable to detect"
    echo "  Use Local IP: http://$LOCAL_IP:8000"
fi
echo ""
echo "📍 From Server (Use Local IP):"
echo ""
echo "  Frontend:  http://localhost:8000"
echo "  Backend:   http://localhost:8001"
echo ""
echo "⚠️  Make sure ports 8000 and 8001 are open in firewall!"
echo ""


