@echo off
echo ========================================
echo    Opening Chatbot Dashboard
echo ========================================
echo.

echo Checking if servers are running...
netstat -an | findstr "8002\|3000" >nul
if %errorlevel% neq 0 (
    echo Servers not running. Starting them now...
    echo.
    
    echo Starting Backend Server...
    start "Backend Server" cmd /k "python start_backend_robust.py"
    
    echo Waiting 8 seconds for backend to start...
    timeout /t 8 /nobreak >nul
    
    echo Starting Frontend Server...
    start "Frontend Server" cmd /k "cd frontend && npm run dev"
    
    echo Waiting 15 seconds for frontend to start...
    timeout /t 15 /nobreak >nul
) else (
    echo Servers are already running!
)

echo.
echo ========================================
echo    Opening Dashboard
echo ========================================
echo.

echo Opening Dashboard in your browser...
start http://localhost:3000

echo.
echo Dashboard opened!
echo.
echo Available URLs:
echo - Main Chatbot: http://localhost:3000
echo - Admin Panel:  http://localhost:3000/admin
echo - API Docs:     http://localhost:8002/docs
echo - Health Check: http://localhost:8002/health
echo.
pause
