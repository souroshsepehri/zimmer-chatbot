# 🐳 Docker Deployment Guide for Persian Chatbot

Complete Docker-based deployment guide for your Persian chatbot application.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Docker Setup](#docker-setup)
3. [Configuration](#configuration)
4. [Production Deployment](#production-deployment)
5. [Docker Compose](#docker-compose)
6. [Environment Variables](#environment-variables)
7. [Data Persistence](#data-persistence)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Git
- OpenAI API Key

### One-Command Deployment

```bash
# Clone and deploy
git clone https://github.com/your-username/chatbot2.git
cd chatbot2
cp backend/env.example .env
# Edit .env with your API key
docker-compose up -d
```

## 🐳 Docker Setup

### Step 1: Install Docker

#### Ubuntu/Debian
```bash
# Update package index
sudo apt update

# Install required packages
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release -y

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

#### CentOS/RHEL
```bash
# Install required packages
sudo yum install -y yum-utils

# Add Docker repository
sudo yum-config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo

# Install Docker
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin -y

# Start and enable Docker
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Step 2: Verify Installation

```bash
# Check Docker version
docker --version
docker compose version

# Test Docker
docker run hello-world
```

## ⚙️ Configuration

### Environment File Setup

Create `.env` file in project root:

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
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# Docker Configuration
COMPOSE_PROJECT_NAME=persian-chatbot
```

### Docker Compose Configuration

Your `docker-compose.yml` should look like this:

```yaml
version: '3.8'

services:
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - VECTORSTORE_PATH=${VECTORSTORE_PATH}
      - PORT=${PORT}
      - HOST=${HOST}
    volumes:
      - ./backend/app.db:/app/app.db
      - ./backend/vectorstore:/app/vectorstore
      - ./backend/logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  frontend:
    build: 
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}
    depends_on:
      - backend
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3000"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

networks:
  default:
    name: chatbot-network
```

## 🏗️ Production Deployment

### Step 1: Create Dockerfiles

#### Backend Dockerfile (`backend/Dockerfile`)

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p vectorstore logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run application
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile (`frontend/Dockerfile`)

```dockerfile
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM node:18-alpine AS runner

# Set working directory
WORKDIR /app

# Install wget for health checks
RUN apk add --no-cache wget

# Copy built application
COPY --from=builder /app/out ./out
COPY --from=builder /app/package*.json ./

# Install production dependencies
RUN npm ci --only=production && npm cache clean --force

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000 || exit 1

# Start application
CMD ["npm", "start"]
```

### Step 2: Nginx Configuration

Create `nginx.conf`:

```nginx
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
        server_name your-domain.com;

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
```

### Step 3: Deploy

```bash
# Build and start all services
docker compose up -d --build

# Check status
docker compose ps

# View logs
docker compose logs -f

# Initialize database
docker compose exec backend python init_database.py
docker compose exec backend python add_sample_data.py
```

## 🔧 Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `OPENAI_MODEL` | GPT model | `gpt-4o-mini` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `DATABASE_URL` | Database URL | `sqlite:///./app.db` |
| `VECTORSTORE_PATH` | Vector store path | `./vectorstore` |
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000/api` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Backend port | `8000` |
| `HOST` | Backend host | `0.0.0.0` |
| `COMPOSE_PROJECT_NAME` | Project name | `persian-chatbot` |

## 💾 Data Persistence

### Volume Configuration

```yaml
volumes:
  # Database persistence
  - ./backend/app.db:/app/app.db
  
  # Vector store persistence
  - ./backend/vectorstore:/app/vectorstore
  
  # Logs persistence
  - ./backend/logs:/app/logs
```

### Backup Script

Create `backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup database
docker compose exec backend cp /app/app.db /app/backup_$DATE.db
docker cp $(docker compose ps -q backend):/app/backup_$DATE.db $BACKUP_DIR/

# Backup vectorstore
docker compose exec backend tar -czf /app/vectorstore_$DATE.tar.gz /app/vectorstore
docker cp $(docker compose ps -q backend):/app/vectorstore_$DATE.tar.gz $BACKUP_DIR/

# Cleanup old backups (keep 7 days)
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

## 📊 Monitoring

### Health Checks

```bash
# Check all services
docker compose ps

# Check specific service
docker compose exec backend python -c "import requests; print(requests.get('http://localhost:8000/health').json())"

# Check logs
docker compose logs backend
docker compose logs frontend
```

### Monitoring Script

Create `monitor.sh`:

```bash
#!/bin/bash

echo "=== Persian Chatbot Status ==="
echo "Date: $(date)"
echo

# Check Docker services
echo "Docker Services:"
docker compose ps
echo

# Check backend health
echo "Backend Health:"
curl -s http://localhost:8000/health | jq .
echo

# Check database
echo "Database Status:"
curl -s http://localhost:8000/test-db | jq .
echo

# Check disk usage
echo "Disk Usage:"
df -h
echo

# Check memory usage
echo "Memory Usage:"
free -h
echo
```

## 🆘 Troubleshooting

### Common Issues

#### 1. Services Won't Start

```bash
# Check logs
docker compose logs

# Check configuration
docker compose config

# Rebuild services
docker compose down
docker compose up -d --build
```

#### 2. Database Issues

```bash
# Check database file
docker compose exec backend ls -la /app/app.db

# Reinitialize database
docker compose exec backend python init_database.py
docker compose exec backend python add_sample_data.py
```

#### 3. Port Conflicts

```bash
# Check port usage
sudo netstat -tlnp | grep -E ":(80|3000|8000)"

# Change ports in docker-compose.yml
ports:
  - "8080:8000"  # Change external port
```

#### 4. Memory Issues

```bash
# Check memory usage
docker stats

# Limit memory usage
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
```

### Useful Commands

```bash
# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Execute commands in containers
docker compose exec backend bash
docker compose exec frontend sh

# Restart services
docker compose restart backend
docker compose restart frontend

# Update services
docker compose pull
docker compose up -d

# Clean up
docker compose down
docker system prune -a
```

## 🔄 Updates and Maintenance

### Update Script

Create `update.sh`:

```bash
#!/bin/bash

echo "Updating Persian Chatbot..."

# Pull latest changes
git pull origin main

# Rebuild and restart services
docker compose down
docker compose up -d --build

# Wait for services to start
sleep 30

# Check health
curl -s http://localhost:8000/health

echo "Update completed!"
```

### Maintenance Tasks

```bash
# Daily maintenance
docker system prune -f

# Weekly maintenance
docker compose down
docker compose pull
docker compose up -d

# Monthly maintenance
docker system prune -a
```

---

## 🎉 Success!

Your Persian chatbot is now running in Docker containers!

**Access URLs:**
- Frontend: `http://your-domain.com`
- Backend API: `http://your-domain.com/api`
- Health Check: `http://your-domain.com/health`

**Next Steps:**
1. Set up SSL certificate
2. Configure domain name
3. Set up monitoring
4. Configure backups
5. Optimize performance

