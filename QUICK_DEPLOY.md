# ⚡ Quick Deploy to Render

## 🚀 One-Click Deployment

### Method 1: Blueprint (Easiest)
1. **Go to [render.com](https://render.com)**
2. **Sign up with GitHub**
3. **Click "New +" → "Blueprint"**
4. **Paste**: `https://github.com/souroshsepehri/chatbot2`
5. **Select branch**: `json-faq-system-clean`
6. **Click "Apply"**

### Method 2: Manual Setup
1. **Create Web Service**
2. **Connect GitHub repository**
3. **Use these settings**:

#### Backend:
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `cd backend && python -m uvicorn app:app --host 0.0.0.0 --port $PORT`

#### Frontend:
- **Environment**: Static Site
- **Build Command**: `cd frontend && npm install && npm run build`
- **Publish Directory**: `frontend/out`

## 🔑 Required Environment Variables

### Backend:
```
OPENAI_API_KEY = your_openai_api_key_here
DATABASE_URL = sqlite:///./app.db
VECTORSTORE_PATH = ./vectorstore
```

### Frontend:
```
NEXT_PUBLIC_API_URL = https://your-backend-url.onrender.com/api
```

## 🎯 Expected URLs

- **Backend**: `https://persian-chatbot-backend.onrender.com`
- **Frontend**: `https://persian-chatbot-frontend.onrender.com`
- **Health Check**: `https://persian-chatbot-backend.onrender.com/health`

## ⚠️ Important Notes

1. **Set your OpenAI API key** in backend environment variables
2. **Update frontend API URL** after backend is deployed
3. **Free tier** services sleep after 15 minutes of inactivity
4. **First deployment** may take 5-10 minutes

## 🆘 Need Help?

- Check build logs in Render dashboard
- Verify environment variables are set
- Make sure you're using the correct branch: `json-faq-system-clean`

---

**Ready to deploy? Run `deploy-to-render.bat` and follow the steps! 🚀**
