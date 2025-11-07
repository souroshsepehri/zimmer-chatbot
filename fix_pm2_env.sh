#!/bin/bash

# Fix PM2 Environment Variables
echo "========================================"
echo "   Fixing PM2 Environment Variables"
echo "========================================"
echo ""

cd ~/chatbot2/backend

# Read API key from .env file
API_KEY=$(grep "OPENAI_API_KEY" .env | cut -d'=' -f2)

if [ -z "$API_KEY" ]; then
    echo "❌ Error: Could not read API key from .env file"
    exit 1
fi

echo "✅ Found API key in .env file"
echo ""

# Stop and delete current process
echo "[1/3] Stopping current PM2 process..."
pm2 stop chatbot-backend
pm2 delete chatbot-backend

# Start with environment variable
echo "[2/3] Starting PM2 with environment variable..."
pm2 start uvicorn --name chatbot-backend \
  --interpreter python3 \
  --env OPENAI_API_KEY="$API_KEY" \
  -- app:app --host 0.0.0.0 --port 8002

# Save PM2 config
echo "[3/3] Saving PM2 configuration..."
pm2 save

# Wait and check logs
echo ""
echo "Waiting 3 seconds..."
sleep 3

echo ""
echo "Checking logs..."
pm2 logs chatbot-backend --lines 10 --nostream

echo ""
echo "========================================"
echo "   Setup Complete!"
echo "========================================"
echo ""
echo "Test the API:"
echo "  curl http://localhost:8002/health"
echo "  curl -X POST http://localhost:8002/api/chat -H 'Content-Type: application/json' -d '{\"message\": \"سلام\"}'"
echo ""

