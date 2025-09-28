@echo off
echo ========================================
echo    Quick Admin Panel Access
echo ========================================
echo.

echo Checking if servers are running...
netstat -an | findstr ":8000" >nul
if %errorlevel% neq 0 (
    echo Backend server is NOT running!
    echo.
    echo Starting Backend...
    start "Backend" cmd /k "cd backend && python app.py"
    timeout /t 5 /nobreak >nul
) else (
    echo Backend server is running!
)

netstat -an | findstr ":3000" >nul
if %errorlevel% neq 0 (
    echo Frontend server is NOT running!
    echo.
    echo Starting Frontend...
    start "Frontend" cmd /k "cd frontend && npm run dev"
    timeout /t 10 /nobreak >nul
) else (
    echo Frontend server is running!
)

echo.
echo Opening Admin Panel...
start http://localhost:3000/admin

echo.
echo Admin Panel opened!
echo If it doesn't load, wait a few more seconds.
echo.
pause
