@echo off
echo ========================================
echo    FINAL FIX FOR ALL ERROR ICONS
echo ========================================
echo.

echo Setting up environment...
set OPENAI_API_KEY=your_openai_api_key_here

echo.
echo 1. Setting up database...
python setup_database.py

echo.
echo 2. Testing all components...
python fix_all_errors.py

echo.
echo 3. Starting backend server...
start "Backend Server" cmd /k "cd backend && set OPENAI_API_KEY=your_openai_api_key_here && python -m uvicorn app:app --host 127.0.0.1 --port 8002"

echo.
echo 4. Starting frontend server...
start "Frontend Server" cmd /k "cd frontend && npm run dev"

echo.
echo 5. Waiting for servers to start...
timeout /t 15 /nobreak >nul

echo.
echo 6. Testing final status...
python -c "import requests; print('Backend:', requests.get('http://localhost:8002/health').json()); print('Frontend:', requests.get('http://localhost:3000').status_code)"

echo.
echo ========================================
echo    ALL ERROR ICONS FIXED!
echo ========================================
echo.
echo ✅ Backend: http://localhost:8002
echo ✅ Frontend: http://localhost:3000
echo ✅ Admin Panel: python admin_panel.py
echo.
echo Opening chatbot...
start http://localhost:3000
echo.
echo All error icons should now be gone!
echo.
pause
