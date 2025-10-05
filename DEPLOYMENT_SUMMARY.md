# 📚 Persian Chatbot Deployment Documentation Summary

Complete deployment documentation for your Persian chatbot application.

## 📁 Documentation Files

### Main Guides
- **`SERVER_DEPLOYMENT_GUIDE.md`** - Complete server deployment guide
- **`DOCKER_DEPLOYMENT_GUIDE.md`** - Docker-specific deployment guide
- **`TROUBLESHOOTING_GUIDE.md`** - Comprehensive troubleshooting guide

### Deployment Scripts
- **`deploy-server.sh`** - Linux/macOS Docker deployment script
- **`deploy-server.bat`** - Windows Docker deployment script
- **`deploy-manual.sh`** - Linux manual server setup script

## 🚀 Quick Start Options

### Option 1: Docker Deployment (Recommended)
```bash
# Linux/macOS
chmod +x deploy-server.sh
./deploy-server.sh

# Windows
deploy-server.bat
```

### Option 2: Manual Server Setup
```bash
# Linux only
chmod +x deploy-manual.sh
./deploy-manual.sh
```

### Option 3: Step-by-Step Manual
Follow the detailed guides in `SERVER_DEPLOYMENT_GUIDE.md`

## 🎯 What You Get

### Application Features
- **Persian Chatbot** with OpenAI GPT-4 integration
- **FAQ Management System** with admin panel
- **Semantic Search** using vector embeddings
- **Logging System** for monitoring and analytics
- **Responsive Web Interface** in Persian/Farsi

### Technical Stack
- **Backend**: FastAPI (Python 3.9+)
- **Frontend**: Next.js (React)
- **Database**: SQLite (with PostgreSQL option)
- **AI**: OpenAI GPT-4 + Embeddings
- **Vector Store**: FAISS
- **Web Server**: Nginx
- **Containerization**: Docker & Docker Compose

## 📋 Prerequisites

