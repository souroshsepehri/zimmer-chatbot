@echo off
echo ========================================
echo    Opening Database Admin Panel
echo ========================================
echo.

echo Checking if servers are running...
netstat -an | findstr "8000\|3000" >nul
if %errorlevel% neq 0 (
    echo Servers not running. Starting them now...
    echo.
    
    echo Starting Backend Server...
    start "Backend Server" cmd /k "cd backend && python app.py"
    
    echo Waiting 5 seconds for backend to start...
    timeout /t 5 /nobreak >nul
    
    echo Starting Frontend Server...
    start "Frontend Server" cmd /k "cd frontend && npm run dev"
    
    echo Waiting 10 seconds for frontend to start...
    timeout /t 10 /nobreak >nul
) else (
    echo Servers are already running!
)

echo.
echo ========================================
echo    Opening Admin Panel
echo ========================================
echo.

echo Opening Admin Panel in your browser...
start http://localhost:3000/admin

echo.
echo Admin Panel opened!
echo.
echo Available URLs:
echo - Main Chatbot: http://localhost:3000
echo - Admin Panel:  http://localhost:3000/admin
echo - API Docs:     http://localhost:8000/docs
echo.
pause
