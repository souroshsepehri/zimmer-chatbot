@echo off
echo ========================================
echo    Starting Chatbot with API Key
echo ========================================
echo.

echo Setting OpenAI API Key...
echo Please set your OPENAI_API_KEY environment variable first!
echo Example: set OPENAI_API_KEY=your_api_key_here
echo.
echo Testing API key...
python -c "import os; print('API Key set:', bool(os.getenv('OPENAI_API_KEY')))"

echo.
echo Starting backend server...
cd backend
python -m uvicorn app:app --host 127.0.0.1 --port 8002 --reload

echo.
echo Server started! You can now:
echo 1. Open another terminal
echo 2. cd frontend
echo 3. npm run dev
echo 4. Go to http://localhost:3000
echo.
pause
