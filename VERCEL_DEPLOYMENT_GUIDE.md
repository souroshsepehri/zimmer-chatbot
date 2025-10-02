# Vercel Deployment Guide for Persian Chatbot

## Quick Setup

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy your project**:
   ```bash
   vercel
   ```

## Environment Variables

Before deploying, make sure to set up your environment variables in the Vercel dashboard:

1. Go to your project in Vercel dashboard
2. Navigate to Settings > Environment Variables
3. Add the following variables:

```
OPENAI_API_KEY=your_actual_openai_api_key
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
RETRIEVAL_TOP_K=4
RETRIEVAL_THRESHOLD=0.82
DATABASE_URL=sqlite:///./app.db
```

## Important Notes

- The app is configured to work with Vercel's serverless environment
- Database tables are only created when not running on Vercel (serverless functions don't support persistent file storage)
- For production, consider using a cloud database like PostgreSQL or MongoDB
- The app includes CORS settings for Vercel domains

## File Structure

```
├── main.py              # Main FastAPI app (Vercel entry point)
├── vercel.json          # Vercel configuration
├── requirements.txt     # Python dependencies
├── .env.example        # Environment variables template
└── backend/            # Your existing backend code
    ├── core/
    ├── models/
    ├── routers/
    └── services/
```

## Testing Locally

To test the Vercel configuration locally:

```bash
vercel dev
```

This will start a local development server that mimics Vercel's environment.

## Troubleshooting

If you encounter issues:

1. Check that all environment variables are set correctly
2. Ensure your OpenAI API key is valid
3. Check the Vercel function logs for detailed error messages
4. Make sure all dependencies are listed in requirements.txt
