@echo off
echo ========================================
echo    Starting Chatbot System
echo ========================================
echo.

echo Starting Backend Server...
cd backend
start "Backend Server" cmd /k "python app.py"
cd ..

echo Waiting 5 seconds...
timeout /t 5 /nobreak >nul

echo Starting Frontend Server...
cd frontend
start "Frontend Server" cmd /k "npm run dev"
cd ..

echo Waiting 15 seconds for servers to start...
timeout /t 15 /nobreak >nul

echo.
echo Opening Admin Panel...
start http://localhost:3000/admin

echo.
echo ========================================
echo    System Started!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo Admin Panel: http://localhost:3000/admin
echo.
echo Press any key to exit this window...
pause >nul
