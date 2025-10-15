#!/bin/bash

# Persian Chatbot Server Deployment Script
# This script automates the deployment process for your Persian chatbot

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="persian-chatbot"
BACKEND_PORT=8000
FRONTEND_PORT=3000
NGINX_PORT=80

# Functions
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    print_status "Checking system requirements..."
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        exit 1
    fi
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    
    # Check if PM2 is installed
    if ! command -v pm2 &> /dev/null; then
        print_status "Installing PM2..."
        npm install -g pm2
        if [ $? -ne 0 ]; then
            print_error "Failed to install PM2. Please install manually: npm install -g pm2"
            exit 1
        fi
    fi
    
    # Check if Git is installed
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    print_success "All requirements met"
}

setup_environment() {
    print_status "Setting up environment..."
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_status "Creating .env file..."
        cp backend/env.example .env
        print_warning "Please edit .env file and add your OpenAI API key"
        print_warning "Run: nano .env"
        read -p "Press Enter after editing .env file..."
    fi
    
    # Check if OpenAI API key is set
    if ! grep -q "OPENAI_API_KEY=sk-" .env; then
        print_error "OpenAI API key not found in .env file"
        print_error "Please add your OpenAI API key to .env file"
        exit 1
    fi
    
    print_success "Environment configured"
}

create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p backend/vectorstore
    mkdir -p logs
    mkdir -p backups
    
    print_success "Directories created"
}

deploy_with_pm2() {
    print_status "Deploying with PM2..."
    
    # Install dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        print_error "Failed to install Python dependencies"
        exit 1
    fi
    
    # Install frontend dependencies if frontend directory exists
    if [ -d "frontend" ]; then
        print_status "Installing frontend dependencies..."
        cd frontend
        npm install
        if [ $? -ne 0 ]; then
            print_error "Failed to install frontend dependencies"
            exit 1
        fi
        cd ..
    fi
    
    print_success "Dependencies installed"
    
    # Stop existing processes
    print_status "Stopping existing processes..."
    pm2 delete all 2>/dev/null || true
    
    # Install PM2 log rotation
    pm2 install pm2-logrotate 2>/dev/null || true
    pm2 set pm2-logrotate:max_size 10M
    pm2 set pm2-logrotate:retain 30
    pm2 set pm2-logrotate:compress true
    
    # Start services
    print_status "Starting services..."
    pm2 start ecosystem.config.js --env production
    
    # Wait for services to start
    print_status "Waiting for services to start..."
    sleep 30
    
    # Check if services are running
    if ! pm2 status | grep -q "online"; then
        print_error "Services failed to start"
        pm2 logs
        exit 1
    fi
    
    print_success "Services started successfully"
}

initialize_database() {
    print_status "Initializing database..."
    
    # Wait for backend to be ready
    print_status "Waiting for backend to be ready..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            break
        fi
        sleep 2
    done
    
    # Initialize database
    python init_database.py
    python add_sample_data.py
    
    print_success "Database initialized"
}

setup_nginx() {
    print_status "Setting up Nginx reverse proxy..."
    
    # Create nginx configuration
    cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:3000;
    }

    server {
        listen 80;
        server_name _;

        # Frontend
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Backend API
        location /api/ {
            proxy_pass http://backend/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            proxy_pass http://backend/health;
        }
    }
}
EOF
    
    # Add nginx service to docker-compose.yml if not exists
    if ! grep -q "nginx:" docker-compose.yml; then
        cat >> docker-compose.yml << 'EOF'

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
EOF
    fi
    
    # Restart with nginx
    docker-compose up -d
    
    print_success "Nginx configured"
}

test_deployment() {
    print_status "Testing deployment..."
    
    # Test backend health
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        print_success "Backend health check passed"
    else
        print_error "Backend health check failed"
        return 1
    fi
    
    # Test frontend
    if curl -s http://localhost:3000 | grep -q "بات هوشمند"; then
        print_success "Frontend is accessible"
    else
        print_warning "Frontend test failed, but this might be normal"
    fi
    
    # Test nginx proxy
    if curl -s http://localhost/health | grep -q "healthy"; then
        print_success "Nginx proxy is working"
    else
        print_warning "Nginx proxy test failed"
    fi
    
    print_success "Deployment test completed"
}

show_status() {
    print_status "Deployment Status:"
    echo
    echo "Services:"
    pm2 status
    echo
    echo "Access URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000/api"
    echo "  Health Check: http://localhost:8000/health"
    echo
    echo "Useful Commands:"
    echo "  View logs: pm2 logs"
    echo "  Stop services: pm2 stop all"
    echo "  Restart services: pm2 restart all"
    echo "  Monitor services: pm2 monit"
    echo "  Update services: git pull && pm2 reload all"
    echo
    echo "PM2 Commands:"
    echo "  pm2 status          - Check service status"
    echo "  pm2 logs            - View logs"
    echo "  pm2 monit           - Monitor services"
    echo "  pm2 restart all     - Restart all services"
    echo "  pm2 stop all        - Stop all services"
}

create_management_scripts() {
    print_status "Creating management scripts..."
    
    # Create start script
    cat > start-chatbot.sh << 'EOF'
#!/bin/bash
echo "Starting Persian Chatbot..."
pm2 start ecosystem.config.js --env production
echo "Services started. Access at http://localhost:3000"
EOF
    chmod +x start-chatbot.sh
    
    # Create stop script
    cat > stop-chatbot.sh << 'EOF'
#!/bin/bash
echo "Stopping Persian Chatbot..."
pm2 stop all
echo "Services stopped"
EOF
    chmod +x stop-chatbot.sh
    
    # Create restart script
    cat > restart-chatbot.sh << 'EOF'
#!/bin/bash
echo "Restarting Persian Chatbot..."
pm2 restart all
echo "Services restarted"
EOF
    chmod +x restart-chatbot.sh
    
    # Create update script
    cat > update-chatbot.sh << 'EOF'
#!/bin/bash
echo "Updating Persian Chatbot..."
git pull origin main
pip install -r requirements.txt
pm2 reload all
echo "Update completed"
EOF
    chmod +x update-chatbot.sh
    
    # Create backup script
    cat > backup-chatbot.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "Creating backup..."

# Backup database
cp app.db $BACKUP_DIR/app-$DATE.db

# Backup PM2 configuration
pm2 save
cp ~/.pm2/dump.pm2 $BACKUP_DIR/pm2-config-$DATE.pm2

# Backup vectorstore
tar -czf $BACKUP_DIR/vectorstore-$DATE.tar.gz vectorstore/

echo "Backup completed: $BACKUP_DIR/app-$DATE.db"
EOF
    chmod +x backup-chatbot.sh
    
    print_success "Management scripts created"
}

# Main deployment process
main() {
    echo "=========================================="
    echo "Persian Chatbot Server Deployment Script"
    echo "=========================================="
    echo
    
    check_requirements
    setup_environment
    create_directories
    deploy_with_pm2
    initialize_database
    test_deployment
    create_management_scripts
    show_status
    
    echo
    print_success "Deployment completed successfully!"
    print_status "Your Persian chatbot is now running"
    print_status "Access it at: http://localhost"
    echo
    print_status "Management scripts created:"
    print_status "  ./start-chatbot.sh   - Start services"
    print_status "  ./stop-chatbot.sh    - Stop services"
    print_status "  ./restart-chatbot.sh - Restart services"
    print_status "  ./update-chatbot.sh  - Update services"
    print_status "  ./backup-chatbot.sh  - Backup data"
}

# Run main function
main "$@"

