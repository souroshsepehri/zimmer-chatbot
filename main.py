from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import from backend modules
try:
    from core.db import engine, Base
    from routers import chat, faqs, logs
    from core.config import settings
    BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"Backend modules not available: {e}")
    BACKEND_AVAILABLE = False

# Simple fallback chatbot without LangChain
def simple_chatbot_response(message: str) -> str:
    """Simple chatbot response without AI dependencies"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['سلام', 'hello', 'hi']):
        return "سلام! خوش آمدید. چطور می‌تونم کمکتون کنم؟"
    elif any(word in message_lower for word in ['چطوری', 'حالت', 'چطوری']):
        return "من خوبم، ممنون! شما چطورید؟"
    elif any(word in message_lower for word in ['خداحافظ', 'bye', 'goodbye']):
        return "خداحافظ! امیدوارم روز خوبی داشته باشید."
    elif any(word in message_lower for word in ['کمک', 'help', 'راهنما']):
        return "من اینجا هستم تا کمکتون کنم. سوالاتتون رو بپرسید."
    else:
        return "متوجه نشدم. لطفاً سوال خود را واضح‌تر بپرسید."

# Skip database initialization in Vercel serverless environment
# Database will be handled by external service in production

# Create FastAPI app
app = FastAPI(
    title="Persian Chatbot API",
    description="A Persian chatbot with FAQ management and semantic search",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local development
        "https://persian-chatbot-frontend.onrender.com",  # Render frontend
        "https://*.onrender.com",  # Any Render subdomain
        "https://*.vercel.app",  # Vercel domains
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers only if backend is available
if BACKEND_AVAILABLE:
    app.include_router(chat.router, prefix="/api", tags=["chat"])
    app.include_router(faqs.router, prefix="/api", tags=["faqs"])
    app.include_router(logs.router, prefix="/api", tags=["logs"])


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


@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/chat")
async def simple_chat(request: dict):
    """Simple chat endpoint that works without LangChain dependencies"""
    message = request.get("message", "")
    if not message:
        return {"answer": "لطفاً پیام خود را وارد کنید."}
    
    # Try to use backend if available, otherwise use simple fallback
    if BACKEND_AVAILABLE:
        try:
            # This would normally call the backend chat router
            # For now, use simple response
            response = simple_chatbot_response(message)
            return {"answer": response}
        except Exception as e:
            print(f"Backend chat error: {e}")
            return {"answer": simple_chatbot_response(message)}
    else:
        return {"answer": simple_chatbot_response(message)}

@app.get("/test-db")
async def test_database():
    """Test database connection and data"""
    if not BACKEND_AVAILABLE:
        return {
            "status": "error",
            "database": "not_available",
            "message": "Backend modules not available in serverless environment"
        }
    
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
    import os
    port = int(os.environ.get("PORT", 8002))
    uvicorn.run(app, host="0.0.0.0", port=port)
