@echo off
REM Backend Startup Script for Windows
REM This script starts the FastAPI backend server with Neon database configuration

echo.
echo ========================================
echo   Task CRUD API - Backend Startup
echo ========================================
echo.
echo 🚀 Starting FastAPI Backend...
echo 📊 Using Neon PostgreSQL Database
echo.

REM Navigate to backend directory
cd /d "%~dp0backend" || exit /b 1

REM Load environment variables from .env file
REM Note: Windows doesn't have a built-in way to load .env files like Unix
REM You may need to set these manually or use a tool like direnv

REM For now, display instructions
echo ⚠️  Make sure your .env file is configured with Neon database URL
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    exit /b 1
)

echo ✅ Python found
echo.

REM Start the FastAPI server
echo 🌐 Backend starting on http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

pause
