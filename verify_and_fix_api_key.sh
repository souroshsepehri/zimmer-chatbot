#!/bin/bash

# Verify and Fix API Key Loading
echo "========================================"
echo "   Verifying API Key Setup"
echo "========================================"
echo ""

cd ~/chatbot2/backend

# Check if .env file exists
echo "[1/3] Checking .env file..."
if [ -f ".env" ]; then
    echo "✅ .env file exists"
    if grep -q "OPENAI_API_KEY" .env; then
        echo "✅ OPENAI_API_KEY found in .env"
        # Show first few chars (for verification)
        API_KEY_PREVIEW=$(grep "OPENAI_API_KEY" .env | cut -d'=' -f2 | cut -c1-10)
        echo "   Preview: $API_KEY_PREVIEW..."
    else
        echo "❌ OPENAI_API_KEY not found in .env"
    fi
else
    echo "❌ .env file not found!"
    exit 1
fi

echo ""
echo "[2/3] Testing API key loading..."
# Test if Python can read it
python3 -c "
from dotenv import load_dotenv
import os
load_dotenv()
key = os.getenv('OPENAI_API_KEY', '')
if key:
    print(f'✅ API key loaded: {key[:10]}...')
else:
    print('❌ API key not loaded')
"

echo ""
echo "[3/3] Restarting PM2 to reload environment..."
pm2 restart chatbot-backend

echo ""
echo "Waiting 3 seconds..."
sleep 3

echo ""
echo "Checking PM2 logs..."
pm2 logs chatbot-backend --lines 10 --nostream

echo ""
echo "========================================"
echo "   Verification Complete"
echo "========================================"
echo ""
echo "Test the API:"
echo "  curl http://localhost:8002/health"
echo "  curl -X POST http://localhost:8002/api/chat -H 'Content-Type: application/json' -d '{\"message\": \"سلام\"}'"
echo ""

