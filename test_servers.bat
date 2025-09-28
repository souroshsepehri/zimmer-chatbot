@echo off
echo ========================================
echo    Testing Server Startup
echo ========================================
echo.

echo Testing Backend...
cd /d C:\chatbot2\backend
echo Current directory: %CD%
echo Files in backend:
dir *.py
echo.
echo Starting backend...
python app.py
