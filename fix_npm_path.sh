#!/bin/bash

# Script to fix npm path issues on Linux
echo "========================================"
echo "   Fixing npm Path Issue (Linux)"
echo "========================================"
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Current directory: $(pwd)"
echo ""

# Navigate to frontend directory
if [ ! -d "frontend" ]; then
    echo "ERROR: frontend directory not found!"
    echo "Please run this script from the chatbot project root directory."
    exit 1
fi

cd frontend

# Verify we're in the right directory
echo "Current directory: $(pwd)"
echo ""

# Remove node_modules and package-lock.json if they exist
if [ -d "node_modules" ]; then
    echo "Removing old node_modules..."
    rm -rf node_modules
fi

if [ -f "package-lock.json" ]; then
    echo "Removing package-lock.json..."
    rm -f package-lock.json
fi

# Clear npm cache
echo "Clearing npm cache..."
npm cache clean --force

# Install dependencies fresh
echo ""
echo "Installing npm dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: npm install failed!"
    echo ""
    echo "Troubleshooting steps:"
    echo "1. Make sure Node.js is installed: node --version"
    echo "2. Make sure npm is installed: npm --version"
    echo "3. Check if you're in the correct directory: $(pwd)"
    exit 1
fi

echo ""
echo "========================================"
echo "   npm Dependencies Installed!"
echo "========================================"
echo ""
echo "You can now run: ./start_chatbot_server.sh"
echo ""

