@echo off
echo Building Manufacturing Orchestration UI (Clean Build)...
echo.

REM Set environment variables for Windows
set GENERATE_SOURCEMAP=false
set NODE_ENV=production
set ESLINT_NO_DEV_ERRORS=true
set CI=false

REM Run the clean build (ignores ESLint warnings)
call npm run build:clean

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Clean build completed successfully!
    echo 📁 Output directory: build/
    echo 🚀 Ready for deployment!
    echo.
    echo 📊 Build Statistics:
    dir build\static\js\*.js /b
    echo.
) else (
    echo.
    echo ❌ Build failed!
    echo Check the errors above and fix them.
)

echo.
pause