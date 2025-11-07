@echo off
echo ========================================
echo    Setting Up API Key
echo ========================================
echo.

cd /d "%~dp0"

REM Navigate to backend directory
cd backend

REM Prompt for API key
set /p API_KEY="Enter your OpenAI API key: "

REM Create .env file with API key
(
echo OPENAI_API_KEY=%API_KEY%
echo OPENAI_MODEL=gpt-4o-mini
echo EMBEDDING_MODEL=text-embedding-3-small
echo RETRIEVAL_TOP_K=4
echo RETRIEVAL_THRESHOLD=0.82
echo DATABASE_URL=sqlite:///./app.db
) > .env

echo ✅ API key saved to backend\.env
echo.
echo File location: %CD%\.env
echo.
echo ⚠️  Important: Restart your chatbot server for changes to take effect
echo.
pause

