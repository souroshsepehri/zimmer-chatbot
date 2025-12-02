# Load .env file explicitly at the very top (before FastAPI app and before importing smart_agent)
from dotenv import load_dotenv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, ".env")
load_dotenv(ENV_PATH)

from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path
from datetime import datetime, timedelta
from core.db import engine, Base
from routers import chat, faqs, logs, smart_chat, simple_chat, external_api, debug, smart_agent, api_integration, admin, admin_bot_settings, admin_sites
from core.config import settings

# Import smart_agent early to ensure it's initialized with the loaded env vars
from services.smart_agent import smart_agent

# Import all models to ensure they are registered with SQLAlchemy
from models import faq, log, tracked_site

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Persian Chatbot API",
    description="A Persian chatbot with FAQ management and semantic search",
    version="1.0.0"
)

# Admin authentication constants
ADMIN_USERNAME = "zimmer admin"
ADMIN_PASSWORD = "admin1234"
ADMIN_SESSION_COOKIE = "admin_session"
ADMIN_SESSION_TIMEOUT_MINUTES = 5

# Add CORS middleware - Allow all origins for development
# In production, specify exact origins
import os
is_production = os.environ.get("ENVIRONMENT") == "production"

cors_origins = [
    "http://localhost:3000",  # Next.js dev server
    "http://localhost:3001",  # Alternative Next.js port
    "http://127.0.0.1:3000",  # Localhost IP
    "http://127.0.0.1:3001",  # Alternative localhost IP
    "http://localhost:8000",  # Alternative frontend port
    "http://127.0.0.1:8000",  # Alternative frontend port IP
    "https://persian-chatbot-frontend.onrender.com",  # Render frontend
]

# In development, allow all origins
if not is_production:
    cors_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins if is_production else ["*"],
    allow_credentials=is_production,  # Only allow credentials in production with specific origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add SessionMiddleware for backward compatibility with existing admin router
# (The router uses request.session, but our new auth uses cookies)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "CHANGE_THIS_SESSION_SECRET"),
    session_cookie="zimmer_admin_session",
    max_age=None,
)

# Admin authentication middleware (cookie-based)
@app.middleware("http")
async def admin_auth_middleware(request: Request, call_next):
    path = request.url.path

    # Let health, API and static files pass
    if path.startswith("/health") or path.startswith("/api") or path.startswith("/static"):
        return await call_next(request)

    # Allow login page itself without session
    if path.startswith("/admin/login"):
        return await call_next(request)

    # Protect all other /admin paths
    if path.startswith("/admin"):
        session_cookie = request.cookies.get(ADMIN_SESSION_COOKIE)
        if not session_cookie:
            return RedirectResponse(url="/admin/login", status_code=302)

        try:
            last_active = datetime.fromisoformat(session_cookie)
        except ValueError:
            resp = RedirectResponse(url="/admin/login", status_code=302)
            resp.delete_cookie(ADMIN_SESSION_COOKIE, path="/admin")
            return resp

        if datetime.utcnow() - last_active > timedelta(minutes=ADMIN_SESSION_TIMEOUT_MINUTES):
            resp = RedirectResponse(url="/admin/login", status_code=302)
            resp.delete_cookie(ADMIN_SESSION_COOKIE, path="/admin")
            return resp

        # Session valid -> refresh timestamp
        response = await call_next(request)
        response.set_cookie(
            ADMIN_SESSION_COOKIE,
            datetime.utcnow().isoformat(),
            httponly=True,
            path="/admin",
        )
        return response

    # Non-admin routes: normal behavior
    return await call_next(request)

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(faqs.router, prefix="/api", tags=["faqs"])
app.include_router(logs.router, prefix="/api", tags=["logs"])
app.include_router(smart_chat.router, prefix="/api", tags=["smart-chat"])
app.include_router(simple_chat.router, prefix="/api", tags=["simple-chat"])
app.include_router(external_api.router, prefix="/api", tags=["external-api"])
app.include_router(debug.router, prefix="/api", tags=["debug"])
app.include_router(api_integration.router, prefix="/api", tags=["api-integration"])
app.include_router(admin.router, tags=["admin"])
app.include_router(admin_bot_settings.router)
app.include_router(admin_sites.router)

# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def root():
    # Serve simple HTML chatbot interface
    html_content = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بات هوشمند زیمر</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .chatbot-container {
            width: 90%;
            max-width: 800px;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 { font-size: 2rem; margin-bottom: 10px; }
        .header p { opacity: 0.9; }
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
        }
        .message.user { justify-content: flex-end; }
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        .message.bot .message-content {
            background: #e3f2fd;
            color: #1565c0;
        }
        .message.user .message-content {
            background: #667eea;
            color: white;
        }
        .input-container {
            padding: 20px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
        }
        .input-field {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }
        .input-field:focus { border-color: #667eea; }
        .send-button {
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        .send-button:hover { background: #5a6fd8; }
        .send-button:disabled { background: #ccc; cursor: not-allowed; }
        .loading { display: none; text-align: center; padding: 10px; color: #666; }
        .error { background: #ffebee; color: #c62828; padding: 10px; margin: 10px 20px; border-radius: 8px; text-align: center; }
    </style>
</head>
<body>
    <div class="chatbot-container">
        <div class="header">
            <h1>بات هوشمند زیمر</h1>
            <p>دستیار هوشمند فارسی برای پاسخ به سؤالات شما</p>
        </div>
        <div class="chat-messages" id="chatMessages">
            <div class="message bot">
                <div class="message-content">
                    سلام وقت بخیر! ربات هوشمند زیمر هستم. چطور می‌تونم کمکتون کنم؟
                </div>
            </div>
        </div>
        <div class="loading" id="loading">در حال پردازش...</div>
        <div class="input-container">
            <input type="text" id="messageInput" class="input-field" placeholder="پیام خود را بنویسید..." />
            <button id="sendButton" class="send-button">ارسال</button>
        </div>
    </div>
    <script>
        const chatMessages = document.getElementById('chatMessages');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const loading = document.getElementById('loading');
        const API_BASE = window.location.origin + '/api';
        
        function addMessage(text, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'bot'}`;
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = text;
            messageDiv.appendChild(contentDiv);
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        function showLoading() {
            loading.style.display = 'block';
            sendButton.disabled = true;
        }
        
        function hideLoading() {
            loading.style.display = 'none';
            sendButton.disabled = false;
        }
        
        function showError(message) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error';
            errorDiv.textContent = message;
            chatMessages.appendChild(errorDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        
        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;
            
            addMessage(message, true);
            messageInput.value = '';
            showLoading();
            
            try {
                const response = await fetch(`${API_BASE}/chat`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                addMessage(data.answer || 'پاسخ دریافت شد', false);
                
            } catch (error) {
                console.error('Error:', error);
                showError('خطا در ارتباط با سرور. لطفاً دوباره تلاش کنید.');
            } finally {
                hideLoading();
            }
        }
        
        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
        messageInput.focus();
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


# Admin login routes
@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_form():
    return """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>ورود مدیر زیمر</title>
        <style>
            body {
                font-family: sans-serif;
                background: #f5f5f5;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
            }
            .card {
                background: white;
                padding: 24px 32px;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.08);
                min-width: 320px;
            }
            .card h1 {
                font-size: 20px;
                margin-bottom: 16px;
                text-align: center;
            }
            .field {
                margin-bottom: 12px;
            }
            .field label {
                display: block;
                margin-bottom: 4px;
                font-size: 14px;
            }
            .field input {
                width: 100%;
                padding: 8px 10px;
                border-radius: 6px;
                border: 1px solid #ccc;
                font-size: 14px;
            }
            button {
                width: 100%;
                padding: 10px;
                border-radius: 6px;
                border: none;
                background: #667eea;
                color: white;
                font-size: 14px;
                cursor: pointer;
            }
            button:hover {
                background: #5564c8;
            }
            .error {
                color: #c0392b;
                margin-bottom: 8px;
                font-size: 13px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <form class="card" method="post" action="/admin/login">
            <h1>ورود مدیر زیمر</h1>
            <div class="field">
                <label>نام کاربری</label>
                <input type="text" name="username" />
            </div>
            <div class="field">
                <label>رمز عبور</label>
                <input type="password" name="password" />
            </div>
            <button type="submit">ورود</button>
        </form>
    </body>
    </html>
    """


@app.post("/admin/login", response_class=HTMLResponse)
async def admin_login_submit(username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        resp = RedirectResponse(url="/admin", status_code=302)
        resp.set_cookie(
            ADMIN_SESSION_COOKIE,
            datetime.utcnow().isoformat(),
            httponly=True,
            path="/admin",
        )
        return resp

    # Invalid credentials -> show same form with error message
    html = """
    <!DOCTYPE html>
    <html lang="fa" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <title>ورود مدیر زیمر</title>
        <style>
            body {
                font-family: sans-serif;
                background: #f5f5f5;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
            }
            .card {
                background: white;
                padding: 24px 32px;
                border-radius: 12px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.08);
                min-width: 320px;
            }
            .card h1 {
                font-size: 20px;
                margin-bottom: 16px;
                text-align: center;
            }
            .field {
                margin-bottom: 12px;
            }
            .field label {
                display: block;
                margin-bottom: 4px;
                font-size: 14px;
            }
            .field input {
                width: 100%;
                padding: 8px 10px;
                border-radius: 6px;
                border: 1px solid #ccc;
                font-size: 14px;
            }
            button {
                width: 100%;
                padding: 10px;
                border-radius: 6px;
                border: none;
                background: #667eea;
                color: white;
                font-size: 14px;
                cursor: pointer;
            }
            button:hover {
                background: #5564c8;
            }
            .error {
                color: #c0392b;
                margin-bottom: 8px;
                font-size: 13px;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <form class="card" method="post" action="/admin/login">
            <h1>ورود مدیر زیمر</h1>
            <div class="error">نام کاربری یا رمز عبور اشتباه است.</div>
            <div class="field">
                <label>نام کاربری</label>
                <input type="text" name="username" />
            </div>
            <div class="field">
                <label>رمز عبور</label>
                <input type="password" name="password" />
            </div>
            <button type="submit">ورود</button>
        </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html, status_code=401)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/test-db")
async def test_database():
    """Test database connection and data"""
    try:
        from core.db import get_db
        from models.faq import FAQ
        
        db = next(get_db())
        faq_count = db.query(FAQ).count()
        db.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "faq_count": faq_count,
            "message": "Database is working properly"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    import socket
    import os
    
    def is_port_available(port):
        """Check if a port is available"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return True
            except OSError:
                return False
    
    # Get port from environment variable or settings
    port = int(os.environ.get("PORT", settings.server_port))
    host = os.environ.get("HOST", settings.server_host)
    
    # Try to find an available port if the default is busy
    original_port = port
    max_attempts = 10
    for attempt in range(max_attempts):
        if is_port_available(port):
            break
        if attempt == 0:
            print(f"⚠️  Port {port} is already in use. Trying alternative ports...")
        port = original_port + attempt + 1
    else:
        print(f"❌ Could not find an available port after {max_attempts} attempts.")
        print(f"   Please stop the process using port {original_port} or set a different PORT environment variable.")
        exit(1)
    
    if port != original_port:
        print(f"ℹ️  Using port {port} instead of {original_port}")
    
    uvicorn.run(app, host=host, port=port)


# ============================================================================
# Testing Instructions (run these commands on the server):
# ============================================================================
# cd /home/chatbot/chatbot2/backend
# source venv/bin/activate
# uvicorn main:app --reload
#
# Then test:
# 1. Open /admin → it should redirect to /admin/login
# 2. Enter username "zimmer admin" and password "admin1234" → 
#    it should redirect to /admin and show the existing admin panel
# 3. Wait more than 5 minutes without clicking anything on admin, 
#    then reload /admin → it should redirect to /admin/login again
# ============================================================================

