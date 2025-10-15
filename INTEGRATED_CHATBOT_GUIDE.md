# 🤖 Integrated Chatbot System Guide

## Overview
Your chatbot system combines **FAQ database** + **URL agent** for comprehensive responses.

## 🎯 Main Chatbot Endpoints

### 1. **Primary Chatbot (FAQ + Web Content)**
```bash
POST /api/dual-answer
```
**Request:**
```json
{
  "question": "سؤال شما",
  "use_primary_only": false,    // Use FAQ only
  "use_secondary_only": false,  // Use web content only
  "website_filter": null        // Filter by specific website
}
```

### 2. **FAQ-Only Chatbot**
```bash
POST /api/simple-chat
```
**Request:**
```json
{
  "message": "سؤال شما"
}
```

### 3. **Enhanced Chat with URL Support**
```bash
POST /api/chat-with-url
```
**Request:**
```json
{
  "question": "سؤال شما",
  "context_preference": "both",  // "faq", "web", or "both"
  "website_filter": null
}
```

## 🌐 Adding Websites to Your Chatbot

### Add a Website:
```bash
POST /api/add-website
```
**Request:**
```json
{
  "url": "https://example.com",
  "max_pages": 50
}
```

### List Added Websites:
```bash
GET /api/websites
```

### Get System Stats:
```bash
GET /api/stats
```

## 🎮 Usage Examples

### Example 1: FAQ + Web Content
```bash
curl -X POST "http://localhost:8002/api/dual-answer" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "خدمات شما چیست؟",
    "use_primary_only": false,
    "use_secondary_only": false
  }'
```

### Example 2: FAQ Only
```bash
curl -X POST "http://localhost:8002/api/simple-chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "ساعات کاری شما چیست؟"
  }'
```

### Example 3: Add Website
```bash
curl -X POST "http://localhost:8002/api/add-website" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://yourcompany.com",
    "max_pages": 30
  }'
```

## 🌐 Web Interfaces

### Main Interface:
- **URL**: http://localhost:8002
- **Features**: FAQ + Web content chatbot
- **Language**: Persian (RTL)

### Admin Panel:
- **URL**: http://localhost:8002/admin
- **Features**: Manage FAQs, websites, view stats

### API Documentation:
- **URL**: http://localhost:8002/docs
- **Features**: Interactive API testing

## 🤖 Chatbot Widget for External Websites

### Widget Code:
```html
<!-- Chatbot Widget -->
<div id="chatbot-widget"></div>
<script>
(function() {
    var script = document.createElement('script');
    script.src = 'http://localhost:8002/static/chatbot-widget.js';
    script.async = true;
    document.head.appendChild(script);
})();
</script>
```

### Widget Features:
- ✅ Persian language support
- ✅ FAQ + Web content responses
- ✅ Responsive design
- ✅ Easy integration

## 🔧 Configuration Options

### Context Preferences:
- `"faq"` - Use only FAQ database
- `"web"` - Use only web content
- `"both"` - Use both databases (recommended)

### Website Filter:
- `null` - Search all websites
- `"https://example.com"` - Search specific website only

## 📊 Response Format

### Dual Answer Response:
```json
{
  "answer": "پاسخ ترکیبی از FAQ و محتوای وب",
  "sources_used": ["FAQ Database", "Website Content"],
  "primary_success": true,
  "secondary_success": true,
  "search_metadata": {
    "timestamp": "2024-01-01T12:00:00",
    "databases_searched": ["primary_faq", "secondary_web"]
  }
}
```

## 🚀 Getting Started

1. **Start the server:**
   ```bash
   python start_with_url_agent.py
   ```

2. **Add your FAQ data** (if not already done)

3. **Add websites to knowledge base:**
   ```bash
   curl -X POST "http://localhost:8002/api/add-website" \
     -H "Content-Type: application/json" \
     -d '{"url": "https://yourwebsite.com", "max_pages": 50}'
   ```

4. **Test the chatbot:**
   - Visit: http://localhost:8002
   - Or use API endpoints directly

## 🎯 Best Practices

1. **Use dual-answer endpoint** for best results
2. **Add relevant websites** to expand knowledge
3. **Monitor stats** to see system performance
4. **Use website filters** for specific content
5. **Test with Persian questions** for best experience

## 🔍 Troubleshooting

### If website scraping fails:
- Check if website is accessible
- Try with smaller `max_pages` value
- Check server logs for errors

### If FAQ responses are poor:
- Ensure FAQ database has data
- Check database connection
- Use `use_primary_only: true` for FAQ-only mode

### If API calls fail:
- Check server is running on port 8002
- Verify JSON format
- Check API documentation at /docs
