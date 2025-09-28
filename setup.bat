@echo off
echo ========================================
echo    Persian Chatbot Setup
echo ========================================
echo.

echo Creating environment file...
echo OPENAI_API_KEY=your_openai_api_key_here > .env
echo DATABASE_URL=sqlite:///./app.db >> .env
echo VECTORSTORE_PATH=./vectorstore >> .env
echo NEXT_PUBLIC_API_URL=http://localhost:8000/api >> .env

echo.
echo Environment file created! Please edit .env and add your OpenAI API key.
echo.
echo Then run: docker-compose up --build
echo.
pause
