@echo off
echo ========================================
echo    Create .env File for API Key
echo ========================================
echo.

cd /d "%~dp0"

if exist .env (
    echo .env file already exists!
    echo.
    choice /C YN /M "Do you want to overwrite it"
    if errorlevel 2 goto :end
)

echo Enter your OpenAI API key:
set /p API_KEY="API Key: "

if "%API_KEY%"=="" (
    echo Error: API key cannot be empty!
    pause
    exit /b 1
)

(
echo OPENAI_API_KEY=%API_KEY%
echo OPENAI_MODEL=gpt-3.5-turbo
echo EMBEDDING_MODEL=text-embedding-3-small
echo RETRIEVAL_TOP_K=4
echo RETRIEVAL_THRESHOLD=0.82
echo DATABASE_URL=sqlite:///./app.db
) > .env

echo.
echo ========================================
echo    .env file created successfully!
echo ========================================
echo.
echo Location: %CD%\.env
echo.
echo Remember to restart your server for changes to take effect!
echo.
pause

:end

