from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import openai
import os
import json
from typing import Optional

# Initialize OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Create FastAPI app
app = FastAPI(
    title="Persian Chatbot API",
    description="A simplified Persian chatbot for Vercel deployment",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://*.vercel.app",
        "https://*.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ChatRequest(BaseModel):
    message: str
    debug: Optional[bool] = False

class ChatResponse(BaseModel):
    answer: str
    debug_info: Optional[dict] = None

# Simple FAQ data (in production, this would come from a database)
FAQ_DATA = [
    {
        "question": "ساعات کاری شما چیست؟",
        "answer": "ساعات کاری ما از 8 صبح تا 6 عصر، شنبه تا پنج‌شنبه است."
    },
    {
        "question": "چگونه می‌توانم سفارش دهم؟",
        "answer": "شما می‌توانید از طریق وب‌سایت، تماس تلفنی یا مراجعه حضوری سفارش خود را ثبت کنید."
    },
    {
        "question": "هزینه ارسال چقدر است؟",
        "answer": "هزینه ارسال بستگی به وزن و مسافت دارد. برای اطلاعات دقیق با ما تماس بگیرید."
    },
    {
        "question": "آیا امکان بازگشت کالا وجود دارد؟",
        "answer": "بله، در صورت عدم رضایت، تا 7 روز پس از خرید امکان بازگشت کالا وجود دارد."
    }
]

def simple_faq_search(message: str) -> Optional[str]:
    """Simple keyword-based FAQ search"""
    message_lower = message.lower()
    
    for faq in FAQ_DATA:
        # Check if any word from the question appears in the message
        question_words = faq["question"].lower().split()
        if any(word in message_lower for word in question_words if len(word) > 3):
            return faq["answer"]
    
    return None

async def get_openai_response(message: str) -> str:
    """Get response from OpenAI API"""
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "شما یک دستیار هوشمند فارسی هستید که به سؤالات کاربران پاسخ می‌دهید. پاسخ‌های خود را به فارسی و به صورت مفید و دوستانه ارائه دهید."},
                {"role": "user", "content": message}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "متأسفانه در حال حاضر نمی‌توانم پاسخ دهم. لطفاً دوباره تلاش کنید."

@app.get("/")
async def root():
    """Serve the chatbot interface"""
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

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat message and return response"""
    try:
        # First try simple FAQ search
        faq_answer = simple_faq_search(request.message)
        if faq_answer:
            return ChatResponse(
                answer=faq_answer,
                debug_info={"source": "faq", "method": "simple_search"} if request.debug else None
            )
        
        # If no FAQ match, use OpenAI
        if openai.api_key:
            openai_answer = await get_openai_response(request.message)
            return ChatResponse(
                answer=openai_answer,
                debug_info={"source": "openai", "method": "gpt-3.5-turbo"} if request.debug else None
            )
        else:
            return ChatResponse(
                answer="متأسفانه در حال حاضر سرویس در دسترس نیست. لطفاً با پشتیبانی تماس بگیرید.",
                debug_info={"source": "fallback", "method": "no_api_key"} if request.debug else None
            )
            
    except Exception as e:
        print(f"Chat error: {e}")
        return ChatResponse(
            answer="خطایی در پردازش پیام شما رخ داد. لطفاً دوباره تلاش کنید.",
            debug_info={"error": str(e)} if request.debug else None
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
