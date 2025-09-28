@echo off
echo ========================================
echo    FIXING CHATBOT STARTUP
echo ========================================

echo Starting Backend Server...
start cmd /k "cd backend && python app.py"
timeout /t 5 >nul

echo Starting Frontend Server...
start cmd /k "cd frontend && npm run dev"
timeout /t 15 >nul

echo Opening Chatbot...
start http://localhost:3000

echo.
echo ========================================
echo    CHATBOT SHOULD NOW WORK!
echo ========================================
echo.
echo If messages still don't show, check the browser console for errors.
echo.
pause

