#!/bin/bash

# Setup API Key for Cloud Server
echo "========================================"
echo "   Setting Up API Key"
echo "========================================"
echo ""

cd ~/chatbot2/backend

# Check if .env exists
if [ -f ".env" ]; then
    echo "⚠️ .env file already exists"
    echo ""
    echo "Current OPENAI_API_KEY status:"
    if grep -q "OPENAI_API_KEY" .env; then
        echo "✅ API key is set (value is hidden)"
    else
        echo "❌ API key not found in .env"
    fi
    echo ""
    read -p "Do you want to update it? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file"
        exit 0
    fi
fi

echo "Enter your OpenAI API key:"
read -s API_KEY

if [ -z "$API_KEY" ]; then
    echo "❌ Error: API key cannot be empty"
    exit 1
fi

# Create or update .env file
cat > .env << EOF
OPENAI_API_KEY=$API_KEY
PORT=8002
HOST=0.0.0.0
EOF

echo ""
echo "✅ API key saved to .env file"
echo ""
echo "⚠️  Important: Restart the server for changes to take effect"
echo ""
echo "To restart:"
echo "  1. Stop current server: pkill -f uvicorn"
echo "  2. Start again: nohup uvicorn app:app --host 0.0.0.0 --port 8002 --workers 1 > ../backend.log 2>&1 &"
echo ""



