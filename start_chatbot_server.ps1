# PowerShell script to start the chatbot server
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   Starting Chatbot Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the script directory
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

Write-Host "Current directory: $ProjectRoot" -ForegroundColor Gray
Write-Host ""

# Step 1: Check and install frontend dependencies
Write-Host "[1/3] Checking Frontend Dependencies..." -ForegroundColor Yellow
Set-Location "$ProjectRoot\frontend"

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: npm install failed!" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
} else {
    Write-Host "Frontend dependencies found." -ForegroundColor Green
}

Set-Location $ProjectRoot

# Step 2: Start Backend Server
Write-Host ""
Write-Host "[2/3] Starting Backend Server..." -ForegroundColor Yellow
Set-Location "$ProjectRoot\backend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot\backend'; python app.py"
Start-Sleep -Seconds 5
Set-Location $ProjectRoot

# Step 3: Start Frontend Server
Write-Host ""
Write-Host "[3/3] Starting Frontend Server..." -ForegroundColor Yellow
Set-Location "$ProjectRoot\frontend"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$ProjectRoot\frontend'; npm run dev"
Start-Sleep -Seconds 10
Set-Location $ProjectRoot

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "   Chatbot Started Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:8002" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Admin:    http://localhost:3000/admin" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opening browser..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"
Write-Host ""
Write-Host "Both servers are running in separate windows." -ForegroundColor Gray
Write-Host "Close those windows to stop the servers." -ForegroundColor Gray
Write-Host ""
Read-Host "Press Enter to exit"

