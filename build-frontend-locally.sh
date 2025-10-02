#!/bin/bash
# Build frontend locally to avoid Render vulnerabilities
echo "🔨 Building frontend locally..."

cd frontend

echo "📦 Installing dependencies..."
npm install --legacy-peer-deps

echo "🏗️ Building frontend..."
npm run build

echo "✅ Frontend built successfully!"
echo "📁 Frontend files are in: frontend/out/"
echo ""
echo "Now you can deploy to Render with the pre-built frontend."
