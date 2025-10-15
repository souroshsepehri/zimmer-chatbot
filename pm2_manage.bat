@echo off
echo PM2 Management Script for Persian Chatbot
echo ==========================================

:menu
echo.
echo Select an option:
echo 1. Start all services
echo 2. Stop all services
echo 3. Restart all services
echo 4. Reload all services (zero-downtime)
echo 5. Check status
echo 6. View logs
echo 7. Monitor services
echo 8. Save configuration
echo 9. Delete all processes
echo 10. Health check
echo 11. Exit
echo.
set /p choice="Enter your choice (1-11): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto reload
if "%choice%"=="5" goto status
if "%choice%"=="6" goto logs
if "%choice%"=="7" goto monitor
if "%choice%"=="8" goto save
if "%choice%"=="9" goto delete
if "%choice%"=="10" goto health
if "%choice%"=="11" goto exit
goto menu

:start
echo Starting all services...
pm2 start ecosystem.config.js --env production
pm2 save
goto menu

:stop
echo Stopping all services...
pm2 stop all
goto menu

:restart
echo Restarting all services...
pm2 restart all
goto menu

:reload
echo Reloading all services (zero-downtime)...
pm2 reload all
goto menu

:status
echo Current status:
pm2 status
echo.
pause
goto menu

:logs
echo Viewing logs (Press Ctrl+C to exit):
pm2 logs
goto menu

:monitor
echo Opening monitoring dashboard...
pm2 monit
goto menu

:save
echo Saving PM2 configuration...
pm2 save
echo Configuration saved!
pause
goto menu

:delete
echo Deleting all processes...
pm2 delete all
echo All processes deleted!
pause
goto menu

:health
echo Checking service health...
echo.
echo Backend Health:
curl -s http://localhost:8000/health 2>nul || echo "Backend not responding"
echo.
echo Frontend Health:
curl -s http://localhost:3000 2>nul || echo "Frontend not responding"
echo.
pause
goto menu

:exit
echo Goodbye!
exit /b 0
