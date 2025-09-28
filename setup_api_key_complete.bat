@echo off
echo ========================================
echo    OpenAI API Key Setup
echo ========================================
echo.

echo Setting environment variable...
set OPENAI_API_KEY=%OPENAI_API_KEY%

echo.
echo Creating .env file...
echo OPENAI_API_KEY=%OPENAI_API_KEY% > .env
echo OPENAI_MODEL=gpt-4o-mini >> .env
echo EMBEDDING_MODEL=text-embedding-3-small >> .env
echo RETRIEVAL_TOP_K=4 >> .env
echo RETRIEVAL_THRESHOLD=0.82 >> .env
echo DATABASE_URL=sqlite:///./app.db >> .env

echo.
echo Testing API key...
python -c "import os; print('API Key set:', bool(os.getenv('OPENAI_API_KEY')))"

echo.
echo Testing intent system...
python -c "from services.intent import intent_detector; result = intent_detector.detect('سلام'); print('Intent test result:', result['label'], result['confidence'])"

echo.
echo ========================================
echo    Setup Complete!
echo ========================================
echo.
echo Your OpenAI API key has been configured.
echo You can now start the chatbot with:
echo   python start_backend_robust.py
echo.
echo Or use the complete system launcher:
echo   ..\FINAL_START.bat
echo.
pause
