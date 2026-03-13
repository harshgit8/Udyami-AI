# Fix Dependencies Issue

## Problem
The error `TypeError: Client.__init__() got an unexpected keyword argument 'proxies'` occurs due to incompatibility between `openai>=2.0.0` and `httpx>=0.28.1`.

## Solution
I've updated `pyproject.toml` to use compatible versions:
- `httpx>=0.27.0,<0.28.0` (downgraded from 0.28.1)
- `openai>=1.54.0` (downgraded from 2.0.0)

## Steps to Fix

### Option 1: Using uv (Recommended)
```bash
cd service
uv sync
uv run uvicorn src.app_local:app --reload --host 0.0.0.0 --port 8000
```

### Option 2: Using pip
```bash
cd service
pip install -e .
uvicorn src.app_local:app --reload --host 0.0.0.0 --port 8000
```

### Option 3: Force reinstall specific packages
```bash
cd service
pip uninstall httpx openai -y
pip install "httpx>=0.27.0,<0.28.0" "openai>=1.54.0"
uvicorn src.app_local:app --reload --host 0.0.0.0 --port 8000
```

## Verify
After running the commands, the server should start without errors.
