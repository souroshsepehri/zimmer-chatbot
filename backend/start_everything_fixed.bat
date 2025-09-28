@echo off
echo ========================================
echo    Starting Fixed Chatbot System
echo ========================================
echo.

echo Setting OpenAI API Key...
set OPENAI_API_KEY=%OPENAI_API_KEY%

echo.
echo Testing system...
python fix_all_issues.py

echo.
echo Starting backend server...
echo Server will be available at: http://127.0.0.1:8002
echo API docs: http://127.0.0.1:8002/docs
echo.
echo To test the frontend:
echo 1. Open another terminal
echo 2. cd frontend
echo 3. npm run dev
echo 4. Go to http://localhost:3000/admin
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app:app --host 127.0.0.1 --port 8002 --reload
