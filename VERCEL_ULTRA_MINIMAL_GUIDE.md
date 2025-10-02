# Vercel Ultra-Minimal Deployment Guide

## Problem
Even the simplified version is still hitting the 250MB limit. This guide provides ultra-minimal solutions.

## Solution Options (Choose One)

### Option 1: Micro Version (Recommended)
- **Files**: `main-micro.py` + `requirements-micro.txt`
- **Dependencies**: FastAPI + Uvicorn + Pydantic only
- **Size**: ~30-50MB
- **Features**: Full chatbot UI + simple FAQ search

### Option 2: Ultra-Minimal Version
- **Files**: `main-ultra-minimal.py` + `requirements-ultra-minimal.txt`
- **Dependencies**: FastAPI + Uvicorn only (no Pydantic)
- **Size**: ~20-30MB
- **Features**: Full chatbot UI + simple FAQ search

## Deployment Steps

### Step 1: Choose Your Version
```bash
# Option 1: Micro version
cp main-micro.py main.py
cp requirements-micro.txt requirements.txt

# OR Option 2: Ultra-minimal version
cp main-ultra-minimal.py main.py
cp requirements-ultra-minimal.txt requirements.txt
```

### Step 2: Deploy to Vercel
1. **Via Vercel CLI:**
   ```bash
   vercel --prod
   ```

2. **Via GitHub:**
   - Push to GitHub
   - Connect repo to Vercel
   - Deploy

3. **Via Manual Upload:**
   - Upload `main.py` and `requirements.txt`
   - No `vercel.json` needed

## What's Included

### ✅ Features
- Beautiful Persian chatbot interface
- Simple keyword-based FAQ search
- Responsive design
- Error handling
- Health check endpoint
- Real-time chat interface

### ✅ FAQ Topics Covered
- ساعات کاری (Working hours)
- سفارش (Orders)
- ارسال (Shipping)
- بازگشت (Returns)
- قیمت (Pricing)
- تماس (Contact)

### ❌ Removed (for size optimization)
- OpenAI API integration
- Heavy ML libraries
- Database connections
- Complex dependencies
- Vector search

## File Sizes Comparison

| Version | Dependencies | Estimated Size |
|---------|-------------|----------------|
| Original | FastAPI + LangChain + FAISS + SQLAlchemy + OpenAI | 250MB+ |
| Vercel | FastAPI + Uvicorn + Pydantic + OpenAI | 100-150MB |
| Micro | FastAPI + Uvicorn + Pydantic | 30-50MB |
| Ultra-Minimal | FastAPI + Uvicorn only | 20-30MB |

## Testing

After deployment, test:
- `GET /` - Chatbot interface
- `POST /api/chat` - Chat API
- `GET /health` - Health check

## Customization

### Adding More FAQs
Edit the `FAQ_DATA` list in your chosen `main.py` file:

```python
FAQ_DATA = [
    {"q": "سوال جدید", "a": "پاسخ جدید"},
    # Add more FAQs here
]
```

### Styling
The CSS is embedded in the HTML. Modify the `<style>` section to change appearance.

## Troubleshooting

### Still getting 250MB error?
1. Try the ultra-minimal version
2. Check if Vercel is installing additional dependencies
3. Consider using a different platform (Render, Railway)

### Chat not working?
1. Check browser console for errors
2. Verify the API endpoint is accessible
3. Test with simple messages first

## Alternative Platforms

If Vercel continues to have size issues:
- **Render**: Supports larger functions
- **Railway**: Good for Python apps
- **Heroku**: Traditional hosting option
- **DigitalOcean App Platform**: Alternative serverless

## Next Steps

1. Deploy the micro or ultra-minimal version
2. Test all functionality
3. Add more FAQs as needed
4. Consider upgrading to a platform with higher limits if you need more features
