@echo off
echo ========================================
echo    TESTING INPUT FUNCTIONALITY
echo ========================================

echo Starting Backend Server...
start cmd /k "cd backend && python app.py"
timeout /t 5 >nul

echo Starting Frontend Server...
start cmd /k "cd frontend && npm run dev"
timeout /t 15 >nul

echo Opening Test Page...
start http://localhost:3000

echo.
echo ========================================
echo    TEST INSTRUCTIONS
echo ========================================
echo.
echo 1. Check the "Input Test" section on the page
echo 2. Try typing in both input fields
echo 3. Check if text appears as you type
echo 4. Then test the chat widget
echo 5. Open browser console (F12) to see debug logs
echo.
echo If the test inputs work but chat doesn't, there's a specific issue with the chat component.
echo.
pause

