#!/bin/bash
# Render Deployment Script
echo "🚀 Starting Render deployment..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p backend/vectorstore
mkdir -p backend/logs

# Set permissions
echo "🔐 Setting permissions..."
chmod +x backend/app.py

echo "✅ Deployment setup completed!"
echo "🌐 Your app will be available at:"
echo "   Backend: https://persian-chatbot-backend.onrender.com"
echo "   Frontend: https://persian-chatbot-frontend.onrender.com"
