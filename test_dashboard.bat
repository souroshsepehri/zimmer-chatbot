@echo off
echo ========================================
echo    Testing Dashboard API Endpoints
echo ========================================
echo.

echo Setting OpenAI API Key...
set OPENAI_API_KEY=%OPENAI_API_KEY%

echo.
echo Starting backend server...
start "Backend Server" python -m uvicorn app:app --host 127.0.0.1 --port 8002 --reload

echo.
echo Waiting for server to start...
timeout /t 5 /nobreak > nul

echo.
echo Testing API endpoints...
python test_api_endpoints.py

echo.
echo ========================================
echo    Dashboard Test Complete
echo ========================================
echo.
echo Backend server is running on: http://127.0.0.1:8002
echo API docs: http://127.0.0.1:8002/docs
echo.
echo To test the frontend dashboard:
echo 1. Open another terminal
echo 2. cd frontend
echo 3. npm run dev
echo 4. Go to http://localhost:3000/admin
echo.
pause
