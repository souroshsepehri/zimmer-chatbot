# Where to Put Your API Keys

## 📍 Location
**Create a `.env` file in the `backend` directory:**

- **Windows**: `C:\chatbot2\backend\.env`
- **Linux/Cloud**: `~/chatbot2/backend/.env`

## 📝 File Format

Create the `.env` file with this content:

```env
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small
RETRIEVAL_TOP_K=4
RETRIEVAL_THRESHOLD=0.82
DATABASE_URL=sqlite:///./app.db
```

## 🖥️ How to Create on Cloud Server

```bash
# Navigate to backend directory
cd ~/chatbot2/backend

# Create .env file
nano .env
```

Paste your API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Save: `Ctrl+X`, then `Y`, then `Enter`

## 🪟 How to Create on Windows

```powershell
# Navigate to backend directory
cd C:\chatbot2\backend

# Create .env file
notepad .env
```

Paste your API key:
```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

Save and close.

## ✅ Verify It's Working

After creating the `.env` file, restart your server:

```bash
# On cloud server
pkill -f uvicorn
cd ~/chatbot2/backend
source venv/bin/activate
nohup uvicorn app:app --host 0.0.0.0 --port 8002 --workers 1 > ../backend.log 2>&1 &
```

## 🔒 Security Notes

- ⚠️ **Never commit `.env` to git** - it's already in `.gitignore`
- ✅ The `.env` file is automatically loaded by the app
- ✅ Keep your API key secret and secure

