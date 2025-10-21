#!/bin/bash

# Migration script from Docker to Podman
# This script helps migrate existing Docker setup to Podman

set -e

echo "🔄 Migrating from Docker to Podman..."

# Stop any running Docker containers
echo "🛑 Stopping Docker containers..."
docker-compose down 2>/dev/null || echo "No Docker containers running"

# Remove Docker containers and images (optional)
read -p "🗑️  Do you want to remove Docker containers and images? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧹 Cleaning up Docker resources..."
    docker-compose down --rmi all --volumes --remove-orphans 2>/dev/null || echo "No Docker resources to clean"
fi

# Check if Podman is installed
if ! command -v podman &> /dev/null; then
    echo "❌ Podman is not installed. Please install Podman first."
    echo "📖 Installation guide: https://podman.io/getting-started/installation"
    exit 1
fi

# Install podman-compose if not available
if ! command -v podman-compose &> /dev/null; then
    echo "📦 Installing podman-compose..."
    if command -v pip3 &> /dev/null; then
        pip3 install podman-compose
    elif command -v pip &> /dev/null; then
        pip install podman-compose
    else
        echo "❌ pip is not available. Please install Python and pip first."
        exit 1
    fi
fi

# Create Podman network
echo "🔧 Creating Podman network..."
podman network create space-law-network 2>/dev/null || echo "Network already exists"

# Build and start with Podman
echo "🚀 Building and starting with Podman..."
podman-compose -f podman-compose.yml up -d --build

echo "✅ Migration complete!"
echo ""
echo "🎉 Your application is now running with Podman!"
echo ""
echo "📊 Check status:"
echo "   podman-compose -f podman-compose.yml ps"
echo ""
echo "📝 View logs:"
echo "   podman-compose -f podman-compose.yml logs -f"
echo ""
echo "🌐 Access your APIs:"
echo "   Data Collection API: http://localhost:8001"
echo "   Legal Analysis API: http://localhost:8002"
