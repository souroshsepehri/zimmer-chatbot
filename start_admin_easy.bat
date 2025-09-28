@echo off
echo ========================================
echo    Starting Chatbot Admin Panel
echo ========================================
echo.

echo Checking if Python is installed...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python and try again.
    pause
    exit
)

echo Checking if Node.js is installed...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH!
    echo Please install Node.js and try again.
    pause
    exit
)

echo.
echo Starting Backend Server...
cd backend
start "Backend Server" cmd /k "python app.py"
cd ..

echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo Starting Frontend Server...
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo Waiting 15 seconds for frontend to start...
timeout /t 15 /nobreak >nul

echo.
echo Checking server status...
netstat -an | findstr "8000\|3000"

echo.
echo ========================================
echo    Opening Admin Panel
echo ========================================
echo.

echo Opening Admin Panel in browser...
start http://localhost:3000/admin

echo.
echo ========================================
echo    Admin Panel URLs
echo ========================================
echo.
echo Main App: http://localhost:3000
echo Admin Panel: http://localhost:3000/admin
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit this window...
pause >nul
