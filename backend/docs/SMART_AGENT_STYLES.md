# Smart Agent Styles API Documentation

## Overview

The Smart Agent (`/api/smart-agent/chat`) supports multiple response styles/tones that can be controlled by the frontend. The system uses Persian-first instructions to guide the LLM's response tone.

## Supported Style Keys

The following 7 styles are available:

| Key | Persian Label | Description |
|-----|---------------|-------------|
| `auto` | خودکار | سیستم خودش بسته به سوال و زمینه، لحن مناسب را انتخاب می‌کند. |
| `formal` | رسمی و حرفه‌ای | لحن رسمی، محترمانه، مناسب مستندات و ارتباط B2B. |
| `friendly` | صمیمی و محاوره‌ای | لحن صمیمی شبیه چت اینستاگرام، اما همچنان محترمانه. |
| `brief` | خیلی خلاصه | جواب‌های خیلی کوتاه، مستقیم و بدون حاشیه. |
| `detailed` | کامل و توضیحی | جواب‌های طولانی‌تر با توضیح جزئیات و مثال. |
| `explainer` | آموزشی مرحله‌به‌مرحله | توضیح پاسخ به صورت گام‌به‌گام برای آموزش. |
| `marketing` | مارکتینگی و ترغیب‌کننده | لحن تبلیغاتی ملایم، مناسب معرفی سرویس به مشتری. |

## API Endpoints

### 1. Get Available Styles

**Endpoint:** `GET /api/smart-agent/styles`

**Description:** Returns a list of all available response styles with their Persian labels and descriptions.

**Response Format:**
```json
[
  {
    "key": "auto",
    "label": "خودکار",
    "description": "سیستم خودش بسته به سوال و زمینه، لحن مناسب را انتخاب می‌کند."
  },
  {
    "key": "formal",
    "label": "رسمی و حرفه‌ای",
    "description": "لحن رسمی، محترمانه، مناسب مستندات و ارتباط B2B."
  },
  // ... more styles
]
```

**Example Frontend Usage:**
```javascript
// Fetch available styles
const response = await fetch('/api/smart-agent/styles');
const styles = await response.json();

// Populate a dropdown/selector
styles.forEach(style => {
  const option = document.createElement('option');
  option.value = style.key;
  option.textContent = style.label; // Use Persian label for display
  option.title = style.description; // Use description for tooltip
  styleSelector.appendChild(option);
});
```

### 2. Chat with Style

**Endpoint:** `POST /api/smart-agent/chat`

**Request Body:**
```json
{
  "message": "سلام، چطور می‌تونم کمک بگیرم؟",
  "style": "friendly",
  "context": {
    "user_id": "123",
    "session_id": "abc"
  }
}
```

**Request Fields:**
- `message` (required): The user's message
- `style` (optional, default: `"auto"`): The response style key
- `context` (optional): Additional context object

**Response Format:**
```json
{
  "response": "سلام! خوش اومدی...",
  "style": "friendly",
  "response_time": 1.23,
  "web_content_used": false,
  "urls_processed": [],
  "context_used": true,
  "timestamp": "2024-01-01T12:00:00",
  "debug_info": null,
  "error": null
}
```

**Response Fields:**
- `response`: The agent's response text
- `style`: **The effective style used** (important: if `style="auto"` was requested, this shows the auto-selected style like `"friendly"` or `"formal"`)
- `response_time`: Time taken in seconds
- `web_content_used`: Whether web content was used
- `urls_processed`: List of URLs processed
- `context_used`: Whether context was used
- `timestamp`: ISO timestamp
- `debug_info`: Optional debug information
- `error`: Optional error message

**Example Frontend Usage:**
```javascript
// Send chat message with selected style
const chatResponse = await fetch('/api/smart-agent/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: userMessage,
    style: selectedStyle, // e.g., "friendly", "formal", "auto", etc.
    context: {
      user_id: currentUserId,
      session_id: sessionId
    }
  })
});

const result = await chatResponse.json();

// Display the response
displayMessage(result.response);

// Show the effective style used (useful for debugging or UI feedback)
console.log(`Response style: ${result.style}`);
```

