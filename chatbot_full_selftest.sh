#!/usr/bin/env bash
set -u  # اگه متغیر بدون مقدار استفاده بشه، خطا بده نه این‌که بی‌صدا رد شه

ROOT_DIR="/home/chatbot/chatbot2"
BACKEND_PORT=8001
DOMAIN="chatbot.zimmerai.com"

echo "=== [0] محیط و سرویس‌ها ==="
cd "$ROOT_DIR" || { echo "ROOT_DIR not found"; exit 1; }

echo
echo "--- سیستم ---"
uname -a || true
python3 --version || true
echo

echo "--- PM2 list ---"
pm2 list || true
echo

echo "=== [1] هِلث backend روی لوپ‌بک ==="
curl -s -o /dev/null -w "HTTP %{http_code}\n" "http://127.0.0.1:${BACKEND_PORT}/health" || echo "health FAILED"
echo

echo "=== [2] چک چند endpoint اصلی روی لوپ‌بک (بدون nginx) ==="

echo "- GET /api/admin/bot-settings"
curl -s -w "\nHTTP %{http_code}\n" "http://127.0.0.1:${BACKEND_PORT}/api/admin/bot-settings" || echo "bot-settings FAILED"
echo

echo "- GET /api/faqs?page_size=3"
curl -s -w "\nHTTP %{http_code}\n" "http://127.0.0.1:${BACKEND_PORT}/api/faqs?page_size=3" || echo "faqs FAILED"
echo

echo "- GET /api/categories"
curl -s -w "\nHTTP %{http_code}\n" "http://127.0.0.1:${BACKEND_PORT}/api/categories" || echo "categories FAILED"
echo

echo "- ساده‌ترین تست POST /api/chat"
curl -s -w "\nHTTP %{http_code}\n" \
  -H "Content-Type: application/json" \
  -d '{"message":"سلام، خودت رو معرفی کن","session_id":"selftest-session","user_id":"selftest-user"}' \
  "http://127.0.0.1:${BACKEND_PORT}/api/chat" || echo "chat FAILED"
echo

echo "=== [3] تست از پشت nginx با HTTPS روی دامنه ==="

echo "- GET https://${DOMAIN}/health"
curl -k -s -w "\nHTTP %{http_code}\n" "https://${DOMAIN}/health" || echo "nginx health FAILED"
echo

echo "- GET https://${DOMAIN}/api/admin/bot-settings"
curl -k -s -w "\nHTTP %{http_code}\n" "https://${DOMAIN}/api/admin/bot-settings" || echo "nginx bot-settings FAILED"
echo

echo "- POST https://${DOMAIN}/api/chat (ساده)"
curl -k -s -w "\nHTTP %{http_code}\n" \
  -H "Content-Type: application/json" \
  -d '{"message":"سلام از پشت nginx","session_id":"nginx-session","user_id":"nginx-user"}' \
  "https://${DOMAIN}/api/chat" || echo "nginx chat FAILED"
echo

echo "=== [4] وجود فایل تنظیمات بات (bot_settings.json) ==="
find "$ROOT_DIR" -maxdepth 4 -name "bot_settings.json" -print || echo "هیچ bot_settings.json ای پیدا نشد"
echo

echo "=== [5] اجرای چند تست pytest هسته API (بدون تست‌های سنگین) ==="
cd "$ROOT_DIR/backend" || { echo "backend dir not found"; exit 1; }

if [ -x "venv/bin/python" ]; then
  source venv/bin/activate
  echo "--- pytest: تست‌های پایه ---"
  pytest tests/test_system_status.py tests/test_api_endpoints.py -q || echo "pytest FAILED (طبیعیه اگه بعضی تست‌ها هنوز تنظیم نباشن)"
  deactivate || true
else
  echo "venv/bin/python پیدا نشد، pytest اسکیپ شد."
fi

echo
echo "=== [DONE] تست خودکار تمام شد. خروجی بالا رو بده تا با هم آنالیز کنیم. ==="
