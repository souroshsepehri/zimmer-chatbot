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
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
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
    mkdir -p backend/logs
    mkdir -p backups
    
    print_success "Directories created"
}

deploy_with_docker() {
    print_status "Deploying with Docker..."
    
    # Stop existing containers
    print_status "Stopping existing containers..."
    docker-compose down 2>/dev/null || true
    
    # Build and start services
    print_status "Building and starting services..."
    docker-compose up -d --build
    
    # Wait for services to start
    print_status "Waiting for services to start..."
    sleep 30
    
    # Check if services are running
    if ! docker-compose ps | grep -q "Up"; then
        print_error "Services failed to start"
        docker-compose logs
        exit 1
    fi
    
    print_success "Services started successfully"
}

initialize_database() {
    print_status "Initializing database..."
    
    # Wait for backend to be ready
    print_status "Waiting for backend to be ready..."
    for i in {1..30}; do
        if docker-compose exec backend python -c "import requests; requests.get('http://localhost:8000/health')" 2>/dev/null; then
            break
        fi
        sleep 2
    done
    
    # Initialize database
    docker-compose exec backend python init_database.py
    docker-compose exec backend python add_sample_data.py
    
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
    docker-compose ps
    echo
    echo "Access URLs:"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend API: http://localhost:8000/api"
    echo "  Health Check: http://localhost:8000/health"
    echo "  Nginx Proxy: http://localhost"
    echo
    echo "Useful Commands:"
    echo "  View logs: docker-compose logs -f"
    echo "  Stop services: docker-compose down"
    echo "  Restart services: docker-compose restart"
    echo "  Update services: docker-compose pull && docker-compose up -d"
}

create_management_scripts() {
    print_status "Creating management scripts..."
    
    # Create start script
    cat > start-chatbot.sh << 'EOF'
#!/bin/bash
echo "Starting Persian Chatbot..."
docker-compose up -d
echo "Services started. Access at http://localhost"
EOF
    chmod +x start-chatbot.sh
    
    # Create stop script
    cat > stop-chatbot.sh << 'EOF'
#!/bin/bash
echo "Stopping Persian Chatbot..."
docker-compose down
echo "Services stopped"
EOF
    chmod +x stop-chatbot.sh
    
    # Create restart script
    cat > restart-chatbot.sh << 'EOF'
#!/bin/bash
echo "Restarting Persian Chatbot..."
docker-compose down
docker-compose up -d
echo "Services restarted"
EOF
    chmod +x restart-chatbot.sh
    
    # Create update script
    cat > update-chatbot.sh << 'EOF'
#!/bin/bash
echo "Updating Persian Chatbot..."
git pull origin main
docker-compose down
docker-compose up -d --build
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
docker-compose exec backend cp /app/app.db /app/backup_$DATE.db
docker cp $(docker-compose ps -q backend):/app/backup_$DATE.db $BACKUP_DIR/

# Backup vectorstore
docker-compose exec backend tar -czf /app/vectorstore_$DATE.tar.gz /app/vectorstore
docker cp $(docker-compose ps -q backend):/app/vectorstore_$DATE.tar.gz $BACKUP_DIR/

echo "Backup completed: $BACKUP_DIR/backup_$DATE.db"
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
    deploy_with_docker
    initialize_database
    setup_nginx
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

