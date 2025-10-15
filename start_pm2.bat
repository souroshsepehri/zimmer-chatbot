@echo off
echo Starting Persian Chatbot with PM2...

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed. Please install Node.js first.
    pause
    exit /b 1
)

REM Check if PM2 is installed
pm2 --version >nul 2>&1
if errorlevel 1 (
    echo Installing PM2...
    npm install -g pm2
    if errorlevel 1 (
        echo Error: Failed to install PM2. Please install manually: npm install -g pm2
        pause
        exit /b 1
    )
)

REM Create logs directory
if not exist "logs" mkdir logs

REM Install PM2 log rotation if not already installed
pm2 list | findstr "pm2-logrotate" >nul 2>&1
if errorlevel 1 (
    echo Installing PM2 log rotation...
    pm2 install pm2-logrotate
)

REM Configure log rotation
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 30
pm2 set pm2-logrotate:compress true

REM Check if .env file exists
if not exist ".env" (
    echo Warning: .env file not found. Please create one with your API keys.
    echo Copying from example...
    if exist "backend\env.example" (
        copy "backend\env.example" ".env"
        echo Please edit .env file with your API keys before starting.
        pause
    )
)

REM Install Python dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install Python dependencies.
    pause
    exit /b 1
)

REM Install frontend dependencies if frontend directory exists
if exist "frontend" (
    echo Installing frontend dependencies...
    cd frontend
    npm install
    if errorlevel 1 (
        echo Error: Failed to install frontend dependencies.
        pause
        exit /b 1
    )
    cd ..
)

REM Start services with PM2
echo Starting services with PM2...
pm2 start ecosystem.config.js --env production

REM Save PM2 configuration
pm2 save

echo.
echo ========================================
echo Persian Chatbot started successfully!
echo ========================================
echo.
echo Services:
echo - Backend: http://localhost:8000
echo - Frontend: http://localhost:3000
echo - Health Check: http://localhost:8000/health
echo.
echo Useful commands:
echo - pm2 status          : Check service status
echo - pm2 logs            : View logs
echo - pm2 monit           : Monitor services
echo - pm2 stop all        : Stop all services
echo - pm2 restart all     : Restart all services
echo.
echo Press any key to open monitoring dashboard...
pause >nul

REM Open PM2 monitoring
pm2 monit
