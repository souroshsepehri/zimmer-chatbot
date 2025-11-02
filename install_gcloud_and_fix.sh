#!/bin/bash

echo "========================================"
echo "   Installing gcloud and Fixing Firewall"
echo "========================================"
echo ""

# Check if already installed
if command -v gcloud > /dev/null; then
    echo "✅ gcloud already installed"
else
    echo "Installing gcloud CLI..."
    # Install via snap (if available)
    if command -v snap > /dev/null; then
        sudo snap install google-cloud-cli --classic
    else
        # Alternative installation method
        echo "Snap not available. Installing via apt..."
        echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
        curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
        sudo apt-get update && sudo apt-get install -y google-cloud-cli
    fi
    
    # Initialize gcloud (may require user interaction)
    echo ""
    echo "⚠️  You may need to authenticate gcloud"
    echo "Run: gcloud auth login"
fi

echo ""
echo "Getting project and zone info..."
PROJECT_ID=$(curl -s -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/project/project-id)
ZONE=$(curl -s -H "Metadata-Flavor: Google" http://169.254.169.254/computeMetadata/v1/instance/zone | awk -F'/' '{print $NF}')

echo "Project: $PROJECT_ID"
echo "Zone: $ZONE"
echo ""

# Create firewall rule
echo "Creating firewall rule..."
gcloud compute firewall-rules create allow-chatbot-ports \
    --allow tcp:3000,tcp:3001,tcp:3002,tcp:3003,tcp:8002 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow chatbot ports" \
    --project=$PROJECT_ID 2>&1 | tee /tmp/firewall_result.txt

if grep -q "already exists" /tmp/firewall_result.txt; then
    echo "✅ Firewall rule already exists"
    echo "Updating it..."
    gcloud compute firewall-rules update allow-chatbot-ports \
        --allow tcp:3000,tcp:3001,tcp:3002,tcp:3003,tcp:8002 \
        --project=$PROJECT_ID
    echo "✅ Firewall rule updated"
else
    echo "✅ Firewall rule created"
fi

rm -f /tmp/firewall_result.txt

echo ""
echo "========================================"
echo "✅ Firewall configured!"
echo "========================================"
echo ""

