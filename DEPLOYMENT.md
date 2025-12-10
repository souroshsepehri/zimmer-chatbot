# Deployment Instructions for Zimmer Chatbot Backend

## Prerequisites

1. Python 3.8+ installed
2. PM2 installed globally: `npm install -g pm2`
3. Virtual environment (recommended)

## Setup Steps

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the `backend` directory:

```
ADMIN_TOKEN=your-secure-admin-token-here
```

Replace `your-secure-admin-token-here` with a strong, secure token.

### 3. Start with PM2

From the project root directory:

```bash
pm2 start ecosystem.config.js
```

### 4. Restart Backend

To restart the backend service:

```bash
pm2 restart chatbot-backend
```

### 5. Check Status

```bash
pm2 status
pm2 logs chatbot-backend
```

### 6. Stop Backend

```bash
pm2 stop chatbot-backend
```

## Manual Start (Alternative)

If you prefer to run without PM2:

```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- Health Check: `GET /health`
- Get Bot Settings: `GET /api/admin/bot-settings` (requires X-Admin-Token header)
- Update Bot Settings: `POST /api/admin/bot-settings` (requires X-Admin-Token header)

## Testing

Test the health endpoint:

```bash
curl http://localhost:8000/health
```

Test admin endpoint (replace YOUR_TOKEN with your actual admin token):

```bash
curl -H "X-Admin-Token: YOUR_TOKEN" http://localhost:8000/api/admin/bot-settings
```

























