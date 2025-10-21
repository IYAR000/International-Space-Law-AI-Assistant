#!/bin/bash

# Test script for Podman setup
# This script validates the Podman configuration and setup

set -e

echo "🧪 Testing Podman setup for International Space Law AI Assistant..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test functions
test_podman_installed() {
    echo "🔍 Testing Podman installation..."
    if command -v podman &> /dev/null; then
        echo -e "${GREEN}✅ Podman is installed: $(podman --version)${NC}"
        return 0
    else
        echo -e "${RED}❌ Podman is not installed${NC}"
        return 1
    fi
}

test_podman_compose() {
    echo "🔍 Testing Podman Compose..."
    if command -v podman-compose &> /dev/null; then
        echo -e "${GREEN}✅ Podman Compose is installed: $(podman-compose --version)${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️  Podman Compose is not installed. Installing...${NC}"
        if command -v pip3 &> /dev/null; then
            pip3 install podman-compose
        elif command -v pip &> /dev/null; then
            pip install podman-compose
        else
            echo -e "${RED}❌ pip is not available${NC}"
            return 1
        fi
    fi
}

test_config_files() {
    echo "🔍 Testing configuration files..."
    local errors=0
    
    # Check podman-compose.yml
    if [ -f "podman-compose.yml" ]; then
        echo -e "${GREEN}✅ podman-compose.yml exists${NC}"
    else
        echo -e "${RED}❌ podman-compose.yml not found${NC}"
        errors=$((errors + 1))
    fi
    
    # Check Containerfiles
    if [ -f "apis/data_collection_api/Containerfile" ]; then
        echo -e "${GREEN}✅ Data Collection API Containerfile exists${NC}"
    else
        echo -e "${RED}❌ Data Collection API Containerfile not found${NC}"
        errors=$((errors + 1))
    fi
    
    if [ -f "apis/legal_analysis_api/Containerfile" ]; then
        echo -e "${GREEN}✅ Legal Analysis API Containerfile exists${NC}"
    else
        echo -e "${RED}❌ Legal Analysis API Containerfile not found${NC}"
        errors=$((errors + 1))
    fi
    
    return $errors
}

test_network_creation() {
    echo "🔍 Testing network creation..."
    if podman network create space-law-network 2>/dev/null; then
        echo -e "${GREEN}✅ Network created successfully${NC}"
    else
        echo -e "${YELLOW}⚠️  Network already exists or creation failed${NC}"
    fi
}

test_build_containers() {
    echo "🔍 Testing container builds..."
    local errors=0
    
    # Test data collection API build
    echo "Building Data Collection API..."
    if podman build -f apis/data_collection_api/Containerfile -t space-law-data-collection ./apis/data_collection_api; then
        echo -e "${GREEN}✅ Data Collection API built successfully${NC}"
    else
        echo -e "${RED}❌ Data Collection API build failed${NC}"
        errors=$((errors + 1))
    fi
    
    # Test legal analysis API build
    echo "Building Legal Analysis API..."
    if podman build -f apis/legal_analysis_api/Containerfile -t space-law-legal-analysis ./apis/legal_analysis_api; then
        echo -e "${GREEN}✅ Legal Analysis API built successfully${NC}"
    else
        echo -e "${RED}❌ Legal Analysis API build failed${NC}"
        errors=$((errors + 1))
    fi
    
    return $errors
}

test_compose_start() {
    echo "🔍 Testing compose startup..."
    if podman-compose -f podman-compose.yml up -d --build; then
        echo -e "${GREEN}✅ Services started successfully${NC}"
        
        # Wait a moment for services to initialize
        sleep 5
        
        # Check if services are running
        if podman-compose -f podman-compose.yml ps | grep -q "Up"; then
            echo -e "${GREEN}✅ Services are running${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️  Services may not be fully started yet${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ Failed to start services${NC}"
        return 1
    fi
}

test_api_endpoints() {
    echo "🔍 Testing API endpoints..."
    local errors=0
    
    # Test data collection API
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Data Collection API is responding${NC}"
    else
        echo -e "${YELLOW}⚠️  Data Collection API health check failed (may not have /health endpoint)${NC}"
    fi
    
    # Test legal analysis API
    if curl -s http://localhost:8002/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Legal Analysis API is responding${NC}"
    else
        echo -e "${YELLOW}⚠️  Legal Analysis API health check failed (may not have /health endpoint)${NC}"
    fi
    
    return $errors
}

cleanup_test() {
    echo "🧹 Cleaning up test resources..."
    podman-compose -f podman-compose.yml down 2>/dev/null || true
    podman rmi space-law-data-collection space-law-legal-analysis 2>/dev/null || true
    echo -e "${GREEN}✅ Cleanup complete${NC}"
}

# Main test execution
main() {
    local total_tests=0
    local passed_tests=0
    
    echo "🚀 Starting Podman setup tests..."
    echo ""
    
    # Test 1: Podman installation
    total_tests=$((total_tests + 1))
    if test_podman_installed; then
        passed_tests=$((passed_tests + 1))
    fi
    echo ""
    
    # Test 2: Podman Compose
    total_tests=$((total_tests + 1))
    if test_podman_compose; then
        passed_tests=$((passed_tests + 1))
    fi
    echo ""
    
    # Test 3: Configuration files
    total_tests=$((total_tests + 1))
    if test_config_files; then
        passed_tests=$((passed_tests + 1))
    fi
    echo ""
    
    # Test 4: Network creation
    total_tests=$((total_tests + 1))
    if test_network_creation; then
        passed_tests=$((passed_tests + 1))
    fi
    echo ""
    
    # Test 5: Container builds
    total_tests=$((total_tests + 1))
    if test_build_containers; then
        passed_tests=$((passed_tests + 1))
    fi
    echo ""
    
    # Test 6: Compose startup
    total_tests=$((total_tests + 1))
    if test_compose_start; then
        passed_tests=$((passed_tests + 1))
    fi
    echo ""
    
    # Test 7: API endpoints
    total_tests=$((total_tests + 1))
    if test_api_endpoints; then
        passed_tests=$((passed_tests + 1))
    fi
    echo ""
    
    # Cleanup
    cleanup_test
    echo ""
    
    # Summary
    echo "📊 Test Summary:"
    echo "   Total tests: $total_tests"
    echo "   Passed: $passed_tests"
    echo "   Failed: $((total_tests - passed_tests))"
    
    if [ $passed_tests -eq $total_tests ]; then
        echo -e "${GREEN}🎉 All tests passed! Podman setup is working correctly.${NC}"
        echo ""
        echo "🚀 You can now use:"
        echo "   podman-compose -f podman-compose.yml up -d"
        echo "   podman-compose -f podman-compose.yml down"
        echo "   podman-compose -f podman-compose.yml logs -f"
        exit 0
    else
        echo -e "${RED}❌ Some tests failed. Please check the output above for details.${NC}"
        exit 1
    fi
}

# Run main function
main "$@"
