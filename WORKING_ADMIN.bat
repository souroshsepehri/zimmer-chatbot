@echo off
echo ========================================
echo    WORKING ADMIN PANEL SOLUTION
echo ========================================
echo.

echo This will open 3 windows:
echo 1. Backend Server
echo 2. Frontend Server  
echo 3. Admin Panel
echo.

echo Press any key to start...
pause >nul

echo.
echo Starting Backend Server...
start "Backend Server" cmd /k "cd /d C:\chatbot2\backend && python app.py"

echo.
echo Starting Frontend Server...
start "Frontend Server" cmd /k "cd /d C:\chatbot2\frontend && npm run dev"

echo.
echo Waiting 30 seconds for servers to start...
echo Please wait...
timeout /t 30 /nobreak >nul

echo.
echo Opening Admin Panel...
start http://localhost:3000/admin

echo.
echo ========================================
echo    DONE!
echo ========================================
echo.
echo Admin Panel should now be open!
echo If not, wait a few more seconds and try:
echo http://localhost:3000/admin
echo.
pause
