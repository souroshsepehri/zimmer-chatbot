# Fix for PM2 Frontend Port 3000 Error

## Problem
The `chatbot-frontend` PM2 process is stuck in a restart loop because:
1. It's trying to use port 3000 (which is already in use)
2. PM2 was likely started with a manual command that overrides the ecosystem.config.js

## Solution

### Quick Fix (Recommended)

Run this command on your server:

```bash
chmod +x fix_pm2_simple.sh
./fix_pm2_simple.sh
```

This script will:
1. Stop and delete the problematic `chatbot-frontend` process
2. Kill any process using port 3000
3. Restart PM2 with the correct configuration (port 8000)

### Manual Fix

If you prefer to fix it manually:

```bash
# 1. Stop and delete the process
pm2 stop chatbot-frontend
pm2 delete chatbot-frontend

# 2. Find and kill process on port 3000
lsof -ti:3000 | xargs kill -9
# OR if lsof is not available:
fuser -k 3000/tcp

# 3. Restart with correct config
pm2 start ecosystem.config.js --only chatbot-frontend --env production --update-env
pm2 save

# 4. Check status
pm2 status chatbot-frontend
pm2 logs chatbot-frontend
```

## What Was Fixed

1. **ecosystem.config.js**: Updated to use `npm run dev` (since the frontend uses static export mode)
2. **Port Configuration**: PM2 now correctly sets `PORT=8000` in the environment
3. **Scripts Created**: `fix_pm2_simple.sh` for easy fixing

## Verification

After running the fix, verify it's working:

```bash
# Check PM2 status
pm2 status

# Check logs (should show port 8000, not 3000)
pm2 logs chatbot-frontend --lines 20

# Check if port 8000 is listening
netstat -tlnp | grep 8000
# OR
lsof -i:8000
```

## Expected Behavior

- Frontend should start on port **8000** (not 3000)
- No more restart loops
- Logs should show: `next dev -H 0.0.0.0 -p 8000`

## If Issues Persist

1. Check if another process is using port 8000:
   ```bash
   lsof -i:8000
   ```

2. Verify the ecosystem.config.js is being used:
   ```bash
   pm2 describe chatbot-frontend
   ```

3. Check for any custom PM2 startup scripts that might override the config

4. Ensure the frontend package.json has the correct port in the dev script

