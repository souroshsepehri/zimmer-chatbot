@echo off
echo ========================================
echo    FINAL FIX FOR INPUT TYPING
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
echo Changes made:
echo 1. Removed debug text display
echo 2. Removed console logs
echo 3. Used textarea instead of input
echo 4. Added auto-resize functionality
echo 5. Clean state management
echo.
echo Try typing in the chat input now!
echo.
pause







