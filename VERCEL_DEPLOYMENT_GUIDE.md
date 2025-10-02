# Vercel Deployment Guide

## Problem Solved
The original deployment failed due to the 250MB serverless function size limit caused by heavy dependencies like `faiss-cpu`, `langchain`, and other ML libraries.

## Solution
Created a simplified version that removes heavy dependencies while maintaining core functionality.

## Files for Vercel Deployment

### 1. Main Application File
- **Use**: `main-vercel.py` (instead of `main.py`)
- **Features**: 
  - Simplified chatbot without heavy ML dependencies
  - Direct OpenAI API integration
  - Simple FAQ search
  - Same beautiful UI

### 2. Requirements File
- **Use**: `requirements-vercel.txt` (instead of `requirements.txt`)
- **Dependencies**:
  ```
  fastapi==0.104.1
  uvicorn==0.24.0
  pydantic==2.5.0
  python-dotenv==1.0.0
  openai>=1.0.0
  ```

### 3. Vercel Configuration
- **File**: `vercel.json`
- **Settings**: Optimized for Python serverless functions

## Deployment Steps

### Option 1: Deploy via Vercel CLI
```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel --prod
```

### Option 2: Deploy via GitHub
1. Push the simplified files to GitHub
2. Connect your GitHub repo to Vercel
3. Set build settings:
   - **Build Command**: Leave empty
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements-vercel.txt`

### Option 3: Manual Upload
1. Go to Vercel Dashboard
2. Create new project
3. Upload `main-vercel.py` as `main.py`
4. Upload `requirements-vercel.txt` as `requirements.txt`
5. Upload `vercel.json`

## Environment Variables
Set these in Vercel dashboard:
- `OPENAI_API_KEY`: Your OpenAI API key

## Features Included
- ✅ Persian chatbot interface
- ✅ OpenAI GPT-3.5-turbo integration
- ✅ Simple FAQ search
- ✅ Beautiful responsive UI
- ✅ Error handling
- ✅ Debug mode
- ✅ Health check endpoint

## Features Removed (for size optimization)
- ❌ FAISS vector search
- ❌ LangChain dependencies
- ❌ SQLAlchemy database
- ❌ Complex ML pipelines
- ❌ Vector embeddings

## Size Comparison
- **Original**: ~250MB+ (exceeds limit)
- **Simplified**: ~50MB (well under limit)

## Testing
After deployment, test these endpoints:
- `GET /` - Chatbot interface
- `POST /api/chat` - Chat API
- `GET /health` - Health check

## Rollback Plan
If you need the full-featured version:
1. Use the original `main.py` and `requirements.txt`
2. Deploy to a platform that supports larger functions (Render, Railway, etc.)
3. Keep the simplified version for Vercel