@echo off
echo ========================================
echo Starting Helix Service
echo ========================================
echo.

cd /d D:\A_LEARN\helix-main\service

echo Activating virtual environment...
call .venv\Scripts\activate

echo.
echo Checking uvicorn installation...
python -m pip show uvicorn >nul 2>&1
if errorlevel 1 (
    echo uvicorn not found. Installing dependencies...
    pip install -e .
)

echo.
echo Starting service on http://localhost:8000
echo API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

python -m uvicorn src.app_local:app --host 0.0.0.0 --port 8000
