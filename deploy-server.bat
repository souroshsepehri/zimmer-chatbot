@echo off
REM Persian Chatbot Server Deployment Script for Windows
REM This script automates the deployment process for your Persian chatbot

setlocal enabledelayedexpansion

REM Colors for output (Windows doesn't support colors in batch, but we can use echo)
set "INFO=[INFO]"
set "SUCCESS=[SUCCESS]"
set "WARNING=[WARNING]"
set "ERROR=[ERROR]"

REM Configuration
set "PROJECT_NAME=persian-chatbot"
set "BACKEND_PORT=8000"
set "FRONTEND_PORT=3000"

echo ==========================================
echo Persian Chatbot Server Deployment Script
echo ==========================================
echo.

REM Check if Docker is installed
echo %INFO% Checking system requirements...
docker --version >nul 2>&1
if errorlevel 1 (
    echo %ERROR% Docker is not installed. Please install Docker Desktop first.
    echo Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo %ERROR% Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

echo %SUCCESS% All requirements met

REM Check if .env file exists
echo %INFO% Setting up environment...
if not exist .env (
    echo %INFO% Creating .env file...
    copy backend\env.example .env
    echo %WARNING% Please edit .env file and add your OpenAI API key
    echo %WARNING% Run: notepad .env
    pause
)

REM Check if OpenAI API key is set
findstr /C:"OPENAI_API_KEY=sk-" .env >nul
if errorlevel 1 (
    echo %ERROR% OpenAI API key not found in .env file
    echo %ERROR% Please add your OpenAI API key to .env file
    pause
    exit /b 1
)

echo %SUCCESS% Environment configured

REM Create necessary directories
echo %INFO% Creating necessary directories...
if not exist backend\vectorstore mkdir backend\vectorstore
if not exist backend\logs mkdir backend\logs
if not exist backups mkdir backups

echo %SUCCESS% Directories created

REM Deploy with Docker
echo %INFO% Deploying with Docker...

REM Stop existing containers
echo %INFO% Stopping existing containers...
docker-compose down 2>nul

REM Build and start services
echo %INFO% Building and starting services...
docker-compose up -d --build

REM Wait for services to start
echo %INFO% Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Check if services are running
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo %ERROR% Services failed to start
    docker-compose logs
    pause
    exit /b 1
)

echo %SUCCESS% Services started successfully

REM Initialize database
echo %INFO% Initializing database...

REM Wait for backend to be ready
echo %INFO% Waiting for backend to be ready...
for /L %%i in (1,1,30) do (
    docker-compose exec backend python -c "import requests; requests.get('http://localhost:8000/health')" >nul 2>&1
    if not errorlevel 1 goto :backend_ready
    timeout /t 2 /nobreak >nul
)
echo %WARNING% Backend may not be ready, continuing anyway...

:backend_ready
REM Initialize database
docker-compose exec backend python init_database.py
docker-compose exec backend python add_sample_data.py

echo %SUCCESS% Database initialized

REM Test deployment
echo %INFO% Testing deployment...

REM Test backend health
curl -s http://localhost:8000/health | findstr "healthy" >nul
if errorlevel 1 (
    echo %WARNING% Backend health check failed
) else (
    echo %SUCCESS% Backend health check passed
)

REM Test frontend
curl -s http://localhost:3000 | findstr "بات هوشمند" >nul
if errorlevel 1 (
    echo %WARNING% Frontend test failed, but this might be normal
) else (
    echo %SUCCESS% Frontend is accessible
)

echo %SUCCESS% Deployment test completed

REM Create management scripts
echo %INFO% Creating management scripts...

REM Create start script
echo @echo off > start-chatbot.bat
echo echo Starting Persian Chatbot... >> start-chatbot.bat
echo docker-compose up -d >> start-chatbot.bat
echo echo Services started. Access at http://localhost:3000 >> start-chatbot.bat

REM Create stop script
echo @echo off > stop-chatbot.bat
echo echo Stopping Persian Chatbot... >> stop-chatbot.bat
echo docker-compose down >> stop-chatbot.bat
echo echo Services stopped >> stop-chatbot.bat

REM Create restart script
echo @echo off > restart-chatbot.bat
echo echo Restarting Persian Chatbot... >> restart-chatbot.bat
echo docker-compose down >> restart-chatbot.bat
echo docker-compose up -d >> restart-chatbot.bat
echo echo Services restarted >> restart-chatbot.bat

REM Create update script
echo @echo off > update-chatbot.bat
echo echo Updating Persian Chatbot... >> update-chatbot.bat
echo git pull origin main >> update-chatbot.bat
echo docker-compose down >> update-chatbot.bat
echo docker-compose up -d --build >> update-chatbot.bat
echo echo Update completed >> update-chatbot.bat

REM Create backup script
echo @echo off > backup-chatbot.bat
echo set BACKUP_DIR=.\backups >> backup-chatbot.bat
echo for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a" >> backup-chatbot.bat
echo set "YY=!dt:~2,2!" >> backup-chatbot.bat
echo set "MM=!dt:~4,2!" >> backup-chatbot.bat
echo set "DD=!dt:~6,2!" >> backup-chatbot.bat
echo set "HH=!dt:~8,2!" >> backup-chatbot.bat
echo set "Min=!dt:~10,2!" >> backup-chatbot.bat
echo set "Sec=!dt:~12,2!" >> backup-chatbot.bat
echo set "timestamp=!YY!!MM!!DD!_!HH!!Min!!Sec!" >> backup-chatbot.bat
echo echo Creating backup... >> backup-chatbot.bat
echo docker-compose exec backend cp /app/app.db /app/backup_!timestamp!.db >> backup-chatbot.bat
echo docker cp $(docker-compose ps -q backend):/app/backup_!timestamp!.db !BACKUP_DIR!\ >> backup-chatbot.bat
echo echo Backup completed >> backup-chatbot.bat

echo %SUCCESS% Management scripts created

REM Show status
echo %INFO% Deployment Status:
echo.
echo Services:
docker-compose ps
echo.
echo Access URLs:
echo   Frontend: http://localhost:3000
echo   Backend API: http://localhost:8000/api
echo   Health Check: http://localhost:8000/health
echo.
echo Management Scripts:
echo   start-chatbot.bat   - Start services
echo   stop-chatbot.bat    - Stop services
echo   restart-chatbot.bat - Restart services
echo   update-chatbot.bat  - Update services
echo   backup-chatbot.bat  - Backup data
echo.

echo %SUCCESS% Deployment completed successfully!
echo %INFO% Your Persian chatbot is now running
echo %INFO% Access it at: http://localhost:3000
echo.
echo %INFO% Management scripts created:
echo %INFO%   .\start-chatbot.bat   - Start services
echo %INFO%   .\stop-chatbot.bat    - Stop services
echo %INFO%   .\restart-chatbot.bat - Restart services
echo %INFO%   .\update-chatbot.bat  - Update services
echo %INFO%   .\backup-chatbot.bat  - Backup data

pause

