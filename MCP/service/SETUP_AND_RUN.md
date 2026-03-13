# Helix Service - Setup and Run Guide

## Issue
You're in the wrong virtual environment. The `(env)` is from MultiAgentsBYGoogleAdk, but this service needs its own `.venv`.

## Solution

### Option 1: Use the Service's Virtual Environment (Recommended)

```bash
# Navigate to service directory
cd D:\A_LEARN\helix-main\service

# Deactivate current environment
deactivate

# Activate the service's .venv
.venv\Scripts\activate

# Install dependencies if needed
pip install -e .

# Run the service
python -m uvicorn src.app_local:app --host 0.0.0.0 --port 8000
```

### Option 2: Install uvicorn in Current Environment

```bash
# Stay in current (env) environment
pip install uvicorn fastapi python-multipart

# Run the service
python -m uvicorn src.app_local:app --host 0.0.0.0 --port 8000
```

### Option 3: Use UV (Modern Python Package Manager)

```bash
# If you have uv installed
cd D:\A_LEARN\helix-main\service
uv sync
uv run uvicorn src.app_local:app --host 0.0.0.0 --port 8000
```

## Quick Fix Script

Create a file `run_service.bat`:

```bat
@echo off
cd /d D:\A_LEARN\helix-main\service
call .venv\Scripts\activate
python -m uvicorn src.app_local:app --host 0.0.0.0 --port 8000
```

Then just run: `run_service.bat`

## Verify Setup

After activating the correct environment:

```bash
# Check uvicorn is installed
python -m pip list | findstr uvicorn

# Should show: uvicorn>=0.37.0
```

## Common Issues

### "No module named uvicorn"
- You're in the wrong virtual environment
- Solution: Activate `.venv` or install uvicorn

### "No module named fastapi"
- Dependencies not installed
- Solution: `pip install -e .` or `uv sync`

### Port already in use
- Another service is running on port 8000
- Solution: Use different port: `--port 8001`

## Environment Variables

Check `.env` file exists:
```bash
cd D:\A_LEARN\helix-main\service
type .env
```

If missing, copy from example:
```bash
copy .env.example .env
```

## Full Setup from Scratch

```bash
# 1. Navigate to service
cd D:\A_LEARN\helix-main\service

# 2. Create virtual environment (if .venv doesn't exist)
python -m venv .venv

# 3. Activate it
.venv\Scripts\activate

# 4. Install dependencies
pip install -e .

# 5. Setup environment
copy .env.example .env
# Edit .env with your settings

# 6. Run service
python -m uvicorn src.app_local:app --host 0.0.0.0 --port 8000
```

## Service URLs

Once running:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Stop Service

Press `Ctrl + C` in the terminal
