# 🚀 Persian Chatbot Server Deployment Guide

Complete guide for deploying your Persian chatbot application to any server.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Deployment Methods](#deployment-methods)
4. [Docker Deployment](#docker-deployment)
5. [Manual Server Setup](#manual-server-setup)
6. [Environment Configuration](#environment-configuration)
7. [Database Setup](#database-setup)
8. [Frontend Deployment](#frontend-deployment)
9. [SSL/HTTPS Setup](#sslhttps-setup)
10. [Monitoring & Maintenance](#monitoring--maintenance)
11. [Troubleshooting](#troubleshooting)

## 🎯 Overview

Your Persian chatbot application consists of:
- **Backend**: FastAPI application with SQLite database
- **Frontend**: Next.js React application
- **AI Integration**: OpenAI GPT-4 and embeddings
- **Vector Store**: FAISS for semantic search
- **Admin Panel**: FAQ and log management

## 🔧 Prerequisites

### Server Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- **RAM**: Minimum 2GB (4GB recommended)
- **Storage**: 10GB+ free space
- **Python**: 3.8+ (3.9+ recommended)
- **Node.js**: 16+ (18+ recommended)
- **Docker**: 20.10+ (if using Docker)

### Required Accounts
- OpenAI API account with API key
- Domain name (optional but recommended)
- SSL certificate (Let's Encrypt recommended)

## 🚀 Deployment Methods

### Method 1: Docker Deployment (Recommended)
- ✅ Easy setup and management
- ✅ Consistent environment
- ✅ Easy scaling and updates
- ✅ Built-in process management

### Method 2: Manual Server Setup
- ✅ Full control over environment
- ✅ Better for custom configurations
- ✅ Direct access to logs and files

## 🐳 Docker Deployment

### Step 1: Prepare Server

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Logout and login to apply docker group changes
```

### Step 2: Clone and Configure

```bash
# Clone repository
git clone https://github.com/your-username/chatbot2.git
cd chatbot2

# Create environment file
cp backend/env.example .env
nano .env
```

### Step 3: Environment Configuration

Create `.env` file with:

```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# Database Configuration
DATABASE_URL=sqlite:///./app.db

# Vector Store
VECTORSTORE_PATH=./vectorstore

# Server Configuration
PORT=8000
HOST=0.0.0.0

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://your-domain.com/api
```

### Step 4: Deploy with Docker

```bash
# Build and start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Step 5: Initialize Database

```bash
# Initialize database and add sample data
docker-compose exec backend python init_database.py
docker-compose exec backend python add_sample_data.py
```

## 🛠️ Manual Server Setup

### Step 1: Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install python3.9 python3.9-pip python3.9-venv -y

# Install Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y

# Install system dependencies
sudo apt install nginx sqlite3 git -y
```

### Step 2: Backend Setup

```bash
# Create application directory
sudo mkdir -p /opt/chatbot
sudo chown $USER:$USER /opt/chatbot
cd /opt/chatbot

# Clone repository
git clone https://github.com/your-username/chatbot2.git .

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt

# Set up environment
cp backend/env.example .env
nano .env  # Configure your settings
```

### Step 3: Database Initialization

```bash
# Initialize database
cd backend
python init_database.py
python add_sample_data.py
cd ..
```

### Step 4: Frontend Setup

```bash
# Install frontend dependencies
cd frontend
npm install

# Build frontend
npm run build
cd ..
```

### Step 5: Process Management

Create systemd service for backend:

```bash
sudo nano /etc/systemd/system/chatbot-backend.service
```

```ini
[Unit]
Description=Persian Chatbot Backend
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/chatbot/backend
Environment=PATH=/opt/chatbot/venv/bin
ExecStart=/opt/chatbot/venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable chatbot-backend
sudo systemctl start chatbot-backend
sudo systemctl status chatbot-backend
```

## 🔧 Environment Configuration

### Backend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-...` |
| `OPENAI_MODEL` | GPT model to use | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `DATABASE_URL` | Database connection string | `sqlite:///./app.db` |
| `VECTORSTORE_PATH` | Path to vector store | `./vectorstore` |
| `PORT` | Server port | `8000` |
| `HOST` | Server host | `0.0.0.0` |

### Frontend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://api.yourdomain.com/api` |

## 🗄️ Database Setup

### SQLite (Default)
- ✅ No additional setup required
- ✅ Good for small to medium applications
- ⚠️ Not suitable for high-concurrency production

### PostgreSQL (Production Recommended)

```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Create database and user
sudo -u postgres psql
CREATE DATABASE chatbot_db;
CREATE USER chatbot_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot_user;
\q

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://chatbot_user:your_password@localhost/chatbot_db
```

## 🌐 Frontend Deployment

### Option 1: Nginx Static Files

```bash
# Copy built files
sudo cp -r frontend/out/* /var/www/html/

# Configure Nginx
sudo nano /etc/nginx/sites-available/chatbot
```

```nginx
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/html;
    index index.html;

    # Frontend routes
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Option 2: PM2 Process Manager

```bash
# Install PM2
npm install -g pm2

# Create ecosystem file
nano ecosystem.config.js
```

```javascript
module.exports = {
  apps: [{
    name: 'chatbot-frontend',
    script: 'npm',
    args: 'start',
    cwd: '/opt/chatbot/frontend',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    }
  }]
};
```

```bash
# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## 🔒 SSL/HTTPS Setup

### Using Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Nginx SSL Configuration

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Your application configuration
    root /var/www/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## 📊 Monitoring & Maintenance

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Database test
curl http://localhost:8000/test-db
```

### Log Management

```bash
# Backend logs
sudo journalctl -u chatbot-backend -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Docker logs (if using Docker)
docker-compose logs -f backend
```

### Backup Script

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/opt/backups/chatbot"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
cp /opt/chatbot/backend/app.db $BACKUP_DIR/app_$DATE.db

# Backup vectorstore
tar -czf $BACKUP_DIR/vectorstore_$DATE.tar.gz /opt/chatbot/backend/vectorstore

# Keep only last 7 days
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

### Update Script

```bash
#!/bin/bash
# update.sh

cd /opt/chatbot

# Pull latest changes
git pull origin main

# Update backend
source venv/bin/activate
pip install -r backend/requirements.txt

# Update frontend
cd frontend
npm install
npm run build
cd ..

# Restart services
sudo systemctl restart chatbot-backend
sudo systemctl reload nginx

echo "Update completed"
```

## 🆘 Troubleshooting

### Common Issues

#### 1. Backend Won't Start
```bash
# Check logs
sudo journalctl -u chatbot-backend -n 50

# Check port availability
sudo netstat -tlnp | grep :8000

# Test manually
cd /opt/chatbot/backend
source ../venv/bin/activate
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

#### 2. Database Connection Issues
```bash
# Check database file
ls -la /opt/chatbot/backend/app.db

# Test database
cd /opt/chatbot/backend
python -c "import sqlite3; conn = sqlite3.connect('app.db'); print('DB OK'); conn.close()"
```

#### 3. Frontend Build Issues
```bash
# Clear cache and rebuild
cd /opt/chatbot/frontend
rm -rf .next node_modules
npm install
npm run build
```

#### 4. CORS Issues
- Check `allow_origins` in `backend/app.py`
- Verify frontend URL in CORS settings
- Ensure HTTPS/HTTP protocol matches

#### 5. OpenAI API Issues
```bash
# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

### Performance Optimization

#### 1. Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_faq_question ON faqs(question);
CREATE INDEX idx_log_timestamp ON logs(timestamp);
```

#### 2. Nginx Optimization
```nginx
# Add to nginx.conf
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

# Caching
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

#### 3. System Optimization
```bash
# Increase file limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize kernel parameters
echo "net.core.somaxconn = 65536" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## 📞 Support

### Useful Commands

```bash
# Check service status
sudo systemctl status chatbot-backend

# Restart services
sudo systemctl restart chatbot-backend
sudo systemctl reload nginx

# Check disk space
df -h

# Check memory usage
free -h

# Check running processes
ps aux | grep -E "(python|node|nginx)"
```

### Log Locations

- **Backend logs**: `sudo journalctl -u chatbot-backend`
- **Nginx logs**: `/var/log/nginx/`
- **System logs**: `/var/log/syslog`
- **Docker logs**: `docker-compose logs`

---

## 🎉 Success!

Your Persian chatbot should now be running on your server! 

**Access URLs:**
- Frontend: `https://your-domain.com`
- Backend API: `https://your-domain.com/api`
- Health Check: `https://your-domain.com/health`

**Next Steps:**
1. Test all functionality
2. Set up monitoring
3. Configure backups
4. Set up SSL certificate
5. Optimize performance

For additional support, check the troubleshooting section or create an issue in the repository.

