# Alternative Ways to Access Your Chatbot

## Option 1: Using ngrok (Tunnel - No Firewall Needed)

Create a secure tunnel without configuring firewall:

```bash
# Install ngrok
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
tar -xzf ngrok-v3-stable-linux-amd64.tgz
sudo mv ngrok /usr/local/bin/

# Or download from: https://ngrok.com/download

# Start tunnel for frontend
ngrok http 3000

# In another terminal, start tunnel for backend
ngrok http 8002
```

You'll get public URLs like:
- `https://abc123.ngrok.io` (frontend)
- `https://xyz789.ngrok.io` (backend)

**Pros:** No firewall configuration needed, HTTPS included
**Cons:** Free tier has session limits, URLs change on restart

## Option 2: Using Cloudflare Tunnel (Free, Permanent)

```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# Login to Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create chatbot

# Run tunnel
cloudflared tunnel --url http://localhost:3000
```

**Pros:** Free, permanent URLs, HTTPS
**Cons:** Requires Cloudflare account

## Option 3: Using SSH Tunnel (From Your Local Machine)

Access through SSH tunnel without opening ports:

```bash
# On your local Windows machine (PowerShell)
ssh -L 3000:localhost:3000 chatbot@vm-185117
ssh -L 8002:localhost:8002 chatbot@vm-185117
```

Then access:
- `http://localhost:3000` (frontend)
- `http://localhost:8002` (backend)

**Pros:** Secure, no firewall changes
**Cons:** Requires SSH connection, only accessible from your machine

## Option 4: Using Reverse Proxy (nginx) with Domain

Set up nginx reverse proxy with a domain name:

```bash
# Install nginx
sudo apt-get update
sudo apt-get install nginx -y

# Create nginx config
sudo nano /etc/nginx/sites-available/chatbot

# Add configuration:
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://localhost:8002;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# Enable site
sudo ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Pros:** Professional, can use domain name, single port (80)
**Cons:** Requires domain name, more setup

## Option 5: Using Google Cloud Load Balancer

Set up a load balancer with static IP:

1. Go to Google Cloud Console → Network Services → Load Balancing
2. Create HTTP(S) Load Balancer
3. Configure backend services
4. Get static IP address
5. Point domain to static IP

**Pros:** Professional, scalable, static IP
**Cons:** Costs money, more complex setup

## Option 6: Using Vercel/Netlify (Frontend Only)

Deploy frontend to Vercel/Netlify, keep backend on server:

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy frontend
cd ~/chatbot2/frontend
vercel

# Update API URL in frontend to point to your backend
```

**Pros:** Free hosting, automatic HTTPS, CDN
**Cons:** Frontend only, backend still needs to be accessible

## Option 7: Using Port Forwarding (Local Network)

If you're on the same network:

```bash
# Access using internal IP
http://INTERNAL-IP:3000
```

**Pros:** Simple, no external access needed
**Cons:** Only works on same network

## Quick Comparison

| Method | Difficulty | Cost | Security | Best For |
|--------|-----------|------|----------|----------|
| Google Cloud Firewall | Easy | Free | High | Production |
| ngrok | Very Easy | Free/Paid | Medium | Testing |
| SSH Tunnel | Easy | Free | High | Development |
| Cloudflare Tunnel | Medium | Free | High | Production |
| nginx Reverse Proxy | Medium | Free | High | Production |
| Load Balancer | Hard | Paid | High | Enterprise |

## Recommended for You

**For Quick Testing:** Use ngrok
**For Production:** Configure Google Cloud Firewall (what we started)
**For Development:** Use SSH Tunnel



