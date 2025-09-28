# Chatbot Setup Guide

## Quick Start

### 1. Set Environment Variables
```bash
# Set your OpenAI API key
$env:OPENAI_API_KEY="your_openai_api_key_here"
```

### 2. Start the Chatbot
```bash
# Option 1: Use the dashboard launcher
.\open_dashboard.bat

# Option 2: Manual start
# Terminal 1 - Backend
python start_backend_robust.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 3. Access the Chatbot
- **Main Chatbot:** http://localhost:3000
- **Admin Panel:** http://localhost:3000/admin
- **API Docs:** http://localhost:8002/docs

## Environment Variables

Create a `.env` file in the project root with:
```
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./app.db
VECTORSTORE_PATH=./vectorstore
```

## Admin Tools

- **Interactive Admin Panel:** `python admin_panel.py`
- **Log Analysis:** `python analyze_logs.py`
- **Quick Test:** `python test_admin.py`

## Features

✅ **Working Chat System** - Persian chatbot with FAQ support
✅ **Complete Logging** - All chats saved to database
✅ **Admin Panel** - View logs, manage FAQs, see statistics
✅ **Dashboard** - Web interface for management
✅ **API Documentation** - Full API docs at /docs
✅ **Database Management** - SQLite database with full logging

## Troubleshooting

If the backend server stops:
1. Check if port 8002 is available
2. Make sure OPENAI_API_KEY is set
3. Use `python start_backend_robust.py` to restart

If the frontend doesn't connect:
1. Make sure backend is running on port 8002
2. Check frontend/next.config.js for correct API URL
