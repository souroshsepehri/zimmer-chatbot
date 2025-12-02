#!/bin/bash

echo "=========================================="
echo "  Checking Backend Error"
echo "=========================================="

echo "=== Backend Error Logs ==="
pm2 logs chatbot-backend --err --lines 20 --nostream

echo ""
echo "=== Backend Output Logs ==="
pm2 logs chatbot-backend --out --lines 10 --nostream

echo ""
echo "=== Backend Process Info ==="
pm2 describe chatbot-backend | head -30

