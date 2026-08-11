@echo off
title Lolzteam Telegram Monitor
echo Checking python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ==============================================================
    echo ERROR: Python is not installed or not in your system PATH!
    echo ==============================================================
    echo 1. Download Python from: https://www.python.org/downloads/
    echo 2. During installation, make sure to CHECK the box:
    echo    "Add Python.exe to PATH" (or "Add Python to PATH")
    echo 3. After installing, close this window and open run.bat again.
    echo ==============================================================
    echo.
    pause
    exit /b
)

echo Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b
)

echo Starting monitor...
python monitor.py
pause
