# 🚀 Complete Render Deployment Guide

## Quick Start (5 Minutes)

### Step 1: Deploy with One Click
1. **Go to [render.com](https://render.com)**
2. **Sign up with GitHub**
3. **Click "New +" → "Blueprint"**
4. **Paste this repository URL**: `https://github.com/souroshsepehri/chatbot2`
5. **Select branch**: `json-faq-system-clean`
6. **Click "Apply"**

### Step 2: Set Your API Key
1. **Go to your backend service settings**
2. **Add Environment Variable**:
   - **Key**: `OPENAI_API_KEY`
   - **Value**: `your_actual_openai_api_key_here`
3. **Click "Save Changes"**

### Step 3: Update Frontend URL
1. **Go to your frontend service settings**
2. **Update Environment Variable**:
   - **Key**: `NEXT_PUBLIC_API_URL`
   - **Value**: `https://YOUR-BACKEND-URL.onrender.com/api`
3. **Redeploy the frontend**

## 🎯 What You'll Get

- **Backend API**: `https://persian-chatbot-backend.onrender.com`
- **Frontend**: `https://persian-chatbot-frontend.onrender.com`
- **Health Check**: `https://persian-chatbot-backend.onrender.com/health`

## 🔧 Manual Setup (Alternative)

If Blueprint doesn't work, use manual setup:

### Backend Service
- **Name**: `persian-chatbot-backend`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `cd backend && python -m uvicorn app:app --host 0.0.0.0 --port $PORT`

### Frontend Service
- **Name**: `persian-chatbot-frontend`
- **Environment**: `Static Site`
- **Build Command**: `cd frontend && npm install && npm run build`
- **Publish Directory**: `frontend/out`

## 🌟 Features Included

✅ **FastAPI Backend** with Persian chatbot
✅ **Next.js Frontend** with modern UI
✅ **FAQ Management** system
✅ **Semantic Search** capabilities
✅ **Chat Logging** and analytics
✅ **Health Monitoring** endpoints
✅ **CORS** configured for production
✅ **Environment Variables** setup
✅ **Auto-deployment** from GitHub

## 🆘 Troubleshooting

### Common Issues:

1. **Build Fails**: Check build logs in Render dashboard
2. **API Not Working**: Verify `OPENAI_API_KEY` is set
3. **Frontend Can't Connect**: Update `NEXT_PUBLIC_API_URL`
4. **CORS Errors**: Backend is pre-configured for Render domains

### Free Tier Limitations:
- Services sleep after 15 minutes of inactivity
- 90 minutes build time per month
- 100GB bandwidth per month

## 📞 Support

- **Render Docs**: [render.com/docs](https://render.com/docs)
- **GitHub Issues**: Create an issue in your repository
- **Community**: [community.render.com](https://community.render.com)

---

**Your Persian Chatbot is ready to deploy! 🎉**
