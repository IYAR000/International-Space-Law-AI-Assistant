@echo off
REM Windows batch script to stop the application with Podman

echo 🛑 Stopping International Space Law AI Assistant...

REM Stop the application
podman-compose -f podman-compose.yml down

if %errorlevel% equ 0 (
    echo ✅ Application stopped successfully!
) else (
    echo ❌ Failed to stop application
    echo 📝 Check for running containers: podman ps
)

pause
