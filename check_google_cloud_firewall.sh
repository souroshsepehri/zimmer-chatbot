#!/bin/bash

echo "========================================"
echo "   Google Cloud Firewall Check"
echo "========================================"
echo ""

# Detect if running on Google Cloud
if [ -f /sys/class/dmi/id/product_name ]; then
    PRODUCT=$(cat /sys/class/dmi/id/product_name)
    if echo "$PRODUCT" | grep -qi "Google"; then
        echo "✅ Detected Google Cloud VM"
        IS_GCP=true
    else
        IS_GCP=false
    fi
else
    # Check metadata service
    if curl -s -f -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/instance/id > /dev/null 2>&1; then
        echo "✅ Detected Google Cloud VM (via metadata service)"
        IS_GCP=true
        
        # Get instance info
        INSTANCE_NAME=$(curl -s -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/instance/name)
        ZONE=$(curl -s -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/instance/zone | awk -F'/' '{print $NF}')
        PROJECT_ID=$(curl -s -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/project/project-id)
        
        echo "Instance Name: $INSTANCE_NAME"
        echo "Zone: $ZONE"
        echo "Project ID: $PROJECT_ID"
        echo ""
    else
        IS_GCP=false
    fi
fi

if [ "$IS_GCP" = false ]; then
    echo "⚠️  Not detected as Google Cloud VM, checking local firewall..."
    echo ""
fi

# Get server info
SERVER_IP=$(hostname -I | awk '{print $1}')
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "Unable to detect")

echo "Internal IP: $SERVER_IP"
echo "External IP: $EXTERNAL_IP"
echo ""

# Check listening ports
echo "Listening Ports:"
netstat -tuln | grep -E "(3000|3001|3002|3003|8002)" | awk '{print "  ", $4}'
echo ""

# Check local firewall
echo "Local Firewall Status:"
if command -v ufw > /dev/null; then
    sudo ufw status | head -5
elif command -v firewall-cmd > /dev/null; then
    sudo firewall-cmd --list-all
fi
echo ""

# Test local access
echo "Testing Local Access:"
if curl -s http://localhost:8002/health > /dev/null 2>&1; then
    echo "  ✅ Backend accessible locally"
else
    echo "  ❌ Backend NOT accessible locally"
fi

FRONTEND_PORT=$(netstat -tuln | grep "300" | grep -oP ':\K[0-9]+' | head -1 || echo "3000")
if curl -s http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
    echo "  ✅ Frontend accessible locally on port $FRONTEND_PORT"
else
    echo "  ❌ Frontend NOT accessible locally"
fi
echo ""

# Instructions
echo "========================================"
echo "   Fix Instructions"
echo "========================================"
echo ""

if [ "$IS_GCP" = true ]; then
    echo "🔧 GOOGLE CLOUD FIREWALL FIX:"
    echo ""
    echo "1. Go to: https://console.cloud.google.com/compute/instances"
    echo "2. Find your VM: $INSTANCE_NAME"
    echo "3. Click on the VM name"
    echo "4. Go to 'NETWORKING' tab"
    echo "5. Click 'View Details' on the network"
    echo "6. Go to 'Firewall Rules'"
    echo "7. Create a new rule with these ports: 3000,3001,3002,3003,8002"
    echo ""
    echo "OR use this direct link (replace PROJECT_ID):"
    echo "https://console.cloud.google.com/networking/firewalls/list?project=$PROJECT_ID"
    echo ""
fi

echo "📝 ACCESS URLS:"
echo ""
echo "Internal IP:"
echo "  Frontend: http://$SERVER_IP:$FRONTEND_PORT"
echo "  Backend:  http://$SERVER_IP:8002"
echo "  Admin:    http://$SERVER_IP:$FRONTEND_PORT/admin"
echo ""

if [ "$EXTERNAL_IP" != "Unable to detect" ]; then
    echo "External IP:"
    echo "  Frontend: http://$EXTERNAL_IP:$FRONTEND_PORT"
    echo "  Backend:  http://$EXTERNAL_IP:8002"
    echo "  Admin:    http://$EXTERNAL_IP:$FRONTEND_PORT/admin"
    echo ""
fi

echo "💡 TIP: If external IP doesn't work, check Google Cloud Console"
echo "   firewall rules at the link above"
echo ""

