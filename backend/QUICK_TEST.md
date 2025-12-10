# Quick Test Instructions

## 1. Add Test Site via Admin Panel

1. Start your backend server:
   ```bash
   cd backend
   # Your server start command (e.g., uvicorn main:app --reload --port 8001)
   ```

2. Open admin panel: http://localhost:8001/static/admin_panel.html

3. Click "مدیریت سایت‌ها" (Manage Sites)

4. Add a new site:
   - **Name**: Test Site
   - **URL**: `https://testsite.com`
   - **Description**: Test site for smoke testing
   - **Active**: ✓ (checked)

5. Click "ذخیره" (Save) and verify it appears in the list

## 2. Test with cURL

```bash
cd backend

# Test 1: Chat with site_host (should resolve site and return fallback if no FAQs)
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "website-widget",
    "user_id": "test-user",
    "message": "یک سوال درباره محتوای همین سایت تست",
    "site_host": "testsite.com"
  }'
```

**Expected Response:**
- `"source": "fallback"` (if no FAQs for this site)
- `"success": false`
- `"debug_info.metadata.tracked_site_id"` should be present
- `"debug_info.smart_agent_raw"` should be `null` (SmartAIAgent NOT called)

## 3. Test Widget on HTML Page

1. Open: http://localhost:8001/static/widget_test_page.html

2. The widget should load in the bottom-right corner

3. Try asking:
   - A question (should return fallback if no site-specific FAQs)
   - Verify the answer is site-specific, not generic AI

## 4. Run Automated Test

```bash
cd backend
python test_site_flow.py
```

This will:
- Create test site if needed
- Test site resolution
- Test chat endpoint with various scenarios
- Verify SmartAIAgent is NOT called

## Verification Checklist

- [ ] Test site appears in admin panel
- [ ] `site_host: "testsite.com"` resolves to site record
- [ ] Chat request with `site_host` includes site info in response
- [ ] When no FAQs exist, returns fallback (not generic AI answer)
- [ ] `smart_agent_raw` is `null` in debug_info
- [ ] Requests without `site_host` still work (backward compatibility)
- [ ] Widget loads and works on test page

## Troubleshooting

If you see generic AI answers:
1. Check logs for any SmartAIAgent calls
2. Verify `USE_SMART_AGENT = False` in `chat_orchestrator.py`
3. Check that `baseline_result.source == "fallback"` when no data
4. Review the response `debug_info` to see what path was taken












