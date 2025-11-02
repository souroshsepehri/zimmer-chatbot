# Fix Google Cloud VM Firewall Access

## Method 1: Using Google Cloud Console (Easiest)

1. Go to: https://console.cloud.google.com/
2. Navigate to: **VPC Network** → **Firewall Rules**
3. Click **CREATE FIREWALL RULE**
4. Configure:
   - **Name**: `allow-chatbot-ports`
   - **Direction**: Ingress
   - **Action**: Allow
   - **Targets**: All instances in the network
   - **Source IP ranges**: `0.0.0.0/0` (or your specific IP)
   - **Protocols and ports**: 
     - TCP: `3000,3001,3002,3003,8002`
5. Click **CREATE**

## Method 2: Check Current Firewall Rules

In Google Cloud Console:
- Go to **VPC Network** → **Firewall Rules**
- Look for rules that might be blocking traffic
- Make sure there's a rule allowing HTTP/HTTPS traffic

## Method 3: Using Metadata Service (from VM itself)

The VM can tag itself to use existing firewall rules.

