#!/bin/bash

# Persian Chatbot Manual Server Deployment Script
# This script sets up the chatbot without Docker

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/chatbot"
BACKEND_PORT=8000
FRONTEND_PORT=3000
NGINX_PORT=80
PYTHON_VERSION="3.9"
NODE_VERSION="18"

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

check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root"
        print_error "Please run as a regular user with sudo privileges"
        exit 1
    fi
}

install_system_dependencies() {
    print_status "Installing system dependencies..."
    
    # Update package list
    sudo apt update
    
    # Install essential packages
    sudo apt install -y curl wget git build-essential software-properties-common apt-transport-https ca-certificates gnupg lsb-release
    
    print_success "System dependencies installed"
}

install_python() {
    print_status "Installing Python $PYTHON_VERSION..."
    
    # Add deadsnakes PPA for Python versions
    sudo add-apt-repository -y ppa:deadsnakes/ppa
    sudo apt update
    
    # Install Python and pip
    sudo apt install -y python$PYTHON_VERSION python$PYTHON_VERSION-venv python$PYTHON_VERSION-dev python$PYTHON_VERSION-pip
    
    # Create symlink for python3
    sudo ln -sf /usr/bin/python$PYTHON_VERSION /usr/bin/python3
    
    print_success "Python $PYTHON_VERSION installed"
}

install_nodejs() {
    print_status "Installing Node.js $NODE_VERSION..."
    
    # Add NodeSource repository
    curl -fsSL https://deb.nodesource.com/setup_$NODE_VERSION.x | sudo -E bash -
    
    # Install Node.js
    sudo apt install -y nodejs
    
    print_success "Node.js $NODE_VERSION installed"
}

install_nginx() {
    print_status "Installing Nginx..."
    
    sudo apt install -y nginx
    
    # Start and enable Nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    print_success "Nginx installed and started"
}

setup_application_directory() {
    print_status "Setting up application directory..."
    
    # Create application directory
    sudo mkdir -p $APP_DIR
    sudo chown $USER:$USER $APP_DIR
    
    # Clone repository
    if [ ! -d "$APP_DIR/.git" ]; then
        print_status "Cloning repository..."
        git clone https://github.com/your-username/chatbot2.git $APP_DIR
    else
        print_status "Repository already exists, updating..."
        cd $APP_DIR
        git pull origin main
    fi
    
    print_success "Application directory set up"
}

setup_backend() {
    print_status "Setting up backend..."
    
    cd $APP_DIR
    
    # Create virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Install Python dependencies
    pip install --upgrade pip
    pip install -r backend/requirements.txt
    
    # Create environment file
    if [ ! -f .env ]; then
        cp backend/env.example .env
        print_warning "Please edit .env file and add your OpenAI API key"
        print_warning "Run: nano .env"
        read -p "Press Enter after editing .env file..."
    fi
    
    # Create necessary directories
    mkdir -p backend/vectorstore
    mkdir -p backend/logs
    
    print_success "Backend set up"
}

setup_frontend() {
    print_status "Setting up frontend..."
    
    cd $APP_DIR/frontend
    
    # Install dependencies
    npm install
    
    # Build frontend
    npm run build
    
    print_success "Frontend set up"
}

initialize_database() {
    print_status "Initializing database..."
    
    cd $APP_DIR/backend
    source ../venv/bin/activate
    
    # Initialize database
    python init_database.py
    python add_sample_data.py
    
    print_success "Database initialized"
}

create_systemd_service() {
    print_status "Creating systemd service..."
    
    # Create service file
    sudo tee /etc/systemd/system/chatbot-backend.service > /dev/null << EOF
[Unit]
Description=Persian Chatbot Backend
After=network.target

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=$APP_DIR/backend
Environment=PATH=$APP_DIR/venv/bin
EnvironmentFile=$APP_DIR/.env
ExecStart=$APP_DIR/venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port $BACKEND_PORT
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable chatbot-backend
    sudo systemctl start chatbot-backend
    
    print_success "Systemd service created and started"
}

