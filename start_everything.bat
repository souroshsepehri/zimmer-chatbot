@echo off
echo ========================================
echo    Starting Complete Chatbot System
echo ========================================
echo.

echo Setting API Key...
echo Please set your OpenAI API key first:
echo set OPENAI_API_KEY=your_actual_api_key_here
echo.
if "%OPENAI_API_KEY%"=="" (
    echo ERROR: OPENAI_API_KEY not set!
    echo Please set it with: set OPENAI_API_KEY=your_actual_api_key_here
    pause
    exit /b 1
)

echo Starting Backend Server (Port 8002)...
start "Backend Server" cmd /k "cd backend && python -m uvicorn app:app --host 127.0.0.1 --port 8002"

echo Waiting 10 seconds for backend to start...
timeout /t 10 /nobreak >nul

echo Starting Frontend Server (Port 3000)...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo Waiting 15 seconds for frontend to start...
timeout /t 15 /nobreak >nul

echo.
echo ========================================
echo    System Ready!
echo ========================================
echo.
echo Available URLs:
echo - Main Chatbot: http://localhost:3000
echo - Admin Panel:  http://localhost:3000/admin
echo - API Docs:     http://localhost:8002/docs
echo.
echo Press any key to open dashboard...
pause >nul

echo Opening Dashboard...
start http://localhost:3000

echo.
echo Dashboard opened!
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause
