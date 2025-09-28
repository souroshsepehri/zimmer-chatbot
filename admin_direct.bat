@echo off
echo ========================================
echo    Direct Admin Panel Access
echo ========================================
echo.

echo Opening Admin Panel directly...
echo Note: This assumes servers are already running
echo.

start http://localhost:3000/admin

echo Admin Panel opened!
echo.
echo If it doesn't work, the servers might not be running.
echo.
pause
