@echo off
title Revision-Ai v2.2 // Project Revision
color 0c

echo ========================================================
echo              ⚡ REVISION-AI v2.2 ⚡
echo    Autonomous Local PC Controller ^& Automation Suite
echo               Project Revision Ecosystem
echo ========================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ and re-run.
    pause
    exit /b 1
)

if not exist "config.json" (
    if exist "config.example.json" (
        echo [INFO] Initializing default config.json from template...
        copy config.example.json config.json >nul
    )
)

echo [INFO] Verifying environment dependencies...
python -m pip install -r requirements.txt --quiet

echo [INFO] Launching Revision-Ai Engine...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Application closed with exit code %errorlevel%.
    pause
)
