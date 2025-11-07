# Cloud Server Start Guide

## Quick Start Commands

### Option 1: Setup and Start (First Time)
```bash
# Make scripts executable
chmod +x setup_and_start_cloud.sh start_cloud_background.sh

# Run setup and start (foreground)
./setup_and_start_cloud.sh
```

### Option 2: Start in Background (After Setup)
```bash
# Start in background
./start_cloud_background.sh

# Or manually:
cd ~/chatbot2/backend
source venv/bin/activate
nohup uvicorn app:app --host 0.0.0.0 --port 8002 --workers 1 > ../backend.log 2>&1 &
```

### Option 3: Manual Step-by-Step

```bash
# 1. Navigate to project root
cd ~/chatbot2
# OR if your project is elsewhere:
cd /path/to/your/chatbot2

# 2. Go to backend directory
cd backend

# 3. Create virtual environment (first time only)
python3 -m venv venv

# 4. Activate virtual environment
source venv/bin/activate

# 5. Install dependencies (first time only)
pip install --upgrade pip
pip install -r requirements.txt
# OR if requirements.txt is in parent directory:
pip install -r ../requirements.txt

# 6. Create necessary directories
mkdir -p vectorstore logs __pycache__

# 7. Start the server
uvicorn app:app --host 0.0.0.0 --port 8002 --workers 1
```

## Troubleshooting

### Error: "cd: backend: No such file or directory"
**Solution:** You're not in the project root directory.
```bash
# Find your project
find ~ -name "app.py" -type f 2>/dev/null | grep backend
# OR
ls -la  # Check current directory contents
# Navigate to the correct location
cd /path/to/chatbot2
```

### Error: "venv/bin/activate: No such file or directory"
**Solution:** Virtual environment doesn't exist. Create it:
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### Error: "Module not found" or import errors
**Solution:** Install dependencies:
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

### Check if server is running
```bash
# Check processes
ps aux | grep uvicorn

# Check ports
netstat -tuln | grep 8002
# OR
lsof -i :8002

# Check logs
tail -f backend.log
```

### Stop the server
```bash
# Find the process
ps aux | grep uvicorn

# Kill by PID (replace XXXX with actual PID)
kill XXXX

# Or kill all uvicorn processes
pkill -f uvicorn
```

## Environment Variables

Set these before starting (optional):
```bash
export PORT=8002
export HOST=0.0.0.0
export OPENAI_API_KEY=your_api_key_here
```

Or create a `.env` file in the backend directory:
```
OPENAI_API_KEY=your_api_key_here
PORT=8002
HOST=0.0.0.0
```

## Access Your Chatbot

Once started, access:
- **API**: `http://your-server-ip:8002`
- **API Docs**: `http://your-server-ip:8002/docs`
- **Health Check**: `http://your-server-ip:8002/health`

## Using PM2 (Production Recommended)

```bash
# Install PM2
npm install -g pm2

# Start with PM2
cd ~/chatbot2
pm2 start ecosystem.config.js --env production

# Useful PM2 commands
pm2 status          # Check status
pm2 logs            # View logs
pm2 monit           # Monitor
pm2 stop all        # Stop all
pm2 restart all     # Restart all
pm2 save            # Save current processes
pm2 startup         # Auto-start on server reboot
```



