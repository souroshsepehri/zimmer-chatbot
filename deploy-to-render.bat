@echo off
echo ========================================
echo    Deploy to Render - Persian Chatbot
echo ========================================
echo.

echo 🚀 Preparing deployment files...
echo.

echo ✅ Created render.yaml configuration
echo ✅ Created requirements.txt in root
echo ✅ Created deployment scripts
echo ✅ Created documentation
echo.

echo 📤 Pushing to GitHub...
git add .
git commit -m "Complete Render deployment setup"
git push origin json-faq-system-clean

echo.
echo 🎉 Deployment files ready!
echo.
echo 📋 Next steps:
echo 1. Go to https://render.com
echo 2. Sign up with GitHub
echo 3. Click "New +" → "Blueprint"
echo 4. Paste: https://github.com/souroshsepehri/chatbot2
echo 5. Select branch: json-faq-system-clean
echo 6. Click "Apply"
echo.
echo 🔑 Don't forget to set your OPENAI_API_KEY!
echo.
pause
