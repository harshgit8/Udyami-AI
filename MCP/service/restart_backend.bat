@echo off
echo Stopping old backend...
taskkill /F /IM uvicorn.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting backend with text extraction...
echo.
python -m uvicorn src.app_local:app --host 0.0.0.0 --port 8000
