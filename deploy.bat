@echo off
echo ========================================
echo    Persian Chatbot Deployment Script
echo ========================================
echo.

echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Creating backend directories...
mkdir backend\vectorstore 2>nul
mkdir backend\logs 2>nul
mkdir backend\__pycache__ 2>nul

echo.
echo Setting up backend database...
cd backend
python -c "import sqlite3; import os; os.makedirs('vectorstore', exist_ok=True); os.makedirs('logs', exist_ok=True); print('✅ Backend setup complete')"
cd ..

echo.
echo Building frontend...
if exist frontend (
    cd frontend
    if exist package.json (
        echo Installing npm dependencies...
        npm install --legacy-peer-deps
        echo Building frontend...
        npm run build
        echo ✅ Frontend built successfully
    ) else (
        echo ⚠️ No package.json found
    )
    cd ..
) else (
    echo ⚠️ Frontend directory not found
)

echo.
echo Starting Persian Chatbot...
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port %PORT%
