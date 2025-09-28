@echo off
echo ========================================
echo    TESTING BACKEND CONNECTION
echo ========================================

echo Testing if backend is running...
curl -X GET http://localhost:8000/api/health 2>nul
if %errorlevel% equ 0 (
    echo Backend is running!
) else (
    echo Backend is NOT running. Starting it...
    start cmd /k "cd backend && python app.py"
    timeout /t 10 >nul
)

echo.
echo Testing chat API...
curl -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d "{\"message\": \"سلام\"}" 2>nul
if %errorlevel% equ 0 (
    echo Chat API is working!
) else (
    echo Chat API is NOT working!
)

echo.
echo Press any key to continue...
pause >nul

