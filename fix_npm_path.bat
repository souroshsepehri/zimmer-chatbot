@echo off
echo ========================================
echo    Fixing npm Path Issue
echo ========================================
echo.

REM Clear npm cache
echo Clearing npm cache...
call npm cache clean --force

REM Navigate to frontend directory
cd frontend

REM Verify we're in the right directory
echo.
echo Current directory: %CD%
echo.

REM Remove node_modules and package-lock.json if they exist
if exist "node_modules" (
    echo Removing old node_modules...
    rmdir /s /q node_modules
)

if exist "package-lock.json" (
    echo Removing package-lock.json...
    del /f /q package-lock.json
)

REM Install dependencies fresh
echo.
echo Installing npm dependencies...
call npm install

if errorlevel 1 (
    echo.
    echo ERROR: npm install failed!
    echo.
    echo Troubleshooting steps:
    echo 1. Make sure Node.js is installed: node --version
    echo 2. Make sure npm is installed: npm --version
    echo 3. Try running: npm cache clean --force
    echo 4. Then run this script again
    pause
    exit /b 1
)

echo.
echo ========================================
echo    npm Dependencies Installed!
echo ========================================
echo.
echo You can now run: start_chatbot_server.bat
echo.
pause

