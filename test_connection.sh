#!/bin/bash

# Test if chatbot is accessible

FRONTEND_PORT=$(netstat -tuln 2>/dev/null | grep "300" | grep -oP ':\K[0-9]+' | head -1 || echo "3000")

echo "Testing chatbot connection..."
echo ""

# Test backend
echo "Backend (8002):"
curl -s http://localhost:8002/health && echo " ✅" || echo " ❌"

# Test frontend
echo "Frontend ($FRONTEND_PORT):"
if curl -s http://localhost:$FRONTEND_PORT | head -1 | grep -q "html\|<!DOCTYPE"; then
    echo " ✅ Frontend is serving HTML"
else
    echo " ❌ Frontend not responding properly"
fi

echo ""
echo "If both show ✅, servers are working!"
echo "Access via SSH tunnel from your computer:"
echo "  ssh -L 8080:localhost:$FRONTEND_PORT chatbot@vm-185117"
echo "  Then open: http://localhost:8080"

