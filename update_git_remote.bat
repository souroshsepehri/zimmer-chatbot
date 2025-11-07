@echo off
echo ========================================
echo    Updating Git Remote Repository
echo ========================================
echo.

cd /d "%~dp0"

echo Current Git Remotes:
git remote -v
echo.

echo Removing all existing remotes...
git remote remove origin 2>nul
git remote remove upstream 2>nul

echo.
echo Adding new remote: https://github.com/souroshsepehri/zimmer-chatbot.git
git remote add origin https://github.com/souroshsepehri/zimmer-chatbot.git

echo.
echo Updated Git Remotes:
git remote -v
echo.

echo ========================================
echo    Git Remote Updated Successfully!
echo ========================================
echo.
pause
