# Podman Deployment Guide

This guide explains how to deploy the International Space Law AI Assistant using Podman instead of Docker.

## Prerequisites

### Install Podman

#### Windows
```powershell
# Using Chocolatey
choco install podman

# Using Scoop
scoop install podman

# Or download from: https://podman.io/getting-started/installation
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install podman

# CentOS/RHEL/Fedora
sudo dnf install podman
```

#### macOS
```bash
# Using Homebrew
brew install podman

# Initialize Podman machine
podman machine init
podman machine start
```

### Install Podman Compose
```bash
pip install podman-compose
```

## Quick Start

1. **Clone and setup:**
   ```bash
   git clone <your-repo>
   cd International-Space-Law-AI-Assistant
   ./scripts/setup-podman.sh
   ```

2. **Start the application:**
   ```bash
   podman-compose -f podman-compose.yml up -d
   ```

3. **Check status:**
   ```bash
   podman-compose -f podman-compose.yml ps
   ```

## Migration from Docker

If you're migrating from Docker:

1. **Run the migration script:**
   ```bash
   ./scripts/migrate-from-docker.sh
   ```

2. **Or manually migrate:**
   ```bash
   # Stop Docker containers
   docker-compose down
   
   # Start with Podman
   podman-compose -f podman-compose.yml up -d --build
   ```

## Key Differences from Docker

### Security Enhancements
- **Rootless containers**: Podman runs containers without root privileges by default
- **SELinux labeling**: Volume mounts use `:Z` flag for proper SELinux context
- **Read-only filesystems**: Containers run with read-only root filesystem
- **No new privileges**: Security option prevents privilege escalation

### Volume Mounts
Podman uses SELinux labeling for volume mounts:
```yaml
volumes:
  - ./shared:/app/shared:Z  # Z flag for SELinux context
```

### Container Files
- **Containerfile**: Podman uses `Containerfile` instead of `Dockerfile`
- **Compatibility**: Existing Dockerfiles work with Podman

## Commands Reference

### Basic Operations
```bash
# Start services
podman-compose -f podman-compose.yml up -d

# Stop services
podman-compose -f podman-compose.yml down

# View logs
podman-compose -f podman-compose.yml logs -f

# Check status
podman-compose -f podman-compose.yml ps

# Rebuild and start
podman-compose -f podman-compose.yml up -d --build
```

### Individual Container Management
```bash
# List containers
podman ps -a

# View container logs
podman logs <container-name>

# Execute commands in container
podman exec -it <container-name> /bin/bash

# Remove containers
podman rm <container-name>

# Remove images
podman rmi <image-name>
```

### Volume Management
```bash
# List volumes
podman volume ls

# Inspect volume
podman volume inspect <volume-name>

# Remove volume
podman volume rm <volume-name>
```

## Configuration Files

### podman-compose.yml
Main orchestration file with Podman-specific optimizations:
- Security options for better isolation
- SELinux labeling for volumes
- Read-only filesystems
- Temporary filesystem mounts

### Containerfile
Podman-compatible container definition files:
- Located in `apis/data_collection_api/Containerfile`
- Located in `apis/legal_analysis_api/Containerfile`

## Environment Variables

Create a `.env` file in the project root:
```bash
# Database Configuration
DB_TYPE=postgresql
DB_HOST=postgres
DB_PORT=5432
DB_NAME=space_law_db
DB_USER=space_law_user
DB_PASSWORD=space_law_password

# API Configuration
DATA_COLLECTION_API_PORT=8001
LEGAL_ANALYSIS_API_PORT=8002

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
```

## Troubleshooting

### Common Issues

1. **Permission denied errors:**
   ```bash
   # Check SELinux status
   getenforce
   
   # If enforcing, set proper context
   chcon -Rt svirt_sandbox_file_t ./shared
   chcon -Rt svirt_sandbox_file_t ./database
   ```

2. **Network connectivity issues:**
   ```bash
   # Check network
   podman network ls
   
   # Create network if needed
   podman network create space-law-network
   ```

3. **Volume mount issues:**
   ```bash
   # Check volume mounts
   podman inspect <container-name> | grep -A 10 "Mounts"
   ```

### Logs and Debugging
```bash
# View all logs
podman-compose -f podman-compose.yml logs

# View specific service logs
podman-compose -f podman-compose.yml logs data-collection-api

# Follow logs in real-time
podman-compose -f podman-compose.yml logs -f
```

## Performance Optimization

### Resource Limits
Add resource limits to your services:
```yaml
services:
  data-collection-api:
    # ... other config
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
```

### Health Checks
```yaml
services:
  data-collection-api:
    # ... other config
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Production Deployment

### Using Podman with Systemd
Create systemd service files for production deployment:

```bash
# Generate systemd files
podman generate systemd --new --files --name <container-name>

# Enable and start services
sudo systemctl --user enable container-<container-name>.service
sudo systemctl --user start container-<container-name>.service
```

### Podman Play
For Kubernetes-like deployment:
```bash
# Generate Kubernetes YAML
podman play kube podman-compose.yml

# Deploy with podman play
podman play kube deployment.yaml
```

## Security Best Practices

1. **Use rootless mode** (default)
2. **Enable SELinux** for additional security
3. **Use read-only containers** where possible
4. **Limit container capabilities**
5. **Use secrets management** for sensitive data
6. **Regular security updates**

## Monitoring

### Health Monitoring
```bash
# Check container health
podman healthcheck run <container-name>

# Monitor resource usage
podman stats
```

### Log Management
```bash
# Configure log rotation
podman run --log-opt max-size=10m --log-opt max-file=3 <image>
```

## Backup and Recovery

### Volume Backup
```bash
# Backup PostgreSQL data
podman run --rm -v postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz -C /data .
```

### Container Backup
```bash
# Export container
podman export <container-name> > container-backup.tar

# Import container
podman import container-backup.tar <image-name>
```

## Support and Resources

- [Podman Documentation](https://docs.podman.io/)
- [Podman Compose Documentation](https://github.com/containers/podman-compose)
- [SELinux and Podman](https://www.redhat.com/sysadmin/selinux-podman)
- [Podman Security](https://docs.podman.io/en/latest/markdown/podman-run.1.html#security-options)
