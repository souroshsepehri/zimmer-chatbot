@echo off
echo ========================================
echo    Testing Admin Panel
echo ========================================
echo.

echo Checking if servers are running...
netstat -an | findstr "8000" >nul
if %errorlevel% neq 0 (
    echo Backend server is NOT running!
    echo Please start it first: cd backend && python app.py
    pause
    exit
) else (
    echo Backend server is running!
)

netstat -an | findstr "3000" >nul
if %errorlevel% neq 0 (
    echo Frontend server is NOT running!
    echo Please start it first: cd frontend && npm run dev
    pause
    exit
) else (
    echo Frontend server is running!
)

echo.
echo Opening Admin Panel...
start http://localhost:3000/admin

echo.
echo ========================================
echo    Admin Panel Test
echo ========================================
echo.
echo Admin Panel should now be open!
echo.
echo Test these pages:
echo 1. Dashboard: http://localhost:3000/admin
echo 2. FAQs: http://localhost:3000/admin/faqs
echo 3. Categories: http://localhost:3000/admin/categories
echo 4. Logs: http://localhost:3000/admin/logs
echo.
echo If any page shows errors, check the browser console.
echo.
pause