configure_nginx() {
    print_status "Configuring Nginx..."
    
    # Create Nginx configuration
    sudo tee /etc/nginx/sites-available/chatbot > /dev/null << EOF
server {
    listen 80;
    server_name _;
    
    # Frontend
    location / {
        root $APP_DIR/frontend/out;
        index index.html;
        try_files \$uri \$uri/ /index.html;
    }
    
    # Backend API
    location /api/ {
        proxy_pass http://localhost:$BACKEND_PORT/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Health check
    location /health {
        proxy_pass http://localhost:$BACKEND_PORT/health;
    }
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Test and reload Nginx
    sudo nginx -t
    sudo systemctl reload nginx
    
    print_success "Nginx configured"
}

setup_ssl() {
    print_status "Setting up SSL certificate..."
    
    # Install Certbot
    sudo apt install -y certbot python3-certbot-nginx
    
    # Get domain name
    read -p "Enter your domain name (or press Enter to skip SSL setup): " DOMAIN_NAME
    
    if [ ! -z "$DOMAIN_NAME" ]; then
        # Update Nginx configuration with domain
        sudo sed -i "s/server_name _;/server_name $DOMAIN_NAME;/" /etc/nginx/sites-available/chatbot
        sudo nginx -t
        sudo systemctl reload nginx
        
        # Get SSL certificate
        sudo certbot --nginx -d $DOMAIN_NAME
        
        print_success "SSL certificate installed for $DOMAIN_NAME"
    else
        print_warning "SSL setup skipped"
    fi
}

create_management_scripts() {
    print_status "Creating management scripts..."
    
    # Create start script
    cat > $APP_DIR/start-chatbot.sh << 'EOF'
#!/bin/bash
echo "Starting Persian Chatbot..."
sudo systemctl start chatbot-backend
sudo systemctl start nginx
echo "Services started"
EOF
    chmod +x $APP_DIR/start-chatbot.sh
    
    # Create stop script
    cat > $APP_DIR/stop-chatbot.sh << 'EOF'
#!/bin/bash
echo "Stopping Persian Chatbot..."
sudo systemctl stop chatbot-backend
sudo systemctl stop nginx
echo "Services stopped"
EOF
    chmod +x $APP_DIR/stop-chatbot.sh
    
    # Create restart script
    cat > $APP_DIR/restart-chatbot.sh << 'EOF'
#!/bin/bash
echo "Restarting Persian Chatbot..."
sudo systemctl restart chatbot-backend
sudo systemctl restart nginx
echo "Services restarted"
EOF
    chmod +x $APP_DIR/restart-chatbot.sh
    
    # Create status script
    cat > $APP_DIR/status-chatbot.sh << 'EOF'
#!/bin/bash
echo "=== Persian Chatbot Status ==="
echo "Backend:"
sudo systemctl status chatbot-backend --no-pager
echo
echo "Nginx:"
sudo systemctl status nginx --no-pager
echo
echo "Health Check:"
curl -s http://localhost:8000/health | jq . || echo "Backend not responding"
EOF
    chmod +x $APP_DIR/status-chatbot.sh
    
    # Create update script
    cat > $APP_DIR/update-chatbot.sh << 'EOF'
#!/bin/bash
echo "Updating Persian Chatbot..."
cd /opt/chatbot
git pull origin main
source venv/bin/activate
pip install -r backend/requirements.txt
cd frontend
npm install
npm run build
cd ..
sudo systemctl restart chatbot-backend
sudo systemctl reload nginx
echo "Update completed"
EOF
    chmod +x $APP_DIR/update-chatbot.sh
    
    # Create backup script
    cat > $APP_DIR/backup-chatbot.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/chatbot"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

echo "Creating backup..."

# Backup database
cp /opt/chatbot/backend/app.db $BACKUP_DIR/app_$DATE.db

# Backup vectorstore
tar -czf $BACKUP_DIR/vectorstore_$DATE.tar.gz -C /opt/chatbot/backend vectorstore

# Keep only last 7 days
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/app_$DATE.db"
EOF
    chmod +x $APP_DIR/backup-chatbot.sh
    
    print_success "Management scripts created"
}

test_deployment() {
    print_status "Testing deployment..."
    
    # Wait for services to start
    sleep 10
    
    # Test backend
    if curl -s http://localhost:$BACKEND_PORT/health | grep -q "healthy"; then
        print_success "Backend is running"
    else
        print_error "Backend is not responding"
        return 1
    fi
    
    # Test frontend
    if curl -s http://localhost | grep -q "بات هوشمند"; then
        print_success "Frontend is accessible"
    else
        print_warning "Frontend test failed"
    fi
    
    print_success "Deployment test completed"
}

show_status() {
    print_status "Deployment Status:"
    echo
    echo "Services:"
    sudo systemctl status chatbot-backend --no-pager
    echo
    sudo systemctl status nginx --no-pager
    echo
    echo "Access URLs:"
    echo "  Frontend: http://localhost"
    echo "  Backend API: http://localhost/api"
    echo "  Health Check: http://localhost/health"
    echo
    echo "Management Scripts:"
    echo "  $APP_DIR/start-chatbot.sh   - Start services"
    echo "  $APP_DIR/stop-chatbot.sh    - Stop services"
    echo "  $APP_DIR/restart-chatbot.sh - Restart services"
    echo "  $APP_DIR/status-chatbot.sh  - Check status"
    echo "  $APP_DIR/update-chatbot.sh  - Update application"
    echo "  $APP_DIR/backup-chatbot.sh  - Backup data"
}

# Main deployment process
main() {
    echo "=========================================="
    echo "Persian Chatbot Manual Server Deployment"
    echo "=========================================="
    echo
    
    check_root
    install_system_dependencies
    install_python
    install_nodejs
    install_nginx
    setup_application_directory
    setup_backend
    setup_frontend
    initialize_database
    create_systemd_service
    configure_nginx
    setup_ssl
    create_management_scripts
    test_deployment
    show_status
    
    echo
    print_success "Manual deployment completed successfully!"
    print_status "Your Persian chatbot is now running"
    print_status "Access it at: http://localhost"
}

# Run main function
main "$@"

