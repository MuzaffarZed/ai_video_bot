@echo off
chcp 65001 >nul
title MuzaffarZed AI Video Generator CLI
cd /d "%~dp0"
echo ========================================================
echo  MUZAFFARZED AI VIDEO CREATOR - TEZKOR GENERATSIYA
echo ========================================================
set /p topic="Video mavzusini kiriting (masalan: Koinot sirlari): "
if "%topic%"=="" set topic=Koinotning eng buyuk sirlari
C:\Users\MuzaffarZed\ai_workspace\venv\Scripts\python.exe cli_generate.py --topic "%topic%"
echo.
echo Video output papkasida tayyor!
pause
