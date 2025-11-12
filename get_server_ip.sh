#!/bin/bash

echo "========================================"
echo "   Getting Your Server IP Address"
echo "========================================"
echo ""

# Method 1: hostname -I (usually works)
LOCAL_IP=$(hostname -I | awk '{print $1}')
echo "📍 Local IP: $LOCAL_IP"
echo ""

# Method 2: Try different external IP services
echo "Trying to get external IP..."
EXTERNAL_IP=""

# Try multiple services
for service in "icanhazip.com" "ipinfo.io/ip" "api.ipify.org" "checkip.amazonaws.com"; do
    IP=$(curl -s --max-time 3 "$service" 2>/dev/null | grep -oE '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}' | head -1)
    if [ ! -z "$IP" ]; then
        EXTERNAL_IP="$IP"
        echo "✅ External IP found: $EXTERNAL_IP"
        break
    fi
done

if [ -z "$EXTERNAL_IP" ]; then
    echo "⚠️  Could not get external IP automatically"
    echo ""
    echo "Try these methods:"
    echo "  1. Check Google Cloud Console → VM Instances → External IP"
    echo "  2. Run: ip addr show"
    echo "  3. Check your VM instance details in Google Cloud"
fi

echo ""
echo "========================================"
echo "   Your Chatbot URLs"
echo "========================================"
echo ""

if [ ! -z "$EXTERNAL_IP" ]; then
    echo "📍 From Your Computer (Use External IP):"
    echo ""
    echo "  ✅ Frontend:  http://$EXTERNAL_IP:8000"
    echo "  ✅ Admin:     http://$EXTERNAL_IP:8000/admin"
    echo "  ✅ Backend:   http://$EXTERNAL_IP:8001"
    echo "  ✅ API Docs:  http://$EXTERNAL_IP:8001/docs"
    echo ""
    echo "  👉 COPY THIS: http://$EXTERNAL_IP:8000"
else
    echo "📍 Use Local IP (if accessing from server):"
    echo ""
    echo "  Frontend:  http://$LOCAL_IP:8000"
    echo "  Backend:   http://$LOCAL_IP:8001"
    echo ""
    echo "📍 To get External IP:"
    echo "  1. Go to Google Cloud Console"
    echo "  2. Compute Engine → VM Instances"
    echo "  3. Find your VM (vm-185117)"
    echo "  4. Look at 'External IP' column"
fi

echo ""
echo "========================================"
echo ""
