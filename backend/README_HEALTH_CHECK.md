# Health Check System

سیستم health check برای بررسی سلامت چت‌بات

## نصب Dependencies

```bash
cd backend
pip install -r requirements.txt
```

یا فقط برای تست‌ها:

```bash
pip install pytest pytest-asyncio pytest-cov httpx
```

## اجرای Health Check

برای اجرای کامل health check و مشاهده گزارش:

```bash
cd backend
python health_check.py
```

این دستور:
- تمام تست‌ها را اجرا می‌کند
- درصد موفقیت را محاسبه می‌کند
- وضعیت هر ماژول را نشان می‌دهد
- لاگ کامل خطاها را در `logs/health_failures.log` ذخیره می‌کند

## اجرای تست‌ها به صورت جداگانه

```bash
# اجرای تمام تست‌ها
pytest tests/ -v

# اجرای تست‌های یک ماژول خاص
pytest tests/test_core_config.py -v

# اجرای تست‌ها با coverage
pytest tests/ --cov=. --cov-report=html
```

## ساختار تست‌ها

```
tests/
├── conftest.py              # Fixtures و تنظیمات pytest
├── test_core_config.py      # تست‌های تنظیمات
├── test_core_db.py          # تست‌های دیتابیس
├── test_models.py           # تست‌های مدل‌های دیتابیس
├── test_api_endpoints.py    # تست‌های API endpoints
├── test_services.py         # تست‌های سرویس‌ها
└── test_integration.py     # تست‌های integration
```

## خروجی Health Check

Health check گزارش زیر را نمایش می‌دهد:

```
============================================================
HEALTH CHECK REPORT
============================================================

[PASS] Tests Passed: 25
[FAIL] Tests Failed: 2
[SKIP] Tests Skipped: 1
[TOTAL] Total Tests: 28

Success Rate: 89.3%

Module Status:
------------------------------------------------------------
  [OK] api_endpoints        (0 failures)
  [OK] core_config          (0 failures)
  [OK] core_db              (0 failures)
  [FAIL] integration          (2 failures)
  [OK] models               (0 failures)
  [OK] services             (0 failures)

============================================================
[WARN] 1 modules have issues. See logs/health_failures.log for details.
============================================================
```

## لاگ خطاها

تمام خطاهای تست‌ها در فایل `logs/health_failures.log` ذخیره می‌شوند که شامل:
- نام تست fail شده
- فایل تست
- پیام خطا
- جزئیات stack trace

## تست‌های موجود

### Core Tests
- ✅ Configuration loading
- ✅ Database connection
- ✅ Model creation

### API Tests
- ✅ Health endpoint
- ✅ Chat endpoint
- ✅ FAQ endpoints (CRUD)
- ✅ Logs endpoints
- ✅ Admin endpoints

### Service Tests
- ✅ SimpleChatbot service
- ✅ FAQ Retriever
- ✅ Chat Chain
- ✅ Intent detection

### Integration Tests
- ✅ Complete chat workflow
- ✅ FAQ management workflow
- ✅ Category management

## افزودن تست جدید

برای افزودن تست جدید:

1. فایل تست را در پوشه `tests/` ایجاد کنید
2. نام فایل باید با `test_` شروع شود
3. کلاس‌های تست باید با `Test` شروع شوند
4. متدهای تست باید با `test_` شروع شوند

مثال:

```python
# tests/test_my_feature.py
import pytest

class TestMyFeature:
    def test_my_feature_works(self, test_client):
        response = test_client.get("/api/my-feature")
        assert response.status_code == 200
```

## نکات مهم

- تست‌ها از دیتابیس درون‌حافظه استفاده می‌کنند (SQLite in-memory)
- سرویس‌های خارجی (مثل OpenAI API) باید mock شوند
- برای تست‌های integration از fixture `test_client` استفاده کنید











