#!/bin/bash
# All-in-one startup script
set -e

echo "🚀 Starting Persian Chatbot..."

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p backend/vectorstore backend/logs

# Setup backend
cd backend
python -c "import sqlite3; import os; os.makedirs('vectorstore', exist_ok=True); os.makedirs('logs', exist_ok=True)"

# Start the app
python -m uvicorn app:app --host 0.0.0.0 --port $PORT
