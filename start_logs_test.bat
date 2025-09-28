@echo off
echo ========================================
echo    Starting Logs Page Test
echo ========================================
echo.

echo Setting OpenAI API Key from environment...
if not defined OPENAI_API_KEY (
    echo ERROR: OPENAI_API_KEY environment variable not set!
    echo Please set your OpenAI API key in environment variables.
    pause
    exit /b 1
)
echo API Key is set from environment variable.

echo.
echo Testing logs system...
cd backend
python fix_logs_complete.py

echo.
echo Starting backend server...
echo Backend: http://127.0.0.1:8002
echo API docs: http://127.0.0.1:8002/docs
echo.
echo To test the logs page:
echo 1. Open another terminal
echo 2. cd frontend
echo 3. npm run dev
echo 4. Go to http://localhost:3000/admin/logs
echo.
echo The logs page should now work correctly!
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app:app --host 127.0.0.1 --port 8002 --reload
