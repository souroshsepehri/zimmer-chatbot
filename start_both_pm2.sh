#!/bin/bash

# Start Backend and Frontend with PM2 Ecosystem
echo "========================================"
echo "   Starting with PM2 Ecosystem"
echo "========================================"
echo ""

PROJECT_ROOT="$HOME/chatbot2"
cd "$PROJECT_ROOT"

# Create PM2 ecosystem file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'chatbot-backend',
      script: 'uvicorn',
      args: 'app:app --host 0.0.0.0 --port 8001',
      interpreter: 'backend/venv/bin/python3',
      cwd: './backend',
      env: {
        OPENAI_API_KEY: process.env.OPENAI_API_KEY || 'your-api-key-here'
      },
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: './logs/backend-error.log',
      out_file: './logs/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },
    {
      name: 'chatbot-frontend',
      script: 'npm',
      args: 'run dev',
      cwd: './frontend',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '512M',
      env: {
        NODE_ENV: 'production',
        PORT: 8000,
        NEXT_PUBLIC_API_URL: 'http://localhost:8001/api'
      },
      error_file: './logs/frontend-error.log',
      out_file: './logs/frontend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};
EOF

# Create logs directory
mkdir -p logs

# Stop existing processes
pm2 stop all 2>/dev/null
pm2 delete all 2>/dev/null

# Load API key from .env if exists
if [ -f "backend/.env" ]; then
    export $(grep -v '^#' backend/.env | xargs)
    echo "✅ Loaded API key from backend/.env"
fi

# Start both services
echo "Starting both services with PM2..."
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Wait a moment
sleep 3

# Show status
echo ""
echo "========================================"
echo "   Services Started!"
echo "========================================"
echo ""
pm2 status
echo ""

# Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

echo "Access your chatbot:"
echo "  Backend API:  http://$SERVER_IP:8001"
echo "  API Docs:     http://$SERVER_IP:8001/docs"
echo "  Frontend:     http://$SERVER_IP:8000"
echo "  Admin Panel: http://$SERVER_IP:8000/admin"
echo ""
echo "Useful commands:"
echo "  pm2 status              - Check status"
echo "  pm2 logs                 - View all logs"
echo "  pm2 logs chatbot-backend - Backend logs"
echo "  pm2 logs chatbot-frontend - Frontend logs"
echo "  pm2 restart all         - Restart both"
echo "  pm2 stop all             - Stop both"
echo "  pm2 monit                - Monitor dashboard"
echo ""


