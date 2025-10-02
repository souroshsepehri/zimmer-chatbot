from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import json

app = FastAPI(title="Persian Chatbot", version="1.0.0")

# Simple FAQ data
FAQ_DATA = [
    {"q": "ساعات کاری", "a": "ساعات کاری ما از 8 صبح تا 6 عصر، شنبه تا پنج‌شنبه است."},
    {"q": "سفارش", "a": "شما می‌توانید از طریق وب‌سایت، تماس تلفنی یا مراجعه حضوری سفارش خود را ثبت کنید."},
    {"q": "ارسال", "a": "هزینه ارسال بستگی به وزن و مسافت دارد. برای اطلاعات دقیق با ما تماس بگیرید."},
    {"q": "بازگشت", "a": "بله، در صورت عدم رضایت، تا 7 روز پس از خرید امکان بازگشت کالا وجود دارد."},
    {"q": "قیمت", "a": "برای اطلاع از قیمت‌ها، لطفاً با بخش فروش تماس بگیرید."},
    {"q": "تماس", "a": "شماره تماس: 021-12345678 یا ایمیل: info@zimmer.com"}
]

def simple_search(message: str) -> str:
    """Ultra-simple keyword search"""
    msg = message.lower()
    for faq in FAQ_DATA:
        if any(word in msg for word in faq["q"].split() if len(word) > 2):
            return faq["a"]
    return "متأسفانه پاسخ مناسبی برای این سؤال ندارم. لطفاً با پشتیبانی تماس بگیرید."

@app.get("/")
async def root():
    return HTMLResponse("""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>بات زیمر</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #f0f0f0; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .header { background: #4a90e2; color: white; padding: 20px; text-align: center; }
        .header h1 { font-size: 24px; margin-bottom: 5px; }
        .messages { height: 300px; overflow-y: auto; padding: 20px; background: #f9f9f9; }
        .message { margin-bottom: 10px; padding: 10px; border-radius: 8px; }
        .bot { background: #e3f2fd; color: #1565c0; }
        .user { background: #4a90e2; color: white; text-align: right; }
        .input-area { padding: 20px; background: white; border-top: 1px solid #eee; display: flex; gap: 10px; }
        .input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .btn { background: #4a90e2; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; }
        .btn:hover { background: #357abd; }
        .loading { display: none; text-align: center; padding: 10px; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>بات هوشمند زیمر</h1>
            <p>دستیار هوشمند فارسی</p>
        </div>
        <div class="messages" id="messages">
            <div class="message bot">سلام! چطور می‌تونم کمکتون کنم؟</div>
        </div>
        <div class="loading" id="loading">در حال پردازش...</div>
        <div class="input-area">
            <input type="text" id="input" class="input" placeholder="پیام خود را بنویسید...">
            <button onclick="send()" class="btn">ارسال</button>
        </div>
    </div>
    <script>
        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = 'message ' + (isUser ? 'user' : 'bot');
            div.textContent = text;
            document.getElementById('messages').appendChild(div);
            document.getElementById('messages').scrollTop = document.getElementById('messages').scrollHeight;
        }
        
        async function send() {
            const input = document.getElementById('input');
            const message = input.value.trim();
            if (!message) return;
            
            addMessage(message, true);
            input.value = '';
            document.getElementById('loading').style.display = 'block';
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: message})
                });
                const data = await response.json();
                addMessage(data.answer, false);
            } catch (error) {
                addMessage('خطا در ارتباط با سرور', false);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        document.getElementById('input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') send();
        });
    </script>
</body>
</html>
    """)

@app.post("/api/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "")
    answer = simple_search(message)
    return {"answer": answer}

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
