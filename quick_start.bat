@echo off
echo ========================================
echo    Quick Start - Manual Steps
echo ========================================
echo.

echo Step 1: Starting Backend Server...
echo Please wait...
cd backend
start "Backend Server" cmd /k "python app.py"
cd ..

echo.
echo Step 2: Starting Frontend Server...
echo Please wait...
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo.
echo Step 3: Waiting for servers to start...
echo Please wait 20 seconds...
timeout /t 20 /nobreak >nul

echo.
echo Step 4: Opening Admin Panel...
start http://localhost:3000/admin

echo.
echo ========================================
echo    Done!
echo ========================================
echo.
echo If the admin panel doesn't load:
echo 1. Wait a few more seconds
echo 2. Check the server windows for errors
echo 3. Try opening http://localhost:3000/admin manually
echo.
pause
