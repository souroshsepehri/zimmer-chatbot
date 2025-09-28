@echo off
echo ========================================
echo    Testing System Status Page
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
echo Starting backend server...
echo Backend: http://127.0.0.1:8002
echo.
echo To test the system status page:
echo 1. Open another terminal
echo 2. cd frontend
echo 3. npm run dev
echo 4. Go to http://localhost:3000/admin
echo 5. Click on "وضعیت سیستم" button in top left
echo 6. Or go directly to http://localhost:3000/admin/system-status
echo.
echo The system status page should now show:
echo - Backend status (online/offline)
echo - Database connection status
echo - API endpoints status
echo - System performance info
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
python -m uvicorn app:app --host 127.0.0.1 --port 8002 --reload
