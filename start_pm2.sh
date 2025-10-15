#!/bin/bash

echo "Starting Persian Chatbot with PM2..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if PM2 is installed
if ! command -v pm2 &> /dev/null; then
    echo "Installing PM2..."
    npm install -g pm2
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install PM2. Please install manually: npm install -g pm2"
        exit 1
    fi
fi

# Create logs directory
mkdir -p logs

# Install PM2 log rotation if not already installed
if ! pm2 list | grep -q "pm2-logrotate"; then
    echo "Installing PM2 log rotation..."
    pm2 install pm2-logrotate
fi

# Configure log rotation
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 30
pm2 set pm2-logrotate:compress true

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Warning: .env file not found. Please create one with your API keys."
    if [ -f "backend/env.example" ]; then
        echo "Copying from example..."
        cp "backend/env.example" ".env"
        echo "Please edit .env file with your API keys before starting."
        read -p "Press Enter to continue after editing .env file..."
    fi
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install Python dependencies."
    exit 1
fi

# Install frontend dependencies if frontend directory exists
if [ -d "frontend" ]; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install frontend dependencies."
        exit 1
    fi
    cd ..
fi

# Start services with PM2
echo "Starting services with PM2..."
pm2 start ecosystem.config.js --env production

# Save PM2 configuration
pm2 save

echo ""
echo "========================================"
echo "Persian Chatbot started successfully!"
echo "========================================"
echo ""
echo "Services:"
echo "- Backend: http://localhost:8000"
echo "- Frontend: http://localhost:3000"
echo "- Health Check: http://localhost:8000/health"
echo ""
echo "Useful commands:"
echo "- pm2 status          : Check service status"
echo "- pm2 logs            : View logs"
echo "- pm2 monit           : Monitor services"
echo "- pm2 stop all        : Stop all services"
echo "- pm2 restart all     : Restart all services"
echo ""

# Ask if user wants to open monitoring dashboard
read -p "Press Enter to open monitoring dashboard (or Ctrl+C to exit)..."
pm2 monit
