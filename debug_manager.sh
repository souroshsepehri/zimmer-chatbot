#!/bin/bash

echo "Chatbot Debug Manager"
echo "===================="

while true; do
    echo ""
    echo "Select an option:"
    echo "1. Run comprehensive diagnostic"
    echo "2. Check database status"
    echo "3. Test chatbot responses"
    echo "4. View debug logs"
    echo "5. Open debug web interface"
    echo "6. Clear debug data"
    echo "7. Export debug data"
    echo "8. Exit"
    echo ""
    read -p "Enter your choice (1-8): " choice

    case $choice in
        1)
            echo "Running comprehensive diagnostic..."
            python debug_chatbot.py
            read -p "Press Enter to continue..."
            ;;
        2)
            echo "Checking database status..."
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
            read -p "Press Enter to continue..."
            ;;
        3)
            echo "Testing chatbot responses..."
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
            read -p "Press Enter to continue..."
            ;;
        4)
            echo "Viewing debug logs..."
            if [ -f "logs/debug.log" ]; then
                echo "Last 20 lines of debug.log:"
                echo "============================"
                tail -20 logs/debug.log
            else
                echo "No debug log found"
            fi
            read -p "Press Enter to continue..."
            ;;
        5)
            echo "Opening debug web interface..."
            echo "Please make sure the server is running first"
            echo "Opening browser..."
            if command -v xdg-open &> /dev/null; then
                xdg-open http://localhost:8000/api/debug/interface
            elif command -v open &> /dev/null; then
                open http://localhost:8000/api/debug/interface
            else
                echo "Please open: http://localhost:8000/api/debug/interface"
            fi
            read -p "Press Enter to continue..."
            ;;
        6)
            echo "Clearing debug data..."
            python -c "
import sys
sys.path.append('backend')
from services.debugger import debugger
debugger.clear_debug_data()
print('Debug data cleared')
"
            read -p "Press Enter to continue..."
            ;;
        7)
            echo "Exporting debug data..."
            python -c "
import sys
sys.path.append('backend')
from services.debugger import debugger
filename = debugger.export_debug_data()
print(f'Debug data exported to: {filename}')
"
            read -p "Press Enter to continue..."
            ;;
        8)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice. Please try again."
            ;;
    esac
done
