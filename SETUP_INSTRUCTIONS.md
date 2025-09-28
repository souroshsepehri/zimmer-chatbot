# Chatbot Setup Instructions

## Quick Start

1. **Set your OpenAI API Key:**
   ```bash
   # Windows PowerShell
   $env:OPENAI_API_KEY="your_actual_api_key_here"
   
   # Windows Command Prompt
   set OPENAI_API_KEY=your_actual_api_key_here
   ```

2. **Start the complete system:**
   ```bash
   .\FINAL_START.bat
   ```

## Manual Setup

### Backend Server
```bash
cd backend
python -m uvicorn app:app --host 127.0.0.1 --port 8002
```

### Frontend Server
```bash
cd frontend
npm run dev
```

## Access Points

- **Main Chatbot**: http://localhost:3000
- **Admin Panel**: http://localhost:3000/admin
- **API Documentation**: http://localhost:8002/docs

## Important Notes

- Replace `your_openai_api_key_here` in all batch files with your actual OpenAI API key
- The system uses port 8002 for backend and port 3000 for frontend
- Chat logging is fully functional and saves all interactions to the database
- Admin panel allows you to view chat logs and manage FAQs

## Troubleshooting

If you see "AI future disabled" errors:
1. Make sure your OpenAI API key is set correctly
2. Ensure both backend and frontend servers are running
3. Check that the database is initialized (run `python setup_database.py`)

## Files Overview

- `FINAL_START.bat` - Complete system startup script
- `setup_database.py` - Initialize database tables
- `test_logs.py` - Check chat logging functionality
- `FINAL_TEST.py` - Comprehensive system test
