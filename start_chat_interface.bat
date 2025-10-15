@echo off
echo 🚀 Starting Chatbot Interface
echo ================================

echo 📡 Starting reliable server...
start /B python simple_reliable_server.py

echo ⏳ Waiting for server to start...
timeout /t 5 /nobreak > nul

echo 🌐 Opening chat interface...
start "" "chat_interface.html"

echo ✅ Chatbot interface is ready!
echo 📱 Open your browser to use the chatbot
echo 🔗 Server running on: http://localhost:8004
echo 💬 Chat interface: chat_interface.html

pause
