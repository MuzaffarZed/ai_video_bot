@echo off
chcp 65001 >nul
title GitHub ga yuklash - MuzaffarZed
cd /d "%~dp0"
echo ========================================================
echo   MUZAFFARZED AI VIDEO BOT - GITHUB REPO GA YUKLASH
echo ========================================================
echo.
echo 1. GitHub.com ga kiring va yangi bo'sh repozitoriy oching
echo    (masalan: https://github.com/MuzaffarZed/ai_video_bot.git)
echo.
set /p repourl="GitHub repozitoriy havolasini kiriting: "
if "%repourl%"=="" (
    echo Xatolik: Havola kiritilmadi!
    pause
    exit /b
)

git remote remove origin 2>nul
git remote add origin %repourl%
git branch -M main
git push -u origin main

echo.
echo ========================================================
echo   MUVAFFAQIYATLI YUKLANDI!
echo ========================================================
echo Endi GitHub repozitoriy sozlamalariga kiring:
echo 1. Settings -> Secrets and variables -> Actions -> New repository secret
echo 2. Name: TELEGRAM_BOT_TOKEN
echo 3. Secret: 8620346829:AAEpF2VVA.tCZDB-NqfvMOCQGFVGiI8yrgLA
echo 4. Actions bo'limiga o'tib "Run workflow" tugmasini bosing!
pause
