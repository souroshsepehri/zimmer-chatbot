# Next Steps - Start Chatbot on Cloud Server

## Step-by-Step Commands

After cloning the repository, run these commands on your **cloud server**:

### Step 1: Navigate to Project
```bash
cd ~/chatbot2/backend
```

### Step 2: Create Virtual Environment (if not exists)
```bash
python3 -m venv venv
```

### Step 3: Activate Virtual Environment
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Create Required Directories
```bash
mkdir -p vectorstore logs __pycache__
```

### Step 6: Start the Server

**Option A: Start in foreground (see logs)**
```bash
uvicorn app:app --host 0.0.0.0 --port 8002 --workers 1
```

**Option B: Start in background (keeps running after disconnect)**
```bash
nohup uvicorn app:app --host 0.0.0.0 --port 8002 --workers 1 > ../backend.log 2>&1 &
```

### Step 7: Verify Server is Running
```bash
# Check if process is running
ps aux | grep uvicorn

# Check if port is listening
netstat -tuln | grep 8002
# OR
lsof -i :8002

# View logs (if started in background)
tail -f ../backend.log
```

## Access Your Chatbot

Once started, access:
- **API**: `http://your-server-ip:8002`
- **API Docs**: `http://your-server-ip:8002/docs`
- **Health Check**: `http://your-server-ip:8002/health`

## Troubleshooting

### If port 8002 is already in use:
```bash
# Find what's using the port
lsof -i :8002
# Kill the process
kill -9 <PID>
# OR use a different port
uvicorn app:app --host 0.0.0.0 --port 8003 --workers 1
```

### If you get "Module not found" errors:
```bash
# Make sure venv is activated
source venv/bin/activate
# Reinstall dependencies
pip install -r requirements.txt
```

### To stop the server:
```bash
# If running in foreground: Ctrl+C
# If running in background:
pkill -f uvicorn
```



