#!/bin/bash
# Simple one-command startup for chatbot

cd ~/zimmer-chatbot

# Stop old processes
pkill -f "python3 app.py" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
pkill -f "next dev" 2>/dev/null
kill -9 $(lsof -ti:8002) 2>/dev/null 2>/dev/null
for p in 3000 3001 3002 3003; do kill -9 $(lsof -ti:$p) 2>/dev/null 2>/dev/null; done
sleep 2

# Start backend
cd backend && source venv/bin/activate 2>/dev/null && python3 app.py > ../backend.log 2>&1 & cd .. && sleep 5

# Start frontend  
cd frontend && npm run dev > ../frontend.log 2>&1 & cd .. && sleep 8

# Show URLs
IP=$(hostname -I | awk '{print $1}')
PORT=$(netstat -tuln 2>/dev/null | grep "300" | grep -oP ':\K[0-9]+' | head -1 || echo "3000")
echo "✅ Servers started!"
echo "Frontend: http://$IP:$PORT"
echo "Backend:  http://$IP:8002"
echo "Admin:    http://$IP:$PORT/admin"

