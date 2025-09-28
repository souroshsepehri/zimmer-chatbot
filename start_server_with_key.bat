@echo off
echo ========================================
echo    Starting Chatbot Server
echo ========================================
echo.

echo Setting OpenAI API Key...
set OPENAI_API_KEY=your_api_key_here

echo.
echo Testing API key configuration...
python -c "import os; print('API Key set:', bool(os.getenv('OPENAI_API_KEY')))"

echo.
echo Testing intent system...
python -c "from services.intent import intent_detector; result = intent_detector.detect('سلام'); print('Intent test result:', result['label'], result['confidence'])"

echo.
echo Starting server...
echo Server will be available at: http://127.0.0.1:8002
echo API docs will be available at: http://127.0.0.1:8002/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app:app --host 127.0.0.1 --port 8002 --reload
