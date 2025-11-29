# Start Chatbot Server with API Key
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Starting Chatbot Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Setting OpenAI API Key..." -ForegroundColor Yellow
$env:OPENAI_API_KEY = "your_api_key_here"

Write-Host ""
Write-Host "Testing API key configuration..." -ForegroundColor Yellow
python -c "import os; print('API Key set:', bool(os.getenv('OPENAI_API_KEY')))"

Write-Host ""
Write-Host "Testing intent system..." -ForegroundColor Yellow
python -c "from services.intent import intent_detector; result = intent_detector.detect('سلام'); print('Intent test result:', result['label'], result['confidence'])"

Write-Host ""
Write-Host "Starting server..." -ForegroundColor Green
Write-Host "Server will be available at: http://127.0.0.1:8002" -ForegroundColor Cyan
Write-Host "API docs will be available at: http://127.0.0.1:8002/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Red
Write-Host ""

python -m uvicorn main:app --host 127.0.0.1 --port 8002 --reload
