# Set API Key Script for Windows PowerShell
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Setting Up API Key" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $scriptDir "backend"

# Prompt for API key
$apiKey = Read-Host "Enter your OpenAI API key" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($apiKey)
$plainApiKey = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Create .env file content
$envContent = @"
OPENAI_API_KEY=$plainApiKey
OPENAI_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-3-small
RETRIEVAL_TOP_K=4
RETRIEVAL_THRESHOLD=0.82
DATABASE_URL=sqlite:///./app.db
"@

# Write to .env file
$envFile = Join-Path $backendDir ".env"
$envContent | Out-File -FilePath $envFile -Encoding utf8 -NoNewline

Write-Host "✅ API key saved to: $envFile" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  Important: Restart your chatbot server for changes to take effect" -ForegroundColor Yellow
Write-Host ""

