# Troubleshooting 502 Bad Gateway Error

## What is a 502 Error?

A 502 Bad Gateway error means the frontend is running but cannot connect to the backend API server.

## Quick Fix Steps

### Step 1: Check if Backend is Running

```bash
# Check if backend process is running
ps aux | grep uvicorn

# Check if port 8001 is listening
netstat -tuln | grep 8001
# OR
lsof -i :8001

# Test backend directly
curl http://localhost:8001/health
```

**If backend is NOT running:**
```bash
cd ~/chatbot2/backend
source venv/bin/activate
nohup uvicorn app:app --host 0.0.0.0 --port 8001 --workers 1 > ../backend.log 2>&1 &
```

### Step 2: Check if Frontend is Running

```bash
# Check if frontend process is running
ps aux | grep "next dev"
ps aux | grep "npm run dev"

# Check if port 8000 is listening
netstat -tuln | grep 8000
# OR
lsof -i :8000

# Test frontend directly
curl http://localhost:8000
```

**If frontend is NOT running:**
```bash
cd ~/chatbot2/frontend
npm install  # If needed
nohup npm run dev > ../frontend.log 2>&1 &
```

### Step 3: Check Logs

```bash
# Backend logs
tail -f ~/chatbot2/backend.log

# Frontend logs
tail -f ~/chatbot2/frontend.log

# If using PM2
pm2 logs chatbot-backend
pm2 logs chatbot-frontend
```

### Step 4: Verify API Configuration

The frontend needs to know where the backend is. Check:

1. **Environment variable:**
```bash
cd ~/chatbot2/frontend
cat .env.local  # If exists
```

2. **Next.js config:**
```bash
cat ~/chatbot2/frontend/next.config.js
```

Should show: `NEXT_PUBLIC_API_URL: 'http://localhost:8001/api'`

### Step 5: Restart Both Services

```bash
# Stop everything
pkill -f uvicorn
pkill -f "npm run dev"
pkill -f "next dev"

# Wait a moment
sleep 3

# Start backend
cd ~/chatbot2/backend
source venv/bin/activate
nohup uvicorn app:app --host 0.0.0.0 --port 8001 --workers 1 > ../backend.log 2>&1 &

# Wait for backend to start
sleep 5

# Start frontend
cd ~/chatbot2/frontend
nohup npm run dev > ../frontend.log 2>&1 &
```

### Step 6: Check CORS Configuration

If backend is running but still getting 502, check CORS in `backend/app.py`:

```python
# Should have CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Common Issues

### Issue 1: Backend Not Started
**Symptom:** `curl http://localhost:8001/health` fails
**Solution:** Start the backend (see Step 1)

### Issue 2: Wrong Port
**Symptom:** Backend on different port
**Solution:** Check what port backend is actually using:
```bash
netstat -tuln | grep python
```

### Issue 3: Firewall Blocking
**Symptom:** Can access from server but not from browser
**Solution:** Check firewall rules
```bash
sudo ufw status
sudo ufw allow 8001/tcp
sudo ufw allow 8000/tcp
```

### Issue 4: API URL Mismatch
**Symptom:** Frontend trying wrong URL
**Solution:** Set environment variable:
```bash
cd ~/chatbot2/frontend
echo "NEXT_PUBLIC_API_URL=http://localhost:8001/api" > .env.local
# Then restart frontend
```

### Issue 5: Next.js Cache
**Symptom:** Changes not taking effect
**Solution:** Clear Next.js cache:
```bash
cd ~/chatbot2/frontend
rm -rf .next
npm run dev
```

## Using PM2 (Recommended)

```bash
cd ~/chatbot2
pm2 stop all
pm2 delete all
pm2 start ecosystem.config.js
pm2 save
pm2 status
```

## Test Connection

```bash
# Test backend
curl http://localhost:8001/health
curl http://localhost:8001/docs

# Test frontend
curl http://localhost:8000

# Test from browser
# Use your server IP, not 0.0.0.0
# http://YOUR-SERVER-IP:8000
```

## Get Server IP

```bash
hostname -I
# OR
curl ifconfig.me
```

Then access: `http://YOUR-SERVER-IP:8000`

## Still Not Working?

1. Check if both services are actually running:
```bash
ps aux | grep -E "uvicorn|next|npm"
```

2. Check for errors in logs:
```bash
tail -50 ~/chatbot2/backend.log
tail -50 ~/chatbot2/frontend.log
```

3. Verify ports are not in use by other processes:
```bash
lsof -i :8000
lsof -i :8001
```

4. Try accessing from server itself:
```bash
curl http://localhost:8000
curl http://localhost:8001/health
```


