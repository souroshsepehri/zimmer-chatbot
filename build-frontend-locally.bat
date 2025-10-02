@echo off
echo ========================================
echo    Building Frontend Locally
echo ========================================
echo.

echo Building frontend to avoid Render vulnerabilities...
cd frontend

echo Installing dependencies...
npm install --legacy-peer-deps

echo Building frontend...
npm run build

echo.
echo ✅ Frontend built successfully!
echo 📁 Frontend files are in: frontend/out/
echo.
echo Now you can deploy to Render with the pre-built frontend.
echo.
pause
