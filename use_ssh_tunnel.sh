#!/bin/bash

echo "========================================"
echo "   SSH Tunnel Solution (No Firewall Changes)"
echo "========================================"
echo ""

# Get frontend port
FRONTEND_PORT=$(netstat -tuln | grep "300" | grep -oP ':\K[0-9]+' | head -1 || echo "3000")

echo "✅ Use SSH Port Forwarding from your local computer!"
echo ""
echo "On your LOCAL computer (Windows/Mac/Linux), run:"
echo ""
echo "ssh -L 3000:localhost:$FRONTEND_PORT -L 8002:localhost:8002 chatbot@vm-185117"
echo ""
echo "Then open in your browser:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8002"
echo "  Admin:    http://localhost:3000/admin"
echo ""
echo "This creates a secure tunnel - no firewall changes needed!"
echo ""

