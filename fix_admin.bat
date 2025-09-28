@echo off
echo ========================================
echo    Fixing Admin Panel Access
echo ========================================
echo.

echo Step 1: Starting Backend Server...
echo Please wait...
cd /d C:\chatbot2\backend
start "Backend Server" cmd /k "python app.py"
cd /d C:\chatbot2

echo.
echo Step 2: Starting Frontend Server...
echo Please wait...
cd /d C:\chatbot2\frontend
start "Frontend Server" cmd /k "npm run dev"
cd /d C:\chatbot2

echo.
echo Step 3: Waiting for servers to start...
echo Please wait 25 seconds...
timeout /t 25 /nobreak >nul

echo.
echo Step 4: Checking if servers are running...
netstat -an | findstr "8000\|3000"

echo.
echo Step 5: Opening Admin Panel...
start http://localhost:3000/admin

echo.
echo ========================================
echo    Admin Panel Opened!
echo ========================================
echo.
echo If it doesn't load:
echo 1. Wait a few more seconds
echo 2. Check the server windows for errors
echo 3. Try: http://localhost:3000/admin
echo.
pause
