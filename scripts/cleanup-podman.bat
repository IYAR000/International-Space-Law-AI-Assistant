@echo off
REM Windows batch script to clean up Podman resources

echo 🧹 Cleaning up Podman resources...

REM Stop and remove containers
echo 🛑 Stopping containers...
podman-compose -f podman-compose.yml down

REM Remove images
echo 🗑️  Removing images...
podman rmi -f $(podman images -q) 2>nul

REM Remove volumes
echo 🗑️  Removing volumes...
podman volume rm -f $(podman volume ls -q) 2>nul

REM Remove networks
echo 🗑️  Removing networks...
podman network rm space-law-network 2>nul

echo ✅ Cleanup complete!
pause
