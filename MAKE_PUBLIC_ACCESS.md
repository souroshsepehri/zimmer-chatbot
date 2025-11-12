# Make Your Chatbot Publicly Accessible

## Step 1: Get Your Server's External IP

```bash
# Method 1: From Google Cloud Console
# Go to: Compute Engine → VM instances → Click on vm-185117 → Copy External IP

# Method 2: From command line (if gcloud is installed)
gcloud compute instances describe vm-185117 --zone=YOUR-ZONE --format='get(networkInterfaces[0].accessConfigs[0].natIP)'

# Method 3: Check Google Cloud Console in browser
# https://console.cloud.google.com/compute/instances
```

## Step 2: Configure Google Cloud Firewall

### Option A: Using Google Cloud Console (Easiest)

1. Go to: https://console.cloud.google.com/networking/firewalls
2. Click **"Create Firewall Rule"**
3. Fill in:
   - **Name**: `allow-chatbot-ports`
   - **Direction**: Ingress
   - **Action**: Allow
   - **Targets**: All instances in the network
   - **Source IP ranges**: `0.0.0.0/0`
   - **Protocols and ports**: 
     - Check **TCP**
     - Enter ports: `8002,3000`
4. Click **Create**

### Option B: Using gcloud command

```bash
# Allow backend port (8002)
gcloud compute firewall-rules create allow-chatbot-backend \
  --allow tcp:8002 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow chatbot backend API access"

# Allow frontend port (3000)
gcloud compute firewall-rules create allow-chatbot-frontend \
  --allow tcp:3000 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow chatbot frontend access"
```

## Step 3: Configure Server Firewall (UFW)

```bash
# Allow ports on the server
sudo ufw allow 8002/tcp
sudo ufw allow 3000/tcp
sudo ufw status
```

## Step 4: Verify Services Are Running

```bash
# Check PM2 status
pm2 status

# Test locally
curl http://localhost:8002/health
curl http://localhost:3000
```

## Step 5: Access Your Chatbot

Once firewall is configured, access from any browser:

- **Backend API**: `http://YOUR-EXTERNAL-IP:8002`
- **API Documentation**: `http://YOUR-EXTERNAL-IP:8002/docs`
- **Frontend**: `http://YOUR-EXTERNAL-IP:3000`
- **Admin Panel**: `http://YOUR-EXTERNAL-IP:3000/admin`

Replace `YOUR-EXTERNAL-IP` with your server's external IP address.

## Step 6: (Optional) Set Up Domain Name

If you have a domain name:

1. Point your domain's A record to your server's external IP
2. Set up reverse proxy (nginx) for cleaner URLs
3. Set up SSL certificate (Let's Encrypt) for HTTPS

## Troubleshooting

### Can't access from browser?

1. **Check firewall rules**: Make sure Google Cloud firewall allows ports 8002 and 3000
2. **Check server firewall**: `sudo ufw status`
3. **Check if services are running**: `pm2 status`
4. **Check server logs**: `pm2 logs`
5. **Test from server**: `curl http://localhost:8002/health`

### Port not accessible?

- Make sure Google Cloud firewall rule is created
- Check that the rule allows traffic from `0.0.0.0/0`
- Verify the rule is applied to your VM instance


