#!/bin/bash

# Get Server IP Address - Multiple Methods
echo "========================================"
echo "   Getting Server IP Address"
echo "========================================"
echo ""

echo "Method 1: hostname -I"
hostname -I | awk '{print $1}'
echo ""

echo "Method 2: ip addr show"
ip addr show | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | cut -d/ -f1
echo ""

echo "Method 3: ifconfig"
ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1
echo ""

echo "Method 4: External IP (if accessible)"
curl -s https://api.ipify.org 2>/dev/null || echo "External IP service not accessible"
echo ""

echo "Method 5: Google DNS"
dig +short myip.opendns.com @resolver1.opendns.com 2>/dev/null || echo "DNS method not available"
echo ""

echo "========================================"
echo "   Your Server IP Addresses"
echo "========================================"
echo ""
echo "Internal IP (for server access):"
hostname -I | awk '{print $1}'
echo ""
echo "If you need external IP, check your cloud provider dashboard"
echo ""

