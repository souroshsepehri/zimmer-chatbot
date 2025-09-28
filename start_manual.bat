@echo off
echo ========================================
echo    Manual Server Startup
echo ========================================
echo.

echo This will open 2 command windows for you to start servers manually.
echo.

echo Opening Backend window...
start "Backend - Start with: python app.py" cmd /k "cd /d C:\chatbot2\backend"

echo Opening Frontend window...
start "Frontend - Start with: npm run dev" cmd /k "cd /d C:\chatbot2\frontend"

echo.
echo ========================================
echo    INSTRUCTIONS
echo ========================================
echo.
echo 1. In the Backend window, type: python app.py
echo 2. In the Frontend window, type: npm run dev
echo 3. Wait for both to start
echo 4. Open: http://localhost:3000/admin
echo.
echo Press any key to open admin panel...
pause >nul

echo Opening Admin Panel...
start http://localhost:3000/admin
