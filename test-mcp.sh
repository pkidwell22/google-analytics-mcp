#!/bin/bash

# Test script for Google Analytics MCP server
# This script tests the MCP server endpoints

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="${1:-http://localhost:8080}"

echo -e "${GREEN}🧪 Testing Google Analytics MCP Server${NC}"
echo -e "${YELLOW}Base URL: ${BASE_URL}${NC}"

# Test health endpoint
echo -e "${YELLOW}1. Testing health endpoint...${NC}"
if curl -s "${BASE_URL}/health" | grep -q "healthy"; then
    echo -e "${GREEN}✅ Health check passed${NC}"
else
    echo -e "${RED}❌ Health check failed${NC}"
    exit 1
fi

# Test MCP initialize
echo -e "${YELLOW}2. Testing MCP initialize...${NC}"
INIT_RESPONSE=$(curl -s -X POST "${BASE_URL}/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test-client", "version": "1.0.0"}}}')

if echo "$INIT_RESPONSE" | grep -q "Google Analytics Server"; then
    echo -e "${GREEN}✅ MCP initialize working${NC}"
else
    echo -e "${RED}❌ MCP initialize failed${NC}"
    echo -e "${YELLOW}Response: ${INIT_RESPONSE}${NC}"
    exit 1
fi

# Test MCP server info
echo -e "${YELLOW}3. Testing MCP server info...${NC}"
if echo "$INIT_RESPONSE" | grep -q "Google Analytics Server"; then
    echo -e "${GREEN}✅ MCP server is properly configured${NC}"
    echo -e "${YELLOW}Server name: Google Analytics Server${NC}"
else
    echo -e "${RED}❌ MCP server configuration issue${NC}"
fi

echo -e "${GREEN}🎉 MCP server tests completed!${NC}"
echo -e "${YELLOW}Server is ready for use with Claude Desktop${NC}"
