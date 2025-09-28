@echo off
echo ========================================
echo    Fixing Dashboard and Logging Issues
echo ========================================
echo.

echo Setting OpenAI API Key from environment...
if not defined OPENAI_API_KEY (
    echo ERROR: OPENAI_API_KEY environment variable not set!
    echo Please set your OpenAI API key in environment variables.
    pause
    exit /b 1
)
echo API Key is set from environment variable.

echo.
echo Testing chat logging...
python test_chat_logging.py

echo.
echo Adding sample data...
python add_sample_data.py

echo.
echo Testing API endpoints...
python test_api_endpoints.py

echo.
echo Starting server...
echo Server will be available at: http://127.0.0.1:8002
echo API docs: http://127.0.0.1:8002/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn app:app --host 127.0.0.1 --port 8002 --reload
