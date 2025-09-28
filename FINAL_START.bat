@echo off
echo ========================================
echo    FINAL CHATBOT STARTUP
echo ========================================
echo.

echo Step 1: Setting API Key...
echo Please set your OpenAI API key first:
echo set OPENAI_API_KEY=your_actual_api_key_here
echo.
if "%OPENAI_API_KEY%"=="" (
    echo ERROR: OPENAI_API_KEY not set!
    echo Please set it with: set OPENAI_API_KEY=your_actual_api_key_here
    pause
    exit /b 1
)

echo Step 2: Starting Backend Server...
cd backend
start "Backend Server" cmd /k "python -m uvicorn app:app --host 127.0.0.1 --port 8002"
cd ..

echo Step 3: Waiting for backend...
timeout /t 15 /nobreak >nul

echo Step 4: Starting Frontend Server...
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo Step 5: Waiting for frontend...
timeout /t 20 /nobreak >nul

echo.
echo ========================================
echo    TESTING SYSTEM
echo ========================================
echo.

echo Testing Backend...
python -c "import requests; response = requests.get('http://localhost:8002/health'); print('Backend Status:', response.json())" 2>nul || echo "Backend not ready yet"

echo Testing Frontend...
python -c "import requests; response = requests.get('http://localhost:3000'); print('Frontend Status:', response.status_code)" 2>nul || echo "Frontend not ready yet"

echo.
echo ========================================
echo    OPENING DASHBOARD
echo ========================================
echo.

echo Opening Dashboard in browser...
start http://localhost:3000

echo.
echo ✅ Chatbot system started!
echo.
echo If servers are not running, check the command windows that opened.
echo Close those windows to stop the servers.
echo.
pause
