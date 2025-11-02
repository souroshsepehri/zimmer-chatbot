#!/bin/bash
# Start both backend and frontend servers

cd ~/zimmer-chatbot && \
cd backend && source venv/bin/activate && python3 app.py > ../backend.log 2>&1 & \
cd ../frontend && npm run dev > ../frontend.log 2>&1 & \
echo "Backend PID: $!" && \
sleep 2 && \
echo "Servers started! Backend: http://localhost:8002 | Frontend: http://localhost:3000" && \
echo "Logs: tail -f backend.log frontend.log"

