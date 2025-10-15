@echo off
echo ========================================
echo    STARTING PERSIAN CHATBOT SERVER
echo ========================================
echo.

echo [1/3] Stopping any existing servers...
taskkill /F /IM python.exe 2>nul

echo [2/3] Starting chatbot server...
start /B python simple_reliable_server.py

echo [3/3] Waiting for server to start...
timeout /t 8 /nobreak > nul

echo.
echo ========================================
echo    SERVER STATUS CHECK
echo ========================================
netstat -an | findstr :8004
if %errorlevel% equ 0 (
    echo ✅ SERVER IS RUNNING ON PORT 8004
    echo.
    echo 🌐 Test URLs:
    echo    http://localhost:8004/api/status
    echo    http://localhost:8004/api/chat
    echo.
    echo 💬 Opening test interface...
    start "" "simple_test.html"
    echo.
    echo ✅ CHATBOT IS READY TO USE!
) else (
    echo ❌ SERVER FAILED TO START
    echo Please check for errors above
)

echo.
echo Press any key to continue...
pause > nul