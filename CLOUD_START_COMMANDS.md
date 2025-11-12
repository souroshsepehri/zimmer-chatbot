# Cloud Server Startup Commands

## Quick Start Commands

### Option 1: Start Both Backend and Frontend Together (Recommended)

```bash
cd ~/chatbot2
chmod +x start_both_cloud.sh
./start_both_cloud.sh
```

This script will:
- Start backend on port **8001**
- Start frontend on port **8000**
- Use PM2 if available, otherwise use nohup

### Option 2: Start Backend Only

```bash
cd ~/chatbot2/backend
source venv/bin/activate
nohup uvicorn app:app --host 0.0.0.0 --port 8001 --workers 1 > ../backend.log 2>&1 &
```

Or using the background script:
```bash
cd ~/chatbot2
chmod +x start_cloud_background.sh
./start_cloud_background.sh
```

### Option 3: Start Frontend Only

```bash
cd ~/chatbot2/frontend
npm install  # First time only
nohup npm run dev > ../frontend.log 2>&1 &
```

### Option 4: Using PM2 (Recommended for Production)

```bash
cd ~/chatbot2
chmod +x start_both_pm2.sh
./start_both_pm2.sh
```

## Manual Commands

### Start Backend Manually

```bash
# Navigate to backend
cd ~/chatbot2/backend

# Activate virtual environment
source venv/bin/activate

# Start backend server
uvicorn app:app --host 0.0.0.0 --port 8001 --workers 1
```

For background execution:
```bash
nohup uvicorn app:app --host 0.0.0.0 --port 8001 --workers 1 > ../backend.log 2>&1 &
```

### Start Frontend Manually

```bash
# Navigate to frontend
cd ~/chatbot2/frontend

# Install dependencies (first time only)
npm install

# Start frontend server
npm run dev
```

For background execution:
```bash
nohup npm run dev > ../frontend.log 2>&1 &
```

## Access URLs

After starting, access your services at:

- **Backend API**: `http://YOUR-SERVER-IP:8001`
- **API Documentation**: `http://YOUR-SERVER-IP:8001/docs`
- **Health Check**: `http://YOUR-SERVER-IP:8001/health`
- **Frontend**: `http://YOUR-SERVER-IP:8000`
- **Admin Panel**: `http://YOUR-SERVER-IP:8000/admin`

## Check Server Status

```bash
# Check if backend is running
curl http://localhost:8001/health

# Check if frontend is running
curl http://localhost:8000

# Check processes
ps aux | grep uvicorn
ps aux | grep "npm run dev"

# Check ports
netstat -tuln | grep 8001
netstat -tuln | grep 8000
```

## View Logs

```bash
# Backend logs
tail -f ~/chatbot2/backend.log

# Frontend logs
tail -f ~/chatbot2/frontend.log

# If using PM2
pm2 logs chatbot-backend
pm2 logs chatbot-frontend
```

## Stop Servers

```bash
# Stop backend
pkill -f uvicorn

# Stop frontend
pkill -f "npm run dev"

# If using PM2
pm2 stop all
pm2 delete all
```

## Environment Variables

Make sure your `.env` file in `backend/` directory has:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small
```

## Firewall Configuration

Make sure ports 8000 and 3000 are open:

```bash
# For UFW
sudo ufw allow 8001/tcp
sudo ufw allow 8000/tcp

# For Google Cloud
# Add firewall rules in Google Cloud Console for ports 8000 and 3000
```

## Troubleshooting

### Port Already in Use

```bash
# Find what's using port 8000
lsof -i :8001

# Kill the process
kill -9 <PID>
```

### Module Not Found Errors

```bash
# Reinstall backend dependencies
cd ~/chatbot2/backend
source venv/bin/activate
pip install -r requirements.txt

# Reinstall frontend dependencies
cd ~/chatbot2/frontend
npm install
```

### Check Server IP

```bash
hostname -I
# or
curl ifconfig.me
```

