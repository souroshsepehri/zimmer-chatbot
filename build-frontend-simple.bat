@echo off
echo ========================================
echo    Building Frontend for Render
echo ========================================
echo.

echo Building frontend...
cd frontend

echo Installing dependencies...
npm install --legacy-peer-deps

echo Building frontend...
npm run build

echo.
echo ✅ Frontend built successfully!
echo 📁 Frontend files are in: frontend/out/
echo.
echo Now commit and push to deploy:
echo git add frontend/out/
echo git commit -m "Add built frontend"
echo git push
echo.
pause
