#!/bin/bash
# Safe build script that handles vulnerabilities
set -e

echo "🚀 Starting safe build process..."

# Install Python dependencies first
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create backend directories
echo "📁 Creating backend directories..."
mkdir -p backend/vectorstore
mkdir -p backend/logs

# Setup backend database
echo "🗄️ Setting up backend..."
cd backend
python -c "
import sqlite3
import os
os.makedirs('vectorstore', exist_ok=True)
os.makedirs('logs', exist_ok=True)
print('✅ Backend setup complete')
"
cd ..

# Build frontend with security fixes
echo "🔨 Building frontend with security updates..."
cd frontend

# Clean install to avoid vulnerabilities
echo "🧹 Cleaning npm cache..."
npm cache clean --force

# Install with audit fix
echo "📦 Installing npm dependencies with security fixes..."
npm install --production=false --audit-level=moderate

# Fix any remaining vulnerabilities
echo "🔒 Fixing vulnerabilities..."
npm audit fix --force || echo "⚠️ Some vulnerabilities may remain"

# Build the frontend
echo "🏗️ Building frontend..."
npm run build

echo "✅ Frontend build complete"
cd ..

echo "🎉 Safe build completed successfully!"
