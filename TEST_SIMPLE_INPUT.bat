@echo off
echo ========================================
echo    TESTING SIMPLE INPUT
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
echo 1. Look for the "Input Test" box in the top-left corner
echo 2. Type in that input field - does it work?
echo 3. If it works, the problem is with the chat component
echo 4. If it doesn't work, there's a React issue
echo 5. Open browser console (F12) to see debug logs
echo 6. Then test the chat widget
echo.
echo This will help us identify exactly where the problem is!
echo.
pause


























