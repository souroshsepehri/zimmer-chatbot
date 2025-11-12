#!/bin/bash

# Set API Key on Cloud Server
echo "Setting up API key..."

cd ~/chatbot2/backend

# Prompt for API key
echo "Enter your OpenAI API key:"
read -s API_KEY

# Create .env file with API key
cat > .env << EOF
OPENAI_API_KEY=$API_KEY
OPENAI_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small
RETRIEVAL_TOP_K=4
RETRIEVAL_THRESHOLD=0.82
DATABASE_URL=sqlite:///./app.db
EOF

echo "✅ API key saved to ~/chatbot2/backend/.env"
echo ""
echo "⚠️  Restart the server for changes to take effect:"
echo "   pkill -f uvicorn"
echo "   cd ~/chatbot2/backend && source venv/bin/activate"
echo "   nohup uvicorn app:app --host 0.0.0.0 --port 8002 --workers 1 > ../backend.log 2>&1 &"

