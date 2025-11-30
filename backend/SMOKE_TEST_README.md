# Smoke Test Guide for Site-Scoped Chat Flow

This guide explains how to test the site-scoped chat functionality to ensure:
1. Site resolution works correctly
2. FAQ/DB retrieval is scoped to the site
3. SmartAIAgent is NOT called when no data is found
4. Fallback behavior works correctly
5. Backward compatibility is maintained

## Prerequisites

1. Backend server must be running on `http://localhost:8001`
2. Database must be initialized and accessible
3. Admin panel should be accessible at `http://localhost:8001/static/admin_panel.html`

## Running the Smoke Test

### Step 1: Run the Automated Smoke Test

```bash
cd backend
python smoke_test_site_flow.py
```

This script will:
- ✅ Check if the backend server is running
- ✅ Create a test site via admin API (domain: `testsite.com`)
- ✅ Test site resolution with various host formats
- ✅ Verify FAQ scoping to the site
- ✅ Test chat endpoint with `site_host` parameter
- ✅ Verify SmartAIAgent is NOT called (DB-only mode)
- ✅ Test backward compatibility (requests without `site_host`)
- ✅ Test unknown site handling (should return fallback)

### Step 2: Manual Testing via Admin Panel

1. Open the admin panel: `http://localhost:8001/static/admin_panel.html`
2. Click "مدیریت سایت‌ها" (Manage Sites)
3. Verify that "Test Site for Smoke Test" appears in the list
4. Optionally add some FAQs for this site:
   - Go to FAQ management
   - Add a FAQ and set `tracked_site_id` to the test site's ID

### Step 3: Test the Widget on HTML Page

1. Open the test page: `http://localhost:8001/static/widget_smoke_test.html`
2. The page simulates a page from `testsite.com`
3. Try asking a question in the chat widget
4. Verify:
   - The widget sends `site_host` parameter
   - Response is scoped to the site's FAQs
   - If no FAQs exist, you get a controlled fallback
   - SmartAIAgent is NOT called (check logs)

### Step 4: Test via cURL

Test the API directly:

```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "website-widget",
    "user_id": "test-user",
    "message": "یک سوال درباره محتوای همین سایت تست",
    "site_host": "testsite.com"
  }'
```

Expected response:
- `source` should be `"fallback"` if no FAQs exist for the site
- `source` should be `"faq"` or `"db"` if FAQs exist
- `debug_info.metadata.tracked_site_id` should contain the site ID
- `debug_info.smart_agent_raw` should be `null` (SmartAIAgent not called)

## Verification Checklist

- [ ] Smoke test script runs without errors
- [ ] Test site is created and appears in admin panel
- [ ] Site resolution works for various host formats
- [ ] Chat endpoint correctly resolves `site_host` to site record
- [ ] FAQ retrieval is scoped to the site (only site FAQs or global FAQs)
- [ ] When no data exists, fallback message is returned
- [ ] SmartAIAgent is NOT called (check `debug_info.smart_agent_raw` is `null`)
- [ ] Backward compatibility works (requests without `site_host` still work)
- [ ] Widget on HTML page correctly sends `site_host`
- [ ] Unknown sites return appropriate fallback

## Troubleshooting

### Issue: Site not resolving

- Check that the site is active (`is_active = True`)
- Verify the domain field is set correctly
- Check logs for site resolution errors

### Issue: SmartAIAgent is being called

- Verify `USE_SMART_AGENT = False` in `chat_orchestrator.py`
- Check that baseline result has `source` not in allowed sources
- Review `chat_orchestrator.py` logic for SmartAIAgent conditions

### Issue: FAQs not scoped correctly

- Verify `tracked_site_id` is passed to `answer_user_query`
- Check `simple_chatbot.load_faqs_from_db(tracked_site_id=...)`
- Verify FAQ queries filter by `tracked_site_id`

### Issue: Widget not sending site_host

- Check browser console for errors
- Verify `window.location.host` is accessible
- Check if cross-origin restrictions are blocking access
- Review `chat-window.html` site_host detection logic

## Architecture Notes

The site-scoped flow works as follows:

1. **Request arrives** with `site_host` parameter
2. **Site resolution**: `resolve_site_by_host()` normalizes host and finds TrackedSite
3. **Context setup**: `tracked_site_id` is added to context
4. **FAQ retrieval**: Only FAQs with matching `tracked_site_id` or `tracked_site_id IS NULL` (global) are loaded
5. **Baseline answering**: `answer_user_query()` uses site-scoped FAQs
6. **SmartAIAgent check**: Only called if baseline has real data AND `USE_SMART_AGENT = True`
7. **Fallback**: If no data found, return controlled fallback message

## Files Modified

- `backend/routers/chat.py` - Handles `site_host` parameter
- `backend/services/chat_orchestrator.py` - Site-scoped orchestration
- `backend/services/answering_agent.py` - Site-scoped FAQ retrieval
- `backend/services/simple_chatbot.py` - Site-scoped FAQ loading
- `backend/services/simple_retriever.py` - Site-scoped FAQ filtering
- `backend/static/chat-window.html` - Widget sends `site_host`
- `backend/schemas/chat.py` - `ChatRequest` includes `site_host`

## Next Steps

After smoke test passes:
1. Add real FAQs for test site via admin panel
2. Test with actual site domain
3. Monitor logs for any unexpected SmartAIAgent calls
4. Verify performance with multiple sites

