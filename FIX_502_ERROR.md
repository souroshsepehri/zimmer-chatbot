# Fix 502 Error - API URL Configuration

## Problem
When accessing the frontend via server IP (e.g., `http://193.162.129.249:8000`), the browser tries to connect to `localhost:8001`, which fails because `localhost` refers to the user's computer, not the server.

## Solution
The frontend now dynamically detects the hostname and uses it for API calls.

## Quick Fix on Server

### Option 1: Set Environment Variable (Recommended)

```bash
cd ~/chatbot2/frontend

# Create .env.local file with your server IP
echo "NEXT_PUBLIC_API_URL=http://193.162.129.249:8001/api" > .env.local

# Or use dynamic hostname (better)
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://$(hostname -I | awk '{print $1}'):8001/api
EOF

# Restart frontend
pkill -f "npm run dev"
rm -rf .next
nohup npm run dev > ../frontend.log 2>&1 &
```

### Option 2: Pull Latest Code (Code is already fixed)

```bash
cd ~/chatbot2
git pull origin main

# Restart frontend
cd frontend
pkill -f "npm run dev"
rm -rf .next
nohup npm run dev > ../frontend.log 2>&1 &
```

## Verify Backend is Running

```bash
# Check backend
ps aux | grep uvicorn
curl http://localhost:8001/health

# If not running, start it:
cd ~/chatbot2/backend
source venv/bin/activate
nohup uvicorn app:app --host 0.0.0.0 --port 8001 --workers 1 > ../backend.log 2>&1 &
```

## Check Firewall

```bash
# Make sure ports are open
sudo ufw status
sudo ufw allow 8000/tcp
sudo ufw allow 8001/tcp

# For Google Cloud, add firewall rules in console
```

## Test

```bash
# From server
curl http://localhost:8001/health
curl http://localhost:8000

# From your computer browser
# http://193.162.129.249:8000
# http://193.162.129.249:8001/health
```

