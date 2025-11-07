# Complete Cloud Server Setup - Next Steps

## ✅ Step 1: Verify Server is Running

```bash
# Check if process is running
ps aux | grep uvicorn

# Check port
netstat -tuln | grep 8002

# Test the API
curl http://localhost:8002/health
curl http://localhost:8002/docs
```

## 🔑 Step 2: Set Up Environment Variables

Create a `.env` file in the backend directory:

```bash
cd ~/chatbot2/backend
nano .env
```

Add your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
PORT=8002
HOST=0.0.0.0
```

Save and exit (Ctrl+X, then Y, then Enter)

## 🔥 Step 3: Configure Firewall (if needed)

Allow access to port 8002:

```bash
# For UFW (Ubuntu)
sudo ufw allow 8002/tcp
sudo ufw status

# For firewalld (CentOS/RHEL)
sudo firewall-cmd --permanent --add-port=8002/tcp
sudo firewall-cmd --reload
```

## 🌐 Step 4: Get Your Server IP

```bash
# Get your server's public IP
curl ifconfig.me
# OR
hostname -I
```

## 🚀 Step 5: Set Up Process Management (PM2) - Recommended

For production, use PM2 to keep the server running:

```bash
# Install PM2 globally
npm install -g pm2

# Navigate to backend
cd ~/chatbot2/backend
source venv/bin/activate

# Stop any running uvicorn process
pkill -f uvicorn

# Start with PM2
pm2 start "uvicorn app:app --host 0.0.0.0 --port 8002" --name chatbot-backend

# Save PM2 configuration
pm2 save

# Set PM2 to start on server boot
pm2 startup
# (Follow the instructions it gives you)

# Useful PM2 commands:
# pm2 status          - Check status
# pm2 logs chatbot-backend - View logs
# pm2 restart chatbot-backend - Restart
# pm2 stop chatbot-backend - Stop
# pm2 monit           - Monitor
```

## 📱 Step 6: Test Your Chatbot

Access your chatbot:
- **API**: `http://YOUR-SERVER-IP:8002`
- **API Docs**: `http://YOUR-SERVER-IP:8002/docs`
- **Health**: `http://YOUR-SERVER-IP:8002/health`

Test with curl:
```bash
curl -X POST http://localhost:8002/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "سلام"}'
```

## 🎨 Step 7: Set Up Frontend (Optional)

If you want to serve the frontend too:

```bash
cd ~/chatbot2/frontend
npm install
npm run build

# Start frontend (in another terminal or with PM2)
npm start
```

## 📊 Step 8: Monitor Your Server

```bash
# View logs
tail -f ~/chatbot2/backend.log

# Check server status
pm2 status  # if using PM2
# OR
ps aux | grep uvicorn
```

## 🔄 Step 9: Set Up Auto-Restart (if not using PM2)

Create a systemd service for auto-restart:

```bash
sudo nano /etc/systemd/system/chatbot.service
```

Add:
```ini
[Unit]
Description=Chatbot Backend Service
After=network.target

[Service]
Type=simple
User=chatbot
WorkingDirectory=/home/chatbot/chatbot2/backend
Environment="PATH=/home/chatbot/chatbot2/backend/venv/bin"
ExecStart=/home/chatbot/chatbot2/backend/venv/bin/uvicorn app:app --host 0.0.0.0 --port 8002
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable chatbot
sudo systemctl start chatbot
sudo systemctl status chatbot
```



