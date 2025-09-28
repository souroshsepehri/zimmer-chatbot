# Deploy Your Persian Chatbot to Render

This guide will help you deploy your FastAPI + Next.js chatbot application to Render.

## Prerequisites

1. **GitHub Repository**: Your code should be in a GitHub repository
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **OpenAI API Key**: You'll need this for the chatbot functionality

## Step 1: Prepare Your Repository

### 1.1 Push Your Code to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 1.2 Verify Files Are Present
Make sure these files are in your repository root:
- `render.yaml` ✅ (Created)
- `backend/requirements.txt` ✅ (Already exists)
- `frontend/package.json` ✅ (Already exists)

## Step 2: Deploy to Render

### 2.1 Create a New Web Service

1. Go to [render.com](https://render.com) and sign in
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Select your repository

### 2.2 Configure Backend Service

**Service Settings:**
- **Name**: `persian-chatbot-backend`
- **Environment**: `Python 3`
- **Region**: Choose closest to your users
- **Branch**: `main`
- **Root Directory**: Leave empty (uses root)
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `cd backend && python -m uvicorn app:app --host 0.0.0.0 --port $PORT`

**Environment Variables:**
- `OPENAI_API_KEY`: Your OpenAI API key (mark as secret)
- `DATABASE_URL`: `sqlite:///./app.db`
- `VECTORSTORE_PATH`: `./vectorstore`
- `PYTHONPATH`: `/opt/render/project/src/backend`

**Advanced Settings:**
- **Health Check Path**: `/health`
- **Auto-Deploy**: Yes

### 2.3 Configure Frontend Service

1. Create another web service for the frontend
2. **Service Settings:**
   - **Name**: `persian-chatbot-frontend`
   - **Environment**: `Static Site`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/out`

3. **Environment Variables:**
   - `NEXT_PUBLIC_API_URL`: `https://persian-chatbot-backend.onrender.com/api`

## Step 3: Update Service URLs

After both services are deployed, you'll get URLs like:
- Backend: `https://persian-chatbot-backend.onrender.com`
- Frontend: `https://persian-chatbot-frontend.onrender.com`

### 3.1 Update Frontend API URL
1. Go to your frontend service settings
2. Update the environment variable:
   - `NEXT_PUBLIC_API_URL`: `https://YOUR-BACKEND-URL.onrender.com/api`
3. Redeploy the frontend service

### 3.2 Update Backend CORS Settings
The backend has been updated to allow Render domains, but you may need to update the specific frontend URL in `backend/app.py` if needed.

## Step 4: Test Your Deployment

1. **Backend Health Check**: Visit `https://your-backend-url.onrender.com/health`
2. **Frontend**: Visit your frontend URL
3. **Test Chat**: Try sending a message to verify the full flow works

## Step 5: Custom Domain (Optional)

1. In Render dashboard, go to your service
2. Click "Settings" → "Custom Domains"
3. Add your domain and follow DNS instructions

## Troubleshooting

### Common Issues:

1. **Build Failures**:
   - Check build logs in Render dashboard
   - Ensure all dependencies are in `requirements.txt`
   - Verify Python version compatibility

2. **CORS Errors**:
   - Update `allow_origins` in `backend/app.py`
   - Ensure frontend URL is correctly set

3. **API Connection Issues**:
   - Verify `NEXT_PUBLIC_API_URL` environment variable
   - Check backend service is running and healthy

4. **Database Issues**:
   - SQLite files are ephemeral on Render free tier
   - Consider upgrading to paid plan for persistent storage
   - Or migrate to PostgreSQL for production

### Free Tier Limitations:

- **Sleep Mode**: Services sleep after 15 minutes of inactivity
- **Build Time**: 90 minutes per month
- **Bandwidth**: 100GB per month
- **Database**: SQLite files are not persistent

## Production Considerations

1. **Database**: Migrate to PostgreSQL for production
2. **Environment Variables**: Use Render's environment variable management
3. **Monitoring**: Set up health checks and monitoring
4. **Scaling**: Consider upgrading to paid plans for better performance

## Support

- Render Documentation: [render.com/docs](https://render.com/docs)
- Render Community: [community.render.com](https://community.render.com)

---

**Your chatbot should now be live on Render!** 🚀

The deployment will create two services:
- Backend API at `https://persian-chatbot-backend.onrender.com`
- Frontend at `https://persian-chatbot-frontend.onrender.com`
