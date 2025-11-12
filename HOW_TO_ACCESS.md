# How to Access Your Chatbot Using Server IP

## Step 1: Find Your Server IP Address

Run this command on your cloud server:

```bash
# Method 1: Get local IP
hostname -I

# Method 2: Get external/public IP
curl ifconfig.me

# Method 3: Get both
echo "Local IP: $(hostname -I | awk '{print $1}')"
echo "External IP: $(curl -s ifconfig.me)"
```

**Example output:**
```
Local IP: 10.128.0.2
External IP: 34.123.45.67
```

## Step 2: Access URLs

Once you have your IP address, use these URLs:

### From Your Computer (External Access)

If you're accessing from your local computer:

**Frontend (Main Chatbot):**
```
http://YOUR-EXTERNAL-IP:8000
```

**Admin Panel:**
```
http://YOUR-EXTERNAL-IP:8000/admin
```

**Backend API:**
```
http://YOUR-EXTERNAL-IP:8001
```

**API Documentation:**
```
http://YOUR-EXTERNAL-IP:8001/docs
```

### From the Server Itself (Local Access)

If you're SSH'd into the server:

**Frontend:**
```
http://localhost:8000
# OR
http://SERVER-LOCAL-IP:8000
```

**Backend:**
```
http://localhost:8001
# OR
http://SERVER-LOCAL-IP:8001
```

## Step 3: Make Sure Firewall Allows Access

### For Google Cloud:

1. Go to Google Cloud Console
2. Navigate to **VPC Network** > **Firewall Rules**
3. Create a new rule or edit existing:
   - **Name**: `allow-chatbot-ports`
   - **Direction**: Ingress
   - **Action**: Allow
   - **Targets**: All instances in the network
   - **Source IP ranges**: `0.0.0.0/0` (or specific IPs)
   - **Protocols and ports**: 
     - TCP: `8000` (Frontend)
     - TCP: `8001` (Backend)

### For UFW (Ubuntu Firewall):

```bash
sudo ufw allow 8000/tcp
sudo ufw allow 8001/tcp
sudo ufw status
```

### For iptables:

```bash
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8001 -j ACCEPT
sudo iptables-save
```

## Step 4: Test Connection

### From Your Computer:

```bash
# Test frontend
curl http://YOUR-EXTERNAL-IP:8000

# Test backend
curl http://YOUR-EXTERNAL-IP:8001/health
```

### From Browser:

1. Open your web browser
2. Type in the address bar: `http://YOUR-EXTERNAL-IP:8000`
3. Press Enter

## Example

If your server's external IP is `34.123.45.67`:

- **Chatbot**: `http://34.123.45.67:8000`
- **Admin**: `http://34.123.45.67:8000/admin`
- **API Docs**: `http://34.123.45.67:8001/docs`

## Troubleshooting

### If you get "Connection Refused":

1. **Check if services are running:**
```bash
ps aux | grep uvicorn
ps aux | grep "npm run dev"
```

2. **Check if ports are listening:**
```bash
netstat -tuln | grep 8000
netstat -tuln | grep 8001
```

3. **Check firewall:**
```bash
sudo ufw status
# or
sudo iptables -L -n
```

### If you get "Timeout":

1. **Check Google Cloud Firewall Rules**
2. **Verify your server's external IP is correct**
3. **Check if services are bound to 0.0.0.0 (not just localhost)**

### If you can access from server but not from browser:

This means firewall is blocking. Open the ports in your cloud provider's firewall settings.

## Quick Script to Show Your Access URLs

Run this on your server:

```bash
#!/bin/bash
LOCAL_IP=$(hostname -I | awk '{print $1}')
EXTERNAL_IP=$(curl -s ifconfig.me 2>/dev/null || echo "Unable to detect")

echo "========================================"
echo "   Your Chatbot Access URLs"
echo "========================================"
echo ""
echo "📍 From Your Computer (Use External IP):"
echo ""
if [ "$EXTERNAL_IP" != "Unable to detect" ]; then
    echo "  Frontend:  http://$EXTERNAL_IP:8000"
    echo "  Admin:     http://$EXTERNAL_IP:8000/admin"
    echo "  Backend:   http://$EXTERNAL_IP:8001"
    echo "  API Docs:  http://$EXTERNAL_IP:8001/docs"
else
    echo "  External IP: Unable to detect"
    echo "  Use Local IP: http://$LOCAL_IP:8000"
fi
echo ""
echo "📍 From Server (Use Local IP):"
echo ""
echo "  Frontend:  http://localhost:8000"
echo "  Backend:   http://localhost:8001"
echo ""
echo "⚠️  Make sure ports 8000 and 8001 are open in firewall!"
echo ""
```

Save this as `show_urls.sh`, make it executable, and run it:
```bash
chmod +x show_urls.sh
./show_urls.sh
```

