@echo off
echo Building Manufacturing Orchestration UI for Production...
echo.

REM Set environment variables for Windows
set GENERATE_SOURCEMAP=false
set NODE_ENV=production
set ESLINT_NO_DEV_ERRORS=true

REM Run the build
call npm run build

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Build completed successfully!
    echo 📁 Output directory: build/
    echo 🚀 Ready for deployment!
) else (
    echo.
    echo ❌ Build failed!
    echo Check the errors above and fix them.
)

echo.
pause