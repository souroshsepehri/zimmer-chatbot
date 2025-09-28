@echo off
echo ========================================
echo    Testing Logs Page and Reports
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
echo Testing backend API endpoints...
cd backend
python test_direct_api.py

echo.
echo Starting backend server...
echo Backend will be available at: http://127.0.0.1:8002
echo.
echo To test the frontend:
echo 1. Open another terminal
echo 2. cd frontend
echo 3. npm run dev
echo 4. Go to http://localhost:3000/admin/logs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app:app --host 127.0.0.1 --port 8002 --reload
