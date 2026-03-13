@echo off
echo Starting Manufacturing Orchestration UI...
echo.

REM Set environment variables for Windows
set GENERATE_SOURCEMAP=false
set NODE_ENV=development
set REACT_APP_API_URL=http://localhost:8000/api
set REACT_APP_WS_URL=ws://localhost:8000/ws

REM Start the development server
call npm start

pause