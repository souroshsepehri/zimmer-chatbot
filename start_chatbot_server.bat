@echo off
echo ========================================
echo    Starting Chatbot Server
echo ========================================
echo.

REM Get the current directory (should be C:\chatbot2)
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

echo Current directory: %CD%
echo.

REM Step 1: Check and install frontend dependencies if needed
echo [1/3] Checking Frontend Dependencies...
cd frontend
if not exist "node_modules" (
    echo Installing npm dependencies...
    call npm install
    if errorlevel 1 (
        echo ERROR: npm install failed!
        pause
        exit /b 1
    )
) else (
    echo Frontend dependencies found.
)
cd ..

REM Step 2: Start Backend Server
echo.
echo [2/3] Starting Backend Server...
cd backend
start "Chatbot Backend" cmd /k "python app.py"
cd ..
timeout /t 5 /nobreak >nul

REM Step 3: Start Frontend Server
echo.
echo [3/3] Starting Frontend Server...
cd frontend
start "Chatbot Frontend" cmd /k "npm run dev"
cd ..
timeout /t 10 /nobreak >nul

echo.
echo ========================================
echo    Chatbot Started Successfully!
echo ========================================
echo.
echo Backend:  http://localhost:8002
echo Frontend: http://localhost:3000
echo Admin:    http://localhost:3000/admin
echo.
echo Opening browser...
timeout /t 2 /nobreak >nul
start http://localhost:3000
echo.
echo Both servers are running in separate windows.
echo Close those windows to stop the servers.
echo.
pause

