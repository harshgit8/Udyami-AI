@echo off
echo Starting Udyami Backend with Document Extraction...
echo.
echo Make sure you have installed dependencies:
echo   pip install pypdf python-docx python-pptx
echo.
python -m uvicorn src.app_local:app --host 0.0.0.0 --port 8000