## Style Behavior

### Auto Style (`"auto"`)

When `style="auto"` is specified (or when no style is provided):
- The system automatically analyzes the user's message
- It selects the most appropriate style based on:
  - Message content and keywords
  - Context and tone of the question
- The response's `style` field will show the **auto-selected style** (e.g., `"friendly"`, `"formal"`), not `"auto"`

### Specific Styles

When a specific style is requested (e.g., `style="formal"`):
- The system uses that exact style
- The response's `style` field will match the requested style
- If an invalid style is provided, it falls back to `"auto"` (no error is returned)

### Invalid Style Handling

If an invalid style key is provided:
- The system automatically falls back to `"auto"`
- No error is returned (graceful degradation)
- The response's `style` field will show the auto-selected style

## Backward Compatibility

✅ **Fully backward compatible**

- Calling `/api/smart-agent/chat` **without** the `style` parameter works exactly as before
- Defaults to `style="auto"` automatically
- Existing clients that don't send `style` will continue to work
- The response always includes the `style` field showing the effective style used

**Example (Old Client):**
```json
// Request (no style parameter)
{
  "message": "سلام"
}

// Response (includes style field)
{
  "response": "...",
  "style": "friendly",  // Auto-selected style
  ...
}
```

## Frontend Integration Guide

### Step 1: Fetch Available Styles

```javascript
async function loadStyles() {
  const response = await fetch('/api/smart-agent/styles');
  const styles = await response.json();
  return styles;
}
```

### Step 2: Create Style Selector UI

```javascript
function createStyleSelector(styles) {
  const selector = document.createElement('select');
  selector.id = 'style-selector';
  
  styles.forEach(style => {
    const option = document.createElement('option');
    option.value = style.key;
    option.textContent = style.label; // Persian label
    option.title = style.description; // Tooltip
    selector.appendChild(option);
  });
  
  // Set default to "auto"
  selector.value = 'auto';
  
  return selector;
}
```

### Step 3: Send Chat with Selected Style

```javascript
async function sendMessage(message, style = 'auto') {
  const response = await fetch('/api/smart-agent/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message: message,
      style: style
    })
  });
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  const result = await response.json();
  
  // Display response
  displayMessage(result.response);
  
  // Optionally show the effective style used
  if (style === 'auto') {
    console.log(`Auto-selected style: ${result.style}`);
  }
  
  return result;
}
```

### Step 4: Handle User Selection

```javascript
// When user selects a style
styleSelector.addEventListener('change', (e) => {
  const selectedStyle = e.target.value;
  // Store for next message
  currentStyle = selectedStyle;
});

// When sending a message
sendButton.addEventListener('click', () => {
  const message = messageInput.value;
  const style = styleSelector.value; // Get selected style
  sendMessage(message, style);
});
```

## Testing

Comprehensive tests are available in `backend/tests/test_smart_agent.py`:

- ✅ `/api/smart-agent/styles` returns full list with keys/labels/descriptions
- ✅ `/api/smart-agent/chat` accepts different style values
- ✅ Response includes effective style (after auto-selection)
- ✅ Invalid style falls back to "auto" (no error)
- ✅ Backward compatibility (calling without style works)

Run tests with:
```bash
pytest tests/test_smart_agent.py -v
```

## Summary

- **7 supported styles**: `auto`, `formal`, `friendly`, `brief`, `detailed`, `explainer`, `marketing`
- **Default style**: `"auto"` (automatic selection)
- **Invalid style handling**: Falls back to `"auto"` gracefully
- **Response includes effective style**: Shows the actual style used (not just input)
- **Fully backward compatible**: Works without `style` parameter
- **Persian-first**: All labels and descriptions are in Persian


















