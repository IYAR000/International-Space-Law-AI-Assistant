#!/bin/bash

# Setup script for Podman migration
# This script helps migrate from Docker to Podman

set -e

echo "🚀 Setting up Podman for International Space Law AI Assistant..."

# Check if Podman is installed
if ! command -v podman &> /dev/null; then
    echo "❌ Podman is not installed. Please install Podman first."
    echo "📖 Installation guide: https://podman.io/getting-started/installation"
    exit 1
fi

# Check if Podman Compose is installed
if ! command -v podman-compose &> /dev/null; then
    echo "⚠️  Podman Compose is not installed. Installing..."
    
    # Install podman-compose
    if command -v pip3 &> /dev/null; then
        pip3 install podman-compose
    elif command -v pip &> /dev/null; then
        pip install podman-compose
    else
        echo "❌ pip is not available. Please install Python and pip first."
        exit 1
    fi
fi

# Create Podman network if it doesn't exist
echo "🔧 Creating Podman network..."
podman network create space-law-network 2>/dev/null || echo "Network already exists"

# Set up rootless mode (recommended)
echo "🔐 Configuring rootless mode..."
if [ "$(id -u)" != "0" ]; then
    echo "✅ Running in rootless mode (recommended)"
else
    echo "⚠️  Running as root. Consider using rootless mode for better security."
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p data/postgres

# Set proper permissions
echo "🔒 Setting permissions..."
chmod +x scripts/*.sh 2>/dev/null || true

echo "✅ Podman setup complete!"
echo ""
echo "🚀 To start the application:"
echo "   podman-compose -f podman-compose.yml up -d"
echo ""
echo "🛑 To stop the application:"
echo "   podman-compose -f podman-compose.yml down"
echo ""
echo "📊 To view logs:"
echo "   podman-compose -f podman-compose.yml logs -f"
echo ""
echo "🔍 To check status:"
echo "   podman-compose -f podman-compose.yml ps"
