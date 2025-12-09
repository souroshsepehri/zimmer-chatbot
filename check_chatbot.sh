#!/usr/bin/env bash
set -e

BASE_PUBLIC="https://chatbot.zimmerai.com"
BASE_LOCAL_BACKEND="http://127.0.0.1:8001"
BASE_LOCAL_FRONTEND="http://127.0.0.1:8000"

echo "=== PM2 STATUS ==="
pm2 ls

echo
echo "=== BACKEND LOCAL HEALTH ==="
curl -sf "$BASE_LOCAL_BACKEND/api/health" || echo "BACKEND LOCAL ERROR"

echo
echo "=== FRONTEND LOCAL HEALTH ==="
curl -sf "$BASE_LOCAL_FRONTEND/" >/dev/null && echo "Frontend 200 OK" || echo "FRONTEND LOCAL ERROR"

echo
echo "=== PUBLIC API HEALTH ==="
curl -i "$BASE_PUBLIC/api/health" || echo "PUBLIC /api/health ERROR"

echo
echo "=== PUBLIC LOGS ==="
curl -i "$BASE_PUBLIC/api/logs?page=1&page_size=5" || echo "PUBLIC /api/logs ERROR"

echo
echo "=== PUBLIC FAQS ==="
curl -i "$BASE_PUBLIC/api/faqs?page=1&page_size=5" || echo "PUBLIC /api/faqs ERROR"

echo
echo "=== PUBLIC CATEGORIES ==="
curl -i "$BASE_PUBLIC/api/categories" || echo "PUBLIC /api/categories ERROR"

