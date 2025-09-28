# Set OpenAI API Key for PowerShell
Write-Host "Setting OpenAI API Key..." -ForegroundColor Green

$env:OPENAI_API_KEY = "your_api_key_here"

Write-Host "API Key set successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "You can now run your chatbot with:" -ForegroundColor Yellow
Write-Host "  python start_backend_robust.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
