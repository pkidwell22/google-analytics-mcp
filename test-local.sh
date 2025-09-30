#!/bin/bash

# Local Docker test script for Google Analytics MCP
# This script builds and runs the MCP server locally for testing

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=$(gcloud config get-value project)
IMAGE_NAME="ga4-mcp:local"
CONTAINER_NAME="ga4-mcp-test"
PORT="8080"

echo -e "${GREEN}Starting local Docker test${NC}"
echo -e "${YELLOW}Project ID: ${PROJECT_ID}${NC}"
echo -e "${YELLOW}Image: ${IMAGE_NAME}${NC}"
echo -e "${YELLOW}Port: ${PORT}${NC}"

# Check if ADC credentials exist
if [ ! -f "$HOME/.config/gcloud/application_default_credentials.json" ]; then
    echo -e "${RED}ERROR: ADC credentials not found at $HOME/.config/gcloud/application_default_credentials.json${NC}"
    echo -e "${YELLOW}Please run: gcloud auth application-default login${NC}"
    exit 1
fi

# Stop and remove existing container if it exists
if docker ps -a --format 'table {{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}Stopping existing container...${NC}"
    docker stop ${CONTAINER_NAME} >/dev/null 2>&1 || true
    docker rm ${CONTAINER_NAME} >/dev/null 2>&1 || true
fi

# Build Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t ${IMAGE_NAME} .

echo -e "${GREEN}Docker image built${NC}"

# Run Docker container
echo -e "${YELLOW}Starting container...${NC}"
docker run --rm -d \
    --name ${CONTAINER_NAME} \
    -p ${PORT}:8080 \
    -e GOOGLE_PROJECT_ID="${PROJECT_ID}" \
    -v "$HOME/.config/gcloud/application_default_credentials.json:/secrets/adc/credentials.json:ro" \
    -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/adc/credentials.json" \
    ${IMAGE_NAME}

echo -e "${GREEN}Container started${NC}"

# Wait for container to be ready
echo -e "${YELLOW}Waiting for container to be ready...${NC}"
sleep 5

# Test health endpoint
echo -e "${YELLOW}Testing health endpoint...${NC}"
if curl -s "http://localhost:${PORT}/health" | grep -q "healthy"; then
    echo -e "${GREEN}Health check passed${NC}"
else
    echo -e "${RED}Health check failed${NC}"
    echo -e "${YELLOW}Container logs:${NC}"
    docker logs ${CONTAINER_NAME}
    exit 1
fi

# Test MCP initialize
echo -e "${YELLOW}Testing MCP initialize...${NC}"
if curl -s -X POST "http://localhost:${PORT}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}' | grep -q "Google Analytics Server"; then
    echo -e "${GREEN}MCP initialize working${NC}"
else
    echo -e "${RED}MCP initialize failed${NC}"
    echo -e "${YELLOW}Container logs:${NC}"
    docker logs ${CONTAINER_NAME}
    exit 1
fi

echo -e "${GREEN}Local test completed successfully!${NC}"
echo -e "${YELLOW}Container is running on http://localhost:${PORT}${NC}"
echo -e "${YELLOW}To stop the container, run: docker stop ${CONTAINER_NAME}${NC}"
echo -e "${YELLOW}To view logs, run: docker logs ${CONTAINER_NAME}${NC}"
