@echo off
echo Setting up PM2 for Persian Chatbot...
echo =====================================

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo Error: Node.js is not installed.
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Install PM2 globally
echo Installing PM2...
npm install -g pm2
if errorlevel 1 (
    echo Error: Failed to install PM2
    pause
    exit /b 1
)

REM Install PM2 log rotation
echo Installing PM2 log rotation...
pm2 install pm2-logrotate

REM Configure log rotation
echo Configuring log rotation...
pm2 set pm2-logrotate:max_size 10M
pm2 set pm2-logrotate:retain 30
pm2 set pm2-logrotate:compress true
pm2 set pm2-logrotate:dateFormat YYYY-MM-DD_HH-mm-ss

REM Create logs directory
if not exist "logs" mkdir logs

echo.
echo PM2 setup completed successfully!
echo.
echo Next steps:
echo 1. Create .env file with your API keys
echo 2. Run: npm start
echo 3. Or run: pm2 start ecosystem.config.js --env production
echo.
echo Useful PM2 commands:
echo - pm2 status          : Check service status
echo - pm2 logs            : View logs
echo - pm2 monit           : Monitor services
echo - pm2 restart all     : Restart all services
echo - pm2 stop all        : Stop all services
echo - pm2 save            : Save current configuration
echo.
pause
