@echo off
echo ========================================
echo External API Setup for 85.208.254.187
echo ========================================
echo.

echo Step 1: Testing server connection...
python setup_external_api.py

echo.
echo Step 2: Testing external API...
python test_external_api.py

echo.
echo Step 3: Setting up environment variables...
echo.
echo Please add these lines to your .env file:
echo.
echo # External API Configuration
echo EXTERNAL_API_URL=http://85.208.254.187
echo EXTERNAL_API_PORT=8000
echo EXTERNAL_API_TIMEOUT=30
echo EXTERNAL_API_ENABLED=true
echo.

echo Step 4: Starting chatbot server...
echo Starting server on port 8002...
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8002

pause
