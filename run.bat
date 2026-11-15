@echo off
title Zartogrify - Open Source AI PC Controller
color 0b

echo ========================================================
echo               ⚡ ZARTOGRIFY v2.2 ⚡
echo       Open-Source Local PC Controller ^& AI Agent
echo                  ZarTo's Studios
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
        echo [INFO] Generating default config.json from template...
        copy config.example.json config.json >nul
    )
)

echo [INFO] Checking dependencies...
python -m pip install -r requirements.txt --quiet

echo [INFO] Launching Zartogrify Engine...
python main.py

if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Application closed with exit code %errorlevel%.
    pause
)
