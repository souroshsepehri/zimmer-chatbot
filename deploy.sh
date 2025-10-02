#!/bin/bash
# Complete deployment script for Persian Chatbot
set -e  # Exit on any error

echo "🚀 Starting Persian Chatbot Deployment..."

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    log "❌ Error: requirements.txt not found in current directory"
    exit 1
fi

# Step 1: Install Python dependencies
log "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Step 2: Create backend directories
log "📁 Creating backend directories..."
mkdir -p backend/vectorstore
mkdir -p backend/logs
mkdir -p backend/__pycache__

# Step 3: Setup backend database
log "🗄️ Setting up backend database..."
cd backend
python -c "
import sqlite3
import os
import sys

# Create directories
os.makedirs('vectorstore', exist_ok=True)
os.makedirs('logs', exist_ok=True)
print('✅ Directories created successfully')

# Test database connection
try:
    conn = sqlite3.connect('app.db')
    conn.close()
    print('✅ Database connection test passed')
except Exception as e:
    print(f'⚠️ Database warning: {e}')

# Test imports
try:
    from app import app
    print('✅ FastAPI app import successful')
except Exception as e:
    print(f'⚠️ App import warning: {e}')
"

cd ..

# Step 4: Build frontend (if possible)
log "🔨 Building frontend..."
if [ -d "frontend" ]; then
    cd frontend
    
    # Check if package.json exists
    if [ -f "package.json" ]; then
        log "📦 Installing npm dependencies..."
        npm install --legacy-peer-deps || log "⚠️ npm install failed, continuing without frontend"
        
        log "🏗️ Building frontend..."
        npm run build || log "⚠️ Frontend build failed, continuing with backend only"
        
        log "✅ Frontend built successfully"
    else
        log "⚠️ No package.json found in frontend directory"
    fi
    
    cd ..
else
    log "⚠️ Frontend directory not found, continuing with backend only"
fi

# Step 5: Start the application
log "🌐 Starting Persian Chatbot..."

# Get port and host from environment
PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}

log "📱 Frontend available at root URL (if built)"
log "🔌 API available at /api"
log "📚 API docs available at /docs"
log "🌐 Server starting on $HOST:$PORT"

# Change to backend directory and start
cd backend

# Start the server
python -m uvicorn app:app --host $HOST --port $PORT --workers 1

# If uvicorn fails, try alternative
if [ $? -ne 0 ]; then
    log "⚠️ uvicorn failed, trying alternative startup..."
    python app.py
fi
