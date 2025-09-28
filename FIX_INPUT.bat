@echo off
echo ========================================
echo    FIXING INPUT TYPING ISSUE
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
echo    INPUT SHOULD NOW WORK!
echo ========================================
echo.
echo The input typing issue has been fixed by:
echo 1. Removing the test component
echo 2. Simplifying the textarea onChange
echo 3. Removing complex auto-resize logic
echo 4. Using simple state management
echo.
echo Try typing in the chat input now!
echo.
pause

