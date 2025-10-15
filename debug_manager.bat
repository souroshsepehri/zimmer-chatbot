@echo off
echo Chatbot Debug Manager
echo ====================

:menu
echo.
echo Select an option:
echo 1. Run comprehensive diagnostic
echo 2. Check database status
echo 3. Test chatbot responses
echo 4. View debug logs
echo 5. Open debug web interface
echo 6. Clear debug data
echo 7. Export debug data
echo 8. Exit
echo.
set /p choice="Enter your choice (1-8): "

if "%choice%"=="1" goto diagnostic
if "%choice%"=="2" goto database
if "%choice%"=="3" goto test
if "%choice%"=="4" goto logs
if "%choice%"=="5" goto interface
if "%choice%"=="6" goto clear
if "%choice%"=="7" goto export
if "%choice%"=="8" goto exit
goto menu

:diagnostic
echo Running comprehensive diagnostic...
python debug_chatbot.py
pause
goto menu

:database
echo Checking database status...
python -c "
import sys
sys.path.append('backend')
from core.db import get_db
from models.faq import FAQ
db = next(get_db())
total = db.query(FAQ).count()
active = db.query(FAQ).filter(FAQ.is_active == True).count()
print(f'Total FAQs: {total}')
print(f'Active FAQs: {active}')
db.close()
"
pause
goto menu

:test
echo Testing chatbot responses...
python -c "
import sys
sys.path.append('backend')
from services.simple_chatbot import SimpleChatbot
bot = SimpleChatbot()
bot.load_faqs_from_db()
test_messages = ['سلام', 'قیمت', 'گارانتی']
for msg in test_messages:
    try:
        response = bot.get_answer(msg)
        print(f'{msg}: {response.get(\"answer\", \"No answer\")[:50]}...')
    except Exception as e:
        print(f'{msg}: Error - {e}')
"
pause
goto menu

:logs
echo Viewing debug logs...
if exist "logs\debug.log" (
    echo Last 20 lines of debug.log:
    echo ============================
    powershell -Command "Get-Content 'logs\debug.log' -Tail 20"
) else (
    echo No debug log found
)
pause
goto menu

:interface
echo Opening debug web interface...
echo Please make sure the server is running first
echo Opening browser...
start http://localhost:8000/api/debug/interface
pause
goto menu

:clear
echo Clearing debug data...
python -c "
import sys
sys.path.append('backend')
from services.debugger import debugger
debugger.clear_debug_data()
print('Debug data cleared')
"
pause
goto menu

:export
echo Exporting debug data...
python -c "
import sys
sys.path.append('backend')
from services.debugger import debugger
filename = debugger.export_debug_data()
print(f'Debug data exported to: {filename}')
"
pause
goto menu

:exit
echo Goodbye!
exit /b 0
