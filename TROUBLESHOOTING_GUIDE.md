# 🆘 Persian Chatbot Troubleshooting Guide

Complete troubleshooting guide for your Persian chatbot deployment issues.

## 📋 Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Common Issues](#common-issues)
3. [Docker Issues](#docker-issues)
4. [Manual Deployment Issues](#manual-deployment-issues)
5. [Database Issues](#database-issues)
6. [API Issues](#api-issues)
7. [Frontend Issues](#frontend-issues)
8. [Performance Issues](#performance-issues)
9. [Security Issues](#security-issues)
10. [Recovery Procedures](#recovery-procedures)

## 🔍 Quick Diagnostics

### Health Check Commands

```bash
# Check if services are running
docker-compose ps                    # Docker
sudo systemctl status chatbot-backend # Manual

# Test backend health
curl http://localhost:8000/health
curl http://localhost:8000/test-db

# Test frontend
curl http://localhost:3000
curl http://localhost

# Check logs
docker-compose logs -f backend       # Docker
sudo journalctl -u chatbot-backend -f # Manual
```

### System Status Check

```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check port usage
sudo netstat -tlnp | grep -E ":(80|3000|8000)"

# Check processes
ps aux | grep -E "(python|node|nginx)"
```

## 🚨 Common Issues

### 1. Services Won't Start

#### Symptoms
- Containers fail to start
- Systemd service shows failed status
- Port already in use errors

#### Solutions

**Docker:**
```bash
# Check what's using the port
sudo netstat -tlnp | grep :8000

# Kill process using port
sudo kill -9 $(sudo lsof -t -i:8000)

# Restart Docker services
docker-compose down
docker-compose up -d
```

**Manual:**
```bash
# Check systemd service status
sudo systemctl status chatbot-backend

# Check service logs
sudo journalctl -u chatbot-backend -n 50

# Restart service
sudo systemctl restart chatbot-backend
```

### 2. Database Connection Issues

#### Symptoms
- "Database connection failed" errors
- Empty responses from API
- SQLite file not found

#### Solutions

**Check database file:**
```bash
# Docker
docker-compose exec backend ls -la /app/app.db

# Manual
ls -la /opt/chatbot/backend/app.db
```

**Reinitialize database:**
```bash
# Docker
docker-compose exec backend python init_database.py
docker-compose exec backend python add_sample_data.py

# Manual
cd /opt/chatbot/backend
source ../venv/bin/activate
python init_database.py
python add_sample_data.py
```

**Fix permissions:**
```bash
# Docker
docker-compose exec backend chown -R app:app /app

# Manual
sudo chown -R $USER:$USER /opt/chatbot/backend
```

### 3. OpenAI API Issues

#### Symptoms
- "OpenAI API key not found" errors
- "Rate limit exceeded" errors
- Empty responses from chatbot

#### Solutions

**Check API key:**
```bash
# Check environment variable
echo $OPENAI_API_KEY

# Check .env file
grep OPENAI_API_KEY .env
```

**Test API key:**
```bash
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

**Fix API key:**
```bash
# Update .env file
nano .env
# Add: OPENAI_API_KEY=sk-your-actual-key-here

# Restart services
docker-compose restart backend  # Docker
sudo systemctl restart chatbot-backend  # Manual
```

### 4. CORS Issues

#### Symptoms
- "CORS policy" errors in browser console
- Frontend can't connect to backend
- 404 errors for API calls

#### Solutions

**Check CORS configuration:**
```python
# In backend/app.py, verify allow_origins includes your frontend URL
allow_origins=[
    "http://localhost:3000",
    "https://your-domain.com",
    "https://*.onrender.com",
]
```

**Update CORS settings:**
```bash
# Edit backend/app.py
nano backend/app.py

# Add your frontend URL to allow_origins
# Restart backend
docker-compose restart backend  # Docker
sudo systemctl restart chatbot-backend  # Manual
```

## 🐳 Docker Issues

### 1. Container Build Failures

#### Symptoms
- "Build failed" errors
- Missing dependencies
- Permission denied errors

#### Solutions

**Clean build:**
```bash
# Remove all containers and images
docker-compose down
docker system prune -a

# Rebuild from scratch
docker-compose up -d --build --force-recreate
```

**Check Dockerfile:**
```bash
# Test Dockerfile locally
docker build -t test-backend ./backend
docker run -p 8000:8000 test-backend
```

**Fix permissions:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x *.sh
```

### 2. Volume Mount Issues

#### Symptoms
- Database not persisting
- Vector store not found
- Permission denied on volumes

#### Solutions

**Check volume mounts:**
```bash
# List volumes
docker volume ls

# Inspect volume
docker volume inspect chatbot2_backend_data
```

**Fix volume permissions:**
```bash
# Create volumes with correct permissions
docker-compose down
docker volume rm chatbot2_backend_data
docker-compose up -d
```

### 3. Network Issues

#### Symptoms
- Containers can't communicate
- "Connection refused" errors
- DNS resolution failures

#### Solutions

**Check network:**
```bash
# List networks
docker network ls

# Inspect network
docker network inspect chatbot2_default
```

**Recreate network:**
```bash
# Remove and recreate
docker-compose down
docker network prune
docker-compose up -d
```

## 🛠️ Manual Deployment Issues

### 1. Python Environment Issues

#### Symptoms
- "Module not found" errors
- Virtual environment not activated
- Wrong Python version

#### Solutions

**Check Python version:**
```bash
python3 --version
which python3
```

**Recreate virtual environment:**
```bash
cd /opt/chatbot
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

**Fix Python path:**
```bash
# Update systemd service
sudo nano /etc/systemd/system/chatbot-backend.service

# Ensure correct Python path
Environment=PATH=/opt/chatbot/venv/bin
ExecStart=/opt/chatbot/venv/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

### 2. Node.js Issues

#### Symptoms
- "Command not found: npm" errors
- Build failures
- Module not found errors

#### Solutions

**Check Node.js version:**
```bash
node --version
npm --version
```

**Reinstall Node.js:**
```bash
# Remove old version
sudo apt remove nodejs npm

# Install latest version
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs
```

**Rebuild frontend:**
```bash
cd /opt/chatbot/frontend
rm -rf node_modules .next
npm install
npm run build
```

### 3. Nginx Issues

#### Symptoms
- "502 Bad Gateway" errors
- Nginx won't start
- Configuration errors

#### Solutions

**Check Nginx status:**
```bash
sudo systemctl status nginx
sudo nginx -t
```

**Fix configuration:**
```bash
# Test configuration
sudo nginx -t

# If errors, check syntax
sudo nano /etc/nginx/sites-available/chatbot

# Reload Nginx
sudo systemctl reload nginx
```

**Check logs:**
```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

## 🗄️ Database Issues

### 1. SQLite Corruption

#### Symptoms
- "Database is locked" errors
- "Database disk image is malformed" errors
- Data not persisting

#### Solutions

**Check database integrity:**
```bash
# Docker
docker-compose exec backend sqlite3 /app/app.db "PRAGMA integrity_check;"

# Manual
sqlite3 /opt/chatbot/backend/app.db "PRAGMA integrity_check;"
```

**Repair database:**
```bash
# Create backup
cp app.db app.db.backup

# Try to repair
sqlite3 app.db ".dump" | sqlite3 app_repaired.db
mv app_repaired.db app.db
```

**Recreate database:**
```bash
# Remove old database
rm app.db

# Reinitialize
python init_database.py
python add_sample_data.py
```

### 2. Migration Issues

#### Symptoms
- "Table doesn't exist" errors
- Schema mismatch errors
- Data loss

#### Solutions

**Check database schema:**
```bash
sqlite3 app.db ".schema"
```

**Reset database:**
```bash
# Backup data first
cp app.db app.db.backup

# Remove and recreate
rm app.db
python init_database.py
python add_sample_data.py
```

## 🔌 API Issues

### 1. Endpoint Not Found

#### Symptoms
- 404 errors for API calls
- "Route not found" errors
- Empty responses

#### Solutions

**Check API routes:**
```bash
# List available routes
curl http://localhost:8000/docs

# Test specific endpoint
curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "test"}'
```

**Check router configuration:**
```python
# In backend/app.py, verify routers are included
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(faqs.router, prefix="/api", tags=["faqs"])
app.include_router(logs.router, prefix="/api", tags=["logs"])
```

### 2. Authentication Issues

#### Symptoms
- "Unauthorized" errors
- API key not working
- Permission denied

#### Solutions

**Check API key configuration:**
```bash
# Verify API key is set
grep OPENAI_API_KEY .env

# Test API key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

**Update API key:**
```bash
# Edit .env file
nano .env

# Restart services
docker-compose restart backend  # Docker
sudo systemctl restart chatbot-backend  # Manual
```

## 🎨 Frontend Issues

### 1. Build Failures

#### Symptoms
- "Build failed" errors
- Missing dependencies
- TypeScript errors

#### Solutions

**Clean and rebuild:**
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run build
```

**Check Node.js version:**
```bash
node --version  # Should be 16+
npm --version
```

**Fix TypeScript errors:**
```bash
# Check TypeScript configuration
npx tsc --noEmit

# Fix any type errors
npm run build
```

### 2. Runtime Errors

#### Symptoms
- White screen of death
- JavaScript errors in console
- API calls failing

#### Solutions

**Check browser console:**
- Open Developer Tools (F12)
- Check Console tab for errors
- Check Network tab for failed requests

**Test API connectivity:**
```bash
# Test from frontend
curl http://localhost:8000/api/health

# Test from browser
# Open: http://localhost:8000/health
```

**Check environment variables:**
```bash
# Verify NEXT_PUBLIC_API_URL is set
echo $NEXT_PUBLIC_API_URL

# Check .env.local file
cat frontend/.env.local
```

## ⚡ Performance Issues

### 1. Slow Response Times

#### Symptoms
- Long loading times
- Timeout errors
- High CPU usage

#### Solutions

**Check system resources:**
```bash
# Check CPU usage
top

# Check memory usage
free -h

# Check disk I/O
iostat -x 1
```

**Optimize database:**
```sql
-- Add indexes
CREATE INDEX idx_faq_question ON faqs(question);
CREATE INDEX idx_log_timestamp ON logs(timestamp);

-- Analyze query performance
EXPLAIN QUERY PLAN SELECT * FROM faqs WHERE question LIKE '%test%';
```

**Optimize Nginx:**
```nginx
# Add to nginx.conf
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# Add caching
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 2. Memory Leaks

#### Symptoms
- Increasing memory usage
- System becomes unresponsive
- Out of memory errors

#### Solutions

**Monitor memory usage:**
```bash
# Check memory usage over time
watch -n 1 'free -h'

# Check process memory
ps aux --sort=-%mem | head -10
```

**Restart services:**
```bash
# Docker
docker-compose restart backend

# Manual
sudo systemctl restart chatbot-backend
```

**Check for memory leaks:**
```python
# Add memory monitoring to backend
import psutil
import os

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB
```

## 🔒 Security Issues

### 1. SSL Certificate Issues

#### Symptoms
- "Not secure" warnings
- Certificate errors
- HTTPS not working

#### Solutions

**Check certificate status:**
```bash
# Check certificate
openssl x509 -in /etc/letsencrypt/live/your-domain.com/cert.pem -text -noout

# Test SSL
curl -I https://your-domain.com
```

**Renew certificate:**
```bash
# Test renewal
sudo certbot renew --dry-run

# Renew certificate
sudo certbot renew
```

**Fix certificate configuration:**
```nginx
# Update Nginx configuration
ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
```

### 2. Firewall Issues

#### Symptoms
- Can't access from outside
- Connection refused
- Port not open

#### Solutions

**Check firewall status:**
```bash
# Check UFW status
sudo ufw status

# Check iptables
sudo iptables -L
```

**Open required ports:**
```bash
# Open HTTP and HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Open SSH (if needed)
sudo ufw allow 22

# Enable firewall
sudo ufw enable
```

## 🔄 Recovery Procedures

### 1. Complete System Recovery

#### When to use
- System is completely broken
- Data corruption
- Security breach

#### Steps

**Backup current state:**
```bash
# Create backup directory
mkdir -p /opt/backups/$(date +%Y%m%d)

# Backup database
cp app.db /opt/backups/$(date +%Y%m%d)/

# Backup configuration
cp .env /opt/backups/$(date +%Y%m%d)/
cp docker-compose.yml /opt/backups/$(date +%Y%m%d)/
```

**Clean installation:**
```bash
# Stop all services
docker-compose down  # Docker
sudo systemctl stop chatbot-backend nginx  # Manual

# Remove old installation
rm -rf /opt/chatbot  # Manual
rm -rf .  # Docker

# Fresh installation
git clone https://github.com/your-username/chatbot2.git
cd chatbot2
# Follow deployment guide
```

### 2. Database Recovery

#### When to use
- Database corruption
- Data loss
- Migration issues

#### Steps

**Stop services:**
```bash
docker-compose stop backend  # Docker
sudo systemctl stop chatbot-backend  # Manual
```

**Backup current database:**
```bash
cp app.db app.db.backup.$(date +%Y%m%d_%H%M%S)
```

**Restore from backup:**
```bash
# Find latest backup
ls -la backups/

# Restore database
cp backups/app_YYYYMMDD_HHMMSS.db app.db
```

**Reinitialize if needed:**
```bash
rm app.db
python init_database.py
python add_sample_data.py
```

### 3. Service Recovery

#### When to use
- Service won't start
- Configuration errors
- Dependency issues

#### Steps

**Check service status:**
```bash
# Docker
docker-compose ps
docker-compose logs

# Manual
sudo systemctl status chatbot-backend
sudo journalctl -u chatbot-backend -n 50
```

**Restart services:**
```bash
# Docker
docker-compose restart

# Manual
sudo systemctl restart chatbot-backend
sudo systemctl restart nginx
```

**Recreate services:**
```bash
# Docker
docker-compose down
docker-compose up -d --build

# Manual
sudo systemctl stop chatbot-backend
sudo systemctl disable chatbot-backend
# Recreate systemd service
sudo systemctl enable chatbot-backend
sudo systemctl start chatbot-backend
```

## 📞 Getting Help

### Log Files to Check

**Docker:**
- `docker-compose logs backend`
- `docker-compose logs frontend`
- `docker-compose logs nginx`

**Manual:**
- `sudo journalctl -u chatbot-backend`
- `/var/log/nginx/error.log`
- `/var/log/nginx/access.log`

### Information to Provide

When asking for help, include:

1. **Error messages** (exact text)
2. **Log files** (relevant sections)
3. **System information** (`uname -a`, `docker --version`)
4. **Configuration** (relevant parts of config files)
5. **Steps to reproduce** the issue

### Useful Commands

```bash
# System information
uname -a
docker --version
python3 --version
node --version

# Service status
docker-compose ps
sudo systemctl status chatbot-backend

# Resource usage
free -h
df -h
top

# Network
sudo netstat -tlnp
curl -I http://localhost:8000/health
```

---

## 🎯 Quick Fix Checklist

When something goes wrong, try these in order:

1. ✅ **Check service status** - Are services running?
2. ✅ **Check logs** - What errors are showing?
3. ✅ **Check resources** - Enough memory/disk space?
4. ✅ **Check configuration** - Are settings correct?
5. ✅ **Restart services** - Simple restart often fixes issues
6. ✅ **Check dependencies** - Are all packages installed?
7. ✅ **Check permissions** - Are files accessible?
8. ✅ **Check network** - Can services communicate?
9. ✅ **Check database** - Is data accessible?
10. ✅ **Check API keys** - Are credentials valid?

If none of these work, follow the detailed recovery procedures above.

