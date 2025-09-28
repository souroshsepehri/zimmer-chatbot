@echo off
echo ========================================
echo    FIXED ADMIN PANEL STARTUP
echo ========================================
echo.

echo Step 1: Killing any existing processes...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000"') do taskkill /PID %%a /F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":3000"') do taskkill /PID %%a /F >nul 2>&1

echo Step 2: Starting Backend Server...
cd /d C:\chatbot2\backend
start "Backend Server" cmd /k "python app.py"
cd /d C:\chatbot2

echo Waiting 8 seconds for backend to start...
timeout /t 8 /nobreak >nul

echo Step 3: Starting Frontend Server...
cd /d C:\chatbot2\frontend
start "Frontend Server" cmd /k "npm run dev"
cd /d C:\chatbot2

echo Waiting 15 seconds for frontend to start...
timeout /t 15 /nobreak >nul

echo Step 4: Checking server status...
netstat -an | findstr "8000\|3000"

echo.
echo Step 5: Opening Admin Panel...
start http://localhost:3000/admin

echo.
echo ========================================
echo    ADMIN PANEL READY!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo Admin Panel: http://localhost:3000/admin
echo.
echo If admin panel doesn't load, wait a few more seconds.
echo.
pause