### Required
- **OpenAI API Key** - Get from [OpenAI Platform](https://platform.openai.com)
- **Server** - Ubuntu 20.04+, CentOS 8+, or Windows 10+
- **Docker** - 20.10+ (for Docker deployment)
- **Git** - For cloning repository

### Optional
- **Domain Name** - For production deployment
- **SSL Certificate** - Let's Encrypt recommended
- **PostgreSQL** - For production database

## 🔧 Configuration

### Environment Variables
Create `.env` file with:
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
DATABASE_URL=sqlite:///./app.db
VECTORSTORE_PATH=./vectorstore
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Ports Used
- **8000** - Backend API
- **3000** - Frontend (development)
- **80** - Nginx (production)
- **443** - HTTPS (production)

## 🚀 Deployment Methods

### 1. Docker Deployment (Easiest)
- ✅ One-command deployment
- ✅ Consistent environment
- ✅ Easy updates and maintenance
- ✅ Built-in process management

**Commands:**
```bash
# Linux/macOS
./deploy-server.sh

# Windows
deploy-server.bat
```

### 2. Manual Server Setup
- ✅ Full control over environment
- ✅ Better for custom configurations
- ✅ Direct access to logs and files

**Commands:**
```bash
# Linux only
./deploy-manual.sh
```

### 3. Cloud Deployment
- **Render.com** - See `RENDER_DEPLOYMENT_GUIDE.md`
- **Vercel** - See `VERCEL_DEPLOYMENT_GUIDE.md`
- **AWS/GCP/Azure** - Follow `SERVER_DEPLOYMENT_GUIDE.md`

## 📊 Management Commands

### Docker Deployment
```bash
# Start services
./start-chatbot.sh

# Stop services
./stop-chatbot.sh

# Restart services
./restart-chatbot.sh

# Update application
./update-chatbot.sh

# Backup data
./backup-chatbot.sh

# View logs
docker-compose logs -f
```

### Manual Deployment
```bash
# Start services
sudo systemctl start chatbot-backend nginx

# Stop services
sudo systemctl stop chatbot-backend nginx

# Restart services
sudo systemctl restart chatbot-backend nginx

# Check status
sudo systemctl status chatbot-backend

# View logs
sudo journalctl -u chatbot-backend -f
```

## 🔍 Health Checks

### Backend Health
```bash
curl http://localhost:8000/health
curl http://localhost:8000/test-db
```

### Frontend Health
```bash
curl http://localhost:3000
curl http://localhost  # With Nginx
```

### Full System Check
```bash
# Check all services
docker-compose ps  # Docker
sudo systemctl status chatbot-backend nginx  # Manual

# Check resources
free -h
df -h
```

## 🆘 Troubleshooting

### Common Issues
1. **Services won't start** - Check logs and port conflicts
2. **Database issues** - Reinitialize database
3. **API errors** - Check OpenAI API key
4. **CORS errors** - Update CORS settings
5. **Build failures** - Check dependencies and versions

### Quick Fixes
```bash
# Restart everything
docker-compose down && docker-compose up -d  # Docker
sudo systemctl restart chatbot-backend nginx  # Manual

# Check logs
docker-compose logs -f  # Docker
sudo journalctl -u chatbot-backend -f  # Manual

# Rebuild
docker-compose up -d --build  # Docker
```

### Detailed Troubleshooting
See `TROUBLESHOOTING_GUIDE.md` for comprehensive solutions.

## 📈 Performance Optimization

### Database Optimization
```sql
-- Add indexes
CREATE INDEX idx_faq_question ON faqs(question);
CREATE INDEX idx_log_timestamp ON logs(timestamp);
```

### Nginx Optimization
```nginx
# Enable gzip compression
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# Add caching
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### System Optimization
```bash
# Increase file limits
echo "* soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "* hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize kernel parameters
echo "net.core.somaxconn = 65536" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## 🔒 Security Considerations

### SSL/HTTPS Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com
```

### Firewall Configuration
```bash
# Open required ports
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22  # SSH

# Enable firewall
sudo ufw enable
```

### Environment Security
- Store API keys in environment variables
- Use strong passwords for database
- Regular security updates
- Monitor access logs

## 📊 Monitoring and Maintenance

### Log Management
```bash
# Backend logs
docker-compose logs -f backend  # Docker
sudo journalctl -u chatbot-backend -f  # Manual

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Backup Strategy
```bash
# Daily backup
./backup-chatbot.sh  # Docker
/opt/chatbot/backup-chatbot.sh  # Manual

# Automated backup (cron)
0 2 * * * /path/to/backup-chatbot.sh
```

### Update Strategy
```bash
# Update application
./update-chatbot.sh  # Docker
/opt/chatbot/update-chatbot.sh  # Manual

# Update system
sudo apt update && sudo apt upgrade  # Ubuntu/Debian
sudo yum update  # CentOS/RHEL
```

## 📞 Support and Resources

### Documentation
- **Main Guide**: `SERVER_DEPLOYMENT_GUIDE.md`
- **Docker Guide**: `DOCKER_DEPLOYMENT_GUIDE.md`
- **Troubleshooting**: `TROUBLESHOOTING_GUIDE.md`

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

### Getting Help
When asking for help, include:
1. **Error messages** (exact text)
2. **Log files** (relevant sections)
3. **System information** (OS, versions)
4. **Configuration** (relevant config files)
5. **Steps to reproduce** the issue

## 🎉 Success!

After successful deployment, you'll have:

- **Frontend**: Accessible at `http://localhost:3000` or `http://your-domain.com`
- **Backend API**: Available at `http://localhost:8000/api`
- **Health Check**: `http://localhost:8000/health`
- **Admin Panel**: `http://localhost:3000/admin`

### Next Steps
1. ✅ Test all functionality
2. ✅ Set up monitoring
3. ✅ Configure backups
4. ✅ Set up SSL certificate
5. ✅ Optimize performance
6. ✅ Set up domain name

---

## 📝 Quick Reference

### Essential Commands
```bash
# Deploy
./deploy-server.sh  # Linux/macOS
deploy-server.bat   # Windows

# Manage
./start-chatbot.sh
./stop-chatbot.sh
./restart-chatbot.sh

# Monitor
docker-compose logs -f
curl http://localhost:8000/health

# Backup
./backup-chatbot.sh
```

### Important Files
- `.env` - Environment configuration
- `docker-compose.yml` - Docker services
- `backend/app.py` - Main application
- `frontend/package.json` - Frontend dependencies

### Key URLs
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Health: `http://localhost:8000/health`
- API Docs: `http://localhost:8000/docs`

Your Persian chatbot is now ready for production! 🚀

