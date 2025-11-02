# Simple Chatbot Access Guide

## ✅ Your Servers Are Running!

Now you just need to **access the chatbot from your computer's browser**.

---

## 🎯 EASIEST WAY (Works Right Now - No Setup Needed)

### Step 1: Open Terminal on Your Computer
(Not on the server, but on your Windows/Mac/Linux computer)

### Step 2: Run This Command
```bash
ssh -L 3000:localhost:3000 -L 8002:localhost:8002 chatbot@vm-185117
```

### Step 3: Keep That Terminal Open
Don't close it! The tunnel stays active while it's open.

### Step 4: Open Your Browser
Go to: **http://localhost:3000**

**That's it!** You'll see your chatbot! 🎉

---

## 🌐 Alternative: Direct Access (Requires Firewall Setup)

If you've fixed the Google Cloud firewall, you can access directly:

1. Get your server's external IP:
   ```bash
   curl ifconfig.me
   ```

2. Open in browser:
   - `http://YOUR_EXTERNAL_IP:3000`
   - `http://YOUR_EXTERNAL_IP:3000/admin`

---

## 💡 Quick Check Script

Run this on the server to see all access methods:
```bash
cd ~/zimmer-chatbot && chmod +x setup_chatbot_access.sh && ./setup_chatbot_access.sh
```

---

## ❓ Troubleshooting

**"Can't connect" from SSH tunnel?**
- Make sure the SSH command is still running
- Check servers are running: `ps aux | grep -E "(python3|npm)"`

**"Page can't be reached" from direct URL?**
- Need to fix Google Cloud firewall (see other guides)
- Or use SSH tunnel method instead

---

**The SSH tunnel method works 100% and requires no configuration!**

