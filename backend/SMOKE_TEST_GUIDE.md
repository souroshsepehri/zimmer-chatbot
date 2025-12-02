# Smoke Test Guide - Site-Scoped Chat Flow

This guide helps you test the site-scoped chat functionality.

## Prerequisites

1. Backend server running on `http://localhost:8001`
2. Database initialized with all tables created
3. Admin panel accessible

## Test Steps

### Step 1: Add Test Site via Admin Panel

1. Open admin panel: `http://localhost:8001/static/admin_panel.html`
2. Click "مدیریت سایت‌ها" (Manage Sites)
3. Add a new site with:
   - **Name**: Test Site
   - **URL**: `https://testsite.com`
   - **Description**: Test site for smoke testing
   - **Active**: ✓ (checked)
4. Click "ذخیره" (Save)
5. Verify the site appears in the list

### Step 2: Run Automated Smoke Test

```bash
cd backend
python test_site_flow.py
```

This script will:
- Create a test site in the database (if not exists)
- Test site resolution with various host formats
- Test chat endpoint with `site_host` parameter
- Verify backward compatibility (requests without `site_host`)

### Step 3: Test with cURL

```bash
# Test 1: Chat with site_host (should resolve site)
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "website-widget",
    "user_id": "test-user",
    "message": "یک سوال درباره محتوای همین سایت تست",
    "site_host": "testsite.com"
  }'

# Test 2: Chat without site_host (backward compatibility)
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "telegram",
    "user_id": "test-user-2",
    "message": "سلام"
  }'

# Test 3: Chat with unknown site_host (should return fallback)
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "website-widget",
    "user_id": "test-user-3",
    "message": "سوال تست",
    "site_host": "unknown-site.com"
  }'
```

### Step 4: Test Widget on HTML Page

1. Open `http://localhost:8001/static/widget_test_page.html` in your browser
2. The page will automatically load the widget
3. Try asking:
   - A question related to the site (if you have FAQs for that site)
   - An unrelated question (should return fallback message)
4. Verify:
   - Widget loads correctly
   - Chat works
   - Only site-specific answers are returned
   - Fallback message appears for unrelated questions

## Expected Behavior

### ✅ Success Criteria

1. **Site Resolution**:
   - `site_host: "testsite.com"` resolves to the test site record
   - `site_host: "www.testsite.com"` also resolves (normalized)
   - `site_host: "unknown-site.com"` returns `null` (no site found)

2. **FAQ/DB Scoping**:
   - FAQs are filtered by `tracked_site_id` when `site_host` is provided
   - Only FAQs for that site (or global FAQs with `tracked_site_id = NULL`) are returned

3. **Fallback Behavior**:
   - When no site data exists, returns controlled fallback message
   - SmartAIAgent is **NOT** called when baseline has no data
   - Response includes `"source": "fallback"` and `"success": false`

4. **Backward Compatibility**:
   - Requests without `site_host` still work (for Telegram, etc.)
   - Existing clients continue to function normally

### 🔍 Verification Points

Check the response JSON for:

```json
{
  "answer": "...",
  "source": "faq" | "fallback" | "error",
  "success": true | false,
  "debug_info": {
    "metadata": {
      "tracked_site_id": 1,
      "tracked_site_name": "Test Site",
      "tracked_site_domain": "testsite.com",
      "site_host": "testsite.com"
    },
    "smart_agent_raw": null  // Should be null (not called)
  }
}
```

## Troubleshooting

### Issue: Site not resolving

- Check that site is created in database
- Verify `domain` field is set correctly (normalized, no www, no port)
- Check logs for site resolution messages

### Issue: SmartAIAgent still being called

- Verify `USE_SMART_AGENT = False` in `chat_orchestrator.py`
- Check that `baseline_result.source` is not in allowed set
- Review logs to see why SmartAIAgent was called

### Issue: Generic AI answers appearing

- Check that `baseline_result.success` is `False` when no data
- Verify fallback message is returned
- Ensure SmartAIAgent is not called for fallback cases

## Logs to Check

Look for these log messages:

```
INFO: Resolved site: Test Site (domain: testsite.com) for host: testsite.com
INFO: Processing chat for site: Test Site (id: 1, domain: testsite.com)
INFO: DB-only mode: using baseline answer. source=fallback, has_answer=False, site_id=1, site_host=testsite.com
```

If you see SmartAIAgent being called when it shouldn't, check the logs to find the path that's calling it.


