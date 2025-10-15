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

REM Check if Node.js and PM2 are installed
echo %INFO% Checking system requirements...
node --version >nul 2>&1
if errorlevel 1 (
    echo %ERROR% Node.js is not installed. Please install Node.js first.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

pm2 --version >nul 2>&1
if errorlevel 1 (
    echo %INFO% Installing PM2...
    npm install -g pm2
    if errorlevel 1 (
        echo %ERROR% Failed to install PM2. Please install manually: npm install -g pm2
        pause
        exit /b 1
    )
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
if not exist logs mkdir logs
if not exist backups mkdir backups

echo %SUCCESS% Directories created

REM Install dependencies
echo %INFO% Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo %ERROR% Failed to install Python dependencies
    pause
    exit /b 1
)

if exist frontend (
    echo %INFO% Installing frontend dependencies...
    cd frontend
    npm install
    if errorlevel 1 (
        echo %ERROR% Failed to install frontend dependencies
        pause
        exit /b 1
    )
    cd ..
)

echo %SUCCESS% Dependencies installed

REM Deploy with PM2
echo %INFO% Deploying with PM2...

REM Stop existing processes
echo %INFO% Stopping existing processes...
pm2 delete all 2>nul

REM Install PM2 log rotation
pm2 install pm2-logrotate 2>nul
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 30
pm2 set pm2-logrotate:compress true

REM Start services
echo %INFO% Starting services...
pm2 start ecosystem.config.js --env production

REM Wait for services to start
echo %INFO% Waiting for services to start...
timeout /t 30 /nobreak >nul

REM Check if services are running
pm2 status | findstr "online" >nul
if errorlevel 1 (
    echo %ERROR% Services failed to start
    pm2 logs
    pause
    exit /b 1
)

echo %SUCCESS% Services started successfully

REM Initialize database
echo %INFO% Initializing database...

REM Wait for backend to be ready
echo %INFO% Waiting for backend to be ready...
for /L %%i in (1,1,30) do (
    curl -s http://localhost:8000/health >nul 2>&1
    if not errorlevel 1 goto :backend_ready
    timeout /t 2 /nobreak >nul
)
echo %WARNING% Backend may not be ready, continuing anyway...

:backend_ready
REM Initialize database
python init_database.py
python add_sample_data.py

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
echo pm2 start ecosystem.config.js --env production >> start-chatbot.bat
echo echo Services started. Access at http://localhost:3000 >> start-chatbot.bat

REM Create stop script
echo @echo off > stop-chatbot.bat
echo echo Stopping Persian Chatbot... >> stop-chatbot.bat
echo pm2 stop all >> stop-chatbot.bat
echo echo Services stopped >> stop-chatbot.bat

REM Create restart script
echo @echo off > restart-chatbot.bat
echo echo Restarting Persian Chatbot... >> restart-chatbot.bat
echo pm2 restart all >> restart-chatbot.bat
echo echo Services restarted >> restart-chatbot.bat

REM Create update script
echo @echo off > update-chatbot.bat
echo echo Updating Persian Chatbot... >> update-chatbot.bat
echo git pull origin main >> update-chatbot.bat
echo pip install -r requirements.txt >> update-chatbot.bat
echo pm2 reload all >> update-chatbot.bat
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
echo copy app.db !BACKUP_DIR!\app-!timestamp!.db >> backup-chatbot.bat
echo pm2 save >> backup-chatbot.bat
echo copy "%USERPROFILE%\.pm2\dump.pm2" !BACKUP_DIR!\pm2-config-!timestamp!.pm2 >> backup-chatbot.bat
echo echo Backup completed >> backup-chatbot.bat

echo %SUCCESS% Management scripts created

REM Save PM2 configuration
pm2 save

REM Show status
echo %INFO% Deployment Status:
echo.
echo Services:
pm2 status
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
echo PM2 Commands:
echo   pm2 status          - Check service status
echo   pm2 logs            - View logs
echo   pm2 monit           - Monitor services
echo   pm2 restart all     - Restart all services
echo   pm2 stop all        - Stop all services
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

