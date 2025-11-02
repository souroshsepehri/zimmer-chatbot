# Quick Access to Your Chatbot

## Your Chatbot URL

Once servers are running, open this in your browser:

### From SSH Tunnel (if you're using SSH to connect):
```
http://localhost:3000
```

### From External Network:
```
http://YOUR_SERVER_IP:3000
```
(Replace YOUR_SERVER_IP with your actual server IP - run `curl ifconfig.me` to get it)

## What You'll See

- **Main Page (`/`)**: Your chatbot interface - users can chat here
- **Admin Panel (`/admin`)**: Manage FAQs, categories, logs, etc.

## Find Your URL Right Now

Run this on your server:
```bash
cd ~/zimmer-chatbot
chmod +x open_chatbot.sh
./open_chatbot.sh
```

This will show you the exact URL to open.

