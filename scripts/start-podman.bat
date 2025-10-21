@echo off
REM Windows batch script to start the application with Podman
REM This script provides Windows users with easy Podman commands

echo 🚀 Starting International Space Law AI Assistant with Podman...

REM Check if Podman is installed
podman --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Podman is not installed or not in PATH
    echo 📖 Please install Podman from: https://podman.io/getting-started/installation
    pause
    exit /b 1
)

REM Check if podman-compose is available
podman-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Podman Compose is not installed. Installing...
    pip install podman-compose
    if %errorlevel% neq 0 (
        echo ❌ Failed to install podman-compose
        pause
        exit /b 1
    )
)

REM Create network if it doesn't exist
echo 🔧 Creating Podman network...
podman network create space-law-network >nul 2>&1

REM Start the application
echo 🚀 Starting application...
podman-compose -f podman-compose.yml up -d --build

if %errorlevel% equ 0 (
    echo ✅ Application started successfully!
    echo.
    echo 🌐 Access your APIs:
    echo    Data Collection API: http://localhost:8001
    echo    Legal Analysis API: http://localhost:8002
    echo.
    echo 📊 To check status: podman-compose -f podman-compose.yml ps
    echo 📝 To view logs: podman-compose -f podman-compose.yml logs -f
    echo 🛑 To stop: podman-compose -f podman-compose.yml down
) else (
    echo ❌ Failed to start application
    echo 📝 Check logs: podman-compose -f podman-compose.yml logs
)

pause
