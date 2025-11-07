# Final Steps - Complete Cloud Server Setup

## ✅ Step 1: Restart Server to Load API Key

```bash
# Stop current server
pkill -f uvicorn

# Navigate to backend
cd ~/chatbot2/backend
source venv/bin/activate

# Start server again (loads .env file)
nohup uvicorn app:app --host 0.0.0.0 --port 8002 --workers 1 > ../backend.log 2>&1 &

# Verify it's running
ps aux | grep uvicorn
```

## ✅ Step 2: Test the Chatbot

```bash
# Test health endpoint
curl http://localhost:8002/health

# Test chat endpoint
curl -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "سلام"}'
```

## ✅ Step 3: Get Your Server's Public IP

```bash
curl ifconfig.me
# OR
hostname -I
```

## ✅ Step 4: Configure Firewall

```bash
# Allow port 8002
sudo ufw allow 8002/tcp
sudo ufw status

# If using firewalld (CentOS/RHEL):
# sudo firewall-cmd --permanent --add-port=8002/tcp
# sudo firewall-cmd --reload
```

## ✅ Step 5: Access Your Chatbot

Once firewall is configured, access from anywhere:
- **API**: `http://YOUR-SERVER-IP:8002`
- **API Docs**: `http://YOUR-SERVER-IP:8002/docs`
- **Health Check**: `http://YOUR-SERVER-IP:8002/health`

## 🚀 Step 6: Set Up PM2 (Production - Recommended)

For auto-restart and better process management:

```bash
# Install PM2
npm install -g pm2

# Stop current server
pkill -f uvicorn

# Start with PM2
cd ~/chatbot2/backend
source venv/bin/activate
pm2 start "uvicorn app:app --host 0.0.0.0 --port 8002" --name chatbot-backend --interpreter venv/bin/python3

# Save PM2 configuration
pm2 save

# Set PM2 to start on server reboot
pm2 startup
# (Follow the instructions it gives you)

# Useful PM2 commands:
pm2 status              # Check status
pm2 logs chatbot-backend # View logs
pm2 restart chatbot-backend # Restart
pm2 monit               # Monitor dashboard
```

## 📊 Step 7: Monitor Your Server

```bash
# View logs
tail -f ~/chatbot2/backend.log

# Check server status
pm2 status  # if using PM2
# OR
ps aux | grep uvicorn
```

## 🔒 Security Notes

1. ✅ API key is in `.env` file (not in code)
2. ✅ `.env` is in `.gitignore` (won't be committed)
3. ⚠️ Make sure firewall is configured
4. ⚠️ Consider using HTTPS in production (nginx reverse proxy)

## 🎉 You're Done!

Your chatbot is now running on the cloud server and accessible from anywhere!

