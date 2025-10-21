# International Space Law AI Assistant - Podman Edition

This repository has been migrated to use **Podman** instead of Docker for better security, performance, and compatibility.

## 🚀 Quick Start

### Windows Users
```cmd
# Start the application
scripts\start-podman.bat

# Stop the application  
scripts\stop-podman.bat

# Clean up resources
scripts\cleanup-podman.bat
```

### Linux/macOS Users
```bash
# Setup and start
./scripts/setup-podman.sh
podman-compose -f podman-compose.yml up -d

# Stop
podman-compose -f podman-compose.yml down
```

## 📋 Prerequisites

1. **Install Podman**
   - Windows: `choco install podman` or download from [podman.io](https://podman.io)
   - Linux: `sudo apt install podman` (Ubuntu/Debian)
   - macOS: `brew install podman`

2. **Install Podman Compose**
   ```bash
   pip install podman-compose
   ```

## 🔄 Migration from Docker

If you're migrating from Docker:

```bash
# Run the migration script
./scripts/migrate-from-docker.sh

# Or manually:
docker-compose down
podman-compose -f podman-compose.yml up -d --build
```

## 🏗️ Architecture

The application consists of:

- **Data Collection API** (Port 8001)
- **Legal Analysis API** (Port 8002)  
- **PostgreSQL Database** (Port 5432)
- **Redis Cache** (Port 6379)

## 📁 Key Files

- `podman-compose.yml` - Main orchestration file
- `apis/*/Containerfile` - Container definitions (replaces Dockerfile)
- `scripts/` - Helper scripts for different platforms
- `PODMAN-DEPLOYMENT.md` - Detailed deployment guide

## 🔧 Configuration

### Environment Variables
Create a `.env` file:
```bash
DB_TYPE=postgresql
DB_HOST=postgres
DB_PORT=5432
DB_NAME=space_law_db
DB_USER=space_law_user
DB_PASSWORD=space_law_password
```

### Security Features
- Rootless containers (no root required)
- SELinux labeling for volume mounts
- Read-only container filesystems
- No privilege escalation

## 📊 Management Commands

```bash
# View running containers
podman-compose -f podman-compose.yml ps

# View logs
podman-compose -f podman-compose.yml logs -f

# Rebuild and restart
podman-compose -f podman-compose.yml up -d --build

# Stop all services
podman-compose -f podman-compose.yml down
```

## 🔍 Troubleshooting

### Common Issues

1. **Permission errors on Windows:**
   - Run PowerShell as Administrator
   - Enable WSL2 if using Windows

2. **SELinux issues on Linux:**
   ```bash
   chcon -Rt svirt_sandbox_file_t ./shared
   chcon -Rt svirt_sandbox_file_t ./database
   ```

3. **Network connectivity:**
   ```bash
   podman network create space-law-network
   ```

### Getting Help

- Check logs: `podman-compose -f podman-compose.yml logs`
- View container status: `podman ps -a`
- Inspect containers: `podman inspect <container-name>`

## 🆚 Docker vs Podman

| Feature | Docker | Podman |
|---------|--------|--------|
| Daemon | Required | Not required |
| Root privileges | Often needed | Rootless by default |
| Security | Good | Better (SELinux, rootless) |
| Compatibility | N/A | Docker-compatible |
| Resource usage | Higher | Lower |

## 📚 Documentation

- [PODMAN-DEPLOYMENT.md](PODMAN-DEPLOYMENT.md) - Comprehensive deployment guide
- [Podman Documentation](https://docs.podman.io/)
- [Podman Compose](https://github.com/containers/podman-compose)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with Podman
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review the [PODMAN-DEPLOYMENT.md](PODMAN-DEPLOYMENT.md) guide
3. Open an issue on GitHub
4. Check Podman documentation

---

**Note:** This project has been optimized for Podman but maintains compatibility with Docker through the original `docker-compose.yml` file.
