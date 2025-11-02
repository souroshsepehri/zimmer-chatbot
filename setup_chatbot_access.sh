#!/bin/bash

echo "========================================"
echo "   Setting Up Chatbot Access"
echo "========================================"
echo ""

# Check if servers are running
if ! pgrep -f "python3 app.py" > /dev/null; then
    echo "❌ Backend is not running. Starting it..."
    cd ~/zimmer-chatbot/backend
    source venv/bin/activate 2>/dev/null || true
    python3 app.py > ../backend.log 2>&1 &
    sleep 5
    echo "✅ Backend started"
else
    echo "✅ Backend is running"
fi

if ! pgrep -f "npm run dev" > /dev/null && ! pgrep -f "next dev" > /dev/null; then
    echo "❌ Frontend is not running. Starting it..."
    cd ~/zimmer-chatbot/frontend
    npm run dev > ../frontend.log 2>&1 &
    sleep 10
    echo "✅ Frontend started"
else
    echo "✅ Frontend is running"
fi

# Get ports and IPs
FRONTEND_PORT=$(netstat -tuln 2>/dev/null | grep "300" | grep -oP ':\K[0-9]+' | head -1 || echo "3000")
SERVER_IP=$(hostname -I | awk '{print $1}')
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s icanhazip.com 2>/dev/null || echo "Unable to detect")

echo ""
echo "========================================"
echo "   Chatbot Access URLs"
echo "========================================"
echo ""
echo "📍 METHOD 1: SSH Tunnel (Easiest - Works Right Now)"
echo ""
echo "On your LOCAL computer, run this command:"
echo ""
echo "  ssh -L 3000:localhost:$FRONTEND_PORT -L 8002:localhost:8002 chatbot@vm-185117"
echo ""
echo "Then open in your browser:"
echo "  ✅ http://localhost:3000"
echo "  ✅ http://localhost:3000/admin"
echo ""
echo "📍 METHOD 2: Direct Access (If Firewall Fixed)"
echo ""
if [ "$EXTERNAL_IP" != "Unable to detect" ]; then
    echo "  Frontend: http://$EXTERNAL_IP:$FRONTEND_PORT"
    echo "  Admin:    http://$EXTERNAL_IP:$FRONTEND_PORT/admin"
else
    echo "  Frontend: http://$SERVER_IP:$FRONTEND_PORT"
    echo "  Admin:    http://$SERVER_IP:$FRONTEND_PORT/admin"
fi
echo ""

# Create a local HTML file that can be opened
cat > ~/open_chatbot.html << EOF
<!DOCTYPE html>
<html>
<head>
    <title>Chatbot Access</title>
    <meta charset="utf-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 2em;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .method {
            background: #f5f5f5;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }
        .method h2 {
            color: #667eea;
            margin-bottom: 15px;
            font-size: 1.3em;
        }
        .method ol {
            margin-left: 20px;
            line-height: 1.8;
        }
        .method code {
            background: #333;
            color: #0f0;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }
        .button {
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 8px;
            margin-top: 10px;
            font-weight: bold;
            transition: transform 0.2s;
        }
        .button:hover {
            transform: translateY(-2px);
        }
        .note {
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin-top: 20px;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Chatbot Access</h1>
        <p class="subtitle">Your chatbot servers are running. Follow these steps:</p>
        
        <div class="method">
            <h2>📌 Method 1: SSH Tunnel (Recommended)</h2>
            <ol>
                <li>Open your terminal/command prompt</li>
                <li>Run this command:</li>
                <li><code>ssh -L 3000:localhost:$FRONTEND_PORT -L 8002:localhost:8002 chatbot@vm-185117</code></li>
                <li>Keep that terminal open</li>
                <li>Open in browser: <a href="http://localhost:$FRONTEND_PORT" class="button">Open Chatbot</a></li>
            </ol>
        </div>
        
        <div class="method">
            <h2>🌐 Method 2: Direct Access</h2>
            <p>If firewall is configured, access directly:</p>
            <p><strong>Frontend:</strong> http://$EXTERNAL_IP:$FRONTEND_PORT</p>
            <p><strong>Admin:</strong> http://$EXTERNAL_IP:$FRONTEND_PORT/admin</p>
        </div>
        
        <div class="note">
            <strong>Note:</strong> If Method 2 doesn't work, use Method 1 (SSH Tunnel). 
            It works immediately without any firewall configuration.
        </div>
    </div>
</body>
</html>
EOF

echo "✅ Created access guide at: ~/open_chatbot.html"
echo ""
echo "Download this file to your computer and open it in a browser"
echo "Or view it on server with: cat ~/open_chatbot.html"
echo ""

