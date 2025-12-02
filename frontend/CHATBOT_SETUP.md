# Chatbot API Integration Setup

## Environment Configuration

Create a `.env.local` file in the `frontend` directory with the following:

```env
NEXT_PUBLIC_CHATBOT_API_BASE=https://chatbot.zimmerai.com
```

This environment variable is used by the API proxy route at `/api/chatbot`.

## API Route

The chatbot API proxy is located at:
- **Path**: `app/api/chatbot/route.ts`
- **Endpoint**: `POST /api/chatbot`

### Request Format

```json
{
  "message": "سلام، چطور می‌تونم کمک بگیرم؟",
  "style": "friendly"  // optional, defaults to "auto"
}
```

### Response Format

```json
{
  "success": true,
  "response": "سلام! خوش اومدی...",
  "style": "friendly",
  "raw": {
    "response": "...",
    "style": "friendly",
    "response_time": 1.23,
    "web_content_used": false,
    "urls_processed": [],
    "context_used": false,
    "timestamp": "2024-01-01T12:00:00"
  }
}
```

## Important Note

⚠️ **Static Export Limitation**: The Next.js config currently has `output: 'export'` which means API routes won't work in production static builds. 

For development (`npm run dev`), the API route will work fine.

For production, you have two options:

1. **Remove static export** (if you need API routes in production):
   ```js
   // next.config.js
   const nextConfig = {
     // Remove: output: 'export',
     trailingSlash: true,
     // ... rest of config
   }
   ```

2. **Use direct API calls** from the frontend to `https://chatbot.zimmerai.com/api/smart-agent/chat` (bypassing the proxy)

## Usage Example

```typescript
const response = await fetch('/api/chatbot', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'سلام',
    style: 'friendly'
  })
});

const data = await response.json();
if (data.success) {
  console.log(data.response);
  console.log('Style used:', data.style);
}
```


















