# 🚀 PM2 Deployment Guide for Persian Chatbot

Complete PM2-based deployment guide for your Persian chatbot application.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [PM2 Setup](#pm2-setup)
3. [Configuration](#configuration)
4. [Production Deployment](#production-deployment)
5. [Process Management](#process-management)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)
8. [Maintenance](#maintenance)

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- PM2 (will be installed automatically)
- OpenAI API Key

### One-Command Deployment

```bash
# Clone and setup
git clone https://github.com/your-username/chatbot2.git
cd chatbot2
npm run setup
cp backend/env.example .env
# Edit .env with your API key
npm start
```

## 🔧 PM2 Setup

### Step 1: Install PM2

```bash
# Install PM2 globally
npm install -g pm2

# Install PM2 log rotation
pm2 install pm2-logrotate

# Verify installation
pm2 --version
```

### Step 2: Setup Log Rotation

```bash
# Configure log rotation
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 30
pm2 set pm2-logrotate:compress true
pm2 set pm2-logrotate:dateFormat YYYY-MM-DD_HH-mm-ss
pm2 set pm2-logrotate:workerInterval 30
pm2 set pm2-logrotate:rotateInterval 0 0 * * *
pm2 set pm2-logrotate:rotateModule true
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

# PM2 Configuration
NODE_ENV=production
```

### PM2 Ecosystem Configuration

Your `ecosystem.config.js` includes:

- **Backend Process**: FastAPI application with auto-restart
- **Frontend Process**: Next.js application with auto-restart
- **Log Management**: Centralized logging with rotation
- **Memory Management**: Automatic restart on memory limits
- **Health Monitoring**: Built-in health checks

## 🏗️ Production Deployment

### Step 1: Prepare Environment

```bash
# Install dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# Create logs directory
mkdir -p logs

# Set up environment
cp backend/env.example .env
# Edit .env with your configuration
```

### Step 2: Start Services

```bash
# Start all services in production mode
npm start

# Or start in development mode
npm run start:dev

# Check status
npm run status
```

### Step 3: Save PM2 Configuration

```bash
# Save current PM2 configuration
pm2 save

# Setup PM2 to start on system boot
pm2 startup

# Follow the instructions provided by pm2 startup
```

## 🔄 Process Management

### Basic Commands

```bash
# Start services
npm start                    # Production mode
npm run start:dev           # Development mode

# Stop services
npm run stop                # Stop all processes
pm2 stop chatbot-backend    # Stop specific process
pm2 stop chatbot-frontend   # Stop specific process

# Restart services
npm run restart             # Restart all processes
pm2 restart chatbot-backend # Restart specific process

# Reload services (zero-downtime)
npm run reload              # Reload all processes
pm2 reload chatbot-backend  # Reload specific process

# Delete processes
npm run delete              # Delete all processes
pm2 delete chatbot-backend  # Delete specific process
```

### Advanced Process Management

```bash
# Scale processes
pm2 scale chatbot-backend 2    # Scale backend to 2 instances
pm2 scale chatbot-frontend 1   # Scale frontend to 1 instance

# Process information
pm2 show chatbot-backend       # Detailed info about backend
pm2 show chatbot-frontend      # Detailed info about frontend

# Process monitoring
pm2 monit                      # Real-time monitoring dashboard
pm2 jlist                      # JSON list of all processes
```

## 📊 Monitoring

### Health Checks

```bash
# Check all services status
npm run status

# Check specific service health
curl http://localhost:8000/health
curl http://localhost:3000

# View logs
npm run logs                   # All logs
npm run logs:backend          # Backend logs only
npm run logs:frontend         # Frontend logs only

# Real-time monitoring
npm run monitor               # PM2 monitoring dashboard
```

### Log Management

```bash
# View logs
pm2 logs                      # All logs
pm2 logs chatbot-backend      # Backend logs
pm2 logs chatbot-frontend     # Frontend logs
pm2 logs --lines 100          # Last 100 lines

# Clear logs
pm2 flush                     # Clear all logs
pm2 flush chatbot-backend     # Clear specific logs

# Log rotation status
pm2 show pm2-logrotate
```

### Performance Monitoring

```bash
# System resources
pm2 monit                     # Real-time dashboard
pm2 jlist | jq '.[] | {name, cpu, memory}'  # Resource usage

# Process details
pm2 show chatbot-backend | grep -E "(cpu|memory|uptime|restarts)"
```

## 🆘 Troubleshooting

### Common Issues

#### 1. Services Won't Start

```bash
# Check PM2 status
pm2 status

# Check logs for errors
pm2 logs --err

# Check configuration
pm2 show chatbot-backend

# Restart with fresh configuration
pm2 delete all
npm start
```

#### 2. Memory Issues

```bash
# Check memory usage
pm2 monit

# Restart high memory processes
pm2 restart chatbot-backend

# Adjust memory limits in ecosystem.config.js
max_memory_restart: '2G'  # Increase limit
```

#### 3. Port Conflicts

```bash
# Check port usage
netstat -tlnp | grep -E ":(80|3000|8000)"
lsof -i :8000
lsof -i :3000

# Kill processes using ports
sudo kill -9 $(lsof -t -i:8000)
sudo kill -9 $(lsof -t -i:3000)
```

#### 4. Log Issues

```bash
# Check log files
ls -la logs/

# Check log rotation
pm2 show pm2-logrotate

# Reinstall log rotation
pm2 uninstall pm2-logrotate
pm2 install pm2-logrotate
```

### Useful Commands

```bash
# Process management
pm2 list                      # List all processes
pm2 describe chatbot-backend  # Detailed process info
pm2 env 0                     # Environment variables for process 0

# System information
pm2 info                      # PM2 system info
pm2 ping                      # Test PM2 daemon
pm2 kill                      # Kill PM2 daemon

# Backup and restore
pm2 save                      # Save current configuration
pm2 resurrect                 # Restore saved configuration
```

## 🔄 Updates and Maintenance

### Update Script

Create `update.sh`:

```bash
#!/bin/bash

echo "Updating Persian Chatbot..."

# Pull latest changes
git pull origin main

# Install/update dependencies
pip install -r requirements.txt
cd frontend && npm install && cd ..

# Reload services (zero-downtime)
pm2 reload all

# Wait for services to start
sleep 10

# Check health
curl -s http://localhost:8000/health
curl -s http://localhost:3000

echo "Update completed!"
```

### Maintenance Tasks

```bash
# Daily maintenance
pm2 flush                     # Clear old logs
pm2 save                      # Save current state

# Weekly maintenance
pm2 restart all               # Restart all services
pm2 save                      # Save configuration

# Monthly maintenance
pm2 uninstall pm2-logrotate   # Reinstall log rotation
pm2 install pm2-logrotate
pm2 set pm2-logrotate:retain 30
```

### Backup Script

Create `backup.sh`:

```bash
#!/bin/bash

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PM2 configuration
pm2 save
cp ~/.pm2/dump.pm2 $BACKUP_DIR/pm2-config-$DATE.pm2

# Backup database
cp app.db $BACKUP_DIR/app-$DATE.db

# Backup vectorstore
tar -czf $BACKUP_DIR/vectorstore-$DATE.tar.gz vectorstore/

# Cleanup old backups (keep 7 days)
find $BACKUP_DIR -name "*.pm2" -mtime +7 -delete
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

## 🎯 Performance Optimization

### PM2 Configuration Tuning

```javascript
// ecosystem.config.js optimizations
{
  instances: 'max',           // Use all CPU cores
  exec_mode: 'cluster',       // Cluster mode for better performance
  max_memory_restart: '1G',   // Restart on memory limit
  node_args: '--max-old-space-size=1024',  // Node.js memory limit
  kill_timeout: 5000,         // Graceful shutdown timeout
  wait_ready: true,           // Wait for ready signal
  listen_timeout: 3000,       // Listen timeout
  restart_delay: 4000         // Delay between restarts
}
```

### System Optimization

```bash
# Increase file descriptor limits
ulimit -n 65536

# Optimize PM2 settings
pm2 set pm2-logrotate:max_size 50M
pm2 set pm2-logrotate:retain 7
pm2 set pm2-logrotate:compress true
```

## 🔐 Security Considerations

### Process Security

```bash
# Run PM2 as non-root user
sudo -u www-data pm2 start ecosystem.config.js

# Set proper file permissions
chmod 600 .env
chmod 755 logs/
chown -R www-data:www-data logs/
```

### Environment Security

```bash
# Secure environment file
chmod 600 .env
chown root:root .env

# Use environment-specific configurations
pm2 start ecosystem.config.js --env production
```

---

## 🎉 Success!

Your Persian chatbot is now running with PM2 process management!

**Access URLs:**
- Frontend: `http://your-domain.com:3000`
- Backend API: `http://your-domain.com:8000/api`
- Health Check: `http://your-domain.com:8000/health`

**Key Commands:**
- `npm start` - Start all services
- `npm run status` - Check service status
- `npm run logs` - View logs
- `npm run monitor` - Real-time monitoring
- `pm2 save` - Save configuration

**Next Steps:**
1. Set up SSL certificate
2. Configure domain name
3. Set up monitoring alerts
4. Configure automated backups
5. Optimize performance settings
