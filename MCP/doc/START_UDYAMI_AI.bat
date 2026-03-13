@echo off
title Udyami AI - Complete System Startup
color 0A

echo.
echo ========================================
echo    UDYAMI AI SYSTEM STARTUP
echo ========================================
echo.

echo Step 1: Clearing Python cache...
cd service
if exist src\__pycache__ rmdir /s /q src\__pycache__
if exist src\utils\__pycache__ rmdir /s /q src\utils\__pycache__
echo Cache cleared!

echo.
echo Step 2: Checking system...
python verify_system.py

echo.
echo ========================================
echo.
echo Step 3: Starting Backend...
echo.
echo Backend will start on: http://localhost:8000
echo Keep this window open!
echo.
echo Press Ctrl+C to stop the backend
echo.
pause

python -m uvicorn src.app_local:app --host 0.0.0.0 --port 8000
